#!/usr/bin/env python3
"""
活动换皮自动化脚本
从源活动出发，自动追踪子表链路，克隆并替换 ID，输出 TSV。

用法：
  python activity_reskin.py config.json           # dry-run: 只输出文件
  python activity_reskin.py config.json --write    # 写入 GSheet
"""

import json
import re
import subprocess
import sys
import io
import os
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── 路径 ──
SCRIPT_DIR = Path(__file__).parent
QUERY_TOOL = SCRIPT_DIR.parent.parent / 'google-workspace-cli' / 'gsheet_query.py'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'

# ── X2 表别名 → SheetID（核心表）──
X2_TABLES = {
    '2112': {'alias': '2112_x2_activity_config', 'id_col': 1, 'tab': None},
    '2135': {'alias': '2135_x2_activity_package', 'id_col': 1, 'tab': 'activity_event_pkg（qa）'},
    '2011': {'alias': '2011_x2_iap_config', 'id_col': 1, 'tab': None},
    '2013': {'alias': '2013_x2_iap_template', 'id_col': 1, 'tab': None},
    '2121': {'alias': '2121_x2_activity_special', 'id_col': 1, 'tab': None},
    '2115': {'alias': '2115_x2_activity_task', 'id_col': 2, 'tab': 'activity_task_master（27装备打造bingo）'},
    '2116': {'alias': '2116_x2_activity_item_exchange', 'id_col': 2, 'tab': None},
    '2124': {'alias': '2124_x2_activity_drop', 'id_col': 1, 'tab': None},
    '2137': {'alias': '2137_x2_activity_asset_retake', 'id_col': 1, 'tab': None},
    '2122': {'alias': '2122_x2_activity_rank_rule', 'id_col': 2, 'tab': None},
    '2118': {'alias': '2118_x2_activity_rank_rewards', 'id_col': 3, 'tab': None},
}

# 组件 typ → 子表编号
COMPONENT_TABLE_MAP = {
    'task': '2115', 'task_group': '2121', 'package': '2135',
    'exchange': '2116', 'drop': '2124', 'rank': '2122',
    'retake': '2137', 'buff': '2121', 'jump_link': '2121',
    'weekly_pay_ratio': '2121', 'festival_wonder': '2121',
    'wonder_hero_display': '2121', 'wonder_egg_drop': '2121',
    'flash_sale_buy_duration': '2121', 'flash_sale_gacha': '2121',
    'flash_sale_popup': '2121', 'flash_sale_raffle': '2121',
    'flash_sale_buy_opentime': '2121', 'discount': '2121',
    'emoji_show': '2121', 'actv_links': '2121',
    'drop_topay_show': '2121', 'drop_topay': '2121',
    'new_progress': '2121', 'cost': '2121',
    'multi_gacha': '2121', 'show_probability': '2121',
    'broadcast_bubble': '2121', 'item_red_point': '2121',
    'actv_show_rank': '2121', 'tech_lucky_reward': '2121',
    'tech_lucky_cost': '2121', 'server_recharge_countdown': '2121',
    'statue_preview': '2121', 'monopoly_piggy_bank': '2121',
    'actv_growth_invest': '2121', 'quest_reward_require': '2121',
    '7days_happy': '2121', 'score_limit': '2121',
    'hero_display': '2121', 'iap_show': None,
    'mecha_skin_select': None, 'battle_pass': '2130',
    'bp_rank_item': None, 'fes_module': None,
    'create_entity': None, 'monopoly_gacha_map': None,
    'monopoly_gacha_dice': None, 'login_complement': '2121',
    'search_nun': None, 'union_ipo': None,
    # A3: 补全追踪链
    'wonder_egg_drop_target': '2124',  # wonder_egg_drop 的 expr 内含 2124 drop ID
    'fes_card_gallary': '2121',
}

# A3: 深层追踪链（从子表发现更深的引用）
# battle_pass → 2130 → 2131, rank → 2122 → 2118
DEEP_CHAIN = {
    '2130': '2131',   # BP通行证 → BP等级奖励（通过 BpID 关联）
    '2122': '2118',   # 排名规则 → 排名奖励（通过 rank_components 关联）
}


