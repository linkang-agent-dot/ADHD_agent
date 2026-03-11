# -*- coding: utf-8 -*-
"""
X2 配置表分支差异汇总 → Google Sheet

对比两个分支的配置表差异，创建 Google Sheet：
- 每个配置表一个页签
- 新增行整行绿色，修改行仅变化的单元格标黄
- 直接调用 node run-gws.js 绕过 cmd.exe 8191 字符限制
"""

import subprocess
import json
import os
import sys
import time
import argparse

REPO_DIR = r"D:\UGit\x2gdconf"
NPM_DIR = os.path.join(os.environ.get('APPDATA', ''), 'npm')
RUN_GWS_JS = os.path.join(NPM_DIR, 'node_modules', '@googleworkspace', 'cli', 'run-gws.js')
GWS_CMD = os.path.join(NPM_DIR, 'gws.cmd')

COLOR_HEADER = {"red": 0.75, "green": 0.82, "blue": 0.95}
COLOR_ADDED = {"red": 0.85, "green": 0.95, "blue": 0.85}
COLOR_MODIFIED = {"red": 1.0, "green": 0.93, "blue": 0.70}

FORMAT_BATCH_SIZE = 50
DATA_CHUNK_SIZE = 20
PAYLOAD_LIMIT = 7000


def run_git(args):
    result = subprocess.run(
        ["git"] + args,
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=REPO_DIR
    )
    return result.stdout


