# -*- coding: utf-8 -*-
"""
6个节日：整体 KPI + R级付费数据 全量查询
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

FESTIVALS = [
    {"name": "万圣节",  "start": "2025-10-17", "start_m1": "2025-10-16", "end": "2025-11-06", "rlevel_date": "2025-10-16"},
    {"name": "感恩节",  "start": "2025-11-13", "start_m1": "2025-11-12", "end": "2025-12-04", "rlevel_date": "2025-11-12"},
    {"name": "圣诞节",  "start": "2025-12-12", "start_m1": "2025-12-11", "end": "2026-01-01", "rlevel_date": "2025-12-11"},
    {"name": "春节",    "start": "2026-01-13", "start_m1": "2026-01-12", "end": "2026-02-08", "rlevel_date": "2026-01-12"},
    {"name": "情人节",  "start": "2026-02-11", "start_m1": "2026-02-10", "end": "2026-03-05", "rlevel_date": "2026-02-10"},
    {"name": "科技节",  "start": "2026-03-13", "start_m1": "2026-03-12", "end": "2026-04-03", "rlevel_date": "2026-03-12"},
]

# ───────────────────────────────────────────────
# Query 1: 各节日整体 KPI（全部 iap_type）
# ───────────────────────────────────────────────
def query_overall_kpi(f):
    SQL = f"""
    SELECT
        COUNT(DISTINCT b1.user_id)                            AS pay_users,
        COUNT(*)                                               AS buy_times,
        CAST(SUM(b1.pay_price) AS DECIMAL(18,2))              AS revenue,
        CAST(AVG(b1.pay_price) AS DECIMAL(18,4))              AS avg_price
    FROM (
        SELECT user_id, pay_price
        FROM v1041.ods_user_order
        WHERE partition_date BETWEEN '{f["start_m1"]}' AND '{f["end"]}'
          AND date(date_add('hour',-8,created_at)) BETWEEN date '{f["start"]}' AND date '{f["end"]}'
          AND pay_status = 1
          AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
    ) b1
    """
    return api.execute_sql(SQL)[0]

# Query 2: 各节日活跃用户数（取节日期间任意一天登录过的去重人数）
def query_dau(f):
    SQL = f"""
    SELECT COUNT(DISTINCT user_id) AS active_users
    FROM v1041.dl_active_user_d
    WHERE partition_date BETWEEN '{f["start"]}' AND '{f["end"]}'
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
    """
    return api.execute_sql(SQL)[0]

# ───────────────────────────────────────────────
# Query 3: 各节日 × R级 付费数据
# ───────────────────────────────────────────────
def query_rlevel(f):
    SQL = f"""
    SELECT
        r.rlevel,
        COUNT(DISTINCT dau.user_id)  AS active_users,
        COUNT(DISTINCT o.user_id)    AS pay_users,
        CAST(SUM(COALESCE(o.pay_price, 0)) AS DECIMAL(18,2)) AS revenue
    FROM (
        SELECT DISTINCT user_id
        FROM v1041.dl_active_user_d
        WHERE partition_date BETWEEN '{f["start"]}' AND '{f["end"]}'
          AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
    ) dau
    JOIN (
        SELECT user_id, rlevel
        FROM v1041.da_user_rlevel_pay_ratio
        WHERE create_date = '{f["rlevel_date"]}'
    ) r ON dau.user_id = r.user_id
    LEFT JOIN (
        SELECT user_id, pay_price
        FROM v1041.ods_user_order
        WHERE partition_date BETWEEN '{f["start_m1"]}' AND '{f["end"]}'
          AND date(date_add('hour',-8,created_at)) BETWEEN date '{f["start"]}' AND date '{f["end"]}'
          AND pay_status = 1
          AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
    ) o ON dau.user_id = o.user_id
    GROUP BY r.rlevel
    ORDER BY CASE r.rlevel WHEN 'chaoR' THEN 1 WHEN 'daR' THEN 2 WHEN 'zhongR' THEN 3 WHEN 'xiaoR' THEN 4 END
    """
    return api.execute_sql(SQL)

# ───────────────────────────────────────────────
# 主程序
# ───────────────────────────────────────────────
results = {}
for f in FESTIVALS:
    print(f"\n{'='*50}", flush=True)
    print(f"[{f['name']}] {f['start']} ~ {f['end']}", flush=True)

    # 1. 整体 KPI
    print("  查整体 KPI ...", flush=True)
    kpi = query_overall_kpi(f)
    print("  查活跃用户 ...", flush=True)
    dau = query_dau(f)

    rev   = float(kpi.get('revenue', 0) or 0)
    pays  = int(kpi.get('pay_users', 0) or 0)
    actv  = int(dau.get('active_users', 0) or 0)
    arppu = round(rev / pays, 2) if pays > 0 else 0
    arpu  = round(rev / actv, 4) if actv > 0 else 0
    prate = round(pays / actv * 100, 2) if actv > 0 else 0

    print(f"  总收入: ${rev:,.0f}  付费: {pays:,}  活跃: {actv:,}  付费率: {prate}%  ARPPU: ${arppu}  ARPU: ${arpu}")

    # 2. R级数据
    print("  查 R级数据 ...", flush=True)
    rrows = query_rlevel(f)
    rlevel_data = {}
    for rr in rrows:
        rl = rr.get('rlevel', '')
        ra = int(rr.get('active_users', 0) or 0)
        rp = int(rr.get('pay_users', 0) or 0)
        rrev = float(rr.get('revenue', 0) or 0)
        rlevel_data[rl] = {
            "active": ra, "payers": rp, "revenue": round(rrev, 2),
            "pay_rate": round(rp/ra*100, 1) if ra > 0 else 0,
            "arppu": round(rrev/rp, 2) if rp > 0 else 0,
            "arpu": round(rrev/ra, 2) if ra > 0 else 0,
        }
        print(f"    {rl:8s}  活跃:{ra:5,}  付费:{rp:5,}  付费率:{rp/ra*100 if ra else 0:.1f}%  收入:${rrev:>10,.0f}  ARPU:${rrev/ra if ra else 0:.2f}")

    results[f['name']] = {
        "start": f['start'], "end": f['end'],
        "kpi": {"revenue": rev, "pay_users": pays, "active_users": actv,
                "pay_rate": prate, "arppu": arppu, "arpu": arpu},
        "rlevel": rlevel_data,
    }

# 保存
out = r'C:\ADHD_agent\_tmp_hist_kpi_full.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n\n✅ 所有数据已保存至 {out}")
