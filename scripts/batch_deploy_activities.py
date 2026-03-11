#!/usr/bin/env python3
"""
批量部署科技节活动到 iGame
从 Google Sheet 读取活动配置，整理后提交到 iGame
"""

import json
import subprocess
import os
from datetime import datetime, timedelta

# 配置
IGAME_SCRIPT = os.path.expanduser("~/.claude/skills/igame-skill/scripts/igame-query.js")
GOOGLE_PROJECT_ID = "calm-repeater-489707-n1"

# 2026科技节时间配置（根据 Sheet 第8行：3-11 开始）
FESTIVAL_START = datetime(2026, 3, 11, 10, 0, 0)  # 3月11日 10:00
FESTIVAL_END = datetime(2026, 3, 25, 4, 0, 0)     # 3月25日 04:00（持续14天）
PREVIEW_MINUTES = 1470  # 预览时间（分钟）= 24.5小时

# 灰度测试服务器
GRAY_SERVERS = [
    "2006502", "2054002", "2600202", "2010102", "2077002", "2060302",
    "2018202", "2023502", "2038602", "2047502", "2055802", "2024502"
]

# 全服一组服务器（跨服-全服使用）
ALL_SERVERS_GROUP = [
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
]

# 跨服分组 - Schema6（国际服）
CROSS_SERVER_GROUPS_S6 = [
    ["2016902", "2012402", "2007202", "2052702", "2032002", "2058802", "2063202", "2051302", "2027002", "2041002", "2033902"],
    ["2077102", "2037402", "2054202", "2047102", "2013402", "2058402", "2058302", "2600602", "2018502", "2010302", "2050802"],
    ["2044602", "2032402", "2060902", "2013602", "2008502", "2028602", "2031402", "2030502", "2052502", "2079302", "2079102"],
    ["2006402", "2012302", "2021902", "2024402", "2030002", "2056102", "2068602", "2073702", "2066102", "2029902", "2055302"],
    ["2006702", "2014502", "2603602", "2049702", "2017802", "2043802", "2046502", "2018602", "2022002", "2069702", "2078702"],
    ["2077702", "2079402", "2075202", "2062402", "2061402", "2078402", "2025502", "2051002", "2050502", "2039502", "2033202"],
    ["2012102", "2015702", "2019202", "2600502", "2603702", "2006102", "2024702", "2075802", "2062602", "2074702", "2026002"],
]

# 跨服分组 - Schema3-5（国际服）
CROSS_SERVER_GROUPS_S35 = [
    ["2084502", "2086302", "2084102", "2090402", "2088302", "2088202", "2090002", "2089202", "2088902", "2091802", "2090802", "2092102", "2606802"],
    ["2604002", "2087402", "2605102", "2085302", "2603302", "2604402", "2090302", "2092002", "2091202", "2091302", "2091102", "2091702", "2606902"],
    ["2088802", "2090602", "2089602", "2607202", "2090702", "2091902", "2089802", "2090202", "2091402", "2091502", "2090902", "2091002", "2607102"],
    ["2090102", "2605902", "2089902", "2090502", "2091602", "2607702", "2606502", "2089702", "2607002", "2607402", "2607802", "2607302", "2607502", "2607602"],
]

# 单服服务器列表（按 schema 分）
SINGLE_SERVERS_S6 = [
    "2006102", "2006402", "2006702", "2007202", "2008502", "2010302", "2012102", "2012302", "2012402", "2013402",
    "2013602", "2014502", "2015702", "2016902", "2017802", "2018502", "2018602", "2019202", "2021902", "2022002",
    "2024402", "2024702", "2025502", "2026002", "2027002", "2028602", "2029902", "2030002", "2030502", "2031402",
    "2032002", "2032402", "2033202", "2033902", "2037402", "2039502", "2041002", "2043802", "2044602", "2046502",
    "2047102", "2049702", "2050502", "2050802", "2051002", "2051302", "2052502", "2052702", "2054202", "2055302",
    "2056102", "2058302", "2058402", "2058802", "2060902", "2061402", "2062402", "2062602", "2063202", "2066102",
    "2068602", "2069702", "2073702", "2074702", "2075202", "2075802", "2077102", "2077702", "2078402", "2078702",
    "2079102", "2079302", "2079402", "2600502", "2600602", "2603602", "2603702"
]

