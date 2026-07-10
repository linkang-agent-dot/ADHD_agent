"""
使用 media-crawler-mcp (端口 18080) 获取小红书旅游内容并推送
"""
import requests, json, sys, os, urllib.request, time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

MCP_URL = 'http://127.0.0.1:18080'
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

def init_mcp():
    """连接 SSE 获取 session_id，读到就关闭"""
    import threading, queue
    s = requests.Session()
    r = s.get(f'{MCP_URL}/sse', stream=True, timeout=60)
    q = queue.Queue()
    
    def reader():
        try:
            for line in r.iter_lines():
                q.put(line.decode())
        except Exception as e:
            q.put(f'ERROR:{e}')
        finally:
            q.put(None)
    
    t = threading.Thread(target=reader, daemon=True)
    t.start()
    
    session_id = None
    endpoint = None
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            item = q.get(timeout=5)
        except queue.Empty:
            continue
        if item is None:
            break
        if item.startswith('data:'):
            data = item[5:].strip()
            if 'session_id' in data:
                try:
                    obj = json.loads(data)
                    session_id = obj.get('session_id', '')
                except:
                    pass
            elif data.startswith('/') and 'session_id' in data:
                endpoint = data.split('?session_id=')[0] if '?session_id=' in data else data
            if session_id and endpoint:
                break
    r.close()
    if not endpoint or not session_id:
        raise Exception(f'无法获取 session_id，endpoint={endpoint}, session_id={session_id}')
    full_endpoint = f'{MCP_URL}{endpoint}'
    return s, full_endpoint, session_id

def call_mcp(s, endpoint, session_id, tool_name, arguments, timeout=120):
    """调用 MCP 工具"""
    hdrs = {'Content-Type': 'application/json', 'Mcp-Session-Id': session_id}
    resp = s.post(endpoint, json={
        'jsonrpc': '2.0', 'id': 99, 'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    }, headers=hdrs, timeout=timeout)
    return json.loads(resp.json()['result']['content'][0]['text'])

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
        print('未找到飞书 webhook', file=sys.stderr)
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

def send_feishu_image(text, image_path):
    """发送图片+文字到飞书"""
    webhook = get_webhook()
    if not webhook:
        print('未找到飞书 webhook', file=sys.stderr)
        return False
    if not os.path.exists(image_path):
        print(f'图片不存在: {image_path}', file=sys.stderr)
        return False
    try:
        import base64
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
        payload = {
            'msg_type': 'image',
            'content': {'image_base64': img_data}
        }
        # 先发文字
        if text:
            send_feishu_text(text)
        # 再发图片
        payload_enc = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(webhook, data=payload_enc,
                                     headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as e:
        print(f'飞书图片推送失败: {e}', file=sys.stderr)
        return False

def main():
    print('=== 小红书旅游推送开始 (media-crawler-mcp) ===')
    
    s, endpoint, session_id = init_mcp()
    print(f'SSE 连接成功: session_id={session_id}')
    
    # 搜索旅游关键词
    kws = ['旅游攻略', '旅行打卡', '出游推荐']
    all_results = []
    seen_ids = set()
    
    for kw in kws:
        try:
            raw = call_mcp(s, endpoint, session_id, 'crawl_search', {
                'platform': 'xhs',
                'store_type': 'json',
                'keywords': kw
            }, timeout=120)
            print(f'  搜索 [{kw}]: 获得数据', file=sys.stderr)
            
            # 解析返回数据
            if isinstance(raw, dict):
                items = raw.get('data', []) or raw.get('feeds', []) or []
            elif isinstance(raw, list):
                items = raw
            else:
                items = []
            
            for item in items:
                note_id = item.get('id', '') or item.get('note_id', '')
                if not note_id or note_id in seen_ids:
                    continue
                seen_ids.add(note_id)
                
                title = item.get('title', '') or item.get('display_title', '')
                if not title:
                    continue
                
                # 封面图
                cover_url = ''
                cover = item.get('cover', {}) or {}
                if isinstance(cover, str):
                    cover_url = cover
                else:
                    cover_url = (cover.get('urlDefault', '') or cover.get('urlPre', '')
                                 or cover.get('url', '') or '')
                
                # 点赞
                interact = item.get('interact_info', {}) or item.get('interactInfo', {})
                try:
                    like = int(interact.get('liked_count', '0') or interact.get('likedCount', '0') or 0)
                except:
                    like = 0
                
                # 作者
                user = item.get('user', {}) or {}
                if isinstance(user, dict):
                    user_nick = user.get('nickname', '') or user.get('nickName', '')
                else:
                    user_nick = str(user)
                
                all_results.append({
                    'id': note_id,
                    'title': title,
                    'cover_url': cover_url,
                    'like': like,
                    'user': user_nick,
                })
        except Exception as e:
            print(f'  搜索 [{kw}] 出错: {e}', file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        
        if len(all_results) >= 10:
            break
    
    # 按点赞排序取 Top5
    all_results.sort(key=lambda x: x['like'], reverse=True)
    feeds = all_results[:5]
    print(f'获取到 {len(feeds)} 条内容')
    
    today = datetime.now().strftime('%Y-%m-%d')
    push_texts = []
    
    for i, f in enumerate(feeds, 1):
        title = f['title']
        like = f['like']
        user = f['user']
        cover_url = f['cover_url']
        
        text = f'📌 {title}\n👍 {like}  |  @{user}'
        push_texts.append(text)
        
        # 下载封面
        img_path = os.path.join(UPLOAD_DIR, f'push_{i}.jpg')
        if cover_url:
            downloaded = download(cover_url, img_path)
            if downloaded:
                print(f'  封面已下载: {img_path}', file=sys.stderr)
            else:
                print(f'  封面下载失败: {cover_url}', file=sys.stderr)
    
    # 发飞书：每条内容一条消息（文字+图片）
    header = f'📊 小红书旅游热度Top5（{today}）\n'
    for i, t in enumerate(push_texts, 1):
        img_path = os.path.join(UPLOAD_DIR, f'push_{i}.jpg')
        send_feishu_text(header + t)
        if os.path.exists(img_path):
            send_feishu_image('', img_path)
    
    # 保存数据
    body_lines = [f'📊 小红书旅游热度Top5（{today}）', '']
    for i, f in enumerate(feeds, 1):
        body_lines.append(f'{i}. {f["title"]}')
        body_lines.append(f'   👍 {f["like"]} | @{f["user"]}')
    body_lines.append('')
    body_lines.append('---每日11:30自动推送')
    
    with open(os.path.join(UPLOAD_DIR, 'push_data.json'), 'w', encoding='utf-8') as fp:
        json.dump({'feeds': feeds, 'body': '\n'.join(body_lines)}, fp, ensure_ascii=False, indent=2)
    
    print('=== 完成 ===', file=sys.stderr)

if __name__ == '__main__':
    main()
