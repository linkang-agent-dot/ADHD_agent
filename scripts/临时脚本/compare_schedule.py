import json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

with open('C:/Users/linkang/igame_s5_full.json', encoding='utf-8') as f:
    s5 = json.load(f)
with open('C:/Users/linkang/igame_s2_full.json', encoding='utf-8') as f:
    s2 = json.load(f)

igame = {}
for item in s5['data'] + s2['data']:
    aid = item['activityConfigId']
    st = item.get('startTime', 0)
    et = item.get('endTime', 0)
    if st:
        dt = datetime.datetime.fromtimestamp(st/1000)
        sd = f'{dt.month}-{dt.day}'
    else:
        sd = 'N/A'
    if et:
        dt = datetime.datetime.fromtimestamp(et/1000)
        ed = f'{dt.month}-{dt.day}'
    else:
        ed = 'N/A'
    igame[aid] = {'name': item['name'], 'start': sd, 'end': ed, 'start_ts': st, 'end_ts': et, 'status': item['status']}

# Sheet gantt schedule (from cell colors)
sheet_schedule = {
    '21115733': ('3-12','4-2'),
    '21115731': ('3-12','4-2'),
    '21115732': ('3-12','4-2'),
    '21115740': ('3-12','4-2'),
    '21115728': ('3-13','3-22'),
    '21115726': ('3-12','3-18'),
    '21115675': (None, None),
    '21115729': ('3-16','3-22'),
    '21115696': ('3-23','4-2'),
    '21115376': ('3-23','4-2'),
    '21115746': ('3-12','4-2'),
    '21115398': ('3-12','4-2'),
    '21115399': ('3-25','3-29'),
    '21115526': ('3-12','4-2'),
    '21115527': ('3-13','3-17'),
    '21115747': ('3-12','4-2'),
    '21115745': ('3-19','4-2'),
    '21115358': ('3-13','3-25'),
    '21115359': ('3-13','3-25'),
    '21115360': ('3-13','3-25'),
    '21115730': ('3-13','3-25'),
    '21115735': ('3-27','4-2'),
    '21115594': ('3-12','4-1'),
    '21115472': ('3-18','3-22'),
    '21115380': ('3-27','4-2'),
    '21115037': ('3-13','3-19'),
    '21115632': ('3-25','3-31'),
    '21115633': ('3-25','3-31'),
    '21115739': ('3-12','4-1'),
    '21115738': ('3-12','4-1'),
    '21115736': ('3-12','4-1'),
    '21115559': ('3-12','4-1'),
    '21115560': ('3-12','4-1'),
    '21115571': ('3-12','4-1'),
    '21115741': ('3-16','3-30'),
    '21115742': ('3-16','3-30'),
    '21115607': ('3-19','3-25'),
    '21115479': ('3-26','3-30'),
    '21115312': ('3-26','3-30'),
    '21115313': ('3-26','3-30'),
    '21115734': ('3-30','4-1'),
    '21115737': ('3-12','4-1'),
    '21115743': ('3-12','4-1'),
    '21115744': ('3-28','4-1'),
    '21115727': ('3-26','3-29'),
}

activities = [
    ('主城特效累充bingo','21115733','TRUE'),
    ('主城特效累充-联盟版','21115731','TRUE'),
    ('主城特效累充-服务器版','21115732','TRUE'),
    ('手札','21115740','TRUE'),
    ('弹珠主体GACHA(不灰度)','21115728','FALSE'),
    ('机甲累充','21115726','TRUE'),
    ('单笔充值-帮派版本(不灰度)','21115675','FALSE'),
    ('每日弹珠礼包(不灰度)','21115729','FALSE'),
    ('推币机(不灰度)','21115696','FALSE'),
    ('推币机-单笔累充(不灰度)','21115376','FALSE'),
    ('长节日BP(不灰度)','21115746','FALSE'),
    ('节日通用-强消耗-s3-5','21115398','FALSE'),
    ('节日通用-强消耗-s6','21115399','TRUE'),
    ('对对碰s3-5','21115526','FALSE'),
    ('对对碰s6','21115527','TRUE'),
    ('大富翁-节日装饰','21115747','TRUE'),
    ('大富翁-组队子活动','21115745','TRUE'),
    ('合成小游戏-s3','21115358','FALSE'),
    ('合成小游戏-s4','21115359','FALSE'),
    ('合成小游戏-s5','21115360','TRUE'),
    ('挖矿累积任务','21115730','TRUE'),
    ('节日挖孔小游戏(不灰度)','21115735','FALSE'),
    ('多条件连锁','21115594','TRUE'),
    ('掉落转付费','21115472','TRUE'),
    ('7日(不灰)','21115380','FALSE'),
    ('bingo','21115037','TRUE'),
    ('周卡_s3-5','21115632','FALSE'),
    ('周卡_s6','21115633','TRUE'),
    ('联动礼包-行军表情特效','21115739','TRUE'),
    ('行军特效-付费率','21115738','TRUE'),
    ('行军表情-付费率','21115736','TRUE'),
    ('预购连锁礼包_s3-5(不灰)','21115559','FALSE'),
    ('预购连锁礼包_s6(不灰)','21115560','FALSE'),
    ('装饰兑换商店-通用','21115571','TRUE'),
    ('限时抢购-S6(不灰)','21115741','FALSE'),
    ('限时抢购-S3-5(不灰)','21115742','FALSE'),
    ('挂机BP','21115607','TRUE'),
    ('团购礼包','21115479','FALSE'),
    ('订阅卡累充-s3','21115312','FALSE'),
    ('订阅卡累充-s4-6','21115313','FALSE'),
    ('巨猿','21115734','TRUE'),
    ('签到','21115737','FALSE'),
    ('科技节日卡包BP','21115743','TRUE'),
    ('科技节-三合一礼包','21115744','TRUE'),
    ('异种蛮猴-节日版','21115727','FALSE'),
]

