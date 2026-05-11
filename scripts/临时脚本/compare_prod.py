import json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

# 1. Parse production sheet gantt colors
with open('C:/Users/linkang/sheet_prod_colors.json', encoding='utf-8') as f:
    color_data = json.load(f)

dates = ['3-12','3-13','3-14','3-15','3-16','3-17','3-18','3-19','3-20','3-21','3-22','3-23','3-24','3-25','3-26','3-27','3-28','3-29','3-30','3-31','4-1','4-2']

# Row 0 in color data = sheet row 7 (first activity: 主城特效累充bingo)
prod_activities = [
    ('主城特效累充bingo','21115733','liusiyi','TRUE'),
    ('主城特效累充-联盟版','21115731','liusiyi','TRUE'),
    ('主城特效累充-服务器版','21115732','liusiyi','TRUE'),
    ('手札','21115740','linkang','TRUE'),
    ('弹珠主体GACHA+累计活动','21115728','linkang','TRUE'),
    ('机甲累充','21115726','linkang','TRUE'),
    ('单笔充值-帮派版本(正式服ID)','21117563','linkang','TRUE'),
    ('每日弹珠礼包','21115729','linkang','TRUE'),
    ('推币机','21115696','linkang','TRUE'),
    ('推币机-单笔累充','21115376','linkang','TRUE'),
    ('长节日BP','21115746','minghao','TRUE'),
    ('节日通用-强消耗-s3-5','21115398','minghao','TRUE'),
    ('节日通用-强消耗-s6','21115399','minghao','TRUE'),
    ('对对碰s3-5','21115526','minghao','TRUE'),
    ('对对碰s6','21115527','minghao','TRUE'),
    ('大富翁-节日装饰','21115747','minghao','TRUE'),
    ('大富翁-组队子活动','21115745','minghao','TRUE'),
    ('合成小游戏-s3','21115358','linkang','TRUE'),
    ('合成小游戏-s4','21115359','linkang','TRUE'),
    ('合成小游戏-s5','21115360','linkang','TRUE'),
    ('挖矿累积任务','21115730','linkang','TRUE'),
    ('节日挖孔小游戏','21115735','liusiyi','TRUE'),
    ('多条件连锁','21115594','linkang','TRUE'),
    ('掉落转付费','21115472','liusiyi','TRUE'),
    ('7日','21115380','liusiyi','TRUE'),
    ('bingo','21115037','liusiyi','TRUE'),
    ('周卡_s3-5','21115632','minghao','TRUE'),
    ('周卡_s6','21115633','minghao','TRUE'),
    ('联动礼包-行军表情特效','21115739','liusiyi','TRUE'),
    ('行军特效-付费率','21115738','liusiyi','TRUE'),
    ('行军表情-付费率','21115736','liusiyi','TRUE'),
    ('预购连锁礼包_s3-5','21115559','linkang','TRUE'),
    ('预购连锁礼包_s6','21115560','linkang','TRUE'),
    ('装饰兑换商店-通用','21115571','linkang','TRUE'),
    ('限时抢购-S6-通用皮(1,2期)','21115741','linkang','FALSE'),
    ('限时抢购-S3-5-通用皮(3期)','21115742','linkang','FALSE'),
    ('挂机BP','21115607','liusiyi','TRUE'),
    ('团购礼包','21115479','minghao','FALSE'),
    ('订阅卡累充-s3','21115312','linkang','FALSE'),
    ('订阅卡累充-s4-6','21115313','linkang','FALSE'),
    ('巨猿','21115734','liusiyi','TRUE'),
    ('签到','21115737','liusiyi','TRUE'),
    ('科技节日卡包BP','21115743','linkang','TRUE'),
    ('科技节-三合一礼包','21115744','linkang','FALSE'),
    ('异种蛮猴-节日版','21115727','linkang','FALSE'),
]

rows_data = color_data['sheets'][0]['data'][0]['rowData']
sheet_schedule = {}
for i, (name, aid, owner, online) in enumerate(prod_activities):
    if i >= len(rows_data):
        sheet_schedule[aid] = (None, None)
        continue
    row = rows_data[i]
    cells = row.get('values', [])
    colored_dates = []
    for j in range(min(len(cells), len(dates))):
        cell = cells[j]
        bg = cell.get('effectiveFormat', {}).get('backgroundColor', {})
        r = bg.get('red', 1.0)
        g = bg.get('green', 1.0)
        b = bg.get('blue', 1.0)
        if not (r > 0.95 and g > 0.95 and b > 0.95):
            colored_dates.append(dates[j])
    if colored_dates:
        sheet_schedule[aid] = (colored_dates[0], colored_dates[-1])
    else:
        sheet_schedule[aid] = (None, None)

# 2. Parse iGame data
with open('C:/Users/linkang/igame_s5_new.json', encoding='utf-8') as f:
    s5 = json.load(f)
