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
| **ClaudeDailyPlan** | 每天 10:00 | **今日工作简报**（跨项目 top-3 + X2 节点 timeline+Jira+BUG）→ HTML 弹浏览器 | `.claude\scripts\daily_plan_scan.ps1`（2026-06-15 改：显式 `--model sonnet5` + 预算 5→8）+ `daily_plan_prompt.txt` |
| **ClaudeBugScan** | ~~工作日每小时~~ **已停用(2026-07-06)** | 扫 Jira 名下未解决 BUG 写 `_my_bugs_summary.txt`；因当前无 QA、且 30 天烧掉约 $1649 名义 token 成本，用户要求停。任务保留未删，QA 回归后 `Enable-ScheduledTask ClaudeBugScan` 即恢复 | bug-scan skill |
| **ClaudeFestivalReportOpen** | 每天 09:20 | 自动打开节日日报 HTML（扫 `KB\产出-数据分析\节日日报_实时\`；**2026-07-06 修复：改为把当天更新过的每份 `*_latest.html` 逐一打开**——原"只开最新一份"在多节日并行时永远只弹最后刷新的那个，世界杯/深海曾连续4天没被弹出。同日改：**脚本 -Prefix 改可选，默认循环 X3/X2/P2**，任务只调一次脚本） | `open_festival_report.ps1`（$scanDir）。⚠️改此任务两坑：schtasks `/tr` 有**261字符上限**(塞不下多次调用→让脚本自己循环)；`schtasks /change` 会**交互式要密码卡死**→改任务动作用 `Set-ScheduledTask -Action` |
| **ClaudeP2CumRevMonitor** | 每天 09:12 | P2 大盘累计付费监控(近2个月滚动·全服·北京日切)：三张折线=日流水/累计/ARPU。节日=dim_iap.iap_type『混合-节日活动』(P2 dim表干净自带标记·无需白名单)，归属按日期窗切(拓荒节5/12-6/09→深海节6/10-7/01→世界杯竞猜7/02+·窗口由日流水曲线实测)。产出 `KB\产出-数据分析\节日日报_实时\P2累计付费日报_latest.html`。**P2节日占大盘44% vs X3仅6-10%**(2026-07-06首跑)。新节日=FEST_WINDOWS头部加一项 | `skills\p2-festival-monitor\p2_cumulative_monitor.py`(克隆X3版·TRINO_AWS/v1041.dl_user_order/pay_price无pay_status列) |
| **ClaudeDailyReport** | 每天 21:00 | 生成工作日报 txt + 回写 `工作line.md` 三/五节 | `_daily_report.py`（在 C--Windows-System32 项目目录） |
| **ClaudeX3FestivalMonitor** | 全天每小时 | X3 节日收入监控（06-19 08:30 后转夏日节第三批 1910-1930） | [[x3]] x3-festival-monitor |
| **ClaudeX3SwitchBatch3** | 一次性 2026-06-19 08:30 | 夏日节日报 批二(1880-1900)→批三(1910-1930) 自动切换，跑完自删 | `skills\x3-festival-monitor\_switch_batch3.py`，详见 [[x3]] |
| **ClaudeX3WorldCupMonitor** | 全天每小时(:35) | X3 世界杯节日收入监控(D0=2026-06-26·全服1-98=server_id 1000-1970·累充100597·END 07-20)，产出 `KB\产出-数据分析\节日日报_实时\X3世界杯日报_latest.html`；决赛后(7/20+)删任务 | `skills\x3-festival-monitor\x3_worldcup_daily.py`(克隆夏日脚本仅改配置块)，详见 [[x3]] |
| **ClaudeX3DeepSeaMonitor** | 全天每小时(:50) | X3 深海节收入监控(D0=2026-07-03·59服显式清单1170-2010·累充100598白名单45包·UTC日切·END 07-17北京08:00)，产出 `KB\产出-数据分析\节日日报_实时\X3深海节日报_latest.html`；7/17后删任务 | `skills\x3-festival-monitor\x3_deepsea_daily.py`(克隆世界杯脚本·配置读取改走git show origin/dev)，详见 [[x3]] |
| **ClaudeX3CumRevMonitor** | 每天 09:10 | X3 大盘累计付费监控(近2个月滚动·北京日切)：**4个服段页签**(全服/世界杯1-98服/深海59服/总效果1-88服=成熟服基本盘·看节日净拉动认它·节日收入均已按服段过滤)×三张折线图(日流水/累计付费/ARPU)，总付费 vs 各节日(尼罗滚动/夏日/世界杯/深海·CASE链每单只归一个节日·复用包130020/021/1002001按时间窗归属)，**图上竖线标注各节日上线时间点**(含夏日批二/批三)；ARPU分母=当日总付费人数。产出 `KB\产出-数据分析\节日日报_实时\X3累计付费日报_latest.html`(文件名带"日报_latest"→09:20 FestivalReportOpen 会自动弹)。**新节日上线=FESTIVALS头部加一项(谓词+窗口+颜色+d0)，需要就SEGMENTS加服段页签** | `skills\x3-festival-monitor\x3_cumulative_monitor.py` |
| ~~**ClaudeX2FestivalMonitor**~~ **已删除(2026-06-29 D17 收工)** | ~~全天每小时(:05)~~ | X2 拓荒节日报(2026-06-12 D0~06-29 D17)，产出 `~\X2拓荒节日报_latest.html`；节日结束用户确认停，已 Unregister | [[reference_x2_festival_monitor]] |
| **ClaudeTokenWeeklyReport** | 每周五 17:00 | ①Token 用量周报 ②**本周归纳清单**(2026-06-15加挂)：扫7天KB/memory改动→`claude -p`按模块列「知识\|对应模块\|来源」→`~\归纳验收周报_latest.md`+气泡。两步独立fail-open。**产出已迁中文名+流水归档(2026-07-06)**：`KB\_自动流水\Token周报\Token周报_{date}.md/html`+`Token周报_latest.html`，两个 py 已同步改路径/文件名；工作line每日备份同步迁 `KB\_自动流水\工作line备份\`（daily_report_scan.ps1 $bakDir 已改，带BOM保存） | `token_weekly_scan.ps1`(末尾归纳段) + `token_weekly_report.py`/`_html.py`(token) + `handover_review_prompt.txt`(归纳) |
| **WC-GuessDashboard-Daily12** | 每天 12:00(北京) | X3世界杯竞猜运营看板：拉iGame(prod)实时竞猜+赛程交叉分类→对阵总览/已上线/待上线/待发奖/已发奖 HTML | `KB\产出-数值设计\X3_世界杯\_gen_竞猜运营看板.py`(数据源 `wc_dashboard_data.json`:对阵确定加schedule、发完奖加settled);产出 `..\世界杯竞猜运营看板.html`;决赛后删任务。⚠️任务**直调python.exe+脚本路径**(非.bat·中文路径在cmd/.bat下Task环境编码崩→result1;直调python Unicode传参=result0) |
| **ClaudeX3PiggyBankDaily** | 每天 10:30 | 异国美酒储蓄罐回归报告**每日图表更新**:拉datain日数据→重绘ARPPU/日流水折线+储蓄罐vs纯异国美酒礼包堆叠面积+大盘均值线→回写HTML(只更图表+数据截至日期;漏斗/表/KPI是上线窗快照不动)。**纯python直调**(非claude -p、非.bat) | `KB\产出-数值设计\X3_异国美酒储蓄罐\_daily_update.py`(import ai-to-sql的_datain_api.execute_sql,DATAIN_API_KEY走User环境变量,q()带3次重试抗datain抖动);产出 `..\异国美酒储蓄罐_增加档位分析.html` |
| **ClaudeWeeklyBackup** | 每周一 12:00 | **全局 .claude 周镜像备份**：把 `~\.claude` 的 memory/agents/hooks/settings.json/skills(仅文本代码配置且单文件≤512KB) robocopy /MIR 到 `C:\ADHD_agent\_global_backup\claude-snapshot\`；commit+push 由每日 18:00 的 **PushADHD** 任务顺带完成（git 里 auto sync commit 落在周一 18:00）。周一 12:00 后改的 memory/skill 要等下周一才进快照；日志 `_global_backup\backup_log.txt`（2026-07-13 核实自动在跑） | `C:\ADHD_agent\scripts\weekly_global_backup.ps1` |
| **帕鲁情报巡检**(计划任务名待核对,脚本已就位) | 每天 12:00/18:00 | 幻兽帕鲁1.0 情报巡检：B站增量+WebSearch(补丁/meta)扫描，判定有无真情报(新补丁/强度共识变化/图鉴数据错误/新玩法验证)，有则小改攻略合集HTML(`C:\Users\linkang\Desktop\幻兽帕鲁1.0_攻略合集\`)，报告写 `KB\_自动流水\帕鲁情报\帕鲁情报_latest.md`。⚠️stdin管道喂prompt乱码坑2026-07-17已修(见下条+[[reference_headless_claude_cli]]) | `C:\ADHD_agent\skills\palworld-tools\palworld_intel_scan.ps1` + `palworld_intel_prompt.txt`；状态 `intel_state.json`(bili_last_ts增量水位) |
| **GameRadar-Daily** | 每天 09:00 | 策略游戏雷达(中/美/日)：App Store+Google Play+YouTube+Reddit 热门/飙升榜→HTML 弹浏览器；个人选游戏用 | `C:\Users\linkang\game-radar\run_daily.ps1`(纯 python，非 claude -p，无静默失败风险)，详见 [[reference_game_radar]] || **ClaudeMorningPriority/X3Monitor 退出码偶发 1** | — | 退出码 1 不一定真失败（claude -p 退出码不可靠）；DailyPlan 有新鲜度闸门兜底，X3Monitor 看产出 HTML 是否当日刷新判断 | — |

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

## ⚠️ DailyReport 瞬时静默失败 → 加自愈重试（2026-06-15）

- **现象**：`ClaudeDailyReport`（21:00）06-12~15 连续 4 天失败 —— `claude -p` 退出码 0 但没写出今日 `_latest.txt`，新鲜度闸门判失败、`_latest.txt` 冻在 06-11。`--model opus` / `$null|` 喂 stdin / `--max-budget 8` 三道已知修复当时都在了。
- **定位**：交互环境用**原样命令**手动复现（把 `_latest.txt` 设回过期态再跑）→ **176s 正常写出、exit 0、成功**。即命令本身没 bug，是 21:00 headless 跑的**瞬时态**失败（API 抖动/模型路由/资源争用，重跑即好）。无法在交互会话稳定复现。
- **修法（已落地）**：`daily_report_scan.ps1` 把 `claude -p` + 新鲜度闸门包进**最多 3 次自愈重试循环**，刷新到今日即 break；每次尝试写日志。re-run 必成立 → 重试能兜住这类瞬时失败。备份 `daily_report_scan.ps1.bak.20260615b`。
- 排查口诀：DailyReport 失败先看是否「exit 0 但 _latest.txt 没刷新」；是 → 八成瞬时态，手动 `Start-ScheduledTask ClaudeDailyReport` 或直接重跑命令多半即好；重试循环现已自动兜底。同源 DailyPlan 若复发可照搬此重试块。
- **重试仍救不回的两种实测（06-16/06-17）**：① 06-16 三次重试全失败、第3次 exit 1 报 `API Error: The socket connection was closed unexpectedly`——21:00 那一刻 API 网络层整段抖、背靠背重试撞同一波；② 06-17 三次全 exit 0 但不写盘、**无任何报错**——claude 真返回成功却没写文件。两次都是手动重跑即成。
- **增强（2026-06-18 落地，仍在观察）**：(a) 重试改**带间隔退避** `@(0,120,240)` 秒，跨过 21:00 短时提供商抖动（治 socket 类）；(b) **每次尝试把 claude 完整输出+真实耗时落盘** `~\_daily_report_attempts.txt`（治"exit 0 不写盘"——此前成功路径不记 $result，连日失败手里没证据；下次失败看这个文件即可判断 claude 报错/没调Write/预算耗尽/提供商degraded）。备份 `daily_report_scan.ps1.bak.20260615b`。**根因尚未坐实**，靠 attempts 文件取证后再定。
- ⚠️ 猜测但未证实：用户频繁切 team/onehub provider，若 21:00 活跃 provider 是 onehub 且不稳，claude -p 可能拿到 degraded 响应/空结果却 exit 0。等 attempts 取证。

## 🎯 DailyReport 连续失败真根因坐实（2026-06-25，前面所有猜测作废）

- **真根因**：`ClaudeDailyReport` 计划任务 cwd=`C:\Windows\System32`，`claude -p` 据此加载的是 **`C--Windows-System32` 项目的 memory**（不是 `C--Users-linkang`！）。那里的 `daily-report-from-transcripts.md` 把日报输出路径写成旧的 **`C:\Users\linkang\工作日报_{date}.txt`**（home，错），claude 听 memory 不听 prompt → **每晚都成功生成、却写错地方**；新鲜度闸门只认 KB `每日日报\_latest.txt`，永远判失败。06-08~06-24 home 里堆了 16 份 `工作日报_{date}.txt` 就是铁证。
- **为什么之前查不出/手动跑能成**：① 手动跑 cwd=`C:\Users\linkang` → 加载 linkang memory（无此坑）→ 听 prompt 写对 KB ✅；② 脚本成功路径不记 $result，直到 06-18 加了 `_daily_report_attempts.txt` 才抓到 claude 自报"日报已生成：C:\Users\linkang\工作日报_2026-06-24.txt"——一眼看穿写错路径。**之前"瞬时态/socket/provider"全是误判**（socket 那次 06-16 是真插曲，但不是连续失败主因）。
- **修法（2026-06-25 落地，治本+兜底）**：① 改 `C--Windows-System32\memory\daily-report-from-transcripts.md`+`daily-report-format-prefs.md`，顶部钉死输出路径=KB `每日日报\{date}.txt`+`_latest.txt`、首行须含今日日期；② `daily_report_scan.ps1` 加路径漂移保险：闸门没过但 home 有今日 `工作日报_{today}.txt` 就自动搬到 KB 救活。
- **通用教训**：调度任务 cwd 决定 `claude -p` 加载哪个项目 memory；System32 cwd 的任务（DailyReport/BugScan）吃 `C--Windows-System32` memory，别以为是 linkang 的。改这类任务行为先看它的 cwd→对应 memory 目录。

## 🔁 晨报/日报合并升级：晨报改跨项目任务规划版 + 工作line 回写强化（2026-07-08）

- **背景**：工作line.md 三/五节自 06-24 起断档半个月没自动刷新。两个根因：① 21:00 prompt 把回写(6b)排在"预算护栏"之后，预算紧就被跳过；② "今日无变化就不动文件"被宽松判定——日期自然推进（倒排表过期）没被当成变化。07-07 的 API 断连只是叠加事故。
- **改法（已落地）**：
  - `daily_plan_prompt.txt`（10:00 晨报）**重写（07-08 当天用户二次收敛为极简两节版）**：只输出 ①Deadline 倒排表(14天内·算剩N天) ②"今天可以做"清单(≤6条·必做在前)。不拆细、无 top-3/挂起/X2周期等独立节；Jira 全项目查询保留但只当输入不单独成节。数据源=工作line 五节；开头带"工作line 超 3 天没更新就顶部报警"自检；首行闸门格式 `# 今日工作简报 {today}` 未动。
  - `daily_report_prompt.txt`（21:00 日报）6b 回写强化：明确回写=第二优先级不许因预算跳过；"无变化"须过三关（无过期日期/无实际推进/无新决定）才成立，**日期自然推进本身就是变化**；动了文件必须同步改「最后更新」为今天。6b(1) 改成固定节【今日 timeline 完成情况】：逐条对照当天早上 `_daily_plan.txt` 的"今天可以做"清单标 ✅/🔄/❌(没动的写滚明天)，简报缺失则对照工作line 五节今天到期项，全节≤8行。
