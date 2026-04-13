import subprocess, json, time

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

def try_write_ascii(sheet, data, label):
    time.sleep(4)
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': f'{sheet}!A1', 'valueInputOption': 'USER_ENTERED'}, ensure_ascii=True)
    body = json.dumps({'values': data}, ensure_ascii=True)
    result = subprocess.run([GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body], capture_output=True)
    ok = result.returncode == 0 and len(result.stdout) > 0
    print(f"  [{label}] rc={result.returncode} len={len(body)} {'OK' if ok else 'FAIL'}")
    return ok

# Full data without the "->"-containing rows
print("Test A: full data WITHOUT the -> rows:")
try_write_ascii('前期循环-甘特', [
    ['X2节日-第一期循环（前35天）甘特图'],
    ['策略：不改变X2基本节日循环，新增已验证P2形式，预期新增ARPC +7.8'],
    [],
    ['分类', '付费模块', '开发类型', '负责人', '活动ID', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', '备注'],
    ['累充', '累充', '复用', 'liusiyi', '211201012', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['行军皮肤', '节日BP', '复用', 'minghao', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['强消耗活动', '强消耗扭蛋', '复用', 'minghao', '', '','','Y','Y','Y','Y','Y', '第3周起'],
    ['', '7日', '复用', 'liusiyi', '211201011', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['中小R付费', '周卡', '搬运', 'minghao', '211201010', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
], 'no arrows')

print("Test B: just the -> rows:")
try_write_ascii('前期循环-甘特', [
    ['主城GACHA', 'GACHA+累计活动', '复用', 'gongliang->linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['装饰', '大富翁-节日装饰', '新增', 'gongliang->minghao', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['礼包付费', '抢购礼包', '新增', 'gongliang->liusiyi', '21127223', '','','Alt','','','Alt','?', '隔周'],
], 'arrows only')

print("Test C: replace -> with _ in data:")
try_write_ascii('前期循环-甘特', [
    ['X2节日-第一期循环（前35天）甘特图'],
    ['分类', '付费模块', '开发类型', '负责人', '活动ID', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', '备注'],
    ['主城GACHA', 'GACHA+累计活动', '复用', 'gongliang_linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['装饰', '大富翁', '新增', 'gongliang_minghao', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['礼包付费', '抢购礼包', '新增', 'gongliang_liusiyi', '21127223', '','','Alt','','','Alt','?', '隔周'],
    ['', '7日', '复用', 'liusiyi', '211201011', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['中小R付费', '周卡', '搬运', 'minghao', '211201010', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
], 'no arrows replaced')
