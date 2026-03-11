#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用一个已有的草稿活动(status=1)来测试 submit 接口
这样可以确认接口格式是否正确
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

# 先获取一个草稿活动的完整详情
print("=" * 60)
print("Step 1: 获取草稿活动详情")

# 获取最近的草稿活动
url = API_HOST + "/ark/activity/list"
resp = requests.get(url, headers=headers, params={"pageIndex": 1, "pageSize": 5, "status": 1}, timeout=10)
data = resp.json()

for act in data.get("data", [])[:3]:
    print()
    print("  活动: {} (id={})".format(act["name"], act["id"]))
    print("  configId: {}".format(act["activityConfigId"]))
    print("  status: {}".format(act["status"]))
    print("  时间: {} ~ {}".format(act["startTime"], act["endTime"]))
    print("  跨服: {}".format(act["acrossServer"]))
    print("  服务器: {}".format(act.get("servers")))
    
    # 获取详情
    detail_url = API_HOST + "/ark/activity/{}/detail".format(act["id"])
    detail_resp = requests.get(detail_url, headers=headers, timeout=10)
    if detail_resp.status_code == 200:
        detail = detail_resp.json().get("data", {})
        print("  requests: {}".format(detail.get("requests")))
        print("  responses: {}".format(detail.get("responses")))

# 用第一个草稿活动试试 submit
print()
print("=" * 60)
print("Step 2: 尝试提交草稿活动")

first_draft = data["data"][0]
act_id = first_draft["id"]
act_name = first_draft["name"]
act_config = first_draft["activityConfigId"]

print("  选中活动: {} (id={}, configId={})".format(act_name, act_id, act_config))

# 构建和实际提交请求完全相同的格式
submit_body = {
    "activities": [{
        "id": act_id,
        "acrossServer": first_draft["acrossServer"],
        "acrossServerRank": first_draft["acrossServerRank"],
        "activityConfigId": act_config,
        "previewTime": first_draft["previewTime"] if first_draft["previewTime"] > 10000 else 1773106200000,
        "startTime": first_draft["startTime"],
        "endTime": first_draft["endTime"],
        "endShowTime": first_draft["endShowTime"] if first_draft["endShowTime"] > 10000 else 1774468800000,
        "servers": first_draft["servers"],
    }]
}

print("  请求体: {}".format(json.dumps(submit_body, ensure_ascii=False)[:500]))

submit_url = API_HOST + "/ark/activity/submit"
resp = requests.post(submit_url, json=submit_body, headers=headers, timeout=15)
print("  HTTP {}: {}".format(resp.status_code, resp.text[:300]))