def run_query(alias: str, command: str, *args, retries: int = 2) -> str:
    """调用 gsheet_query.py，返回 stdout。失败时自动重试。"""
    cmd = [sys.executable, str(QUERY_TOOL), command, alias] + list(args)
    for attempt in range(retries + 1):
        result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace',
                                cwd=str(QUERY_TOOL.parent))
        if result.returncode == 0:
            return result.stdout
        if attempt < retries:
            import time
            time.sleep(1.5)  # API 限流等待
    print(f"  ⚠️ query 失败({retries+1}次): {' '.join(cmd[-4:])}", file=sys.stderr)
    print(f"     {result.stderr[:200]}", file=sys.stderr)
    return ''


def get_table_args(table_id: str) -> List[str]:
    """获取表专属参数（--id-col, --tab）"""
    info = X2_TABLES.get(table_id, {})
    args = []
    id_col = info.get('id_col', 1)
    if id_col != 1:  # gsheet_query 默认 id_col=1 (P2 auto-shift)
        args.extend(['--id-col', str(id_col)])
    tab = info.get('tab')
    if tab:
        args.extend(['--tab', tab])
    return args


def read_raw_rows(alias: str, id_min: str, id_max: str, extra_args: List[str] = None) -> List[List[str]]:
    """用 idrange 读原始行（Tab 分隔），返回 [[cell, ...], ...]"""
    args = [id_min, id_max]
    if extra_args:
        args.extend(extra_args)
    raw = run_query(alias, 'idrange', *args)
    rows = []
    for line in raw.split('\n'):
        line = line.strip()
        if not line or line.startswith('[info]') or line.startswith('HEADER') or line.startswith('Found'):
            continue
        if line.startswith('row '):
            # 格式: "row NNN: \tval1\tval2\t..."
            idx = line.find(':\t')
            if idx >= 0:
                row_data = line[idx + 1:]  # 含前导 \t
            else:
                idx2 = line.find(': ')
                row_data = line[idx2 + 2:] if idx2 >= 0 else line
            cells = row_data.split('\t')
            rows.append(cells)
    return rows


def read_single_row(alias: str, row_id: str, extra_args: List[str] = None) -> List[str]:
    """读单行"""
    rows = read_raw_rows(alias, row_id, row_id, extra_args)
    return rows[0] if rows else []


def get_tail_max_id(alias: str, n: int = 5, id_col: int = 1, table_id: str = None) -> int:
    """获取表尾部最大 ID"""
    # tail 只支持 --tab，不支持 --id-col
    tab_args = []
    if table_id:
        info = X2_TABLES.get(table_id, {})
        tab = info.get('tab')
        if tab:
            tab_args = ['--tab', tab]
    raw = run_query(alias, 'tail', str(n), *tab_args)
    max_id = 0
    for line in raw.split('\n'):
        if line.startswith('row '):
            idx = line.find(':\t')
            if idx < 0:
                idx = line.find(': ')
            if idx >= 0:
                cells = line[idx + 1:].split('\t') if ':\t' in line else line[idx + 2:].split('\t')
                if len(cells) > id_col:
                    try:
                        val = int(cells[id_col].strip())
                        max_id = max(max_id, val)
                    except (ValueError, IndexError):
                        pass
    return max_id


def do_replace(cell: str, replacements: Dict[str, str]) -> Tuple[str, bool]:
    """精确边界替换（数字 ID 不会部分匹配）
    防链式替换：先用占位符替换所有匹配，再统一还原为目标值。
    """
    if not cell:
        return cell, False
    # 按 key 长度降序排列，优先匹配更长的 ID（防止短 ID 误匹配长 ID 的子串）
    sorted_items = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
    # Phase 1: 所有匹配替换为占位符 __PLACEHOLDER_N__
    placeholders = {}
    new_cell = cell
    for i, (old_val, new_val) in enumerate(sorted_items):
        ph = f'__PH{i}__'
        placeholders[ph] = new_val
        pattern = r'(?<![0-9])' + re.escape(old_val) + r'(?![0-9])'
        new_cell = re.sub(pattern, ph, new_cell)
    # Phase 2: 占位符还原为目标值
    for ph, new_val in placeholders.items():
        new_cell = new_cell.replace(ph, new_val)
    return new_cell, new_cell != cell


def parse_components(components_json: str) -> Dict[str, List[str]]:
    """解析 2112 components JSON，返回 {typ: [id_str, ...]}"""
    result = {}
    try:
        components = json.loads(components_json)
    except (json.JSONDecodeError, TypeError):
        return result
    for comp in components:
        typ = comp.get('typ', '')
        cid = str(comp.get('id', ''))
        if typ and cid and cid != '0':
            result.setdefault(typ, []).append(cid)
    return result


