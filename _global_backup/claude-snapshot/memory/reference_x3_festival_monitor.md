---
name: x3
description: X3 节日每日收入监控脚本+计划任务，移植自 X2，全服口径/Pack前缀圈节日/iap_type2分模块
metadata: 
  node_type: memory
  type: reference
  originSessionId: d85a4e25-0b5a-4f0e-862d-4d42bcee2238
---

X3 版节日日报，移植自 [[reference_ai_to_sql]] 用的 x2-festival-monitor。

## 位置
- 脚本：`C:\ADHD_agent\skills\x3-festival-monitor\x3_festival_daily.py`
- 建计划任务：`create_task.bat`（任务名 `ClaudeX3FestivalMonitor`，每天 09:00 跑，报昨天完整日）
- 日志：`C:\Users\linkang\_x3_festival_daily_log.txt`
- 产出：`C:\Users\linkang\X3{节日名}日报_D{n}_{日期}.html`（带按天页签的暗色 HTML，KPI/ARPU增量/模块构成/趋势/关注点）

## X3 口径差异（vs X2）
- 数仓：TRINO_HF / `v1090.ods_user_order`（X2 是 v1089.dl_user_order）
- 收入 USD 口径：仅 `currency_type='usd'` 取 `actual_charge`，其余(含 TOKEN)取 `pay_price`（TOKEN 的 actual_charge 自 2026-06-02 改记代币单位=USD×100，再取会放大 100 倍，见 [[feedback_x3_token_actual_charge_unit]]）
- 服段：默认全服（X3 节日按服龄分服上线，无统一日历服段）

## ⚠️ 数仓时区 = 北京时间（created_at + partition_date 都是）
实测验证：开场日 hour=8 节日流水暴涨、之前近 0；下线日(06-08) hour=8 起零成交。
若是 UTC，08:00 北京开场会落在 hour=0。所以 `hour(created_at)` 和 `partition_date` 都按北京日切。
节日活动 08:00(北京) 开/关 ↔ 数仓 hour=8。

## ⚠️ 节日必须配 FESTIVAL_END_TS 时间上界（2026-06-08 夏日踩坑）
白名单口径只认「iap_id 在累充白名单里」，**无活动下线时间卡口**。白名单含大量**跨活动复用包**
(情人节连锁 2107xx / 通用通行证 130020·130021 / 许愿池 1002001)，这些包**下个活动会被重新挂上来卖**，
没卡口会把节日下线后的常态流水继续误算成本届节日。
- 修复：脚本顶部加 `FESTIVAL_END_TS`(节日活动下线时点，北京时间) + `FEST_TIME_GUARD = "o.created_at < TIMESTAMP '...'"`，
  焊进 `fest_cond`(line~360) 和 `summer_pred`(line~522) 两处节日预测式，一处定义全局生效。只改夏日侧不动 BENCHMARK_FEST_PRED。
- 夏日窗口 = 05-29 08:00 → 06-08 08:00(北京)。专属装饰/拜访包 06-05 就停售，但累充活动+复用包挂到 06-08 08:00；
  06-08 当天 00:00~08:00 有 $400 真实收尾尾单，08:00 后零成交。对 D0~D9 无影响(全在卡口前)。

## ⚠️ 节日礼包口径必须查配置表，不能用 Pack 前缀/名字猜（踩坑）
- **错误做法**：按 iap_id 前缀（夏日=2109）或 dim_iap 名字圈节日 → 漏包严重。
  夏日恋语**复用情人节 2107xx 连锁/锚点礼包**（换 TimeCycle），前缀 2109 只框到 4 个装饰/拜访包，
  会把 2107xx 特惠连锁/抽奖券 + 130020/130021 通行证 + 1002001 许愿池（D1 约 $2239）全错算成"非节日"。
- **正确做法**：节日礼包全集 = `ActvOnline.RechargePointPackWhitelist`（累充活动白名单，见 [[reference_x3_recharge_isolation]]）。
  脚本运行时实时读 `C:\x3\gdconfig\tsv\ActvOnline__ActvOnline.tsv` 的 RECHARGE_ACTV_ID 行 + `Pack__Pack.tsv` 的 PackType。
  夏日恋语累充 ContentID = **100595**（行名"26情人节-累充"是 TimeCycle 复用残留，别被名字骗，见 [[feedback_x3_timecycle_name_legacy]]）。
- **模块分类 = Pack.PackType**（11=特惠连锁 / 15=抽奖券 / 16=家具外观 / 18=通行证），PACK_OVERRIDE 拆细：210717家具/1002001许愿池/210921拜访皮肤/210917·918·919装饰礼包（PackType11但属夏日恋语装饰链647，单独成"装饰礼包"模块）。
- **ALWAYS_INCLUDE_PACKS**：装饰礼包 917/918/919 强制并入节日（累充白名单本期可能不收它们，且配置在被实时编辑会 14↔17 抖动；并入后收入口径稳定）。累充白名单口径 = "算不算累充积分"，≠ "是不是节日礼包"，收入监控按后者。

## 换节日只改脚本顶部配置块
`FESTIVAL_NAME / FESTIVAL_D0(Pack首销日) / BASELINE_START/END / RECHARGE_ACTV_ID(该节日累充ContentID)`
（D0 查首销日：`SELECT min(partition_date) FROM v1090.ods_user_order WHERE pay_status=1 AND iap_id IN (白名单)`；
 累充 ContentID 在 ActvOnline 里找该节日的"累充"行，看 RechargePointPackWhitelist 非空那行）
- 支持回算：`python x3_festival_daily.py 2026-05-29` 或环境变量 `X3_REPORT_DATE`，生成指定日报告。

