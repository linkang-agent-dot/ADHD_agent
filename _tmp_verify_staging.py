import json
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    return Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

creds = get_credentials()
service = build("sheets", "v4", credentials=creds)
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{STAGING_SHEET}'!B:D"
).execute()
rows = result.get("values", [])
print(f"Total rows in staging: {len(rows)}")
print("Last 16 rows (tab | key | cn):")
for r in rows[-16:]:
    cols = r[:3] if len(r) >= 3 else r
    print(" | ".join(str(c) for c in cols))
