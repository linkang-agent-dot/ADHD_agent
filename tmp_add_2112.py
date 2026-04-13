import subprocess, json, os

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
SHEET = '1RFAyBfpG3-8rm3ugNn3NHFdeDg8Erha0VttGzokIy6E'
TAB = '复活节checklist'

# 活动名 -> 2112 ID 映射（来自 QA 页签）
ID_MAP = {
    '主城特效累充bingo':           '21127692',
    '主城特效累充-联盟版':          '21127657',
    '主城特效累充-服务器版':         '21127658',
    '推币机':                     '21127801, 21127802',
    '长节日BP（高级行军皮肤）':      '21127638',
    '大富翁-节日装饰':             '21127614',
    '大富翁-团队合作子活动':        '21127751',
    '7日':                        '21127752',
    '行军特效-付费率':             '21127695',
    '行军表情-付费率':             '21127697',
    '预购连锁礼包':               '21127630, 21127631',
    '抢购礼包':                   '21127693, 21127694',
    '地铁（跑步-都市小游戏类）':    '21127659',
    '多条件连锁（投小游戏内容）':   '21127659',  # 地铁汇聚
    '节日卡包系统+礼包+新增兑换商店每日刷新': '21127803, 21127804',
    '异族大富翁':                 '21127704, 21127706, 21127707, 21127718',
    '普通大富翁':                 '21127614, 21127751',
    '赛车':                      '21127753, 21127754, 21127755, 21127756, 21127757, 21127758, 21127759',
    '巨猿':                      '21127578, 21127698',
}

# 读当前 checklist
params = json.dumps({'spreadsheetId': SHEET, 'range': f"'{TAB}'!A1:F50"})
r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
                   capture_output=True, text=True, encoding='utf-8')
rows = json.loads(r.stdout).get('values', [])
print(f"Current rows: {len(rows)}")

# 重建带 2112 列的数据：A=负责人, B=活动名, C=2112, D=是否已贴累充表, E=是否上单笔累充, F=链接
new_rows = []
for i, row in enumerate(rows):
    if i == 0:
        # 空行
        new_rows.append(['', '', '', '', '', ''])
        continue
    if i == 1:
        # 表头
        new_rows.append([row[0] if len(row)>0 else '',
                         row[1] if len(row)>1 else '',
                         '2112',
                         row[2] if len(row)>2 else '',
                         row[3] if len(row)>3 else '',
                         row[4] if len(row)>4 else ''])
        continue
    # 数据行
    name = row[1] if len(row) > 1 else ''
    id_val = ID_MAP.get(name, '')
    new_rows.append([
        row[0] if len(row)>0 else '',
        name,
        id_val,
        row[2] if len(row)>2 else '',
        row[3] if len(row)>3 else '',
        row[4] if len(row)>4 else '',
    ])

# 写回
range_str = f"'{TAB}'!A1:F{len(new_rows)}"
body = json.dumps({'range': range_str, 'majorDimension': 'ROWS', 'values': new_rows}, ensure_ascii=False)
params2 = json.dumps({'spreadsheetId': SHEET, 'range': range_str, 'valueInputOption': 'USER_ENTERED'})
r2 = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'update', '--params', params2, '--json', body],
                    capture_output=True, text=True, encoding='utf-8')
result = json.loads(r2.stdout) if r2.stdout else None
if result:
    print(f"OK cells={result.get('updatedCells')} range={result.get('updatedRange')}")
else:
    print(f"ERR: {r2.stderr[:300]}")
