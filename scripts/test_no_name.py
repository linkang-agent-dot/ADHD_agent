#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试不传 name 或传空 name 提交活动"""
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

# 先把之前提交的 7554 和 7555 撤回/删除
print("=== 先撤回 7554 和 7555 ===")
for act_id in [7554, 7555]:
    url = "{}/ark/activity/recall".format(API_HOST)
    resp = requests.post(url, json={"ids": [act_id]}, headers=headers, timeout=15)
    data = resp.json()
    print("撤回 {}: {}".format(act_id, json.dumps(data, ensure_ascii=False)[:200]))

# 再删除
print("\n=== 删除 7554 和 7555 ===")
for act_id in [7554, 7555]:
    url = "{}/ark/activity/{}".format(API_HOST, act_id)
    resp = requests.delete(url, headers=headers, timeout=15)
    print("删除 {}: HTTP {} - {}".format(act_id, resp.status_code, resp.text[:200]))

# 测试: 不带 name 提交
print("\n=== 测试: 不带 name 提交 21115731 ===")
payload_no_name = [{
    "activityConfigId": "21115731",
    "acrossServer": 1,
    "acrossServerRank": 0,
    "previewTime": 0,
    "startTime": 1773194400000,
    "endTime": 1774382400000,
    "endShowTime": 0,
    "servers": [gray_servers],
}]

url = API_HOST + "/ark/activity/submit"
resp = requests.post(url, json=payload_no_name, headers=headers, timeout=30)
data = resp.json()
print("不带name: {}".format(json.dumps(data, ensure_ascii=False)[:300]))

if data.get('success') and data.get('data'):
    new_id = data['data'][0] if isinstance(data['data'], list) else data['data']
    # 查看创建出来的活动name是什么
    url2 = "{}/ark/activity/{}/detail".format(API_HOST, new_id)
    resp2 = requests.get(url2, headers=headers, timeout=15)
    d2 = resp2.json()
    if d2.get('success') and d2.get('data'):
        print("新活动 {} name='{}'".format(new_id, d2['data'].get('name', '')))