def run_gws(args, json_body=None):
    """调用 gws API。大 payload 自动走 node 直连。"""
    if json_body is not None:
        json_str = json.dumps(json_body, ensure_ascii=False)
        if len(json_str) > PAYLOAD_LIMIT:
            return _run_gws_node(args, json_body)

    cmd = [GWS_CMD] + args
    if json_body is not None:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding='utf-8', errors='replace'
        )
    except OSError:
        return _run_gws_node(args, json_body)

    if result.returncode != 0:
        print(f"  GWS Error: {result.stderr or result.stdout}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout


def _run_gws_node(args, json_body=None):
    """直接调用 node run-gws.js，绕过 cmd.exe 8191 字符限制。"""
    cmd = ['node', RUN_GWS_JS] + args
    if json_body is not None:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding='utf-8', errors='replace', timeout=120
        )
    except OSError as e:
        print(f"  Node Error: {e}", file=sys.stderr)
        return None

    if result.returncode != 0:
        print(f"  Node GWS Error: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout


def get_changed_files(source, target):
    """获取两个分支间有差异的配置表文件列表（排除 i18n）。"""
    output = run_git(["diff", "--name-only", f"{target}...{source}", "--", "fo/config/"])
    files = []
    for line in output.strip().split('\n'):
        line = line.strip()
        if line and line.endswith('.tsv') and '/i18n/' not in line:
            files.append(line)
    return files


def get_header(filepath, source):
    """获取表头。优先取 fwcli_name 行（字段名），否则取第一个有效行。"""
    content = run_git(["show", f"{source}:{filepath}"])
    lines = content.split('\n')
    fallback = None
    for line in lines:
        parts = line.split('\t')
        if len(parts) <= 2:
            continue
        if parts[0] == 'fwcli_name':
            return parts
        if fallback is None:
            fallback = parts
    return fallback or (lines[0].split('\t') if lines else [])


def _pad_row(parts, expected_len):
    """补齐短行：TSV 尾部空值列可能缺少 tab 分隔符。"""
    if len(parts) < expected_len:
        parts.extend([''] * (expected_len - len(parts)))
    return parts


def get_diff_data(filepath, source, target, header_cols=0):
    """提取差异行。header_cols 用于补齐尾部空列。"""
    diff_output = run_git(["diff", f"{target}...{source}", "--", filepath])
    added_lines = []
    removed_lines = []

    for line in diff_output.split('\n'):
        if line.startswith('+++') or line.startswith('---'):
            continue
        if line.startswith('+'):
            content = line[1:]
            if content.strip():
                added_lines.append(content)
        elif line.startswith('-'):
            content = line[1:]
            if content.strip():
                removed_lines.append(content)

    removed_map = {}
    for line in removed_lines:
        parts = line.split('\t')
        if header_cols:
            _pad_row(parts, header_cols)
        row_id = next((p.strip() for p in parts if p.strip()), None)
        if row_id:
            removed_map[row_id] = parts

    results = []
    for line in added_lines:
        parts = line.split('\t')
        if header_cols:
            _pad_row(parts, header_cols)
        row_id = next((p.strip() for p in parts if p.strip()), None)
        is_modified = row_id in removed_map
        results.append({
            'cells': parts,
            'type': 'modified' if is_modified else 'added',
            'id': row_id,
            'old_cells': removed_map.get(row_id),
        })
    return results


def write_values_chunked(spreadsheet_id, sheet_name, values):
    """分块写入数据，自动处理超长行。"""
    for start in range(0, len(values), DATA_CHUNK_SIZE):
        chunk = values[start:start + DATA_CHUNK_SIZE]
        row_start = start + 1
        body = {"values": chunk, "majorDimension": "ROWS"}
        params = json.dumps({
            "spreadsheetId": spreadsheet_id,
            "range": f"'{sheet_name}'!A{row_start}",
            "valueInputOption": "RAW"
        })

        json_str = json.dumps(body, ensure_ascii=False)
        if len(json_str) > PAYLOAD_LIMIT:
            for i, row in enumerate(chunk):
                single_body = {"values": [row], "majorDimension": "ROWS"}
                single_params = json.dumps({
                    "spreadsheetId": spreadsheet_id,
                    "range": f"'{sheet_name}'!A{row_start + i}",
                    "valueInputOption": "RAW"
                })
                run_gws(
                    ['sheets', 'spreadsheets', 'values', 'update',
                     '--params', single_params],
                    single_body
                )
                time.sleep(0.15)
        else:
            run_gws(
                ['sheets', 'spreadsheets', 'values', 'update',
                 '--params', params],
                body
            )
        time.sleep(0.2)


def build_format_requests(sheet_id, rows, col_count):
    """构建格式化请求列表：表头蓝色+冻结，新增行绿色，修改行精确到单元格黄色。"""
    requests = [
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {
                    "backgroundColor": COLOR_HEADER,
                    "textFormat": {"bold": True},
                }},
                "fields": "userEnteredFormat(backgroundColor,textFormat.bold)"
            }
        },
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount"
            }
        }
    ]

    for row_idx, row in enumerate(rows):
        actual_row = row_idx + 1

        if row['type'] == 'added':
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": actual_row,
                        "endRowIndex": actual_row + 1,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": COLOR_ADDED}},
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })
        elif row['type'] == 'modified' and row.get('old_cells'):
            old = row['old_cells']
            new = row['cells']
            for col_idx in range(max(len(old), len(new))):
                old_val = old[col_idx].strip() if col_idx < len(old) else ''
                new_val = new[col_idx].strip() if col_idx < len(new) else ''
                if old_val != new_val:
                    requests.append({
                        "repeatCell": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": actual_row,
                                "endRowIndex": actual_row + 1,
                                "startColumnIndex": col_idx + 1,
                                "endColumnIndex": col_idx + 2,
                            },
                            "cell": {"userEnteredFormat": {"backgroundColor": COLOR_MODIFIED}},
                            "fields": "userEnteredFormat.backgroundColor"
                        }
                    })
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": actual_row,
                        "endRowIndex": actual_row + 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": COLOR_MODIFIED}},
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })

    return requests


