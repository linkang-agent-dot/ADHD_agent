import subprocess, json

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# Test the specific failing row
test_data = [
    ['cumul', 'cumul', 'reuse', 'liusiyi', '211201012', 'Y','Y','Y','Y','Y','Y','Y', 'all 7 weeks'],
    ['main GACHA', 'GACHA+cumul activity', 'reuse', 'gongliang->linkang', '', 'Y','Y','Y','Y','Y','Y','Y', 'all 7 weeks'],
]

params = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': '前期循环-甘特!A1', 'valueInputOption': 'USER_ENTERED'}, ensure_ascii=False)
body = json.dumps({'values': test_data}, ensure_ascii=False)

result = subprocess.run([GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body], capture_output=True)
out = result.stdout.decode('utf-8', errors='replace')
err = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
print(f"ASCII test: rc={result.returncode} out={out[:200]}")

# Test with Chinese
test_data2 = [
    ['累充', '累充', '复用', 'liusiyi', '211201012', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['主城GACHA', 'GACHA加累计活动', '复用', 'gongliang->linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
]

body2 = json.dumps({'values': test_data2}, ensure_ascii=False)
result2 = subprocess.run([GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body2], capture_output=True)
out2 = result2.stdout.decode('utf-8', errors='replace')
print(f"Chinese no-plus test: rc={result2.returncode} out={out2[:200]}")

# Test with Chinese + plus
test_data3 = [
    ['累充', '累充', '复用', 'liusiyi', '211201012', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['主城GACHA', 'GACHA+累计活动', '复用', 'gongliang->linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
]

body3 = json.dumps({'values': test_data3}, ensure_ascii=False)
result3 = subprocess.run([GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body3], capture_output=True)
out3 = result3.stdout.decode('utf-8', errors='replace')
print(f"Chinese with-plus test: rc={result3.returncode} out={out3[:200]}")
