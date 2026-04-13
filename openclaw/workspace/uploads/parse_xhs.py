# -*- coding: utf-8 -*-
import json, sys, os, requests

with open(r'C:\Users\linkang\.openclaw\workspace\uploads\xhs_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

content = data['result']['content']
print(f'Content type: {type(content)}')
print(f'Content len: {len(content)}')

item = content[0]
print(f'Item 0 type: {item["type"]}')
txt = item['text']
print(f'Text type: {type(txt)}')

parsed = json.loads(txt)
feeds = parsed['feeds']
print(f'\nTotal feeds: {len(feeds)}\n')

os.makedirs(r'C:\ADHD_agent\openclaw\workspace\uploads', exist_ok=True)

for i, feed in enumerate(feeds[:5]):
    nc = feed['noteCard']
    title = nc.get('displayTitle', '(无标题)')
    user = nc['user']['nickName']
    liked = nc['interactInfo']['likedCount']
    collected = nc['interactInfo']['collectedCount']
    shared = nc['interactInfo']['sharedCount']
    cover_url = nc['cover'].get('urlDefault', '') or nc['cover'].get('urlPre', '')
    fid = feed['id']
    xtoken = feed.get('xsecToken', '')

    print(f'{i+1}. {title}')
    print(f'   @{user} | 赞:{liked} 收藏:{collected} 转发:{shared}')
    print(f'   ID: {fid}')
    print(f'   Cover: {cover_url}')
    print(f'   xsecToken: {xtoken[:30]}...')
    print()

    # Download cover image
    if cover_url:
        img_path = rf'C:\ADHD_agent\openclaw\workspace\uploads\push_{i+1}.jpg'
        try:
            r = requests.get(cover_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(img_path, 'wb') as imgf:
                    imgf.write(r.content)
                print(f'   [图片已保存: {img_path} ({len(r.content)} bytes)]')
            else:
                print(f'   [图片下载失败: {r.status_code}]')
        except Exception as e:
            print(f'   [图片下载异常: {e}]')

# Save parsed feeds for reference
with open(r'C:\Users\linkang\.openclaw\workspace\uploads\xhs_feeds.json', 'w', encoding='utf-8') as f:
    json.dump(feeds[:5], f, ensure_ascii=False, indent=2)
