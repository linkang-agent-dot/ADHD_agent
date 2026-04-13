#小红书旅游热度每日推送 - 完整版（带摘要+图片）
import requests, json, sys, os
from datetime import datetime
import time

sys.stdout.reconfigure(encoding='utf-8')
MCP_URL = 'http://localhost:18060/mcp'

def init_mcp():
    s = requests.Session()
    hdrs = {'Accept':'application/json, text/event-stream'}
    r1 = s.post(MCP_URL, json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers=hdrs)
    hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
    s.post(MCP_URL, json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs)
    return s, hdrs

def get_hot_notes_with_detail(s, hdrs):
    resp = s.post(MCP_URL, json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_feeds','arguments':{'keyword':'旅游','filters':{'sort_by':'综合'}}}}, headers=hdrs)
    data = resp.json()
    feeds = json.loads(data['result']['content'][0]['text'])['feeds']
    
    results = []
    for f in feeds:
        if f.get('modelType') == 'note' and len(results) < 5:
            card = f.get('noteCard', {})
            interact = card.get('interactInfo', {})
            note_id = f.get('id', '')
            token = f.get('xsecToken', '')
            results.append({
                'title': card.get('displayTitle', '无标题')[:35],
                'likes': interact.get('likedCount', '0'),
                'collects': interact.get('collectedCount', '0'),
                'author': card.get('user', {}).get('nickname', ''),
                'note_id': note_id,
                'token': token,
            })
    return results

def get_note_summary(s, hdrs, note_id, token):
    """获取笔记摘要"""
    try:
        time.sleep(1)  # 避免请求过快
        resp = s.post(MCP_URL, json={'jsonrpc':'2.0','id':99,'method':'tools/call','params':{'name':'get_feed_detail','arguments':{'feed_id':note_id,'xsec_token':token}}}, headers=hdrs, timeout=30)
        data = resp.json()
        note = json.loads(data['result']['content'][0]['text'])['data']['note']
        desc = note.get('desc', '')[:100]
        # 获取封面图
        images = note.get('imageList', [])
        img_url = images[0].get('urlDefault', '') if images else ''
        return desc, img_url
    except Exception as e:
        return "获取摘要失败", ""

def build_message_with_details(results):
    date = datetime.now().strftime("%Y-%m-%d")
    msg = f"📊 小红书旅游热度Top5（{date}）\n\n"
    for i, r in enumerate(results, 1):
        msg += f"{i}. {r['title']}\n"
        msg += f"   👍{r['likes']} | ⭐{r['collects']} | @{r['author']}\n"
        if r.get('summary'):
            msg += f"   📝 {r['summary']}\n"
        msg += "\n"
    msg += "---每日11:30自动推送"
    return msg

if __name__ == "__main__":
    try:
        s, hdrs = init_mcp()
        results = get_hot_notes_with_detail(s, hdrs)
        
        # 获取每条笔记的摘要
        for r in results:
            summary, img_url = get_note_summary(s, hdrs, r['note_id'], r['token'])
            r['summary'] = summary
            r['img_url'] = img_url
            print(f"已获取: {r['title'][:20]}...")
        
        msg = build_message_with_details(results)
        print("\n" + msg)
        
        # 保存图片供发送
        for i, r in enumerate(results, 1):
            if r.get('img_url'):
                try:
                    img_data = s.get(r['img_url']).content
                    path = f'C:\\Users\\linkang\\.openclaw\\workspace\\push_{i}.jpg'
                    with open(path, 'wb') as f:
                        f.write(img_data)
                    r['img_path'] = path
                except:
                    pass
        
        print(f"\n共 {len([r for r in results if r.get('img_path')])} 张图片已保存")

        # 飞书推送（与 async-notify 共用 IM API）
        try:
            _scripts = r'C:\ADHD_agent\.cursor\skills\async-notify\scripts'
            if _scripts not in sys.path:
                sys.path.insert(0, _scripts)
            from feishu_helper import send_images, get_token

            paths = [
                r['img_path']
                for r in results
                if r.get('img_path') and os.path.isfile(r['img_path'])
            ]
            token = get_token()
            send_images(paths, caption=msg, token=token)
            print("飞书推送已发送（文字+封面图）")
        except Exception as fe:
            print(f"飞书推送失败: {fe}")

    except Exception as e:
        print(f"获取失败: {e}")
