#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接搜索请求函数 (0,x.A) 或 (0,C.A) 的实际实现，找到 base URL"""
import re
import requests

url = "https://igame.tap4fun.com/static/js/index.a32e59b9.js"
resp = requests.get(url, timeout=15)
content = resp.text

# 从上下文得知 x.A 和 C.A 是请求函数
# 找到 2365 模块 (t(2365) 被赋值给 x/e)
# 也找 62557 模块

# 搜索模块定义 - webpack 格式通常是 62557:e=>{...} 或 62557:(e,t)=>{...}
for mod_id in ["62557", "2365"]:
    # 找到模块的位置
    # webpack 格式: ,62557:(e,t,n)=>{...} 或 62557:e=>{...}
    pat = r',?' + mod_id + r'\s*:\s*(?:\(([^)]*)\)\s*=>|function\s*\(([^)]*)\))\s*\{'
    match = re.search(pat, content)
    if match:
        start = match.start()
        # 获取模块内容 (找到匹配的 })
        snippet = content[start:start+2000]
        print("=== 模块 {} ===".format(mod_id))
        print(snippet[:1000])
        print("...")
        print()

# 也搜索 fetch 或 request 函数中的 baseURL/host 配置
# iGame 使用的是 igame-cn.tap4fun.com
igame_cn = re.findall(r'igame-cn\.tap4fun\.com[^"\']*', content)
print("igame-cn 引用: {}".format(igame_cn[:5]))

# 测试 igame-cn.tap4fun.com 网关
print("\n=== 测试 igame-cn.tap4fun.com 网关 ===")
auth_file = __import__("os").path.expanduser("~/.igame-auth.json")
import json
with open(auth_file, 'r', encoding='utf-8') as f:
    auth = json.load(f)

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + auth["token"],
    'clientid': auth['clientId'],
    'gameid': '1041',
    'regionid': '201',
    'origin': 'https://igame.tap4fun.com',
    'referer': 'https://igame.tap4fun.com/',
}

# 在 igame-cn.tap4fun.com 上测试
test_host = "https://igame-cn.tap4fun.com"
test_paths = [
    "/activity/list?pageIndex=1&pageSize=1",
    "/activity/add",
    "/activity/submit",
    "/ark/activity/list?pageIndex=1&pageSize=1",
    "/ark/activity/add",
]

gray_servers = ["2006502", "2054002", "2600202"]
body = {
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

for path in test_paths:
    full_url = test_host + path
    try:
        if "list" in path:
            r = requests.get(full_url, headers=headers, timeout=10)
        else:
            r = requests.post(full_url, json=body, headers=headers, timeout=10)
        print("  {} {} -> {} {}".format(
            "GET" if "list" in path else "POST",
            path, r.status_code, r.text[:120]))
    except Exception as e:
        print("  {} -> ERR: {}".format(path, str(e)[:60]))
