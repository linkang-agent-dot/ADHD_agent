import requests, json, sys, os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 使用 MediaCrawler MCP (port 18080)
def init_sse_session():
    r = requests.get('http://127.0.0.1:18080/sse', stream=True, timeout=10)
    endpoint = None
    for line in r.iter_lines():
        line = line.decode()
        if line.startswith('data:'):
            endpoint = line[5:].strip()
            break
    r.close()
    if not endpoint:
        raise Exception('无法连接 MediaCrawler MCP')
    return endpoint

def call_tool(endpoint, tool_name, arguments):
    session_id = endpoint.split('session_id=')[1] if 'session_id=' in endpoint else ''
    resp = requests.post(f'http://127.0.0.1:18080{endpoint}', json={
        'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
        'params': {'name': tool_name, 'arguments': arguments}
    }, timeout=120)
    return json.loads(resp.json()['result']['content'][0]['text'])

UPLOAD_DIR = r'C:\Users\linkang\.openclaw\workspace\uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def download(url, path):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
            return True
    except:
        pass
    return False

def main():
    print('=== 小红书旅游推送开始 ===')
    
    endpoint = init_sse_session()
    print(f'Connected to MediaCrawler MCP')
    
    # 搜索旅游内容
    raw = call_tool(endpoint, 'crawl_search', {
        'platform': 'xhs',
        'store_type': 'json',
        'keywords': '旅游攻略'
    })
    print(f'搜索结果: {str(raw)[:300]}')
    
    items = raw if isinstance(raw, list) else raw.get('result', raw.get('data', []))
    print(f'共 {len(items)} 条')

if __name__ == '__main__':
    main()
