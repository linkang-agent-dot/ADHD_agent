import requests, json, os, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

app_id = 'cli_a934245330789ccf'
locations = [r'C:\Users\linkang\.openclaw\openclaw.env', r'C:\Users\linkang\.openclaw\workspace\feishu.env']
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

token_url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
r = requests.post(token_url, json={'app_id': app_id, 'app_secret': app_secret}, timeout=10)
token = r.json().get('tenant_access_token', '')

user_id = 'ou_e48f6c4c0395f45b74b51525f348678b'
headers = {'Authorization': f'Bearer {token}'}
msg_url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'

results = []
for i in range(1, 6):
    img_path = os.path.join(r'C:\Users\linkang\.openclaw\workspace\uploads', f'xhs_push_{i}.jpg')
    print(f'处理图片{i}')
    
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            data = {'image_type': 'message'}
            files = {'image': (f'xhs_push_{i}.jpg', f, 'image/jpeg')}
            upload_url = 'https://open.feishu.cn/open-apis/im/v1/images/import'
            upload_r = requests.post(upload_url, headers=headers, data=data, files=files, timeout=30)
            print(f'  upload status={upload_r.status_code}, ct={upload_r.headers.get("content-type")}')
            print(f'  response text: {upload_r.text[:200]}')
            
            try:
                upload_resp = upload_r.json()
                code = upload_resp.get('code', -1)
                print(f'  code={code}')
                if code == 0:
                    image_key = upload_resp['data']['image_key']
                    img_payload = {
                        'receive_id': user_id,
                        'msg_type': 'image',
                        'content': json.dumps({'image_key': image_key})
                    }
                    msg_r = requests.post(msg_url, headers=headers, json=img_payload, timeout=30)
                    res = msg_r.json()
                    print(f'  发送: code={res.get("code")}')
                    if res.get('code') == 0:
                        results.append(f'[{i}]图片 OK')
            except Exception as e:
                print(f'  解析失败: {e}')

print(f'\n图片发送成功: {len(results)}')
