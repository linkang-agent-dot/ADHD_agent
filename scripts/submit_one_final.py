#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试: 用status=5(已部署)活动的完整数据来重新submit
排除所有数据格式问题
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

# 获取 7551 的详情并完全复原请求
print("=== 获取活动 7551 详情 ===")
resp = requests.get(API_HOST + "/ark/activity/7551/detail", headers=headers, timeout=10)
act = resp.json()["data"]

print("  name: {}".format(act["name"]))
print("  configId: {}".format(act["activityConfigId"]))
print("  status: {}".format(act["status"]))
print("  原始请求: {}".format(act["requests"][0]["data"][:200] if act.get("requests") else "无"))
print()

# 从原始请求中恢复
original_req = json.loads(act["requests"][0]["data"])
print("=== 原始请求体 ===")
print(json.dumps(original_req, ensure_ascii=False, indent=2))
print()

# 直接发送
print("=== 发送到 /ark/activity/submit ===")
resp = requests.post(API_HOST + "/ark/activity/submit",
    data=act["requests"][0]["data"],  # 用原始 JSON 字符串
    headers=headers, timeout=15)
print("HTTP {}: {}".format(resp.status_code, resp.text[:300]))

# 也试试不同的 Content-Type
print()
print("=== 尝试 application/json;charset=UTF-8 ===")
headers2 = dict(headers)
headers2['Content-Type'] = 'application/json;charset=UTF-8'
resp2 = requests.post(API_HOST + "/ark/activity/submit",
    data=act["requests"][0]["data"],
    headers=headers2, timeout=15)
print("HTTP {}: {}".format(resp2.status_code, resp2.text[:300]))

# 也试试不同的 gameid
print()
for gid in ["1041", "P2", ""]:
    headers3 = dict(headers)
    headers3['gameid'] = gid
    resp3 = requests.post(API_HOST + "/ark/activity/submit",
        data=act["requests"][0]["data"],
        headers=headers3, timeout=15)
    result = resp3.json()
    print("gameid={}: HTTP {} success={} msg={}".format(
        gid, resp3.status_code, result.get("success"), result.get("message")))
