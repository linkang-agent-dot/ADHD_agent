import requests, json, os

# 读取 push_data
data = json.load(open(r'C:\Users\linkang\.openclaw\workspace\uploads\push_data.json', encoding='utf-8'))
feeds = data['feeds']

# 读取飞书 bot token
app_id = 'cli_a934245330789ccf'

# 尝试从 openclaw.env 读取
env_path = r'C:\Users\linkang\.openclaw\openclaw.env'
app_secret = ''
if os.path.exists(env_path):
    for line in open(env_path, encoding='utf-8'):
        if 'FEISHU_APP_SECRET' in line:
            app_secret = line.split('=', 1)[1].strip().strip('"\'')
            break

print(f'app_secret found: {len(app_secret) > 0}')

# 获取 tenant_access_token
token_url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
r = requests.post(token_url, json={'app_id': app_id, 'app_secret': app_secret}, timeout=10)
resp = r.json()
print(resp)
token = resp.get('tenant_access_token', '')
