#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排期审核对比脚本 - 对比排期审核表(xlsx)与正式上线表(csv)
用法: python schedule_audit.py --xlsx <排期表路径> --csv <上线表路径> --mapping <映射JSON> --output <输出目录>
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta

import pandas as pd

# ============================================================
# 配置常量
# ============================================================
# Excel 表结构
XLSX_ROW_HEADERS = 0       # 列名行
XLSX_ROW_DAY_NUM = 1       # 日编号行
XLSX_ROW_WEEKDAY = 2       # 星期行
XLSX_ROW_DATE_SERIAL = 3   # 日期序列号行
XLSX_ROW_DATA_START = 4    # 数据起始行
XLSX_COL_ACTIVITY = 0      # 活动名称列
XLSX_COL_PERSON = 1        # 负责人列
XLSX_COL_CHECK = 2         # 检查列
XLSX_COL_CROSS_SERVER = 3  # 跨服类型列
XLSX_COL_ONLINE = 4        # 上线标记列
XLSX_COL_SERVER_COUNT = 5  # 服务器数量列
XLSX_COL_MUTUAL_CHECK = 6  # 互测check列
XLSX_COL_MUTUAL_PERSON = 7 # 互测负责人列
XLSX_COL_ACT_COUNT = 8     # 活动条数列
XLSX_COL_DATE_START = 11   # 日期列起始
XLSX_COL_DATE_END = 34     # 日期列结束(不含)

# CSV 列索引
CSV_COL_ID = 0
CSV_COL_NAME = 1
CSV_COL_SERVERS = 2
CSV_COL_CROSS_RANK = 3
CSV_COL_CROSS_SERVER = 4
CSV_COL_START = 5
CSV_COL_END = 6
CSV_COL_DURATION = 7

# 服务器数量标准
SERVER_FULL = 130           # 全服标准（不含灰度）
SERVER_FULL_GRAY = 142      # 全服含灰度
SERVER_S6 = 77              # Schema6 标准
SERVER_S35 = 53             # Schema3-5 标准
SERVER_GRAY_EXTRA = 12      # 灰度额外服务器数

# 时间偏移：排期标记日 = 部署日，实际上线 = +1天
DEPLOY_DAY_OFFSET = 1


# ============================================================
# 数据读取
# ============================================================
def read_xlsx(xlsx_path):
    """读取排期审核表，返回 (date_map, activities)"""
    df = pd.read_excel(xlsx_path, engine='openpyxl', header=None)

    # 解析日期列
    date_map = {}
    for col in range(XLSX_COL_DATE_START, min(XLSX_COL_DATE_END, len(df.columns))):
        serial_val = df.iloc[XLSX_ROW_DATE_SERIAL, col]
        if pd.notna(serial_val):
            try:
                serial = int(float(serial_val))
                date_map[col] = datetime(1899, 12, 30) + timedelta(days=serial)
            except (ValueError, TypeError):
                date_map[col] = None
        else:
            date_map[col] = None

    # 提取活动数据
    activities = {}
    for row in range(XLSX_ROW_DATA_START, len(df)):
        name = df.iloc[row, XLSX_COL_ACTIVITY]
        if pd.isna(name) or str(name).strip() == '':
            continue
        name = str(name).strip()
        person = str(df.iloc[row, XLSX_COL_PERSON]).strip() if pd.notna(df.iloc[row, XLSX_COL_PERSON]) else ''
        cross_server = str(df.iloc[row, XLSX_COL_CROSS_SERVER]).strip() if pd.notna(df.iloc[row, XLSX_COL_CROSS_SERVER]) else ''
        server_count = df.iloc[row, XLSX_COL_SERVER_COUNT]
        act_count = df.iloc[row, XLSX_COL_ACT_COUNT]

        # 收集日期标记
        active_dates = []
        mark_details = []
        for col in range(XLSX_COL_DATE_START, min(XLSX_COL_DATE_END, len(df.columns))):
            val = df.iloc[row, col]
            if pd.notna(val) and str(val).strip() not in ('', 'False', '0', '0.0'):
                val_str = str(val).strip()
                dt = date_map.get(col)
                if dt:
                    active_dates.append(dt)
                    mark_details.append(f"{dt.strftime('%m.%d')}({val_str})")

        activities[name] = {
            'person': person,
            'cross_server': cross_server,
            'server_count': server_count,
            'act_count': act_count,
            'active_dates': active_dates,
            'mark_details': mark_details,
            'start': min(active_dates) if active_dates else None,
            'end': max(active_dates) if active_dates else None,
        }

    return date_map, activities


