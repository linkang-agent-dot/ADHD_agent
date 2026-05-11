"""
修复 2111 写错问题：
1. 清除线上 tab 第 7 行（211110567 误写）
2. 向 QA tab 追加正确的 3 行
"""
import subprocess, json, os, sys

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ID_2111 = "1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk"
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}

def node_call(args, body=None):
    cmd = [NODE, GWS_JS] + args
    if body:
        cmd += ["--json", json.dumps(body, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    return r.returncode, r.stdout, r.stderr

# ── Step 1: 清除线上 tab 第 7 行 ──────────────────────────────────────────────
print("Step 1: 跳过（线上 tab 第 7 行已清除）")

# ── Step 2: 向 QA tab 追加 3 行 ───────────────────────────────────────────────
QA_TAB = "activity_calendar_x2（QA）"

# 3 行数据
rows = [
    # 211110567: 主活动，afcutc，占星节开始时间（936h 是占位，用户需更新）
    {
        "id": "211110567",
        "actvCfgId": "21127361",
        "comment": "占星节-掉落转付费-主活动",
        "schema": json.dumps({"typ": "schema", "id": [1,2,3,4,5,6]}, ensure_ascii=False),
        "trigger": json.dumps({"typ": "afcutc", "val": "936h"}, ensure_ascii=False),
    },
    # 211110568: 掉落活动，跟随主活动
    {
        "id": "211110568",
        "actvCfgId": "21127359",
        "comment": "占星节-掉落转付费-掉落活动",
        "schema": json.dumps({"typ": "schema", "id": [1,2,3,4,5,6]}, ensure_ascii=False),
        "trigger": json.dumps({"typ": "activity_start", "val": "21127361"}, ensure_ascii=False),
    },
    # 211110569: 礼包活动，跟随主活动
    {
        "id": "211110569",
        "actvCfgId": "21127360",
        "comment": "占星节-掉落转付费-礼包活动",
        "schema": json.dumps({"typ": "schema", "id": [1,2,3,4,5,6]}, ensure_ascii=False),
        "trigger": json.dumps({"typ": "activity_start", "val": "21127361"}, ensure_ascii=False),
    },
]

for row in rows:
    print(f"\nStep 2: 追加 {row['id']} → {row['comment']}")
    values = [["", row["id"], row["actvCfgId"], row["comment"], row["schema"], row["trigger"]]]
    body_append = {"values": values}
    params = json.dumps({
        "spreadsheetId": ID_2111,
        "range": f"{QA_TAB}!A:F",
        "valueInputOption": "RAW",
        "insertDataOption": "INSERT_ROWS",
    })
    rc, out, err = node_call(
        ["sheets", "spreadsheets", "values", "append",
         "--params", params],
        body_append
    )
    print(f"  append: rc={rc}")
    if rc != 0:
        print(f"  ERR: {err[:400]}")
        print(f"  OUT: {out[:400]}")
    else:
        try:
            d = json.loads(out)
            updated = d.get("updates", {}).get("updatedRange", "?")
            print(f"  OK: updatedRange={updated}")
        except:
            print(f"  OUT: {out[:300]}")

print("\n=== 完成 ===")
