# -*- coding: utf-8 -*-
import requests, json, sys, os, time
sys.stdout.reconfigure(encoding='utf-8')

UPLOAD_DIR = r'C:\Users\linkang\.openclaw\workspace\uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}
r1 = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
    'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
               'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
}, headers=hdrs, timeout=10)
hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
s.post('http://localhost:18060/mcp', json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs)

# Get feeds from homepage
resp = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
    'params': {'name': 'list_feeds', 'arguments': {}}
}, headers=hdrs, timeout=30)
raw = resp.json()
content = raw.get('result', {}).get('content', [{}])[0].get('text', '')
data = json.loads(content)
all_feeds = data.get('feeds', [])
print(f'Total feeds: {len(all_feeds)}', flush=True)

# Filter for travel-related
travel_keywords = ['旅游', '旅行', '出游', '攻略', '打卡', '酒店', '机票', '民宿', '景点', '美食']
results = []
for f in all_feeds:
    if f.get('modelType') != 'note':
        continue
    card = f.get('noteCard', {})
    title = card.get('displayTitle', '')
    user = card.get('user', {}).get('nickName', '')
    interact = card.get('interactInfo', {})
    cover = card.get('cover', {})
    cover_url = cover.get('urlDefault', '') or cover.get('urlPre', '') or cover.get('url', '')
    liked = interact.get('likedCount', '0') or '0'
    for kw in travel_keywords:
        if kw in title:
            try:
                if '万' in liked:
                    like_count = int(liked.replace('万+', '').replace('万', '')) * 10000
                else:
                    like_count = int(liked)
            except:
                like_count = 0
            results.append({
                'title': title,
                'user': user,
                'cover_url': cover_url,
                'like': like_count,
                'raw_liked': liked
            })
            break

results.sort(key=lambda x: x['like'], reverse=True)
top5 = results[:5]
print(f'Travel feeds found: {len(top5)}', flush=True)
for i, r in enumerate(top5, 1):
    print(f'{i}. {r["title"]} | {r["raw_liked"]} | {r["user"]}', flush=True)

# Download covers
for i, r in enumerate(top5, 1):
    if r['cover_url']:
        img_path = os.path.join(UPLOAD_DIR, f'push_{i}.jpg')
        try:
            rr = requests.get(r['cover_url'], timeout=15)
            if rr.status_code == 200:
                with open(img_path, 'wb') as ff:
                    ff.write(rr.content)
                print(f'Downloaded cover {i}: {img_path}', flush=True)
        except Exception as e:
            print(f'Download error {i}: {e}', flush=True)

# Save push data
with open(os.path.join(UPLOAD_DIR, 'push_data.json'), 'w', encoding='utf-8') as fp:
    json.dump({'feeds': top5}, fp, ensure_ascii=False, indent=2)

print('Script done', flush=True)