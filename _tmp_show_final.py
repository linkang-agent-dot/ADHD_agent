import json
with open(r'C:\ADHD_agent\_tmp_multi_rating_final.json', encoding='utf-8') as f:
    d = json.load(f)
print(f'分母: {d["denom"]:,}')
print()
print(f'{"活动":<24} {"收入":>12} {"付费人":>7} {"ARPPU":>7} {"付费率":>7} {"ARPU":>6} {"超R%":>6} | {"得分":>6} {"等级":>3} {"梯队":>3}')
print('-'*110)
for r in d['results']:
    print(f"{r['activity']:<24} {r['pay_total']:>12,.0f} {r['pay_num']:>7,} {r['arppu']:>7.1f} {r['pay_rate']:>6.2f}% {r['arpu']:>6.2f} {r['chaor_pct']:>5.1f}% | {r['total_score']:>6.1f}  {r['grade']:>3}  {r['tier']:>3}")
