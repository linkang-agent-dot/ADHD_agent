"""Test full row3 write, capture error properly"""
import subprocess, json, os, sys

GWS = r"C:\Users\linkang\AppData\Roaming\npm\gws.cmd"
ID_2112 = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"

filter_json = json.dumps({"op":"ge","typ":"building","id":111811,"val":6}, separators=(",",":"))
text_main = json.dumps({"group_label":"LC_EVENT_droptopay_tuohuang_title","label":"LC_EVENT_droptopay_tuohuang_title","title":"LC_EVENT_droptopay_tuohuang_title"}, separators=(",",":"))
comp_main = ([{"typ":"actv_links","id":212100317}]+[{"typ":"drop_topay_show","id":212100315}]+[{"typ":"drop_topay","id":212100314}]+[{"typ":"new_progress","id":i} for i in range(212100319,212100499)]+[{"typ":"retake","id":21371255},{"typ":"retake","id":21371256},{"typ":"retake","id":21371257},{"typ":"retake","id":21371258}]+[{"typ":"exchange","id":i} for i in range(21161748,21161758)])
comp_json = json.dumps(comp_main, separators=(",",":"))
desc_main = json.dumps({"rule":"LC_EVENT_droptopay_tuohuang_rule"}, separators=(",",":"))
comment = "\u5360\u661f\u8282-\u6389\u843d\u8f6c\u4ed8\u8d39-\u4e3b\u6d3b\u52a8"

row3 = ["","21127361",comment,"event_labor_2025_shop_schema1","0","49995","211201003",filter_json,text_main,comp_json,desc_main,"21191331","1",'""',"assets/operation/P2dlcimg/activityImg/EventBanner_BG_428.png","0","0","0","21127359","0","[]",'""',"0","1511030002","1",'""',"0"]

# Check - skip since row is already at 1469 with empty components
# We need to UPDATE J1469
# Use gws sheets spreadsheets values batchUpdate

jv_update = json.dumps({
    "valueInputOption": "RAW",
    "data": [{"range": "activity_config_QA!J1469", "values": [[comp_json]]}]
}, ensure_ascii=True)

print(f"Update JSON len: {len(jv_update)}")

out_file = r"C:\Users\linkang\AppData\Local\Temp\update_test.json"
with open(out_file, "w", encoding="utf-8") as f:
    r = subprocess.run(
        [GWS, "sheets", "spreadsheets", "values", "batchUpdate",
         "--params", json.dumps({"spreadsheetId": ID_2112}, ensure_ascii=True),
         "--json", jv_update],
        stdout=f, stderr=subprocess.STDOUT
    )

print(f"Exit: {r.returncode}")
result = open(out_file, "rb").read().decode("utf-8", errors="replace")
print("Result:", result[:400])
