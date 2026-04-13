#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接调用 datain-skill query 函数查询 P2 近7天付费指标
"""
import sys, json, os
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\datain-skill\scripts")
os.chdir(r"C:\ADHD_agent\.agents\skills\datain-skill")

import common, query_game

# 时间窗口：近7天 2026-03-31 ~ 2026-04-06
START = "2026-03-31"
END   = "2026-04-06"

# 运营分析用 user_id 算法（与SQL匹配）
params = {
    "algorithmId": "user_id",
    "fullDayLimit": 1,
    "startAt": START,
    "endAt":   END,
    "games": ["1041"],
    "dimensions": [],
    "dimensionFilters": [],
    "indicators": [
        {"id": "60d4131ae862647e69cfe709", "name": "内购收入"},
        {"id": "60d4281cb75b54435c6225fc", "name": "ARPU"},
        {"id": "60d42914b75b54435c6225fd", "name": "ARPPU"},
        {"id": "60ebdb03e023ba0836356b20", "name": "付费率"},
        {"id": "60ebd70ae023ba0836356b1a", "name": "付费用户数"},
        {"id": "612c7942b27d3b153da7e954", "name": "平均 DAU"},
    ],
    "indicatorFilters": [],
    "tagDimensions": [],
    "tagFilters": [],
}

print(f"查询 P2(1041) {START} ~ {END} 付费概览...")
result = query_game.query(params)

print("\n=== 查询结果 ===")
if result and "columns" in result:
    cols = {c["key"]: c["name"] for c in result["columns"]}
    for row in result.get("result", []):
        for k, v in row.items():
            print(f"  {cols.get(k, k)}: {v}")
else:
    print(json.dumps(result, ensure_ascii=False, indent=2))
