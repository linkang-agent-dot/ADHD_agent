import requests, json, time, sys, os

sys.stdout.reconfigure(encoding='utf-8')

# 先检查 MediaCrawler 的 data 目录
data_dir = r'C:\ADHD_agent\media-crawler-mcp\data'
if os.path.exists(data_dir):
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            fpath = os.path.join(root, f)
            print(f"Found: {fpath}")
else:
    print(f"Data dir does not exist: {data_dir}")

# 尝试触发搜索并立即检查
r = requests.get('http://127.0.0.1:18080/sse', stream=True, timeout=10)
endpoint = None
for line in r.iter_lines():
    line = line.decode('utf-8', errors='ignore')
    if line.startswith('data:'):
        endpoint = line[5:].strip()
        break
r.close()

if not endpoint:
    print("SSE连接失败")
    exit()

time.sleep(0.5)

resp = requests.post(f'http://127.0.0.1:18080{endpoint}', json={
    'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
    'params': {'name': 'crawl_search', 'arguments': {
        'platform': 'xhs',
        'store_type': 'json',
        'keywords': '旅游攻略 三月'
    }}
}, timeout=10)
print(f"Search req status: {resp.status_code}")
print(f"Search req response: {resp.text[:500]}")

# 等15秒再检查文件
time.sleep(15)
if os.path.exists(data_dir):
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            fpath = os.path.join(root, f)
            print(f"Found after search: {fpath}")
else:
    print("Still no data dir")