## ⚠️ FESTIVAL_D0 必须是活动真实开场日，不能用"pack 首销日"推
节日 pack 多为**跨节日复用包**（130020/130021 节庆通用通行证、1002001 许愿池、2107xx 情人节连锁被夏日复用），
无限期查 `min(partition_date)` 会查到去年(2025-05)别的节日的尾单。正确做法：看该服段节日流水从 0 起跳那天。
夏日恋语 1-88 服：05-25 仅 $30(噪声尾单)、05-26~28 为 0、**05-29 起跳 $2918/105人 → D0=05-29**。
（FESTIVAL_D0 + partition_date 下限过滤保证只算当期；占比分母=节日期内累计总流水，不含开场前。）

## 首日同期对比（上期节日基准）
报告含"首日同期对比"区块：本期夏日 D0 vs 上期情人节 D0（BENCHMARK_D0=2026-02-06），**按已跑小时对齐**。
- 两节日均 **08:00 开场**（节日流水从该时跳起，之前是背景噪声）；LAUNCH_HOUR=8。
- 脚本查 `hour(created_at)` 窗口 `[8, through]`，through=夏日 D0 当前最大小时，两边同窗口比，避免拿夏日10h比情人节整天。
- 情人节口径：`iap_id LIKE '2107%' OR in (130020,130021,1002001)`，模块同 PackType（210716晋升皮肤=PackType1→皮肤礼包）。
- **ARPU 口径 = 节日流水 / 当日总付费人数**（不是节日付费人数！主区和对比区都用总付费人数 d.payers，见 [[feedback_x3_festival_arpu_denominator]]）。
- 首10h 实测：情人节 总$14527/439人/节日$4998/占比34.4%/节日ARPU$11.4；夏日 总$9290/245人/节日$4212/占比45.3%/节日ARPU$17.2。
  结论：夏日大盘缩水(4个月服龄)，但节日占比↑、节日付费人数↑、节日ARPU↑（$17 vs $11），节日变现效率全面更高；仅大盘绝对规模落后。

## 当前配置（2026-06-09 改指第二批）
**第二批 = 1880/1890/1900 三服**（夏日恋语分服龄滚动上线的下一批），累充仍 100595。
- `FESTIVAL_NAME=夏日节1880-1900服`、**D0=2026-06-09**（夏日专属装饰包 210917/918/919 在该批 06-05~06-08 收入为 0、06-09 首次出单实测验证）、
  `FESTIVAL_END_TS=2026-06-19 08:00`（沿用 10 天窗口）、基线 05-26~06-08（实测无夏日流水污染）、
  `SERVER_FILTER=BETWEEN 1880 AND 1900`。D0 早盘：总$126/节日$65/9人。
- ⚠️ **同期对比(BENCHMARK_*)/R级生命周期对齐仍是第一批校准值**（成熟 1000-1540 情人节服），而第二批是较年轻服
  （1880 开服~04-27、D0 约服龄 43 天，1900 为爆发期大服）→ 生命周期不匹配，对比区块仅粗略参考，待按本批服龄重校准。
- 第一批历史（2026-05-29 建）：1-88服(1000-1870)，D0=05-29，基线 05-15~05-28，05-29→06-08 已收尾，日报 HTML 已逐日落盘归档。
  D0(05-29)：总$8548/节日$2918/246人/占比34.1%。
- 白名单实时读 config（17 包，含装饰特惠 210917/918/919），换批只改脚本顶部配置块即可。
详见 X3 数仓口径 [[reference_x3_festival_performance]]。

## R级维度分析（2026-06 夏日节增量，对比情人节）
- 报告已加 R级口径：分时图 R级筛选、R级分层、R级付费率&ARPU(vs 上期情人节)、按日/累计 R级对打。
- **R级来源**：`v1090.dl_user_rlevel_all_info` 按日快照(chaoR/daR/zhongR/xiaoR→超/大/中/小R)；该表**不全**(漏部分真实付费用户)，故分类=快照优先 + 累充(USD)兜底估档(≥$1500超R/≥$500大R/≥$50中R/>0小R，阈值由已分级用户累充分布反推)；非R=零充免费玩家。
- **付费率必须用"付费玩家付费率"= 节日付费人数 / 当期总付费人数**（分母=付费玩家，排除免费玩家占比）。用"节日付费/活跃"会被免费玩家结构带歪(老服免费玩家流失→分母变小→付费率虚高)。
- **服段 = 「服务器生命周期一致」原则**（核心）：生命周期一致 = **各期取 D0 时服龄(距开服天数)同阶段的服(按服龄阈值匹配)，不是同一批物理服**；排除新服爆发期干扰。**夏日(本期)=1000~1870(88服，节日实际投放到1870；1880 在 D0 时仅 D32 未达 D35 且未上节日，排除)**、**情人节(对比)=1000~1540(55服)**，两期各取"D0已过D35的成熟服"。代码 SERVER_FILTER(88)/SERVER_FILTER_VAL(55)+查询函数 sf 参数。dim_open_server.open_time 算服龄。绝对值跨服数不同只可比率。
- **⚠️ 待办(最终版)**：R级分类时点要**钉到"节日后"的固定快照**(节日结束后那份)，反映玩家经此节日的最终档位、且不随刷新漂。节日进行中(as-of当前)会随累充兜底含本期消费而漂，仅小R/非R边界动，超/大/中R稳定——进行中不改，节后做最终版再钉死。
- 脚本顶部 SERVER_FILTER / RCLASS / rl_join/ltv_join(asof) 已就绪，最终版只需把 as-of 改成节后快照日。
