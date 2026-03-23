import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
s = requests.Session()
hdrs = {'Accept':'application/json, text/event-stream'}
r1 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers=hdrs)
hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs)

# 重试获取失败的
top_notes = [
    ('690577db0000000007037a27', 'ABCWd2LW-U6UclbEh_Rwz4k-THqmDZ-tyIApEPhmXoGFo=', '3_目的地推荐'),
    ('68e63376000000000700115c', 'ABVpZG9P7PYEpneCmXqC8T3raeavKlL-xoNE8_yHF7DW8=', '5_九寨沟'),
    ('69a8fb42000000002801f441', 'ABWQLAyV8L9gntQ54gTrjkI7ccG9fk4bJbXCOL7Kkuw3I=', '6_春季目的地'),
]

for i, (note_id, token, filename) in enumerate(top_notes, 3):
    print(f"\n=== {i}. 重试获取 ===")
    import time
    time.sleep(2)
    resp = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'get_feed_detail','arguments':{'feed_id':note_id,'xsec_token':token}}}, headers=hdrs, timeout=30)
    data = resp.json()
    try:
        note = json.loads(data['result']['content'][0]['text'])['data']['note']
        images = note.get('imageList', [])
        if images:
            url = images[0].get('urlDefault', '')
            if url:
                r = s.get(url, timeout=30)
                path = f'C:\\Users\\linkang\\.openclaw\\workspace\\{filename}.jpg'
                with open(path, 'wb') as f:
                    f.write(r.content)
                print(f"已保存: {path}")
    except Exception as e:
        print(f"失败: {e}")
