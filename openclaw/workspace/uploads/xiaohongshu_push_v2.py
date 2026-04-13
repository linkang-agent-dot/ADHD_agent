# 小红书旅游热度每日推送 v2 - 使用 list_feeds + get_feed_detail，带封面图
import requests, json, sys, os, time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
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
    }, headers=hdrs, timeout=10)
    hdrs['Mcp-Session-Id'] = r1.headers.get('Mcp-Session-Id', '')
    s.post(MCP_URL, json={'jsonrpc': '2.0', 'method': 'notifications/initialized'}, headers=hdrs)
    return s, hdrs

def get_travel_feeds(s, hdrs):
    """获取小红书首页Feeds，筛选旅游相关内容"""
    resp = s.post(MCP_URL, json={
        'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
        'params': {'name': 'list_feeds', 'arguments': {}}
    }, headers=hdrs, timeout=30)
    
    data = resp.json()
    feeds = json.loads(data['result']['content'][0]['text'])['feeds']
    
    results = []
    travel_keywords = ['旅游', '旅行', '出游', '攻略', '打卡', '拍照', '度假', '景点']
    
    for f in feeds:
        if f.get('modelType') != 'note':
            continue
        card = f.get('noteCard', {})
        title = card.get('displayTitle', '')
        
        # 简单关键词过滤
        if not any(kw in title for kw in travel_keywords):
            continue
        
        interact = card.get('interactInfo', {})
        cover = card.get('cover', {})
        img_url = cover.get('urlDefault', '') or cover.get('urlPre', '')
        
        results.append({
            'title': title[:35],
            'likes': interact.get('likedCount', '0'),
            'collects': interact.get('collectedCount', '0'),
            'author': card.get('user', {}).get('nickname', ''),
            'note_id': f.get('id', ''),
            'token': f.get('xsecToken', ''),
            'img_url': img_url,
            'type': card.get('type', 'normal'),  # video or normal
        })
        
        if len(results) >= 5:
            break
    
    return results

def get_note_summary(s, hdrs, note_id, token):
    """获取笔记描述"""
    try:
        time.sleep(0.5)
        resp = s.post(MCP_URL, json={
            'jsonrpc': '2.0', 'id': 99, 'method': 'tools/call',
            'params': {'name': 'get_feed_detail', 'arguments': {
                'feed_id': note_id,
                'xsec_token': token,
                'load_all_comments': False,
                'limit': 1
            }}
        }, headers=hdrs, timeout=30)
        data = resp.json()
        note = json.loads(data['result']['content'][0]['text'])
        note_data = note.get('data', {}).get('note', {})
        desc = note_data.get('desc', '')[:80]
        
        # 尝试从详情中取封面图
        image_list = note_data.get('imageList', [])
        img_url = image_list[0].get('urlDefault', '') if image_list else ''
        
        return desc, img_url
    except Exception as e:
        return f"获取失败: {e}", ""

def download_image(s, url, path):
    """下载图片"""
    try:
        if not url:
            return False
        r = s.get(url, timeout=15)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
            return True
    except:
        pass
    return False

def build_message(results):
    date = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 小红书旅游热度Top5（{date}）\n\n"
    for i, r in enumerate(results, 1):
        emoji = "🎬" if r['type'] == 'video' else "📝"
        msg += f"{emoji} {i}. {r['title']}\n"
        msg += f"   👍{r['likes']} | ⭐{r['collects']} | @{r['author']}\n"
        if r.get('summary'):
            msg += f"   📝 {r['summary']}\n"
        msg += "\n"
    msg += "---每日11:30自动推送"
    return msg

if __name__ == "__main__":
    print("=== 小红书旅游推送开始 ===")
    s, hdrs = init_mcp()
    
    # 获取Feeds
    results = get_travel_feeds(s, hdrs)
    print(f"获取到 {len(results)} 条Feeds")
    
    # 获取每条笔记的详情和摘要
    for i, r in enumerate(results):
        summary, detail_img = get_note_summary(s, hdrs, r['note_id'], r['token'])
        r['summary'] = summary
        # 优先用详情接口的图，其次用列表的图
        if detail_img:
            r['img_url'] = detail_img
        print(f"  [{i+1}] {r['title'][:25]}... | 图:{bool(r['img_url'])}")
    
    # 下载封面图
    img_paths = []
    for i, r in enumerate(results):
        if r.get('img_url'):
            path = os.path.join(UPLOAD_DIR, f'push_{i+1}.jpg')
            ok = download_image(s, r['img_url'], path)
            if ok:
                img_paths.append(path)
                print(f"  图片已下载: {path}")
    
    print(f"\n共下载 {len(img_paths)} 张图片")
    
    # 打印消息
    msg = build_message(results)
    print("\n" + msg)
    
    print("\n=== 完成 ===")
