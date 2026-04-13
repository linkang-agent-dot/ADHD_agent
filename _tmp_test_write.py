import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# Test with different sheet names
test_sheets = ['前期循环-甘特', '6月拓荒节-甘特', '7月烟火庆典-甘特', '5月占星节-甘特', '总览-排期对比']

for sheet in test_sheets:
    params = json.dumps({
        'spreadsheetId': SPREADSHEET_ID,
        'range': f'{sheet}!A1',
        'valueInputOption': 'USER_ENTERED'
    }, ensure_ascii=False)
    body = json.dumps({'values': [['test123']]}, ensure_ascii=False)
    
    result = subprocess.run(
        [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update',
         '--params', params, '--json', body],
        capture_output=True
    )
    stdout = result.stdout.decode('utf-8', errors='replace')
    returncode = result.returncode
    print(f"Sheet '{sheet}': rc={returncode} | stdout={stdout[:100].strip()}")
