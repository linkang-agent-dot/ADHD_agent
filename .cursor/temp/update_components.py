"""
用 gws auth export + google-auth 直接调 Sheets API
更新 activity_config_QA!J1469 为完整 activity_components
"""
import subprocess, json, os, urllib.request

GWS = r"C:\Users\linkang\AppData\Roaming\npm\gws.cmd"

# 1. 获取 refresh_token
r = subprocess.run([GWS, "auth", "export"],
                   capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
creds = json.loads(r.stdout)

# 2. 用 google.oauth2.credentials 刷新 token
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

credentials = Credentials(
    token=None,
    refresh_token=creds["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=creds["client_id"],
    client_secret=creds["client_secret"]
)
credentials.refresh(Request())
access_token = credentials.token
print("Token OK:", access_token[:20] + "...")

# 3. 构建 activity_components
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
print(f"Components len: {len(comp_json)}, items: {len(comp_main)}")

# 4. batchUpdate 只更新 J1469 (activity_components = column 10 = J)
ID_2112 = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"
url = f"https://sheets.googleapis.com/v4/spreadsheets/{ID_2112}/values:batchUpdate"

body = {
    "valueInputOption": "RAW",
    "data": [
        {
            "range": "activity_config_QA!J1469",
            "values": [[comp_json]]
        }
    ]
}
body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")

req = urllib.request.Request(
    url,
    data=body_bytes,
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        print("Updated:", result.get("totalUpdatedCells"), "cells")
        if result.get("responses"):
            for r2 in result["responses"]:
                print("  -", r2.get("updatedRange"), r2.get("updatedCells"), "cells")
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print(e.read().decode())
