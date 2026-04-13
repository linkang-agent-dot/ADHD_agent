import subprocess, json, ast

indicators = json.dumps([
    {'id': '60d412c3e862647e69cfe707', 'name': 'pay'},
    {'id': '60d42914b75b54435c6225fd', 'name': 'arppu'},
])
dimensions = json.dumps([{'id': 'report_date', 'name': 'day'}])

result = subprocess.run(
    ['python', 'skills/datain-skill/scripts/query_game.py', '-c', 'query',
     '-g', '1041', '--startAt', '2026-01-22', '--endAt', '2026-02-11',
     '--algorithmId', 'user_id', '--indicators', indicators,
     '--dimensions', dimensions],
    capture_output=True, encoding='utf-8', errors='replace'
)
data = ast.literal_eval(result.stdout)
for row in data['result']:
    print(row['report_date'], row['bi_dau_pay_price'], row['bi_dau'], row['bi_pau'], row['ci_arppu'])
