import subprocess, json, time

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

def try_write(sheet, data, label):
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': f'{sheet}!A1', 'valueInputOption': 'USER_ENTERED'}, ensure_ascii=False)
    body = json.dumps({'values': data}, ensure_ascii=False)
    result = subprocess.run([GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body], capture_output=True)
    ok = result.returncode == 0 and len(result.stdout) > 0
    print(f"  [{label}] rc={result.returncode} {'OK' if ok else 'FAIL'}")
    time.sleep(3)

print("Test 1: write '+' char to 5月 (if + is issue, should fail):")
try_write('5月占星节-甘特', [['GACHA+累计活动']], 'plus in 5yue')

print("Test 2: write '6月' data WITHOUT '+' (replace with 'and'):")
try_write('6月拓荒节-甘特', [
    ['X2-6月拓荒节 甘特图'],
    ['节日付费', '累充 and 排行榜 and 乐透', '新开发', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
], 'no-plus in 6yue')

print("Test 3: write '6月' data WITH '+' in json escaped:")
data_with_plus = [['节日付费', '累充+排行榜+乐透', '全程']]
# Try ensure_ascii=True to see if that changes anything
body_ascii = json.dumps({'values': data_with_plus}, ensure_ascii=True)
params = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': '6月拓荒节-甘特!A1', 'valueInputOption': 'USER_ENTERED'}, ensure_ascii=False)
result = subprocess.run([GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body_ascii], capture_output=True)
print(f"  [ascii-encoded +] rc={result.returncode} {'OK' if result.returncode==0 and len(result.stdout)>0 else 'FAIL'}")
