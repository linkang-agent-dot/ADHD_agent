#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接从 iGame 前端代码中发现 API 端点
"""

import json
import os
import re
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

# 1. 获取 iGame 首页，找到 JS bundle
print("=== 获取 iGame 前端 JS ===")
resp = requests.get("https://igame.tap4fun.com/", timeout=15)
print("首页状态: {}".format(resp.status_code))

# 提取 JS 文件链接
js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', resp.text)
print("找到 {} 个 JS 文件".format(len(js_files)))
for jf in js_files[:10]:
    print("  {}".format(jf))

# 2. 下载 JS 文件，搜索 activity/add 相关的 API 路径
print()
print("=== 搜索 activity 相关 API 路径 ===")
for jf in js_files:
    if not jf.startswith("http"):
        jf = "https://igame.tap4fun.com" + jf
    try:
        js_resp = requests.get(jf, timeout=15)
        if js_resp.status_code == 200:
            content = js_resp.text
            # 搜索 activity 相关的路径
            patterns = re.findall(r'["\'](/(?:ark/)?activity/[a-zA-Z_/]+)["\']', content)
            if patterns:
                unique_patterns = sorted(set(patterns))
                print("  {} 中找到:".format(jf.split("/")[-1][:50]))
                for p in unique_patterns:
                    print("    {}".format(p))
    except Exception as e:
        print("  获取 {} 失败: {}".format(jf[:50], str(e)[:40]))
