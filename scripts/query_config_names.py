#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 Google Sheet 读取完整活动数据 + 尝试 iGame 配置查询"""
import subprocess, json, os, sys, requests

sys.stdout.reconfigure(encoding='utf-8')

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8'

# Part 1: 读取 Google Sheet 更大范围，看有没有其他列有 iGame 名称
print("="*60)
print("Part 1: Google Sheet 完整表头和数据")
print("="*60)
params = json.dumps({
    'spreadsheetId': SPREADSHEET_ID,
    'range': '2026科技节上线checklist+甘特图（测试）!A1:AZ5'
})
cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params]
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
if result.returncode == 0:
    data = json.loads(result.stdout)
    rows = data.get('values', [])
    for i, row in enumerate(rows):
        print("Row {}: {}".format(i, row))
        print()

# Part 2: 尝试通过 iGame API 搜索配置名称
print("="*60)
print("Part 2: 尝试 iGame 接口查询 configId -> config name")
print("="*60)

auth_file = os.path.expanduser("~/.igame-auth.json")
with open(auth_file, 'r', encoding='utf-8') as f:
    auth = json.load(f)

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + auth['token'],
    'clientid': auth['clientId'],
    'gameid': auth.get('gameId', '1041'),
    'regionid': auth.get('regionId', '201'),
    'origin': 'https://igame.tap4fun.com',
    'referer': 'https://igame.tap4fun.com/',
}

API_HOST = "https://webgw-cn.tap4fun.com"

# 尝试获取已提交活动7554的完整详情，看有没有 configName 字段
url = "{}/ark/activity/{}/detail".format(API_HOST, 7554)
resp = requests.get(url, headers=headers, timeout=15)
data = resp.json()
if data.get('success') and data.get('data'):
    d = data['data']
    print("Activity 7554 full detail:")
    print(json.dumps(d, ensure_ascii=False, indent=2)[:1000])
else:
    print("7554 detail: FAIL - {}".format(data.get('message', resp.status_code)))
