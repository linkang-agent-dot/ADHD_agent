# -*- coding: utf-8 -*-
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

SSID = "1B46X-aWpv0DXL9Q_sBvUkNBdLIw34wMPTnOLKQnPNOw"
SHEET_GID = 531423017

def gws(args_list):
    cmd = json.dumps({"args": args_list}, ensure_ascii=False)
    r = subprocess.run(["node","C:/ADHD_agent/scripts/gws_stdin.js"],
        input=cmd, capture_output=True, text=True, encoding='utf-8')
    print(f"  rc={r.returncode}")
    print(f"  stdout={r.stdout[:300]}")
    print(f"  stderr={r.stderr[:300]}")
    return r.returncode == 0

def rgb(r,g,b): return {"red":r/255,"green":g/255,"blue":b/255}

# Small test: just bold row 1
reqs = [{
    "repeatCell": {
        "range": {"sheetId":SHEET_GID, "startRowIndex":0, "endRowIndex":1, "startColumnIndex":0, "endColumnIndex":5},
        "cell": {"userEnteredFormat": {
            "textFormat": {"bold": True, "fontSize": 12, "foregroundColor": rgb(26,115,232)},
        }},
        "fields": "userEnteredFormat(textFormat)"
    }
}]

print("Test: bold+color row 1")
gws(["sheets","spreadsheets","batchUpdate",
    "--params", json.dumps({"spreadsheetId":SSID}),
    "--json", json.dumps({"requests":reqs})])
