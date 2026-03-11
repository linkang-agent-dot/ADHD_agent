#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目标: 找到"保存活动"(创建草稿)的正确接口
已知: /activity/add 返回404, /activity/submit 是部署接口
尝试更多可能的路径
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

gray_servers = ["2006502", "2054002", "2600202"]
test_body = {
    "activityConfigId": "21115696",
    "name": "推币机",
    "previewTime": 1773106200000,
    "startTime": 1773194400000,
    "endTime": 1774382400000,
    "endShowTime": 1774468800000,
    "acrossServer": 1,
    "acrossServerRank": 1,
    "servers": [gray_servers],
}

# 也带 activities 包裹的版本
test_body_wrapped = {"activities": [test_body]}

# 所有可能的 POST 端点
paths_post = [
    # 原始路径变体
    ("/ark/activity/add", test_body),
    ("/ark/activity/add", test_body_wrapped),
    ("/ark/activity/save", test_body),
    ("/ark/activity/save", test_body_wrapped),
    ("/ark/activity/draft", test_body),
    ("/ark/activity/create", test_body),
    # 可能的 v2 路径
    ("/ark/activity/config/add", test_body),
    ("/ark/activity/config/save", test_body),
    # PUT 方法
]

paths_put = [
    ("/ark/activity/add", test_body),
    ("/ark/activity/add", test_body_wrapped),
    ("/ark/activity/save", test_body),
]

print("=== POST 测试 ===")
for path, body in paths_post:
    url = API_HOST + path
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=8)
        status = resp.status_code
        try:
            data = resp.json()
            msg = data.get("message", data.get("error", ""))
            success = data.get("success", "")
            marker = " ** 非404 **" if status != 404 else ""
            print("  POST {} -> {} | success={} msg={}{}".format(
                path, status, success, msg[:60], marker))
        except:
            print("  POST {} -> {} | {}".format(path, status, resp.text[:80]))
    except Exception as e:
        print("  POST {} -> ERR {}".format(path, str(e)[:40]))

print()
print("=== PUT 测试 ===")
for path, body in paths_put:
    url = API_HOST + path
    try:
        resp = requests.put(url, json=body, headers=headers, timeout=8)
        status = resp.status_code
        try:
            data = resp.json()
            msg = data.get("message", data.get("error", ""))
            success = data.get("success", "")
            marker = " ** 非404 **" if status != 404 else ""
            print("  PUT {} -> {} | success={} msg={}{}".format(
                path, status, success, msg[:60], marker))
        except:
            print("  PUT {} -> {} | {}".format(path, status, resp.text[:80]))
    except Exception as e:
        print("  PUT {} -> ERR {}".format(path, str(e)[:40]))

# 看看 operation 子模块
print()
print("=== operation 子模块测试 ===")
op_paths = [
    ("/ark/activity/batch_submit", {"ids": [365], "reason": "测试提交"}),
    ("/ark/activity/batch/submit", {"ids": [365], "reason": "测试提交"}),
    ("/ark/activity/apply", {"ids": [365], "reason": "测试提交"}),
    ("/ark/activity/batch_deploy", {"ids": [365]}),
    ("/ark/activity/deploy", {"activities": [{"id": 365}]}),
]
for path, body in op_paths:
    url = API_HOST + path
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=8)
        status = resp.status_code
        try:
            data = resp.json()
            msg = data.get("message", data.get("error", ""))
            success = data.get("success", "")
            marker = " ** 非404 **" if status != 404 else ""
            print("  POST {} -> {} | success={} msg={}{}".format(
                path, status, success, msg[:60], marker))
        except:
            print("  POST {} -> {} | {}".format(path, status, resp.text[:80]))
    except Exception as e:
        print("  POST {} -> ERR {}".format(path, str(e)[:40]))
