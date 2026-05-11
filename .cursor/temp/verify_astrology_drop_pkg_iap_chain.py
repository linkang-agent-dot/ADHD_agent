import json
import os
import subprocess

NODE = r"C:\Program Files\nodejs\node.exe"
GWS_JS = r"C:\Users\linkang\AppData\Roaming\npm\node_modules\@googleworkspace\cli\run-gws.js"
ENV = {**os.environ, "NODE_PATH": r"C:\Users\linkang\AppData\Roaming\npm\node_modules"}


def call(args):
    res = subprocess.run([NODE, GWS_JS] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if res.returncode != 0:
        raise RuntimeError(res.stdout + res.stderr)
    return json.loads(res.stdout)


def get(spreadsheet_id, range_name):
    params = json.dumps({"spreadsheetId": spreadsheet_id, "range": range_name}, ensure_ascii=False)
    return call(["sheets", "spreadsheets", "values", "get", "--params", params]).get("values", [])


def main():
    ids = {
        "2112": "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo",
        "2121": "1i_rhQfUNhbDdL7GYeQV7ZMGUvO6o37s18lbMBIJYge4",
        "2011": "1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY",
        "2013": "1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E",
    }
    checks = {
        "2112_21127360": get(ids["2112"], "activity_config_QA!B1468:J1468"),
        "2121_new": get(ids["2121"], "activity_special!B2315:M2315"),
        "2011_new": get(ids["2011"], "iap_config_x2qa!B3450:M3450"),
        "2013_new": get(ids["2013"], "iap_template_x2（qa）!B6725:D6728"),
        "2121_old": get(ids["2121"], "activity_special!B2109:M2109"),
        "2011_old": get(ids["2011"], "iap_config_x2qa!B3429:M3429"),
    }
    for name, rows in checks.items():
        print(f"=== {name} ===")
        print(json.dumps(rows, ensure_ascii=False))


if __name__ == "__main__":
    main()
