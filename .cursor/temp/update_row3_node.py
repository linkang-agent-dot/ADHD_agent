"""
绕过 CMD 8192 字符限制：直接用 node 调用 run-gws.js
更新 activity_config_QA!J1469 为完整 activity_components
"""
import subprocess, json, os

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ID_2112 = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"

comp_main = (
    [{"typ":"actv_links","id":212100317}] +
    [{"typ":"drop_topay_show","id":212100315}] +
    [{"typ":"drop_topay","id":212100314}] +
    [{"typ":"new_progress","id":i} for i in range(212100319, 212100499)] +
    [{"typ":"retake","id":21371255},{"typ":"retake","id":21371256},
     {"typ":"retake","id":21371257},{"typ":"retake","id":21371258}] +
    [{"typ":"exchange","id":i} for i in range(21161748, 21161758)]
)
comp_json = json.dumps(comp_main, separators=(",",":"))
print(f"Components: {len(comp_json)} chars, {len(comp_main)} items")

# batchUpdate：更新 J1469 这一个单元格
params_json = json.dumps({"spreadsheetId": ID_2112})
body_json = json.dumps({
    "valueInputOption": "RAW",
    "data": [{"range": "activity_config_QA!J1469", "values": [[comp_json]]}]
}, ensure_ascii=False)

out_file = r"C:\Users\linkang\AppData\Local\Temp\node_update_result.json"
with open(out_file, "w", encoding="utf-8") as f:
    r = subprocess.run(
        [NODE, GWS_JS,
         "sheets", "spreadsheets", "values", "batchUpdate",
         "--params", params_json,
         "--json", body_json],
        stdout=f, stderr=subprocess.STDOUT,
        env={**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}
    )

print(f"Exit: {r.returncode}")
result = open(out_file, "rb").read().decode("utf-8", errors="replace")
print("Result:", result[:600])
