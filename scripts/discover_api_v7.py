#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""搜索 chunk JS 中的 API host 配置"""
import re
import requests

# 检查 4292 chunk
for js_file in ["4292.5a753d73.js", "index.a32e59b9.js", "runtime.75f33eae.js"]:
    url = "https://igame.tap4fun.com/static/js/" + js_file
    resp = requests.get(url, timeout=15)
    content = resp.text
    
    # 搜索 URL/host 配置
    hosts = re.findall(r'["\'](https?://[^"\']+\.tap4fun\.com[^"\']*)["\']', content)
    if hosts:
        print("=== {} ===".format(js_file))
        for h in sorted(set(hosts)):
            print("  {}".format(h))
    
    # 搜索 webgw 相关
    webgw = re.findall(r'webgw[^"\']*', content)
    if webgw:
        print("  webgw: {}".format(sorted(set(webgw))[:5]))
    
    # 搜索 fetch/request/axios 配置
    fetch_config = re.findall(r'fetch\s*\(\s*["\'](https?://[^"\']+)', content)
    if fetch_config:
        print("  fetch hosts: {}".format(sorted(set(fetch_config))))
    
    # 搜索环境变量或 API_URL 配置
    env_vars = re.findall(r'(?:API_URL|BASE_URL|API_HOST|GATEWAY)["\s:=]*["\'](https?://[^"\']+)["\']', content, re.IGNORECASE)
    if env_vars:
        print("  env vars: {}".format(sorted(set(env_vars))))
    
    print()

# 同时直接测试: 前端是不是通过 igame.tap4fun.com 本身做代理?
print("=== 测试 igame.tap4fun.com 作为 API 代理 ===")

import json, os
auth_file = os.path.expanduser("~/.igame-auth.json")
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

body = {"activityConfigId": "21115696", "name": "test", "previewTime": 1773106200000,
        "startTime": 1773194400000, "endTime": 1774382400000, "endShowTime": 1774468800000,
        "acrossServer": 1, "acrossServerRank": 1, "servers": [["2006502"]]}

# 试试 igame.tap4fun.com 本身
for path in ["/api/activity/add", "/api/ark/activity/add", "/gateway/activity/add", "/proxy/activity/add"]:
    try:
        r = requests.post("https://igame.tap4fun.com" + path, json=body, headers=headers, timeout=8)
        print("  POST igame.tap4fun.com{} -> {} {}".format(path, r.status_code, r.text[:100]))
    except:
        pass

# 试试 webgw-cn 但不加 /ark 前缀
for path in ["/activity/add", "/activity/submit"]:
    try:
        r = requests.post("https://webgw-cn.tap4fun.com" + path, json=body, headers=headers, timeout=8)
        print("  POST webgw-cn{} -> {} {}".format(path, r.status_code, r.text[:100]))
    except:
        pass
