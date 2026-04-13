import requests, json, sys, re

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}
r1 = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
    'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
}, headers=hdrs)
hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
s.post('http://localhost:18060/mcp', json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs)

results = []

# 搜索旅游攻略
for keyword in ['旅游攻略', '春季出行好去处', '三月旅行']:
    resp = s.post('http://localhost:18060/mcp', json={
        'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
        'params': {
            'name': 'search_feeds',
            'arguments': {
                'keyword': keyword,
                'filters': {'sort_by': 'like', 'publish_time': 'month'},
                'note_type': 'normal'
            }
        }
    }, headers=hdrs)
    
    data = resp.json()
    if 'result' in data and 'data' in data['result']:
        items = data['result']['data']
        for item in items[:5]:
            results.append({
                'keyword': keyword,
                'title': item.get('title', ''),
                'desc': item.get('desc', '')[:200],
                'liked': item.get('liked', 'N/A'),
                'type': '小红书'
            })

print(f"获取到 {len(results)} 条小红书数据")
print(json.dumps(results[:15], ensure_ascii=False, indent=2))
