#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比排期审核表和正式上线表的时间安排 - 修正版
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

output_lines = []
def log(msg=""):
    output_lines.append(str(msg))

# ============ 1. 读取排期审核表 ============
xlsx_path = r"c:\Users\linkang\Desktop\节日排期表\实际排期审核.xlsx"
df = pd.read_excel(xlsx_path, engine='openpyxl', header=None)

log("=" * 120)
log("【排期审核表日期列解析】")
log()

# 表头结构:
# 行0: 列名 (节日活动名, 活动上线负责人, ...)
# 行1: 日编号 (1,2,3,...22) -> 从列11开始
# 行2: 星期几 (周二,周三,...) -> 从列11开始  
# 行3: Excel日期序列号 (46063,46064,...) -> 从列11开始
# 行4+: 活动数据

# 解析日期列 - 使用行3的Excel序列号
date_map = {}  # col_idx -> datetime
for col_idx in range(11, min(34, len(df.columns))):
    day_num = df.iloc[1, col_idx]      # 日编号 (1-22)
    weekday = df.iloc[2, col_idx]      # 星期几
    serial_val = df.iloc[3, col_idx]   # Excel日期序列号
    
    actual_date = None
    if pd.notna(serial_val):
        try:
            serial = int(float(serial_val))
            actual_date = datetime(1899, 12, 30) + timedelta(days=serial)
        except:
            pass
    
    date_map[col_idx] = actual_date
    date_str = actual_date.strftime('%Y.%m.%d(%a)') if actual_date else 'N/A'
    log(f"  列{col_idx}: 第{day_num}天, {weekday}, 日期={date_str}")

log()

# ============ 2. 提取每个活动的排期 ============
log("=" * 120)
log("【每个活动的排期时间提取（从第4行开始）】")
log()

xlsx_schedule = {}
for row_idx in range(4, len(df)):
    activity_name = df.iloc[row_idx, 0]
    if pd.isna(activity_name) or str(activity_name).strip() == '':
        continue
    activity_name = str(activity_name).strip()
    person = str(df.iloc[row_idx, 1]).strip() if pd.notna(df.iloc[row_idx, 1]) else ''
    
    # 收集所有有标记的日期列
    active_dates = []
    mark_details = []
    for col_idx in range(11, min(34, len(df.columns))):
        val = df.iloc[row_idx, col_idx]
        if pd.notna(val) and str(val).strip() != '':
            dt = date_map.get(col_idx)
            val_str = str(val).strip()
            # 排除纯False/0的情况（可能是check列的残留）
            if val_str in ['False', '0', '0.0']:
                continue
            if dt:
                active_dates.append(dt)
                mark_details.append(f"{dt.strftime('%m.%d')}({val_str})")
            else:
                mark_details.append(f"col{col_idx}({val_str})")
    
    if active_dates:
        sched_start = min(active_dates)
        sched_end = max(active_dates)
        # 活动通常覆盖标记日期的整天，所以结束日是最后标记日的次日0点
        start_str = sched_start.strftime('%Y.%m.%d')
        end_str = sched_end.strftime('%Y.%m.%d')
    else:
        sched_start = None
        sched_end = None
        start_str = '无时间标记'
        end_str = '无时间标记'
    
    log(f"  {activity_name} (负责人:{person})")
    log(f"    覆盖日期范围: {start_str} ~ {end_str}")
    if mark_details:
        log(f"    各日期标记: {', '.join(mark_details)}")
    log()
    
    xlsx_schedule[activity_name] = {
        'person': person,
        'start': sched_start,
        'end': sched_end,
        'start_str': start_str,
        'end_str': end_str,
        'active_dates': active_dates,
        'mark_details': mark_details
    }

# ============ 3. 读取正式上线表 ============
csv_path = r"c:\Users\linkang\Desktop\节日排期表\情人节正式上线.csv"
df_csv = pd.read_csv(csv_path, encoding='gbk')
csv_cols = list(df_csv.columns)

csv_activities = {}
for idx, row in df_csv.iterrows():
    act_id = str(row[csv_cols[0]]).strip().replace('\t', '')
    act_name = str(row[csv_cols[1]]).strip().replace('\t', '')
    start_time = str(row[csv_cols[5]]).strip().replace('\t', '')
    end_time = str(row[csv_cols[6]]).strip().replace('\t', '')
    duration = str(row[csv_cols[7]]).strip().replace('\t', '')
    
    if act_name not in csv_activities:
        csv_activities[act_name] = []
    csv_activities[act_name].append({
        'id': act_id,
        'start': start_time,
        'end': end_time,
        'duration': duration
    })