def read_csv(csv_path, encoding='gbk'):
    """读取正式上线表，返回 activities_by_name"""
    df = pd.read_csv(csv_path, encoding=encoding)
    cols = list(df.columns)

    activities = {}
    for _, row in df.iterrows():
        act_id = str(row[cols[CSV_COL_ID]]).strip().replace('\t', '')
        act_name = str(row[cols[CSV_COL_NAME]]).strip().replace('\t', '')
        servers_raw = str(row[cols[CSV_COL_SERVERS]]).strip().replace('\t', '')
        cross_rank = str(row[cols[CSV_COL_CROSS_RANK]]).strip().replace('\t', '')
        cross_server = str(row[cols[CSV_COL_CROSS_SERVER]]).strip().replace('\t', '')
        start_time = str(row[cols[CSV_COL_START]]).strip().replace('\t', '')
        end_time = str(row[cols[CSV_COL_END]]).strip().replace('\t', '')
        duration = str(row[cols[CSV_COL_DURATION]]).strip().replace('\t', '')

        # 解析服务器
        group_match = re.match(r'(\d+)组', servers_raw)
        num_groups = int(group_match.group(1)) if group_match else 0
        all_servers = set(re.findall(r'(\d{7})', servers_raw))
        num_servers = len(all_servers)

        if act_name not in activities:
            activities[act_name] = []
        activities[act_name].append({
            'id': act_id,
            'start': start_time,
            'end': end_time,
            'duration': duration,
            'cross_rank': cross_rank,
            'cross_server': cross_server,
            'num_groups': num_groups,
            'num_servers': num_servers,
            'all_servers': all_servers,
            'servers_raw_short': servers_raw[:80] + ('...' if len(servers_raw) > 80 else ''),
        })

    return activities


