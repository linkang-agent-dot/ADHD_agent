#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 2111_p2_activity_calendar 表读取 activityConfigId -> name 映射"""
import subprocess, json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'

SPREADSHEET_ID = '1OaExug4AwwFlGH6LGbBiMnvQF41hYg0LsXiMQZ9XX6g'

# Step 1: 先获取表格信息，找到正确的 sheet 名称
params = json.dumps({
    'spreadsheetId': SPREADSHEET_ID,
    'fields': 'sheets.properties'
})
cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'get', '--params', params]
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
info = json.loads(result.stdout)

print("=== Sheet 列表 ===")
target_sheet = None
for sheet in info.get('sheets', []):
    props = sheet.get('properties', {})
    title = props.get('title', '')
    gid = props.get('sheetId', '')
    print("  gid={}: '{}'".format(gid, title))
    if gid == 1688241274:
        target_sheet = title

if not target_sheet:
    print("找不到 activity_calendar sheet!")
    # 用第一个 sheet
    target_sheet = info['sheets'][0]['properties']['title']

print("\n使用 sheet: '{}'".format(target_sheet))

# Step 2: 读取 A列和C列
params = json.dumps({
    'spreadsheetId': SPREADSHEET_ID,
    'range': "'{}'!A:C".format(target_sheet)
})
cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params]
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

if not result.stdout.strip():
    print("Empty response. stderr: {}".format(result.stderr[:500]))
    sys.exit(1)

data = json.loads(result.stdout)
if 'error' in data:
    print("ERROR: {}".format(data['error']))
    sys.exit(1)

rows = data.get('values', [])
print("共读取 {} 行".format(len(rows)))

# 构建映射: A_INT_id -> S_STR_comment
config_name_map = {}
for row in rows[1:]:
    if len(row) >= 3:
        config_id = str(row[0]).strip()
        name = str(row[2]).strip()
        if config_id and name:
            config_name_map[config_id] = name

# 我们需要的 configId 列表
target_ids = [
    "21115731", "21115740", "21115733", "21115732", "21115728", "21115726",
    "21115729", "21115696", "21115376", "21115746", "21115398", "21115399",
    "21115526", "21115527", "21115747", "21115358", "21115359", "21115360",
    "21115735", "21115594", "21115472", "21115380", "21115037", "21115632",
    "21115633", "21115739", "21115738", "21115736", "21115559", "21115560",
    "21115441", "21115741", "21115742", "21115607", "21115479", "21115312",
    "21115313", "21115734", "21115737", "21115743", "21115744",
]

print("\n=== 映射结果 ===")
found = 0
not_found = []
for cid in target_ids:
    name = config_name_map.get(cid, None)
    if name:
        print("{}: {}".format(cid, name))
        found += 1
    else:
        not_found.append(cid)

print("\n找到 {}/{} 个".format(found, len(target_ids)))
if not_found:
    print("未找到: {}".format(not_found))

# 保存映射到 JSON
output = {cid: config_name_map.get(cid, "") for cid in target_ids}
output_path = os.path.join(os.path.dirname(__file__), 'config_name_map.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("\n映射已保存到: {}".format(output_path))
