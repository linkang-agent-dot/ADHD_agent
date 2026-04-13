-- ============================================================
-- Dashboard: 【P2】节日活动付费数据情况
-- URL: https://datain.tap4fun.com/dashboard/66ab4f762a840a587f0d8fd4
-- 创建者: 贺馨之
-- 图表总数: 11
-- ============================================================

-- ------------------------------------------------------------
-- 图表 1: 节日活动礼包整体档位购买人数情况
-- 图表名称: 【P2】节日活动礼包整体档位购买人数
-- 图表ID: 66ab24182a840a587f0d51f9
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id from v1041.ods_user_click 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and control_id = '${ control_id }'
group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2 ), 


pay_info as (
select a.*, rlevel from 
(select user_id, pay_price, sum(pay_price) as total from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 
and iap_id in (select iap_id from dim.iap where game_cd = 1041 and iap_type = '混合-节日活动')
group by 1, 2 ) a 
inner join 
(select user_id, rlevel from log_info 
group by 1, 2) b on a.user_id = b.user_id ) 


select pay_price, 
       count(distinct user_id) as num_all,
       count(distinct case when rlevel = 'xiaoR' then user_id else null end) as num_xiao,
       count(distinct case when rlevel = 'zhongR' then user_id else null end) as num_zhong,
       count(distinct case when rlevel = 'daR' then user_id else null end) as num_da,
       count(distinct case when rlevel = 'chaoR' then user_id else null end) as num_chao from pay_info 
group by 1 
order by 1 asc


-- ------------------------------------------------------------
-- 图表 2: 指定节日活动礼包付费情况
-- 图表名称: 【P2】指定节日活动礼包购买情况
-- 图表ID: 66ab29f52a840a587f0d5a33
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id from v1041.ods_user_click 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and control_id = '${ control_id }'
group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2 ), 


pay_info as (
select a.*, pay_price, pay_price_fes, pay_total from log_info a 
left join 
(select user_id,
        sum(case when b1.iap_id in (${ iap_id }) then pay_price else null end) as pay_price,
        sum(case when iap_type = '混合-节日活动' then pay_price else null end) as pay_price_fes,
        sum(pay_price) as pay_total from 
(select user_id, iap_id, pay_price from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 ) b1 
left join 
(select iap_id, iap_type from dim.iap where game_cd = 1041) b2 on b1.iap_id = b2.iap_id 
group by 1 ) b on a.user_id = b.user_id )


select *, 
       round(cast(pay_price as real) / cast(pay_price_fes as real), 4) * 100 as price_fes_ratio,
       round(cast(pay_price as real) / cast(pay_total as real), 4) * 100 as price_ratio,
       round(cast(buy_num as real) / cast(log_num as real), 4) * 100 as buy_ratio,
       round(cast(pay_price as real) / cast(buy_num as real), 2) as arppu,
       round(cast(pay_price as real) / cast(log_num as real), 2) as arpu from 
(select '全体玩家' as label, 
        count(distinct user_id) as log_num,
        count(distinct case when pay_price >0 then user_id else null end) as buy_num,
        sum(pay_price) as pay_price,
        sum(pay_price_fes) as pay_price_fes,
        sum(pay_total) as pay_total from pay_info
group by 1 
union all 
select '付费玩家' as label, 
        count(distinct user_id) as log_num, 
        count(distinct case when pay_price >0 then user_id else null end) as buy_num,
        sum(pay_price) as pay_price,
        sum(pay_price_fes) as pay_price_fes,
        sum(pay_total) as pay_total from pay_info
where rlevel != 'feiR'
group by 1 
union all 
select  rlevel as label, 
        count(distinct user_id) as log_num, 
        count(distinct case when pay_price >0 then user_id else null end) as buy_num,
        sum(pay_price) as pay_price,
        sum(pay_price_fes) as pay_price_fes,
        sum(pay_total) as pay_total from pay_info
where rlevel != 'feiR'
group by 1 )
order by log_num desc


