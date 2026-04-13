# -*- coding: utf-8 -*-
"""
科技节各子活动付费明细查询
Step1: 找出科技节内所有 control_id
Step2: 按 control_id 统计 pay_users, buy_times, revenue
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\ADHD_agent\.agents\skills\ai-to-sql\scripts')
import _datain_api as api

START = '2026-03-13'
END   = '2026-04-03'
START_PART = '2026-03-12'
END_PART   = '2026-04-03'
FESTIVAL_ID = '%2112%'

# Step 1: 找出所有科技节 control_id 及其名字（用 click 事件表）
SQL_CTRL_IDS = f"""
SELECT 
  control_id,
  COUNT(DISTINCT user_id) AS click_users
FROM v1041.ods_user_click
WHERE partition_date BETWEEN '{START_PART}' AND '{END_PART}'
  AND date(date_add('hour',-8,created_at)) BETWEEN date '{START}' AND date '{END}'
  AND control_id LIKE '{FESTIVAL_ID}'
GROUP BY control_id
ORDER BY click_users DESC
LIMIT 50
"""

print("=== Step1: 科技节各 control_id ===")
try:
    r1 = api.execute_sql(SQL_CTRL_IDS)
    rows1 = r1.get('rows', []) if isinstance(r1, dict) else r1
    print(f"Found {len(rows1)} control_ids:")
    for row in rows1:
        print(row)
    with open('_tmp_ctrl_ids.json', 'w', encoding='utf-8') as f:
        json.dump(rows1, f, ensure_ascii=False, indent=2)
except Exception as e:
    print(f"ERROR: {e}")
    rows1 = []

# Step 2: 按 control_id 统计付费明细
# 思路：用 ods_user_click 按 control_id 建立用户-活动映射，再 join 购买表
# 只统计各活动的节日相关礼包购买（iap_type like '%节日活动%' OR 从 control_id 对应商品直接 join）
SQL_PER_ACTIVITY = f"""
WITH festival_users AS (
  -- 每个用户点击过的科技节子活动
  SELECT 
    user_id,
    control_id
  FROM v1041.ods_user_click
  WHERE partition_date BETWEEN '{START_PART}' AND '{END_PART}'
    AND date(date_add('hour',-8,created_at)) BETWEEN date '{START}' AND date '{END}'
    AND control_id LIKE '{FESTIVAL_ID}'
  GROUP BY user_id, control_id
),
festival_orders AS (
  -- 节日期间所有节日活动礼包购买
  SELECT o.user_id, o.iap_id, o.pay_price
  FROM v1041.ods_user_order o
  JOIN v1041.dim_iap d ON o.iap_id = d.iap_id
  WHERE o.partition_date BETWEEN '{START_PART}' AND '{END_PART}'
    AND date(date_add('hour',-8,o.created_at)) BETWEEN date '{START}' AND date '{END}'
    AND o.pay_status = 1
    AND d.iap_type LIKE '%节日活动%'
    AND o.user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
)
SELECT
  fu.control_id,
  COUNT(DISTINCT fo.user_id) AS pay_users,
  COUNT(*)                   AS buy_times,
  CAST(SUM(fo.pay_price) AS DECIMAL(18,2)) AS revenue
FROM festival_users fu
JOIN festival_orders fo ON fu.user_id = fo.user_id
GROUP BY fu.control_id
ORDER BY revenue DESC
"""

print("\n=== Step2: 各 control_id 付费明细 ===")
try:
    r2 = api.execute_sql(SQL_PER_ACTIVITY)
    rows2 = r2.get('rows', []) if isinstance(r2, dict) else r2
    cols2 = r2.get('columns', []) if isinstance(r2, dict) else []
    print(f"Columns: {cols2}")
    print(f"Rows: {len(rows2)}")
    for row in rows2:
        print(row)
    with open('_tmp_per_activity_result.json', 'w', encoding='utf-8') as f:
        json.dump({'columns': cols2, 'rows': rows2}, f, ensure_ascii=False, indent=2)
    print("Saved to _tmp_per_activity_result.json")
except Exception as e:
    print(f"ERROR step2: {e}")
