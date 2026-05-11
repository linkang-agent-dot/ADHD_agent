# Fix dec_buff_pilot_increase_name/desc Chinese text
import subprocess, json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding="utf-8")

def get_sheets_api():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    creds = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=creds).spreadsheets()

sheets_api = get_sheets_api()
SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"

# Row 9405: dec_buff_pilot_increase_name
# Fix cn (col C), zh (col H =繁体), cns (col T)
# cn: 飙车族受到射击手的伤害减少
# zh: 飆車族受到射擊手的傷害減少
new_name_cn = "飙车族受到射击手的伤害减少"
new_name_zh = "飆車族受到射擊手的傷害減少"

sheets_api.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="'EVENT'!C9405",
    valueInputOption="RAW",
    body={"values": [[new_name_cn]]},
).execute()
sheets_api.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="'EVENT'!H9405",
    valueInputOption="RAW",
    body={"values": [[new_name_zh]]},
).execute()
sheets_api.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="'EVENT'!T9405",
    valueInputOption="RAW",
    body={"values": [[new_name_cn]]},
).execute()
print("name: cn/zh/cns updated")

# Row 9406: dec_buff_pilot_increase_desc
# Fix cn, zh, cns
new_desc_cn = "减少飙车族受到射击手的伤害{0}。技能持续2小时，技能使用后冷却72小时。"
new_desc_zh = "減少飆車族受到射擊手的傷害{0}。技能持續2小時，技能使用後冷卻72小時。"

sheets_api.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="'EVENT'!C9406",
    valueInputOption="RAW",
    body={"values": [[new_desc_cn]]},
).execute()
sheets_api.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="'EVENT'!H9406",
    valueInputOption="RAW",
    body={"values": [[new_desc_zh]]},
).execute()
sheets_api.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="'EVENT'!T9406",
    valueInputOption="RAW",
    body={"values": [[new_desc_cn]]},
).execute()
print("desc: cn/zh/cns updated")

# Verify
r = sheets_api.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range="'EVENT'!B9405:D9406"
).execute()
for row in r.get("values", []):
    print(f"  {row[0]}: {row[1]}")
