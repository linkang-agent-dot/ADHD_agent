import json
d = json.load(open(r'C:\ADHD_agent\_tmp_multi_rating_v3.json', encoding='utf-8'))
print(f'分母: {d["denom"]:,}  活动数: {len(d["results"])}')
for r in d['results']:
    print(r['activity'], r['pay_total'], r['pay_num'], r['arppu'], r['pay_rate'], r['arpu'], r['chaor_pct'], r['total_score'], r['grade'], r['tier'])
