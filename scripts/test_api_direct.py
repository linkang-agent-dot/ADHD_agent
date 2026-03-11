#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接调用 iGame API 测试"""

import json
import os
import requests

# 读取认证信息
auth_file = os.path.expanduser("~/.igame-auth.json")
with open(auth_file, 'r', encoding='utf-8') as f:
    auth = json.load(f)

API_HOST = "https://webgw-cn.tap4fun.com"

# 测试数据 - 简化版，只用灰度服务器
test_payload = {
    "activityConfigId": "21115696",
    "name": "推币机",
    "previewTime": 1470,
    "startTime": 1773194400000,
    "endTime": 1774382400000,
    "endShowTime": 1440,
    "acrossServer": 1,
    "acrossServerRank": 1,
    "servers": [[
        "2006502", "2054002", "2600202", "2010102", "2077002", "2060302",
        "2018202", "2023502", "2038602", "2047502", "2055802", "2024502"
    ]],
    "remark": "2026科技节活动测试"
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {auth["token"]}',
    'clientid': auth['clientId'],
    'gameid': auth.get('gameId', '1041'),
    'regionid': auth.get('regionId', '201'),
    'origin': 'https://igame.tap4fun.com',
    'referer': 'https://igame.tap4fun.com/',
}

print("=" * 60)
print("测试 iGame 活动保存接口")
print("=" * 60)
print(f"API: {API_HOST}/ark/activity/add")
print(f"活动: {test_payload['name']} ({test_payload['activityConfigId']})")
print(f"服务器数量: {len(test_payload['servers'][0])}")
print()

# 发送请求
url = f"{API_HOST}/ark/activity/add"
print(f"发送 POST 请求到: {url}")
print(f"请求体: {json.dumps(test_payload, ensure_ascii=False)[:200]}...")
print()

try:
    response = requests.post(url, json=test_payload, headers=headers, timeout=30)
    print(f"HTTP 状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print()
    print("响应内容:")
    print(response.text)
except Exception as e:
    print(f"请求失败: {e}")
