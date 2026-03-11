#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import requests

resp = requests.get("https://igame.tap4fun.com/", timeout=15)
js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', resp.text)
print("JS files: {}".format(js_files))

for jf in js_files:
    url = "https://igame.tap4fun.com/" + jf.lstrip("/")
    print("\nFetching: {}".format(url))
    try:
        js_resp = requests.get(url, timeout=15)
        if js_resp.status_code == 200:
            content = js_resp.text
            # 搜索所有 activity 相关路径
            patterns = re.findall(r'["\'](/(?:ark/)?activity[/a-zA-Z_]*)["\']', content)
            # 也搜索 concat 拼接的路径
            patterns2 = re.findall(r'activity[/a-zA-Z_]+', content)
            all_patterns = sorted(set(patterns + patterns2))
            if all_patterns:
                print("  找到 activity 路径:")
                for p in all_patterns:
                    print("    {}".format(p))
            else:
                print("  未找到 activity 路径")
            
            # 特别搜索 add/save/submit/deploy 相关
            deploy_patterns = re.findall(r'["\']((?:/ark)?/[a-zA-Z/]*(?:add|save|submit|deploy|draft|create)[a-zA-Z/]*)["\']', content)
            if deploy_patterns:
                print("  save/submit/deploy 相关路径:")
                for p in sorted(set(deploy_patterns)):
                    print("    {}".format(p))
    except Exception as e:
        print("  Error: {}".format(e))
