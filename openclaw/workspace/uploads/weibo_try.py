import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 尝试用 MediaCrawler MCP (port 18080) 获取微博数据
try:
    r = requests.get('http://127.0.0.1:18080/sse', stream=True, timeout=10)
    endpoint = None
    for line in r.iter_lines():
        line = line.decode('utf-8')
        if line.startswith('data:'):
            endpoint = line[5:].strip()
            break
    r.close()
    print(f"SSE endpoint: {endpoint}")
    
    if endpoint:
        hdrs = {'Content-Type': 'application/json'}
        resp = requests.post(f'http://127.0.0.1:18080{endpoint}', json={
            'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
            'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
        }, headers=hdrs, timeout=10)
        print(f"MediaCrawler init: {resp.status_code}")
except Exception as e:
    print(f"MediaCrawler MCP 不可用: {e}")

# 用 web_search 作为微博搜索的补充
print("\n尝试 web_search 搜索微博数据...")
