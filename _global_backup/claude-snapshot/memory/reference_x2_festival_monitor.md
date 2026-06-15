---
name: reference_x2_festival_monitor
description: X2 节日收入日监控脚本与口径——每个新节日只改配置区；节日判定=dim_iap节日类型(抓复用旧id) + 新累充段id兜底
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8a63801d-35eb-4466-b3d8-8c2950b6492a
---

# X2 节日收入日监控（x2-festival-monitor）

- 脚本：`C:\ADHD_agent\skills\x2-festival-monitor\x2_festival_daily.py`，**默认当天**（每小时实时刷新）；回算传日期参数或 `X2_REPORT_DATE` 环境变量
- 产出：`~\X2{节日}日报_D{n}_{date}.html` + `~\X2{节日}日报_latest.html`（固定名副本，长期开着同一链接）
- 计划任务：`ClaudeX2FestivalMonitor` 每小时(:05)，`create_task.bat` 注册（⚠️bat 中文注释在 GBK 控制台会炸，直接用里面的 schtasks 命令）；节日结束 `schtasks /delete /tn ClaudeX2FestivalMonitor /f`

## 每个新节日要改的配置区（脚本顶部）

FESTIVAL_NAME / FESTIVAL_D0 / BASELINE_START~END(D0前14天) / SERVER_FILTER / MODULE_RULES / ID_SEG_RULES

## 节日判定口径（2026拓荒节定稿，三层）

1. `dim_iap.iap_type IN ('混合-节日活动','活动礼包')` — **抓复用旧 id 的模块**（X2 节日 BP/GACHA/大富翁/七日/抽奖券每节日复用同一批 iap id，dim_iap 名字还是旧节日的，靠类型不靠名字）
2. 新累充段 id 范围兜底（dim_iap 未录入时名字=裸id）— **真源=该节日累充表 2122 的白名单**(2011 id 改前缀 2013)，不能猜前缀；拓荒=2013910029/30 + 2013920120-154/161-191(+193 random)
3. 挖矿关卡 scene 礼包 `20132302xx`（iap_type=小游戏-挖矿，不在节日类型里，要显式加段）

## 模块归类（classify_module 两层）

- 名字关键词优先（MODULE_RULES）→ id 段兜底（ID_SEG_RULES，没名字的新 id 先整桶「节日累充礼包」，dim_iap 录入名字后自动细分）
- 精确细分真源：用户给的礼包名表（2026拓荒 = GSheet `1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E` gid=1938706798 F列名字）

## 模块易混点

- **强消耗抽奖券 ≠ GACHA**（2026-06-12 核实）：`2013500177-179`(节日通用-强消耗抽奖券礼包) 的 PkgTitle = `LC_ITEM_new_strong_consume_gacha_token2_name`，喂强消耗活动(消耗攒积分+奖池抽奖)；节日 GACHA = `920188-197` 礼包 → 巨猿 gacha 内圈道具 `111111316`。两模块分开统计，占星/拓荒口径一致
- 2026 拓荒累充段精确 id→模块映射已焊进脚本 `ID_SEG_RULES`（逐段带注释，真源 = iap_template_x2(qa) F列）

## 坑

- 灰度服别想当然：拓荒节无灰度全正式（占星有 12-75 服区间，拓荒是 12服+ 全量）
- D0 当天跑出来是部分实时数据，完整 D0 日报 = D0+1 天自动跑
- 复用旧 iap id 在 dim_iap 显示旧节日名（如"2025占星节高级通行证"实为拓荒 BP），按类型+出单日期判归属
