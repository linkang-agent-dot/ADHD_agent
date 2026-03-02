#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比排期审核表和正式上线表的服务器配置
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta

output_lines = []
def log(msg=""):
    output_lines.append(str(msg))

# ============ 1. 读取排期审核表 ============
xlsx_path = r"c:\Users\linkang\Desktop\节日排期表\实际排期审核.xlsx"
df = pd.read_excel(xlsx_path, engine='openpyxl', header=None)

log("=" * 120)
log("【排期审核表 - 服务器相关字段提取】")
log()

# 行0是列名，行4+是数据
# 列0=节日活动名, 列1=活动上线负责人, 列2=检查, 列3=跨服, 列4=上线, 列5=上线总服务器数量
# 列6=互测check, 列7=互测负责人, 列8=活动条数

xlsx_data = {}
for row_idx in range(4, len(df)):
    name = df.iloc[row_idx, 0]
    if pd.isna(name) or str(name).strip() == '':
        continue
    name = str(name).strip()
    person = str(df.iloc[row_idx, 1]).strip() if pd.notna(df.iloc[row_idx, 1]) else ''
    check_val = df.iloc[row_idx, 2]
    cross_server = str(df.iloc[row_idx, 3]).strip() if pd.notna(df.iloc[row_idx, 3]) else ''
    online_flag = df.iloc[row_idx, 4]
    server_count = df.iloc[row_idx, 5]
    mutual_check = df.iloc[row_idx, 6]
    mutual_person = str(df.iloc[row_idx, 7]).strip() if pd.notna(df.iloc[row_idx, 7]) else ''
    activity_count = df.iloc[row_idx, 8]
    
    log(f"  {name}")
    log(f"    跨服类型: {cross_server}")
    log(f"    上线: {online_flag}, 服务器数量: {server_count}, 活动条数: {activity_count}")
    log(f"    互测check: {mutual_check}, 检查: {check_val}")
    log()
    
    xlsx_data[name] = {
        'person': person,
        'cross_server': cross_server,
        'online_flag': online_flag,
        'server_count': server_count,
        'activity_count': activity_count,
        'mutual_check': mutual_check,
    }

# ============ 2. 读取正式上线表 ============
csv_path = r"c:\Users\linkang\Desktop\节日排期表\情人节正式上线.csv"
df_csv = pd.read_csv(csv_path, encoding='gbk')
csv_cols = list(df_csv.columns)

log("=" * 120)
log("【正式上线表 - 服务器相关字段提取】")
log()

csv_data = {}
for idx, row in df_csv.iterrows():
    act_id = str(row[csv_cols[0]]).strip().replace('\t', '')
    act_name = str(row[csv_cols[1]]).strip().replace('\t', '')
    servers = str(row[csv_cols[2]]).strip().replace('\t', '')
    cross_rank = str(row[csv_cols[3]]).strip().replace('\t', '')  # 是否跨服排名
    cross_server = str(row[csv_cols[4]]).strip().replace('\t', '')  # 是否跨服
    
    # 解析服务器信息
    # 跨服的格式: "X组 (server1, server2, ...), (server3, server4, ...)"
    # 单服的格式: "server1, server2, server3, ..."
    
    # 提取组数
    group_match = re.match(r'(\d+)组', servers)
    num_groups = int(group_match.group(1)) if group_match else 0
    
    # 提取所有服务器ID
    all_servers = re.findall(r'(\d{7})', servers)
    num_servers = len(all_servers)
    
    if act_name not in csv_data:
        csv_data[act_name] = []
    csv_data[act_name].append({
        'id': act_id,
        'servers_raw': servers[:80] + ('...' if len(servers) > 80 else ''),
        'cross_rank': cross_rank,
        'cross_server': cross_server,
        'num_groups': num_groups,
        'num_servers': num_servers,
        'all_servers': set(all_servers),
    })

# 打印每个唯一活动的服务器信息
for act_name, items in csv_data.items():
    # 所有同名活动应该有相同的服务器配置
    log(f"  {act_name}")
    for item in items:
        log(f"    ID:{item['id']} | 跨服排名:{item['cross_rank']} | 跨服:{item['cross_server']} | 分组:{item['num_groups']}组 | 服务器数:{item['num_servers']}")
    log()

# ============ 3. 对比分析 ============
log("=" * 120)
log("【服务器配置逐项对比】")
log()

