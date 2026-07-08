import requests, json, sys, os, urllib.request, threading, queue
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

UPLOAD_DIR = r'C:\Users\linkang\.openclaw\workspace\uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

results = queue.Queue()

def read_sse(url):
    try:
        r = requests.get(url, stream=True, timeout=30)
        for line in r.iter_lines():
            line = line.decode()
            if line.startswith('data:'):
                results.put(line[5:].strip())
    except Exception as e:
        results.put(f'ERROR:{e}')

def connect_sse():
    sse_url = 'http://127.0.0.1:18080/sse'
    t = threading.Thread(target=read_sse, args=(sse_url,), daemon=True)
    t.start()
    endpoint = results.get(timeout=10)
    if endpoint.startswith('ERROR'):
        raise Exception(endpoint)
    return endpoint

def send_raw(endpoint, payload):
    msg_url = f'http://127.0.0.1:18080{endpoint}'
    requests.post(msg_url, json=payload, timeout=120)
    
def recv_response():
    return results.get(timeout=130)

def init_mcp(endpoint):
    send_raw(endpoint, {
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
                   'clientInfo': {'name': 'openclaw', 'version': '1.0'}}
    })
    recv_response()
    send_raw(endpoint, {'jsonrpc': '2.0', 'method': 'notifications/initialized'})

def call_tool(endpoint, tool_name, arguments, timeout=120):
    rid = 99
    send_raw(endpoint, {
        'jsonrpc': '2.0', 'id': rid, 'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    })
    resp = recv_response()
    data = json.loads(resp)
    content = data.get('result', {}).get('content', [])
    if content:
        text = content[0].get('text', '')
        return json.loads(text)
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
    
    endpoint = connect_sse()
    print(f'已连接 MCP，endpoint: {endpoint}')
    
    init_mcp(endpoint)
    print('MCP 初始化完成')

    kws = ['旅游攻略', '旅行推荐', '暑期出游']
    all_results = []
    seen_ids = set()

    for kw in kws:
        print(f'搜索关键词: {kw}')
        try:
            raw = call_tool(endpoint, 'crawl_search', {
                'platform': 'xhs',
                'store_type': 'json',
                'keywords': kw
            }, timeout=120)
            items = raw if isinstance(raw, list) else []
            print(f'  获取到 {len(items)} 条')
            for item in items:
                note_id = str(item.get('note_id', '') or item.get('id', ''))
                if not note_id or note_id in seen_ids:
                    continue
                seen_ids.add(note_id)
                
                title = item.get('title', '')
                liked = item.get('liked_count', item.get('like_count', 0))
                user = item.get('nickname', '')
                cover = item.get('cover', {})
                if isinstance(cover, dict):
                    cover_url = cover.get('url_default', cover.get('url', ''))
                elif isinstance(cover, str):
                    cover_url = cover
                else:
                    cover_url = ''
                
                if not title:
                    continue
                
                all_results.append({
                    'id': note_id,
                    'title': title,
                    'cover_url': cover_url,
                    'like': liked,
                    'user': user
                })
                print(f'    {title[:30]}... | 👍{liked} | @{user}')
        except Exception as e:
            print(f'  搜索 {kw} 出错: {e}', file=sys.stderr)
        
        if len(all_results) >= 15:
            break

    all_results.sort(key=lambda x: int(x.get('like', 0) or 0), reverse=True)
    feeds = all_results[:5]
    print(f'获取到 {len(feeds)} 条内容')

    today = datetime.now().strftime('%Y-%m-%d')
    
    push_items = []
    for i, f in enumerate(feeds, 1):
        title = f['title']
        like = f['like']
        user = f['user']
        cover_url = f['cover_url']
        
        text = f'📌 {title}\n👍 {like} | @{user}'
        push_items.append((text, cover_url, i))
        print(f'{i}. {title} | 👍{like} | @{user} | {cover_url}')

    # 下载封面
    downloaded = {}
    for text, cover_url, i in push_items:
        if cover_url:
            img_path = os.path.join(UPLOAD_DIR, f'push_{i}.jpg')
            if download(cover_url, img_path):
                print(f'  封面已下载: {img_path}')
                downloaded[i] = img_path

    # 发飞书 - 每条发一条消息
    for text, _, i in push_items:
        send_feishu_text(text)
        print(f'  已推送: {text[:50]}...')

    # 保存数据
    with open(os.path.join(UPLOAD_DIR, 'push_data.json'), 'w', encoding='utf-8') as fp:
        json.dump({'feeds': feeds}, fp, ensure_ascii=False, indent=2)

    print('=== 完成 ===')

if __name__ == '__main__':
    main()
