import sys, re
sys.stdout.reconfigure(encoding='utf-8')

idx = r'C:\Users\linkang\AppData\Local\cursor-agent\versions\2026.03.30-a5d3e17\index.js'
content = open(idx, 'r', encoding='utf-8', errors='replace').read()

# 找 cursor API 相关 URL
cursor_hosts = re.findall(r'["\']https?://[^"\']*cursor[^"\']{0,80}["\']', content)
unique_hosts = list(dict.fromkeys(cursor_hosts))[:15]
print('=== Cursor API URLs ===')
for h in unique_hosts:
    print(f'  {h[:120]}')
print()

# 找 /chat/completions 或 /v1/ 路由
api_routes = re.findall(r'["\'][/][^\s"\']{0,60}(?:completions|models|chat|message)[^\s"\']{0,40}["\']', content)
unique_routes = list(dict.fromkeys(api_routes))[:15]
print('=== API Routes ===')
for r in unique_routes:
    print(f'  {r[:120]}')
print()

# 当前模型选择逻辑
model_select = re.findall(r'\.model\s*=\s*["\'][^"\']{3,50}["\']', content)
unique_models = list(dict.fromkeys(model_select))[:10]
print('=== Model assignments ===')
for m in unique_models:
    print(f'  {m[:100]}')
