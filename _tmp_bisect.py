import subprocess, json

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

full_data = [
    ['X2节日-第一期循环（前35天）甘特图'],
    ['策略：不改变X2基本节日循环，新增已验证P2形式，预期新增ARPC +7.8'],
    [],
    ['分类', '付费模块', '开发类型', '负责人', '活动ID', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', '备注'],
    ['累充', '累充', '复用', 'liusiyi', '211201012', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['主城GACHA', 'GACHA+累计活动', '复用', 'gongliang->linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['', '每日GACHA礼包', '新增', 'gongliang->linkang', '', '','','Y','Y','Y','Y','Y', '第3周起 | P2-ARPC: 0.6'],
    ['行军皮肤', '节日BP', '复用', 'minghao', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['强消耗活动', '强消耗扭蛋', '复用', 'minghao', '', '','','Y','Y','Y','Y','Y', '第3周起'],
    ['装饰', '大富翁-节日装饰', '新增', 'gongliang->minghao', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周 | P2-ARPC: 3.2'],
    ['活跃类', '掉落转付费', '新增', 'linkang', '', 'Y','Y','Y','?','?','?','?', '前3周待确认 | P2-ARPC: 0.5'],
    ['', '7日', '复用', 'liusiyi', '211201011', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['中小R付费', '周卡', '搬运', 'minghao', '211201010', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    ['礼包付费', '抢购礼包-养成投放', '新增', 'gongliang->liusiyi', '21127223', '','','Alt','','','Alt','?', '隔周W3/W6 | P2-ARPC: 3.5'],
    ['节日卡包', '节日卡包', '借用圣诞', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
    [],
    ['Y=活跃  空白=未启动  Alt=交替投放  ?=待确认'],
    ['新增内容合计ARPC预期: 0.6+3.2+0.5+3.5 = 7.8'],
]

def try_write(sheet, data, label):
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': f'{sheet}!A1', 'valueInputOption': 'USER_ENTERED'}, ensure_ascii=False)
    body = json.dumps({'values': data}, ensure_ascii=False)
    result = subprocess.run([GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body], capture_output=True)
    out = result.stdout.decode('utf-8', errors='replace')
    ok = result.returncode == 0 and len(result.stdout) > 0
    print(f"  [{label}] rc={result.returncode} len={len(body)} {'OK' if ok else 'FAIL'} {out[:60].strip()}")
    return ok

# Binary search: find which row causes the failure
print("Binary search on 前期循环-甘特:")
for i in range(1, len(full_data)+1):
    ok = try_write('前期循环-甘特', full_data[:i], f'rows 1-{i}')
    if not ok:
        print(f"  --> FAIL at row {i}: {full_data[i-1]}")
        break
