"""写入 X2 2112 21127361 主活动 — 用 ensure_ascii=True 避免编码问题"""
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

# 中文用 unicode escape
comment = "\u5360\u661f\u8282-\u6389\u843d\u8f6c\u4ed8\u8d39-\u4e3b\u6d3b\u52a8"  # 占星节-掉落转付费-主活动

row3 = ["", "21127361", comment,
        "event_labor_2025_shop_schema1", "0", "49995", "211201003",
        filter_json, text_main, comp_main_json, desc_main,
        "21191331", "1", EMPTY_STR,
        "assets/operation/P2dlcimg/activityImg/EventBanner_BG_428.png",
        "0", "0", "0", "21127359", "0", "[]", EMPTY_STR,
        "0", "1511030002", "1", EMPTY_STR, "0"]

# ensure_ascii=True: 中文 unicode escape → ASCII safe
jv = json.dumps([row3], ensure_ascii=True)
print("JSON len:", len(jv))
print("Start:", jv[:80])

r = subprocess.run(
    [GWS, "sheets", "+append", "--spreadsheet", ID_2112, "--json-values", jv],
    capture_output=True, text=True, encoding="utf-8", errors="replace"
)
out = (r.stdout or "")[:500]
err = (r.stderr or "")[:200]
print("Exit:", r.returncode)

import re
m = re.search(r'"updatedRange"\s*:\s*"([^"]+)"', out)
if m:
    print("updatedRange:", m.group(1))
else:
    print("OUT:", out[:300])
    print("ERR:", err)
