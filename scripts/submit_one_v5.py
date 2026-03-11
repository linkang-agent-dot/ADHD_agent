#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用已知存在的 activityConfigId 验证接口格式"""

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

# ---- 测试 1: 用已有活动 ID 查询活动类型列表 ----
print("=" * 60)
print("测试1: 查询活动类型列表")
url = API_HOST + "/ark/activity/type/query"
resp = requests.get(url, headers=headers, timeout=15)
print("  状态码: {}".format(resp.status_code))
if resp.status_code == 200:
    data = resp.json()
    print("  结果: {}".format(json.dumps(data, ensure_ascii=False)[:500]))
print()

# ---- 测试 2: 用已存在的活动 (id=7551) 来看它的完整数据 ----
print("=" * 60)
print("测试2: 查看已有活动7551的详情")
url = API_HOST + "/ark/activity/7551/detail"
resp = requests.get(url, headers=headers, timeout=15)
print("  状态码: {}".format(resp.status_code))
if resp.status_code == 200:
    data = resp.json()
    if data.get("data"):
        act = data["data"]
        print("  name: {}".format(act.get("name")))
        print("  activityConfigId: {}".format(act.get("activityConfigId")))
        print("  status: {}".format(act.get("status")))
        print("  previewTime: {}".format(act.get("previewTime")))
        print("  startTime: {}".format(act.get("startTime")))
        print("  endTime: {}".format(act.get("endTime")))
        print("  endShowTime: {}".format(act.get("endShowTime")))
        print("  acrossServer: {}".format(act.get("acrossServer")))
        # 提取实际请求体
        if act.get("requests"):
            req_data = json.loads(act["requests"][0]["data"])
            print("\n  实际提交时的请求体:")
            print("  {}".format(json.dumps(req_data, ensure_ascii=False, indent=4)))
print()

# ---- 测试 3: 尝试用相同格式提交新的 activityConfigId ----
# 先看看 21115696 是否能在其他地方找到
print("=" * 60)
print("测试3: 搜索活动 21115696 是否在列表中")
url = API_HOST + "/ark/activity/list"
params_search = {"pageIndex": 1, "pageSize": 100, "activityConfigId": "21115696"}
resp = requests.get(url, headers=headers, params=params_search, timeout=15)
if resp.status_code == 200:
    data = resp.json()
    print("  总数: {}".format(data.get("total")))
    if data.get("data"):
        for item in data["data"]:
            if item.get("activityConfigId") == "21115696":
                print("  找到! id={}, name={}, status={}".format(
                    item["id"], item["name"], item["status"]))
    else:
        print("  未找到 activityConfigId=21115696 的活动")

# 也用 name 搜索
params_name = {"pageIndex": 1, "pageSize": 10, "name": "推币机"}
resp2 = requests.get(url, headers=headers, params=params_name, timeout=15)
if resp2.status_code == 200:
    data2 = resp2.json()
    print("\n  按名称搜索 '推币机': 总数={}".format(data2.get("total")))
    if data2.get("data"):
        for item in data2["data"][:5]:
            print("    id={}, configId={}, name={}, status={}".format(
                item["id"], item["activityConfigId"], item["name"], item["status"]))
print()

# ---- 测试 4: 用已知有效的 configId 试试格式 ----
print("=" * 60)
print("测试4: 用已知有效 configId 21111121 (最强猴子) 试格式")
print("  注意: 仅验证格式，用3个灰度服")
test_activity = {
    "acrossServer": 1,
    "acrossServerRank": 1,
    "activityConfigId": "21111121",
    "previewTime": 1773106200000,
    "startTime": 1773194400000,
    "endTime": 1774382400000,
    "endShowTime": 1774468800000,
    "servers": [["2006502", "2054002", "2600202"]],
}
payload = {"activities": [test_activity]}
url = API_HOST + "/ark/activity/submit"
resp = requests.post(url, json=payload, headers=headers, timeout=15)
print("  状态码: {}".format(resp.status_code))
try:
    rdata = resp.json()
    print("  success: {}  message: {}".format(rdata.get("success"), rdata.get("message")))
    if rdata.get("success") or rdata.get("data"):
        print("  >>> {}".format(json.dumps(rdata, ensure_ascii=False, indent=2)[:500]))
except:
    print("  响应: {}".format(resp.text[:300]))
