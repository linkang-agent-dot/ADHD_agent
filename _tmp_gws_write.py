"""
直接用 gws API 写入：通过 subprocess 传入 inline JSON
"""
import json, subprocess, sys

SPREADSHEET = "1ElKLw7zvz2-vjcgNkjpC54d6nW04lke_NWOPQs0Uq0Q"
SHEET       = "评分表（每月更新）"

with open(r'C:\ADHD_agent\_tmp_rating_v4.json', encoding='utf-8') as f:
    data = json.load(f)

SHORT_NAME = {
    '科技节-挖孔小游戏':  ('挖孔小游戏',    '2026科技节'),
    '节日-大富翁':        ('大富翁',          '跨节日(复活节/节日通用)'),
    '科技节-通行证':      ('通行证',          '2026科技节'),
    '节日-行军外观':      ('行军外观',        '跨节日(科技节/复活节)'),
    '科技节-推币机':      ('推币机',          '2026科技节'),
    '节日-挖矿小游戏':    ('挖矿小游戏',      '跨节日(通用)'),
    '科技节-弹珠GACHA':   ('弹珠GACHA',       '2026科技节'),
    '万圣节-小连锁':      ('小连锁',          '2025万圣节'),
    '深海节-节日礼包团购':('节日礼包团购',    '2025深海节'),
    '科技节-集结奖励':    ('集结奖励',        '2026科技节'),
    '情人节-BP':          ('情人节BP',         '2026情人节'),
    '感恩节-每日补给':    ('每日补给',        '2025感恩节'),
    '复活节-强消耗':      ('强消耗',          '2026复活节'),
    '节日-累充':          ('累充',            '跨节日(周年庆/深海节)'),
    '节日-掉落转付费':    ('掉落转付费',      '跨节日(通用)'),
    '节日-对对碰':        ('对对碰',          '跨节日(通用)'),
    '周年庆-预购连锁':    ('预购连锁',        '2025周年庆'),
    '节日-限时抢购':      ('限时抢购',        '跨节日(通用)'),
    '情人节-bingo':       ('bingo',            '2026情人节'),
    '科技节-周卡':        ('科技节周卡',      '2026科技节'),
    '科技节-巨猿砸蛋锤':  ('巨猿砸蛋锤',      '2026科技节'),
    '节日-改造猴特权':    ('改造猴特权',      '跨节日(通用)'),
    '节日-装饰兑换券':    ('装饰兑换券',      '跨节日(通用)'),
}

rows_data = []
for r in data['results']:
    act = r['activity']
    short, jieri = SHORT_NAME.get(act, (act, '2026科技节'))
    row = [
        short, 1, r['origin'],
        r['total_score'], r['grade'],
        r['s_xianli'], r['s_zhuanhua'], r['s_jingyu'], r['s_fenceng'],
        round(r['arpu'], 4), round(r['pay_rate'], 4),
        round(r['chaor_pct'], 2), round(r['arppu'], 4),
        round(r['pay_total'], 2), '', jieri,
    ]
    rows_data.append(row)

# 使用 values.batchUpdate 通过 params + json
range_str = f"'{SHEET}'!A34:P56"

params = json.dumps({
    "spreadsheetId": SPREADSHEET
}, ensure_ascii=True)

body = json.dumps({
    "valueInputOption": "USER_ENTERED",
    "data": [
        {
            "range": range_str,
            "majorDimension": "ROWS",
            "values": rows_data
        }
    ]
}, ensure_ascii=False)

# 写到文件再传
with open(r'C:\ADHD_agent\_tmp_batchupd_params.json', 'w', encoding='ascii') as f:
    f.write(params)
with open(r'C:\ADHD_agent\_tmp_batchupd_body.json', 'w', encoding='utf-8') as f:
    f.write(body)

print(f"Params: {params}")
print(f"Body range: {range_str}, rows: {len(rows_data)}")

# 先尝试 batchUpdate（body 里有 spreadsheetId）
result = subprocess.run(
    'gws sheets spreadsheets values batchUpdate --params "@C:\\ADHD_agent\\_tmp_batchupd_params.json" --json "@C:\\ADHD_agent\\_tmp_batchupd_body.json"',
    shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print("STDOUT:", result.stdout[:2000])
print("STDERR:", result.stderr[:500])
print("RC:", result.returncode)
