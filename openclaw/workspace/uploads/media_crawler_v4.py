import requests, json, time, sys, threading
from queue import Queue, Empty

sys.stdout.reconfigure(encoding='utf-8')

# SSE事件队列
events = []
event_lock = threading.Lock()

def sse_client(endpoint, timeout=90):
    """在后台线程持续读取SSE事件"""
    try:
        r = requests.get(f'http://127.0.0.1:18080{endpoint}', stream=True, timeout=timeout)
        for line in r.iter_lines():
            if line:
                line = line.decode('utf-8', errors='ignore')
                if line.startswith('data:'):
                    with event_lock:
                        events.append(line[5:].strip())
                    print(f"SSE event: {line[:200]}")
    except Exception as e:
        print(f"SSE client error: {e}")

# 1. 连接SSE
r = requests.get('http://127.0.0.1:18080/sse', stream=True, timeout=10)
endpoint = None
for line in r.iter_lines():
    line = line.decode('utf-8', errors='ignore')
    if line.startswith('data:'):
        endpoint = line[5:].strip()
        print(f"Got endpoint: {endpoint}")
        break
r.close()

if not endpoint:
    print("SSE连接失败")
    exit()

# 2. 启动SSE监听线程
t = threading.Thread(target=sse_client, args=(endpoint, 90), daemon=True)
t.start()
time.sleep(0.5)

# 3. 发送搜索请求
resp = requests.post(f'http://127.0.0.1:18080{endpoint}', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
    'params': {'name': 'crawl_search', 'arguments': {
        'platform': 'xhs',
        'store_type': 'json',
        'keywords': '旅游攻略 三月 春季出行'
    }}
}, timeout=10)
print(f"Search req: {resp.status_code}, {resp.text[:200]}")

# 4. 等待结果（最多60秒）
t.join(60)
print(f"\n=== 共收到 {len(events)} 个SSE事件 ===")
for i, ev in enumerate(events):
    print(f"Event {i}: {ev[:500]}")
