#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查当前账号权限"""

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

# 1. 用户信息
print("=== 用户信息 ===")
resp = requests.get(API_HOST + "/ark/user/current", headers=headers, timeout=10)
user = resp.json().get("data", {})
print("  ID: {}".format(user.get("id")))
print("  姓名: {}".format(user.get("name")))
print("  邮箱: {}".format(user.get("email")))
print("  部门: {}".format(user.get("departName")))
print("  子部门: {}".format(user.get("departSubName")))
print()

# 2. 菜单权限
print("=== 菜单权限 ===")
resp = requests.get(API_HOST + "/ark/menu/list", headers=headers, timeout=10)
menus = resp.json()
if menus.get("data"):
    for m in menus["data"]:
        print("  {} (path={})".format(m.get("name", ""), m.get("path", "")))
        for c in m.get("children", []):
            print("    - {} (path={})".format(c.get("name", ""), c.get("path", "")))
else:
    print("  菜单数据: {}".format(json.dumps(menus, ensure_ascii=False)[:300]))
print()

# 3. 用户权限/角色
print("=== 权限/角色检查 ===")
role_paths = [
    "/ark/competenceMng/user/info",
    "/ark/admin/user/role",
    "/ark/admin/user/1957",
    "/ark/user/role",
    "/ark/admin/employee/1957",
]
for p in role_paths:
    try:
        resp = requests.get(API_HOST + p, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print("  {} -> {}".format(p, json.dumps(data, ensure_ascii=False)[:300]))
    except:
        pass
print()

# 4. 测试一个已知可以写的接口（如服务器权重修改）来确认写权限
print("=== 写权限测试(不实际执行) ===")
# 只是测试一下 OPTIONS 请求
for p in ["/ark/activity/submit", "/ark/activity/add", "/ark/flow/server"]:
    url = API_HOST + p
    try:
        resp = requests.options(url, headers=headers, timeout=5)
        print("  OPTIONS {} -> {} | Allow: {}".format(
            p, resp.status_code, resp.headers.get("Allow", "N/A")))
    except:
        pass