-- ------------------------------------------------------------
-- 图表 3: 指定节日活动礼包档位购买人数情况
-- 图表名称: 【P2】指定节日活动礼包档位购买人数
-- 图表ID: 66ab2acb2a840a587f0d5b5b
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id from v1041.ods_user_click 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and control_id = '${ control_id }'
group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2 ), 


pay_info as (
select a.*, rlevel from 
(select user_id, pay_price, sum(pay_price) as total from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 
and iap_id in (${ iap_id })
group by 1, 2 ) a 
inner join 
(select user_id, rlevel from log_info 
group by 1, 2) b on a.user_id = b.user_id ) 


select pay_price, 
       count(distinct user_id) as num_all,
       count(distinct case when rlevel = 'xiaoR' then user_id else null end) as num_xiao,
       count(distinct case when rlevel = 'zhongR' then user_id else null end) as num_zhong,
       count(distinct case when rlevel = 'daR' then user_id else null end) as num_da,
       count(distinct case when rlevel = 'chaoR' then user_id else null end) as num_chao from pay_info 
group by 1 
order by 1 asc


-- ------------------------------------------------------------
-- 图表 4: 获取指定道具玩家礼包付费总额情况
-- 图表名称: 【P2】获取指定道具玩家礼包付费情况
-- 图表ID: 66ab3e972a840a587f0d7b50
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2 )


----获取指定道具玩家付费情况

select min(pay_price) as min_pay_price,
       approx_percentile(pay_price, 0.25) as pay_price25,
       approx_percentile(pay_price, 0.5) as pay_price50,
       avg(pay_price) as avg_pay_price,
       approx_percentile(pay_price, 0.75) as pay_price75,
       max(pay_price) as max_pay_price from 
(select user_id from v1041.dl_user_asset_d
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and asset_id = '${ asset_id }'
and add_num > 0 
group by 1) a 
inner join log_info b on a.user_id = b.user_id 
inner join 
(select user_id, sum(pay_price) as pay_price from v1041.ods_user_order 
where date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 
and iap_id in (${ iap_id })
group by 1 ) c on a.user_id = c.user_id


-- ------------------------------------------------------------
-- 图表 5: 节日活动礼包整体付费情况
-- 图表名称: 【P2】节日活动礼包整体购买情况-新
-- 图表ID: 66b03f3a7f0b225af663fbb5
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id from v1041.ods_user_click 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and control_id = '${ control_id }'
group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2 ), 


pay_info as (
select a.*, pay_price, pay_total from log_info a 
left join 
(select user_id,
        sum(case when iap_type = '混合-节日活动' then pay_price else null end) as pay_price,
        sum(pay_price) as pay_total from 
(select user_id, iap_id, pay_price from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 ) b1 
left join 
(select iap_id, iap_type from dim.iap where game_cd = 1041 ) b2 on b1.iap_id = b2.iap_id 
group by 1) b on a.user_id = b.user_id )


select *, 
       round(cast(pay_price as real) / cast(pay_total as real), 4) * 100 as price_ratio, 
       round(cast(buy_num as real) / cast(log_num as real), 4) * 100 as buy_ratio,
       round(cast(pay_price as real) / cast(buy_num as real), 2) as arppu,
       round(cast(pay_price as real) / cast(log_num as real), 2) as arpu from 
(select '全体玩家' as label, 
        count(distinct user_id) as log_num,
        count(distinct case when pay_price >0 then user_id else null end) as buy_num,
        sum(pay_price) as pay_price,
        sum(pay_total) as pay_total from pay_info
group by 1 
union all 
select '付费玩家' as label, 
        count(distinct user_id) as log_num, 
        count(distinct case when pay_price >0 then user_id else null end) as buy_num,
        sum(pay_price) as pay_price,
        sum(pay_total) as pay_total from pay_info
where rlevel != 'feiR'
group by 1 
union all 
select  rlevel as label, 
        count(distinct user_id) as log_num, 
        count(distinct case when pay_price >0 then user_id else null end) as buy_num,
        sum(pay_price) as pay_price,
        sum(pay_total) as pay_total from pay_info
where rlevel != 'feiR'
group by 1 )
order by log_num desc


