"""检查日报任务的 outbox 结果 + 飞书消息"""
import sys, json, requests
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.cursor\skills\async-notify\scripts')
import feishu_helper

# 读 outbox
f = r'C:\ADHD_agent\openclaw\workspace\cursor_outbox\task_20260402_235719_a5a50a.json'
raw = open(f, 'rb').read().decode('utf-8', errors='replace')
d = json.loads(raw)
print('=== outbox result ===')
print(f'status: {d.get("status")}')
print(d.get('result', '')[:2000])
print()

# 读飞书最新消息
token = feishu_helper.get_token()
chat_id = 'oc_0a0221a14304e40b0a4998028be80b5a'
url = f'https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=chat&container_id={chat_id}&page_size=2&sort_type=ByCreateTimeDesc'
r = requests.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=10)
items = r.json().get('data', {}).get('items', [])
print('=== 飞书最新消息 ===')
for item in items[:2]:
    body = item.get('body', {}).get('content', '')
    try:
        content = json.loads(body)
        text = content.get('text', '')[:800]
        print(text)
        print('---')
    except:
        print(body[:300])
