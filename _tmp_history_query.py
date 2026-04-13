# -*- coding: utf-8 -*-
"""补拉历史节日数据凑 metrics_trend 6期"""
import subprocess, json, ast

GWS = r"C:\Users\linkang\AppData\Roaming\npm\gws.cmd"

def datain_query(start, end, dimensions=None, extra_indicators=None):
    indicators = json.dumps([
        {"id": "60d412c3e862647e69cfe707", "name": "revenue"},
        {"id": "60d4281cb75b54435c6225fc", "name": "arpu"},
        {"id": "60d42914b75b54435c6225fd", "name": "arppu"},
    ])
    cmd = [
        "python", "skills/datain-skill/scripts/query_game.py",
        "-c", "query", "-g", "1041",
        "--startAt", start, "--endAt", end,
        "--algorithmId", "user_id",
        "--indicators", indicators,
    ]
    if dimensions:
        cmd += ["--dimensions", json.dumps(dimensions)]
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", cwd=r"c:\ADHD_agent")
    data = ast.literal_eval(r.stdout)
    row = data["result"][0]
    return {
        "revenue": round(row["bi_dau_pay_price"], 2),
        "arpu":    round(row["ci_arpu"], 4),
        "arppu":   round(row["ci_arppu"], 4),
        "dau":     row["bi_dau"],
        "pau":     row["bi_pau"],
    }

# 各期时间窗（根据实际节日档期估算）
events = [
    ("2025万圣节",  "2025-10-24", "2025-11-13"),
    ("2025感恩节",  "2025-11-14", "2025-12-04"),
    ("2025圣诞节",  "2025-12-12", "2026-01-01"),
    ("2026情人节",  "2026-01-22", "2026-02-11"),
    ("2026科技节",  "2026-03-13", "2026-04-02"),
]

results = {}
for name, s, e in events:
    try:
        d = datain_query(s, e)
        d["event"] = name
        d["start"] = s
        d["end"] = e
        # pay_rate 粗估（PAU/DAU * 100，全局口径供 fallback）
        d["pay_rate"] = round(d["pau"] / d["dau"] * 100, 2) if d["dau"] else 0
        results[name] = d
        print(f"{name}: revenue=${d['revenue']:,.0f} arpu={d['arpu']:.2f} arppu={d['arppu']:.2f} pay_rate={d['pay_rate']:.2f}%")
    except Exception as ex:
        print(f"{name}: ERROR {ex}")

# 同时补拉节日线各期（map_indicator）
fes_events = [
    ("2025万圣节",  "2025-10-24", "2025-11-13"),
    ("2025感恩节",  "2025-11-14", "2025-12-04"),
    ("2025圣诞节",  "2025-12-12", "2026-01-01"),
    ("2026情人节",  "2026-01-22", "2026-02-11"),
    ("2026科技节",  "2026-03-13", "2026-04-02"),
]
fes_indicators = json.dumps([
    {"id": "698978c359dd0b4c980d417f", "name": "fes_total"},
    {"id": "63fdd46ed72b6b7ed0163cd8", "name": "fes_special"},
    {"id": "6406ae6762e1ac341b950d79", "name": "fes_bp"},
    {"id": "6406ae6862e1ac341b950d7c", "name": "fes_skin"},
    {"id": "653b17384f406057e9f85c56", "name": "fes_mining"},
])

print("\n--- 节日线细分 ---")
fes_results = {}
for name, s, e in fes_events:
    try:
        cmd = [
            "python", "skills/datain-skill/scripts/query_game.py",
            "-c", "query", "-g", "1041",
            "--startAt", s, "--endAt", e,
            "--algorithmId", "user_id",
            "--indicators", fes_indicators,
        ]
        r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", cwd=r"c:\ADHD_agent")
        data = ast.literal_eval(r.stdout)
        row = data["result"][0]
        fes_total   = row.get("bi_iap_growth_type_pay_p2_festival", 0)
        fes_special = row.get("bi_iap_growth_smallest_type_pay_p2_mix_festival_festival_special", 0)
        fes_bp      = row.get("bi_iap_growth_smallest_type_pay_p2_mix_festival_festival_bp", 0)
        fes_skin    = row.get("bi_iap_growth_smallest_type_pay_p2_mix_festival_festival_skin", 0)
        fes_mining  = row.get("bi_iap_growth_smallest_type_pay_p2_mix_festival_mining_game", 0)
        fes_results[name] = {
            "fes_total": round(fes_total, 2),
            "fes_special": round(fes_special, 2),
            "fes_bp": round(fes_bp, 2),
            "fes_skin": round(fes_skin, 2),
            "fes_mining": round(fes_mining, 2),
        }
        print(f"{name}: 节日总={fes_total:,.0f} 特惠={fes_special:,.0f} BP={fes_bp:,.0f} 皮肤={fes_skin:,.0f} 挖矿={fes_mining:,.0f}")
    except Exception as ex:
        print(f"{name}: ERROR {ex}")

# 同时拉R级分层
print("\n--- R级付费分布 ---")
r_indicators = json.dumps([
    {"id": "60d412c3e862647e69cfe707", "name": "revenue"},
    {"id": "60d42914b75b54435c6225fd", "name": "arppu"},
])
r_dim = json.dumps([{"id": "6188c07b0bf85369c540393e", "name": "R分级"}])
r_results = {}
for name, s, e in [("2026情人节","2026-01-22","2026-02-11"), ("2026科技节","2026-03-13","2026-04-02")]:
    cmd = [
        "python", "skills/datain-skill/scripts/query_game.py",
        "-c", "query", "-g", "1041",
        "--startAt", s, "--endAt", e,
        "--algorithmId", "user_id",
        "--indicators", r_indicators,
        "--dimensions", r_dim,
    ]
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", cwd=r"c:\ADHD_agent")
    data = ast.literal_eval(r.stdout)
    tiers = {}
    total_rev = 0
    for row in data["result"]:
        rl = row["td_rlevel"]
        rev = row["bi_dau_pay_price"]
        pau = row["bi_pau"]
        arppu = row["ci_arppu"]
        tiers[rl] = {"revenue": round(rev,2), "pau": pau, "arppu": round(arppu,4)}
        if rl != "feiR":
            total_rev += rev
    r_results[name] = tiers
    print(f"\n{name}:")
    for rl, v in sorted(tiers.items(), key=lambda x: -x[1]["revenue"]):
        pct = v["revenue"]/total_rev*100 if total_rev else 0
        print(f"  {rl}: ${v['revenue']:,.0f} ({pct:.1f}%)  PAU={v['pau']}  ARPPU=${v['arppu']:.2f}")

# 写入合并结果
output = {"metrics": results, "fes": fes_results, "r_tiers": r_results}
with open(r"c:\ADHD_agent\_tmp_history_result.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("\n\n已写入 _tmp_history_result.json")