-- ------------------------------------------------------------
-- 图表 6: 指定节日活动礼包付费总额对应人数情况
-- 图表名称: 【P2】指定节日活动礼包付费总额对应人数
-- 图表ID: 66bc4573cd6e3328d23e1ece
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id from v1041.ods_user_click 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and control_id = '${ control_id }'
group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2 ), 


pay_info as (
select a.*, rlevel from 
(select user_id, sum(pay_price) as total from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 
and iap_id in (${ iap_id })
group by 1 ) a 
inner join 
(select user_id, rlevel from log_info 
group by 1, 2) b on a.user_id = b.user_id ) 


select total, 
       count(distinct user_id) as num_all,
       count(distinct case when rlevel = 'xiaoR' then user_id else null end) as num_xiao,
       count(distinct case when rlevel = 'zhongR' then user_id else null end) as num_zhong,
       count(distinct case when rlevel = 'daR' then user_id else null end) as num_da,
       count(distinct case when rlevel = 'chaoR' then user_id else null end) as num_chao from pay_info 
group by 1 
order by 1 asc


-- ------------------------------------------------------------
-- 图表 7: 节日活动礼包付费总额对应人数情况
-- 图表名称: 【P2】节日活动礼包付费总额对应人数
-- 图表ID: 66bc2460cd6e3328d23e01a8
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id from v1041.ods_user_click 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and control_id = '${ control_id }'
group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2 ), 


pay_info as (
select a.*, rlevel from 
(select user_id, sum(pay_price) as total from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 
and iap_id in (select iap_id from dim.iap where game_cd = 1041 and iap_type = '混合-节日活动')
group by 1) a 
inner join 
(select user_id, rlevel from log_info 
group by 1, 2) b on a.user_id = b.user_id ) 

select total, 
       count(distinct user_id) as num_all,
       count(distinct case when rlevel = 'xiaoR' then user_id else null end) as num_xiao,
       count(distinct case when rlevel = 'zhongR' then user_id else null end) as num_zhong,
       count(distinct case when rlevel = 'daR' then user_id else null end) as num_da,
       count(distinct case when rlevel = 'chaoR' then user_id else null end) as num_chao from pay_info 
group by 1 
order by 1 asc


-- ------------------------------------------------------------
-- 图表 8: 各类型礼包付费额占比
-- 图表名称: 【P2】各类型付费额占比
-- 图表ID: 66e2aa8abe17ff5999d57ec6
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2 )

select pay_date, iap_type3, sum(pay_total) as pay_total from (
select a.*, pay_date, iap_type3, pay_total 
from log_info a 
left join 
(
select user_id, pay_date, iap_type3, sum(pay_price) as pay_total from 
(select user_id, date(date_add('hour',-8,created_at)) as pay_date, iap_id, pay_price from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 ) b1 
left join 
(select * from dim.iap where game_cd = 1041 ) b2 on b1.iap_id = b2.iap_id 
group by 1,2,3
) b on a.user_id = b.user_id
) group by 1,2


-- ------------------------------------------------------------
-- 图表 9: 节日活动各礼包付费情况
-- 图表名称: 【P2】节日活动礼包整体购买情况-分id
-- 图表ID: 66e25e77be17ff5999d52b86
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id from v1041.ods_user_click 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and control_id = '${ control_id }'
group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2 )
 
 
select iap_id, iap_id_name, count(distinct a.user_id) as pay_user_cnt, sum(pay_total) as pay_total 
from log_info a 
inner join 
(
select user_id, b1.iap_id, iap_id_name, sum(pay_price) as pay_total 
        from 
(select user_id, iap_id, pay_price from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 ) b1 
inner join 
(select iap_id, iap_id_name, iap_type from dim.iap where game_cd = 1041 and iap_type = '混合-节日活动') b2 on b1.iap_id = b2.iap_id 
group by 1,2,3) b on a.user_id = b.user_id 
group by 1,2


