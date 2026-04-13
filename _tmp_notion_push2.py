# -*- coding: utf-8 -*-
"""推送带模块分类的报告到Notion"""
import sys, json, subprocess
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\ADHD_agent\_tech_fest_report_v2.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 通过MCP调用脚本写入，用json做数据传输避免编码问题
payload = {
    "page_id": "33bbc16a-735f-818f-a9f7-d1b31155d6a2",
    "content": content
}
with open(r'C:\ADHD_agent\_tmp_notion_payload.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)

print(f"内容长度: {len(content)} chars")
print("payload已保存")