lines = []
lines.append('=' * 95)
lines.append('  2026科技节灰度 排期对比: 甘特图 vs iGame实际配置')
lines.append('=' * 95)
lines.append('')

mismatch = []
match_ok = []
no_schedule = []
not_in_igame = []

for name, aid, grey in activities:
    sheet_s, sheet_e = sheet_schedule.get(aid, (None, None))
    ig = igame.get(aid)

    if not ig:
        not_in_igame.append((name, aid, sheet_s, sheet_e))
        continue

    ig_s = ig['start']
    ig_e_raw = ig['end']

    # iGame endTime 08:00 means activity ends at that moment
    # So last active day = endTime - 1 day
    try:
        parts = ig_e_raw.split('-')
        m = int(parts[0])
        d = int(parts[1])
        dt = datetime.datetime(2026, m, d) - datetime.timedelta(days=1)
        ig_e_inclusive = f'{dt.month}-{dt.day}'
    except:
        ig_e_inclusive = ig_e_raw

    if sheet_s is None:
        no_schedule.append((name, aid, ig_s, ig_e_inclusive, grey))
        continue

    start_ok = (ig_s == sheet_s)
    end_ok = (ig_e_inclusive == sheet_e)

    if start_ok and end_ok:
        match_ok.append((name, aid, sheet_s, sheet_e))
    else:
        diff_parts = []
        if not start_ok:
            diff_parts.append(f'开始: 甘特{sheet_s} vs iGame{ig_s}')
        if not end_ok:
            diff_parts.append(f'结束: 甘特{sheet_e} vs iGame{ig_e_inclusive}')
        mismatch.append((name, aid, sheet_s, sheet_e, ig_s, ig_e_inclusive, grey, ' | '.join(diff_parts)))

lines.append(f'排期不一致: {len(mismatch)} 条')
lines.append(f'排期一致: {len(match_ok)} 条')
lines.append(f'甘特图无色块: {len(no_schedule)} 条')
lines.append(f'iGame中未找到: {len(not_in_igame)} 条')
lines.append('')

if mismatch:
    lines.append('-' * 95)
    lines.append('【排期不一致的活动】')
    lines.append('-' * 95)
    for name, aid, ss, se, igs, ige, grey, diff in mismatch:
        lines.append(f'  {aid}  {name}  (灰度={grey})')
        lines.append(f'    甘特图: {ss} ~ {se}')
        lines.append(f'    iGame:  {igs} ~ {ige}')
        lines.append(f'    差异:   {diff}')
        lines.append('')

if match_ok:
    lines.append('-' * 95)
    lines.append('【排期一致的活动】')
    lines.append('-' * 95)
    for name, aid, ss, se in match_ok:
        lines.append(f'  [OK] {aid}  {name}  {ss}~{se}')

if no_schedule:
    lines.append('')
    lines.append('-' * 95)
    lines.append('【甘特图无色块 (iGame有配置)】')
    lines.append('-' * 95)
    for name, aid, igs, ige, grey in no_schedule:
        lines.append(f'  {aid}  {name}  iGame: {igs}~{ige}  (灰度={grey})')

if not_in_igame:
    lines.append('')
    lines.append('-' * 95)
    lines.append('【iGame中未找到】')
    lines.append('-' * 95)
    for name, aid, ss, se in not_in_igame:
        sched = f'{ss}~{se}' if ss else '无排期'
        lines.append(f'  {aid}  {name}  甘特图: {sched}')

with open('C:/Users/linkang/schedule_compare.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Report saved.')