def discover_sub_ids(alias: str, row_ids: List[str], table_id: str,
                     extra_args: List[str] = None) -> Dict[str, List[str]]:
    """读子表行，发现更深层引用。返回 {deeper_table: [ids]}"""
    deeper = {}

    for rid in row_ids:
        row = read_single_row(alias, rid, extra_args)
        if not row:
            continue
        row_text = '\t'.join(row)

        # 2135 → 取 iap 列（col[3] 通常是 A_INT_iap）
        if table_id == '2135':
            # iap 列：找包含 2011 前缀的数字
            for cell in row:
                cell = cell.strip()
                if cell.startswith('2011') and cell.isdigit():
                    deeper.setdefault('2011', []).append(cell)

        # 2011 → 在整行中搜索 2013 ID
        elif table_id == '2011':
            for m in re.finditer(r'(?<![0-9])(2013\d{6,})(?![0-9])', row_text):
                deeper.setdefault('2013', []).append(m.group(1))

    return deeper


def clone_rows(source_rows: List[List[str]], full_mapping: Dict[str, str],
               text_replacements: Dict[str, str],
               comment_col: int = 2, constant_col: int = 3,
               target_comment: str = None, target_constant: str = None,
               is_primary: bool = False,
               preserve_cols: List[int] = None) -> List[List[str]]:
    """克隆多行，应用 ID 替换 + 文本替换
    preserve_cols: 这些列保持源值不做任何替换（如 base_activity_id）
    """
    preserve_cols = preserve_cols or []
    cloned = []
    for row in source_rows:
        new_row = []
        for i, cell in enumerate(row):
            if i in preserve_cols:
                # 保持原值
                new_row.append(cell)
                continue
            # ID 替换
            new_cell, _ = do_replace(cell, full_mapping)
            # 文本替换（comment 和所有文本列）
            for old_txt, new_txt in text_replacements.items():
                new_cell = new_cell.replace(old_txt, new_txt)
            new_row.append(new_cell)

        # 主活动行：覆盖 comment 和 constant
        if is_primary and target_comment and len(new_row) > comment_col:
            new_row[comment_col] = target_comment
        if is_primary and target_constant and len(new_row) > constant_col:
            new_row[constant_col] = target_constant

        cloned.append(new_row)
    return cloned