-- ------------------------------------------------------------
-- 图表 10: 节日活动礼包ARPPU
-- 图表名称: 【P2】节日活动礼包ARPPU
-- 图表ID: 67108043f3cbfa421b1bd12b
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as 
(select user_id, real_server_id, date(date_add('hour',-8,created_at)) as partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ), 

pay_info as 
(select pay_date, b1.user_id,rlevel,
        sum(case when iap_type = '混合-节日活动' then pay_price else null end) as pay_price,
        sum(pay_price) as pay_total,
        count(distinct case when iap_type = '混合-节日活动' then b1.user_id end) as pay_user_cnt,
        count(distinct b1.user_id) as total_pay_user_cnt from 
(select date(date_add('hour',-8,created_at)) as pay_date, user_id, iap_id, pay_price from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 ) b1 
left join 
(select iap_id, iap_type from dim.iap where game_cd = 1041 ) b2 on b1.iap_id = b2.iap_id 
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from v1041.da_user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1) b3 on b1.user_id = b3.user_id
group by 1,2,3)


select a.partition_date, sum(pay_price) / sum(pay_user_cnt) as arppu1,
sum(pay_total) / sum(total_pay_user_cnt) as arppu2
from log_info a 
left join pay_info b on a.partition_date = b.pay_date and a.user_id = b.user_id 
where rlevel in (${Rlevel})
group by 1


-- ------------------------------------------------------------
-- 图表 11: 节日活动礼包各服务器整体付费情况
-- 图表名称: 【P2】节日活动礼包整体购买情况-服务器
-- 图表ID: 67d23f83f56c9e4c8156c1ad
-- 数据源: TRINO
-- ------------------------------------------------------------

with log_info as (
select aa.user_id, real_server_id, coalesce(rlevel, 'feiR') as rlevel from 
(select user_id,
        a.partition_date,
        real_server_id,
        max(cast(schema as integer)) as schema from 
(select user_id, real_server_id, partition_date from v1041.ods_user_login
where create_time >= substring(cast(date_add('day', -1, date '${ report_date.start }') as varchar), 1 , 7 ) 
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and user_id not in (select user_id from dl.test_user where game_cd = 1041)
and real_server_id in (${ server_id })
group by 1, 2, 3 ) a 
left join 
(select partition_date,
        event_period as schema,
        case when cast(json_extract(event_attribute,'$.server_id') as varchar) is null then server_id 
             else cast(json_extract(event_attribute,'$.server_id') as varchar) end as server_id from v1041.ods_logic_server_event
where create_time >= '2023-01'
and event_type = 'schema'
and cast(event_period as integer) <= 6 
and event_status = '2') b on a.real_server_id = b.server_id and a.partition_date >= b.partition_date 
group by 1, 2, 3 ) aa 
inner join 
(select user_id from v1041.ods_user_click 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and control_id = '${ control_id }'
group by 1) bb on aa.user_id = bb.user_id
left join 
(select user_id, max_by(rlevel, create_date) as rlevel from da.user_rlevel_pay_ratio
where create_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
group by 1 ) cc on aa.user_id = cc.user_id 
where schema in (${ schema })
group by 1, 2, 3 ), 


pay_info as (
select a.*, pay_price, pay_total from log_info a 
left join 
(select user_id,
        sum(case when iap_type = '混合-节日活动' then pay_price else null end) as pay_price,
        sum(pay_price) as pay_total from 
(select user_id, iap_id, pay_price from v1041.ods_user_order 
where partition_date between cast(date_add('day', -1, date '${ report_date.start }') as varchar) and '${ report_date.end }'
and date(date_add('hour',-8,created_at)) between date '${ report_date.start }' and date '${ report_date.end }'
and pay_status = 1 ) b1 
left join 
(select iap_id, iap_type from dim.iap where game_cd = 1041 ) b2 on b1.iap_id = b2.iap_id 
group by 1) b on a.user_id = b.user_id )


select real_server_id, coalesce(sum(pay_price),0) as pay_price from pay_info
group by 1 
order by 1

