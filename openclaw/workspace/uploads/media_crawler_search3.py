import requests, json, time, sys

sys.stdout.reconfigure(encoding='utf-8')

s = requests.Session()

# 1. 获取SSE endpoint
r = s.get('http://127.0.0.1:18080/sse', stream=True, timeout=10)
endpoint = None
for line in r.iter_lines():
    line = line.decode('utf-8', errors='ignore')
    if line.startswith('data:'):
        endpoint = line[5:].strip()
        break
print(f"Endpoint: {endpoint}")

msg_url = f'http://127.0.0.1:18080{endpoint}'

# 2. 初始化
resp = s.post(msg_url, json={
    'jsonrpc':'2.0','id':1,'method':'initialize',
    'params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'test','version':'1.0'}}
}, timeout=10)
print(f"Init: {resp.status_code}")

s.post(msg_url, json={'jsonrpc':'2.0','method':'notifications/initialized'}, timeout=5)

# 3. 发送搜索请求
resp = s.post(msg_url, json={
    'jsonrpc':'2.0','id':2,'method':'tools/call',
    'params':{'name':'crawl_search','arguments':{
        'platform':'xhs',
        'store_type':'json',
        'keywords':'旅游攻略 三月'
    }}
}, timeout=10)
print(f"Search sent: {resp.status_code} {resp.text[:200]}")

# 4. 持续读取SSE响应（用r.headers读取）
# MediaCrawler返回202后会保持SSE连接，我们通过同一个session的stream读取响应
print("Waiting for SSE events...")
start = time.time()
event_count = 0
# 注意：这里不能用新的requests.get，因为SSE是同一个HTTP连接
# MediaCrawler MCP通过同一个SSE连接推送事件
# 但我们的POST请求没有关闭连接，所以事件可能混在POST的响应里？
# 实际上SSE和POST是不同路径：POST发到{endpoint}，事件从SSE的r.iter_lines来
# 所以应该能同时接收

# 给10秒收集事件
deadline = start + 10
r._content_consumed = False
r.raw._original_response = r.raw._original_response
for line in r.iter_lines():
    elapsed = time.time() - start
    if elapsed > 10:
        break
    if line:
        line = line.decode('utf-8', errors='ignore')
        if line.startswith('data:'):
            event_count += 1
            data = line[5:].strip()
            print(f"Event {event_count}: {data[:400]}")
            # 检查是否是数据结果
            if event_count > 3:  # skip init events
                try:
                    obj = json.loads(data)
                    if 'result' in obj:
                        print(f"  => Result found: {str(obj)[:500]}")
                except:
                    pass

print(f"\n总共 {event_count} 个SSE事件")
