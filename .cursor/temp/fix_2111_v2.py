"""
v2: 
1. 删除 QA tab 第 7-9 行（旧数据下移导致的错位，恢复原位）
2. 正确追加 3 行到 QA tab 末尾（用 OVERWRITE 模式 + 手动找末行）
"""
import subprocess, json, os

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ID_2111 = "1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk"
QA_SHEET_ID = None  # 稍后查询
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}

def node_call(args, body=None):
    cmd = [NODE, GWS_JS] + args
    if body:
        cmd += ["--json", json.dumps(body, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    return r.returncode, r.stdout, r.stderr

# ── Step 0: 获取 QA tab 的 sheetId ───────────────────────────────────────────
print("Step 0: 获取 QA tab sheetId...")
params = json.dumps({"spreadsheetId": ID_2111, "includeGridData": False})
rc, out, err = node_call(["sheets", "spreadsheets", "get", "--params", params])
if rc != 0:
    print(f"  ERR: {err[:300]}\n  OUT: {out[:300]}")
    exit(1)

d = json.loads(out)
qa_sheet_id = None
for sheet in d.get("sheets", []):
    title = sheet["properties"]["title"]
    if "QA" in title and "x2" in title and "线上" not in title:
        qa_sheet_id = sheet["properties"]["sheetId"]
        print(f"  QA tab: {title!r} → sheetId={qa_sheet_id}")
        break

if qa_sheet_id is None:
    print("  未找到 QA tab！sheets:", [s["properties"]["title"] for s in d.get("sheets", [])])
    exit(1)

params_batch = json.dumps({"spreadsheetId": ID_2111})
print("\nStep 1: 已删除（上次执行完成）")

# ── Step 2: 找 QA tab 末行号 ────────────────────────────────────────────────
print("\nStep 2: 读 QA tab B 列找末行号...")
params_read = json.dumps({"spreadsheetId": ID_2111, "range": "activity_calendar_x2（QA）!B:B"})
rc, out, err = node_call(["sheets", "spreadsheets", "values", "get", "--params", params_read])
if rc != 0:
    print(f"  ERR: {err[:300]}")
    exit(1)
d2 = json.loads(out)
rows_b = d2.get("values", [])
last_row = len(rows_b)  # 1-based
print(f"  B列总行数: {last_row}，末行 ID: {rows_b[-1][0] if rows_b else '?'}")

# 下一个空行（追加位置）
next_row = last_row + 1
print(f"  追加位置: row {next_row}")

# ── Step 3: 写入 3 行 ───────────────────────────────────────────────────────
rows_data = [
    ["", "211110567", "21127361", "占星节-掉落转付费-主活动",
     json.dumps({"typ": "schema", "id": [1,2,3,4,5,6]}, ensure_ascii=False),
     json.dumps({"typ": "afcutc", "val": "936h"}, ensure_ascii=False)],
    ["", "211110568", "21127359", "占星节-掉落转付费-掉落活动",
     json.dumps({"typ": "schema", "id": [1,2,3,4,5,6]}, ensure_ascii=False),
     json.dumps({"typ": "activity_start", "val": "21127361"}, ensure_ascii=False)],
    ["", "211110569", "21127360", "占星节-掉落转付费-礼包活动",
     json.dumps({"typ": "schema", "id": [1,2,3,4,5,6]}, ensure_ascii=False),
     json.dumps({"typ": "activity_start", "val": "21127361"}, ensure_ascii=False)],
]

# 先扩展 sheet 3 行
print(f"\nStep 3a: 扩展 QA tab 3 行...")
body_expand = {
    "requests": [{
        "appendDimension": {
            "sheetId": qa_sheet_id,
            "dimension": "ROWS",
            "length": 3
        }
    }]
}
rc, out, err = node_call(
    ["sheets", "spreadsheets", "batchUpdate", "--params", params_batch],
    body_expand
)
print(f"  appendDimension rc={rc}")
if rc != 0:
    print(f"  ERR: {err[:300]}\n  OUT: {out[:300]}")
    exit(1)
print("  OK: 扩展了 3 行")

target_range = f"activity_calendar_x2（QA）!A{next_row}:F{next_row + 2}"
print(f"\nStep 3b: 写入 3 行到 {target_range}...")
body_write = {"values": rows_data}
params_write = json.dumps({
    "spreadsheetId": ID_2111,
    "range": target_range,
    "valueInputOption": "RAW",
})
rc, out, err = node_call(
    ["sheets", "spreadsheets", "values", "update", "--params", params_write],
    body_write
)
print(f"  update rc={rc}")
if rc != 0:
    print(f"  ERR: {err[:400]}\n  OUT: {out[:400]}")
else:
    d3 = json.loads(out)
    print(f"  OK: updatedRange={d3.get('updatedRange')}, updatedRows={d3.get('updatedRows')}")

print("\n=== 完成 ===")
