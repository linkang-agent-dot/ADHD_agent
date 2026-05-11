# -*- coding: utf-8 -*-
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

SSID = "1B46X-aWpv0DXL9Q_sBvUkNBdLIw34wMPTnOLKQnPNOw"
SHEET = "换皮后数值"

def gws_update(range_str, values, mode="RAW"):
    cmd_input = json.dumps({
        "args": ["sheets", "spreadsheets", "values", "update",
            "--params", json.dumps({
                "spreadsheetId": SSID,
                "range": f"'{SHEET}'!{range_str}",
                "valueInputOption": mode
            }),
            "--json", json.dumps({"values": values})
        ]
    }, ensure_ascii=False)
    r = subprocess.run(["node","C:/ADHD_agent/scripts/gws_stdin.js"],
        input=cmd_input, capture_output=True, text=True, encoding='utf-8')
    resp = json.loads(r.stdout) if r.stdout.strip() else {}
    print(f"  {'OK' if r.returncode==0 else 'FAIL'}: {range_str} ({resp.get('updatedCells','?')})")

# Fix row 137: remove test data residue, just "礼包设计"
gws_update("A137:K138", [
    ["礼包设计","","","","","","","","","",""],
    ["","","","","","","","","","",""],
])

# Fix row 139: was "礼包总览" header, truncated by column limit
gws_update("A139:H139", [
    ["", "礼包总览", "", "", "", "", "", ""],
])

print("Fixes applied!")
