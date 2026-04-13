"""读取飞书最近消息，验证发送内容是否正常"""
import sys
import json
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.cursor\skills\async-notify\scripts')
import feishu_helper

token = feishu_helper.get_token()
chat_id = 'oc_0a0221a14304e40b0a4998028be80b5a'
url = f'https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=chat&container_id={chat_id}&page_size=5&sort_type=ByCreateTimeDesc'
headers = {'Authorization': f'Bearer {token}'}
r = requests.get(url, headers=headers, timeout=10)
data = r.json()
items = data.get('data', {}).get('items', [])

for i, item in enumerate(items):
    msg_type = item.get('msg_type')
    body_raw = item.get('body', {}).get('content', '')
    ts = item.get('create_time', '')
    print(f'--- 消息 {i+1} [{msg_type}] ts={ts} ---')
    try:
        content = json.loads(body_raw)
        if msg_type == 'text':
            text = content.get('text', '')
            print(text[:500])
        elif msg_type == 'post':
            zh = content.get('zh_cn', {})
            print(f'标题: {zh.get("title", "")}')
            rows = zh.get('content', [])
            for row in rows[:5]:
                line_parts = []
                for elem in row:
                    line_parts.append(elem.get('text', ''))
                print('  ' + ''.join(line_parts))
    except Exception as e:
        print(f'解析失败: {e}')
        print(body_raw[:300])
    print()