with open('C:/Users/linkang/igame_s2_new.json', encoding='utf-8') as f:
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
    igame[aid] = {
        'name': item['name'],
        'start': sd,
        'end': ed,
        'start_ts': st,
        'end_ts': et,
        'status': item['status'],
    }

# 3. Compare
lines = []
lines.append('=' * 95)
lines.append('  2026科技节【正式服】排期对比: 甘特图 vs iGame')
lines.append('=' * 95)

sheet_online = [(n,a,o,ol) for n,a,o,ol in prod_activities if ol == 'TRUE']
sheet_offline = [(n,a,o,ol) for n,a,o,ol in prod_activities if ol == 'FALSE']

lines.append(f'')
lines.append(f'排期表总活动: {len(prod_activities)} 条 (上线={len(sheet_online)}, 未上线={len(sheet_offline)})')

# Filter iGame to only 21115/21117 prefix
igame_tech = {k:v for k,v in igame.items() if k.startswith('21115') or k.startswith('21117')}
lines.append(f'iGame科技节活动: {len(igame_tech)} 条')
lines.append('')

mismatch = []
match_ok = []
not_in_igame = []
no_schedule = []

for name, aid, owner, online in prod_activities:
    ss, se = sheet_schedule.get(aid, (None, None))
    ig = igame.get(aid)

    if not ig:
        not_in_igame.append((name, aid, owner, online, ss, se))
        continue

    ig_s = ig['start']
    ig_e_raw = ig['end']

    # iGame endTime is exclusive, subtract 1 day for inclusive end
    try:
        parts = ig_e_raw.split('-')
        m = int(parts[0])
        d = int(parts[1])
        dt = datetime.datetime(2026, m, d) - datetime.timedelta(days=1)
        ig_e = f'{dt.month}-{dt.day}'
    except:
        ig_e = ig_e_raw

    if ss is None:
        no_schedule.append((name, aid, owner, online, ig_s, ig_e))
        continue

    start_ok = (ig_s == ss)
    end_ok = (ig_e == se)

    if start_ok and end_ok:
        match_ok.append((name, aid, ss, se, online))
    else:
        diff = []
        if not start_ok:
            diff.append(f'开始: 甘特{ss} vs iGame{ig_s}')
        if not end_ok:
            diff.append(f'结束: 甘特{se} vs iGame{ig_e}')
        mismatch.append((name, aid, ss, se, ig_s, ig_e, online, ' | '.join(diff)))

lines.append(f'排期一致: {len(match_ok)} 条')
lines.append(f'排期不一致: {len(mismatch)} 条')
lines.append(f'甘特图无色块: {len(no_schedule)} 条')
lines.append(f'iGame中未找到: {len(not_in_igame)} 条')

if match_ok:
    lines.append('')
    lines.append('-' * 95)
    lines.append('[排期一致]')
    lines.append('-' * 95)
    for name, aid, ss, se, online in match_ok:
        lines.append(f'  [OK] {aid}  {name}  {ss}~{se}  上线={online}')

if mismatch:
    lines.append('')
    lines.append('-' * 95)
    lines.append('[排期不一致]')
    lines.append('-' * 95)
    for name, aid, ss, se, igs, ige, online, diff in mismatch:
        lines.append(f'  {aid}  {name}  上线={online}')
        lines.append(f'    甘特图: {ss} ~ {se}')
        lines.append(f'    iGame:  {igs} ~ {ige}')
        lines.append(f'    差异:   {diff}')
        lines.append('')

if not_in_igame:
    lines.append('')
    lines.append('-' * 95)
    lines.append('[iGame中未找到]')
    lines.append('-' * 95)
    for name, aid, owner, online, ss, se in not_in_igame:
        sched = f'{ss}~{se}' if ss else '无排期'
        lines.append(f'  {aid}  {name}  负责人:{owner}  上线={online}  甘特图:{sched}')

if no_schedule:
    lines.append('')
    lines.append('-' * 95)
    lines.append('[甘特图无色块但iGame有配置]')
    lines.append('-' * 95)
    for name, aid, owner, online, igs, ige in no_schedule:
        lines.append(f'  {aid}  {name}  iGame:{igs}~{ige}  上线={online}')

# 4. Check iGame activities not in sheet
sheet_ids = set(a[1] for a in prod_activities)
lines.append('')
lines.append('-' * 95)
lines.append('[iGame中有但排期表中没有的科技节活动]')
lines.append('-' * 95)
ec = 0
for aid, info in sorted(igame_tech.items()):
    if aid not in sheet_ids:
        sl = '等待部署' if info['status'] == 5 else '已提交待审' if info['status'] == 2 else f"s{info['status']}"
        lines.append(f'  {aid}  {info["name"]}  [{sl}]  {info["start"]}~{info["end"]}')
        ec += 1
if ec == 0:
    lines.append('  无')

with open('C:/Users/linkang/prod_compare.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('done')
