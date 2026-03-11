#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""找到模块 62557 中 P8 的导出值"""
import re
import requests

url = "https://igame.tap4fun.com/static/js/index.a32e59b9.js"
resp = requests.get(url, timeout=15)
content = resp.text

# webpack module 62557 的定义通常是 62557:function(e,t,n){...} 或 62557:(e,t,n)=>{...}
# 搜索 62557 模块定义
patterns = [
    r'62557\s*:\s*(?:function\s*\([^)]*\)|(?:\([^)]*\)\s*=>))\s*\{([^}]{0,500})',
    r'62557\s*:\s*\(([^)]+)\)\s*=>\s*\{([^}]{0,500})',
]

for pat in patterns:
    matches = re.findall(pat, content)
    if matches:
        print("模块 62557 定义:")
        for m in matches:
            print("  {}".format(str(m)[:300]))

# 更简单的方式：搜索包含 P8: 的导出定义
# 在 webpack bundle 中，导出通常是 n.d(t,{P8:()=>xxx})
p8_exports = re.findall(r'd\([^,]+,\{[^}]*P8:\s*\(\)\s*=>\s*(\w+)', content)
print("\nP8 导出变量名: {}".format(p8_exports[:5]))

# 找到这些变量的值
for var_name in p8_exports[:5]:
    # 搜索变量定义
    var_patterns = [
        r'{}\s*=\s*["\']([^"\']+)["\']'.format(re.escape(var_name)),
        r'const\s+{}\s*=\s*["\']([^"\']+)["\']'.format(re.escape(var_name)),
        r'var\s+{}\s*=\s*["\']([^"\']+)["\']'.format(re.escape(var_name)),
        r'{}\s*:\s*["\']([^"\']+)["\']'.format(re.escape(var_name)),
    ]
    for vp in var_patterns:
        matches = re.findall(vp, content)
        if matches:
            print("  {} = '{}'".format(var_name, matches[0]))
            break

# 直接搜索 "/ark" 或 "/api" 这种常见前缀
ark_defs = re.findall(r'["\'](/ark)["\']', content)
api_defs = re.findall(r'["\'](/api/v\d+)["\']', content)
print("\n/ark 出现次数: {}".format(len(ark_defs)))
print("/api/vN 出现次数: {}".format(len(api_defs)))

# 直接找所有像 base URL 的常量
base_urls = re.findall(r'["\'](/(?:ark|api|v\d)[/a-zA-Z]*)["\']', content)
print("\n可能的 base URL 前缀: {}".format(sorted(set(base_urls))[:20]))
