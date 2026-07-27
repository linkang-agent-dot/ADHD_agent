# _data 接管说明

`传奇永恒EL_66人性价比全解_20260724.html`（上级目录，**FINAL·v6**：v1数据榜 → v2社区验证 → v3实战党 → v4实战操作 → v5五源交叉评级 → v6瓦坎达45人全评级）的数据与生成脚本。配套终表：上级目录 `瓦坎达永恒评述三期_评级全表_20260725.md`（六五神/分档/避雷/溢价/永恒vs时刻/跨源冲突点）。

| 文件 | 用途 |
|---|---|
| `el_list.json` | fifaaddict API 拉的 EL 赛季 66 人列表（含 uid，2026-07-24） |
| `el_stats.json` | 66 个球员 SSR 页解析出的全量数据（六维/分位置OVR/逆足/体型/特性/薪资） |
| `el_scored.json` | 加权打分结果（强度分+性价比分），权重与修正规则见 `gen_report.py` |
| `A胖_永恒前锋前腰手感评价_转写_BV1aRm7BxEUt.txt` | B站独立源全文转写（bilibili-transcribe skill 产出），v5⑧章节的评级依据 |
| `瓦坎达_永恒评述_上/中/下期_transcript.txt` | 职业选手瓦坎达抖音直播切片三期全文转写（07-25，共约60分钟逐卡评述45+人），v6 评级依据 |
| `wkd_transcribe.py` | 抖音音频流→faster-whisper 转写脚本（音频直链抓法见 memory `reference_fifaaddict_fcol_scrape.md` 抖音段） |
| `tm_list.json` | ICON TM(时刻)100人列表（07-26），永恒vs时刻基础OVR对比（全表附2）数据源 |
| `el_tm_attrs.json` | 12名同名球员 永恒/时刻 两版34项小属性+特性+体重全量（07-27，fo4pid接口逐会话抓），全表附3-5数据源；⚠️该接口每会话限~2次查询且**总评为裸值=游戏内−3** |
| `gen_decision_page.py` | 「换代决策页」生成器（①ID印象②刀刃属性③结论三段式）⚠️其5卡口径版含球员等级误读，参考用 |
| `el_tm_attrs_full.json` | **全量终版数据：66名EL全部+47名同名TM的34项细项/特性/体重**（07-27，89次抓取零失败） |
| `fetch_all_attrs.py` | 批量抓取器（断点续传+会话轮换限流，每会话2次+退避） |
| `gen_all_players_page.py` | **66人拉通页生成器（FINAL）**：有TM=6卡vs8卡对比、无TM=6卡直列；LV常数待确证后改一行重跑 |
| `gen_full_attrs_page.py` | **29项全量对照页生成器（FINAL口径：永恒6卡vs时刻8卡+球员等级5+队套6，无预筛无观点）**——球员等级加成LV=4为假设值，用户给确值后改常数重跑 |
| `parse_nuxt.js` | node 解析 fifaaddict SSR 页 `window.__NUXT__` → JSON（需先抓 `elpages/*.html`，抓法见 memory `reference_fifaaddict_fcol_scrape.md`） |
| `gen_st_final.py` | **中锋模型定稿页生成器（07-27 用户逐档裁定版）**：档位制(145/155/165=1/2/3)×五档权重+特训背包(+5点单项≤2)+逆足系数(5/4/3逆=1.0/0.95/0.85)，全员66人算中锋分≥80进榜+身材参考列+45条评语 → `永恒中锋评价_定稿版_20260727.html`。**过边锋/其他位置=复制此骨架只改权重表+逆足系数** |
| `gen_report.py` | 报告 HTML 生成器（v1 基础版；v2-v4 的社区验证/实战专区/实战操作建议章节是后续 python 补丁直接改 HTML 追加的，**重跑 gen_report.py 会回退到 v1，勿重跑**） |

换赛季复用：改 `class=el` 为其他赛季代号（fo4info API 的 seasons 字典）→ 重抓列表和球员页 → 重跑 parse+score。抓取全链路（握手 API、SSR、搜狗微信、抖音评论区）唯一入口 = memory `reference_fifaaddict_fcol_scrape.md`。
