#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确定位 submit 接口校验失败的原因：
1. 带 id 字段 + 已知有效 configId
2. 不带 id + 已知有效 configId
3. 带 id + 新 configId
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

# 测试用例
tests = [
    {
        "desc": "1) 有id(7551) + 已知configId(21111121) - 模拟已有活动重新提交",
        "body": {"activities": [{
            "id": 7551,
            "acrossServer": 1,
            "acrossServerRank": 1,
            "activityConfigId": "21111121",
            "previewTime": 1773106200000,
            "startTime": 1773194400000,
            "endTime": 1774382400000,
            "endShowTime": 1774468800000,
            "servers": [gray_servers],
        }]}
    },
    {
        "desc": "2) 无id + 已知configId(21111121) - 新建一个已有config的活动",
        "body": {"activities": [{
            "acrossServer": 1,
            "acrossServerRank": 1,
            "activityConfigId": "21111121",
            "previewTime": 1773106200000,
            "startTime": 1773194400000,
            "endTime": 1774382400000,
            "endShowTime": 1774468800000,
            "servers": [gray_servers],
        }]}
    },
    {
        "desc": "3) 无id + 新configId(21115696推币机)",
        "body": {"activities": [{
            "acrossServer": 1,
            "acrossServerRank": 1,
            "activityConfigId": "21115696",
            "previewTime": 1773106200000,
            "startTime": 1773194400000,
            "endTime": 1774382400000,
            "endShowTime": 1774468800000,
            "servers": [gray_servers],
        }]}
    },
    {
        "desc": "4) 无id + 不存在的configId(99999999)",
        "body": {"activities": [{
            "acrossServer": 1,
            "acrossServerRank": 1,
            "activityConfigId": "99999999",
            "previewTime": 1773106200000,
            "startTime": 1773194400000,
            "endTime": 1774382400000,
            "endShowTime": 1774468800000,
            "servers": [gray_servers],
        }]}
    },
]

url = API_HOST + "/ark/activity/submit"

for t in tests:
    print("=" * 60)
    print(t["desc"])
    resp = requests.post(url, json=t["body"], headers=headers, timeout=15)
    print("  HTTP {}: ".format(resp.status_code), end="")
    try:
        data = resp.json()
        print("success={}, message={}, code={}".format(
            data.get("success"), data.get("message"), data.get("code")))
        if data.get("data"):
            print("  data: {}".format(json.dumps(data["data"], ensure_ascii=False)[:300]))
    except:
        print(resp.text[:200])
    print()