def main():
    parser = argparse.ArgumentParser(description='活动换皮自动化')
    parser.add_argument('config', help='换皮配置 JSON')
    parser.add_argument('--write', action='store_true', help='写入 GSheet（默认 dry-run）')
    args = parser.parse_args()

    # ── 读配置 ──
    with open(args.config, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    source_id = str(cfg['source_activity_id'])
    target_id = str(cfg['target_activity_id'])
    item_mapping = {str(k): str(v) for k, v in cfg.get('item_mapping', {}).items()}
    activity_mapping = {str(k): str(v) for k, v in cfg.get('activity_mapping', {}).items()}
    text_replacements = cfg.get('text_replacements', {})
    preserve_ids = set(str(x) for x in cfg.get('preserve_ids', []))
    # A2: 复用旧组件的类型列表 — 这些 typ 的子表不新建，2112 components 保留源 ID
    reuse_types = set(cfg.get('reuse_types', []))

    # 输出目录
    output_dir = Path(f'output_{target_id}')
    output_dir.mkdir(exist_ok=True)

    print(f"═══ 活动换皮: {source_id} → {target_id} ═══\n")

    # ── Step 1: 读源 2112 行 ──
    print("Step 1: 读源活动...")
    alias_2112 = X2_TABLES['2112']['alias']
    source_row = read_single_row(alias_2112, source_id, get_table_args('2112'))
    if not source_row:
        print(f"❌ 找不到源活动 {source_id}")
        sys.exit(1)
    print(f"  ✓ 2112 row {source_id} ({len(source_row)} 列)")

    # 解析 components（col[9]）
    components_col = 9
    if len(source_row) > components_col:
        components = parse_components(source_row[components_col])
    else:
        components = {}
    print(f"  ✓ 发现 {sum(len(v) for v in components.values())} 个组件，{len(components)} 种类型")
    for typ, ids in components.items():
        table = COMPONENT_TABLE_MAP.get(typ, '?')
        print(f"    {typ} → 表{table}: {ids}")

    # ── Step 2: 追踪子表 ──
    print("\nStep 2: 追踪子表链路...")
    chain = {}  # {table_id: [row_ids]}

    # 记录复用组件的旧 ID（用于 2112 components 恢复）
    reuse_old_ids = {}  # {typ: [old_ids]}
    for typ, ids in components.items():
        if typ in reuse_types:
            reuse_old_ids[typ] = ids
            print(f"    {typ}: 复用旧 ID {ids}")
            continue
        table = COMPONENT_TABLE_MAP.get(typ)
        if table and table in X2_TABLES:
            chain.setdefault(table, []).extend(ids)

    # 去重
    for t in chain:
        chain[t] = sorted(set(chain[t]))

    # 读 2135 → 发现 2011（批量读，只保留 chain 中的目标行）
    if '2135' in chain:
        alias_2135 = X2_TABLES['2135']['alias']
        args_2135 = get_table_args('2135')
        id_col_2135 = X2_TABLES['2135'].get('id_col', 1)
        target_2135 = set(chain['2135'])
        deeper_from_2135 = {}
        int_ids = sorted(int(x) for x in chain['2135'])
        all_2135 = read_raw_rows(alias_2135, str(int_ids[0]), str(int_ids[-1]), args_2135)
        for row in all_2135:
            # 只处理目标 ID 的行
            if len(row) > id_col_2135 and row[id_col_2135].strip() in target_2135:
                for cell in row:
                    cell = cell.strip()
                    if re.match(r'^2011\d+$', cell):
                        deeper_from_2135.setdefault('2011', []).append(cell)
        for t, ids in deeper_from_2135.items():
            chain.setdefault(t, []).extend(ids)
            chain[t] = sorted(set(chain[t]))
        print(f"  ✓ 2135 → 发现 2011: {deeper_from_2135.get('2011', [])}")

    # 读 2011 → 发现 2013（两种方式）
    if '2011' in chain:
        alias_2011 = X2_TABLES['2011']['alias']
        args_2011 = get_table_args('2011')
        deeper_from_2011 = {}

        # 方式1: 正向 — 批量读 2011，只保留 chain 中的目标行
        id_col_2011 = X2_TABLES['2011'].get('id_col', 1)
        target_2011 = set(chain['2011'])
        int_2011 = sorted(int(x) for x in chain['2011'])
        all_2011 = read_raw_rows(alias_2011, str(int_2011[0]), str(int_2011[-1]), args_2011)
        for row in all_2011:
            if len(row) > id_col_2011 and row[id_col_2011].strip() in target_2011:
                row_text = '\t'.join(row)
                for m in re.finditer(r'(?<![0-9])(2013\d{6,})(?![0-9])', row_text):
                    deeper_from_2011.setdefault('2013', []).append(m.group(1))

        # 方式2: 反向 — 在 2013 表中搜索 config_id = 源 2011 ID
        alias_2013 = X2_TABLES['2013']['alias']
        args_2013 = get_table_args('2013')
        for source_2011_id in chain['2011']:
            raw = run_query(alias_2013, 'search', source_2011_id,
                            *(args_2013 if args_2013 else []))
            # 从 search 输出中提取 2013 ID（用正则匹配 2013 开头的数字）
            for line in raw.split('\n'):
                if line.startswith('row '):
                    # 在整行中搜索 2013xxxxxx 格式的 ID
                    for m in re.finditer(r'(?<![0-9])(2013\d{6,})(?![0-9])', line):
                        deeper_from_2011.setdefault('2013', []).append(m.group(1))

        for t, ids in deeper_from_2011.items():
            chain.setdefault(t, []).extend(ids)
            chain[t] = sorted(set(chain[t]))
        print(f"  ✓ 2011 → 发现 2013: {deeper_from_2011.get('2013', [])}")

    print(f"\n  链路汇总:")
    for t, ids in sorted(chain.items()):
        print(f"    表{t}: {len(ids)} 行 — {ids[:5]}{'...' if len(ids) > 5 else ''}")

    # ── Step 3: 分配新 ID ──
    print("\nStep 3: 分配新 ID...")
    full_mapping = {}
    full_mapping.update(item_mapping)
    full_mapping.update(activity_mapping)

    # 子表 ID：已在 manual_mapping 中的用手动值，否则自动分配
    # next_id_overrides: 外先从全局文件读，再用配置覆盖
    global_next_file = Path('_global_next_ids.json')
    next_id_overrides = {}
    if global_next_file.exists():
        with open(global_next_file, 'r', encoding='utf-8') as f:
            next_id_overrides = {k: str(v) for k, v in json.load(f).items()}
    # 配置文件的 overrides 优先级更高
    next_id_overrides.update(cfg.get('next_id_overrides', {}))
    auto_assigned = {}
    next_id_after = {}  # 记录各表分配后的 next_id，传回给调用方
    for table_id, row_ids in chain.items():
        table_info = X2_TABLES.get(table_id, {})
        alias = table_info.get('alias')
        if not alias:
            continue

        # 获取起始 ID：优先用外部传入的 override，否则查 tail
        if table_id in next_id_overrides:
            next_id = int(next_id_overrides[table_id])
        else:
            id_col = table_info.get('id_col', 1)
            max_existing = get_tail_max_id(alias, n=10, id_col=id_col, table_id=table_id)
            next_id = max_existing + 1

        for rid in row_ids:
            if rid in full_mapping:
                continue
            if rid in preserve_ids:
                continue

            new_id = str(next_id)
            full_mapping[rid] = new_id
            auto_assigned[rid] = f"{new_id} (表{table_id})"
            next_id += 1

        next_id_after[table_id] = next_id

    print(f"  ✓ 手动映射: {len(item_mapping) + len(activity_mapping)} 项")
    print(f"  ✓ 自动分配: {len(auto_assigned)} 项")
    for old_id, desc in auto_assigned.items():
        print(f"    {old_id} → {desc}")

    # 保存完整映射 + next_id 供下一个活动使用
    mapping_file = output_dir / 'mapping.json'
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(full_mapping, f, ensure_ascii=False, indent=2)

    next_id_file = output_dir / 'next_ids.json'
    with open(next_id_file, 'w', encoding='utf-8') as f:
        json.dump(next_id_after, f, ensure_ascii=False, indent=2)

    # A4: 更新全局 next_ids 文件（手动补配后也要更新这个文件）
    global_next_file = Path(SCRIPT_DIR) / '_global_next_ids.json' if 'SCRIPT_DIR' in dir() else Path('_global_next_ids.json')
    global_next = {}
    if global_next_file.exists():
        with open(global_next_file, 'r', encoding='utf-8') as f:
            global_next = json.load(f)
    for t, v in next_id_after.items():
        global_next[t] = max(int(global_next.get(t, 0)), v)
    with open(global_next_file, 'w', encoding='utf-8') as f:
        json.dump(global_next, f, ensure_ascii=False, indent=2)

    print(f"\n  ✓ 映射表已保存: {mapping_file}")
    print(f"  ✓ 全局 next_ids 已更新: {global_next_file}")
    print(f"  ✓ next_id 已保存: {next_id_file}")

    # ── Step 4: 克隆输出 ──
    print("\nStep 4: 克隆并输出...")

    all_outputs = {}  # {table_id: [rows]}
    residual_old_ids = set()  # 残留旧 ID 检测

    # 4a: 克隆 2112 主活动行
    # col[6] = base_activity_id，保持源值不替换
    cloned_2112 = clone_rows(
        [source_row], full_mapping, text_replacements,
        comment_col=2, constant_col=3,
        target_comment=cfg.get('target_comment'),
        target_constant=cfg.get('target_constant'),
        is_primary=True,
        preserve_cols=[6]
    )
    # A2: 恢复 reuse_types 的旧 ID — 在 2112 components 中把被替换的 ID 改回源值
    if reuse_types and cloned_2112:
        import json as _json
        comp_col = 9  # components 列
        if len(cloned_2112[0]) > comp_col:
            try:
                comps = _json.loads(cloned_2112[0][comp_col])
                type_counters = {}
                for c in comps:
                    typ = c.get('typ', '')
                    if typ in reuse_old_ids and 'id' in c:
                        idx = type_counters.get(typ, 0)
                        old_ids = reuse_old_ids[typ]
                        if idx < len(old_ids):
                            c['id'] = old_ids[idx]
                            type_counters[typ] = idx + 1
                cloned_2112[0][comp_col] = _json.dumps(comps, ensure_ascii=False, separators=(',', ':'))
            except (_json.JSONDecodeError, IndexError):
                pass

    all_outputs['2112'] = cloned_2112
    print(f"  ✓ 2112: {len(cloned_2112)} 行")

    # 4b: 克隆各子表（批量读取，减少 API 调用）
    for table_id, row_ids in sorted(chain.items()):
        table_info = X2_TABLES.get(table_id, {})
        alias = table_info.get('alias')
        if not alias:
            print(f"  ⚠️ 表{table_id} 无别名，跳过")
            continue

        extra_args = get_table_args(table_id)
        id_col_idx = table_info.get('id_col', 1)

        # 过滤掉 preserve
        target_ids = [rid for rid in row_ids if rid not in preserve_ids]
        if not target_ids:
            continue

        # 批量读：如果 ID 连续（跨度 < 实际数×3），用 idrange 一次拉；否则分段读
        int_ids = sorted(int(x) for x in target_ids)
        id_span = int_ids[-1] - int_ids[0] + 1
        all_rows_raw = []
        if id_span <= len(int_ids) * 3:
            # 连续：一次 idrange
            all_rows_raw = read_raw_rows(alias, str(int_ids[0]), str(int_ids[-1]), extra_args)
        else:
            # 分散：按连续段分组读取
            segments = []
            seg_start = int_ids[0]
            seg_prev = int_ids[0]
            for iid in int_ids[1:]:
                if iid - seg_prev > 100:  # 间隔超过100视为新段
                    segments.append((seg_start, seg_prev))
                    seg_start = iid
                seg_prev = iid
            segments.append((seg_start, seg_prev))
            print(f"    ID 分散（跨度{id_span} vs 实际{len(int_ids)}），分{len(segments)}段读取")
            for s, e in segments:
                all_rows_raw.extend(read_raw_rows(alias, str(s), str(e), extra_args))

        # 按 ID 列建索引
        row_by_id = {}
        for r in all_rows_raw:
            if len(r) > id_col_idx:
                rid = r[id_col_idx].strip()
                row_by_id[rid] = r

        rows = []
        for rid in target_ids:
            if rid in row_by_id:
                rows.append(row_by_id[rid])
            else:
                print(f"  ⚠️ 表{table_id} row {rid} 未找到（源行可能不存在）")

        if rows:
            cloned = clone_rows(rows, full_mapping, text_replacements)
            all_outputs[table_id] = cloned
            print(f"  ✓ 表{table_id}: {len(cloned)} 行")
        else:
            print(f"  ⚠️ 表{table_id}: 无有效行")

    # ── 输出 TSV 文件 ──
    print(f"\n输出目录: {output_dir}")
    total_rows = 0
    for table_id, rows in sorted(all_outputs.items()):
        tsv_file = output_dir / f'{table_id}.tsv'
        with open(tsv_file, 'w', encoding='utf-8') as f:
            for row in rows:
                f.write('\t'.join(row) + '\n')
        total_rows += len(rows)
        print(f"  {tsv_file.name}: {len(rows)} 行")

    # ── 残留旧 ID 扫描 ──
    print(f"\n残留旧 ID 扫描...")
    # 检查源活动 ID 和核心道具 ID 是否残留
    check_ids = [source_id] + list(item_mapping.keys()) + list(activity_mapping.keys())
    # 2112 的 base_activity_id (col[6]) 故意保留旧 ID，不算残留
    # 收集 preserve_cols 中保留的旧值
    preserved_values = set()
    if all_outputs.get('2112') and source_row:
        preserved_values.add(source_row[6].strip())  # base_activity_id 原值
    found_residual = False
    for table_id, rows in all_outputs.items():
        for row_idx, row in enumerate(rows):
            row_text = '\t'.join(row)
            for check_id in check_ids:
                if check_id in full_mapping and check_id not in preserved_values and \
                   re.search(r'(?<![0-9])' + re.escape(check_id) + r'(?![0-9])', row_text):
                    if check_id not in preserve_ids:
                        print(f"  ⚠️ 表{table_id} 行{row_idx}: 残留旧 ID {check_id}")
                        found_residual = True

    if not found_residual:
        print(f"  ✅ 无残留旧 ID")

    # ── 汇总 ──
    summary_file = output_dir / 'summary.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"活动换皮: {source_id} → {target_id}\n")
        f.write(f"生成日期: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"总计 {total_rows} 行，涉及 {len(all_outputs)} 张表：\n")
        for tid, rows in sorted(all_outputs.items()):
            f.write(f"  表{tid}: {len(rows)} 行\n")
        f.write(f"\nID 映射（{len(full_mapping)} 项）:\n")
        for old, new in sorted(full_mapping.items(), key=lambda x: x[0]):
            f.write(f"  {old} → {new}\n")
        f.write(f"\n残留旧 ID: {'有 ⚠️' if found_residual else '无 ✅'}\n")

    print(f"\n{'═' * 50}")
    print(f"✅ 完成！共 {total_rows} 行，{len(all_outputs)} 张表")
    print(f"   映射表: {mapping_file}")
    print(f"   汇总: {summary_file}")
    if not args.write:
        print(f"\n   当前为 dry-run 模式，确认后加 --write 写入 GSheet")


if __name__ == '__main__':
    main()
