# -*- coding: utf-8 -*-
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

SSID = "1B46X-aWpv0DXL9Q_sBvUkNBdLIw34wMPTnOLKQnPNOw"
SHEET = "换皮后数值"

def gws_update(range_str, values):
    cmd_input = json.dumps({
        "args": [
            "sheets", "spreadsheets", "values", "update",
            "--params", json.dumps({
                "spreadsheetId": SSID,
                "range": f"'{SHEET}'!{range_str}",
                "valueInputOption": "USER_ENTERED"
            }),
            "--json", json.dumps({"values": values})
        ]
    }, ensure_ascii=False)

    result = subprocess.run(
        ["node", "C:/ADHD_agent/scripts/gws_stdin.js"],
        input=cmd_input, capture_output=True, text=True, encoding='utf-8'
    )
    print(f"  returncode: {result.returncode}")
    print(f"  stdout: {result.stdout[:300]}")
    print(f"  stderr: {result.stderr[:300]}")
    return result.returncode == 0

# Small test
print("Test 1: small write")
gws_update("A137:C138", [["test1", "test2", "test3"], ["a", "b", "c"]])
