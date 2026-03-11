#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提交2个活动到 iGame"""

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

gray_servers = ["2006502", "2054002", "2600202", "2010102", "2077002", "2060302",
                "2018202", "2023502", "2038602", "2047502", "2055802", "2024502"]

activities = [
    {
        "activityConfigId": "21115731",
        "name": "主城特效累充-联盟版",
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
        "name": "手札",
        "acrossServer": 0,
        "acrossServerRank": 0,
        "previewTime": 0,
        "startTime": 1773194400000,
        "endTime": 1774382400000,
        "endShowTime": 0,
        "servers": [gray_servers],
    },
]

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
