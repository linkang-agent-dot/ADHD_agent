#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排期审核报告生成器 - 基于 audit_results.json 生成 markdown 报告
用法: python report_generator.py --input <audit_results.json> --output <报告.md> --holiday <节日名>
"""
import argparse
import json
import os
from datetime import datetime


def generate_report(data, holiday_name='节日'):
    """生成 markdown 格式的审核报告"""
    lines = []
    meta = data['meta']
    matching = data['activity_matching']
    time_comp = data['time_comparison']
    server_comp = data['server_comparison']
    naming = data['naming_issues']

    # 标题
    lines.append(f'# {holiday_name}活动 - 排期审核 vs 正式上线 总结报告')
    lines.append('')
    lines.append(f'> 审核日期：{meta["audit_date"]}')
    lines.append(f'> 数据来源：排期审核表(xlsx) vs 正式上线表(csv)')
    lines.append('')
    lines.append('---')
    lines.append('')

    # 一、总览
    lines.append('## 一、总览')
    lines.append('')
    lines.append('| 维度 | 排期审核表 | 正式上线表 | 说明 |')
    lines.append('|------|-----------|-----------|------|')
    lines.append(f'| 活动数 | {meta["xlsx_activity_count"]}项 | '
                 f'{meta["csv_total_records"]}条记录(去重后{meta["csv_unique_names"]}个唯一活动名) | '
                 f'上线表含多期拆分 |')
    ref = meta.get('ref_server_sets', {})
    lines.append(f'| 服务器 | 全服{ref.get("full", "?")} / 含灰度? | '
                 f'S6:{ref.get("s6", "?")} + S3-5:{ref.get("s35", "?")} = '
                 f'{ref.get("s6", 0) + ref.get("s35", 0)}(全服) | |')
    lines.append('')
    lines.append('---')
    lines.append('')

    # 二、活动条目匹配
    lines.append(f'## 二、活动条目匹配（{meta["xlsx_activity_count"]}项排期 vs 上线表）')
    lines.append('')

    # 已匹配
    lines.append(f'### ✅ 已匹配：{matching["matched_count"]}项')
    lines.append('')
    if matching['matched']:
        lines.append('| # | 排期审核表 | 负责人 | 正式上线表 | 上线条数 |')
        lines.append('|---|-----------|--------|-----------|---------|')
        for i, m in enumerate(matching['matched'], 1):
            csv_desc = _format_csv_items(m['csv_items'])
            lines.append(f'| {i} | {m["xlsx_name"]} | {m["person"]} | {csv_desc} | {m["csv_count"]} |')
        lines.append('')

    # 排期有但上线缺失
    if matching['xlsx_missing']:
        lines.append(f'### ❌ 排期表有但上线表缺失：{matching["xlsx_missing_count"]}项')
        lines.append('')
        lines.append('| # | 活动 | 负责人 | 说明 |')
        lines.append('|---|------|--------|------|')
        for i, m in enumerate(matching['xlsx_missing'], 1):
            lines.append(f'| {i} | **{m["name"]}** | {m["person"]} | {m["note"]} |')
        lines.append('')

    # 上线有但排期缺失
    if matching['csv_missing']:
        lines.append(f'### ❌ 上线表有但排期表缺失：{matching["csv_missing_count"]}项')
        lines.append('')
        lines.append('| 活动 | 上线条数 | 活动ID | 说明 |')
        lines.append('|------|---------|--------|------|')
        for m in matching['csv_missing']:
            ids_str = '/'.join(str(i) for i in m['ids'][:5])
            if len(m['ids']) > 5:
                ids_str += '...'
            lines.append(f'| **{m["name"]}** | {m["count"]}条 | {ids_str} | 排期表无此活动 |')
        lines.append('')

    lines.append('---')
    lines.append('')

    # 三、上线时间对比
    lines.append('## 三、上线时间对比')
    lines.append('')
    lines.append('### 规律发现')
    lines.append('')
    lines.append(f'排期标记日 = 部署操作日，实际上线 = 标记日 {time_comp["offset_pattern"]}')
    lines.append('')

    if time_comp['with_marks']:
        lines.append('### 有日期标记的活动逐期比对')
        lines.append('')
        for item in time_comp['with_marks']:
            lines.append(f'#### {item["xlsx_name"]}（负责人: {item["person"]}）')
            lines.append('')
            lines.append(f'排期标记: {", ".join(item["mark_details"])}')
            lines.append('')
            lines.append('| 上线活动 | ID | 上线时间 | 时长 | 比对结果 |')
            lines.append('|---------|-----|---------|------|---------|')
            for c in item['comparisons']:
                start_short = c['csv_start'][:16] if c['csv_start'] else ''
                end_short = c['csv_end'][:16] if c['csv_end'] else ''
                lines.append(f'| {c["csv_name"]} | {c["csv_id"]} | {start_short}~{end_short} | '
                             f'{c["csv_duration"]} | {c["result"]} |')
            lines.append('')

    if time_comp['without_marks']:
        lines.append('### 无日期标记的活动（仅列出上线时间）')
        lines.append('')
        lines.append('| 排期活动 | 上线活动 | ID | 上线时间 | 时长 |')
        lines.append('|---------|---------|-----|---------|------|')
        for item in time_comp['without_marks']:
            start_short = item['start'][:16] if item['start'] else ''
            end_short = item['end'][:16] if item['end'] else ''
            lines.append(f'| {item["xlsx_name"]} | {item["csv_name"]} | {item["csv_id"]} | '
                         f'{start_short}~{end_short} | {item["duration"]} |')
        lines.append('')

    lines.append('---')
    lines.append('')

    # 四、服务器配置对比
    lines.append('## 四、服务器配置对比')
    lines.append('')

    if server_comp['cross_type_mismatch']:
        lines.append(f'### 跨服类型不匹配：{len(server_comp["cross_type_mismatch"])}项')
        lines.append('')
        lines.append('| # | 排期活动 | 上线活动 | 排期标注 | 上线实际 | 说明 |')
        lines.append('|---|---------|---------|---------|---------|------|')
        for i, m in enumerate(server_comp['cross_type_mismatch'], 1):
            lines.append(f'| {i} | {m["xlsx_name"]} | {m["csv_name"]} | {m["xlsx_cross"]} | '
                         f'{m["csv_cross"]} | {m["note"]} |')
        lines.append('')

    if server_comp['server_count_issues']:
        lines.append(f'### 服务器数量异常：{len(server_comp["server_count_issues"])}项')
        lines.append('')
        lines.append('| # | 活动 | ID | 预期 | 实际 | 差异 | 说明 |')
        lines.append('|---|------|----|------|------|------|------|')
        for i, m in enumerate(server_comp['server_count_issues'], 1):
            lines.append(f'| {i} | {m["csv_name"]} | {m["csv_id"]} | {m["expected"]} | '
                         f'{m["actual"]} | {m["diff"]:+d} | {m["note"]} |')
        lines.append('')

    if server_comp['schema_split_check']:
        all_ok = all(s['ok'] for s in server_comp['schema_split_check'])
        status = '全部通过 ✅' if all_ok else '存在问题 ❌'
        lines.append(f'### Schema 分割完整性：{status}')
        lines.append('')
        lines.append('| Schema6 活动 | Schema3-5 活动 | S6服务器 | S35服务器 | 合计 | 重叠 | 结果 |')
        lines.append('|-------------|---------------|---------|----------|------|------|------|')
        for s in server_comp['schema_split_check']:
            result = '✅ 无重叠' if s['ok'] else f'❌ 重叠{s["overlap"]}个'
            lines.append(f'| {s["s6_name"]} | {s["s35_name"]} | {s["s6_count"]} | '
                         f'{s["s35_count"]} | {s["combined"]} | {s["overlap"]} | {result} |')
        lines.append('')

    lines.append('---')
    lines.append('')

    # 五、活动命名问题
    if naming:
        lines.append('## 五、活动命名问题')
        lines.append('')
        lines.append('| 上线表活动名 | ID | 问题 |')
        lines.append('|-------------|-----|------|')
        for n in naming:
            ids_str = '/'.join(str(i) for i in n['ids'][:3])
            lines.append(f'| **{n["csv_name"]}** | {ids_str} | {n["issue"]} |')
        lines.append('')
        lines.append('---')
        lines.append('')

    # 六、待确认事项清单
    lines.append('## 六、待确认事项清单')
    lines.append('')
    todo_items = _generate_todo_list(matching, server_comp, naming)
    if todo_items:
        lines.append('| 序号 | 优先级 | 事项 | 说明 |')
        lines.append('|------|--------|------|------|')
        for i, t in enumerate(todo_items, 1):
            lines.append(f'| {i} | {t["priority"]} | {t["item"]} | {t["note"]} |')
    else:
        lines.append('无待确认事项。')
    lines.append('')

    return '\n'.join(lines)


def _format_csv_items(items):
    """格式化 CSV 匹配项目"""
    if len(items) <= 2:
        return ' + '.join(f'{it["csv_name"]}({it["id"]})' for it in items)
    else:
        first = f'{items[0]["csv_name"]}({items[0]["id"]})'
        return f'{first} 等{len(items)}条'


def _generate_todo_list(matching, server_comp, naming):
    """自动生成待确认事项"""
    todos = []

    # 高优先级：排期表有但上线缺失
    for m in matching['xlsx_missing']:
        todos.append({
            'priority': '🔴高',
            'item': f'**{m["name"]}** 排期表有但上线表缺失',
            'note': m['note'],
        })

    # 高优先级：上线有但排期缺失
    for m in matching['csv_missing']:
        if m['count'] >= 3:  # 多条记录更严重
            todos.append({
                'priority': '🔴高',
                'item': f'**{m["name"]}** ({m["count"]}条) 上线表有但排期表缺失',
                'note': '是否遗漏审核？',
            })

    # 中优先级：跨服类型不匹配
    if server_comp['cross_type_mismatch']:
        todos.append({
            'priority': '🟡中',
            'item': f'{len(server_comp["cross_type_mismatch"])}项活动**跨服类型不匹配**',
            'note': '确认排期表描述或上线配置哪个正确',
        })

    # 中优先级：服务器数量异常
    if server_comp['server_count_issues']:
        todos.append({
            'priority': '🟡中',
            'item': f'{len(server_comp["server_count_issues"])}项活动**服务器数量异常**',
            'note': '确认是否有意为之',
        })

    # 低优先级：命名问题
    if naming:
        todos.append({
            'priority': '🟢低',
            'item': f'{len(naming)}个活动名称可能有误',
            'note': '沿用旧节日名称或年份错误',
        })

    return todos


def main():
    parser = argparse.ArgumentParser(description='排期审核报告生成器')
    parser.add_argument('--input', required=True, help='audit_results.json 路径')
    parser.add_argument('--output', required=True, help='输出报告路径(.md)')
    parser.add_argument('--holiday', default='节日', help='节日名称（如"2026情人节"）')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    report = generate_report(data, args.holiday)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f'报告已生成: {args.output}')


if __name__ == '__main__':
    main()
