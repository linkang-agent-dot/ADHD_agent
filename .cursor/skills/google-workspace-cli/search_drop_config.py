# -*- coding: utf-8 -*-
"""搜索 drop 随机掉落相关配置"""
import subprocess
import json
import sys
import os

# 设置编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
if not os.path.exists(GWS_CMD):
    import shutil
    GWS_CMD = shutil.which('gws') or 'gws'

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
        return data.get('values', [])
    except json.JSONDecodeError:
        print(f"Error: {result.stdout}", file=sys.stderr)
        return []

def search_drop_configs(spreadsheet_id):
    """搜索 drop 相关配置"""
    print("正在读取表格数据...")
    rows = read_sheet(spreadsheet_id, 'activity_special_master!A1:Z1000')
    
    if not rows:
        print("未读取到数据")
        return
    
    # 获取表头
    headers = rows[0] if rows else []
    print(f"表头: {headers[:5]}...")
    print(f"共 {len(rows)} 行数据\n")
    
    # 查找 drop 相关配置
    drop_configs = []
    keywords = ['drop', '掉落', '随机', 'random']
    
    for i, row in enumerate(rows[1:], start=2):  # 跳过表头
        if len(row) < 3:
            continue
        
        # 检查各个字段
        row_str = ' '.join(str(cell) for cell in row).lower()
        comment = row[1] if len(row) > 1 else ''
        config_type = row[2] if len(row) > 2 else ''
        
        # 检查是否包含关键词
        found = False
        for keyword in keywords:
            if keyword in row_str or keyword in comment.lower() or keyword in config_type.lower():
                found = True
                break
        
        if found:
            drop_configs.append({
                'row': i,
                'id': row[0] if len(row) > 0 else '',
                'comment': comment,
                'type': config_type,
                'full_row': row
            })
    
    # 输出结果
    print(f"找到 {len(drop_configs)} 个可能的 drop 相关配置:\n")
    print("=" * 80)
    
    for config in drop_configs:
        print(f"\n行 {config['row']}:")
        print(f"  ID: {config['id']}")
        print(f"  注释: {config['comment']}")
        print(f"  类型: {config['type']}")
        if len(config['full_row']) > 3:
            print(f"  奖励: {config['full_row'][3][:100] if len(config['full_row'][3]) > 100 else config['full_row'][3]}")
        print("-" * 80)
    
    # 按类型分组统计
    type_counts = {}
    for config in drop_configs:
        t = config['type']
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"\n按类型统计:")
    for t, count in sorted(type_counts.items()):
        print(f"  {t}: {count} 个")

if __name__ == '__main__':
    spreadsheet_id = '1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc'
    search_drop_configs(spreadsheet_id)
