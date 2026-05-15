#!/usr/bin/env python3
"""
批量换皮：读 reskin_all_activities.json，逐个活动调 activity_reskin.py
每个活动的子表新 ID 会累积到全局映射，后续活动自动引用。
"""

import json
import subprocess
import sys
import io
import os
import shutil
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR = Path(__file__).parent
RESKIN_SCRIPT = SCRIPT_DIR / 'activity_reskin.py'


def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'reskin_all_activities.json'

    with open(config_file, 'r', encoding='utf-8') as f:
        master = json.load(f)

    shared_item = master['shared_item_mapping']
    shared_activity = master['shared_activity_mapping']
    shared_text = master['shared_text_replacements']
    shared_preserve = master['shared_preserve_ids']
    activities = master['activities']

    # 全局映射只包含手动指定的 item + activity 映射，不累积子表 ID
    # 子表 ID 每个活动独立分配，避免跨活动碰撞
    global_mapping = {}
    global_mapping.update(shared_item)
    global_mapping.update(shared_activity)
    # 全局已占用的新 ID 集合：防止不同活动分配到同一个新 ID
    used_new_ids = set(global_mapping.values())

    # 合并输出目录
    merged_dir = SCRIPT_DIR / 'output_all_pioneer'
    merged_dir.mkdir(exist_ok=True)

    # 按表汇总的 TSV
    merged_tsv = {}  # {table_id: [lines]}

    total_rows = 0
    success = 0
    failed = []

    print(f"{'═' * 60}")
    print(f"  批量换皮：{len(activities)} 个活动")
    print(f"{'═' * 60}\n")

    for i, act in enumerate(activities):
        src = act['source']
        tgt = act['target']
        print(f"[{i+1}/{len(activities)}] {src} → {tgt} ({act['comment']})")

        # 生成单活动配置 JSON（含累积的全局映射）
        single_config = {
            'project': 'X2',
            'source_activity_id': src,
            'target_activity_id': tgt,
            'target_comment': act['comment'],
            'target_constant': act['constant'],
            'item_mapping': {**shared_item, **{k: v for k, v in global_mapping.items()
                                                if not k.startswith('2112')}},
            'activity_mapping': {**shared_activity, **{k: v for k, v in global_mapping.items()
                                                        if k not in shared_item}},
            'text_replacements': shared_text,
            'preserve_ids': shared_preserve
        }

        tmp_config = SCRIPT_DIR / f'_tmp_reskin_{tgt}.json'
        with open(tmp_config, 'w', encoding='utf-8') as f:
            json.dump(single_config, f, ensure_ascii=False, indent=2)

        # 运行 activity_reskin.py
        result = subprocess.run(
            [sys.executable, str(RESKIN_SCRIPT), str(tmp_config)],
            capture_output=True, encoding='utf-8', errors='replace',
            cwd=str(SCRIPT_DIR)
        )

        if result.returncode != 0:
            print(f"  ❌ 失败: {result.stderr[:200]}")
            failed.append(src)
            tmp_config.unlink(missing_ok=True)
            continue

        # 记录该活动分配的新 ID 到 used_new_ids（防止后续活动撞号）
        # 但不合并到 global_mapping（子表 ID 不跨活动共享）
        output_dir = SCRIPT_DIR / f'output_{tgt}'
        mapping_file = output_dir / 'mapping.json'
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                act_mapping = json.load(f)
            for v in act_mapping.values():
                used_new_ids.add(v)

        # 合并 TSV 文件
        act_rows = 0
        for tsv_file in output_dir.glob('*.tsv'):
            table_id = tsv_file.stem
            with open(tsv_file, 'r', encoding='utf-8') as f:
                lines = [l.rstrip('\n') for l in f if l.strip()]
            merged_tsv.setdefault(table_id, []).extend(lines)
            act_rows += len(lines)

        total_rows += act_rows
        success += 1

        # 解析 stdout 获取关键信息
        for line in result.stdout.split('\n'):
            if '自动分配' in line or '残留' in line or '完成' in line:
                print(f"  {line.strip()}")

        # 清理临时文件
        tmp_config.unlink(missing_ok=True)
        print()

    # 输出合并 TSV
    print(f"\n{'═' * 60}")
    print(f"  合并输出")
    print(f"{'═' * 60}\n")

    for table_id, lines in sorted(merged_tsv.items()):
        out_file = merged_dir / f'{table_id}.tsv'
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        print(f"  {table_id}.tsv: {len(lines)} 行")

    # 输出全局映射
    global_mapping_file = merged_dir / 'global_mapping.json'
    with open(global_mapping_file, 'w', encoding='utf-8') as f:
        json.dump(global_mapping, f, ensure_ascii=False, indent=2)

    # 汇总
    print(f"\n{'═' * 60}")
    print(f"  ✅ 完成: {success}/{len(activities)} 活动成功")
    if failed:
        print(f"  ❌ 失败: {failed}")
    print(f"  📊 总行数: {total_rows}")
    print(f"  📁 输出: {merged_dir}")
    print(f"  🗺️ 全局映射: {global_mapping_file} ({len(global_mapping)} 项)")
    print(f"{'═' * 60}")


if __name__ == '__main__':
    main()