SINGLE_SERVERS_S35 = [
    "2084102", "2084502", "2085302", "2086302", "2087402", "2088202", "2088302", "2088802", "2088902", "2089202",
    "2089602", "2089702", "2089802", "2089902", "2090002", "2090102", "2090202", "2090302", "2090402", "2090502",
    "2090602", "2090702", "2090802", "2090902", "2091002", "2091102", "2091202", "2091302", "2091402", "2091502",
    "2091602", "2091702", "2091802", "2091902", "2092002", "2092102", "2603302", "2604002", "2604402", "2605102",
    "2605902", "2606502", "2606802", "2606902", "2607002", "2607102", "2607202", "2607302", "2607402", "2607502",
    "2607602", "2607702", "2607802"
]

# 活动列表（从 Google Sheet 提取）
ACTIVITIES = [
    {"name": "主城特效累充bingo", "activityConfigId": "21115733", "owner": "liusiyi", "crossServer": "单服", "count": 2},
    {"name": "主城特效累充-联盟版", "activityConfigId": "21115731", "owner": "liusiyi", "crossServer": "跨服-全服", "count": 1},
    {"name": "主城特效累充-服务器版", "activityConfigId": "21115732", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "手札", "activityConfigId": "21115740", "owner": "gongliang", "crossServer": "单服", "count": 1},
    {"name": "弹珠主体GACHA+累计活动", "activityConfigId": "21115728", "owner": "gongliang", "crossServer": "单服", "count": 1},
    {"name": "机甲累充", "activityConfigId": "21115726", "owner": "gongliang", "crossServer": "单服", "count": 1},
    {"name": "每日弹珠礼包", "activityConfigId": "21115729", "owner": "gongliang", "crossServer": "单服", "count": 1},
    {"name": "推币机", "activityConfigId": "21115696", "owner": "linkang", "crossServer": "跨服-全服", "count": 1},
    {"name": "推币机-单笔累充", "activityConfigId": "21115376", "owner": "gongliang", "crossServer": "单服", "count": 1},
    {"name": "长节日BP", "activityConfigId": "21115746", "owner": "minghao", "crossServer": "跨服-全服", "count": 1},
    {"name": "节日通用-强消耗-schema3-5", "activityConfigId": "21115398", "owner": "minghao", "crossServer": "跨服-分组", "schema": "3-5", "count": 1},
    {"name": "节日通用-强消耗-schema6", "activityConfigId": "21115399", "owner": "minghao", "crossServer": "跨服-分组", "schema": "6", "count": 1},
    {"name": "科技节-通用第二套-对对碰schema3-5", "activityConfigId": "21115526", "owner": "minghao", "crossServer": "跨服-分组", "schema": "3-5", "count": 3},
    {"name": "科技节-通用第二套-对对碰schema6", "activityConfigId": "21115527", "owner": "minghao", "crossServer": "跨服-分组", "schema": "6", "count": 1},
    {"name": "大富翁-节日装饰", "activityConfigId": "21115747", "owner": "minghao", "crossServer": "跨服-分组", "count": 3},
    {"name": "合成小游戏活动-科技节版本（3月循环）-schema3", "activityConfigId": "21115358", "owner": "gongliang", "crossServer": "跨服-分组", "schema": "3", "count": 1},
    {"name": "合成小游戏活动-科技节版本（3月循环）-schema4", "activityConfigId": "21115359", "owner": "gongliang", "crossServer": "跨服-分组", "schema": "4", "count": 1},
    {"name": "合成小游戏活动-科技节版本（3月循环）-schema5", "activityConfigId": "21115360", "owner": "gongliang", "crossServer": "跨服-分组", "schema": "5", "count": 1},
    {"name": "科技节-节日挖孔小游戏", "activityConfigId": "21115735", "owner": "liusiyi", "crossServer": "跨服-全服", "count": 1},
    {"name": "多条件连锁", "activityConfigId": "21115594", "owner": "linkang", "crossServer": "单服", "count": 1},
    {"name": "掉落转付费", "activityConfigId": "21115472", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "7日", "activityConfigId": "21115380", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "bingo", "activityConfigId": "21115037", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "周卡_schema3-5", "activityConfigId": "21115632", "owner": "minghao", "crossServer": "单服", "schema": "3-5", "count": 1},
    {"name": "周卡_schema6", "activityConfigId": "21115633", "owner": "minghao", "crossServer": "单服", "schema": "6", "count": 1},
    {"name": "联动礼包-行军表情、特效", "activityConfigId": "21115739", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "行军特效-付费率", "activityConfigId": "21115738", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "行军表情-付费率", "activityConfigId": "21115736", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "科技节预购连锁礼包_schema3-5", "activityConfigId": "21115559", "owner": "linkang", "crossServer": "跨服分组", "schema": "3-5", "count": 1},
    {"name": "科技节预购连锁礼包_schema6", "activityConfigId": "21115560", "owner": "linkang", "crossServer": "跨服分组", "schema": "6", "count": 1},
    {"name": "装饰兑换商店-通用", "activityConfigId": "21115441", "owner": "linkang", "crossServer": "单服", "count": 0},
    {"name": "科技节-限时抢购-S6-通用皮（1、2期）", "activityConfigId": "21115741", "owner": "gongliang", "crossServer": "单服", "schema": "6", "count": 1},
    {"name": "科技节-限时抢购-S3-5-通用皮（3期）", "activityConfigId": "21115742", "owner": "gongliang", "crossServer": "单服", "schema": "3-5", "count": 1},
    {"name": "挂机BP", "activityConfigId": "21115607", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "团购礼包", "activityConfigId": "21115479", "owner": "linkang", "crossServer": "单服", "count": 1},
    {"name": "通用-订阅卡累充-schema3", "activityConfigId": "21115312", "owner": "linkang", "crossServer": "单服", "schema": "3", "count": 1},
    {"name": "通用-订阅卡累充-schema4-6", "activityConfigId": "21115313", "owner": "linkang", "crossServer": "单服", "schema": "4-6", "count": 1},
    {"name": "巨猿", "activityConfigId": "21115734", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "签到", "activityConfigId": "21115737", "owner": "liusiyi", "crossServer": "单服", "count": 1},
    {"name": "科技节日卡包BP", "activityConfigId": "21115743", "owner": "linkang", "crossServer": "单服", "count": 1},
    {"name": "科技节-三合一礼包", "activityConfigId": "21115744", "owner": "linkang", "crossServer": "单服", "count": 1},
]