# ============================================================
# 辅助函数
# ============================================================
def parse_date(s):
    """解析日期字符串"""
    if not s or s == 'nan':
        return None
    s = s.strip()
    for fmt in ['%Y.%m.%d %H:%M:%S', '%Y.%m.%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
        try:
            return datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            continue
    return None


def is_bugui(name):
    """检查活动名称是否标注"不灰" """
    return '不灰' in name


def expected_server_count(name, cross_type, is_schema6=False, is_schema35=False):
    """根据活动属性返回预期服务器数"""
    if is_bugui(name):
        # "不灰"活动 = 全服含灰度
        if is_schema6:
            return SERVER_S6 + SERVER_GRAY_EXTRA  # 89
        elif is_schema35:
            return SERVER_S35  # 53 (灰度服务器加在 S6 侧)
        else:
            return SERVER_FULL_GRAY  # 142
    else:
        if is_schema6:
            return SERVER_S6   # 77
        elif is_schema35:
            return SERVER_S35  # 53
        else:
            return SERVER_FULL  # 130


# ============================================================
# 1. 活动条目匹配
# ============================================================
def audit_activity_matching(xlsx_acts, csv_acts, mapping):
    """对比活动条目"""
    results = {
        'matched': [],
        'xlsx_missing': [],  # 排期有但上线缺失
        'csv_missing': [],   # 上线有但排期缺失
    }

    all_matched_csv = set()

    for xlsx_name, csv_names in mapping.items():
        if xlsx_name not in xlsx_acts:
            continue
        xa = xlsx_acts[xlsx_name]

        if not csv_names:
            results['xlsx_missing'].append({
                'name': xlsx_name,
                'person': xa['person'],
                'note': '上线表中无对应条目',
            })
            continue

        found_any = False
        matched_items = []
        total_csv_count = 0

        for cn in csv_names:
            if cn in csv_acts:
                items = csv_acts[cn]
                total_csv_count += len(items)
                for item in items:
                    matched_items.append({
                        'csv_name': cn,
                        'id': item['id'],
                        'start': item['start'],
                        'end': item['end'],
                    })
                all_matched_csv.add(cn)
                found_any = True

        if found_any:
            results['matched'].append({
                'xlsx_name': xlsx_name,
                'person': xa['person'],
                'csv_items': matched_items,
                'csv_count': total_csv_count,
            })
        else:
            results['xlsx_missing'].append({
                'name': xlsx_name,
                'person': xa['person'],
                'note': f'映射目标 {csv_names} 在上线表中未找到',
            })

    # 检查上线表中未匹配的
    for csv_name in csv_acts:
        if csv_name not in all_matched_csv:
            items = csv_acts[csv_name]
            results['csv_missing'].append({
                'name': csv_name,
                'count': len(items),
                'ids': [it['id'] for it in items],
                'start': items[0]['start'] if items else '',
                'end': items[-1]['end'] if items else '',
            })

    return results


# ============================================================
# 2. 上线时间对比
# ============================================================
def audit_time(xlsx_acts, csv_acts, mapping):
    """对比上线时间"""
    results = {
        'with_marks': [],     # 有排期标记的活动
        'without_marks': [],  # 无排期标记的活动
        'offset_pattern': f'+{DEPLOY_DAY_OFFSET}天（排期标记日=部署日，次日上线）',
    }

    for xlsx_name, csv_names in mapping.items():
        if xlsx_name not in xlsx_acts or not csv_names:
            continue
        xa = xlsx_acts[xlsx_name]

        csv_items = []
        for cn in csv_names:
            if cn in csv_acts:
                for item in csv_acts[cn]:
                    csv_items.append({'name': cn, **item})

        if not csv_items:
            continue

        if xa['active_dates']:
            # 有排期标记
            comparisons = []
            for ci in sorted(csv_items, key=lambda x: x['start']):
                csv_start = parse_date(ci['start'])
                csv_end = parse_date(ci['end'])

                match_result = '⚠️ 无法比对'
                if csv_start and xa['active_dates']:
                    # 检查 csv 开始日 - 1 天是否在排期标记中
                    deploy_day = (csv_start - timedelta(days=DEPLOY_DAY_OFFSET)).date()
                    sched_dates = [d.date() for d in xa['active_dates']]

                    if deploy_day in sched_dates:
                        match_result = f'✅ 匹配（排期{deploy_day.strftime("%m.%d")} → 上线{csv_start.strftime("%m.%d")}，+{DEPLOY_DAY_OFFSET}天）'
                    elif xa['start'] and xa['end']:
                        sched_range_start = xa['start'].date()
                        sched_range_end = (xa['end'] + timedelta(days=1)).date()
                        if sched_range_start <= csv_start.date() <= sched_range_end:
                            match_result = '✅ 在排期覆盖范围内'
                        else:
                            diff = (csv_start.date() - sched_range_start).days
                            match_result = f'❌ 超出排期范围（差{diff:+d}天）'

                comparisons.append({
                    'csv_name': ci['name'],
                    'csv_id': ci['id'],
                    'csv_start': ci['start'],
                    'csv_end': ci['end'],
                    'csv_duration': ci.get('duration', ''),
                    'result': match_result,
                })

            results['with_marks'].append({
                'xlsx_name': xlsx_name,
                'person': xa['person'],
                'mark_details': xa['mark_details'],
                'comparisons': comparisons,
            })
        else:
            # 无排期标记
            for ci in csv_items:
                results['without_marks'].append({
                    'xlsx_name': xlsx_name,
                    'csv_name': ci['name'],
                    'csv_id': ci['id'],
                    'start': ci['start'],
                    'end': ci['end'],
                    'duration': ci.get('duration', ''),
                })

    return results


# ============================================================
# 3. 服务器配置对比
# ============================================================
def audit_servers(xlsx_acts, csv_acts, mapping):
    """对比服务器配置"""
    results = {
        'cross_type_mismatch': [],   # 跨服类型不匹配
        'server_count_issues': [],   # 服务器数量异常
        'schema_split_check': [],    # Schema分割检查
        'naming_issues': [],         # 命名问题
    }

    # 建立参考服务器集合
    ref_sets = build_reference_server_sets(csv_acts)

    for xlsx_name, csv_names in mapping.items():
        if xlsx_name not in xlsx_acts or not csv_names:
            continue
        xa = xlsx_acts[xlsx_name]

        for cn in csv_names:
            if cn not in csv_acts:
                continue
            item = csv_acts[cn][0]  # 取第一条作为代表

            # 1. 跨服类型比对
            xlsx_cross = xa['cross_server']
            csv_cross = item['cross_server']

            if xlsx_cross == '单服' and csv_cross != '单服':
                results['cross_type_mismatch'].append({
                    'xlsx_name': xlsx_name,
                    'csv_name': cn,
                    'xlsx_cross': xlsx_cross,
                    'csv_cross': f"{csv_cross}({item['num_groups']}组/{item['num_servers']}服)",
                    'note': '排期=单服，上线≠单服',
                })
            elif '跨服' in xlsx_cross and csv_cross != '跨服':
                results['cross_type_mismatch'].append({
                    'xlsx_name': xlsx_name,
                    'csv_name': cn,
                    'xlsx_cross': xlsx_cross,
                    'csv_cross': f"{csv_cross}({item['num_servers']}服)",
                    'note': f'排期={xlsx_cross}，上线={csv_cross}',
                })

            # 2. 服务器数量检查
            is_s6 = 'schema6' in cn.lower() or 's6' in cn.lower()
            is_s35 = 'schema3' in cn.lower() or 's3-5' in cn.lower() or 'schema3~5' in cn.lower()
            expected = expected_server_count(xlsx_name, xa['cross_server'], is_s6, is_s35)
            actual = item['num_servers']

            if actual != expected and actual > 0:
                results['server_count_issues'].append({
                    'xlsx_name': xlsx_name,
                    'csv_name': cn,
                    'csv_id': item['id'],
                    'expected': expected,
                    'actual': actual,
                    'diff': actual - expected,
                    'is_bugui': is_bugui(xlsx_name),
                    'note': _server_count_note(xlsx_name, expected, actual, is_s6, is_s35),
                })

    # 3. Schema 分割检查
    schema_pairs = find_schema_pairs(csv_acts)
    for s6_name, s35_name in schema_pairs:
        s6_servers = csv_acts[s6_name][0]['all_servers'] if s6_name in csv_acts else set()
        s35_servers = csv_acts[s35_name][0]['all_servers'] if s35_name in csv_acts else set()

        if s6_servers and s35_servers:
            overlap = s6_servers & s35_servers
            combined = s6_servers | s35_servers
            results['schema_split_check'].append({
                's6_name': s6_name,
                's35_name': s35_name,
                's6_count': len(s6_servers),
                's35_count': len(s35_servers),
                'combined': len(combined),
                'overlap': len(overlap),
                'ok': len(overlap) == 0,
            })

    return results, ref_sets


def build_reference_server_sets(csv_acts):
    """从CSV中提取参考服务器集合"""
    ref = {'full': set(), 's6': set(), 's35': set()}

    # 找全服活动（单服 + 130服务器左右）
    for name, items in csv_acts.items():
        for item in items:
            if item['cross_server'] == '单服' and item['num_servers'] == SERVER_FULL:
                ref['full'] = item['all_servers']
                break
        if ref['full']:
            break

    # 找 schema6 参考
    for name, items in csv_acts.items():
        if 'schema6' in name.lower() or '_schema6' in name.lower():
            for item in items:
                if item['num_servers'] == SERVER_S6:
                    ref['s6'] = item['all_servers']
                    break
            if ref['s6']:
                break

    # 找 schema3-5 参考
    for name, items in csv_acts.items():
        if 'schema3' in name.lower() or 'schema3-5' in name.lower():
            for item in items:
                if item['num_servers'] == SERVER_S35:
                    ref['s35'] = item['all_servers']
                    break
            if ref['s35']:
                break

    return ref


def find_schema_pairs(csv_acts):
    """自动发现 schema6/schema3-5 配对"""
    pairs = []
    s6_names = [n for n in csv_acts if 'schema6' in n.lower() or '_schema6' in n.lower() or '-s6' in n.lower()]
    s35_names = [n for n in csv_acts if 'schema3' in n.lower() or 's3-5' in n.lower() or 'schema3~5' in n.lower()]

    for s6 in s6_names:
        # 尝试找配对的 s35
        base = s6.lower().replace('schema6', '').replace('_schema6', '').replace('-s6', '').replace('-schema6', '')
        for s35 in s35_names:
            s35_base = s35.lower().replace('schema3-5', '').replace('schema3~5', '').replace('_schema3-5', '').replace('-s3-5', '').replace('-schema3-5', '')
            if base.strip('-_ ') == s35_base.strip('-_ '):
                pairs.append((s6, s35))
                break

    return pairs


def _server_count_note(xlsx_name, expected, actual, is_s6, is_s35):
    """生成服务器数量差异说明"""
    diff = actual - expected
    if is_bugui(xlsx_name):
        if actual == SERVER_FULL:
            return f'"不灰"活动应有{SERVER_FULL_GRAY}服(含灰度)，实际只有{SERVER_FULL}，可能缺少灰度服务器'
        elif actual == SERVER_FULL_GRAY:
            return '符合"不灰"规则（全服含灰度）'
        else:
            return f'预期{expected}，实际{actual}（差{diff:+d}）'
    else:
        if actual == SERVER_FULL_GRAY:
            return f'普通活动多出{SERVER_GRAY_EXTRA}个灰度服务器，确认是否有意为之'
        else:
            return f'预期{expected}，实际{actual}（差{diff:+d}）'


# ============================================================
# 4. 命名检查
# ============================================================
def audit_naming(csv_acts, holiday_keywords):
    """检查上线表活动命名问题"""
    issues = []
    current_year = datetime.now().strftime('%Y')

    # 常见节日名称
    all_holidays = ['圣诞', '万圣', '感恩', '登月', '夏日', '春节', '新年', '中秋', '国庆', '端午', '元旦', '复活']

    # 排除当前节日关键词
    other_holidays = [h for h in all_holidays if h not in holiday_keywords]

    for name, items in csv_acts.items():
        # 检查是否包含其他节日名称
        for h in other_holidays:
            if h in name:
                issues.append({
                    'csv_name': name,
                    'ids': [it['id'] for it in items],
                    'issue': f'名称包含"{h}"，可能是旧模板',
                })
                break

        # 检查年份
        year_matches = re.findall(r'20\d{2}', name)
        for y in year_matches:
            if y != current_year:
                issues.append({
                    'csv_name': name,
                    'ids': [it['id'] for it in items],
                    'issue': f'年份为{y}，当前为{current_year}',
                })

    return issues


# ============================================================
# 主流程
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='排期审核对比工具')
    parser.add_argument('--xlsx', required=True, help='排期审核表路径(.xlsx)')
    parser.add_argument('--csv', required=True, help='正式上线表路径(.csv)')
    parser.add_argument('--mapping', required=True, help='活动映射JSON文件路径')
    parser.add_argument('--output', default='.', help='输出目录')
    parser.add_argument('--holiday', default='', help='当前节日关键词，逗号分隔（如"情人,valentine"）')
    parser.add_argument('--csv-encoding', default='gbk', help='CSV编码（默认gbk）')
    args = parser.parse_args()

    print(f"读取排期表: {args.xlsx}")
    date_map, xlsx_acts = read_xlsx(args.xlsx)
    print(f"  提取到 {len(xlsx_acts)} 个活动，{len(date_map)} 个日期列")

    print(f"读取上线表: {args.csv}")
    csv_acts = read_csv(args.csv, encoding=args.csv_encoding)
    total_csv = sum(len(v) for v in csv_acts.values())
    print(f"  提取到 {len(csv_acts)} 个唯一活动名，共 {total_csv} 条记录")

    print(f"读取映射: {args.mapping}")
    with open(args.mapping, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    print(f"  映射条目: {len(mapping)}")

    holiday_keywords = [k.strip() for k in args.holiday.split(',') if k.strip()]

    # 执行审核
    print("\n执行活动条目匹配...")
    match_results = audit_activity_matching(xlsx_acts, csv_acts, mapping)

    print("执行时间对比...")
    time_results = audit_time(xlsx_acts, csv_acts, mapping)

    print("执行服务器配置对比...")
    server_results, ref_sets = audit_servers(xlsx_acts, csv_acts, mapping)

    print("执行命名检查...")
    naming_issues = audit_naming(csv_acts, holiday_keywords)

    # 输出结果 JSON
    os.makedirs(args.output, exist_ok=True)
    output_data = {
        'meta': {
            'audit_date': datetime.now().strftime('%Y.%m.%d'),
            'xlsx_path': args.xlsx,
            'csv_path': args.csv,
            'xlsx_activity_count': len(xlsx_acts),
            'csv_unique_names': len(csv_acts),
            'csv_total_records': total_csv,
            'ref_server_sets': {
                'full': len(ref_sets['full']),
                's6': len(ref_sets['s6']),
                's35': len(ref_sets['s35']),
            },
        },
        'activity_matching': {
            'matched_count': len(match_results['matched']),
            'matched': match_results['matched'],
            'xlsx_missing_count': len(match_results['xlsx_missing']),
            'xlsx_missing': match_results['xlsx_missing'],
            'csv_missing_count': len(match_results['csv_missing']),
            'csv_missing': match_results['csv_missing'],
        },
        'time_comparison': {
            'offset_pattern': time_results['offset_pattern'],
            'with_marks': time_results['with_marks'],
            'without_marks': time_results['without_marks'],
        },
        'server_comparison': {
            'cross_type_mismatch': server_results['cross_type_mismatch'],
            'server_count_issues': server_results['server_count_issues'],
            'schema_split_check': server_results['schema_split_check'],
        },
        'naming_issues': naming_issues,
    }

    # 序列化时处理 set 类型
    output_path = os.path.join(args.output, 'audit_results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n审核结果已写入: {output_path}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("审核摘要")
    print("=" * 60)
    print(f"活动匹配: {len(match_results['matched'])} 匹配, "
          f"{len(match_results['xlsx_missing'])} 排期缺失, "
          f"{len(match_results['csv_missing'])} 上线多余")
    print(f"时间对比: {len(time_results['with_marks'])} 项有标记, "
          f"{len(time_results['without_marks'])} 项无标记")
    print(f"跨服类型不匹配: {len(server_results['cross_type_mismatch'])} 项")
    print(f"服务器数量异常: {len(server_results['server_count_issues'])} 项")
    print(f"Schema分割检查: {len(server_results['schema_split_check'])} 对")
    print(f"命名问题: {len(naming_issues)} 项")


if __name__ == '__main__':
    main()
