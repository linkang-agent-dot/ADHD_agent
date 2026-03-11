# -*- coding: utf-8 -*-
"""
Google Workspace CLI Helper
用于简化 gws 命令调用，解决 Windows PowerShell 引号转义问题

使用方法:
    python gws_helper.py list-files
    python gws_helper.py read-sheet <spreadsheet_id> <range>
    python gws_helper.py create-doc <title>
    python gws_helper.py write-doc <doc_id> <content_file>
    python gws_helper.py summarize-sheet <spreadsheet_id> <output_title>
"""

import subprocess
import json
import os
import sys
import argparse

# 配置
GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
if not os.path.exists(GWS_CMD):
    # 尝试找到 gws
    import shutil
    GWS_CMD = shutil.which('gws') or 'gws'


def run_gws(args, json_body=None):
    """运行 gws 命令"""
    cmd = [GWS_CMD] + args
    if json_body:
        cmd.extend(['--json', json.dumps(json_body, ensure_ascii=False)])
    
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        encoding='utf-8',
        env={**os.environ, 'GOOGLE_WORKSPACE_PROJECT_ID': os.environ.get('GOOGLE_WORKSPACE_PROJECT_ID', '')}
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr or result.stdout}", file=sys.stderr)
        return None
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.stdout


def list_files(limit=20, keyword=None, file_type=None):
    """列出 Drive 文件，支持关键词过滤"""
    params = {'pageSize': 100}
    cmd = [GWS_CMD, 'drive', 'files', 'list', '--params', json.dumps(params)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Error: {result.stdout}", file=sys.stderr)
        return []
    
    if data and 'files' in data:
        files = data['files']
        
        # 按关键词过滤
        if keyword:
            keyword_lower = keyword.lower()
            files = [f for f in files if keyword_lower in f.get('name', '').lower()]
        
        # 按类型过滤
        if file_type == 'sheet':
            files = [f for f in files if 'spreadsheet' in f.get('mimeType', '')]
        elif file_type == 'doc':
            files = [f for f in files if 'document' in f.get('mimeType', '')]
        
        files = files[:limit]
        print(f"\n找到 {len(files)} 个文件:\n")
        for f in files:
            print(f"  {f['name']}")
            print(f"    ID: {f['id']}")
            print(f"    类型: {f['mimeType']}")
            print()
        return files
    return []


def search_files(keyword, file_type=None):
    """搜索 Drive 文件"""
    return list_files(limit=50, keyword=keyword, file_type=file_type)


def read_sheet(spreadsheet_id, range_name):
    """读取 Google Sheet 数据"""
    params = json.dumps({
        'spreadsheetId': spreadsheet_id,
        'range': range_name
    })
    
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    try:
        data = json.loads(result.stdout)
        if 'values' in data:
            print(f"\n读取 {len(data['values'])} 行数据:\n")
            for row in data['values'][:20]:
                print('\t'.join(str(cell) for cell in row))
        return data
    except json.JSONDecodeError:
        print(f"Error: {result.stdout}", file=sys.stderr)
        return None


def get_sheet_info(spreadsheet_id):
    """获取表格信息"""
    params = json.dumps({
        'spreadsheetId': spreadsheet_id,
        'fields': 'properties.title,sheets.properties'
    })
    
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'get', '--params', params]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    try:
        data = json.loads(result.stdout)
        print(f"\n表格: {data['properties']['title']}")
        print(f"工作表:")
        for sheet in data.get('sheets', []):
            props = sheet['properties']
            print(f"  - {props['title']} (ID: {props['sheetId']})")
        return data
    except json.JSONDecodeError:
        print(f"Error: {result.stdout}", file=sys.stderr)
        return None