def datetime_to_timestamp(dt):
    """转换 datetime 为毫秒时间戳"""
    return int(dt.timestamp() * 1000)


def get_servers_for_activity(activity):
    """根据活动配置获取服务器列表"""
    cross_server = activity.get("crossServer", "单服")
    schema = activity.get("schema", "")
    
    if cross_server == "跨服-全服":
        # 全服一组
        return [ALL_SERVERS_GROUP], 1, 1  # servers, acrossServer, acrossServerRank
    
    elif cross_server in ["跨服-分组", "跨服分组"]:
        # 跨服分组
        if schema in ["6"]:
            return CROSS_SERVER_GROUPS_S6, 1, 1
        elif schema in ["3-5", "3", "4", "5"]:
            return CROSS_SERVER_GROUPS_S35, 1, 1
        else:
            # 默认使用 S6 分组
            return CROSS_SERVER_GROUPS_S6, 1, 1
    
    else:
        # 单服
        if schema in ["6"]:
            servers = SINGLE_SERVERS_S6 + GRAY_SERVERS
        elif schema in ["3-5", "3", "4", "5"]:
            servers = SINGLE_SERVERS_S35 + GRAY_SERVERS
        else:
            # 默认全部服务器
            servers = list(set(SINGLE_SERVERS_S6 + SINGLE_SERVERS_S35 + GRAY_SERVERS))
        
        # 单服每个服务器单独一组
        return [[s] for s in servers], 0, 1


def build_activity_payload(activity):
    """构建活动提交的 payload"""
    servers, across_server, across_server_rank = get_servers_for_activity(activity)
    
    start_ts = datetime_to_timestamp(FESTIVAL_START)
    end_ts = datetime_to_timestamp(FESTIVAL_END)
    preview_ts = datetime_to_timestamp(FESTIVAL_START - timedelta(minutes=PREVIEW_MINUTES))
    end_show_ts = end_ts + 86400000  # 结束后展示24小时
    
    payload = {
        "activityConfigId": activity["activityConfigId"],
        "name": activity["name"],
        "previewTime": preview_ts,
        "startTime": start_ts,
        "endTime": end_ts,
        "endShowTime": end_show_ts,
        "acrossServer": across_server,
        "acrossServerRank": across_server_rank,
        "servers": servers,
        "remark": f"2026科技节活动 - {activity['owner']}负责"
    }
    
    return payload


def call_igame_api(command, api_path, params):
    """调用 iGame API"""
    params_json = json.dumps(params, ensure_ascii=False)
    cmd = ["node", IGAME_SCRIPT, command, api_path, params_json]
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {result.stdout}")
        return None


