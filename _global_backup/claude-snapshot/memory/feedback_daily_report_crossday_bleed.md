---
name: feedback_daily_report_crossday_bleed
description: 每日工作日报按文件mtime挑会话会把跨天历史误算成今天，改成按消息真实北京时间过滤
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 15089e8e-9b83-4e7f-8a0a-be3da1e6abc1
---

每日工作日报（`daily_report_scan.ps1` 21:00 跑 → `claude -p`）2026-06-08 "全错"：报告把 5-29 起的拓荒节全流程等多天工作全堆到 6-08。

**根因**：旧 prompt 让模型"按 jsonl 文件 LastWriteTime=今天挑会话 + 整份读取"。但会话文件是长期续用的——① 一个 6.5 开的长会话今天只要被碰一次 mtime 就变今天，整份跨天历史被算进今天；② 实测 42 个今天 mtime 的文件里 13 个内部根本没有当天消息（纯老会话误纳）。再叠加模型没遵守格式/输出路径。

**修复（已落地）**：
- 新增确定性提取器 `~\.claude\scripts\extract_today_sessions.py`：扫所有 jsonl，按【每条消息的真实北京时间(UTC+8)】过滤 type==user 的真实提问（剔 system-reminder/tool_result/Stop hook feedback 等噪声），按会话分组写 `~\_today_user_prompts.txt`。
- `daily_report_scan.ps1` 在 `claude -p` 前先跑提取器。
- `daily_report_prompt.txt` 步骤2-3 改成"直接 Read `_today_user_prompts.txt`"，明令禁止再按文件 mtime 扫 jsonl。

**通用教训**：凡按"jsonl 文件 mtime"判断"某天做了啥"都不可靠（会话跨天续用）；要按记录内 timestamp 切，且 timestamp 是 UTC、本地工作日要转北京时间(UTC+8)再取 date。相关渲染链路见 [[reference_daily_report_html]]。
