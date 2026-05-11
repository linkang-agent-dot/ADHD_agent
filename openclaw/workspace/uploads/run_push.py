import requests, json, sys, os, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

MCP_URL = 'http://localhost:18060/mcp'
s = requests.Session()
h = {'Accept': 'application/json, text/event-stream'}
r1 = s.post(MCP_URL, json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers=h, timeout=10)
sid = r1.headers.get('Mcp-Session-Id','')
h['Mcp-Session-Id'] = sid
s.post(MCP_URL, json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=h)

kws = ['旅游', '旅行']
results = []
seen = set()

for kw in kws:
    r = s.post(MCP_URL, json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_feeds','arguments':{'keyword':kw}}}, headers=h, timeout=120)
    data = json.loads(r.text)
    try:
        content = data['result']['content']
        if isinstance(content, list):
            text = content[0].get('text', '')
            feeds_data = json.loads(text)
        else:
            feeds_data = content
    except:
        feeds_data = {}
    feeds = feeds_data.get('feeds', []) if isinstance(feeds_data, dict) else []
    for f in feeds:
        if f.get('modelType') != 'note':
            continue
        nid = f.get('id','')
        if not nid or nid in seen:
            continue
        seen.add(nid)
        card = f.get('noteCard',{})
        title = card.get('displayTitle','')
        cover = card.get('cover',{})
        cover_url = cover.get('urlDefault','') or cover.get('urlPre','') or cover.get('url','')
        try:
            like = int(card.get('interactInfo',{}).get('likedCount','0') or 0)
        except:
            like = 0
        if title:
            results.append({'id':nid,'title':title,'cover_url':cover_url,'like':like,'user':card.get('user',{}).get('nickName','')})
    if len(results) >= 5:
        break

results.sort(key=lambda x: x['like'], reverse=True)
results = results[:5]

out = json.dumps({'feeds': results}, ensure_ascii=False, indent=2)
open(r'C:\Users\linkang\.openclaw\workspace\uploads\push_data.json','w',encoding='utf-8').write(out)

today = '2026-04-27'
lines = ['小红书旅游热度Top5（{}）'.format(today),'']
for i,f in enumerate(results,1):
    lines.append('{}. {}\n   👍 {} | @{}'.format(i, f['title'], f['like'], f['user']))
lines.append('')
lines.append('---每日11:30自动推送')
body = '\n'.join(lines)
print(body)

# 下载封面图
UPLOAD_DIR = r'C:\Users\linkang\.openclaw\workspace\uploads'
for i, f in enumerate(results, 1):
    if f['cover_url']:
        img_path = os.path.join(UPLOAD_DIR, 'push_{}.jpg'.format(i))
        try:
            rr = requests.get(f['cover_url'], timeout=15)
            if rr.status_code == 200:
                with open(img_path, 'wb') as fp:
                    fp.write(rr.content)
                print('下载封面: push_{}.jpg'.format(i))
        except Exception as e:
            print('下载失败 push_{}: {}'.format(i, e))

print('=== 完成 ===')
