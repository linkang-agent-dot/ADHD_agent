---
name: reference_daily_report_html
description: 每日日报/工作节点已 HTML 化每天浏览器弹出，含通用 txt→HTML 渲染器
metadata: 
  node_type: memory
  type: reference
  originSessionId: c63c1018-eea1-4f38-a96b-ff6e2ad0358e
---

`~\.claude\scripts\` 下几个 Windows 定时任务的产出 HTML 化、每天用默认浏览器自动弹出：

- **通用渲染器** `render_report_html.py` —— `python render_report_html.py <in.txt> <out.html> [标题]`。无外部依赖，自带深色样式。同吃两种格式：①标题行+"N. 标题 —— 一句话"卡片+【段落】小节（日报）；②轻 markdown（`#/##/###` 标题、`|表格|`、`**粗体**`、`-/N.` 列表）。`#` 当页面大标题，`##`→h2，`###`→h3；整组都含 `——` 的列表渲染成卡片。**复用它，别再为别的报告现写 HTML**。
- **每日日报** `daily_report_scan.ps1`（21:00）→ `claude -p` 出 `每日日报\_latest.txt` → 渲染 `_latest.html` → 浏览器弹出（兜底 notepad txt）。
- **每日工作节点** `daily_plan_scan.ps1`（10:00）→ `claude -p` 出 `~\_daily_plan.txt` → 渲染 `~\_daily_plan.html` → 浏览器弹出 + 保留 flag/气泡。
- **节日日报**（X3/X2）走另一条：python 直接生成 HTML，`open_festival_report.ps1` + 任务 `ClaudeFestivalReportOpen`（09:20）每天开"今天更新过的"。

改这些 .ps1 注意 [[feedback_ps_script_needs_bom]]：含中文必须 UTF-8+BOM，否则定时任务静默崩。

## ⚠️ claude -p 静默失败防线（2026-06-09 加，daily_plan_scan.ps1）
`claude -p` headless 即使退出码 0，也可能没真正写出 txt（实测 06-06~06-09 连续 4 天没写 `_daily_plan.txt`、日志却记"成功"，渲染步骤把旧 txt 重渲一遍 → HTML mtime 天天刷新但**内容冻在旧日期**，是 mtime 新/内容旧的静默失败，同源 [[feedback_daily_report_crossday_bleed]]）。
- 修复：渲染前加**新鲜度闸门**——校验 `_daily_plan.txt` 首行日期 == 今天(`-match [regex]::Escape($today)`)。`exitCode 0 且 fresh` 才算成功并渲染+弹成功气泡；否则记真失败(区分非0退出/退出0但txt未刷新)、**跳过渲染**(HTML 保旧 mtime 便于一眼看出今天没更新)、弹⚠️警告气泡。
- 其它两条同架构链路(daily_report/festival)如出现同样"看着更新实则旧"，照搬这道首行日期闸门。
