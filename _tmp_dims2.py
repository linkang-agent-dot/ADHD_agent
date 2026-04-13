import subprocess, json, ast

result = subprocess.run(
    ['python', 'skills/datain-skill/scripts/query_game.py', '-c', 'get_param_names', 
     '-g', '1041', '--funcs', 'dimensions', '--algorithmId', 'user_id'],
    capture_output=True, encoding='utf-8', errors='replace'
)
data = ast.literal_eval(result.stdout)
dims = data.get('dimensions', [])
# Print all dims to find iap/payment type related ones
for d in dims:
    if any(k in d for k in ['礼包', 'iap', 'IAP', '节日', '活动', '类型', '商品', '购买']):
        print(d)