- **验证口径**：次日早看 `_daily_plan.txt` 是否新格式；晚看工作line「最后更新」是否=当天。工作line 内容 2026-07-08 已手动刷新到位（世界杯R16收尾/深海节运营期），回写从当晚起接手。
- **工作line 可视化（2026-07-08 同日加）**：`KB\工作计划\工作line_tree.json`（层级数据：主工作流→分支→每件事）+ `_render_workline_html.py`（渲染器）→ `工作line_可视化.html`（可折叠甘特，本地直开）。21:00 日报 prompt 6b(3) 会在工作line 有变化时同步 json+重渲（fail-open）。手动刷新=改 json 后跑一次渲染器。status 枚举：done/active/critical/pending/external/auto/paused。

## ⚠️ DailyReport 新鲜度闸门被 10:00 早版打穿（2026-07-08 修）

- **现象**：07-07 21:00 claude -p 第 1 次就 API 断连（exit 1, `Connection closed mid-response`），但 3 次重试一次没触发——直接判失败收场，当天只剩 10:00 早版（半天内容），HTML 没刷新、没弹窗。
- **根因**：自从加了工作日 10:00 早版（也写 `_latest.txt`，首行含当日日期），21:00 的新鲜度闸门"首行含今日日期"**在跑之前就恒为真**——闸门形同虚设：失败被误判 fresh 跳出重试循环，最终又因 exit≠0 判失败，重试机制整个失效。
- **修法（已落地）**：① 闸门加 mtime 校验——`_latest.txt` 必须在**本次尝试开始之后**被写过才算 fresh；② 最终成功判据从 `exit 0 且 fresh` 改成只看 fresh（claude -p 退出码不可靠，写完盘才断连不该白扔）。备份 `daily_report_scan.ps1.bak.20260708`。
- **通用教训**：新鲜度闸门若只查"内容像今天的"，任何**同日更早的写入方**（早版/别的任务）都会打穿它；正确判据 = 内容新鲜 **且** 本次运行期间写的（mtime > 尝试起点）。DailyPlan 等同架构链路如加早版也要照搬。
- 07-07 当天日报已于 07-08 手工补齐全天版（`每日日报\2026-07-07.txt` 重写 + 2026-07-07.html）。

