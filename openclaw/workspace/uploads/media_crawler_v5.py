import requests, json, time, sys, queue

sys.stdout.reconfigure(encoding='utf-8')

results_queue = queue.Queue()

def sse_reader(url, q):
    """持续读取SSE直到收到完成通知或超时"""
    try:
        r = requests.get(url, stream=True, timeout=120)
        for line in r.iter_lines():
            if line:
                line = line.decode('utf-8', errors='ignore')
                if line.startswith('data:'):
                    data = line[5:].strip()
                    q.put(data)
                    print(f"SSE: {data[:300]}")
    except Exception as e:
        print(f"SSE error: {e}")
        q.put(f"ERROR:{e}")

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
import threading
t = threading.Thread(target=sse_reader, args=(f'http://127.0.0.1:18080{endpoint}', results_queue), daemon=True)
t.start()
time.sleep(0.5)

# 3. 发送搜索请求
resp = requests.post(f'http://127.0.0.1:18080{endpoint}', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
    'params': {'name': 'crawl_search', 'arguments': {
        'platform': 'xhs',
        'store_type': 'json',
        'keywords': '旅游攻略 三月'
    }}
}, timeout=10)
print(f"Search: {resp.status_code} {resp.text[:200]}")

# 4. 等待SSE事件，最多90秒
found_data = False
start = time.time()
while time.time() - start < 90:
    try:
        ev = results_queue.get(timeout=5)
        if 'ERROR' in ev:
            break
        # 检查是否包含搜索结果
        if 'result' in ev or 'note' in ev.lower() or 'content' in ev.lower():
            found_data = True
    except:
        pass

print(f"\n=== 等待完成通知 ===")
# 等done通知
while time.time() - start < 120:
    try:
        ev = results_queue.get(timeout=5)
        print(f"Final: {ev[:300]}")
        if 'done' in ev.lower() or 'complete' in ev.lower():
            break
    except:
        break

print(f"\n总共收到 {results_queue.qsize()} 个事件")
