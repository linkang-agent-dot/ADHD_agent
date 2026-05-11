"""写入 X2 2112 21127361 主活动（单独调试）"""
import subprocess, json, sys, os

GWS = r"C:\Users\linkang\AppData\Roaming\npm\gws.cmd"
ID_2112 = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"

EMPTY_STR = '""'
filter_json = json.dumps({"op":"ge","typ":"building","id":111811,"val":6}, separators=(",",":"))
text_main = json.dumps({
    "group_label":"LC_EVENT_droptopay_tuohuang_title",
    "label":"LC_EVENT_droptopay_tuohuang_title",
    "title":"LC_EVENT_droptopay_tuohuang_title"
}, separators=(",",":"))

comp_main = (
    [{"typ":"actv_links","id":212100317}] +
    [{"typ":"drop_topay_show","id":212100315}] +
    [{"typ":"drop_topay","id":212100314}] +
    [{"typ":"new_progress","id":i} for i in range(212100319, 212100499)] +
    [{"typ":"retake","id":21371255},{"typ":"retake","id":21371256},
     {"typ":"retake","id":21371257},{"typ":"retake","id":21371258}] +
    [{"typ":"exchange","id":i} for i in range(21161748, 21161758)]
)
comp_main_json = json.dumps(comp_main, separators=(",",":"))
desc_main = json.dumps({"rule":"LC_EVENT_droptopay_tuohuang_rule"}, separators=(",",":"))

row3 = ["", "21127361", "占星节-掉落转付费-主活动",
        "event_labor_2025_shop_schema1", "0", "49995", "211201003",
        filter_json, text_main, comp_main_json, desc_main,
        "21191331", "1", EMPTY_STR,
        "assets/operation/P2dlcimg/activityImg/EventBanner_BG_428.png",
        "0", "0", "0", "21127359", "0", "[]", EMPTY_STR,
        "0", "1511030002", "1", EMPTY_STR, "0"]

jv = json.dumps([row3], ensure_ascii=False)
print("JSON len:", len(jv))

# 写到临时文件，通过文件传参
tmp = r"C:\Users\linkang\AppData\Local\Temp\row3_values.json"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(jv)

# 用 PowerShell 调用 gws，从文件读 json-values
out_file = r"C:\Users\linkang\AppData\Local\Temp\row3_result.json"
ps_cmd = f'$jv = Get-Content "{tmp}" -Raw -Encoding UTF8; gws sheets "+append" --spreadsheet {ID_2112} --json-values $jv > "{out_file}" 2>&1'
r = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("PS Exit:", r.returncode)
print("PS OUT:", r.stdout[:200])
print("PS ERR:", r.stderr[:200])

if os.path.exists(out_file):
    with open(out_file, encoding="utf-8", errors="replace") as f:
        content = f.read()
    print("GWS Result:", content[:500])
