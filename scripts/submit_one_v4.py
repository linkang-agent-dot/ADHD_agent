#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试不同的请求体格式"""

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

# 灰度服
gray_servers = ["2006502", "2054002", "2600202", "2010102", "2077002", "2060302",
                "2018202", "2023502", "2038602", "2047502", "2055802", "2024502"]

base_activity = {
    "acrossServer": 1,
    "acrossServerRank": 1,
    "activityConfigId": "21115696",
    "name": "推币机",
    "previewTime": 1773106200000,
    "startTime": 1773194400000,
    "endTime": 1774382400000,
    "endShowTime": 1774468800000,
    "servers": [gray_servers],
}

# 尝试不同的格式
formats = [
    ("格式1: activities数组+name", {"activities": [base_activity]}),
    ("格式2: 不带name", {"activities": [{k: v for k, v in base_activity.items() if k != "name"}]}),
    ("格式3: 直接传对象(不带activities)", base_activity),
    ("格式4: 带type字段", {"activities": [{**base_activity, "type": ""}]}),
    ("格式5: 带rule字段", {"activities": [{**base_activity, "rule": None, "customParam": None}]}),
    ("格式6: endShowTime=timestamp", {"activities": [{**base_activity, "endShowTime": 1774468800000}]}),
    ("格式7: previewTime=分钟", {"activities": [{**{k:v for k,v in base_activity.items()}, "previewTime": 1470, "endShowTime": 1440}]}),
]

for name, payload in formats:
    print("=" * 60)
    print("测试 {}".format(name))
    url = API_HOST + "/ark/activity/submit"
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    print("  状态码: {}".format(response.status_code))
    try:
        resp = response.json()
        msg = resp.get("message", "")
        success = resp.get("success", False)
        print("  success: {}  message: {}".format(success, msg))
        if success:
            print("  >>> 完整响应: {}".format(json.dumps(resp, ensure_ascii=False, indent=2)[:500]))
    except:
        print("  响应: {}".format(response.text[:200]))
    print()
