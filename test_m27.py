import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')

API_KEY = 'sk-cp-UZlYE7WEtHwVEgCKEZOpgSNezyVxA3mTGdUy8k0nkNJindUuOv_bUj2GlxO1VI6eTizdHvoR8tEHzaDBhTf4WEBuF2OZTuQ-kYHxi-amwfRtV8VG2CRKlaE'

r = requests.post('https://api.minimax.chat/v1/chat/completions',
    headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
    json={'model': 'MiniMax-M2.7', 'messages': [{'role': 'user', 'content': '你好，用一句话介绍自己'}], 'max_tokens': 100},
    timeout=30)

print(f'Status: {r.status_code}')
data = r.json()
base = data.get('base_resp', {})
if base.get('status_code', 0) != 0:
    print(f'Error: {base}')
else:
    msg = data['choices'][0]['message']['content']
    print(f'Response: {msg[:300]}')
    usage = data.get('usage', {})
    print(f'Tokens: prompt={usage.get("prompt_tokens")}, completion={usage.get("completion_tokens")}')