## ⚠️ 调度脚本 `claude -p` 不带 `--model` 会漂移到停服模型（2026-06-15 DailyPlan 中招）

- **现象**：06-13 DailyPlan exit 1，报 `There's an issue with the selected model (claude-fable-5). It may not exist or you may not have access to it.`
- **根因**：脚本 `claude -p` **没指定 `--model`**，吃到 CLI 默认 model。本机默认漂到 `claude-fable-5`（已停服，本账号无权限，`.claude.json` 里残留 `claude-fable-5[1m]` 状态）→ 直接挂。注：settings.json 里 model 虽是 `opus[1m]`，但 `-p` 默认仍可能漂。
- **修法（已落地，可复用到任何 claude -p 调度脚本）**：命令行**显式写死 `--model sonnet5`**（日报/巡检这类轻结构化任务 sonnet5 够用、肯定有权限、还省钱），别依赖默认 model。
- 同次把 DailyPlan 预算 `--max-budget-usd 5` → `8`（与 DailyReport 对齐），解决并存的「exit 0 但未刷新(预算耗尽没写盘)」。备份 `daily_plan_scan.ps1.bak.20260615`。
- 🚫 **这些调度脚本绝不能加 `-NoProfile`**：脚本里的 `claude`/`ccr` 命令是 `C:\Users\linkang\Documents\WindowsPowerShell\profile.ps1` 里定义的函数（`function claude { & "...\claude.cmd" @args }`），加 `-NoProfile` 会让 `& claude` 直接找不到命令。任务 Action 当前是 `powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ...`，保持不动。
- ❓ **未解**：2026-06-15 手动 `Start-ScheduledTask` 触发时，powershell 进程卡在脚本启动阶段(连第8行"开始生成"日志都没写、无 claude 子进程)，挂 11 分钟后被手杀。profile 已排除(仅两行函数、不联网)，根因未定。可能是手动触发的偶发态。验证修复优先让次日 10:00 自动任务跑，别反复手动触发硬怼。
