#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""找到 c.P8 (API base URL prefix) 的值"""
import re
import requests

url = "https://igame.tap4fun.com/static/js/index.a32e59b9.js"
resp = requests.get(url, timeout=15)
content = resp.text

# 搜索 P8 的定义
# 可能是 P8:"..." 或 P8 = "..." 或 exports.P8 = "..."
p8_patterns = re.findall(r'P8["\s:=]+["\'](/?[^"\']*)["\']', content)
print("=== P8 值 ===")
for p in sorted(set(p8_patterns)):
    print("  P8 = '{}'".format(p))

# 也搜索 a.P8 或 c.P8 附近的定义
# 在 webpack bundle 中, 通常是 {P8: "/xxx"} 这样的对象
p8_obj = re.findall(r'\{[^{}]*P8:\s*["\'](/?[^"\']*)["\'][^{}]*\}', content)
print("\n=== P8 对象定义 ===")
for p in sorted(set(p8_obj)):
    print("  {}".format(p[:200]))

# 搜索更广泛的模式
p8_any = re.findall(r'P8\s*[:=]\s*["\'](/[^"\']+)["\']', content)
print("\n=== P8 赋值 ===")
for p in sorted(set(p8_any)):
    print("  {}".format(p))

# 也试试找 62557 模块 (从 batch_submit 上下文中 var e=t(2365),a=t(62557) 得知 a.P8)
idx = content.find("62557")
if idx >= 0:
    snippet = content[max(0,idx-100):idx+500]
    print("\n=== 模块 62557 上下文 ===")
    print(snippet[:800])
