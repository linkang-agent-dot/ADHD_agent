#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提交单个活动到 iGame - 参考已有活动的实际请求格式"""

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

# 参考已有活动请求体:
# {"activities":[{"acrossServer":1,"acrossServerRank":1,"activityConfigId":"21111121",
#   "endShowTime":1773619200000,"endTime":1773532800000,"id":7551,
#   "previewTime":1772926200000,"servers":[[...]],"startTime":1773014400000}]}

# 推币机 - 灰度服务器测试（只用灰度的12个服）
activity = {
    "acrossServer": 1,
    "acrossServerRank": 1,
    "activityConfigId": "21115696",
    "previewTime": 1773106200000,   # 2026-03-10 09:30 (开始前24.5h)
    "startTime": 1773194400000,     # 2026-03-11 10:00
    "endTime": 1774382400000,       # 2026-03-25 04:00
    "endShowTime": 1774468800000,   # 2026-03-26 04:00 (结束后24h)
    "servers": [[
        "2006502", "2054002", "2600202", "2010102", "2077002", "2060302",
        "2018202", "2023502", "2038602", "2047502", "2055802", "2024502"
    ]],
}

# 外层用 activities 数组包裹
payload = {"activities": [activity]}

print("=" * 60)
print("提交活动: 推币机 (21115696)")
print("接口: POST /ark/activity/submit")
print("服务器: {} 个 (灰度测试)".format(len(activity["servers"][0])))
print("=" * 60)
print()
print("请求体:")
print(json.dumps(payload, ensure_ascii=False, indent=2)[:500])
print()

url = API_HOST + "/ark/activity/submit"
print("发送请求: POST {}".format(url))

response = requests.post(url, json=payload, headers=headers, timeout=30)
print("HTTP 状态码: {}".format(response.status_code))
print()
print("响应内容:")
try:
    resp_data = response.json()
    print(json.dumps(resp_data, ensure_ascii=False, indent=2))
except:
    print(response.text)
