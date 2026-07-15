import requests, json, sys, base64
sys.stdout.reconfigure(encoding='utf-8')
s = requests.Session()
hdrs = {'Accept':'application/json, text/event-stream'}
r1 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers=hdrs, timeout=10)
hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id','')
s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs, timeout=10)
resp = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'get_login_qrcode','arguments':{}}}, headers=hdrs, timeout=30)
data = json.loads(resp.text)
content_list = data['result']['content']
for item in content_list:
    if item.get('type') == 'image':
        img_data = base64.b64decode(item['data'])
        with open(r'C:\ADHD_agent\openclaw\workspace\uploads\xhs_qrcode.png', 'wb') as f:
            f.write(img_data)
        print('QR saved to uploads/xhs_qrcode.png')
    elif item.get('type') == 'text':
        print('text:', item['text'])
