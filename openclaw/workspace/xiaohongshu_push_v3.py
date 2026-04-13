import requests, json, sys, os, urllib.request
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

MCP_URL = 'http://localhost:18060/mcp'
UPLOAD_DIR = r'C:\Users\linkang\.openclaw\workspace\uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 飞书 webhook（从 workspace 读取）
WEBHOOK_FILE = r'C:\Users\linkang\.openclaw\workspace\MCP_CONFIG.md'
FEISHU_WEBHOOK = None

def get_webhook():
    global FEISHU_WEBHOOK
    if FEISHU_WEBHOOK:
        return FEISHU_WEBHOOK
    try:
        import re
        content = open(WEBHOOK_FILE, 'r', encoding='utf-8').read()
        m = re.search(r'https://open[^\s"]+feishu[^\s"]+', content)
        if m:
            FEISHU_WEBHOOK = m.group()
    except:
        pass
    return FEISHU_WEBHOOK

def init_mcp():
    s = requests.Session()
    hdrs = {'Accept': 'application/json, text/event-stream'}
    r1 = s.post(MCP_URL, json={
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
                   'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
    }, headers=hdrs, timeout=10)
    hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
    s.post(MCP_URL, json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs)
    return s, hdrs

def call_mcp(s, hdrs, tool_name, arguments, timeout=120):
    resp = s.post(MCP_URL, json={
        'jsonrpc': '2.0', 'id': 99, 'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    }, headers=hdrs, timeout=timeout)
    return json.loads(resp.json()['result']['content'][0]['text'])

def get_travel_feeds(s, hdrs):
    kws = ['旅游', '旅行', '出游', '攻略', '打卡']
    results = []
    seen_ids = set()

    for kw in kws:
        try:
            raw = call_mcp(s, hdrs, 'search_feeds', {'keyword': kw}, timeout=120)
            feeds = raw.get('feeds', [])
        except Exception as e:
            print(f'搜索 {kw} 出错: {e}', file=sys.stderr)
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

            # cover url - try multiple fields
            cover_url = (cover.get('urlDefault', '') or cover.get('urlPre', '')
                         or cover.get('url', ''))

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
    return results[:5]

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

def send_feishu_text(text):
    webhook = get_webhook()
    if not webhook:
        print('未找到飞书 webhook，无法推送', file=sys.stderr)
        return False
    try:
        payload = json.dumps({'msg_type': 'text', 'content': {'text': text}}).encode('utf-8')
        req = urllib.request.Request(webhook, data=payload,
                                     headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f'飞书推送失败: {e}', file=sys.stderr)
        return False

def main():
    print('=== 小红书旅游推送开始 ===')
    s, hdrs = init_mcp()

    # 验证登录
    try:
        status = call_mcp(s, hdrs, 'check_login_status', {}, timeout=15)
        print(f'登录状态: {status}')
    except Exception as e:
        print(f'登录检查失败: {e}', file=sys.stderr)

    feeds = get_travel_feeds(s, hdrs)
    print(f'获取到 {len(feeds)} 条内容')

    today = datetime.now().strftime('%Y-%m-%d')
    lines = [f'📊 小红书旅游热度Top5（{today}）', '']

    push_texts = []
    for i, f in enumerate(feeds, 1):
        title = f['title']
        like = f['like']
        user = f['user']
        cover_url = f['cover_url']

        line = f'{i}. {title}\n   👍 {like} | @{user}'
        lines.append(line)
        push_texts.append(f'📌 {title}\n👍 {like} | @{user}')

        if cover_url:
            img_path = os.path.join(UPLOAD_DIR, f'xhs_push_{i}.jpg')
            if download(cover_url, img_path):
                print(f'  封面已下载: {img_path}', file=sys.stderr)

    lines.append('')
    lines.append('---每日11:30自动推送')
    body = '\n'.join(lines)
    print(body)

    # 发飞书
    if push_texts:
        header = f'📊 小红书旅游热度Top5（{today}）\n'
        for t in push_texts:
            send_feishu_text(header + t)
    else:
        send_feishu_text(body)

    # 保存
    with open(os.path.join(UPLOAD_DIR, 'push_data.json'), 'w', encoding='utf-8') as fp:
        json.dump({'feeds': feeds, 'body': body}, fp, ensure_ascii=False, indent=2)

    print('=== 完成 ===', file=sys.stderr)

if __name__ == '__main__':
    main()
