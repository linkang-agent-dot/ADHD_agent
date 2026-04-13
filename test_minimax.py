import requests, json, time

agents_md = open(r'C:\ADHD_agent\openclaw\workspace\AGENTS.md', encoding='utf-8').read()
memory_md = open(r'C:\ADHD_agent\openclaw\workspace\MEMORY.md', encoding='utf-8').read()
full_system = f'You are a helpful AI assistant.\n\n---AGENTS.MD---\n{agents_md}\n\n---MEMORY.MD---\n{memory_md}'

tools = []
for name in ['read', 'write', 'edit', 'exec', 'web_search', 'web_fetch', 'message', 'cron',
             'browser_navigate', 'browser_click', 'browser_screenshot', 'browser_type',
             'browser_wait', 'feishu_doc', 'feishu_chat', 'feishu_wiki', 'feishu_drive',
             'feishu_bitable', 'feishu_app_scopes', 'memory_search', 'memory_write']:
    tools.append({
        'type': 'function',
        'function': {
            'name': name,
            'description': f'Tool: {name} - does something useful with extended description.',
            'parameters': {'type': 'object', 'properties': {'arg1': {'type': 'string', 'description': 'First argument'}, 'arg2': {'type': 'string', 'description': 'Second argument'}}, 'required': ['arg1']}
        }
    })

API_KEY = 'sk-cp-UZlYE7WEtHwVEgCKEZOpgSNezyVxA3mTGdUy8k0nkNJindUuOv_bUj2GlxO1VI6eTizdHvoR8tEHzaDBhTf4WEBuF2OZTuQ-kYHxi-amwfRtV8VG2CRKlaE'
headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

payload = {
    'model': 'MiniMax-M2.5',
    'messages': [
        {'role': 'system', 'content': full_system},
        {'role': 'user', 'content': 'hi'}
    ],
    'max_tokens': 4096,
    'tools': tools,
    'stream': True
}

for i in range(5):
    r = requests.post('https://api.minimax.chat/v1/chat/completions',
        headers=headers, json=payload, timeout=30)
    has_794 = '794' in r.text[:500]
    status = 'FAIL(794)' if has_794 else 'OK'
    print(f'Run {i+1}: {status} (HTTP {r.status_code})')
    time.sleep(1)
