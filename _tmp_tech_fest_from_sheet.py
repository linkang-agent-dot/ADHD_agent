# -*- coding: utf-8 -*-
"""从 GSheet 礼包表筛 2026 科技节相关行并汇总（接续上文复盘）。"""
import json
import subprocess
import re

SPREADSHEET = "1S4noJfqUTQbqjlNEubi-kc7rAagGL4cHw2F_lVyD4wg"
GWS = r"C:\Users\linkang\AppData\Roaming\npm\gws.cmd"


def main() -> None:
    r = subprocess.run(
        [
            GWS,
            "sheets",
            "+read",
            "--spreadsheet",
            SPREADSHEET,
            "--range",
            "Sheet1!A2:D257",
            "--format",
            "json",
        ],
        capture_output=True,
    )
    text = r.stdout.decode("utf-8", errors="replace")
    data = json.loads(text)
    rows = data.get("values") or []

    def is_tech_fest(iap_id: str, name: str) -> bool:
        # 名称优先，排除误伤
        if "挖矿小游戏" in name or "情人节" in name:
            return False
        if "2026科技节" in name or "科技节" in name:
            return True
        # 科技节通行证 BP
        if iap_id in ("201390128_battle_pass", "201390129_battle_pass"):
            return True
        # 弹珠 GACHA：108xx + 1090~1092（1093+_scene 为挖矿，需排除）
        if re.match(r"^201351108\d+_(normal|random)$", iap_id):
            return True
        if re.match(r"^201351109[012]_(normal|random)$", iap_id):
            return True
        if iap_id in (
            "2013502000_normal",
            "2013101243_normal",
            "2013510998_normal",
        ):
            return True
        if "fes_weekly_card" in iap_id and iap_id.startswith("201351047"):
            return True
        return False

    picked = []
    for row in rows:
        if len(row) < 4:
            continue
        iap_id, name, cnt_s, pay_s = row[0], row[1], row[2], row[3]
        if not is_tech_fest(iap_id, name):
            continue
        try:
            cnt = int(float(cnt_s))
            pay = float(pay_s)
        except (TypeError, ValueError):
            continue
        picked.append((iap_id, name, cnt, pay))

    picked.sort(key=lambda x: -x[3])
    total_pay = sum(x[3] for x in picked)
    sum_users_lines = sum(x[2] for x in picked)

    print("=== 2026科技节相关礼包行（来自 GSheet，按金额降序）===")
    for t in picked:
        print(f"{t[3]:>12.2f}  {t[2]:>6}人  {t[0]}  {t[1]}")
    print()
    print(f"行数: {len(picked)}")
    print(f"礼包付费合计(各 iap 相加): ${total_pay:,.2f}")
    print(f"「付费人数」逐行求和(会重复计同一用户): {sum_users_lines:,}")
    print()
    print("说明: 去重付费人数需 SQL/数仓；此处合计金额可与 Datain「p2-节日」~$769,480 对照。")


if __name__ == "__main__":
    main()