mapping = {
    '主城特效累充': ['情人节2026-主城特效累充-个人'],
    '主城特效累充-服务器版（不灰）': ['情人节2026-主城特效累充-服务器'],
    '节日预购礼包': ['通用-情人节预购连锁礼包_schema6', '通用-情人节预购连锁礼包_schema3-5'],
    'GACHA+配套充值+累计活动（不灰）': ['26新组件gacha-云上探宝'],
    'GACHA每日小额礼包（不灰）': ['新组件gacha-云上探宝-每日礼包'],
    '单笔充值（不灰）': ['26情人节-单笔充值-第一轮', '26情人节-单笔充值-第二轮'],
    '机甲累充（不灰）': ['26情人节-机甲累充'],
    '机甲皮肤抽奖': [],
    '联动礼包+行军表情': ['联动礼包-2026情人节', '2026情人节-行军特效礼包', '情人节2026-行军表情礼包'],
    '长节日BP（无排行榜，不灰度，有全服进度）': ['情人节2026-横版bp（循环宝箱版）'],
    '强消耗扭蛋': ['情人节2026-强消耗-schema6', '情人节2026-强消耗-schema3-5'],
    '强消耗对对碰-任务形式': ['通用-对对碰schema6', '通用-对对碰schema3-5'],
    '挖矿': ['26情人节-挖矿累积任务'],
    '挖孔': ['情人节-节日挖孔小游戏-schema6', '情人节-节日挖孔小游戏-schema3-5'],
    '普通大富翁': ['节日大富翁进度活动（感恩节）'],
    '掉落转付费': ['登月节-掉落转付费-通用第三套'],
    '情人节累充排行榜（不灰）': ['情人节2025-排行送花活动'],
    '7日': [],
    '节日特惠卡第二期': ['节日通用-特惠卡礼包'],
    '周卡': [],
    '聚宝盆（不灰）': [
        '节日活动-聚宝盆抽奖-第1期（schema6）',
        '节日活动-聚宝盆抽奖-第1期（schema3~5）',
    ],
    '组队BP': ['情人节2026组队BP'],
    '挂机BP': ['挂机BP-情人节'],
    '节日随机转盘': ['新小额随机转盘-schema6-通用', '新小额随机转盘-schema3-5-通用'],
    '抢购礼包（贬值外显）（不灰）': ['情人节-限时抢购-S6-通用皮（1、2期', '情人节-限时抢购-S3-5-通用皮（3期'],
    '巨猿': ['情人节-2026-wonder巨猿'],
    '签到': ['情人节签到-2026'],
    '买一赠一（看情况补付费）（不灰）': [],
    'bingo': ['圣诞节-bingo-通用第三套'],
}

# 定义预期的全服schema6服务器列表和schema3-5服务器列表
# 从CSV中提取参考集 - 用一个大活动的全服服务器列表作为参考
ref_all_servers = set()
ref_schema6_servers = set()
ref_schema35_servers = set()

# 取一个全服单服活动的服务器列表作为"全服"参考
for item in csv_data.get('情人节签到-2026', []):
    ref_all_servers = item['all_servers']
    break

# 取schema6活动参考
for item in csv_data.get('通用-情人节预购连锁礼包_schema6', []):
    ref_schema6_servers = item['all_servers']
    break

# 取schema3-5活动参考
for item in csv_data.get('通用-情人节预购连锁礼包_schema3-5', []):
    ref_schema35_servers = item['all_servers']
    break

log(f"参考服务器集合:")
log(f"  全服（单服活动参考，如签到）: {len(ref_all_servers)} 个服务器")
log(f"  Schema6 参考: {len(ref_schema6_servers)} 个服务器")
log(f"  Schema3-5 参考: {len(ref_schema35_servers)} 个服务器")
log(f"  Schema6 + Schema3-5 = {len(ref_schema6_servers | ref_schema35_servers)} 个")
log(f"  全服 vs Schema合并 差异: {ref_all_servers - (ref_schema6_servers | ref_schema35_servers)}")
log()

# 跨服类型映射
cross_type_map = {
    '单服': ('否', '单服'),
    '跨服-全服': ('是', '跨服'),
    '跨服-分组': ('是', '跨服'),  # 分组也是跨服
    '跨服分组': ('是', '跨服'),
}

