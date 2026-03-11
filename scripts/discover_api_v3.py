#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""搜索前端 JS 中的 API base URL 和 axios 配置"""
import re
import requests

url = "https://igame.tap4fun.com/static/js/index.a32e59b9.js"
resp = requests.get(url, timeout=15)
content = resp.text

# 搜索 base URL / axios 配置
base_patterns = re.findall(r'baseURL["\s:]*["\'](https?://[^"\']+)["\']', content)
api_patterns = re.findall(r'["\'](https?://[^"\']*(?:webgw|api|gateway|igame)[^"\']*)["\']', content)
prefix_patterns = re.findall(r'prefix["\s:]*["\'](/[^"\']+)["\']', content)

print("=== baseURL ===")
for p in sorted(set(base_patterns)):
    print("  {}".format(p))

print("\n=== API hosts ===")
for p in sorted(set(api_patterns)):
    print("  {}".format(p))

print("\n=== prefix ===")
for p in sorted(set(prefix_patterns)):
    print("  {}".format(p))

# 搜索 activity/add 附近的代码
idx = content.find("activity/add")
if idx >= 0:
    snippet = content[max(0,idx-200):idx+200]
    # 使可读
    print("\n=== activity/add 上下文 ===")
    print(snippet)

# 搜索 activity/submit 附近的代码
idx2 = content.find("activity/submit")
if idx2 >= 0:
    snippet2 = content[max(0,idx2-200):idx2+200]
    print("\n=== activity/submit 上下文 ===")
    print(snippet2)

# 搜索 batch_submit 附近的代码
idx3 = content.find("batch_submit")
if idx3 >= 0:
    snippet3 = content[max(0,idx3-200):idx3+200]
    print("\n=== batch_submit 上下文 ===")
    print(snippet3)
