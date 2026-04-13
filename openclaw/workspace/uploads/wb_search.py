import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# MediaCrawler MCP (port 18080)
r = requests.get('http://127.0.0.1:18080/sse', stream=True, timeout=10)
endpoint = None
for line in r.iter_lines():
    line = line.decode('utf-8')
    if line.startswith('data:'):
        endpoint = line[5:].strip()
        break
r.close()
print(f"SSE endpoint: {endpoint}")

hdrs = {'Content-Type': 'application/json'}
sid = endpoint.split('session_id=')[1] if endpoint else ''

def mcp_call(session_id, tool_name, arguments):
    full_url = f'http://127.0.0.1:18080/messages/?session_id={session_id}'
    resp = requests.post(full_url, json={
        'jsonrpc': '2.0', 'id': 4, 'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    }, headers=hdrs, timeout=60)
    return resp.json()

# 搜索微博旅游
print("搜索微博关键词: 旅游攻略...")
result1 = mcp_call(sid, 'crawl_search', {
    'platform': 'wb',
    'store_type': 'json',
    'keywords': '旅游攻略'
})
print(json.dumps(result1, ensure_ascii=False)[:3000])
