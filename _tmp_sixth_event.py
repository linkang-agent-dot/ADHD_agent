# -*- coding: utf-8 -*-
import subprocess, json, ast

indicators = json.dumps([
    {"id": "60d412c3e862647e69cfe707", "name": "revenue"},
    {"id": "60d4281cb75b54435c6225fc", "name": "arpu"},
    {"id": "60d42914b75b54435c6225fd", "name": "arppu"},
])
fes_indicators = json.dumps([
    {"id": "698978c359dd0b4c980d417f", "name": "fes_total"},
    {"id": "63fdd46ed72b6b7ed0163cd8", "name": "fes_special"},
    {"id": "6406ae6762e1ac341b950d79", "name": "fes_bp"},
    {"id": "6406ae6862e1ac341b950d7c", "name": "fes_skin"},
    {"id": "653b17384f406057e9f85c56", "name": "fes_mining"},
])

for name, s, e in [
    ("2025周年庆", "2025-08-01", "2025-08-21"),
    ("2025暑期节", "2025-07-18", "2025-08-07"),
    ("2025八月节", "2025-08-22", "2025-09-11"),
]:
    cmd = ["python", "skills/datain-skill/scripts/query_game.py",
           "-c", "query", "-g", "1041",
           "--startAt", s, "--endAt", e,
           "--algorithmId", "user_id", "--indicators", indicators]
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", cwd=r"c:\ADHD_agent")
    try:
        d = ast.literal_eval(r.stdout)["result"][0]
        rev = d["bi_dau_pay_price"]
        pay_rate = d["bi_pau"] / d["bi_dau"] * 100 if d["bi_dau"] else 0
        print(f"{name} ({s}~{e}): revenue=${rev:,.0f}  arpu={d['ci_arpu']:.2f}  arppu={d['ci_arppu']:.2f}  pay_rate={pay_rate:.2f}%")
        # 节日线
        cmd2 = ["python", "skills/datain-skill/scripts/query_game.py",
                "-c", "query", "-g", "1041",
                "--startAt", s, "--endAt", e,
                "--algorithmId", "user_id", "--indicators", fes_indicators]
        r2 = subprocess.run(cmd2, capture_output=True, encoding="utf-8", errors="replace", cwd=r"c:\ADHD_agent")
        d2 = ast.literal_eval(r2.stdout)["result"][0]
        fes_total = d2.get("bi_iap_growth_type_pay_p2_festival", 0)
        fes_special = d2.get("bi_iap_growth_smallest_type_pay_p2_mix_festival_festival_special", 0)
        fes_bp = d2.get("bi_iap_growth_smallest_type_pay_p2_mix_festival_festival_bp", 0)
        fes_skin = d2.get("bi_iap_growth_smallest_type_pay_p2_mix_festival_festival_skin", 0)
        fes_mining = d2.get("bi_iap_growth_smallest_type_pay_p2_mix_festival_mining_game", 0)
        print(f"  节日线: 总={fes_total:,.0f} 特惠={fes_special:,.0f} BP={fes_bp:,.0f} 皮肤={fes_skin:,.0f} 挖矿={fes_mining:,.0f}")
    except Exception as ex:
        print(f"{name}: Error {ex}")
        print("stdout:", r.stdout[:300])
