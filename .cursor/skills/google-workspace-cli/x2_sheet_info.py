# -*- coding: utf-8 -*-
"""
X2 配置表页签信息工具
通过 gws CLI 读取 Google Sheet 页签信息，用于 X2 导表前的页签-分支匹配检查

使用方法:
    python x2_sheet_info.py                    # 显示帮助
    python x2_sheet_info.py --list             # 列出所有配置表
    python x2_sheet_info.py 1111               # 查找 1111 相关的表并显示页签
    python x2_sheet_info.py --tabs i18n        # 读取指定表的所有页签
    python x2_sheet_info.py --check item_dev   # 检查页签与当前分支是否匹配

配置要求:
    1. 安装 gws CLI: npm install -g @googleworkspace/cli
    2. 设置环境变量: $env:GOOGLE_WORKSPACE_PROJECT_ID = "calm-repeater-489707-n1"
    3. 完成 OAuth 授权: gws auth login
"""

import subprocess
import json
import os
import sys
import re
import shutil

# 配置
GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
if not os.path.exists(GWS_CMD):
    GWS_CMD = shutil.which('gws') or 'gws'

# X2 配置表索引 ID
X2_INDEX_SPREADSHEET_ID = '1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc'
X2_INDEX_SHEET_NAME = 'fw_gsheet_config'

# 设置输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')


def run_gws_cmd(args):
    """运行 gws 命令并返回 JSON 结果"""
    cmd = [GWS_CMD] + args
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            env={**os.environ}
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            if 'error' in error_msg.lower():
                try:
                    err = json.loads(result.stdout)
                    return {'error': err.get('error', {}).get('message', error_msg)}
                except:
                    pass
            return {'error': error_msg}
        
        return json.loads(result.stdout)
    except Exception as e:
        return {'error': str(e)}


def get_sheet_info(spreadsheet_id):
    """获取表格的所有页签信息"""
    params = json.dumps({
        'spreadsheetId': spreadsheet_id,
        'fields': 'properties.title,sheets.properties'
    })
    
    return run_gws_cmd(['sheets', 'spreadsheets', 'get', '--params', params])


def get_x2_config_index():
    """获取 X2 配置表索引"""
    params = json.dumps({
        'spreadsheetId': X2_INDEX_SPREADSHEET_ID,
        'range': f'{X2_INDEX_SHEET_NAME}!A:G'
    })
    
    result = run_gws_cmd(['sheets', 'spreadsheets', 'values', 'get', '--params', params])
    
    if 'error' in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        return []
    
    configs = []
    for row in result.get('values', []):
        if len(row) >= 4:
            configs.append({
                'category': row[0],
                'table_name': row[1],
                'short_name': row[2],
                'spreadsheet_id': row[3],
                'type': row[4] if len(row) > 4 else '',
            })
    
    return configs


def find_config_table(keyword):
    """根据关键词查找配置表"""
    configs = get_x2_config_index()
    
    matches = []
    keyword_lower = keyword.lower()
    
    for cfg in configs:
        if keyword_lower in cfg['table_name'].lower() or keyword_lower in cfg['short_name'].lower():
            matches.append(cfg)
    
    return matches


def parse_tab_info(sheet_props):
    """
    解析页签信息，提取版本标注
    
    页签命名规则示例:
    - "1111_item" -> 无版本标注
    - "1111_item_master" -> master 版本
    - "1111_item_hotfix" -> hotfix 版本
    - "1111_item_dev" -> dev 版本
    - "1111_item_22版本" -> test1/22版本
    """
    title = sheet_props.get('title', '')
    sheet_id = sheet_props.get('sheetId', 0)
    hidden = sheet_props.get('hidden', False)
    
    # 检测版本标注
    version = None
    title_lower = title.lower()
    
    if 'master' in title_lower:
        version = 'master'
    elif 'hotfix' in title_lower:
        version = 'hotfix'
    elif 'dev' in title_lower:
        version = 'dev'
    elif '22版本' in title or 'test1' in title_lower:
        version = 'test1'
    
    # 提取表名（去除版本后缀）
    table_name = re.sub(r'[_\-]?(master|hotfix|dev|test1|22版本)$', '', title, flags=re.IGNORECASE)
    
    return {
        'title': title,
        'sheet_id': sheet_id,
        'hidden': hidden,
        'version': version,
        'table_name': table_name
    }


def check_branch_tab_match(branch_name, tab_name):
    """
    检查分支和页签版本是否匹配
    
    返回: (is_match, warning_message)
    """
    tab_info = parse_tab_info({'title': tab_name})
    tab_version = tab_info['version']
    
    if not tab_version:
        return True, None  # 无版本标注，不检查
    
    branch_lower = branch_name.lower()
    
    # 判断分支类型
    if branch_lower.startswith('dev') or 'dev_' in branch_lower:
        branch_type = 'dev'
    elif branch_lower.startswith('hotfix') or 'hotfix_' in branch_lower:
        branch_type = 'hotfix'
    elif branch_lower.startswith('master'):
        branch_type = 'master'
    elif 'test1' in branch_lower:
        branch_type = 'test1'
    else:
        return True, None  # 未知分支类型，不检查
    
    # 版本匹配检查
    if branch_type != tab_version:
        return False, f"⚠️ 分支-页签版本不匹配: 分支={branch_type}, 页签={tab_version}"
    
    return True, None


