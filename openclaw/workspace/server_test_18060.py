import requests, json
s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}
try:
    r1 = s.post('http://127.0.0.1:18060/mcp', json={
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
                   'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
    }, headers=hdrs, timeout=5)
    hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
    r2 = s.post('http://127.0.0.1:18060/mcp', json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs, timeout=5)
    print(f"INIT OK, Session-Id: {hdrs['Mcp-Session-Id'][:20]}...")
    resp = s.post('http://127.0.0.1:18060/mcp', json={
        'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
        'params': {'name': 'check_login_status', 'arguments': {}}
    }, headers=hdrs, timeout=10)
    print(f"TOOL CALL STATUS: {resp.status_code}")
    print(resp.text[:300])
except Exception as e:
    print(f"ERR:{e}")
