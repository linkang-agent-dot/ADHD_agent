import subprocess, sys, os

def run_sql(sql, datasource="TRINO_AWS", limit=100, label=""):
    script = os.path.join(os.path.dirname(__file__), ".agents/skills/ai-to-sql/scripts/query_trino.py")
    result = subprocess.run(
        [sys.executable, script, "--datasource", datasource, "--limit", str(limit), "--sql", sql],
        capture_output=True, text=True, cwd=os.path.dirname(__file__)
    )
    print(f"\n=== {label} ===")
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

# 精确关联：11112091 获取的 event_task 记录（change_type=1）
# 与同一用户、同一毫秒的 ods_user_task（status=5或6）关联
# 这样能确定：是哪个 event 的任务奖励直接包含了 11112091
run_sql("""
WITH gain AS (
  SELECT
    a.user_id,
    a.created_at,
    a.activity_id,
    a.partition_date
  FROM v1041.ods_user_asset a
  WHERE a.partition_date BETWEEN '2026-04-07' AND '2026-04-09'
    AND a.asset_id = '11112091'
    AND a.change_type = '1'
    AND a.reason_id = 'event_task'
)
SELECT
  JSON_EXTRACT_SCALAR(t.attribute1, '$.event') AS event_id,
  JSON_EXTRACT_SCALAR(t.attribute1, '$.is_auto') AS is_auto,
  t.status,
  count(distinct g.user_id) AS user_cnt,
  count(*) AS match_cnt
FROM gain g
JOIN v1041.ods_user_task t
  ON t.user_id = g.user_id
  AND t.partition_date = g.partition_date
  AND t.created_at = g.created_at
  AND t.status IN (5, 6)
GROUP BY
  JSON_EXTRACT_SCALAR(t.attribute1, '$.event'),
  JSON_EXTRACT_SCALAR(t.attribute1, '$.is_auto'),
  t.status
ORDER BY user_cnt DESC
""", limit=30, label="精确同毫秒：11112091 event_task获取 vs 任务完成 event_id")
