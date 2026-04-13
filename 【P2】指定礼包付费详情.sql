-- ============================================================
-- Dashboard: 【P2】指定礼包付费详情
-- ID: 69a553cec7bbf6219adb7816
-- URL: https://datain.tap4fun.com/dashboard/69a553cec7bbf6219adb7816
-- 图表数: 1
-- ============================================================

-- ------------------------------------------------------------
-- 图表: 【P2】指定礼包付费详情
-- ID: 69a55334c7bbf6219adb77c2
-- 类型: SQL  数据源: TRINO
-- 参数: time(DATE_RANGE), server_id(LIST), iap_id(LIST)
-- ------------------------------------------------------------
with user as (
select user_id from v1041.ods_user_login
where partition_date between cast(date_add('day', -1, date '${ time.start }' ) as varchar) and '${ time.end }'
and date(date_add('hour',-8,created_at)) between date '${ time.start }' and date '${ time.end }'
and server_id in (${ server_id })
and user_id not in (select user_id from v1041.dl_test_user)
group by 1 ) ,


buy_info as (
select a.user_id, 
       rlevel,
       iap_id_name,
       sum(pay_price) as pay_price from 
(select user_id, iap_id, sum(pay_price) as pay_price from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ time.start }' ) as varchar) and '${ time.end }'
and date(date_add('hour',-8,created_at)) between date '${ time.start }' and date '${ time.end }'
and pay_status = 1 
group by 1,2) a 
left join 
(select iap_id, iap_id_name from v1041.dim_iap) b on a.iap_id = b.iap_id 
inner join user c on a.user_id = c.user_id 
left join 
(select user_id, max_by(rlevel, cohort) as rlevel from v1041.da_user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ time.start }' ) as varchar) and '${ time.end }'
group by 1) d on a.user_id = d.user_id 
where iap_id_name in (${ iap_id })
group by 1,2,3) 


select a.*, total_buy_num, total_pay, log_num, chaor_num,chaor_pay, dar_num,dar_pay,zhongr_num,zhongr_pay,xiaor_num,xiaor_pay from 
(select 'group' as group1,
        iap_id_name,
        count(distinct user_id) as buy_num,
        sum(pay_price) as pay_price from buy_info
group by 1,2 ) a 
left join 
(select 'group' as group1, 
         count(distinct user_id) as total_buy_num,
         sum(pay_price) as total_pay from buy_info
group by 1) b on a.group1 = b.group1 
left join 
(select 'group' as group1,
        count(distinct user_id) as log_num from user 
group by 1) c on a.group1 = c.group1 
left join 
(select 'group' as group1,
        iap_id_name,
        count(distinct case when rlevel = 'chaoR' then user_id else null end) as chaor_num,
        sum(case when rlevel = 'chaoR' then pay_price else null end) as chaor_pay, 
        count(distinct case when rlevel = 'daR' then user_id else null end) as dar_num,
        sum(case when rlevel = 'daR' then pay_price else null end) as dar_pay, 
        count(distinct case when rlevel = 'zhongR' then user_id else null end) as zhongr_num,
        sum(case when rlevel = 'zhongR' then pay_price else null end) as zhongr_pay, 
        count(distinct case when rlevel = 'xiaoR' then user_id else null end) as xiaor_num,
        sum(case when rlevel = 'xiaoR' then pay_price else null end) as xiaor_pay from buy_info
group by 1,2 ) d on a.group1 = d.group1 and a.iap_id_name = d.iap_id_name

