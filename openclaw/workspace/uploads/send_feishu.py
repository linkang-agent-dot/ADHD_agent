import requests, json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

app_id = 'cli_a934245330789ccf'
app_secret = os.environ.get('FEISHU_APP_SECRET', '')
open_id = 'ou_e48f6c4c0395f45b74b51525f348678b'

# Get token
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': app_id, 'app_secret': app_secret}, timeout=10)
token = r.json().get('tenant_access_token', '')
print('Token OK:', bool(token))
if not token:
    print('Failed to get token:', r.json())
    sys.exit(1)

headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

upload_dir = r'C:\Users\linkang\.openclaw\workspace\uploads'
push_data = json.load(open(os.path.join(upload_dir, 'push_data.json'), 'r', encoding='utf-8'))
feeds = push_data['feeds']

for i, f in enumerate(feeds, 1):
    title = f['title']
    author = f['user']
    likes = f['like']
    img_path = os.path.join(upload_dir, f'xhs_push_{i}.jpg')

    print(f'\n--- Sending #{i} ---')

    image_key = None
    if os.path.exists(img_path):
        with open(img_path, 'rb') as fp:
            img_data = fp.read()
        files = {'image': (f'push_{i}.jpg', img_data, 'image/jpeg')}
        rimg = requests.post('https://open.feishu.cn/open-apis/im/v1/images',
            headers={'Authorization': 'Bearer ' + token},
            data={'image_type': 'message'},
            files=files, timeout=15)
        img_resp = rimg.json()
        print('Image upload code:', img_resp.get('code'))
        if img_resp.get('code') == 0:
            image_key = img_resp.get('data', {}).get('image_key', '')
            print('Image key:', image_key)

    text = f'📌 {title}\n👍 {likes} | @{author}'
    if image_key:
        payload = {
            'receive_id': open_id,
            'msg_type': 'post',
            'content': json.dumps({
                'zh_cn': {
                    'title': f'小红书旅游热度 #{i}',
                    'content': [[
                        {'tag': 'text', 'text': text},
                        {'tag': 'img', 'image_key': image_key}
                    ]]
                }
            })
        }
    else:
        payload = {
            'receive_id': open_id,
            'msg_type': 'text',
            'content': json.dumps({'text': text})
        }

    send_url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id'
    rsend = requests.post(send_url, headers=headers, json=payload, timeout=15)
    resp = rsend.json()
    print('Send code:', resp.get('code'), '| msg:', resp.get('msg'))
    if resp.get('code') != 0:
        print('Full resp:', json.dumps(resp, ensure_ascii=False))

print('\nAll done!')
