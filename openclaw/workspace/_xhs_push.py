import requests, json, time, sys

s = requests.Session()
hdrs = {'Accept':'application/json, text/event-stream'}

# initialize
try:
    r1 = s.post('http://localhost:18060/mcp', 
        json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, 
        headers=hdrs, timeout=30)
    print('init status:', r1.status_code)
    if r1.status_code != 200:
        print('init response:', r1.text[:500])
        sys.exit(1)
    hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
except Exception as e:
    print('init error:', e)
    sys.exit(1)

# initialized
try:
    s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs, timeout=10)
except Exception as e:
    print('initialized notification error:', e)

# search
try:
    resp = s.post('http://localhost:18060/mcp', 
        json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_feeds','arguments':{'keyword':'旅游攻略'}}}, 
        headers=hdrs, timeout=180)
    print('search response:', resp.text[:3000])
except Exception as e:
    print('search error:', e)
