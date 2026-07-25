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
| `parse_nuxt.js` | node 解析 fifaaddict SSR 页 `window.__NUXT__` → JSON（需先抓 `elpages/*.html`，抓法见 memory `reference_fifaaddict_fcol_scrape.md`） |
| `gen_report.py` | 报告 HTML 生成器（v1 基础版；v2-v4 的社区验证/实战专区/实战操作建议章节是后续 python 补丁直接改 HTML 追加的，**重跑 gen_report.py 会回退到 v1，勿重跑**） |

换赛季复用：改 `class=el` 为其他赛季代号（fo4info API 的 seasons 字典）→ 重抓列表和球员页 → 重跑 parse+score。抓取全链路（握手 API、SSR、搜狗微信、抖音评论区）唯一入口 = memory `reference_fifaaddict_fcol_scrape.md`。
