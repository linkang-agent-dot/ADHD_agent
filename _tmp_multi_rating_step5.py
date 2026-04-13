"""
多活动评级 Step5: 用用户给定分母 12474 重新计算评级
"""
import json

TOTAL_PAYERS = 12474

with open(r'C:\ADHD_agent\_tmp_multi_final.json', encoding='utf-8') as f:
    raw = json.load(f)

def score_arppu(v):
    if v >= 100: return 100
    if v >= 70:  return 90
    if v >= 50:  return 80
    if v >= 35:  return 70
    if v >= 25:  return 60
    if v >= 15:  return 45
    return 30

def score_pay_rate(v):
    if v >= 15: return 100
    if v >= 12: return 90
    if v >= 10: return 80
    if v >= 8:  return 70
    if v >= 6:  return 55
    if v >= 4:  return 40
    return 25

def score_arpu(v):
    if v >= 20: return 100
    if v >= 15: return 90
    if v >= 10: return 80
    if v >= 7:  return 70
    if v >= 5:  return 60
    if v >= 3:  return 45
    return 30

def score_chaor(v):
    if 60 <= v <= 70: return 100
    if (55 <= v < 60) or (70 < v <= 75): return 85
    if (50 <= v < 55) or (75 < v <= 80): return 70
    if (45 <= v < 50) or (80 < v <= 85): return 55
    return 40

def grade(score):
    if score >= 85: return 'S', 'T1'
    if score >= 80: return 'A', 'T1'
    if score >= 75: return 'A', 'T2'
    if score >= 65: return 'B', 'T2'
    if score >= 50: return 'C', 'T3'
    return 'D', 'T3'

results = []
for act, m in raw.items():
    pay_num   = m['pay_num']
    pay_total = m['pay_total']
    arppu     = m['arppu']
    chaor_pct = m['chaor_pct']

    pay_rate = round(pay_num / TOTAL_PAYERS * 100, 2)
    arpu     = round(pay_total / TOTAL_PAYERS, 2)

    s_arppu    = score_arppu(arppu)
    s_pay_rate = score_pay_rate(pay_rate)
    s_arpu     = score_arpu(arpu)
    s_chaor    = score_chaor(chaor_pct)
    total_score = round(s_arppu*0.4 + s_pay_rate*0.3 + s_arpu*0.2 + s_chaor*0.1, 1)
    lv, tier   = grade(total_score)

    results.append({
        'activity': act, 'pay_total': pay_total, 'pay_num': pay_num,
        'arppu': arppu, 'pay_rate': pay_rate, 'arpu': arpu,
        'chaor_pct': chaor_pct, 'total_score': total_score, 'grade': lv, 'tier': tier,
        'scores': {'arppu': s_arppu, 'pay_rate': s_pay_rate, 'arpu': s_arpu, 'chaor': s_chaor}
    })

results.sort(key=lambda x: -x['total_score'])

print(f"分母: {TOTAL_PAYERS:,}\n")
print(f"{'活动':22s} {'收入':>12} {'付费人':>7} {'ARPPU':>7} {'付费率':>7} {'ARPU':>6} {'超R%':>6} | {'得分':>6} {'等级':>3} {'梯队':>3}")
print("-" * 107)
for r in results:
    print(f"{r['activity']:22s} {r['pay_total']:>12,.0f} {r['pay_num']:>7,} "
          f"{r['arppu']:>7.1f} {r['pay_rate']:>6.2f}% {r['arpu']:>6.2f} {r['chaor_pct']:>5.1f}% "
          f"| {r['total_score']:>6.1f}  {r['grade']:>3}  {r['tier']:>3}")

with open(r'C:\ADHD_agent\_tmp_multi_rating_v2.json', 'w', encoding='utf-8') as f:
    json.dump({'denom': TOTAL_PAYERS, 'results': results}, f, ensure_ascii=False, indent=2)
print(f"\n分母: 全量登录活跃付费玩家 {TOTAL_PAYERS:,}")
