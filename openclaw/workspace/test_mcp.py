import requests, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

MCP_URL = 'http://localhost:18060/mcp'

def init_mcp():
    s = requests.Session()
    hdrs = {'Accept': 'application/json, text/event-stream'}
    r1 = s.post(MCP_URL, json={
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
                   'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
    }, headers=hdrs, timeout=10)
    hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
    s.post(MCP_URL, json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs)
    return s, hdrs

def call_mcp(s, hdrs, tool_name, arguments, timeout=120):
    resp = s.post(MCP_URL, json={
        'jsonrpc': '2.0', 'id': 99, 'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    }, headers=hdrs, timeout=timeout)
    return json.loads(resp.json()['result']['content'][0]['text'])

s, hdrs = init_mcp()
print('MCP initialized, session:', hdrs['Mcp-Session-Id'])

try:
    status = call_mcp(s, hdrs, 'check_login_status', {}, timeout=15)
    print('check_login_status:', json.dumps(status, ensure_ascii=False))
except Exception as e:
    print('check_login_status ERROR:', e)
