# -*- coding: utf-8 -*-
"""显示 drop 配置的详细信息"""
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

def show_drop_configs():
    """显示 drop 配置详情"""
    spreadsheet_id = '1sicvhfxZhagLVmpEg4HDcaCnPWPgsWkhgZKC-HxCCuc'
    
    # 读取完整数据
    print("正在读取表格数据...")
    rows = read_sheet(spreadsheet_id, 'activity_special_master!A1:Z1000')
    
    if not rows:
        print("未读取到数据")
        return
    
    headers = rows[0]
    
    # 重点关注的 drop 配置 ID
    drop_config_ids = [
        '21211308',  # lucky_drop
        '21211468',  # daily_drop_limit
        '21211062',  # random
        '21211201',  # 7days_log_in_random
        '21211202',
        '21211203',
        '21211204',
    ]
    
    print("\n" + "=" * 100)
    print("DROP 随机掉落相关配置详情")
    print("=" * 100 + "\n")
    
    for row in rows[1:]:
        if len(row) < 3:
            continue
        
        config_id = row[0] if len(row) > 0 else ''
        if config_id not in drop_config_ids:
            continue
        
        comment = row[1] if len(row) > 1 else ''
        config_type = row[2] if len(row) > 2 else ''
        reward = row[3] if len(row) > 3 else ''
        expr = row[4] if len(row) > 4 else ''
        arg1 = row[5] if len(row) > 5 else ''
        arg2 = row[6] if len(row) > 6 else ''
        arg3 = row[7] if len(row) > 7 else ''
        reward_expr = row[8] if len(row) > 8 else ''
        desc = row[9] if len(row) > 9 else ''
        array = row[10] if len(row) > 10 else ''
        status = row[11] if len(row) > 11 else ''
        condition = row[12] if len(row) > 12 else ''
        score_rule = row[13] if len(row) > 13 else ''
        country_use_type = row[14] if len(row) > 14 else ''
        
        print(f"\n【配置 ID: {config_id}】")
        print(f"  注释: {comment}")
        print(f"  类型: {config_type}")
        print(f"  arg1: {arg1}")
        print(f"  arg2: {arg2}")
        print(f"  arg3: {arg3}")
        if reward and reward != '[]':
            print(f"  奖励 (A_ARR_reward): {reward[:200]}")
        if expr and expr != '{}':
            print(f"  表达式 (A_MAP_expr): {expr[:300]}")
        if reward_expr and reward_expr != '[]':
            print(f"  奖励表达式 (A_ARR_reward_expr): {reward_expr[:200]}")
        if array and array != '[]':
            print(f"  数组 (A_ARR_array): {array[:200]}")
        if status and status != '[]':
            print(f"  状态 (A_ARR_status): {status[:200]}")
        if condition and condition != '{}':
            print(f"  条件 (S_MAP_condition): {condition[:200]}")
        if score_rule and score_rule != '[]':
            print(f"  评分规则 (S_ARR_score_rule): {score_rule[:200]}")
        print(f"  国家使用类型: {country_use_type}")
        print("-" * 100)
    
    print("\n\n【配置类型总结】")
    print("1. lucky_drop - 幸运掉落，用于跨服幸运奖")
    print("2. daily_drop_limit - 每日掉落上限限制")
    print("3. random - 随机数生成")
    print("4. 7days_log_in_random - 7天登录随机奖励")
    print("\n这些配置可以复用，主要关注类型字段和表达式字段的配置方式。")

if __name__ == '__main__':
    show_drop_configs()
