---
name: reference_background_scheduled_tasks
description: "本机 Windows 计划任务里所有 Claude 自动任务清单（触发时间/脚本路径/产出），问\"后台有什么自动任务\"或要新增/改/停自动任务时先读"
metadata: 
  node_type: memory
  type: reference
  originSessionId: cc067ea9-0727-440e-9ade-fd05cb35fe86
---

本机（C:\Users\linkang）跑的 Claude 后台自动任务清单。查/改前先 `Get-ScheduledTask | ? TaskName -match 'Claude'` 核对实际状态（本文件是快照，可能漂）。

## 任务清单（2026-06-10 核对）

| 任务名 | 触发 | 干啥 | 脚本/prompt |
|--------|------|------|------------|
| **ClaudeMorningPriority** | ~~每天 09:00~~ **已停用** | 跨项目今日优先 top-3（长期产出失败，已并入 DailyPlan） | `.claude\scripts\morning_priority_scan.ps1` + `_prompt.txt`（保留未删，回退用） |
| **ClaudeDailyPlan** | 每天 10:00 | **今日工作简报**（跨项目 top-3 + X2 节点 timeline+Jira+BUG）→ HTML 弹浏览器 | `.claude\scripts\daily_plan_scan.ps1`（2026-06-15 改：显式 `--model sonnet` + 预算 5→8）+ `daily_plan_prompt.txt` |
| **ClaudeBugScan** | 工作日(周一-五)每小时 09:23 起 | 扫 Jira 名下未解决 BUG 写 `_my_bugs_summary.txt` | bug-scan skill |
| **ClaudeFestivalReportOpen** | 每天 09:20 | 自动打开节日日报 HTML | — |
| **ClaudeDailyReport** | 每天 21:00 | 生成工作日报 txt + 回写 `工作line.md` 三/五节 | `_daily_report.py`（在 C--Windows-System32 项目目录） |
| **ClaudeX3FestivalMonitor** | 全天每小时 | X3 节日收入监控（现指夏日节第二批 1880-1900） | [[x3]] x3-festival-monitor |
| **ClaudeX2FestivalMonitor** | 全天每小时(:05) | X2 拓荒节日报(2026-06-12 D0 启用)，产出 `~\X2拓荒节日报_latest.html`，节日结束删任务 | [[reference_x2_festival_monitor]] |
| **ClaudeTokenWeeklyReport** | 每周五 17:00 | Token 用量周报 | — |
| **ClaudeWeeklyBackup** | 每周一 12:00 | 周备份 | — |
| **ClaudeMorningPriority/X3Monitor 退出码偶发 1** | — | 退出码 1 不一定真失败（claude -p 退出码不可靠）；DailyPlan 有新鲜度闸门兜底，X3Monitor 看产出 HTML 是否当日刷新判断 | — |

## 关键架构

- **晨间简报合并（2026-06-10）**：原本 09:00 MorningPriority（跨项目 top-3，极简 txt）+ 10:00 DailyPlan（只 X2，详细 HTML）两次弹窗冗余，且 MorningPriority 长期产出失败（`_今日优先.txt` 根本不存在）。
  合并方案 = **以 DailyPlan 健壮脚本为底盘**（有新鲜度闸门/HTML 渲染/flag/失败气泡），把跨项目 top-3 加成报告最顶一节，X2 详情保留在下。10:00 一次弹窗。MorningPriority 停用（脚本未删，可回退）。
- **新鲜度闸门**（daily_plan_scan.ps1 核心）：claude -p 退出码 0 也可能没真写出今日 txt（静默失败）→ 脚本校验 `_daily_plan.txt` 首行含今日日期才渲染 HTML，否则保留旧 mtime + 弹失败气泡。所以**改 prompt 时首行必须保持 `# {标题} {today}` 含日期**，否则闸门会判失败不渲染。
- **工作line.md = 单一事实源**：`C:\ADHD_agent\KB\工作计划\工作line.md`，每晚 21:00 DailyReport 自动写回三/五节（timeline 状态 + deadline 速查），早上 DailyPlan 读它出 top-3。三者闭环。

