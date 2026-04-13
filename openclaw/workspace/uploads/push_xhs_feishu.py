# -*- coding: utf-8 -*-
import json, sys, os, requests

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\linkang\.openclaw\workspace\uploads\xhs_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

content = data['result']['content']
parsed = json.loads(content[0]['text'])
feeds = parsed['feeds']

os.makedirs(r'C:\ADHD_agent\openclaw\workspace\uploads', exist_ok=True)

results = []
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

    img_path = rf'C:\ADHD_agent\openclaw\workspace\uploads\push_{i+1}.jpg'

    item = {
        'index': i+1,
        'title': title,
        'user': user,
        'liked': liked,
        'collected': collected,
        'shared': shared,
        'cover_url': cover_url,
        'feed_id': fid,
        'xsec_token': xtoken,
        'img_path': img_path
    }
    results.append(item)
    print(f'{i+1}. title={title} user={user}')

# Save results
with open(r'C:\Users\linkang\.openclaw\workspace\uploads\push_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('Results saved')
