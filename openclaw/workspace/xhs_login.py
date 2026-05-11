import requests, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
s = requests.Session()
hdrs = {'Accept':'application/json, text/event-stream'}
r1 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers=hdrs, timeout=10)
hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs, timeout=10)
resp = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'get_login_qrcode','arguments':{}}}, headers=hdrs, timeout=30)
result = resp.json()
print(json.dumps(result, ensure_ascii=False))
# Save session headers for next call
import pickle
with open('xhs_session.pkl', 'wb') as f:
    pickle.dump(hdrs, f)