def apply_formatting(spreadsheet_id, format_requests):
    """分批发送格式化请求。"""
    for i in range(0, len(format_requests), FORMAT_BATCH_SIZE):
        batch = format_requests[i:i + FORMAT_BATCH_SIZE]
        params = json.dumps({"spreadsheetId": spreadsheet_id})
        body = {"requests": batch}
        run_gws(
            ['sheets', 'spreadsheets', 'batchUpdate', '--params', params],
            body
        )
        time.sleep(0.3)


def main():
    parser = argparse.ArgumentParser(description='X2 配置表分支差异汇总 → Google Sheet')
    parser.add_argument('--source', required=True, help='源分支 (feature branch)，如 origin/dev_X2-39183')
    parser.add_argument('--target', default='origin/dev', help='目标分支 (基准)，默认 origin/dev')
    parser.add_argument('--title', default=None, help='Google Sheet 标题')
    args = parser.parse_args()

    os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'

    source = args.source
    target = args.target
    title = args.title or f"X2 分支差异汇总 ({source.replace('origin/', '')} vs {target.replace('origin/', '')})"

    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)

    print("\n[1/5] 拉取最新远程分支...")
    run_git(["fetch", "origin"])

    print("\n[2/5] 提取差异数据...")
    changed_files = get_changed_files(source, target)
    if not changed_files:
        print("  没有发现配置表差异。")
        return

    all_data = {}
    for filepath in changed_files:
        sheet_name = os.path.basename(filepath).replace('.tsv', '')
        header = get_header(filepath, source)
        rows = get_diff_data(filepath, source, target, header_cols=len(header))
        if rows:
            all_data[filepath] = {'name': sheet_name, 'rows': rows, 'header': header}
            added_cnt = sum(1 for r in rows if r['type'] == 'added')
            mod_cnt = sum(1 for r in rows if r['type'] == 'modified')
            print(f"  {sheet_name}: {added_cnt} 新增, {mod_cnt} 修改")

    if not all_data:
        print("  所有文件差异为空行，无需创建表格。")
        return

    print(f"\n[3/5] 创建 Google Sheet ({len(all_data)} 个页签)...")
    sheet_list = []
    for i, (filepath, info) in enumerate(all_data.items()):
        sheet_list.append({
            "properties": {"sheetId": i, "title": info['name'], "index": i}
        })

    create_body = {
        "properties": {"title": title},
        "sheets": sheet_list,
    }
    result = run_gws(['sheets', 'spreadsheets', 'create'], create_body)
    if not result or 'spreadsheetId' not in result:
        print("创建失败！", file=sys.stderr)
        return
    spreadsheet_id = result['spreadsheetId']
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    print(f"  链接: {url}")

    print(f"\n[4/5] 写入数据...")
    all_format_requests = []

    for idx, (filepath, info) in enumerate(all_data.items()):
        sheet_name = info['name']
        rows = info['rows']
        sheet_id = idx
        print(f"  写入: {sheet_name} ({len(rows)} 行)...", end='', flush=True)

        header = info['header']
        col_count = len(header) + 1
        header_row = ["变更类型"] + header
        values = [header_row]
        for row in rows:
            label = "新增" if row['type'] == 'added' else "修改"
            values.append([label] + row['cells'])

        write_values_chunked(spreadsheet_id, sheet_name, values)
        print(" OK")

        fmt = build_format_requests(sheet_id, rows, col_count)
        all_format_requests.extend(fmt)

    print(f"\n[5/5] 应用精确着色 ({len(all_format_requests)} 条请求)...")
    apply_formatting(spreadsheet_id, all_format_requests)
    print("  着色完成")

    print(f"\n{'=' * 60}")
    print(f"  Google Sheet 已创建")
    print(f"  链接: {url}")
    print(f"{'=' * 60}")
    print(f"\n  图例: 绿色 = 新增行 | 黄色 = 修改的单元格 | 蓝色 = 表头")
    print(f"  共 {len(all_data)} 个页签，已排除 fo/i18n 本地化文件")


if __name__ == '__main__':
    main()
