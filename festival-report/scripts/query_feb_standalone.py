# -*- coding: utf-8 -*-
"""
查02-02~02-08独立周期内所有节日礼包的精确收入
并从春节窗口(01-13~02-08)中扣除，重建7期数据
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

# ── 1. 查独立周期 02-02~02-08 全部节日礼包明细 ──
SQL_FEB = """
SELECT
    b2.iap_id_name,
    b2.iap_type2,
    COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
    COUNT(*) AS buy_times,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
FROM (
    SELECT user_id, iap_id, pay_price
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2026-02-01' AND '2026-02-08'
      AND date(date_add('hour',-8,created_at)) BETWEEN date '2026-02-02' AND date '2026-02-08'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name, iap_type2
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY b2.iap_id_name, b2.iap_type2
ORDER BY revenue DESC
"""

print("=== 查询02-02~02-08独立周期 ===", flush=True)
feb_rows = api.execute_sql(SQL_FEB)

feb_total = 0
feb_packs = []
for r in feb_rows:
    name = r['iap_id_name']
    t2 = r.get('iap_type2', '')
    rev = float(r.get('revenue', 0) or 0)
    buyers = int(r.get('pay_user_cnt', 0) or 0)
    times = int(r.get('buy_times', 0) or 0)
    feb_total += rev
    feb_packs.append({
        "name": name, "iap_type2": t2,
        "revenue": round(rev, 2), "buyers": buyers, "times": times
    })
    print(f"  ${rev:>10,.0f}  [{t2}]  {name}")

print(f"\n  独立周期总计: ${feb_total:,.0f}  ({len(feb_packs)}种礼包)")

# ── 2. 查原春节窗口01-13~02-01（扣除独立周期后的纯春节） ──
SQL_CNY_PURE = """
SELECT
    b2.iap_id_name,
    b2.iap_type2,
    COUNT(DISTINCT b1.user_id) AS pay_user_cnt,
    COUNT(*) AS buy_times,
    CAST(SUM(b1.pay_price) AS DECIMAL(18,2)) AS revenue
FROM (
    SELECT user_id, iap_id, pay_price
    FROM v1041.ods_user_order
    WHERE partition_date BETWEEN '2026-01-12' AND '2026-02-01'
      AND date(date_add('hour',-8,created_at)) BETWEEN date '2026-01-13' AND date '2026-02-01'
      AND pay_status = 1
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
) b1
INNER JOIN (
    SELECT iap_id, iap_id_name, iap_type2
    FROM v1041.dim_iap
    WHERE iap_type = '混合-节日活动'
) b2 ON b1.iap_id = b2.iap_id
GROUP BY b2.iap_id_name, b2.iap_type2
ORDER BY revenue DESC
"""

print("\n=== 查询纯春节 01-13~02-01 ===", flush=True)
cny_rows = api.execute_sql(SQL_CNY_PURE)

cny_total = 0
cny_packs = []
for r in cny_rows:
    name = r['iap_id_name']
    t2 = r.get('iap_type2', '')
    rev = float(r.get('revenue', 0) or 0)
    buyers = int(r.get('pay_user_cnt', 0) or 0)
    times = int(r.get('buy_times', 0) or 0)
    cny_total += rev
    cny_packs.append({
        "name": name, "iap_type2": t2,
        "revenue": round(rev, 2), "buyers": buyers, "times": times
    })

print(f"  纯春节总计: ${cny_total:,.0f}  ({len(cny_packs)}种礼包)")
print(f"  原春节(含独立期): ${cny_total + feb_total:,.0f}")
print(f"  独立周期: ${feb_total:,.0f}")

# ── 3. 保存结果 ──
result = {
    "feb_standalone": {
        "label": "2月独立周期",
        "start": "2026-02-02",
        "end": "2026-02-08",
        "total": round(feb_total, 2),
        "packs": feb_packs,
    },
    "cny_pure": {
        "label": "春节(纯)",
        "start": "2026-01-13",
        "end": "2026-02-01",
        "total": round(cny_total, 2),
        "packs": cny_packs,
    },
}

with open(r'C:\ADHD_agent\_tmp_feb_standalone.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\nDone: saved to _tmp_feb_standalone.json")
