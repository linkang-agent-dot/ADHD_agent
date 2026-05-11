# -*- coding: utf-8 -*-
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

SSID = "1B46X-aWpv0DXL9Q_sBvUkNBdLIw34wMPTnOLKQnPNOw"
SHEET = "换皮后数值"

def gws_update(range_str, values):
    cmd = json.dumps({
        "args": ["sheets","spreadsheets","values","update",
            "--params", json.dumps({
                "spreadsheetId": SSID,
                "range": f"'{SHEET}'!{range_str}",
                "valueInputOption": "RAW"
            }),
            "--json", json.dumps({"values": values})
        ]
    }, ensure_ascii=False)
    r = subprocess.run(["node","C:/ADHD_agent/scripts/gws_stdin.js"],
        input=cmd, capture_output=True, text=True, encoding='utf-8')
    ok = r.returncode == 0
    resp = json.loads(r.stdout) if r.stdout.strip() else {}
    print(f"  {'OK' if ok else 'FAIL'}: {range_str} ({resp.get('updatedCells','?')})")

# Clear stale rows 85-90
empty = ["","","","","","","","","","",""]
gws_update("A85:K90", [empty]*6)

# Also check and clear 104-121 (between totals and comparison)
# Row 104+ might have old simulation/comparison data
gws_update("A104:K121", [empty]*18)

# Also clear 133-136 (between old comparison end and package start)
gws_update("A133:K136", [empty]*4)

print("Cleanup done!")
