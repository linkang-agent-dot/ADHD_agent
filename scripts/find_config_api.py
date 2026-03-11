#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""尝试通过 toolbox 或 game API 查询配置名称"""
import json, os, requests, sys

sys.stdout.reconfigure(encoding='utf-8')

auth_file = os.path.expanduser("~/.igame-auth.json")
with open(auth_file, 'r', encoding='utf-8') as f:
    auth = json.load(f)

API_HOST = "https://webgw-cn.tap4fun.com"
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + auth["token"],
    'clientid': auth['clientId'],
    'gameid': auth.get('gameId', '1041'),
    'regionid': auth.get('regionId', '201'),
    'origin': 'https://igame.tap4fun.com',
    'referer': 'https://igame.tap4fun.com/',
}

config_id = "21115731"

# 方向1: toolbox 模块可能有配置查询
import subprocess
result = subprocess.run(
    ["node", r"C:\Users\linkang\.agents\skills\igame-skill\scripts\igame-query.js", "ls", "toolbox"],
    capture_output=True, text=True, encoding='utf-8'
)
print("=== toolbox 模块 ===")
print(result.stdout[:1000])

# 方向2: 直接尝试游戏服务器 API
game_endpoints = [
    "/ark/toolbox/activityConfig/" + config_id,
    "/ark/toolbox/config/" + config_id,
    "/ark/toolbox/activity-config?configId=" + config_id,
    "/ark/activity/checkConfig?activityConfigId=" + config_id,
    "/ark/activity/check?activityConfigId=" + config_id,
]

print("\n=== 尝试游戏配置接口 ===")
for ep in game_endpoints:
    url = API_HOST + ep
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print("{}: {}".format(ep, json.dumps(data, ensure_ascii=False)[:400]))
    elif resp.status_code == 500:
        data = resp.json()
        print("{}: 500 - {}".format(ep, data.get('message', '')[:150]))
    else:
        pass

# 方向3: 看看 /ark/activity/export 能不能导出配置信息
print("\n=== 尝试 export ===")
url = API_HOST + "/ark/activity/export"
resp = requests.get(url, headers=headers, params={"page": 1, "size": 5}, timeout=15)
print("export: HTTP {} content-type={}".format(resp.status_code, resp.headers.get('content-type', '')))
if resp.status_code == 200 and 'json' in resp.headers.get('content-type', ''):
    print(resp.text[:500])
