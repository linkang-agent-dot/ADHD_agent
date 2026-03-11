#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 2111 表的正确名称提交 2 个活动"""
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

gray_servers = ["2006502", "2054002", "2600202", "2010102", "2077002", "2060302",
                "2018202", "2023502", "2038602", "2047502", "2055802", "2024502"]

# 先删除之前的测试活动（已撤回的状态）
print("=== 清理之前的测试活动 ===")
url = API_HOST + "/ark/activity/list"
resp = requests.get(url, headers=headers, params={"page": 1, "size": 10}, timeout=15)
data = resp.json()
if data.get('success') and isinstance(data.get('data'), list):
    for act in data['data']:
        if act.get('status') == 19 and act['id'] in [7553, 7554, 7555, 7556]:
            del_url = "{}/ark/activity/{}".format(API_HOST, act['id'])
            del_resp = requests.delete(del_url, headers=headers, timeout=10)
            print("删除 {} ({}): HTTP {}".format(act['id'], act.get('name', ''), del_resp.status_code))

# 用 2111 表的正确名称提交
activities = [
    {
        "activityConfigId": "21115731",
        "name": "26科技节-主城特效累充-联盟团购",
        "acrossServer": 1,
        "acrossServerRank": 0,
        "previewTime": 0,
        "startTime": 1773194400000,
        "endTime": 1774382400000,
        "endShowTime": 0,
        "servers": [gray_servers],
    },
    {
        "activityConfigId": "21115740",
        "name": "26科技节-节日手札",
        "acrossServer": 0,
        "acrossServerRank": 0,
        "previewTime": 0,
        "startTime": 1773194400000,
        "endTime": 1774382400000,
        "endShowTime": 0,
        "servers": [gray_servers],
    },
]

print("\n=== 提交活动 ===")
url = API_HOST + "/ark/activity/submit"

for act in activities:
    print("提交: {} ({})".format(act["name"], act["activityConfigId"]))
    resp = requests.post(url, json=[act], headers=headers, timeout=30)
    data = resp.json()
    if data.get("success"):
        print("  成功! iGame ID: {}".format(data["data"]))
    else:
        print("  失败: {}".format(data.get("message")))
    print()