def create_doc(title):
    """创建新文档"""
    create_body = {'title': title}
    cmd = [GWS_CMD, 'docs', 'documents', 'create', '--json', json.dumps(create_body, ensure_ascii=False)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    try:
        data = json.loads(result.stdout)
        doc_id = data['documentId']
        print(f"\n文档创建成功!")
        print(f"  标题: {title}")
        print(f"  ID: {doc_id}")
        print(f"  链接: https://docs.google.com/document/d/{doc_id}/edit")
        return doc_id
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error: {result.stdout}", file=sys.stderr)
        return None


def write_doc(doc_id, content):
    """写入文档内容"""
    request = {
        'requests': [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
    }
    
    params = json.dumps({'documentId': doc_id})
    json_str = json.dumps(request, ensure_ascii=False)
    
    cmd = [GWS_CMD, 'docs', 'documents', 'batchUpdate', '--params', params, '--json', json_str]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode == 0:
        print(f"\n内容已写入文档")
        print(f"  链接: https://docs.google.com/document/d/{doc_id}/edit")
        return True
    else:
        print(f"Error: {result.stdout or result.stderr}", file=sys.stderr)
        return False


def summarize_sheet(spreadsheet_id, output_title, sheets_to_read=None):
    """读取 Google Sheet 并创建总结文档"""
    
    # 1. 获取表格信息
    print("正在读取表格信息...")
    info = get_sheet_info(spreadsheet_id)
    if not info:
        return None
    
    source_title = info['properties']['title']
    sheets = info.get('sheets', [])
    
    # 2. 读取各工作表数据
    summary_content = f"{output_title}\n\n"
    summary_content += f"原始表格: {source_title}\n"
    summary_content += f"链接: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/\n"
    summary_content += "=" * 50 + "\n\n"
    
    for sheet in sheets[:5]:  # 最多读取5个工作表
        sheet_name = sheet['properties']['title']
        if sheet['properties'].get('hidden'):
            continue
            
        print(f"正在读取: {sheet_name}...")
        
        params = json.dumps({
            'spreadsheetId': spreadsheet_id,
            'range': f"'{sheet_name}'!A1:Z30"
        })
        
        cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        try:
            data = json.loads(result.stdout)
            values = data.get('values', [])
            
            summary_content += f"\n【{sheet_name}】\n"
            summary_content += "-" * 30 + "\n"
            
            for row in values[:15]:
                summary_content += '\t'.join(str(cell) for cell in row) + '\n'
            
            if len(values) > 15:
                summary_content += f"... (还有 {len(values) - 15} 行)\n"
            
            summary_content += "\n"
        except json.JSONDecodeError:
            continue
    
    # 3. 创建总结文档
    print("正在创建总结文档...")
    doc_id = create_doc(output_title)
    if not doc_id:
        return None
    
    # 4. 写入内容
    print("正在写入内容...")
    write_doc(doc_id, summary_content)
    
    print("\n" + "=" * 50)
    print("总结文档已创建完成!")
    print(f"链接: https://docs.google.com/document/d/{doc_id}/edit")
    
    return doc_id


def main():
    # 修复 Windows 控制台编码问题
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    parser = argparse.ArgumentParser(description='Google Workspace CLI Helper')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list-files
    list_parser = subparsers.add_parser('list-files', help='列出 Drive 文件')
    list_parser.add_argument('--limit', type=int, default=20, help='显示数量限制')
    list_parser.add_argument('--keyword', '-k', help='按关键词过滤')
    list_parser.add_argument('--type', '-t', choices=['sheet', 'doc'], help='按类型过滤')
    
    # search
    search_parser = subparsers.add_parser('search', help='搜索 Drive 文件')
    search_parser.add_argument('keyword', help='搜索关键词')
    search_parser.add_argument('--type', '-t', choices=['sheet', 'doc'], help='按类型过滤')
    
    # read-sheet
    read_parser = subparsers.add_parser('read-sheet', help='读取 Google Sheet')
    read_parser.add_argument('spreadsheet_id', help='表格 ID')
    read_parser.add_argument('range', nargs='?', default='Sheet1!A1:Z50', help='范围 (默认: Sheet1!A1:Z50)')
    
    # sheet-info
    info_parser = subparsers.add_parser('sheet-info', help='获取表格信息')
    info_parser.add_argument('spreadsheet_id', help='表格 ID')
    
    # create-doc
    create_parser = subparsers.add_parser('create-doc', help='创建新文档')
    create_parser.add_argument('title', help='文档标题')
    
    # write-doc
    write_parser = subparsers.add_parser('write-doc', help='写入文档内容')
    write_parser.add_argument('doc_id', help='文档 ID')
    write_parser.add_argument('content_file', help='内容文件路径')
    
    # summarize-sheet
    summarize_parser = subparsers.add_parser('summarize-sheet', help='总结 Google Sheet 并创建文档')
    summarize_parser.add_argument('spreadsheet_id', help='表格 ID')
    summarize_parser.add_argument('output_title', help='输出文档标题')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 检查环境变量
    if not os.environ.get('GOOGLE_WORKSPACE_PROJECT_ID'):
        print("警告: 未设置 GOOGLE_WORKSPACE_PROJECT_ID 环境变量", file=sys.stderr)
    
    if args.command == 'list-files':
        list_files(args.limit, keyword=args.keyword, file_type=getattr(args, 'type', None))
    elif args.command == 'search':
        search_files(args.keyword, file_type=getattr(args, 'type', None))
    elif args.command == 'read-sheet':
        read_sheet(args.spreadsheet_id, args.range)
    elif args.command == 'sheet-info':
        get_sheet_info(args.spreadsheet_id)
    elif args.command == 'create-doc':
        create_doc(args.title)
    elif args.command == 'write-doc':
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        write_doc(args.doc_id, content)
    elif args.command == 'summarize-sheet':
        summarize_sheet(args.spreadsheet_id, args.output_title)


if __name__ == '__main__':
    main()
