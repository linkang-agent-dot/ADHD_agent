"""
把 _tmp_rating_v4.json 的 23 个活动写入 Google Sheet 评分表
gws sheets spreadsheets.values.update
"""
import json, subprocess, sys

SPREADSHEET = "1ElKLw7zvz2-vjcgNkjpC54d6nW04lke_NWOPQs0Uq0Q"
SHEET       = "评分表（每月更新）"
START_ROW   = 34

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
        short,                          # A
        1,                              # B
        r['origin'],                    # C
        r['total_score'],               # D
        r['grade'],                     # E
        r['s_xianli'],                  # F
        r['s_zhuanhua'],                # G
        r['s_jingyu'],                  # H
        r['s_fenceng'],                 # I
        round(r['arpu'], 4),            # J ARPU
        round(r['pay_rate'], 4),        # K 付费率
        round(r['chaor_pct'], 2),       # L 超R收入占比
        round(r['arppu'], 4),           # M ARPPU
        round(r['pay_total'], 2),       # N 总付费额
        '',                             # O 投放内容
        jieri,                          # P 节日时间
    ]
    rows_data.append(row)

end_row = START_ROW + len(rows_data) - 1
range_str = f"'{SHEET}'!A{START_ROW}:P{end_row}"

payload = {
    "majorDimension": "ROWS",
    "values": rows_data
}

print(f"写入范围: {range_str}  共 {len(rows_data)} 行")
payload_str = json.dumps(payload, ensure_ascii=False)

# 写 payload 到临时文件
with open(r'C:\ADHD_agent\_tmp_payload_v4.json', 'w', encoding='utf-8') as pf:
    pf.write(payload_str)

# --params 是 URL query 参数（spreadsheetId, range, valueInputOption 均为 URL path/query）
params = json.dumps({
    "spreadsheetId": SPREADSHEET,
    "range": range_str,
    "valueInputOption": "USER_ENTERED"
}, ensure_ascii=False)

cmd2 = f'gws sheets spreadsheets values update --params "{params.replace(chr(34), chr(39))}" --json @C:\\ADHD_agent\\_tmp_payload_v4.json'
# 更安全：分开传
params_file = r'C:\ADHD_agent\_tmp_params_v4.json'
with open(params_file, 'w', encoding='utf-8') as pf2:
    pf2.write(params)

cmd3 = f'gws sheets spreadsheets values update --params @{params_file} --json @C:\\ADHD_agent\\_tmp_payload_v4.json'
result = subprocess.run(cmd3, shell=True, capture_output=True, text=True,
                        encoding='utf-8', errors='replace')

print("STDOUT:", result.stdout[:3000])
if result.stderr:
    print("STDERR:", result.stderr[:500])
print("Return code:", result.returncode)
