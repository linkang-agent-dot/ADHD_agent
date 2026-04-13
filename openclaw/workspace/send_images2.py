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
msg_url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'

results = []
for i in range(1, 6):
    img_path = os.path.join(r'C:\Users\linkang\.openclaw\workspace\uploads', f'xhs_push_{i}.jpg')
    
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            img_data = f.read()
        
        # 构造 multipart/form-data 发送图片消息
        import uuid
        boundary = uuid.uuid4().hex
        
        # JSON part
        json_part = json.dumps({
            'receive_id': user_id,
            'msg_type': 'image',
            'content': json.dumps({'image_key': f'img_{i}'})
        })
        
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="request"\r\n'
            f'Content-Type: application/json\r\n\r\n'
            f'{json_part}\r\n'
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="image"; filename="xhs_push_{i}.jpg"\r\n'
            f'Content-Type: image/jpeg\r\n\r\n'
        ).encode('utf-8') + img_data + f'\r\n--{boundary}--'.encode('utf-8')
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        }
        
        msg_r = requests.post(msg_url, headers=headers, data=body, timeout=30)
        print(f'[{i}] status={msg_r.status_code}')
        try:
            res = msg_r.json()
            print(f'  code={res.get("code")}')
            if res.get('code') == 0:
                results.append(f'[{i}] OK')
            else:
                print(f'  error: {res}')
        except:
            print(f'  raw: {msg_r.text[:200]}')

print(f'\n成功: {len(results)}/5')
