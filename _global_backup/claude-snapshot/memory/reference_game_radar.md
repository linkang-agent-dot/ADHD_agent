---
name: reference_game_radar
description: 策略游戏雷达——每天抓中/美/日热门+飙升策略游戏出 HTML 的个人监控工具；改数据源/榜单/频率/调度时间，或排查它不出图时先读
metadata: 
  node_type: memory
  type: reference
  originSessionId: db146b9a-fa92-46f8-b533-36a4295b2cfd
---

个人工具：每天抓三国（中/美/日）热门+飙升策略游戏，出一张自包含 HTML 供用户挑游戏体验。计划任务 `GameRadar-Daily` 每天 09:00 跑 + 弹浏览器（见 [[reference_background_scheduled_tasks]]）。

## 位置
- 根目录 `C:\Users\linkang\game-radar\`
  - `scripts\build_report.py` — 主程序（抓取+排名变化+渲染，全在这一个文件，**改配置改这里**）
  - `scripts\gplay_fetch.mjs` — Google Play 取数（Node，**必须 .mjs**，ESM `import gplay from 'google-play-scraper'`；`scripts\node_modules` 已装 v10.x）
  - `data\previous.json` — 昨日榜单快照（算 ▲▼/NEW 用，每次跑后覆盖）；`data\run.log` — 调度日志
  - `output\latest.html`（稳定入口）+ `output\radar_YYYY-MM-DD.html`（每日存档）
  - `run_daily.ps1` — 调度入口（写死 `C:\Python314\python.exe`，末尾 `Start-Process latest.html` 自动弹，不想弹删这行）

## 数据源现状 + 各自的坑（关键）
| 源 | 取法 | 覆盖 | 坑 |
|---|---|---|---|
| Apple App Store | iTunes RSS `itunes.apple.com/{cc}/rss/{kind}/limit=25/genre=7017/json` | 中/美/日 × 免费/畅销/付费 | **genre=7017=策略**；无 key 全通；中文乱码只是终端显示，文件本身 UTF-8 正常 |
| Google Play | `gplay.list({category:GAME_STRATEGY,collection,country,lang})` 经 .mjs | 美/日 × 免费/畅销 | **中国无 GP**→CN 给 TapTap 手动链接补 Android；新版 scraper 是 ESM，CommonJS `require` 会挂 |
| YouTube | `python -m yt_dlp --dump-json --flat-playlist "ytsearchN:<query>"`，按播放量排序 | 各国分别用 zh/en/ja query | **无需 API key**（这是关键，省了申请 key）；flat-playlist 没有上传日期，只按播放量排 |
| Reddit | `old.reddit.com/r/{sub}/top.json?t=week` + Chrome UA | 全球(英文社区) | 本沙箱 IP 被 **403 限流**；失败自动降级成可点的子版块链接卡片。用户本机 IP 跑大概率能通 |
| TapTap | 仅给链接 `taptap.cn/top/download` | 中国 Android | API 需 X-UA 签名，没逆向；中国 iOS 已被 Apple CN 覆盖，价值不大故只给链接 |

## 飙升/新游算法
free 榜对比 `previous.json`：去年排名-今年排名≥3=▲；昨日不在榜今日在=NEW。**第一天没有对比基准，飙升区为空属正常**，跑满一天后才有。

## 推荐引擎（两段式：打分粗筛 → LLM 按工作画像精排，「🎯 今天推荐」首屏 tab）
**核心诉求**（用户2026-06-23明确）：不是粗糙看排名，要「读懂游戏+最近版本更新+扣到他做重度SLG设计能不能用」。

### 第一段 粗筛 scripts\recommend.py（`build_recommendations` 返回全部打分候选，不再切TOP/不写history）
- 偏发现打分：NEW +25 / 飙升 delta×1.3(封顶40) / 榜内基础分 / 多区每多1区+12 / 双平台+10 / 畅销榜+10 / 免费榜Top5+6 / YouTube命中+8~16 / TASTE_BOOST+8。
- 冷却 `COOLDOWN_DAYS=3` ×0.45（`data\recommend_history.json`）。
- 每条候选带回 `apple_id/apple_cc/gplay_id/gplay_cc`（供第二段抓详情）。
- `finalize_fallback()` = LLM 不可用时的降级出口（纯打分+stars）。

### 第二段 精排 scripts\analyze.py（默认主路径，2026-07-02 起主后端=Claude）
- build_report 取打分前 `N_ANALYZE=18` 候选 → `enrich()` 抓每个的**简介+最近版本更新说明**（Apple `lookup?id=&country=` 给 releaseNotes/version/date/genres；GP detail 给 recentChanges，扩了 gplay_fetch.mjs 的 `type:'detail'` job）→ `analyze_llm()` **一次** LLM 调用，传**工作画像** `config\work_profile.md` + 候选 JSON，返回每游戏 {relevance 0-100, verdict 必看/可看/跳过, what_it_is, recent_update, why_relevant(扣付费/活动/养成/数值/排行/留存), what_to_study}。
- build_report 取 verdict≠跳过 前 `N_SHOW=9` 展示，写 history。
- **工作画像可编辑**：`config\work_profile.md`（SLG系统数值+节日活动+变现live-ops；想改推荐口味改这个文件，不用动代码）。
- **降级链 fail-open**：Claude CLI → Gemini API → 纯打分（HTML 顶部挂⚠️提示）。报告永远出得来。

### 主后端 Claude CLI（无头，走订阅不用 API key）
- `analyze_with_claude()`：subprocess 调 `%APPDATA%\npm\claude.cmd -p --output-format text --model sonnet --settings '{"hooks":{"Stop":[]}}'`，prompt 走 stdin，timeout 600s，2 轮重试。
- ⚠️**Stop hook 污染坑（已踩）**：无头 `-p` 模式下用户的 Stop hook（pending_verify_gate 收工自检）会追加一轮，最终输出变成自检回复而不是 JSON → 必须 `--settings '{"hooks":{"Stop":[]}}'` 关掉。任何本机无头 claude 调用都适用此坑。
- 副作用（加分项）：无头 claude 会加载 CLAUDE.md/memory，分析能结合用户自己的项目经验做对标。
- 解析容错：`_parse_and_merge` 会从杂散文字里正则抠 `[...]` 数组。

### ⚠️ Gemini 免费层坑（现为备胎，坑仍在）
- `gemini-2.5-pro` 免费层 `limit:0` 根本不可用 → 模型列表只留 `["gemini-2.5-flash","gemini-2.0-flash"]`。
- 免费层有**每分钟**请求/token 限额：反复手测会 429（生产一天1次不会触）；3 轮重试 + 退避 `[0,25,55]s` 跨过分钟窗口。
- `GEMINI_API_KEY` 在 User 级环境变量，计划任务能读到。

### 首日现象
无昨日基线时飙升/新进信号为0，但**第二段 LLM 仍按工作画像精排**，所以即使首日也是「按对你工作的参考价值」排序，不是单纯榜单。第二天起飙升信号叠加进粗筛候选池。

### 调参入口
recommend.py 顶部 `TASTE_BOOST/COOLDOWN_DAYS`；build_report.py 顶部 `N_ANALYZE(18)/N_SHOW(9)`；analyze.py 顶部 `CLAUDE_MODEL(sonnet)/CLAUDE_TIMEOUT/GEMINI_MODELS/RETRY_ROUNDS/BACKOFF`；口味改 `config\work_profile.md`。

## 常见改动入口（都在 build_report.py 顶部）
- 加/改国家：`COUNTRIES`（含 yt_queries、是否有 gplay、gplay_lang）
- 改榜单类型：`APPLE_KINDS` / `GPLAY_KINDS`
- 改 Reddit 子版块：`REDDIT_SUBS`
- 改条数：`N_CHART`(25) / `N_YT`(8)
- 改频率/时间：`Set-ScheduledTask`/重注册 `GameRadar-Daily` 的 trigger
- 手动跑：`C:\Python314\python.exe C:\Users\linkang\game-radar\scripts\build_report.py`

## 可接的第二步
榜单冒出热门视频后，可用 `youtube-analyzer` skill（`GEMINI_API_KEY` 已配）深扒某个视频玩法：`python C:\Users\linkang\.agents\skills\youtube-analyzer\scripts\analyze_youtube.py <url> "分析核心玩法"`。
