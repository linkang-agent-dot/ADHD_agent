import requests, json, os, sys, urllib.request, re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

UPLOAD_DIR = r'C:\Users\linkang\.openclaw\workspace\uploads'
RESULTS_FILE = os.path.join(UPLOAD_DIR, 'push_results.json')

app_id = 'cli_a934245330789ccf'
app_secret = os.environ.get('FEISHU_APP_SECRET', '')
open_id = 'ou_e48f6c4c0395f45b74b51525f348678b'

# Get token
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': app_id, 'app_secret': app_secret}, timeout=10)
token = r.json().get('tenant_access_token', '')
print('Token OK:', bool(token))
headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

# Load results
results = json.load(open(RESULTS_FILE, 'r', encoding='utf-8'))
print(f'Loaded {len(results)} items')

today = '2026-05-06'

for item in results:
    idx = item['index']
    title = item.get('title') or '(无标题)'
    author = item['user']
    likes = item['liked']
    collected = item.get('collected', '?')
    shared = item.get('shared', '?')
    img_path = item.get('img_path', '')
    feed_id = item['feed_id']

    text = f'''📌 {title}
👤 @{author}
👍 {likes} | ⭐ {collected} | 🔗 {shared}
🔗 https://www.xiaohongshu.com/explore/{feed_id}
#旅游 #旅行攻略'''

    print(f'\n--- Sending #{idx}: {title[:30]} ---')

    # Upload image
    image_key = None
    if img_path and os.path.exists(img_path):
        try:
            with open(img_path, 'rb') as f:
                img_data = f.read()
            files = {'image': (f'push_{idx}.jpg', img_data, 'image/jpeg')}
            rimg = requests.post('https://open.feishu.cn/open-apis/im/v1/images',
                headers={'Authorization': 'Bearer ' + token},
                data={'image_type': 'message'},
                files=files, timeout=15)
            img_resp = rimg.json()
            print('Image upload: code=' + str(img_resp.get('code')))
            if img_resp.get('code') == 0:
                image_key = img_resp.get('data', {}).get('image_key', '')
        except Exception as e:
            print('Image upload error:', e)

    # Send message with image
    if image_key:
        payload = {
            'receive_id': open_id,
            'msg_type': 'post',
            'content': json.dumps({
                'zh_cn': {
                    'title': f'[{idx}/5] {title}',
                    'content': [[
                        {'tag': 'text', 'text': f'👤 @{author}  |  👍{likes} ⭐{collected} 🔗{shared}\n\n#旅游 #旅行攻略\n🔗 https://www.xiaohongshu.com/explore/{feed_id}'},
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
    print('Send result: code=' + str(resp.get('code')) + ', msg=' + str(resp.get('msg', '')))
    if resp.get('code') != 0:
        print('Full resp:', json.dumps(resp, ensure_ascii=False))

print('\nAll done!')
