#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
换一个思路：
1. 先搜索是否有 status=1 (已保存/草稿) 状态的活动
2. 尝试用 batch_submit 提交
3. 检查权限相关接口
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

# ---- 1. 查看当前用户信息和权限 ----
print("=" * 60)
print("1) 查看当前用户信息")
for path in ["/ark/user/info", "/ark/admin/info", "/ark/user/current", "/ark/menu/list"]:
    url = API_HOST + path
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print("  {} -> {}".format(path, json.dumps(data, ensure_ascii=False)[:300]))
    except:
        pass
print()

# ---- 2. 搜索已保存(草稿)状态的活动 ----
print("=" * 60)
print("2) 搜索不同状态的活动")
for status in [1, 2, 3, 4, 5]:
    url = API_HOST + "/ark/activity/list"
    params = {"pageIndex": 1, "pageSize": 3, "status": status}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    data = resp.json()
    total = data.get("total", 0)
    items = data.get("data", [])
    names = ", ".join(["{} (id={})".format(a.get("name",""), a.get("id","")) for a in items[:3]])
    print("  status={}: 共{}条 | {}".format(status, total, names[:100]))
print()

# ---- 3. 尝试 batch_submit ----
print("=" * 60)
print("3) 尝试 batch_submit 接口")
# 找一个 status=1 的活动ID
url = API_HOST + "/ark/activity/list"
resp = requests.get(url, headers=headers, params={"pageIndex": 1, "pageSize": 5, "status": 1}, timeout=10)
data = resp.json()
if data.get("data"):
    draft_id = data["data"][0]["id"]
    draft_name = data["data"][0]["name"]
    print("  找到草稿活动: {} (id={})".format(draft_name, draft_id))
    
    # 尝试提交
    submit_url = API_HOST + "/ark/activity/batch_submit"
    submit_body = {"ids": [draft_id], "reason": "测试提交"}
    resp2 = requests.post(submit_url, json=submit_body, headers=headers, timeout=15)
    print("  batch_submit 结果: {} {}".format(resp2.status_code, resp2.text[:200]))
else:
    print("  没有草稿状态的活动")

# ---- 4. 查看权限 ----
print()
print("=" * 60)
print("4) 查看权限信息")
for path in ["/ark/competence/user/competence", "/ark/competence/list", "/ark/admin/roles", "/ark/admin/permissions"]:
    url = API_HOST + path
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print("  {} -> {}".format(path, json.dumps(data, ensure_ascii=False)[:200]))
        else:
            print("  {} -> HTTP {}".format(path, resp.status_code))
    except:
        pass