def parse_date(s):
    s = s.strip()
    for fmt in ['%Y.%m.%d %H:%M:%S', '%Y.%m.%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
        try:
            return datetime.strptime(s, fmt)
        except:
            continue
    return None

# ============ 4. 建立映射并对比时间 ============
log("=" * 120)
log("【排期时间 vs 上线时间 逐项对比】")
log()

mapping = {
    '主城特效累充': ['情人节2026-主城特效累充-个人'],
    '主城特效累充-服务器版（不灰）': ['情人节2026-主城特效累充-服务器'],
    '节日预购礼包': ['通用-情人节预购连锁礼包_schema6', '通用-情人节预购连锁礼包_schema3-5'],
    'GACHA+配套充值+累计活动（不灰）': ['26新组件gacha-云上探宝'],
    'GACHA每日小额礼包（不灰）': ['新组件gacha-云上探宝-每日礼包'],
    '单笔充值（不灰）': ['26情人节-单笔充值-第一轮', '26情人节-单笔充值-第二轮'],
    '机甲累充（不灰）': ['26情人节-机甲累充'],
    '联动礼包+行军表情': ['联动礼包-2026情人节', '2026情人节-行军特效礼包', '情人节2026-行军表情礼包'],
    '长节日BP（无排行榜，不灰度，有全服进度）': ['情人节2026-横版bp（循环宝箱版）'],
    '强消耗扭蛋': ['情人节2026-强消耗-schema6', '情人节2026-强消耗-schema3-5'],
    '强消耗对对碰-任务形式': ['通用-对对碰schema6', '通用-对对碰schema3-5'],
    '挖矿': ['26情人节-挖矿累积任务'],
    '挖孔': ['情人节-节日挖孔小游戏-schema6', '情人节-节日挖孔小游戏-schema3-5'],
    '普通大富翁': ['节日大富翁进度活动（感恩节）'],
    '掉落转付费': ['登月节-掉落转付费-通用第三套'],
    '节日特惠卡第二期': ['节日通用-特惠卡礼包'],
    '聚宝盆（不灰）': [
        '节日活动-聚宝盆抽奖-第1期（schema6）', '节日活动-聚宝盆抽奖-第2期（schema6）',
        '节日活动-聚宝盆抽奖-第3期（schema6）', '节日活动-聚宝盆抽奖-第4期（schema6）',
        '节日活动-聚宝盆抽奖-第5期（schema6）',
        '节日活动-聚宝盆抽奖-第1期（schema3~5）', '节日活动-聚宝盆抽奖-第2期（schema3~5）',
        '节日活动-聚宝盆抽奖-第3期（schema3~5）', '节日活动-聚宝盆抽奖-第4期（schema3~5）',
        '节日活动-聚宝盆抽奖-第5期（schema3~5）',
    ],
    '组队BP': ['情人节2026组队BP'],
    '挂机BP': ['挂机BP-情人节'],
    '节日随机转盘': ['新小额随机转盘-schema6-通用', '新小额随机转盘-schema3-5-通用'],
    '抢购礼包（贬值外显）（不灰）': ['情人节-限时抢购-S6-通用皮（1、2期', '情人节-限时抢购-S3-5-通用皮（3期'],
    '巨猿': ['情人节-2026-wonder巨猿'],
    '签到': ['情人节签到-2026'],
    'bingo': ['圣诞节-bingo-通用第三套'],
    '情人节累充排行榜（不灰）': ['情人节2025-排行送花活动'],
}

for xlsx_name, csv_names in mapping.items():
    if xlsx_name not in xlsx_schedule:
        continue
    
    sched = xlsx_schedule[xlsx_name]
    log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    log(f"📋 排期表: {xlsx_name} (负责人: {sched['person']})")
    log(f"   排期覆盖: {sched['start_str']} ~ {sched['end_str']}")
    if sched['mark_details']:
        log(f"   详细标记: {', '.join(sched['mark_details'])}")
    
    for csv_name in csv_names:
        if csv_name in csv_activities:
            items = csv_activities[csv_name]
            for item in items:
                csv_start_d = parse_date(item['start'])
                csv_end_d = parse_date(item['end'])
                
                time_match = ""
                if sched['start'] and sched['end'] and csv_start_d and csv_end_d:
                    # 排期的覆盖范围（从最早标记日到最晚标记日的次日）
                    sched_range_start = sched['start']
                    sched_range_end = sched['end'] + timedelta(days=1)
                    
                    # 检查上线时间是否在排期范围内
                    start_in = sched_range_start <= csv_start_d <= sched_range_end + timedelta(days=1)
                    end_in = sched_range_start <= csv_end_d <= sched_range_end + timedelta(days=1)
                    
                    # 检查具体日期是否包含上线开始日
                    start_date_only = csv_start_d.replace(hour=0, minute=0, second=0)
                    exact_match = start_date_only in [d.replace(hour=0, minute=0, second=0) for d in sched['active_dates']]
                    
                    if exact_match:
                        time_match = "✅ 开始日期精确匹配排期标记"
                    elif start_in and end_in:
                        time_match = "✅ 在排期覆盖范围内"
                    elif start_in or end_in:
                        time_match = "⚠️ 部分在排期范围内"
                    else:
                        start_diff = (csv_start_d - sched_range_start).days
                        end_diff = (csv_end_d - sched_range_end).days
                        time_match = f"❌ 超出排期范围 (开始差{start_diff:+d}天, 结束差{end_diff:+d}天)"
                else:
                    time_match = "⚠️ 排期表无具体日期标记，无法自动比对"
                
                log(f"   📌 上线: {csv_name} (ID:{item['id']})")
                log(f"      上线时间: {item['start']} ~ {item['end']} ({item['duration']})")
                log(f"      {time_match}")
        else:
            log(f"   📌 上线: {csv_name} -> ❌ 未找到")
    log()

# ============ 5. 特别分析：有日期标记的活动详细比对 ============
log("=" * 120)
log("【重点：有明确排期标记的活动 - 逐期比对】")
log()

# 聚宝盆 - 有5期标记
sched = xlsx_schedule.get('聚宝盆（不灰）', {})
if sched.get('mark_details'):
    log("🔍 聚宝盆 排期标记 vs 上线时间：")
    for i, (dt, detail) in enumerate(zip(sched['active_dates'], sched['mark_details'])):
        log(f"   排期第{i+1}期: {detail} -> 日期 {dt.strftime('%Y.%m.%d')}")
    log("   上线表 schema6:")
    for name in ['节日活动-聚宝盆抽奖-第1期（schema6）','节日活动-聚宝盆抽奖-第2期（schema6）',
                 '节日活动-聚宝盆抽奖-第3期（schema6）','节日活动-聚宝盆抽奖-第4期（schema6）',
                 '节日活动-聚宝盆抽奖-第5期（schema6）']:
        if name in csv_activities:
            it = csv_activities[name][0]
            csv_d = parse_date(it['start'])
            # 找排期中哪个标记对应
            period_num = int(name.split('第')[1][0])
            if period_num <= len(sched['active_dates']):
                sched_d = sched['active_dates'][period_num-1]
                match = "✅" if csv_d and sched_d.date() == csv_d.date() else "❌ 不匹配"
                log(f"     {name}: 上线{it['start'][:16]}, 排期{sched_d.strftime('%m.%d')} {match}")
            else:
                log(f"     {name}: 上线{it['start'][:16]}")
    log("   上线表 schema3~5:")
    for name in ['节日活动-聚宝盆抽奖-第1期（schema3~5）','节日活动-聚宝盆抽奖-第2期（schema3~5）',
                 '节日活动-聚宝盆抽奖-第3期（schema3~5）','节日活动-聚宝盆抽奖-第4期（schema3~5）',
                 '节日活动-聚宝盆抽奖-第5期（schema3~5）']:
        if name in csv_activities:
            it = csv_activities[name][0]
            csv_d = parse_date(it['start'])
            period_num = int(name.split('第')[1][0])
            if period_num <= len(sched['active_dates']):
                sched_d = sched['active_dates'][period_num-1]
                match = "✅" if csv_d and sched_d.date() == csv_d.date() else "❌ 不匹配"
                log(f"     {name}: 上线{it['start'][:16]}, 排期{sched_d.strftime('%m.%d')} {match}")
    log()

# 挖矿 - 有3期标记
sched = xlsx_schedule.get('挖矿', {})
if sched.get('mark_details'):
    log("🔍 挖矿 排期标记 vs 上线时间：")
    for i, (dt, detail) in enumerate(zip(sched['active_dates'], sched['mark_details'])):
        log(f"   排期第{i+1}期: {detail} -> 日期 {dt.strftime('%Y.%m.%d')}")
    if '26情人节-挖矿累积任务' in csv_activities:
        items = sorted(csv_activities['26情人节-挖矿累积任务'], key=lambda x: x['start'])
        for i, it in enumerate(items):
            csv_d = parse_date(it['start'])
            if i < len(sched['active_dates']):
                sched_d = sched['active_dates'][i]
                match = "✅" if csv_d and sched_d.date() == csv_d.date() else "❌ 不匹配"
                log(f"   上线第{i+1}期 (ID:{it['id']}): {it['start'][:16]}~{it['end'][:16]}, 排期{sched_d.strftime('%m.%d')} {match}")
            else:
                log(f"   上线第{i+1}期 (ID:{it['id']}): {it['start'][:16]}~{it['end'][:16]} (超出排期标记)")
    log()

# 挖孔 - 有7天标记
sched = xlsx_schedule.get('挖孔', {})
if sched.get('mark_details'):
    log("🔍 挖孔 排期标记 vs 上线时间：")
    for i, (dt, detail) in enumerate(zip(sched['active_dates'], sched['mark_details'])):
        log(f"   排期第{i+1}天: {detail} -> 日期 {dt.strftime('%Y.%m.%d')}")
    range_start = min(sched['active_dates']).strftime('%Y.%m.%d')
    range_end = (max(sched['active_dates']) + timedelta(days=1)).strftime('%Y.%m.%d')
    log(f"   排期覆盖范围: {range_start} ~ {range_end}")
    for name in ['情人节-节日挖孔小游戏-schema6', '情人节-节日挖孔小游戏-schema3-5']:
        if name in csv_activities:
            it = csv_activities[name][0]
            csv_start = parse_date(it['start'])
            csv_end = parse_date(it['end'])
            sched_start = min(sched['active_dates'])
            sched_end_d = max(sched['active_dates']) + timedelta(days=1)
            s_match = "✅" if csv_start and sched_start.date() == csv_start.date() else f"❌(排期{sched_start.strftime('%m.%d')} vs 上线{csv_start.strftime('%m.%d') if csv_start else '?'})"
            e_match = "✅" if csv_end and sched_end_d.date() == csv_end.date() else f"❌(排期{sched_end_d.strftime('%m.%d')} vs 上线{csv_end.strftime('%m.%d') if csv_end else '?'})"
            log(f"   {name}: 上线{it['start'][:16]}~{it['end'][:16]}, 开始{s_match}, 结束{e_match}")
    log()

# 单笔充值 - 有标记
sched = xlsx_schedule.get('单笔充值（不灰）', {})
if sched.get('mark_details'):
    log("🔍 单笔充值 排期标记 vs 上线时间：")
    for detail in sched['mark_details']:
        log(f"   标记: {detail}")
    for name in ['26情人节-单笔充值-第一轮', '26情人节-单笔充值-第二轮']:
        if name in csv_activities:
            it = csv_activities[name][0]
            log(f"   {name} (ID:{it['id']}): {it['start'][:16]}~{it['end'][:16]} ({it['duration']})")
    log()

# 机甲累充 - 有标记
sched = xlsx_schedule.get('机甲累充（不灰）', {})
if sched.get('mark_details'):
    log("🔍 机甲累充 排期标记 vs 上线时间：")
    for detail in sched['mark_details']:
        log(f"   标记: {detail}")
    if '26情人节-机甲累充' in csv_activities:
        it = csv_activities['26情人节-机甲累充'][0]
        log(f"   上线: {it['start'][:16]}~{it['end'][:16]} ({it['duration']})")
    log()

# GACHA每日小额礼包
sched = xlsx_schedule.get('GACHA每日小额礼包（不灰）', {})
if sched.get('mark_details'):
    log("🔍 GACHA每日小额礼包 排期标记 vs 上线时间：")
    for detail in sched['mark_details']:
        log(f"   标记: {detail}")
    if '新组件gacha-云上探宝-每日礼包' in csv_activities:
        it = csv_activities['新组件gacha-云上探宝-每日礼包'][0]
        csv_d = parse_date(it['start'])
        if sched['active_dates'] and csv_d:
            sched_d = sched['active_dates'][0]
            match = "✅" if sched_d.date() == csv_d.date() else f"❌(排期{sched_d.strftime('%m.%d')} vs 上线{csv_d.strftime('%m.%d')})"
            log(f"   上线: {it['start'][:16]}~{it['end'][:16]}, 开始日{match}")
    log()

# 周卡
sched = xlsx_schedule.get('周卡', {})
if sched.get('mark_details'):
    log("🔍 周卡 排期标记：")
    for detail in sched['mark_details']:
        log(f"   标记: {detail}")
    log("   上线表: ❌ 未找到对应条目")
    log()

# 写入文件
with open(r"c:\ADHD_agent\schedule_time_v2.txt", 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("Done -> schedule_time_v2.txt")
