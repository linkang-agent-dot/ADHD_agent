#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用正确的格式提交活动 - 直接传数组，不包裹 activities"""

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

# 推币机 - 用灰度服务器测试
payload = [{
    "activityConfigId": "21115696",
    "name": "推币机",
    "acrossServer": 1,
    "acrossServerRank": 0,
    "previewTime": 0,
    "startTime": 1773194400000,    # 2026-03-11 10:00
    "endTime": 1774382400000,      # 2026-03-25 04:00
    "endShowTime": 0,
    "servers": [["2006502", "2054002", "2600202", "2010102", "2077002", "2060302",
                 "2018202", "2023502", "2038602", "2047502", "2055802", "2024502"]],
}]

print("提交活动: 推币机 (21115696)")
print("请求体: " + json.dumps(payload, ensure_ascii=False)[:300])
print()

url = API_HOST + "/ark/activity/submit"
resp = requests.post(url, json=payload, headers=headers, timeout=30)
print("HTTP {}: ".format(resp.status_code))
try:
    data = resp.json()
    print(json.dumps(data, ensure_ascii=False, indent=2)[:500])
except:
    print(resp.text[:500])
