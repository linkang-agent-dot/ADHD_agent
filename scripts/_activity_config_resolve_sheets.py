# -*- coding: utf-8 -*-
import json
import subprocess

SPREADSHEET = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"
TARGET_GIDS = {1922183355, 1943943957}

cmd = (
    "gws sheets spreadsheets get --params "
    + json.dumps(json.dumps({"spreadsheetId": SPREADSHEET}))
    + " --format json"
)
p = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8")
p.check_returncode()
data = json.loads(p.stdout)
for s in data.get("sheets", []):
    props = s.get("properties", {})
    sid = props.get("sheetId")
    title = props.get("title", "")
    if sid in TARGET_GIDS:
        print(sid, repr(title))