for xlsx_name, csv_names in mapping.items():
    if xlsx_name not in xlsx_data:
        continue
    xd = xlsx_data[xlsx_name]
    
    log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    log(f"📋 {xlsx_name}")
    log(f"   排期表: 跨服类型={xd['cross_server']}, 服务器数量={xd['server_count']}, 活动条数={xd['activity_count']}")
    
    if not csv_names:
        log(f"   上线表: ❌ 无对应条目")
        log()
        continue
    
    expected_cross = cross_type_map.get(xd['cross_server'], (None, None))
    
    for csv_name in csv_names:
        if csv_name not in csv_data:
            log(f"   📌 {csv_name}: ❌ 未找到")
            continue
        
        items = csv_data[csv_name]
        # 取第一条作为代表（同名活动的服务器配置应一致）
        item = items[0]
        
        # 1. 跨服类型比对
        csv_cross_rank = item['cross_rank']
        csv_cross = item['cross_server']
        
        cross_match = ""
        if expected_cross[0] is not None:
            if xd['cross_server'] == '单服':
                if csv_cross == '单服':
                    cross_match = "✅"
                else:
                    cross_match = f"❌ 排期=单服, 上线={csv_cross}"
            elif '跨服' in xd['cross_server']:
                if csv_cross == '跨服':
                    cross_match = "✅"
                else:
                    cross_match = f"❌ 排期={xd['cross_server']}, 上线={csv_cross}"
        
        # 2. 跨服排名比对
        rank_match = ""
        if xd['cross_server'] == '跨服-全服':
            if csv_cross_rank == '是':
                rank_match = "✅ 跨服排名=是"
            else:
                rank_match = f"⚠️ 排期=跨服-全服但上线跨服排名={csv_cross_rank}"
        elif xd['cross_server'] == '跨服-分组' or xd['cross_server'] == '跨服分组':
            rank_match = f"跨服排名={csv_cross_rank}"
        
        # 3. 服务器数量比对
        num_servers = item['num_servers']
        num_groups = item['num_groups']
        
        # 检查服务器集合是否匹配预期
        server_set = item['all_servers']
        server_note = ""
        if csv_cross == '单服':
            if server_set == ref_all_servers:
                server_note = "= 全服标准集"
            elif server_set == ref_schema6_servers:
                server_note = "= Schema6标准集"
            elif server_set == ref_schema35_servers:
                server_note = "= Schema3-5标准集"
            else:
                # 检查是否接近
                if ref_all_servers:
                    missing = ref_all_servers - server_set
                    extra = server_set - ref_all_servers
                    if len(missing) <= 5 and len(extra) <= 5:
                        server_note = f"≈ 全服(缺{len(missing)}多{len(extra)})"
                    elif ref_schema6_servers and server_set == ref_schema6_servers:
                        server_note = "= Schema6集"
                    elif ref_schema35_servers and server_set == ref_schema35_servers:
                        server_note = "= Schema3-5集"
        elif csv_cross == '跨服':
            if server_set == ref_all_servers:
                server_note = "= 全服标准集(1组)"
            elif server_set == ref_schema6_servers:
                server_note = "= Schema6标准集"
            elif server_set == ref_schema35_servers:
                server_note = "= Schema3-5标准集"

        # 4. 活动条数比对
        total_csv_items = len(items)
        count_note = ""
        act_count = xd['activity_count']
        if pd.notna(act_count):
            try:
                expected_count = int(float(act_count))
                # 这个csv_name可能只是映射中的一个，需要加上所有映射
                # 暂时只比对单个
            except:
                pass
        
        log(f"   📌 {csv_name} (取ID:{item['id']}为代表, 共{total_csv_items}条)")
        log(f"      跨服: {csv_cross} {cross_match}")
        log(f"      跨服排名: {csv_cross_rank} {rank_match}")
        log(f"      分组数: {num_groups}组, 服务器数: {num_servers} {server_note}")
    
    # 活动条数总计
    total_mapped = 0
    for cn in csv_names:
        if cn in csv_data:
            total_mapped += len(csv_data[cn])
    
    act_count = xd['activity_count']
    if pd.notna(act_count):
        try:
            expected = int(float(act_count))
            if total_mapped == expected:
                log(f"   活动条数: 排期={expected}, 上线={total_mapped} ✅")
            else:
                log(f"   活动条数: 排期={expected}, 上线={total_mapped} ❌ 不匹配")
        except:
            log(f"   活动条数: 排期={act_count}, 上线={total_mapped}")
    
    log()

# ============ 4. 服务器集合一致性检查 ============
log("=" * 120)
log("【服务器集合一致性检查】")
log()

