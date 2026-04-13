# -*- coding: utf-8 -*-
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\skills\generate_event_review\scripts')
import notion_publisher as np_mod

with open(r'C:\ADHD_agent\_tech_fest_input.json','r',encoding='utf-8') as f:
    data = json.load(f)

metrics = np_mod.compute_metrics(data)
md = np_mod.generate_notion_content(data, metrics)

with open(r'C:\ADHD_agent\_tech_fest_report_v2.md','w',encoding='utf-8') as f:
    f.write(md)

print('报告生成完成，行数:', len(md.splitlines()))
