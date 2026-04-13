import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

MCP_URL = 'http://localhost:18060/mcp'
s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}
r1 = s.post(MCP_URL, json={
    'jsonrpc':'2.0','id':1,'method':'initialize',
    'params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}
}, headers=hdrs, timeout=10)
hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
s.post(MCP_URL, json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs)

# Try list_feeds with longer timeout
print('Testing list_feeds...')
try:
    resp = s.post(MCP_URL, json={
        'jsonrpc':'2.0','id':2,'method':'tools/call',
        'params':{'name':'list_feeds','arguments':{}}
    }, headers=hdrs, timeout=60)
    print('list_feeds status:', resp.status_code)
    print('list_feeds response:', resp.text[:1000])
except Exception as e:
    print('list_feeds error:', e)

# Try search_feeds with very long timeout
print('\nTesting search_feeds...')
try:
    resp = s.post(MCP_URL, json={
        'jsonrpc':'2.0','id':3,'method':'tools/call',
        'params':{'name':'search_feeds','arguments':{'keyword':'旅游'}}
    }, headers=hdrs, timeout=120)
    print('search_feeds status:', resp.status_code)
    print('search_feeds response:', resp.text[:2000])
except Exception as e:
    print('search_feeds error:', e)
