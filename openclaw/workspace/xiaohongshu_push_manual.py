# -*- coding: utf-8 -*-
"""获取小红书首页feeds，过滤旅游相关内容，下载封面图，推送飞书"""
import requests
import json
import os
import re
from datetime import datetime

# --- 1. 获取小红书feeds ---
session = requests.Session()
headers_req = {'Accept': 'application/json, text/event-stream'}
r1 = session.post('http://localhost:18060/mcp',
    json={'jsonrpc':'2.0','id':1,'method':'initialize',
          'params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}},
    headers=headers_req)
sid = r1.headers.get('Mcp-Session-Id','')
headers_req['Mcp-Session-Id'] = sid
session.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=headers_req)

resp = session.post('http://localhost:18060/mcp',
    json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'list_feeds','arguments':{}}},
    headers=headers_req, timeout=30)
data = resp.json()
feeds = data.get('result', {}).get('content', [{}])[0].get('text', '')
feeds_json = json.loads(feeds) if feeds else {}
feed_list = feeds_json.get('feeds', [])

print(f"获取到 {len(feed_list)} 条feeds")

# --- 2. 过滤旅游相关内容 ---
travel_keywords = ['旅游','旅行','攻略','打卡','景点','拍照','美食','酒店','民宿',
                   '度假','海滩','海岛','古镇','古城','爬山','徒步','风景','出行']
def is_travel(feed):
    title = feed.get('noteCard', {}).get('displayTitle', '')
    return any(k in title for k in travel_keywords)

travel_feeds = [f for f in feed_list if is_travel(f)]
print(f"旅游相关: {len(travel_feeds)} 条")

# --- 3. 下载封面图 ---
out_dir = r'C:\ADHD_agent\openclaw\workspace\uploads'
os.makedirs(out_dir, exist_ok=True)

today = datetime.now().strftime('%Y-%m-%d')
results = []
for i, feed in enumerate(travel_feeds[:5]):
    nc = feed.get('noteCard', {})
    title = nc.get('displayTitle', '无标题')
    nickname = nc.get('user', {}).get('nickName', '未知')
    liked = nc.get('interactInfo', {}).get('likedCount', '0')
    cover_urls = nc.get('cover', {}).get('infoList', [])
    cover_url = ''
    for cu in cover_urls:
        if cu.get('imageScene') == 'WB_DFT':
            cover_url = cu.get('url', '')
            break
    if not cover_url and cover_urls:
        cover_url = cover_urls[0].get('url', '')

    # 下载图片
    img_path = os.path.join(out_dir, f'push_{i+1}.jpg')
    img_ok = False
    if cover_url:
        try:
            rimg = requests.get(cover_url, timeout=15)
            if rimg.status_code == 200:
                with open(img_path, 'wb') as f:
                    f.write(rimg.content)
                img_ok = True
                print(f"  [{i+1}] 下载封面成功: {img_path}")
        except Exception as e:
            print(f"  [{i+1}] 下载失败: {e}")

    results.append({
        'index': i+1,
        'title': title,
        'nickname': nickname,
        'liked': liked,
        'cover_url': cover_url,
        'img_path': img_path if img_ok else '',
        'feed_id': feed.get('id',''),
        'xsec_token': feed.get('xsecToken','')
    })

# --- 4. 保存数据 ---
save_path = os.path.join(out_dir, 'push_data.json')
with open(save_path, 'w', encoding='utf-8') as f:
    json.dump({'date': today, 'results': results}, f, ensure_ascii=False, indent=2)
print(f"数据已保存: {save_path}")

# --- 5. 输出推送文本 ---
print("\n=== 推送内容 ===")
for r in results:
    print(f"[{r['index']}] {r['title']} | 作者:{r['nickname']} | 赞:{r['liked']}")
