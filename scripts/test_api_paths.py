#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试不同的 API 路径"""

import json
import os
import requests

auth_file = os.path.expanduser("~/.igame-auth.json")
with open(auth_file, 'r', encoding='utf-8') as f:
    auth = json.load(f)

API_HOST = "https://webgw-cn.tap4fun.com"

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {auth["token"]}',
    'clientid': auth['clientId'],
    'gameid': auth.get('gameId', '1041'),
    'regionid': auth.get('regionId', '201'),
    'origin': 'https://igame.tap4fun.com',
    'referer': 'https://igame.tap4fun.com/',
}

test_payload = {
    "activityConfigId": "21115696",
    "name": "推币机",
    "previewTime": 1470,
    "startTime": 1773194400000,
    "endTime": 1774382400000,
    "endShowTime": 1440,
    "acrossServer": 1,
    "acrossServerRank": 1,
    "servers": [["2006502", "2054002", "2600202"]],
}

# 尝试不同的路径
paths_to_try = [
    "/ark/activity/add",
    "/ark/activity/save",
    "/ark/activity/create",
    "/ark/activities/add",
    "/ark/v1/activity/add",
    "/ark/api/activity/add",
]

print("测试不同的 API 路径...")
print("=" * 60)

for path in paths_to_try:
    url = f"{API_HOST}{path}"
    print(f"\n尝试: {url}")
    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=10)
        print(f"  状态码: {response.status_code}")
        if response.status_code != 404:
            print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"  错误: {e}")

# 也测试一下 GET 请求看看有哪些可用的端点
print("\n" + "=" * 60)
print("测试 GET 端点...")

get_paths = [
    "/ark/activity/list?pageIndex=1&pageSize=1",
    "/ark/activity/types",
    "/ark/activity/config",
]

for path in get_paths:
    url = f"{API_HOST}{path}"
    print(f"\n尝试: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  成功! 数据: {str(data)[:200]}...")
    except Exception as e:
        print(f"  错误: {e}")
