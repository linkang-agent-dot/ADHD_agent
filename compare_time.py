#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比排期审核表和正式上线表的时间安排
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

output_lines = []
def log(msg=""):
    output_lines.append(str(msg))

# ============ 1. 读取排期审核表 ============
xlsx_path = r"c:\Users\linkang\Desktop\节日排期表\实际排期审核.xlsx"
df_xlsx = pd.read_excel(xlsx_path, engine='openpyxl', header=None)

log("=" * 120)
log("【排期审核表结构分析】")
log()

# 打印前5行看表头结构
for i in range(min(5, len(df_xlsx))):
    row_data = []
    for j in range(min(35, len(df_xlsx.columns))):
        val = df_xlsx.iloc[i, j]
        if pd.notna(val):
            row_data.append(f"[{j}]={val}")
    log(f"  行{i}: {row_data}")
log()

# 第0行是列名：节日活动名, 活动上线负责人, 检查, 跨服, 上线, 上线总服务器数量, 互测check, 互测负责人, 活动条数, ?, 活动排期, 然后是日期
# 第1行可能有星期几
# 第2行可能有日期数字 (Excel serial)

# 解析日期行 - 第2行(index 2)应该包含日期序列号
log("--- 解析日期列 (从第11列开始) ---")
date_cols = {}
for col_idx in range(11, min(34, len(df_xlsx.columns))):
    # 第0行：日期编号 (1,2,3...)
    header_num = df_xlsx.iloc[0, col_idx]
    # 第1行：星期几
    weekday = df_xlsx.iloc[1, col_idx]
    # 第2行：日期序列号
    date_serial = df_xlsx.iloc[2, col_idx]
    
    actual_date = None
    if pd.notna(date_serial):
        try:
            # Excel日期序列号转换
            serial = int(float(date_serial))
            # Excel base date is 1899-12-30
            actual_date = datetime(1899, 12, 30) + timedelta(days=serial)
            date_str = actual_date.strftime('%m/%d')
        except:
            date_str = str(date_serial)
    else:
        date_str = "N/A"
    
    date_cols[col_idx] = {
        'num': header_num,
        'weekday': weekday,
        'date_serial': date_serial,
        'date': actual_date,
        'date_str': date_str
    }
    log(f"  列{col_idx}: 编号={header_num}, 星期={weekday}, 日期序号={date_serial}, 实际日期={date_str}")

log()

# ============ 2. 提取每个活动的排期 ============
log("=" * 120)
log("【每个活动的排期时间提取】")
log()

