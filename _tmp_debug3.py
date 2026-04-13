import subprocess, json, time

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

def try_write(sheet, data, label, sleep=0):
    if sleep: time.sleep(sleep)
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': f'{sheet}!A1', 'valueInputOption': 'USER_ENTERED'}, ensure_ascii=False)
    body = json.dumps({'values': data}, ensure_ascii=False)
    result = subprocess.run([GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body], capture_output=True)
    out = result.stdout.decode('utf-8', errors='replace')
    ok = result.returncode == 0 and len(result.stdout) > 0
    print(f"  [{label}] rc={result.returncode} len={len(body)} {'OK' if ok else 'FAIL'} | {out[:80].strip()}")
    return ok

# Test directly writing just row 6 content (without previous writes)
print("Test: write only row 6 content directly to fresh sheet:")
try_write('前期循环-甘特', [['主城GACHA', 'GACHA+累计活动', '复用', 'gongliang->linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周']], 'row6 only', sleep=2)

print("Test: write rows 1-6 in one shot with 3s sleep:")
try_write('前期循环-甘特', [
    ['X2节日-第一期循环（前35天）甘特图'],
    ['策略：不改变X2基本节日循环，新增已验证P2形式，预期新增ARPC +7.8'],
    [],
    ['分类', '付费模块', '开发类型', '负责人', '活动ID', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', '备注'],
    ['累充', '累充', '复用', 'liusiyi', '211201012', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['主城GACHA', 'GACHA plus 累计活动', '复用', 'gongliang-to-linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
], 'rows 1-6 (no special chars)', sleep=3)

print("Test: with original content row6:")
try_write('前期循环-甘特', [
    ['X2节日-第一期循环（前35天）甘特图'],
    ['策略'],
    [],
    ['分类', '付费模块'],
    ['累充', '累充'],
    ['主城GACHA', 'GACHA+累计活动'],
], 'rows 1-6 min', sleep=3)
