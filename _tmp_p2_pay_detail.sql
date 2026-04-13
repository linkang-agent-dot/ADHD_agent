-- 【P2】指定礼包付费详情（7天版，全服全包，适配 Trino 直查）
-- 时间窗口：2026-03-31 ~ 2026-04-06
-- 去除 server_id / iap_id 过滤，查全量并按收入倒序取 Top30

WITH user_base AS (
    SELECT DISTINCT user_id
    FROM v1041.ods_user_login
    WHERE partition_date BETWEEN cast(date_add('day', -1, date '2026-03-31') AS varchar) AND '2026-04-06'
      AND date(date_add('hour', -8, created_at)) BETWEEN date '2026-03-31' AND date '2026-04-06'
      AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user)
),

buy_info AS (
    SELECT
        a.user_id,
        d.rlevel,
        a.iap_id,
        b.iap_id_name,
        a.pay_price
    FROM (
        SELECT user_id, iap_id, sum(pay_price) AS pay_price
        FROM v1041.ods_user_order
        WHERE partition_date BETWEEN cast(date_add('day', -1, date '2026-03-31') AS varchar) AND '2026-04-06'
          AND date(date_add('hour', -8, created_at)) BETWEEN date '2026-03-31' AND date '2026-04-06'
          AND pay_status = 1
        GROUP BY 1, 2
    ) a
    LEFT JOIN (SELECT iap_id, iap_id_name FROM v1041.dim_iap) b ON a.iap_id = b.iap_id
    -- 保留 iap_id 数字ID供关联
    INNER JOIN user_base c ON a.user_id = c.user_id
    LEFT JOIN (
        SELECT user_id, max_by(rlevel, cohort) AS rlevel
        FROM v1041.da_user_rlevel_pay_ratio
        WHERE create_date BETWEEN cast(date_add('day', -1, date '2026-03-31') AS varchar) AND '2026-04-06'
        GROUP BY 1
    ) d ON a.user_id = d.user_id
),

agg_by_pack AS (
    SELECT
        'group' AS group1,
        iap_id_name,
        iap_id,
        count(DISTINCT user_id)  AS buy_num,
        sum(pay_price)           AS pay_price
    FROM buy_info
    GROUP BY 1, 2, 3
),

agg_total AS (
    SELECT
        'group'                  AS group1,
        count(DISTINCT user_id)  AS total_buy_num,
        sum(pay_price)           AS total_pay
    FROM buy_info
    GROUP BY 1
),

agg_login AS (
    SELECT 'group' AS group1, count(DISTINCT user_id) AS log_num
    FROM user_base
    GROUP BY 1
),

agg_rlevel AS (
    SELECT
        'group' AS group1,
        iap_id,
        iap_id_name,
        count(DISTINCT CASE WHEN rlevel = 'chaoR'  THEN user_id END) AS chaor_num,
        sum(CASE WHEN rlevel = 'chaoR'  THEN pay_price END)          AS chaor_pay,
        count(DISTINCT CASE WHEN rlevel = 'daR'    THEN user_id END) AS dar_num,
        sum(CASE WHEN rlevel = 'daR'    THEN pay_price END)          AS dar_pay,
        count(DISTINCT CASE WHEN rlevel = 'zhongR' THEN user_id END) AS zhongr_num,
        sum(CASE WHEN rlevel = 'zhongR' THEN pay_price END)          AS zhongr_pay,
        count(DISTINCT CASE WHEN rlevel = 'xiaoR'  THEN user_id END) AS xiaor_num,
        sum(CASE WHEN rlevel = 'xiaoR'  THEN pay_price END)          AS xiaor_pay
    FROM buy_info
    GROUP BY 1, 2, 3
)

SELECT
    a.iap_id,
    a.iap_id_name,
    a.buy_num,
    a.pay_price,
    b.total_buy_num,
    b.total_pay,
    c.log_num,
    round(1.00 * a.buy_num / c.log_num * 100, 2)    AS pay_rate_pct,
    round(a.pay_price / a.buy_num, 2)                AS arppu,
    round(a.pay_price / c.log_num, 4)                AS arpu,
    d.chaor_num,  d.chaor_pay,
    d.dar_num,    d.dar_pay,
    d.zhongr_num, d.zhongr_pay,
    d.xiaor_num,  d.xiaor_pay,
    round(coalesce(d.chaor_pay, 0) / a.pay_price * 100, 1) AS chaor_pay_pct
FROM agg_by_pack a
LEFT JOIN agg_total  b ON a.group1 = b.group1
LEFT JOIN agg_login  c ON a.group1 = c.group1
LEFT JOIN agg_rlevel d ON a.group1 = d.group1 AND a.iap_id = d.iap_id
ORDER BY a.pay_price DESC
LIMIT 30
