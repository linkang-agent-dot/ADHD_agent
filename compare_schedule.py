#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比排期审核表(xlsx)和正式上线表(csv)，输出到文件
"""
import pandas as pd
import sys
import re

output_lines = []
def log(msg=""):
    output_lines.append(str(msg))

# 1. 读取排期审核表 (xlsx)
xlsx_path = r"c:\Users\linkang\Desktop\节日排期表\实际排期审核.xlsx"
try:
    df_xlsx = pd.read_excel(xlsx_path, engine='openpyxl')
    log("=" * 100)
    log("【排期审核表 (xlsx)】")
    log(f"  总行数: {len(df_xlsx)}")
    cols = list(df_xlsx.columns)
    log(f"  列名: {cols}")
    log()
    
    # 提取活动列表 - 跳过前3行表头
    xlsx_activities = []
    activity_col = cols[0]  # 第一列是活动/玩法名称
    schedule_col = cols[3]  # 类型列
    
    log("--- 排期审核表中的所有活动 ---")
    for idx, row in df_xlsx.iterrows():
        activity_name = str(row[cols[0]]).strip()
        if activity_name == 'nan' or activity_name == '':
            continue
        person = str(row[cols[1]]).strip() if len(cols) > 1 else ''
        category = str(row[cols[3]]).strip() if len(cols) > 3 else ''
        has_multi = str(row[cols[4]]).strip() if len(cols) > 4 else ''
        
        # 获取日期安排 - 从第11列开始是日期
        date_info = []
        for ci in range(11, min(len(cols), 34)):
            val = row[cols[ci]]
            if pd.notna(val) and str(val).strip() != '':
                date_info.append(f"col{ci}={val}")
        
        log(f"  [{idx}] 活动: {activity_name}")
        log(f"       负责人: {person}, 类型: {category}, 多期: {has_multi}")
        if date_info:
            log(f"       日期数据: {date_info[:10]}")
        log()
        xlsx_activities.append({
            'name': activity_name,
            'person': person,
            'category': category,
            'row_idx': idx
        })
        
except Exception as e:
    log(f"读取xlsx失败: {e}")
    import traceback
    log(traceback.format_exc())

log("\n" + "=" * 100)

# 2. 读取正式上线表 (csv)
csv_path = r"c:\Users\linkang\Desktop\节日排期表\情人节正式上线.csv"
encodings = ['gbk', 'gb2312', 'gb18030', 'utf-8', 'utf-8-sig']
df_csv = None
for enc in encodings:
    try:
        df_csv = pd.read_csv(csv_path, encoding=enc)
        log(f"【正式上线表 (csv)】 - 编码: {enc}")
        log(f"  总行数: {len(df_csv)}")
        csv_cols = list(df_csv.columns)
        log(f"  列名: {csv_cols}")
        log()
        
        # 清理列名中的特殊字符
        # CSV中的活动名称列
        name_col = csv_cols[1]  # 活动名称
        id_col = csv_cols[0]    # 活动ID
        start_col = csv_cols[5]  # 活动开始时间
        end_col = csv_cols[6]    # 活动结束时间
        duration_col = csv_cols[7]  # 持续时长
        
        log("--- 正式上线表中的所有活动 ---")
        csv_activities = []
        for idx, row in df_csv.iterrows():
            act_id = str(row[id_col]).strip().replace('\t', '')
            act_name = str(row[name_col]).strip().replace('\t', '')
            start_time = str(row[start_col]).strip().replace('\t', '')
            end_time = str(row[end_col]).strip().replace('\t', '')
            duration = str(row[duration_col]).strip().replace('\t', '')
            
            log(f"  [{idx}] ID: {act_id}, 活动: {act_name}")
            log(f"       时间: {start_time} ~ {end_time} ({duration})")
            
            csv_activities.append({
                'id': act_id,
                'name': act_name,
                'start': start_time,
                'end': end_time,
                'duration': duration,
                'row_idx': idx
            })
        break
    except Exception as e:
        continue

if df_csv is None:
    log("无法读取CSV文件")
    sys.exit(1)

log("\n" + "=" * 100)
log("【对比分析】")
log()

# 建立活动名称映射关系（排期审核表中的名称 -> 正式上线表中的名称）
# 排期审核表使用简短名称，正式上线表使用详细名称，需要做模糊匹配

# 先把xlsx活动名称和csv活动名称分别列出
log("--- 排期审核表活动列表（去除表头后）---")
for a in xlsx_activities:
    log(f"  {a['name']} (负责人: {a['person']})")

log()
log("--- 正式上线表活动列表（去重后的唯一活动名称）---")
unique_csv_names = {}
for a in csv_activities:
    base_name = a['name']
    if base_name not in unique_csv_names:
        unique_csv_names[base_name] = []
    unique_csv_names[base_name].append(a)

for name, items in unique_csv_names.items():
    times = [(i['start'], i['end']) for i in items]
    log(f"  {name} (共{len(items)}条, ID: {[i['id'] for i in items]})")
    for t in times:
        log(f"    时间段: {t[0]} ~ {t[1]}")

log()
log("=" * 100)
log("【排期审核表活动 vs 正式上线表活动 匹配检查】")
log()

# 尝试建立映射
xlsx_names = [a['name'] for a in xlsx_activities]
csv_unique_names = list(unique_csv_names.keys())

# 定义关键词映射：排期审核表简称 -> CSV中可能的关键词
keyword_map = {
    '主城特效累充': '主城特效累充',
    '主城特效累充-服务器排名（跨服）': '主城特效累充-服务器',
    '情人预购连锁': '预购连锁礼包',
    'GACHA+单次充值+累计活跃（跨服）': ['GACHA', '云上探宝', '单笔充值'],
    'GACHA每日小礼包（跨服）': ['GACHA', '每日礼', '每日小礼包', '云上探宝-每日'],
    '单笔充值（跨服）': '单笔充值',
    '机甲累充（跨服）': '机甲累充',
    '聚宝盆抽奖': '聚宝盆抽奖',
    '大富翁+行军特效': ['大富翁', '行军特效'],
    '横版BP（好感排行榜，猜对度，安全属性）': ['横版bp', 'BP'],
    '强消耗扭蛋': '强消耗',
    '强消耗对对碰-翻格子式': '对对碰',
    '挖矿': '挖矿',
    '普通礼包': '联动礼包',
    '小额转盘': '小额随机转盘',
    '排行送花活动（跨服）': '排行送花',
    '节通特惠卡礼包': '特惠卡礼包',
    '总卡': '总卡',
    '聚宝盆（跨服）': '聚宝盆抽奖',
    '组队BP': '组队BP',
    '挂机BP': '挂机BP',
    '掉落转付费': '掉落转付费',
    '合成小游戏（第二套限时价值购,跨服）': '合成小游戏',
    '巨猿': 'wonder巨猿',
    '签到': '签到',
    '第一买一送+限时抢购（跨服）': ['限时抢购', '买一送'],
    'bingo': 'bingo',
    '行军表情礼包': '行军表情礼包',
    '节日挖矿小游戏': '节日挖矿小游戏',
}

# 进行匹配
matched = []
unmatched_xlsx = []

for xa in xlsx_activities:
    xname = xa['name']
    found = False
    matched_csv = []
    
    for cname in csv_unique_names:
        cname_lower = cname.lower()
        xname_lower = xname.lower()
        
        # 直接包含匹配
        if xname_lower in cname_lower or cname_lower in xname_lower:
            matched_csv.append(cname)
            found = True
            continue
        
        # 关键词匹配
        for k, v in keyword_map.items():
            if k.lower() in xname_lower or xname_lower in k.lower():
                if isinstance(v, list):
                    for vi in v:
                        if vi.lower() in cname_lower:
                            matched_csv.append(cname)
                            found = True
                elif v.lower() in cname_lower:
                    matched_csv.append(cname)
                    found = True
    
    if found:
        matched.append((xa, list(set(matched_csv))))
    else:
        unmatched_xlsx.append(xa)

log("--- 已匹配的活动 ---")
for xa, csv_names in matched:
    log(f"  排期表: {xa['name']}")
    for cn in csv_names:
        items = unique_csv_names[cn]
        log(f"    -> 上线表: {cn} (共{len(items)}条)")
        for item in items:
            log(f"       ID:{item['id']} 时间:{item['start']}~{item['end']}")
    log()

log("--- 排期审核表中未匹配到正式上线表的活动 ---")
for xa in unmatched_xlsx:
    log(f"  !! 未匹配: {xa['name']} (负责人: {xa['person']})")

log()
log("--- 正式上线表中未匹配到排期审核表的活动 ---")
all_matched_csv_names = set()
for _, csv_names in matched:
    all_matched_csv_names.update(csv_names)

for cname in csv_unique_names:
    if cname not in all_matched_csv_names:
        items = unique_csv_names[cname]
        log(f"  !! 未匹配: {cname} (共{len(items)}条)")
        for item in items:
            log(f"     ID:{item['id']} 时间:{item['start']}~{item['end']}")

# 写入文件
with open(r"c:\ADHD_agent\schedule_comparison.txt", 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("分析完成，结果已写入 schedule_comparison.txt")
