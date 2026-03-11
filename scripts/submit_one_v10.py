#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全复制已成功提交过的活动7551的请求体，原样发送
如果这也失败，说明是权限/网关问题
"""

import json
import os
import requests

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

# 这是活动7551实际成功提交时的原始请求体（从 responses 中提取）
original_request = {
    "activities": [{
        "acrossServer": 1,
        "acrossServerRank": 1,
        "activityConfigId": "21111121",
        "endShowTime": 1773619200000,
        "endTime": 1773532800000,
        "id": 7551,
        "previewTime": 1772926200000,
        "servers": [["2089802", "2090002", "2090402"]],
        "startTime": 1773014400000,
    }]
}

print("=" * 60)
print("完全复制已成功请求体测试")
print("=" * 60)
print("原始请求体:")
print(json.dumps(original_request, ensure_ascii=False, indent=2))
print()

# 发送到 submit
url = API_HOST + "/ark/activity/submit"
print("POST {}".format(url))
resp = requests.post(url, json=original_request, headers=headers, timeout=15)
print("HTTP {}: {}".format(resp.status_code, resp.text[:300]))

# 也发送原始 JSON 字符串（不经过 Python 的 json 处理）
print()
print("=" * 60)
print("发送原始 JSON 字符串")
raw_json = '{"activities":[{"acrossServer":1,"acrossServerRank":1,"activityConfigId":"21111121","endShowTime":1773619200000,"endTime":1773532800000,"id":7551,"previewTime":1772926200000,"servers":[["2089802","2090002","2090402"]],"startTime":1773014400000}]}'
print(raw_json)
print()
resp2 = requests.post(url, data=raw_json, headers=headers, timeout=15)
print("HTTP {}: {}".format(resp2.status_code, resp2.text[:300]))

# 尝试检查当前用户有哪些菜单权限
print()
print("=" * 60)
print("检查菜单权限")
menu_url = API_HOST + "/ark/menu/list"
resp3 = requests.get(menu_url, headers=headers, timeout=10)
if resp3.status_code == 200:
    menus = resp3.json()
    if menus.get("data"):
        for m in menus["data"]:
            name = m.get("name", "")
            if "活动" in name or "activity" in name.lower():
                print("  菜单: {} | path={} | id={}".format(
                    name, m.get("path", ""), m.get("id", "")))
                children = m.get("children", [])
                for c in children:
                    print("    子菜单: {} | path={}".format(
                        c.get("name", ""), c.get("path", "")))
