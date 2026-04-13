# -*- coding: utf-8 -*-
"""R级ARPU分层查询"""
import subprocess, json, ast

r_indicators = json.dumps([
    {"id": "60d412c3e862647e69cfe707", "name": "revenue"},
    {"id": "60d42914b75b54435c6225fd", "name": "arppu"},
    {"id": "60d42828b75b54435c622600", "name": "pau"},
])
r_dim = json.dumps([{"id": "6188c07b0bf85369c540393e", "name": "R分级"}])

for name, s, e in [
    ("2025万圣节", "2025-10-24", "2025-11-13"),
    ("2025圣诞节", "2025-12-12", "2026-01-01"),
    ("2026情人节", "2026-01-22", "2026-02-11"),
    ("2026科技节", "2026-03-13", "2026-04-02"),
]:
    cmd = [
        "python", "skills/datain-skill/scripts/query_game.py",
        "-c", "query", "-g", "1041",
        "--startAt", s, "--endAt", e,
        "--algorithmId", "user_id",
        "--indicators", r_indicators,
        "--dimensions", r_dim,
    ]
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", cwd=r"c:\ADHD_agent")
    try:
        data = ast.literal_eval(r.stdout)
        tiers = {}
        for row in data["result"]:
            rl = row.get("td_rlevel", "?")
            rev = row.get("bi_dau_pay_price", 0)
            pau = row.get("bi_pau", 0)
            # 用 revenue / pau 算 ARPU（节日期间该R级ARPU）
            raw_arppu = row.get("ci_arppu", "0")
            try:
                arppu_v = float(raw_arppu)
            except:
                arppu_v = 0.0
            tiers[rl] = {"rev": round(float(rev),0), "pau": int(pau), "arppu": round(arppu_v,2)}
        total_r_rev = sum(v["rev"] for k,v in tiers.items() if k != "feiR")
        print(f"\n【{name}】")
        for rl in ["超R", "大R", "中R", "小R", "feiR"]:
            v = tiers.get(rl, {"rev":0,"pau":0,"arppu":0})
            pct = v["rev"]/total_r_rev*100 if total_r_rev else 0
            # ARPU = rev / PAU (各层在付费总人数中的人均)
            arpu_tier = v["rev"]/v["pau"] if v["pau"] else 0
            print(f"  {rl}: ${v['rev']:,.0f} ({pct:.1f}%)  PAU={v['pau']}  ARPPU=${v['arppu']:.2f}  层ARPU=${arpu_tier:.2f}")
    except Exception as ex:
        print(f"{name} Error: {ex}")
        print("stdout:", r.stdout[:500])
