import subprocess, json, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

def gws_call(subcommand, params=None, body=None):
    cmd = [GWS_CMD] + subcommand.split()
    if params:
        cmd += ['--params', json.dumps(params, ensure_ascii=False)]
    if body:
        cmd += ['--json', json.dumps(body, ensure_ascii=False)]
    result = subprocess.run(cmd, capture_output=True)
    stdout = result.stdout.decode('utf-8', errors='replace')
    try:
        return json.loads(stdout)
    except:
        return {'_raw': stdout[:200]}

def write_batch(data_map):
    """Use batchUpdate to write multiple ranges at once"""
    value_ranges = []
    for sheet_name, values in data_map.items():
        value_ranges.append({
            'range': f'{sheet_name}!A1',
            'majorDimension': 'ROWS',
            'values': values
        })
    
    params = {
        'spreadsheetId': SPREADSHEET_ID,
        'valueInputOption': 'USER_ENTERED'
    }
    body = {'valueInputOption': 'USER_ENTERED', 'data': value_ranges}
    result = gws_call('sheets spreadsheets values batchUpdate', params=params, body=body)
    return result

# ============= GANTT DATA =============

sheets_data = {
    '前期循环-甘特': [
        ['X2节日-第一期循环（前35天）甘特图'],
        ['策略：不改变X2基本节日循环，新增已验证P2形式，预期新增ARPC +7.8'],
        [],
        ['分类', '付费模块', '开发类型', '负责人', '活动ID', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', '备注'],
        ['累充', '累充', '复用', 'liusiyi', '211201012', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
        ['主城GACHA', 'GACHA+累计活动', '复用', 'gongliang->linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
        ['', '每日GACHA礼包', '新增★', 'gongliang->linkang', '', '','','Y','Y','Y','Y','Y', '第3周起 | P2-ARPC:0.6'],
        ['行军皮肤', '节日BP', '复用', 'minghao', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
        ['强消耗活动', '强消耗扭蛋', '复用', 'minghao', '', '','','Y','Y','Y','Y','Y', '第3周起'],
        ['装饰', '大富翁-节日装饰', '新增★', 'gongliang->minghao', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周 | P2-ARPC:3.2'],
        ['活跃类', '掉落转付费', '新增★', 'linkang', '', 'Y','Y','Y','?','?','?','?', '前3周待确认 | P2-ARPC:0.5'],
        ['', '7日', '复用', 'liusiyi', '211201011', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
        ['中小R付费', '周卡', '搬运', 'minghao', '211201010', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
        ['礼包付费', '抢购礼包-养成投放', '新增★', 'gongliang->liusiyi', '21127223', '','','A','','','A','?', '隔周(W3/W6) | P2-ARPC:3.5'],
        ['节日卡包', '节日卡包', '借用圣诞', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程7周'],
        [],
        ['Y=活跃  空白=未启动  A=交替投放  ?=待确认'],
    ],
    '6月拓荒节-甘特': [
        ['X2-6月拓荒节 甘特图'],
        ['策略：①联动礼包强化shop外显 ②付费率宝箱提付费率 ③多条件连锁深化中R | 警告:linkang独揽全部19模块'],
        [],
        ['分类', '付费模块', '开发类型', '负责人', 'T级', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', '备注'],
        ['节日付费', '累充+排行榜+乐透', '新开发', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['抽奖类', '外圈内圈抽奖(周年换皮)', '换皮', 'linkang', 'A', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['', 'GACHA每日礼包', '换皮', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['节日BP', '长BP+集结礼包', '换皮', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['强消耗', '强消耗扭蛋机', '复用', 'linkang', '', '','','Y','Y','Y','Y','Y', '第3周起'],
        ['进度小游戏', '普通大富翁', '换皮', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['活跃类', '掉落转付费', '复用', 'linkang', '', 'Y','Y','Y','?','?','?','?', '前3周'],
        ['', '7日', '复用', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['大地图', '巨猿', '复用', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['礼包类', '周卡', '复用', 'linkang', 'D', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['', '抢购礼包', '复用', 'linkang', 'B', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['', '多条件连锁 [6月新增]', '搬运', 'linkang', 'C', '','','Y','Y','Y','Y','Y', '第3周起'],
        ['行军表情', '行军表情', '复用', 'linkang', 'D', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['联动礼包', '联动礼包-墙纸 [6月新增]', '搬运+开发', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程-shop外显'],
        ['', '联动礼包-墙壁 [6月新增]', '搬运', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程-shop外显'],
        ['', '联动礼包-柜台 [6月新增]', '搬运', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程-shop外显'],
        ['节日卡包', '节日卡包系统', '换皮', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['随机玩法', '付费率宝箱 [6月新增]', '搬运', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['节日挖矿', '节日挖矿 [6月新增]', '搬运', 'linkang', '', 'Y','Y','Y','Y','Y','Y','Y', '全程'],
        ['[风险]', 'linkang 独揽以上全部19模块，建议至少分出3-4个', '', '', '', '', '', '', '', '', '', '', '高优先级风险'],
        [],
        ['Y=活跃  空白=未启动  ?=待确认'],
    ],
    '7月烟火庆典-甘特': [
        ['X2-7月烟火庆典 甘特图（10周，上下半分割）'],
        ['策略：①节日拉长至10周 ②上半[主城皮肤W1-5]+下半[行军特效W6-10] ③团购/转盘补小中R ④挖孔小游戏(S)攻大超R'],
        [],
        ['分类', '付费模块', '开发类型', '负责人', 'T级', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10', '备注'],
        ['', '←上半[主城皮肤]→', '', '', '', 'Y','Y','Y','Y','Y','', '', '', '', '', ''],
        ['', '←下半[行军特效]→', '', '', '', '', '', '', '', '','Y','Y','Y','Y','Y', ''],
        ['节日付费', '累充+排行榜+乐透', '复用', 'liusiyi', '', 'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y', '全程10周'],
        ['节日BP', '长BP+集结礼包', '换皮', 'sunminghao', '', 'Y','Y','Y','Y','Y','Y','Y','Y','Y','Y', '全程10周'],
        ['强消耗', '强消耗扭蛋机', '复用', 'sunminghao', '', '','','','','','Y','Y','Y','Y','Y', '仅下半[W6-10]'],
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
        ['[亮点]', '挖孔小游戏=唯一S级，专攻大R/超R', 'S', '', '', '', '', '', '', '', '', '', '', '', '', ''],
        [],
        ['Y=活跃  空白=未启动  ?=待确认'],
    ],
}

# Write all sheets in a single batchUpdate call
result = write_batch(sheets_data)
print(f"batchUpdate result: {json.dumps(result, ensure_ascii=False)[:500]}")

if 'responses' in result or 'totalUpdatedRows' in result:
    print("SUCCESS")
    for r in result.get('responses', []):
        print(f"  {r.get('updatedRange','?')}: {r.get('updatedRows','?')} rows")
else:
    print("Checking result keys:", list(result.keys()))
