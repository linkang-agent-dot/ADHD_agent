import subprocess, json, ast

# Check if there is an event/activity dimension in Datain
result = subprocess.run(
    ['python', 'skills/datain-skill/scripts/query_game.py', '-c', 'get_param_names', 
     '-g', '1041', '--funcs', 'dimensions', '--algorithmId', 'user_id'],
    capture_output=True, encoding='utf-8', errors='replace'
)
data = ast.literal_eval(result.stdout)
dims = data.get('dimensions', [])
# Look for activity/event/control related dimensions
keywords = ['活动', '事件', '控制', 'control', '节日', '点击', 'click', '入口', '礼包']
for d in dims:
    if any(k.lower() in d.lower() for k in keywords):
        print(d)
