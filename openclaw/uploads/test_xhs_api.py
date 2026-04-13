import requests, json, sys

sys.stdout.reconfigure(encoding='utf-8')

# 直接调小红书搜索API（移动端接口，可能不需要登录也能搜）
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 MicroMessenger/8.0.0 NetType/WIFI Language/zh_CN',
    'Referer': 'https://servicewechat.com/',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
}

# 试试移动端搜索接口
resp = requests.get(
    'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes',
    params={
        'keyword': '旅游攻略',
        'page': 1,
        'page_size': 20,
        'sort': 'general',
        'note_type': 0,
    },
    headers=headers,
    timeout=10
)
print(f"Status: {resp.status_code}")
print(f"Headers: {dict(resp.headers)}")
print(f"Content: {resp.text[:2000]}")