def generate_activity_summary():
    """生成活动汇总"""
    print("=" * 80)
    print("2026科技节活动部署汇总")
    print("=" * 80)
    print(f"\n活动时间: {FESTIVAL_START.strftime('%Y-%m-%d %H:%M')} ~ {FESTIVAL_END.strftime('%Y-%m-%d %H:%M')}")
    print(f"预览时间: 提前 {PREVIEW_MINUTES} 分钟 ({PREVIEW_MINUTES/60:.1f} 小时)")
    print(f"\n共 {len(ACTIVITIES)} 个活动配置:")
    print("-" * 80)
    
    # 按跨服类型分组
    cross_server_all = []
    cross_server_group = []
    single_server = []
    
    for act in ACTIVITIES:
        cs = act.get("crossServer", "单服")
        if cs == "跨服-全服":
            cross_server_all.append(act)
        elif cs in ["跨服-分组", "跨服分组"]:
            cross_server_group.append(act)
        else:
            single_server.append(act)
    
    print(f"\n【跨服-全服】({len(cross_server_all)} 个)")
    for act in cross_server_all:
        print(f"  - {act['name']} ({act['activityConfigId']}) - {act['owner']}")
    
    print(f"\n【跨服-分组】({len(cross_server_group)} 个)")
    for act in cross_server_group:
        schema = act.get('schema', '未指定')
        print(f"  - {act['name']} ({act['activityConfigId']}) - {act['owner']} [Schema: {schema}]")
    
    print(f"\n【单服】({len(single_server)} 个)")
    for act in single_server:
        schema = act.get('schema', '全部')
        print(f"  - {act['name']} ({act['activityConfigId']}) - {act['owner']} [Schema: {schema}]")
    
    print("\n" + "=" * 80)
    
    # 生成 JSON 格式的活动配置
    payloads = []
    for act in ACTIVITIES:
        payload = build_activity_payload(act)
        payloads.append(payload)
    
    return payloads


def save_payloads_to_file(payloads, filename="activity_payloads.json"):
    """保存 payload 到文件"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(payloads, f, ensure_ascii=False, indent=2)
    print(f"\n活动配置已保存到: {filepath}")
    return filepath


def submit_activities(payloads, dry_run=True):
    """提交活动到 iGame"""
    if dry_run:
        print("\n[DRY RUN] 以下活动将被提交:")
        for i, payload in enumerate(payloads, 1):
            print(f"  {i}. {payload['name']} ({payload['activityConfigId']})")
        print(f"\n总计 {len(payloads)} 个活动")
        print("\n要实际提交，请运行: python batch_deploy_activities.py --submit")
        return
    
    print("\n开始提交活动...")
    success_count = 0
    failed_activities = []
    
    for payload in payloads:
        print(f"\n提交: {payload['name']} ({payload['activityConfigId']})...")
        
        # 调用 saveActivity 接口
        result = call_igame_api("write", "activity/add_activity/saveActivity", payload)
        
        if result and result.get("success"):
            print(f"  ✓ 保存成功")
            
            # 获取返回的活动 ID，然后提交
            activity_id = result.get("data", {}).get("id")
            if activity_id:
                submit_result = call_igame_api("write", "activity/operation/submit", {
                    "ids": [activity_id],
                    "reason": "2026科技节活动批量部署"
                })
                
                if submit_result and submit_result.get("success"):
                    print(f"  ✓ 提交成功 (ID: {activity_id})")
                    success_count += 1
                else:
                    print(f"  ✗ 提交失败: {submit_result}")
                    failed_activities.append(payload['name'])
            else:
                print(f"  ✗ 未获取到活动 ID")
                failed_activities.append(payload['name'])
        else:
            print(f"  ✗ 保存失败: {result}")
            failed_activities.append(payload['name'])
    
    print("\n" + "=" * 80)
    print(f"提交完成: 成功 {success_count}/{len(payloads)}")
    if failed_activities:
        print(f"失败活动: {', '.join(failed_activities)}")


if __name__ == "__main__":
    import sys
    
    # 生成汇总
    payloads = generate_activity_summary()
    
    # 保存到文件
    save_payloads_to_file(payloads)
    
    # 检查是否要实际提交
    if "--submit" in sys.argv:
        confirm = input("\n确认要提交这些活动吗？(yes/no): ")
        if confirm.lower() == "yes":
            submit_activities(payloads, dry_run=False)
        else:
            print("已取消提交")
    else:
        submit_activities(payloads, dry_run=True)
