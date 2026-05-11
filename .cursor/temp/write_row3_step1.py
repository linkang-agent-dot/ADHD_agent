"""Step 1: 写入 21127361 主活动简化版（空components），获取行号"""
import subprocess, json, os, re

GWS = r"C:\Users\linkang\AppData\Roaming\npm\gws.cmd"
ID_2112 = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"
OUT = r"C:\Users\linkang\AppData\Local\Temp\row3_step1.json"

filter_json = json.dumps({"op":"ge","typ":"building","id":111811,"val":6}, separators=(",",":"))
text_main = json.dumps({
    "group_label":"LC_EVENT_droptopay_tuohuang_title",
    "label":"LC_EVENT_droptopay_tuohuang_title",
    "title":"LC_EVENT_droptopay_tuohuang_title"
}, separators=(",",":"))
desc_main = json.dumps({"rule":"LC_EVENT_droptopay_tuohuang_rule"}, separators=(",",":"))

comment = "\u5360\u661f\u8282-\u6389\u843d\u8f6c\u4ed8\u8d39-\u4e3b\u6d3b\u52a8"  # 占星节-掉落转付费-主活动

# 先用空的 activity_components 写入
row3_simple = ["", "21127361", comment,
               "event_labor_2025_shop_schema1", "0", "49995", "211201003",
               filter_json, text_main,
               "[]",  # 先空
               desc_main,
               "21191331", "1", '""',
               "assets/operation/P2dlcimg/activityImg/EventBanner_BG_428.png",
               "0", "0", "0", "21127359", "0", "[]", '""',
               "0", "1511030002", "1", '""', "0"]

jv = json.dumps([row3_simple], ensure_ascii=True)
print(f"JSON len: {len(jv)}")

with open(OUT, "w", encoding="utf-8") as f:
    r = subprocess.run(
        [GWS, "sheets", "+append", "--spreadsheet", ID_2112, "--json-values", jv],
        stdout=f, stderr=subprocess.STDOUT
    )

os.write(1, f"Exit: {r.returncode}\n".encode())

result = open(OUT, encoding="utf-8", errors="replace").read()
m = re.search(r'"updatedRange"\s*:\s*"([^"]+)"', result)
if m:
    rng = m.group(1)
    os.write(1, f"updatedRange: {rng}\n".encode())
    # 提取行号 (activity_config_QA!A1469:... → 1469)
    row_num = re.search(r'!A(\d+)', rng)
    if row_num:
        os.write(1, f"Row number: {row_num.group(1)}\n".encode())
else:
    os.write(1, f"Result: {result[:300]}\n".encode())
