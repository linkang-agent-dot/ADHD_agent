#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from datetime import datetime

with open(r'c:\ADHD_agent\scripts\activity_payloads.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=' * 80)
print('2026科技节活动部署汇总')
print('=' * 80)

start = datetime.fromtimestamp(data[0]['startTime']/1000)
end = datetime.fromtimestamp(data[0]['endTime']/1000)
preview = datetime.fromtimestamp(data[0]['previewTime']/1000)

print('活动时间: {} ~ {}'.format(start.strftime('%Y-%m-%d %H:%M'), end.strftime('%Y-%m-%d %H:%M')))
print('预览时间: {}'.format(preview.strftime('%Y-%m-%d %H:%M')))
print('共 {} 个活动配置'.format(len(data)))
print()

# 按跨服类型分组
cross_all = [a for a in data if a['acrossServer'] == 1 and len(a['servers']) == 1]
cross_group = [a for a in data if a['acrossServer'] == 1 and len(a['servers']) > 1]
single = [a for a in data if a['acrossServer'] == 0]

print('【跨服-全服】({} 个)'.format(len(cross_all)))
for a in cross_all:
    print('  - {} ({})'.format(a['name'], a['activityConfigId']))

print()
print('【跨服-分组】({} 个)'.format(len(cross_group)))
for a in cross_group:
    print('  - {} ({}) - {}组'.format(a['name'], a['activityConfigId'], len(a['servers'])))

print()
print('【单服】({} 个)'.format(len(single)))
for a in single:
    print('  - {} ({}) - {}服'.format(a['name'], a['activityConfigId'], len(a['servers'])))

print()
print('=' * 80)
