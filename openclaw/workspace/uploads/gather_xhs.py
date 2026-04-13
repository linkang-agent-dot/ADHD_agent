import requests, json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

s = requests.Session()
hdrs = {'Accept': 'application/json, text/event-stream'}
r1 = s.post('http://localhost:18060/mcp', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
    'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
}, headers=hdrs)
hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
s.post('http://localhost:18060/mcp', json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs)

all_feeds = []
for keyword in ['旅游攻略', '春季出行', '三月旅行']:
    resp = s.post('http://localhost:18060/mcp', json={
        'jsonrpc': '2.0', 'id': 4, 'method': 'tools/call',
        'params': {'name': 'search_feeds', 'arguments': {'keyword': keyword}}
    }, headers=hdrs)
    data = resp.json()
    if 'result' in data and 'content' in data['result']:
        text = data['result']['content'][0]['text']
        parsed = json.loads(text)
        feeds = parsed.get('feeds', [])
        all_feeds.extend(feeds)
        print(f"关键词'{keyword}'获取到 {len(feeds)} 条")

# 去重
seen = set()
unique = []
for f in all_feeds:
    nid = f.get('id', '')
    if nid not in seen:
        seen.add(nid)
        unique.append(f)

print(f"\n去重后共 {len(unique)} 条")

# 取点赞最高的10条
sorted_feeds = sorted(unique, key=lambda x: int(x.get('noteCard',{}).get('interactInfo',{}).get('likedCount','0') or '0'), reverse=True)

results = []
for f in sorted_feeds[:15]:
    card = f.get('noteCard', {})
    interact = card.get('interactInfo', {})
    results.append({
        'id': f.get('id'),
        'title': card.get('displayTitle', ''),
        'type': card.get('type', 'normal'),
        'user': card.get('user', {}).get('nickName', ''),
        'liked': interact.get('likedCount', '0'),
        'comment': interact.get('commentCount', '0'),
        'collected': interact.get('collectedCount', '0'),
        'shared': interact.get('sharedCount', '0'),
        'url': f"https://www.xiaohongshu.com/explore/{f.get('id')}"
    })

with open('C:/Users/linkang/.openclaw/workspace/uploads/xhs_results.json', 'w', encoding='utf-8') as fp:
    json.dump(results, fp, ensure_ascii=False, indent=2)
print("结果已保存")
