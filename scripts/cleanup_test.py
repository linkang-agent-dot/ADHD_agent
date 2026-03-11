#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""撤回并删除测试活动"""
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

# 撤回 + 删除测试活动 7553, 7554, 7555, 7556
for act_id in [7553, 7554, 7555, 7556]:
    # 先撤回 POST /ark/activity/recall/{id}
    url = "{}/ark/activity/recall/{}".format(API_HOST, act_id)
    resp = requests.post(url, headers=headers, timeout=15)
    print("撤回 {}: HTTP {} - {}".format(act_id, resp.status_code, resp.text[:200]))

print()

for act_id in [7553, 7554, 7555, 7556]:
    # 删除 DELETE /ark/activity/{ids}
    url = "{}/ark/activity/{}".format(API_HOST, act_id)
    resp = requests.delete(url, headers=headers, timeout=15)
    print("删除 {}: HTTP {} - {}".format(act_id, resp.status_code, resp.text[:200]))