def get_current_branch(repo_path=None):
    """获取当前 Git 分支名"""
    try:
        cmd = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        if repo_path:
            cmd = ['git', '-C', repo_path, 'rev-parse', '--abbrev-ref', 'HEAD']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None


def show_table_tabs(table_name_or_id):
    """显示指定配置表的所有页签"""
    # 先尝试从索引查找
    matches = find_config_table(table_name_or_id)
    
    if not matches:
        # 如果没找到，尝试直接作为 spreadsheet_id 使用
        print(f"在索引中未找到 '{table_name_or_id}'，尝试直接读取...")
        info = get_sheet_info(table_name_or_id)
        if 'error' in info:
            print(f"Error: {info['error']}", file=sys.stderr)
            return []
        
        doc_title = info.get('properties', {}).get('title', 'Unknown')
        sheets = info.get('sheets', [])
        
        print(f"\n表格: {doc_title}")
        print(f"页签数量: {len(sheets)}")
        print("-" * 40)
        
        for sheet in sheets:
            props = sheet.get('properties', {})
            tab_info = parse_tab_info(props)
            version_tag = f" [{tab_info['version']}]" if tab_info['version'] else ""
            print(f"  {tab_info['title']}{version_tag}")
        
        return sheets
    
    # 找到匹配的表
    for cfg in matches:
        print(f"\n{'='*50}")
        print(f"表名: {cfg['table_name']}")
        print(f"简称: {cfg['short_name']}")
        print(f"分类: {cfg['category']}")
        print(f"Sheet ID: {cfg['spreadsheet_id']}")
        print("-" * 50)
        
        info = get_sheet_info(cfg['spreadsheet_id'])
        if 'error' in info:
            print(f"  Error: {info['error']}")
            continue
        
        sheets = info.get('sheets', [])
        print(f"页签 ({len(sheets)} 个):")
        
        for sheet in sheets:
            props = sheet.get('properties', {})
            tab_info = parse_tab_info(props)
            version_tag = f" [{tab_info['version']}]" if tab_info['version'] else ""
            hidden_tag = " (隐藏)" if tab_info['hidden'] else ""
            print(f"  • {tab_info['title']}{version_tag}{hidden_tag}")
    
    return matches


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='X2 配置表页签信息工具')
    parser.add_argument('keyword', nargs='?', help='表名关键词 (如 1111, item, i18n)')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有配置表')
    parser.add_argument('--tabs', '-t', help='读取指定表的所有页签')
    parser.add_argument('--check', '-c', help='检查指定页签与当前分支是否匹配')
    parser.add_argument('--repo', '-r', default='D:\\UGit\\x2gdconf', help='Git 仓库路径 (默认: D:\\UGit\\x2gdconf)')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出')
    
    args = parser.parse_args()
    
    # 检查 gws 是否可用
    if not os.path.exists(GWS_CMD) and not shutil.which('gws'):
        print("Error: gws CLI 未安装", file=sys.stderr)
        print("请运行: npm install -g @googleworkspace/cli", file=sys.stderr)
        sys.exit(1)
    
    # 检查环境变量
    if not os.environ.get('GOOGLE_WORKSPACE_PROJECT_ID'):
        print("Warning: 未设置 GOOGLE_WORKSPACE_PROJECT_ID 环境变量", file=sys.stderr)
        print("请运行: $env:GOOGLE_WORKSPACE_PROJECT_ID = 'calm-repeater-489707-n1'", file=sys.stderr)
    
    if args.check:
        # 检查页签与分支匹配
        branch = get_current_branch(args.repo)
        if branch:
            is_match, warning = check_branch_tab_match(branch, args.check)
            if warning:
                print(warning)
                sys.exit(1)
            else:
                print(f"✓ 分支 '{branch}' 与页签 '{args.check}' 匹配")
        else:
            print("Error: 无法获取当前分支", file=sys.stderr)
            sys.exit(1)
    elif args.list:
        # 列出所有配置表
        configs = get_x2_config_index()
        print(f"\nX2 配置表索引 (共 {len(configs)} 个):\n")
        
        current_category = None
        for cfg in configs:
            if cfg['category'] != current_category:
                current_category = cfg['category']
                print(f"\n【{current_category}】")
            print(f"  {cfg['table_name']}")
        
        if args.json:
            print(json.dumps(configs, ensure_ascii=False, indent=2))
    elif args.tabs:
        # 读取指定表的页签
        show_table_tabs(args.tabs)
    elif args.keyword:
        # 搜索并显示页签
        show_table_tabs(args.keyword)
    else:
        # 默认显示帮助
        parser.print_help()
        print("\n示例:")
        print("  python x2_sheet_info.py --list          # 列出所有配置表")
        print("  python x2_sheet_info.py 1111            # 查找 1111 相关表的页签")
        print("  python x2_sheet_info.py --tabs i18n     # 读取 i18n 表的页签")
        print("  python x2_sheet_info.py --check item_dev  # 检查分支匹配")


if __name__ == '__main__':
    main()