xlsx_schedule = {}
for row_idx in range(3, len(df_xlsx)):
    activity_name = df_xlsx.iloc[row_idx, 0]
    if pd.isna(activity_name) or str(activity_name).strip() == '':
        continue
    activity_name = str(activity_name).strip()
    person = str(df_xlsx.iloc[row_idx, 1]).strip() if pd.notna(df_xlsx.iloc[row_idx, 1]) else ''
    category = str(df_xlsx.iloc[row_idx, 3]).strip() if pd.notna(df_xlsx.iloc[row_idx, 3]) else ''
    multi_flag = df_xlsx.iloc[row_idx, 4]  # 上线列
    
    # 提取这行中日期列的所有标记
    date_marks = []
    for col_idx in range(11, min(34, len(df_xlsx.columns))):
        val = df_xlsx.iloc[row_idx, col_idx]
        if pd.notna(val) and str(val).strip() != '':
            date_info = date_cols.get(col_idx, {})
            date_marks.append({
                'col': col_idx,
                'value': val,
                'date': date_info.get('date'),
                'date_str': date_info.get('date_str', '?')
            })
    
    # 判断活动时间范围
    if date_marks:
        # 找出所有有标记的日期
        marked_dates = [m for m in date_marks if m['date'] is not None]
        if marked_dates:
            first_date = min(m['date'] for m in marked_dates)
            last_date = max(m['date'] for m in marked_dates)
            # 结束时间通常是最后一个标记日期的次日（因为活动一般到当天24:00）
            schedule_start = first_date.strftime('%Y.%m.%d')
            schedule_end = (last_date + timedelta(days=1)).strftime('%Y.%m.%d')
        else:
            schedule_start = '?'
            schedule_end = '?'
    else:
        schedule_start = '无标记'
        schedule_end = '无标记'
    
    log(f"  活动: {activity_name}")
    log(f"    负责人: {person}, 跨服: {category}")
    log(f"    排期: {schedule_start} ~ {schedule_end}")
    if date_marks:
        marks_str = ', '.join([f"{m['date_str']}({m['value']})" for m in date_marks])
        log(f"    详细标记: {marks_str}")
    log()
    
    xlsx_schedule[activity_name] = {
        'person': person,
        'category': category,
        'start': schedule_start,
        'end': schedule_end,
        'marks': date_marks
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

# ============ 4. 建立映射并对比时间 ============
log("=" * 120)
log("【排期时间 vs 上线时间 逐项对比】")
log()

# 手动建立精确映射
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

def parse_date(s):
    """解析日期字符串"""
    s = s.strip()
    for fmt in ['%Y.%m.%d %H:%M:%S', '%Y.%m.%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
        try:
            return datetime.strptime(s, fmt)
        except:
            continue
    return None

def date_short(s):
    """提取简短日期"""
    d = parse_date(s)
    if d:
        return d.strftime('%m.%d')
    return s[:10] if len(s) >= 10 else s

for xlsx_name, csv_names in mapping.items():
    if xlsx_name not in xlsx_schedule:
        continue
    
    sched = xlsx_schedule[xlsx_name]
    log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    log(f"📋 排期表: {xlsx_name} (负责人: {sched['person']})")
    log(f"   排期时间: {sched['start']} ~ {sched['end']}")
    if sched['marks']:
        marks_str = ', '.join([f"{m['date_str']}({m['value']})" for m in sched['marks']])
        log(f"   详细标记: {marks_str}")
    
    for csv_name in csv_names:
        if csv_name in csv_activities:
            items = csv_activities[csv_name]
            for item in items:
                csv_start = date_short(item['start'])
                csv_end = date_short(item['end'])
                
                # 比较时间
                sched_start_d = parse_date(sched['start']) if sched['start'] not in ['?', '无标记'] else None
                sched_end_d = parse_date(sched['end']) if sched['end'] not in ['?', '无标记'] else None
                csv_start_d = parse_date(item['start'])
                csv_end_d = parse_date(item['end'])
                
                time_match = ""
                if sched_start_d and csv_start_d and sched_end_d and csv_end_d:
                    # 检查上线时间是否在排期范围内
                    if csv_start_d >= sched_start_d and csv_end_d <= sched_end_d + timedelta(days=1):
                        time_match = "✅ 匹配"
                    elif csv_start_d == sched_start_d or csv_end_d == sched_end_d:
                        time_match = "⚠️ 部分匹配"
                    else:
                        start_diff = (csv_start_d - sched_start_d).days
                        end_diff = (csv_end_d - sched_end_d).days
                        time_match = f"❌ 不匹配 (开始差{start_diff:+d}天, 结束差{end_diff:+d}天)"
                elif sched['start'] in ['?', '无标记']:
                    time_match = "⚠️ 排期表无时间标记，无法比对"
                else:
                    time_match = "⚠️ 无法解析时间"
                
                log(f"   📌 上线表: {csv_name} (ID:{item['id']})")
                log(f"      上线时间: {item['start']} ~ {item['end']} ({item['duration']})")
                log(f"      比对结果: {time_match}")
        else:
            log(f"   📌 上线表: {csv_name} -> ❌ 未找到此条目")
    log()

# ============ 5. 未匹配活动 ============
log("=" * 120)
log("【排期审核表中有但上线表中缺少的活动】")
log()
missing_in_csv = ['机甲皮肤抽奖', '7日', '周卡', '买一赠一（看情况补付费）（不灰）']
for name in missing_in_csv:
    if name in xlsx_schedule:
        s = xlsx_schedule[name]
        log(f"  ❌ {name} (负责人: {s['person']}, 排期: {s['start']}~{s['end']})")

log()
log("【上线表中有但排期审核表中缺少的活动】")
log()
matched_csv_names = set()
for csv_names in mapping.values():
    matched_csv_names.update(csv_names)

for csv_name, items in csv_activities.items():
    if csv_name not in matched_csv_names:
        for item in items:
            log(f"  ❌ {csv_name} (ID:{item['id']}, 时间: {item['start']}~{item['end']})")

# 写入文件
with open(r"c:\ADHD_agent\schedule_time_comparison.txt", 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("时间对比分析完成，结果已写入 schedule_time_comparison.txt")