## ⚠️ claude -p 调度任务静默失败通用根因（2026-06-11 修，DailyPlan+DailyReport 同时中招）

- **现象**：claude -p 退出码 0，但目标 txt 没刷新到今日 → 新鲜度闸门判失败、弹失败气泡、HTML 保旧 mtime。两个日报 06-09~06-11 连续静默失败。
- **根因**：**预算在走到「写文件」步之前就被耗尽**。
  - 早间 DailyPlan：Jira curl 用 `currentUser()` 致 400 + curl SSL handshake 偶发失败，agent 反复重试烧光 `--max-budget-usd 5`。
  - 晚间 DailyReport：重负载日（如 132 条提问 + 改 工作line.md + 写 2 文件）$5 不够。
  - （另：06-07 两个任务都因 `claude.cmd` 不在 PATH 报错，是独立的环境问题，已自愈。）
- **修法（已落地，可复用到任何 claude -p 调度 prompt）**：
  1. prompt 里把**写文件设为最高优先级**：明确「先把核心内容写盘保底，再做次要分析/回写」，并把外部依赖（Jira 等）限「最多重试1次，失败就跳过继续」。
  2. 外部查询用**验证过的健壮写法**（Jira：`assignee=linkang`+`statusCategory!=Done`，SSL 失败走 PowerShell+Tls12，见 [[reference_jira]]）。
  3. **重负载任务预算给够**：DailyReport 已从 `--max-budget-usd 5` → `8`。
  - 排查口诀：先看 `_daily_plan_log.txt`/`_daily_report_log.txt` 区分「exit≠0(环境/PATH)」还是「exit 0 但未刷新(预算耗尽/没写盘)」；后者去对应 prompt 加写盘护栏 / 提预算。

## ⚠️ 调度脚本 `claude -p` 不带 `--model` 会漂移到停服模型（2026-06-15 DailyPlan 中招）

- **现象**：06-13 DailyPlan exit 1，报 `There's an issue with the selected model (claude-fable-5). It may not exist or you may not have access to it.`
- **根因**：脚本 `claude -p` **没指定 `--model`**，吃到 CLI 默认 model。本机默认漂到 `claude-fable-5`（已停服，本账号无权限，`.claude.json` 里残留 `claude-fable-5[1m]` 状态）→ 直接挂。注：settings.json 里 model 虽是 `opus[1m]`，但 `-p` 默认仍可能漂。
- **修法（已落地，可复用到任何 claude -p 调度脚本）**：命令行**显式写死 `--model sonnet`**（日报/巡检这类轻结构化任务 sonnet 够用、肯定有权限、还省钱），别依赖默认 model。
- 同次把 DailyPlan 预算 `--max-budget-usd 5` → `8`（与 DailyReport 对齐），解决并存的「exit 0 但未刷新(预算耗尽没写盘)」。备份 `daily_plan_scan.ps1.bak.20260615`。
- 🚫 **这些调度脚本绝不能加 `-NoProfile`**：脚本里的 `claude`/`ccr` 命令是 `C:\Users\linkang\Documents\WindowsPowerShell\profile.ps1` 里定义的函数（`function claude { & "...\claude.cmd" @args }`），加 `-NoProfile` 会让 `& claude` 直接找不到命令。任务 Action 当前是 `powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ...`，保持不动。
- ❓ **未解**：2026-06-15 手动 `Start-ScheduledTask` 触发时，powershell 进程卡在脚本启动阶段(连第8行"开始生成"日志都没写、无 claude 子进程)，挂 11 分钟后被手杀。profile 已排除(仅两行函数、不联网)，根因未定。可能是手动触发的偶发态。验证修复优先让次日 10:00 自动任务跑，别反复手动触发硬怼。
