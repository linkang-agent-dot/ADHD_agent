import requests, json, os, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 读取 push_data
data = json.load(open(r'C:\Users\linkang\.openclaw\workspace\uploads\push_data.json', encoding='utf-8'))
feeds = data['feeds']
print(f'共{len(feeds)}条内容')

# 读取飞书 bot token
app_id = 'cli_a934245330789ccf'
locations = [
    r'C:\Users\linkang\.openclaw\openclaw.env',
    r'C:\Users\linkang\.openclaw\workspace\feishu.env',
]
app_secret = ''
for p in locations:
    if os.path.exists(p):
        for line in open(p, encoding='utf-8').read().splitlines():
            if 'FEISHU_APP_SECRET' in line:
                app_secret = line.split('=', 1)[1].strip().strip('"\'')
                break
    if app_secret:
        break

if not app_secret:
    app_secret = os.environ.get('FEISHU_APP_SECRET', '')

print(f'app_secret found: {len(app_secret) > 0}')

# 获取 tenant_access_token
token_url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
r = requests.post(token_url, json={'app_id': app_id, 'app_secret': app_secret}, timeout=10)
resp = r.json()
token = resp.get('tenant_access_token', '')
print(f'token: {token[:20]}...')

if not token:
    print('ERROR: 获取 token 失败')
    exit(1)

user_id = 'ou_e48f6c4c0395f45b74b51525f348678b'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
today = '2026-04-12'

results = []

for i, f in enumerate(feeds, 1):
    title = f['title']
    like = f['like']
    user = f['user']
    img_path = os.path.join(r'C:\Users\linkang\.openclaw\workspace\uploads', f'xhs_push_{i}.jpg')

    text = f'[{today}] {i}. {title} | {like}赞 @{user}'

    # 发文字
    payload = {
        'receive_id': user_id,
        'msg_type': 'text',
        'content': json.dumps({'text': text})
    }
    msg_url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'
    msg_r = requests.post(msg_url, headers=headers, json=payload, timeout=30)
    res = msg_r.json()
    code = res.get('code', -1)
    print(f'文字消息{i}: code={code}')
    if code == 0:
        results.append(f'[{i}] OK')
    else:
        print(f'  失败: {res}')

    # 发图片
    if os.path.exists(img_path):
        with open(img_path, 'rb') as img_file:
            files = {'image': (f'xhs_push_{i}.jpg', img_file, 'image/jpeg')}
            upload_url = 'https://open.feishu.cn/open-apis/im/v1/images'
            upload_r = requests.post(upload_url, headers={'Authorization': f'Bearer {token}'}, files=files, timeout=30)
            upload_resp = upload_r.json()
            code = upload_resp.get('code', -1)
            print(f'图片{i}上传: code={code}')
            if code == 0:
                image_key = upload_resp['data']['image_key']
                img_payload = {
                    'receive_id': user_id,
                    'msg_type': 'image',
                    'content': json.dumps({'image_key': image_key})
                }
                img_msg_r = requests.post(msg_url, headers=headers, json=img_payload, timeout=30)
                img_res = img_msg_r.json()
                img_code = img_res.get('code', -1)
                print(f'图片消息{i}: code={img_code}')
                if img_code == 0:
                    results.append(f'[{i}]图片 OK')
            else:
                print(f'  上传失败: {upload_resp}')

print('\n=== 推送结果 ===')
for r in results:
    print(r)
print(f'成功: {len(results)}/{len(feeds)*2}')
