#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尝试更多可能的接口路径和请求格式
- 可能 /activity/add 前端实际用的是另一个网关路径
- 可能需要 /ark/v2/activity/add 或 /ark/api/v1/activity/add 等
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

gray_servers = ["2006502", "2054002", "2600202"]

activity_body = {
    "activities": [{
        "acrossServer": 1,
        "acrossServerRank": 1,
        "activityConfigId": "21115696",
        "previewTime": 1773106200000,
        "startTime": 1773194400000,
        "endTime": 1774382400000,
        "endShowTime": 1774468800000,
        "servers": [gray_servers],
    }]
}

# 测试更多路径变体
paths = [
    "/ark/activity/add",
    "/ark/activity/save",
    "/ark/activity-config/add",
    "/ark/activity-config/save",
    "/ark/activities",
    "/ark/v2/activity/add",
    "/ark/event/add",
    "/ark/event/save",
    "/api/activity/add",
    "/activity/add",
    # 也许前端是直接 igame.tap4fun.com 而不是 webgw-cn
]

print("=" * 60)
print("测试多种路径变体 (POST)")
print("=" * 60)

for p in paths:
    url = API_HOST + p
    try:
        resp = requests.post(url, json=activity_body, headers=headers, timeout=8)
        status = resp.status_code
        try:
            data = resp.json()
            msg = data.get("message", data.get("error", ""))
            success = data.get("success", "")
            flag = " <<<< 有效!" if status != 404 and success != False else ""
            print("  {} {} | success={} msg={}{}".format(status, p, success, msg[:60], flag))
        except:
            print("  {} {} | {}".format(status, p, resp.text[:80]))
    except Exception as e:
        print("  ERR {} | {}".format(p, str(e)[:60]))

# 也试试 igame.tap4fun.com 直接
print("\n" + "=" * 60)
print("测试 igame.tap4fun.com 直接访问")
print("=" * 60)

alt_hosts = [
    "https://igame.tap4fun.com",
    "https://igame-api.tap4fun.com",
]

for host in alt_hosts:
    for p in ["/ark/activity/add", "/api/activity/add", "/activity/add"]:
        url = host + p
        try:
            resp = requests.post(url, json=activity_body, headers=headers, timeout=8)
            status = resp.status_code
            try:
                data = resp.json()
                msg = data.get("message", data.get("error", ""))
                print("  {} {} | msg={}".format(status, url, msg[:80]))
            except:
                print("  {} {} | {}".format(status, url, resp.text[:80]))
        except Exception as e:
            print("  ERR {} | {}".format(url, str(e)[:40]))
