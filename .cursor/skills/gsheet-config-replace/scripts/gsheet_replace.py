#!/usr/bin/env python3
"""
GSheet 配置表批量替换工具
扫描 P2/X2 配置表，在单元格内做字符串替换，写回 GSheet
"""

import json
import re
import subprocess
import sys
import argparse
import io

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
from typing import Dict, List, Any, Optional

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'

# 索引表配置
INDEX_CONFIG = {
    'P2': {
        'spreadsheetId': '1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c',
        'range': 'fw_gsheet_config!A1:F900',
        # B列=表名(如 "1011_i18n - xxx")，需从中提取编号
        # C列=页签名，D列=SheetID
        'id_col': 1,      # B列，需提取前缀数字
        'name_col': 2,    # C列=页签名
        'sheet_id_col': 3 # D列=SheetID
    },
    'X2': {
        'spreadsheetId': '1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc',
        'range': 'fw_gsheet_config!A1:E600',
        'id_col': 0,      # A列=编号
        'name_col': 3,    # D列=页签名
        'sheet_id_col': 4 # E列=SheetID
    }
}


def run_gws(args: List[str], json_body: Optional[Dict] = None) -> Dict:
    """执行 gws 命令并返回 JSON 结果"""
    cmd = [GWS_CMD] + args
    if json_body:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])

    result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        raise Exception(f"gws error: {result.stderr}")

    return json.loads(result.stdout) if result.stdout.strip() else {}


def get_table_index(project: str) -> Dict[str, Dict]:
    """获取表索引 {编号: {name, sheetId}}"""
    config = INDEX_CONFIG[project]
    params = json.dumps({
        'spreadsheetId': config['spreadsheetId'],
        'range': config['range']
    })

    data = run_gws(['sheets', 'spreadsheets', 'values', 'get', '--params', params])
    rows = data.get('values', [])

    index = {}
    for row in rows:
        if len(row) <= max(config['id_col'], config['name_col'], config['sheet_id_col']):
            continue

        id_raw = str(row[config['id_col']]).strip()
        name = row[config['name_col']].strip() if len(row) > config['name_col'] else ''
        sheet_id = row[config['sheet_id_col']].strip() if len(row) > config['sheet_id_col'] else ''

        if not sheet_id:
            continue

        # 从 B 列提取编号（如 "1011_i18n - xxx" → "1011"，或 "2115_x2_activity_task" → "2115"）
        table_id = id_raw.split('_')[0] if '_' in id_raw else id_raw
        # 确保是数字
        if table_id.isdigit():
            index[table_id] = {'name': name, 'sheetId': sheet_id}

    return index


def get_visible_sheets(spreadsheet_id: str) -> List[str]:
    """获取所有未隐藏的页签名"""
    params = json.dumps({'spreadsheetId': spreadsheet_id})
    data = run_gws(['sheets', 'spreadsheets', 'get', '--params', params])

    sheets = []
    for sheet in data.get('sheets', []):
        # API 返回的是 'properties' 不是 'sheetProperties'
        props = sheet.get('properties', {})
        if not props.get('hidden', False):
            sheets.append(props.get('title', ''))

    return [s for s in sheets if s]


def read_sheet_values(spreadsheet_id: str, sheet_name: str, columns: str) -> List[List[str]]:
    """读取页签数据"""
    range_str = f"'{sheet_name}'!{columns}"
    params = json.dumps({
        'spreadsheetId': spreadsheet_id,
        'range': range_str,
        'valueRenderOption': 'FORMATTED_VALUE'
    })

    try:
        data = run_gws(['sheets', 'spreadsheets', 'values', 'get', '--params', params])
        return data.get('values', [])
    except Exception as e:
        print(f"  ⚠️ 读取 {sheet_name} 失败: {e}")
        return []


def do_replace(cell: str, replacements: Dict[str, str], match_mode: str) -> tuple[str, bool]:
    """执行替换，返回 (新值, 是否有变化)"""
    if not cell:
        return cell, False

    new_cell = cell
    for old_val, new_val in replacements.items():
        if match_mode == 'exact':
            # 精确边界匹配，避免误替换更长的 ID
            pattern = r'(?<![0-9])' + re.escape(old_val) + r'(?![0-9])'
            new_cell = re.sub(pattern, new_val, new_cell)
        else:
            new_cell = new_cell.replace(old_val, new_val)

    return new_cell, new_cell != cell


def col_index_to_letter(index: int) -> str:
    """列索引转字母 (0=A, 1=B, 26=AA)"""
    result = ''
    while index >= 0:
        result = chr(index % 26 + ord('A')) + result
        index = index // 26 - 1
    return result


def scan_and_replace(
    spreadsheet_id: str,
    table_id: str,
    table_name: str,
    sheets: List[str],
    columns: str,
    replacements: Dict[str, str],
    match_mode: str,
    row_ids: Optional[List[str]] = None,
    id_column: int = 0
) -> List[Dict]:
    """扫描并替换，返回变更列表

    Args:
        row_ids: 可选，只处理这些行 ID 对应的行
        id_column: 行 ID 所在列索引（默认 0 = A 列）
    """
    changes = []

    for sheet_name in sheets:
        print(f"  扫描页签: {sheet_name}")
        rows = read_sheet_values(spreadsheet_id, sheet_name, columns)

        for row_idx, row in enumerate(rows):
            # 如果指定了 row_ids，只处理匹配的行
            if row_ids:
                if len(row) <= id_column:
                    continue
                row_id = str(row[id_column]).strip()
                if row_id not in row_ids:
                    continue

            for col_idx, cell in enumerate(row):
                if not isinstance(cell, str):
                    cell = str(cell) if cell else ''

                new_cell, changed = do_replace(cell, replacements, match_mode)
                if changed:
                    col_letter = col_index_to_letter(col_idx)
                    row_id_str = str(row[id_column]).strip() if len(row) > id_column else ''
                    changes.append({
                        'spreadsheetId': spreadsheet_id,
                        'tableId': table_id,
                        'tableName': table_name,
                        'sheet': sheet_name,
                        'row': row_idx + 1,
                        'col': col_letter,
                        'rowId': row_id_str,
                        'range': f"'{sheet_name}'!{col_letter}{row_idx + 1}",
                        'oldValue': cell[:100] + ('...' if len(cell) > 100 else ''),
                        'newValue': new_cell[:100] + ('...' if len(new_cell) > 100 else ''),
                        'fullNewValue': new_cell
                    })

    return changes


