import subprocess, json

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# Full data for 前期循环-甘特
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

params = json.dumps({
    'spreadsheetId': SPREADSHEET_ID,
    'range': '前期循环-甘特!A1',
    'valueInputOption': 'USER_ENTERED'
}, ensure_ascii=False)
body_str = json.dumps({'values': full_data}, ensure_ascii=False)

result = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update',
     '--params', params, '--json', body_str],
    capture_output=True
)

with open(r'C:\ADHD_agent\_tmp_full_out.txt', 'wb') as f:
    f.write(result.stdout)

stdout_utf8 = result.stdout.decode('utf-8', errors='replace')
print(f"rc={result.returncode} len={len(result.stdout)}")
print(f"stdout: {stdout_utf8[:300]}")

# Now do 7月
data_7 = [
    ['X2-7月烟火庆典 甘特图（10周，上下半分割）'],
    ['策略：①节日拉长至10周 ②上半主城皮肤(W1-5)+下半行军特效(W6-10)'],
    [],
    ['分类', '付费模块', '开发类型', '负责人', 'T级', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10', '备注'],
    ['时段说明', '上半：主城皮肤', '', '', '', 'Y','Y','Y','Y','Y','', '', '', '', '', ''],
    ['时段说明', '下半：行军特效', '', '', '', '','','','','','Y','Y','Y','Y','Y', ''],
    ['节日付费', '累充+排行榜+乐透', '复用', 'liusiyi', '', 'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y', '全程10周'],
    ['节日BP', '长BP+集结礼包', '换皮', 'sunminghao', '', 'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y', '全程10周'],
    ['强消耗', '强消耗扭蛋机', '复用', 'sunminghao', '', '','','','','','Y','Y','Y','Y','Y', '仅下半W6-10'],
    ['进度小游戏', '普通大富翁', '换皮', 'gongliang', '', 'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y', '全程10周'],
    ['活跃类', '掉落转付费', '复用', 'linkang', '', 'Y','Y','Y','Y','Y','?','?','?','?','?', '上半段确认'],
    ['', '7日', '复用', 'liusiyi', '', 'Y','Y','Y','Y','Y','Y','Y','?','?','?', '前7周待补'],
    ['大地图', '巨猿', '复用', 'liusiyi', '', 'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y', '全程10周'],
    ['礼包类', '周卡', '复用', 'sunminghao', 'D', '','','','Y','Y','Y','Y','Y','Y','Y', 'W4起'],
    ['', '抢购礼包', '复用', 'gongliang', 'B', '','','','','Y','','','','','Y', 'W5/W10 隔5周'],
    ['', '团购礼包 [7月新增]', '搬运', 'sunminghao', 'D', 'Y','Y','Y','Y','Y','?','?','?','?','?', '上半段(小中R)'],
    ['', '小额转盘 [7月新增]', '搬运', 'linkang', 'C', '','','','','','Y','Y','Y','Y','Y', '下半段(小中R)'],
    ['行军表情', '行军表情', '复用', 'liusiyi', 'D', 'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y', '全程10周'],
    ['联动礼包', '联动礼包-柜台', '换皮', 'liusiyi', '', 'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y', '全程10周'],
    ['节日卡包', '节日卡包系统', '换皮', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y', '全程10周'],
    ['随机玩法', '付费率宝箱', '复用', 'linkang', '', 'Y','Y','Y','Y','Y','?','?','?','?','?', '上半段'],
    ['行军特效投放', '挖孔小游戏 [7月新增]', '搬运', 'liusiyi', 'S', '','','','','','Y','Y','Y','Y','Y', '仅下半 | S级! 重点保障'],
    [],
    ['亮点：挖孔小游戏是全部模块中唯一S级，专攻大R/超R'],
    [],
    ['R级', '新增模块', '时段'],
    ['小R', '团购礼包', '上半'],
    ['中R', '团购礼包+小额转盘', '上半+下半'],
    ['大R', '挖孔小游戏', '下半'],
    ['超R', '挖孔小游戏+行军特效', '下半'],
    [],
    ['Y=活跃  空白=未启动  ?=待确认'],
]

params2 = json.dumps({
    'spreadsheetId': SPREADSHEET_ID,
    'range': '7月烟火庆典-甘特!A1',
    'valueInputOption': 'USER_ENTERED'
}, ensure_ascii=False)
body2 = json.dumps({'values': data_7}, ensure_ascii=False)

result2 = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update',
     '--params', params2, '--json', body2],
    capture_output=True
)

with open(r'C:\ADHD_agent\_tmp_7_out.txt', 'wb') as f:
    f.write(result2.stdout)

stdout2 = result2.stdout.decode('utf-8', errors='replace')
print(f"7月 rc={result2.returncode} len={len(result2.stdout)}")
print(f"stdout2: {stdout2[:300]}")