# 比较同类型活动的服务器是否一致
# 所有单服活动应该用相同的全服列表
# schema6活动应该用相同的服务器列表
# schema3-5活动应该用相同的服务器列表

log("--- 单服活动服务器集合对比 ---")
single_server_activities = {}
for act_name, items in csv_data.items():
    for item in items:
        if item['cross_server'] == '单服':
            key = f"{act_name}(ID:{item['id']})"
            single_server_activities[key] = item['all_servers']

# 找出基准集（出现最多的服务器集合大小）
from collections import Counter
size_counts = Counter(len(v) for v in single_server_activities.values())
log(f"单服活动服务器数量分布: {dict(size_counts)}")
log()

# 按服务器数量分组
by_size = {}
for k, v in single_server_activities.items():
    sz = len(v)
    if sz not in by_size:
        by_size[sz] = []
    by_size[sz].append(k)

for sz, names in sorted(by_size.items()):
    log(f"  {sz}个服务器的活动({len(names)}个):")
    for n in names[:5]:
        log(f"    - {n}")
    if len(names) > 5:
        log(f"    ... 还有{len(names)-5}个")
    log()

# 检查同一大小的集合是否完全一致
log("--- 跨服活动服务器集合对比 ---")
cross_server_activities = {}
for act_name, items in csv_data.items():
    for item in items:
        if item['cross_server'] == '跨服':
            key = f"{act_name}(ID:{item['id']})"
            cross_server_activities[key] = {
                'servers': item['all_servers'],
                'groups': item['num_groups'],
                'count': item['num_servers']
            }

log(f"跨服活动总数: {len(cross_server_activities)}")
cross_size_counts = Counter(v['count'] for v in cross_server_activities.values())
log(f"跨服活动服务器数量分布: {dict(cross_size_counts)}")
log()

for sz, names in sorted(by_size.items()):
    # 取这个大小的所有集合，检查是否一致
    sets_of_this_size = [(k, single_server_activities[k]) for k in names]
    if len(sets_of_this_size) > 1:
        base_set = sets_of_this_size[0][1]
        diffs = []
        for k, s in sets_of_this_size[1:]:
            if s != base_set:
                missing = base_set - s
                extra = s - base_set
                diffs.append((k, missing, extra))
        if diffs:
            log(f"⚠️ {sz}服务器集合中有差异:")
            base_name = sets_of_this_size[0][0]
            log(f"  基准: {base_name}")
            for k, missing, extra in diffs[:3]:
                log(f"  {k}: 缺少{missing if missing else '无'}, 多出{extra if extra else '无'}")
            log()

# ============ 5. 详细检查schema分割是否正确 ============
log("=" * 120)
log("【Schema分割检查 - schema6 vs schema3-5 服务器是否有重叠】")
log()

schema_pairs = [
    ('通用-情人节预购连锁礼包_schema6', '通用-情人节预购连锁礼包_schema3-5'),
    ('情人节2026-强消耗-schema6', '情人节2026-强消耗-schema3-5'),
    ('通用-对对碰schema6', '通用-对对碰schema3-5'),
    ('情人节-节日挖孔小游戏-schema6', '情人节-节日挖孔小游戏-schema3-5'),
    ('新小额随机转盘-schema6-通用', '新小额随机转盘-schema3-5-通用'),
    ('节日活动-聚宝盆抽奖-第1期（schema6）', '节日活动-聚宝盆抽奖-第1期（schema3~5）'),
]

for s6_name, s35_name in schema_pairs:
    s6_servers = set()
    s35_servers = set()
    if s6_name in csv_data:
        s6_servers = csv_data[s6_name][0]['all_servers']
    if s35_name in csv_data:
        s35_servers = csv_data[s35_name][0]['all_servers']
    
    if s6_servers and s35_servers:
        overlap = s6_servers & s35_servers
        combined = s6_servers | s35_servers
        short_name = s6_name.split('-')[0] if '-' in s6_name else s6_name[:15]
        
        if overlap:
            log(f"❌ {short_name}: schema6({len(s6_servers)}) + schema3-5({len(s35_servers)}) 有重叠 {len(overlap)}个服务器!")
            log(f"   重叠服务器: {sorted(overlap)[:10]}")
        else:
            log(f"✅ {short_name}: schema6({len(s6_servers)}) + schema3-5({len(s35_servers)}) = {len(combined)} 无重叠")
    log()

# 写入文件
with open(r"c:\ADHD_agent\schedule_server_comparison.txt", 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("Done -> schedule_server_comparison.txt")
