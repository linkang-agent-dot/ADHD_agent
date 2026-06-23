import requests, json, sys, os, urllib.request
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

MCP_URL = 'http://localhost:18060/mcp'
UPLOAD_DIR = r'C:\ADHD_agent\openclaw\workspace\uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_mcp():
    s = requests.Session()
    hdrs = {'Accept': 'application/json, text/event-stream'}
    r1 = s.post(MCP_URL, json={
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
                   'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
    }, headers=hdrs, timeout=15)
    hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
    s.post(MCP_URL, json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs, timeout=10)
    return s, hdrs

def call_mcp(s, hdrs, tool_name, arguments, timeout=120):
    resp = s.post(MCP_URL, json={
        'jsonrpc': '2.0', 'id': 99, 'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    }, headers=hdrs, timeout=timeout)
    result = resp.json()
    if 'result' in result:
        content = result['result']['content']
        if isinstance(content, list) and len(content) > 0:
            raw_text = content[0].get('text', '{}')
            try:
                return json.loads(raw_text)
            except:
                return {'raw': raw_text}
    return {}

def download(url, path):
    if not url:
        return False
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
            return True
    except:
        pass
    return False

print('=== 小红书旅游推送开始 ===')
s, hdrs = init_mcp()
print('MCP初始化完成')

# 验证登录
try:
    status = call_mcp(s, hdrs, 'check_login_status', {}, timeout=15)
    print('登录状态:', status)
except Exception as e:
    print('登录检查失败:', e)

print('开始搜索...')
kws = ['旅游', '旅行', '出游', '攻略', '打卡']
results = []
seen_ids = set()

for kw in kws:
    try:
        print('搜索:', kw, '...')
        raw = call_mcp(s, hdrs, 'search_feeds', {'keyword': kw}, timeout=120)
        feeds = raw.get('feeds', []) if isinstance(raw, dict) else []
        print('  获得', len(feeds), '条')
    except Exception as e:
        print('搜索', kw, '出错:', e)
        continue

    for f in feeds:
        if f.get('modelType') != 'note':
            continue
        note_id = f.get('id', '')
        if not note_id or note_id in seen_ids:
            continue
        seen_ids.add(note_id)

        card = f.get('noteCard', {})
        title = card.get('displayTitle', '')
        interact = card.get('interactInfo', {})
        cover = card.get('cover', {})

        cover_url = (cover.get('urlDefault', '') or cover.get('urlPre', '') or cover.get('url', ''))

        try:
            like = int(interact.get('likedCount', '0') or 0)
        except:
            like = 0

        if not title:
            continue

        results.append({
            'id': note_id,
            'title': title,
            'cover_url': cover_url,
            'like': like,
            'user': card.get('user', {}).get('nickName', ''),
        })

    if len(results) >= 15:
        break

results.sort(key=lambda x: x['like'], reverse=True)
feeds = results[:5]
print('获取到', len(feeds), '条内容')

today = datetime.now().strftime('%Y-%m-%d')
lines = ['小红书旅游热度Top5（' + today + '）', '']

for i, f in enumerate(feeds, 1):
    lines.append(str(i) + '. ' + f['title'])
    lines.append('   赞 ' + str(f['like']) + ' | @' + f['user'])

lines.append('')
lines.append('---每日11:00自动推送')
body = '\n'.join(lines)
print(body)

# 下载封面图
for i, f in enumerate(feeds, 1):
    if f['cover_url']:
        img_path = os.path.join(UPLOAD_DIR, 'push_' + str(i) + '.jpg')
        if download(f['cover_url'], img_path):
            print('封面已下载:', img_path)

# 保存到文件
push_data = {'feeds': feeds, 'body': body}
with open(os.path.join(UPLOAD_DIR, 'push_data.json'), 'w', encoding='utf-8') as fp:
    json.dump(push_data, fp, ensure_ascii=False, indent=2)
print('数据已保存到 push_data.json')
print('=== 完成 ===')
