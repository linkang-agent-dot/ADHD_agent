# -*- coding: utf-8 -*-
"""
分析节日活动在生命周期映射表中的覆盖情况
读取两个CSV文件，找出节日（特别是科技节）相关活动的映射缺口
"""
import csv, sys, re

def load_activity_config(path):
    rows = {}
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows[int(row['A_INT_id'])] = row['S_STR_comment']
            except:
                pass
    return rows

def load_lifecycle_mapping(path):
    mapped_activity_ids = set()
    rows = []
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                act_id = int(row['A_INT_activity_id'])
                if act_id != 0:
                    mapped_activity_ids.add(act_id)
                rows.append(row)
            except:
                pass
    return mapped_activity_ids, rows

def find_unmapped_by_keyword(config, mapped_ids, keyword):
    results = []
    for act_id, comment in config.items():
        if keyword in comment:
            results.append({
                'id': act_id,
                'comment': comment,
                'mapped': act_id in mapped_ids
            })
    results.sort(key=lambda x: x['id'])
    return results

if __name__ == '__main__':
    config_path = r'c:\ADHD_agent\data\activity_config.csv'
    mapping_path = r'c:\ADHD_agent\data\lifecycle_mapping.csv'

    config = load_activity_config(config_path)
    mapped_ids, _ = load_lifecycle_mapping(mapping_path)

    keywords = sys.argv[1:] if len(sys.argv) > 1 else ['科技节']

    for kw in keywords:
        results = find_unmapped_by_keyword(config, mapped_ids, kw)
        print(f"\n{'='*60}")
        print(f"关键词: 【{kw}】  共 {len(results)} 条活动配置")
        print(f"{'='*60}")

        mapped = [r for r in results if r['mapped']]
        unmapped = [r for r in results if not r['mapped']]

        print(f"\n[OK] 已映射（{len(mapped)} 条）:")
        for r in mapped:
            print(f"   {r['id']}  {r['comment']}")

        print(f"\n[!!] 未映射（{len(unmapped)} 条）:")
        if unmapped:
            for r in unmapped:
                print(f"   {r['id']}  {r['comment']}")
        else:
            print("   全部已映射！")

    # 统计整体覆盖率
    total = len(config)
    covered = sum(1 for aid in config if aid in mapped_ids)
    print(f"\n{'='*60}")
    print(f"整体覆盖: {covered}/{total} ({covered/total*100:.1f}%)")
