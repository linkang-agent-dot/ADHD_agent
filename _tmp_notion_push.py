# -*- coding: utf-8 -*-
"""更新Notion科技节复盘页面"""
import sys, json, subprocess
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\skills\generate_event_review\scripts')
import notion_publisher as np_mod

# 读取报告
with open(r'C:\ADHD_agent\_tech_fest_report_v2.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# 读取input数据生成标题
with open(r'C:\ADHD_agent\_tech_fest_input.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

title = np_mod.generate_notion_title(data)
print(f"页面标题: {title}")
print(f"内容长度: {len(md_content)} 字符, {len(md_content.splitlines())} 行")
