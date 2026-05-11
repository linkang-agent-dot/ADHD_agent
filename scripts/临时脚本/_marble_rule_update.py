import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8')

result = subprocess.run(
    ['gws', 'auth', 'export', '--unmasked'],
    capture_output=True, text=True, encoding='utf-8', shell=True
)
creds_data = json.loads(result.stdout.strip())

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

credentials = Credentials(
    token=None,
    refresh_token=creds_data['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret'],
    scopes=['https://www.googleapis.com/auth/spreadsheets'],
)

service = build('sheets', 'v4', credentials=credentials)
sheets_api = service.spreadsheets()

SPREADSHEET_ID = '11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY'
STAGING_SHEET = 'AI翻译暂存'

# Load data
with open('C:/Users/linkang/_marble_rule_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Update existing rule row (7380)
r = sheets_api.values().get(
    spreadsheetId=SPREADSHEET_ID,
    range="'EVENT'!B7380:T7380"
).execute()
old_row = r.get('values', [[]])[0]
print(f'Old rule key: {old_row[0]}, cn first 60: {old_row[1][:60]}...')

new_rule_row = [old_row[0]] + data['rule_translations']
sheets_api.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range="'EVENT'!B7380:T7380",
    valueInputOption='RAW',
    body={'values': [new_rule_row]},
).execute()
print('Rule updated in EVENT row 7380')

# 2. Write box name + desc to staging
staging_rows = data['staging_rows']

spreadsheet = sheets_api.get(spreadsheetId=SPREADSHEET_ID, fields='sheets.properties').execute()
staging_sheet_id = None
for s in spreadsheet['sheets']:
    if s['properties']['title'] == STAGING_SHEET:
        staging_sheet_id = s['properties']['sheetId']
        break

result = sheets_api.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
).execute()
existing = result.get('values', [])
next_row = max(len(existing) + 1, 2)
end_row = next_row + len(staging_rows) - 1

sheets_api.values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{STAGING_SHEET}'!B{next_row}:U{end_row}",
    valueInputOption='RAW',
    body={'values': staging_rows},
).execute()

sheets_api.batchUpdate(
    spreadsheetId=SPREADSHEET_ID,
    body={'requests': [{
        'repeatCell': {
            'range': {
                'sheetId': staging_sheet_id,
                'startRowIndex': next_row - 1,
                'endRowIndex': end_row,
                'startColumnIndex': 0, 'endColumnIndex': 1,
            },
            'cell': {
                'dataValidation': {'condition': {'type': 'BOOLEAN'}, 'strict': True},
                'userEnteredValue': {'boolValue': False},
            },
            'fields': 'dataValidation,userEnteredValue',
        }
    }]},
).execute()

print(f'Box name+desc written to staging rows {next_row}-{end_row}')
print('Done!')
