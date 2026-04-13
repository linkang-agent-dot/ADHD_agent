import requests, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')
s = requests.Session()
hdrs = {'Accept':'application/json, text/event-stream'}
r1 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers=hdrs)
hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs)

# 搜索 MCP
resp = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_feeds','arguments':{'keyword':'OpenClaw使用minimax MCP'}}}, headers=hdrs)
data = resp.json()
feeds = json.loads(data['result']['content'][0]['text'])['feeds']

for f in feeds:
    if f.get('modelType') == 'note':
        card = f.get('noteCard', {})
        note_id = f.get('id')
        token = f.get('xsecToken')
        time.sleep(2)
        resp2 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'get_feed_detail','arguments':{'feed_id':note_id,'xsec_token':token}}}, headers=hdrs, timeout=30)
        note = json.loads(resp2.json()['result']['content'][0]['text'])['data']['note']
        print(f"标题: {note['title']}")
        print(f"内容:\n{note['desc'][:2500]}")
        break