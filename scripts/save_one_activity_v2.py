#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""保存单个活动到 iGame（修正数据格式）"""

import json
import subprocess
import os

IGAME_SCRIPT = os.path.expanduser("~/.claude/skills/igame-skill/scripts/igame-query.js")

# 推币机活动配置 - 参考已有活动的数据格式
# previewTime 和 endShowTime 使用分钟数，而不是时间戳
test_payload = {
    "activityConfigId": "21115696",
    "name": "推币机",
    "previewTime": 1470,              # 预览时间：提前24.5小时（分钟数）
    "startTime": 1773194400000,       # 2026-03-11 10:00 (时间戳)
    "endTime": 1774382400000,         # 2026-03-25 04:00 (时间戳)
    "endShowTime": 1440,              # 结束后展示24小时（分钟数）
    "acrossServer": 1,
    "acrossServerRank": 1,
    "servers": [[
        "2084102", "2084502", "2085302", "2086302", "2087402", "2088202", "2088302", "2088802", "2088902", "2089202",
        "2089602", "2089702", "2089802", "2089902", "2090002", "2090102", "2090202", "2090302", "2090402", "2090502",
        "2090602", "2090702", "2090802", "2090902", "2091002", "2091102", "2091202", "2091302", "2091402", "2091502",
        "2091602", "2091702", "2091802", "2091902", "2092002", "2092102", "2603302", "2604002", "2604402", "2605102",
        "2605902", "2606502", "2606802", "2606902", "2607002", "2607102", "2607202", "2607302", "2607402", "2607502",
        "2607602", "2607702", "2607802", "2006102", "2006402", "2006702", "2007202", "2008502", "2010302", "2012102",
        "2012302", "2012402", "2013402", "2013602", "2014502", "2015702", "2016902", "2017802", "2018502", "2018602",
        "2019202", "2021902", "2022002", "2024402", "2024702", "2025502", "2026002", "2027002", "2028602", "2029902",
        "2030002", "2030502", "2031402", "2032002", "2032402", "2033202", "2033902", "2037402", "2039502", "2041002",
        "2043802", "2044602", "2046502", "2047102", "2049702", "2050502", "2050802", "2051002", "2051302", "2052502",
        "2052702", "2054202", "2055302", "2056102", "2058302", "2058402", "2058802", "2060902", "2061402", "2062402",
        "2062602", "2063202", "2066102", "2068602", "2069702", "2073702", "2074702", "2075202", "2075802", "2077102",
        "2077702", "2078402", "2078702", "2079102", "2079302", "2079402", "2600502", "2600602", "2603602", "2603702",
        "2006502", "2054002", "2600202", "2010102", "2077002", "2060302", "2018202", "2023502", "2038602", "2047502",
        "2055802", "2024502"
    ]],
    "remark": "2026科技节活动 - linkang负责"
}

print("=" * 60)
print("保存活动: {} ({})".format(test_payload["name"], test_payload["activityConfigId"]))
print("服务器数量: {}".format(len(test_payload["servers"][0])))
print("跨服类型: 跨服-全服")
print("预览时间: {}分钟 ({}小时)".format(test_payload["previewTime"], test_payload["previewTime"]/60))
print("结束展示: {}分钟 ({}小时)".format(test_payload["endShowTime"], test_payload["endShowTime"]/60))
print("=" * 60)

# 转换为 JSON
params_json = json.dumps(test_payload, ensure_ascii=False)

# Step 1: 调用 saveActivity 接口保存活动
print("\nStep 1: 调用 activity/add_activity/saveActivity 接口保存活动...")
cmd = ["node", IGAME_SCRIPT, "write", "activity/add_activity/saveActivity", params_json]

result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

print("\n保存结果:")
print(result.stdout)

if result.stderr:
    print("错误信息:")
    print(result.stderr)

# 解析返回结果
try:
    response = json.loads(result.stdout)
    if response.get("success"):
        activity_id = response.get("data", {}).get("id")
        print("\n活动保存成功! ID: {}".format(activity_id))
        
        if activity_id:
            # Step 2: 调用 submit 接口提交活动
            print("\nStep 2: 调用 activity/operation/submit 接口提交活动...")
            submit_params = {
                "ids": [activity_id],
                "reason": "2026科技节活动批量部署"
            }
            submit_json = json.dumps(submit_params, ensure_ascii=False)
            
            cmd2 = ["node", IGAME_SCRIPT, "write", "activity/operation/submit", submit_json]
            result2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8')
            
            print("\n提交结果:")
            print(result2.stdout)
    else:
        print("\n活动保存失败: {}".format(response.get("message")))
        print("错误码: {}".format(response.get("code")))
        print("完整响应: {}".format(json.dumps(response, ensure_ascii=False, indent=2)))
except json.JSONDecodeError as e:
    print("JSON 解析错误: {}".format(e))
