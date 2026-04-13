import requests, json, os

app_id = 'cli_a934245330789ccf'
app_secret = os.environ.get('FEISHU_APP_SECRET', '')
print(f'App secret present: {bool(app_secret)}')

# Get tenant access token
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': app_id, 'app_secret': app_secret}, timeout=10)
print(f'Token response: {r.status_code}')
data = r.json()
print(f'Response: {json.dumps(data, ensure_ascii=False)}')

token = data.get('tenant_access_token', '')
if not token:
    print('NO TOKEN')
    exit(1)

# Get bot info
r2 = requests.get('https://open.feishu.cn/open-apis/bot/v3/info',
    headers={'Authorization': f'Bearer {token}'}, timeout=10)
print(f'Bot info: {json.dumps(r2.json(), ensure_ascii=False)}')

# Get recent DMs (chats with the bot)
r3 = requests.get('https://open.feishu.cn/open-apis/im/v1/chats?page_size=20',
    headers={'Authorization': f'Bearer {token}'}, timeout=10)
print(f'Chats: {json.dumps(r3.json(), ensure_ascii=False)[:2000]}')
