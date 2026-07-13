---
name: project_token_workflow_optimization
description: "2026-07 token用量工作流审计与优化案：Top7工作流占比、已落地的4项优化（速查/部署/GM组合脚本+合并路由）、扫描工具位置；再做token审计或问'哪个工作流最烧钱'先读"
metadata: 
  node_type: memory
  type: project
  originSessionId: 387e7bb5-f12c-4e78-8515-ae4c0cdc8735
---

# Token 用量工作流审计与优化（2026-07-06）

## 审计结论（近30天，576会话，~240亿token，名义~$63k——走中转渠道，只看相对占比）

Top 7 工作流按消耗：①节日活动换皮全链路 ~26% ②美术/媒体资产生产 ~22% ③客户端功能开发(Unity) ~13% ④BUG排查 ~10% ⑤数据分析/日报 ~5% ⑥部署/测试环境/GM ~4.5% ⑦配置仓分支合并 ~3%。

**核心规律**：贵的不是任务是**超长会话 cache 读滚雪球**（单会话最高 16.7 亿 token，output 仅占 0.1%）。用户明确**不拆长会话**（token 够用，靠 memory/唯一入口文档随时开新窗口即可）——别再建议拆。

**分类脚本的坑**：按「skill/知识库/脚本」类关键词归类会把 90% 会话吸进「工具建设」（用户 CLAUDE.md 要求每次沉淀，这些词无处不在）。正解=导出 Top 会话清单人工归类（Top100 占 91% 费用）。

## 已落地优化（2026-07-06，本案四件）

1. **bug-scan 停用**（无 QA，30天省~$1649）：`ClaudeBugScan` 已 Disable 未删，恢复=`Enable-ScheduledTask ClaudeBugScan`。
2. **活动配置速查** `x3-config-export\scripts\actv_lookup.py`：ID/关键词查 ActvOnline+自动跟一层外键（TimeCycle/ActvGroup/Reward，Reward 按 col1=RewardID 匹配）。已实测（102993/远航战备）。
3. **beta 部署一条龙** `test-env-prepare-x3\scripts\deploy_beta.py`：Play+Map(+Center auto)同批→等20s→复查Run→重试一次。--query 模式已实测；**真部署路径未实测，首用时盯一把**。
4. **GM 组合** `test-env-prepare-x3\scripts\gm_combo.py`：`servertime`(查逻辑时间,**已实测**·330服时钟已被时移到未来) / `open-activity`(getservertime→timegm→deployserveractivity) / `advance-time`(跨天推进+自动复查)。**真开活动/真推时间未实测，首用时盯一把**。坑：`--player` 必须是该服现存玩家，清过服的旧ID（如330服的14000）静默返回 `returnInfo:[]`；现存ID用 pymongo 捞 ServerPlayer。

**合并路由**（CLAUDE.md X3 段已加）：X3 配置合并固定走配置仓官方 skill `C:\x3\gdconfig\scripts\x3_skill_merge.md`（+conflict/audit 那套），开工必验 tsv3way driver 已注册。近14天合并烧 ~$1600/10次全是无 skill 裸奔 git。

**media-worker 漏网**：x3-media 已强制派单（大会话合规）；残留=grfal-api skill 被直调做修图/压缩（已在其 SKILL.md 顶部加路由拦截注记）。

## 复用工具

- **Top 会话扫描器**：`C:\Users\linkang\.claude\scripts\token_top_sessions.py`（扫 `~\.claude\projects\*\*.jsonl`，按费用排 Top100+首条消息+skill调用，改 `cutoff` 天数）。周报脚本 `token_weekly_report.py` 只有 6 粗类，细看用这个。
- 会话记录里判「主会话直调 vs 派子agent」：tool_use name=Agent/Task 的 input.subagent_type + `isSidechain` 标记。

## 未做/候选

- GM 常用组合速查（跨天/加道具等）只做了 open-activity，其余按需加进 gm_combo.py 子命令。
- 本地服 3080 部署一条龙未做（链路复杂：stop_gs/ExportTable/软链，见 [[workflow_x3_local_server_gm_telnet]]），仍走 memory 手动。

相关：[[reference_background_scheduled_tasks]] [[workflow_x3_merge_conflict_audit]] [[reference_x3_kadmin_deploy]]