def write_changes(changes: List[Dict]) -> Dict[str, int]:
    """批量写入变更，返回每个表的写入数量"""
    # 按 spreadsheetId 分组
    by_sheet = {}
    for c in changes:
        sid = c['spreadsheetId']
        if sid not in by_sheet:
            by_sheet[sid] = []
        by_sheet[sid].append(c)

    results = {}
    for spreadsheet_id, sheet_changes in by_sheet.items():
        table_id = sheet_changes[0]['tableId']
        success_count = 0

        # 分批写入，每批最多 20 个单元格
        batch_size = 5
        for i in range(0, len(sheet_changes), batch_size):
            batch = sheet_changes[i:i + batch_size]

            # 构建 batchUpdate 请求
            data = []
            for c in batch:
                data.append({
                    'range': c['range'],
                    'values': [[c['fullNewValue']]]
                })

            params = json.dumps({
                'spreadsheetId': spreadsheet_id,
                'valueInputOption': 'RAW'
            })

            body = {'data': data}

            try:
                run_gws(
                    ['sheets', 'spreadsheets', 'values', 'batchUpdate', '--params', params],
                    json_body=body
                )
                success_count += len(batch)
                print(f"    批次 {i//batch_size + 1}: {len(batch)} 处已写入")
            except Exception as e:
                print(f"    批次 {i//batch_size + 1} 写入失败: {e}")

        results[table_id] = success_count
        print(f"  ✅ 表 {table_id}: {success_count}/{len(sheet_changes)} 处已写入")

    return results


def main():
    parser = argparse.ArgumentParser(description='GSheet 配置表批量替换')
    parser.add_argument('--config', required=True, help='配置文件路径 (JSON)')
    parser.add_argument('--write', action='store_true', help='实际写入（默认 dry-run）')
    args = parser.parse_args()

    # 读取配置
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    project = config.get('project', 'P2')
    tables = config.get('tables', [])
    sheets_filter = config.get('sheets', '*')
    columns = config.get('columns', 'A:AZ')
    replacements = config.get('replacements', {})
    match_mode = config.get('matchMode', 'exact')
    row_ids = config.get('rowIds', None)  # 新增：只处理指定行 ID
    id_column = config.get('idColumn', 0)  # 新增：行 ID 所在列（默认 A 列）
    dry_run = not args.write

    if not tables:
        print("❌ 未指定表编号")
        sys.exit(1)

    if not replacements:
        print("❌ 未指定替换映射")
        sys.exit(1)

    print(f"📋 项目: {project}")
    print(f"📋 表: {', '.join(tables)}")
    print(f"📋 替换映射: {len(replacements)} 条")
    print(f"📋 匹配模式: {match_mode}")
    if row_ids:
        print(f"📋 限定行 ID: {len(row_ids)} 个")
    print(f"📋 模式: {'dry-run（不写入）' if dry_run else '⚠️ 实际写入'}")
    print()

    # 获取表索引
    print("🔍 获取表索引...")
    table_index = get_table_index(project)

    all_changes = []

    for table_id in tables:
        if table_id not in table_index:
            print(f"⚠️ 表 {table_id} 未在索引中找到，跳过")
            continue

        info = table_index[table_id]
        spreadsheet_id = info['sheetId']
        table_name = info['name']

        print(f"\n📊 表 {table_id} ({table_name})")
        print(f"   SheetID: {spreadsheet_id}")

        # 获取页签列表
        if sheets_filter == '*':
            sheets = get_visible_sheets(spreadsheet_id)
            print(f"   页签: {len(sheets)} 个未隐藏页签")
        else:
            sheets = sheets_filter if isinstance(sheets_filter, list) else [sheets_filter]
            print(f"   页签: {', '.join(sheets)}")

        # 扫描替换
        changes = scan_and_replace(
            spreadsheet_id, table_id, table_name,
            sheets, columns, replacements, match_mode,
            row_ids=row_ids, id_column=id_column
        )
        all_changes.extend(changes)

        # 按页签统计
        by_sheet = {}
        for c in changes:
            s = c['sheet']
            by_sheet[s] = by_sheet.get(s, 0) + 1

        for s, count in by_sheet.items():
            print(f"   - {s}: {count} 处替换")

    print(f"\n{'='*50}")
    print(f"📊 总计: {len(all_changes)} 处替换")

    if not all_changes:
        print("✅ 无需替换")
        return

    if dry_run:
        print("\n⚠️ dry-run 模式，未写入")
        print("确认后添加 --write 参数执行实际写入")

        # 输出详细变更（最多显示 20 条）
        print("\n变更详情（前 20 条）:")
        for c in all_changes[:20]:
            print(f"  {c['tableId']}:{c['sheet']}!{c['col']}{c['row']}")
            print(f"    - {c['oldValue']}")
            print(f"    + {c['newValue']}")
    else:
        print("\n🚀 开始写入...")
        results = write_changes(all_changes)
        total_written = sum(results.values())
        print(f"\n✅ 写入完成: {total_written} 处")


if __name__ == '__main__':
    main()
