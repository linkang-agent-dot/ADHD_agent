"""
修正：把 pay_total 填到 M（总付费额），N（投放内容）留空，O（节日时间）填节日
旧映射（错）: M=arppu, N=pay_total, O='', P=jieri
新映射（对）: M=pay_total, N='', O=jieri  (15列，去掉P)
数据行在 36-58（row34=科技节标题，row35=列头）
"""
import json, subprocess

GWS_CMD     = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET = "1ElKLw7zvz2-vjcgNkjpC54d6nW04lke_NWOPQs0Uq0Q"
SHEET       = "评分表（每月更新）"
DATA_START  = 36   # 数据实际从row36开始（34=节标题，35=列头）

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
        round(r['arpu'], 4),            # J  付费ARPU
        round(r['pay_rate'], 4),        # K  付费率
        round(r['chaor_pct'], 2),       # L  超R收入占比
        round(r['pay_total'], 2),       # M  总付费额 ← 修正为pay_total
        '',                             # N  投放内容（留空）
        jieri,                          # O  节日时间
    ]
    rows_data.append(row)

end_row = DATA_START + len(rows_data) - 1
range_str = f"'{SHEET}'!A{DATA_START}:O{end_row}"
params = json.dumps({"spreadsheetId": SPREADSHEET})
body = json.dumps({
    "valueInputOption": "USER_ENTERED",
    "data": [{"range": range_str, "majorDimension": "ROWS", "values": rows_data}]
}, ensure_ascii=False)

print(f"写入范围: {range_str}，共 {len(rows_data)} 行")
result = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'batchUpdate',
     '--params', params, '--json', body],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print("STDOUT:", result.stdout[:1500])
if result.stderr: print("STDERR:", result.stderr[:300])
print("RC:", result.returncode)
