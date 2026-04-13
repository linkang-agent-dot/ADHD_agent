import requests, json, time, sys, queue, threading

sys.stdout.reconfigure(encoding='utf-8')

results = queue.Queue()

def read_sse(url, q):
    try:
        r = requests.get(url, stream=True, timeout=120)
        for line in r.iter_lines():
            if line:
                line = line.decode('utf-8', errors='ignore')
                if line.startswith('data:'):
                    data = line[5:].strip()
                    q.put(data)
                    print(f"SSE received: {data[:300]}")
    except Exception as e:
        print(f"SSE error: {e}")
        q.put(f"ERROR:{e}")

# 1. 连接SSE获取endpoint
sse_url = 'http://127.0.0.1:18080/sse'
t = threading.Thread(target=read_sse, args=(sse_url, results), daemon=True)
t.start()

endpoint = results.get(timeout=10)
print(f"Endpoint: {endpoint}")
msg_url = f'http://127.0.0.1:18080{endpoint}'

# 2. 初始化
requests.post(msg_url, json={
    'jsonrpc':'2.0','id':1,'method':'initialize',
    'params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'test','version':'1.0'}}
}, timeout=10)
init_resp = results.get(timeout=10)
print(f"Init OK")

requests.post(msg_url, json={'jsonrpc':'2.0','method':'notifications/initialized'}, timeout=5)

# 3. 搜索
requests.post(msg_url, json={
    'jsonrpc':'2.0','id':2,'method':'tools/call',
    'params':{'name':'crawl_search','arguments':{
        'platform':'xhs',
        'store_type':'json',
        'keywords':'旅游攻略 三月'
    }}
}, timeout=10)
print("Search request sent, waiting for results...")

# 4. 收集SSE事件，最多等60秒
start = time.time()
events = []
while time.time() - start < 60:
    try:
        ev = results.get(timeout=5)
        events.append(ev)
        print(f"Event: {ev[:500]}")
        # 检查是否是完整结果
        if '"result"' in ev and '"data"' in ev.lower():
            break
    except:
        break

print(f"\n共收到 {len(events)} 个事件")
# 尝试找数据
for ev in events:
    if 'note_id' in ev or 'content' in ev or 'liked_count' in ev.lower():
        print(f"Found data: {ev[:1000]}")
