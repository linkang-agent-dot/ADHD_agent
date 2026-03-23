#小红书旅游热度每日推送
import requests, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

def get_xiaohongshu_hot():
    s = requests.Session()
    hdrs = {'Accept':'application/json, text/event-stream'}
    r1 = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}}, headers=hdrs)
    hdrs['Mcp-Session-Id'] = r1.headers['Mcp-Session-Id']
    s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','method':'notifications/initialized'}, headers=hdrs)
    
    # 搜索旅游热度笔记
    resp = s.post('http://localhost:18060/mcp', json={'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'search_feeds','arguments':{'keyword':'旅游','filters':{'sort_by':'综合'}}}}, headers=hdrs)
    data = resp.json()
    feeds = json.loads(data['result']['content'][0]['text'])['feeds']
    
    # 取热度前5
    results = []
    for f in feeds:
        if f.get('modelType') == 'note' and len(results) < 5:
            card = f.get('noteCard', {})
            interact = card.get('interactInfo', {})
            results.append({
                'title': card.get('displayTitle', '无标题')[:35],
                'likes': interact.get('likedCount', '0'),
                'collects': interact.get('collectedCount', '0'),
                'author': card.get('user', {}).get('nickname', ''),
            })
    
    # 生成消息
    msg = "📊 小红书旅游热度Top5（每日更新）\n\n"
    for i, r in enumerate(results, 1):
        msg += f"{i}. {r['title']}\n"
        msg += f"   👍{r['likes']} | ⭐{r['collects']} | @{r['author']}\n\n"
    msg += "---"
    return msg

if __name__ == "__main__":
    msg = get_xiaohongshu_hot()
    print(msg)
