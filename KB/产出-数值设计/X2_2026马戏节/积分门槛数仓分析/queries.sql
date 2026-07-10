-- ============================================================
-- X3 深海酒馆(AO=10071704) 积分/档位达成分布 → 马戏节扭蛋机14档门槛反推
-- 数仓: Datain Trino, X3=1090 (TRINO_HF, v1090视图), X2=1089 (TRINO_HF, v1089)
-- 执行: python C:\ADHD_agent\.agents\skills\ai-to-sql\scripts\query_trino.py --datasource TRINO_HF --sql "..."
-- 日期: 2026-07-10 (活动窗口 2026-07-03~07-12, 数据截至 07-10 当天 = 约 7.3/10 天)
-- 口径坑: v1090 的 user_id/server_id/partition_date 全 varchar; created_at 北京时间
-- ============================================================

-- 【日志形态解码】ods_user_activity 中深海酒馆日志两类:
--   activity_type='0' + attribute1={"actvType":7,...}      = 加入/圈入事件(全服自动, 含不活跃壳)
--   activity_type='4' + attribute1={"stepScore":N,...}     = 积分变化事件, 每次变化写两行:
--        一行 stepScore=累计总分(==activity_score), 一行 stepScore=当前阶段分
--   activity_score = 跨阶段累计总分(单调递增); activity_step = 阶段号(1-7, 观测到1-6)
--   activity_id = 运行时雪花号(相邻4服一组共用), 配置号只在 attribute1 的 activityCfgID

-- Q0: 样本行(解码字段)
SELECT created_at, server_id, user_id, activity_id, activity_type, activity_score,
       activity_step, attribute1
FROM v1090.ods_user_activity
WHERE partition_date='2026-07-05' AND attribute1 LIKE '%10071704%' LIMIT 5;

-- Q1: 参与规模总览
SELECT count(DISTINCT user_id) AS users, count(DISTINCT server_id) AS servers,
       count(*) AS rows, min(partition_date) d_min, max(partition_date) d_max,
       max(activity_score) AS max_score, max(activity_step) AS max_step
FROM v1090.ods_user_activity
WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-10'
  AND attribute1 LIKE '%10071704%';
-- 结果: users=31181(含自动圈入壳), servers=59, rows=815613, max_score=10331462, max_step=6

-- Q2: 阶段×日期映射 + 各阶段产分人数
SELECT activity_step AS step, activity_type, min(partition_date) d_min,
       max(partition_date) d_max, count(DISTINCT user_id) AS users
FROM v1090.ods_user_activity
WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-10'
  AND attribute1 LIKE '%10071704%'
GROUP BY 1,2 ORDER BY 1,2;

-- Q3: 【核心】阶段×档位达成矩阵 + 阶段分分位数
-- 方法: 每人每阶段末累计分 cum_max, 与前序阶段 cum_max 差分 = 该阶段得分(阶段分)
WITH base AS (
  SELECT user_id, activity_step AS step, activity_score
  FROM v1090.ods_user_activity
  WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-10'
    AND attribute1 LIKE '%10071704%' AND activity_type='4'
), per_step AS (
  SELECT user_id, step, max(activity_score) AS cum_max FROM base GROUP BY 1,2
), stage AS (
  SELECT user_id, step,
         cum_max - coalesce(max(cum_max) OVER (PARTITION BY user_id ORDER BY step
                    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0) AS ss
  FROM per_step
)
SELECT step, count(*) AS users_scored,
       count_if(ss>=10000) ge_1w, count_if(ss>=20000) ge_2w, count_if(ss>=30000) ge_3w,
       count_if(ss>=35000) ge_35w, count_if(ss>=50000) ge_5w, count_if(ss>=70000) ge_7w,
       approx_percentile(ss, ARRAY[0.5,0.75,0.9,0.95,0.99]) pct, max(ss) mx
FROM stage GROUP BY step ORDER BY step;

-- Q4: 【核心】玩家活动累计总分分布(产分者)
WITH per_user AS (
  SELECT user_id, max(activity_score) AS total
  FROM v1090.ods_user_activity
  WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-10'
    AND attribute1 LIKE '%10071704%' AND activity_type='4'
  GROUP BY 1
)
SELECT count(*) AS scorers,
       approx_percentile(total, ARRAY[0.05,0.1,0.25,0.4,0.5,0.6,0.75,0.8,0.85,0.9,0.95,0.98,0.99,0.995,0.999]) pct,
       count_if(total>=10000) ge_1w, count_if(total>=30000) ge_3w, count_if(total>=50000) ge_5w,
       count_if(total>=100000) ge_10w, count_if(total>=200000) ge_20w, count_if(total>=300000) ge_30w,
       count_if(total>=500000) ge_50w, count_if(total>=1000000) ge_100w, count_if(total>=2000000) ge_200w,
       count_if(total>=3000000) ge_300w, count_if(total>=5000000) ge_500w, max(total) mx
FROM per_user;

-- Q5: 分母参照 — 59服活跃(ods_user_daily 8天去重 + 逐日)
WITH svr AS (SELECT DISTINCT server_id FROM v1090.ods_user_activity
             WHERE partition_date='2026-07-05' AND attribute1 LIKE '%10071704%')
SELECT d.partition_date, count(DISTINCT d.user_id) AS daily_users
FROM v1090.ods_user_daily d JOIN svr s ON d.server_id=s.server_id
WHERE d.partition_date BETWEEN '2026-07-03' AND '2026-07-10'
GROUP BY 1 ORDER BY 1;
-- 窗口去重: 12824人; 日均 ~6.2k

-- Q6: 逐日酒馆有日志人数(对照, 证明 type=0 是自动圈入)
SELECT partition_date, count(DISTINCT user_id) AS tavern_users
FROM v1090.ods_user_activity
WHERE partition_date BETWEEN '2026-07-03' AND '2026-07-10'
  AND attribute1 LIKE '%10071704%'
GROUP BY 1 ORDER BY 1;
-- D0=16811 >> 当日活跃6477 → type=0 加入事件为全服圈入(含离线壳), 不能当参与分母

-- Q7: 【加分项-X2】占星强消耗14档任务(活动211200205, tasks 211562039-052)
-- status 解码(经 task_score 边界验证): 1=已达成门槛(score>=阈值), 6=进行中未达标, 5=已领奖(score清0)
-- min(status=1 时的 task_score) ≈ 该档门槛(略高于真实值 1~90 分)
SELECT task_id,
       min(CASE WHEN status=1 THEN task_score END) AS threshold,
       count(DISTINCT CASE WHEN status=1 THEN user_id END) AS achieved,
       count(DISTINCT CASE WHEN status=5 THEN user_id END) AS claimed,
       count(DISTINCT user_id) AS touched,
       min(partition_date) d0, max(partition_date) d1
FROM v1089.ods_user_task
WHERE partition_date BETWEEN '2026-05-01' AND '2026-07-10'
  AND attribute1 LIKE '%211200205%'
  AND task_id IN ('211562039','211562040','211562041','211562042','211562043','211562044',
                  '211562045','211562046','211562047','211562048','211562049','211562050',
                  '211562051','211562052')
GROUP BY 1 ORDER BY 1;
-- 实例窗口: 2026-05-17 ~ 05-22

-- 附: 深海酒馆档位奖励领取日志未在 ods_user_asset 找到独立 reason
-- (probe: reason_id LIKE '%tavern%'/'%78604%' 无命中; 达成矩阵改用 Q3 积分差分法, 达成>=领取)
