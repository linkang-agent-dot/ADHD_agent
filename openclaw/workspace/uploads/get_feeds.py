# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\linkang\.openclaw\workspace\uploads\xhs_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
parsed = json.loads(data['result']['content'][0]['text'])
feeds = parsed['feeds']
with open(r'C:\Users\linkang\.openclaw\workspace\uploads\feeds_summary.txt', 'w', encoding='utf-8') as out:
    for i, f in enumerate(feeds[:5]):
        nc = f['noteCard']
        title = nc.get('displayTitle', '(无标题)')
        user = nc['user']['nickName']
        fid = f['id']
        liked = nc['interactInfo']['likedCount']
        collected = nc['interactInfo']['collectedCount']
        shared = nc['interactInfo']['sharedCount']
        line = f'{i+1}|{title}|{user}|{fid}|{liked}|{collected}|{shared}'
        print(line)
        out.write(line + '\n')
