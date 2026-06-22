# 深海节 · 传说铭牌「航者徽记」— 配置备份表

> KB 配置备份表（一个功能一个文件夹），非 live tsv。复用换皮，**无需程序**（纯配置 + 美术 + i18n）。
> **复用源**：104 世界之巅（世界杯榜单铭牌，传说·无 BUFF·榜单获取）—— 跟本铭牌同款（传说品质 / 无属性 / 排行榜投放）。
> **归属**：01 深海罗盘 排行榜 Top 段投放（解 `01转盘` README 待确认④）。

## 这个是什么
玩家头衔铭牌（PlayerTitle 表），纯外显。**无属性**（用户定调：铭牌不带 BUFF，PositionBuff 留空，同 104）。重复获取按天转钻补偿（Reimburse 100|1000，复用）。

## 表清单
| 表 | 新增 | 文件 | 模板 |
|---|---|---|---|
| `PlayerTitle__PlayerTitle.tsv` | **105**（max104+1） | `PlayerTitle_新增105.tsv` | 104 世界之巅 |
| `i18n/Text__Text.tsv` | `TXT_PlayerTitle_Name_105` + `TXT_PlayerTitle_ObtainDesc_105` | `Text_新增105_i18n.tsv` | 104 的两条 key |

## 字段值（105 航者徽记）
| 字段 | 值 | 说明 |
|---|---|---|
| ID | **105** | max(104)+1 |
| Name | 航者徽记 | 字面中文，i18n 扫描自动生成 `TXT_PlayerTitle_Name_105` |
| DK_Icon | `DK_deepsea_icon_title` | 头衔标志大图 **752×192**（⚠️待 Unity 入库，对应美术 `传说铭牌_航者徽记_头衔标志_752x192.png`） |
| PositionBuff | （空） | **无属性**（同 104） |
| Reimburse | 100\|1000 | 重复获取转钻：单日 100 / 上限 1000（复用） |
| ObtainDesc | 深海罗盘排行榜顶端获取 | i18n → `TXT_PlayerTitle_ObtainDesc_105` |
| DK_SmallIcon | `DK_icon_global_deepseatitle` | 小图标 **256×256**（⚠️待入库，对应 `传说铭牌_航者徽记_小图标_256x256.png`） |
| Quality | **3** | 橙/传说 |
| Order | 5 | max(4)+1 |

## i18n（16 语言已译完，见 `Text_新增105_i18n.tsv`）
- `TXT_PlayerTitle_Name_105` = 航者徽记 / Voyager's Crest / …（cn en sp fr id de kr zh ru ua jp it pl po tr th 全 16 列已填）
- `TXT_PlayerTitle_ObtainDesc_105` = 深海罗盘排行榜顶端获取 / Obtained by ranking in the top tier of the Deep Sea Compass leaderboard. / …
- 列序（对齐 Text 表）：col3 cn / 4 en / 5 sp / 6 fr / 7 id / 8 de / 9 kr / 10 zh繁 / 11 ru / 12 ua / 13 jp / 14 it / 15 pl / 16 po / 17 tr / 18 th。

## 美术（本批已出 / 待挑定）
- 头衔标志大图 752×192 + 小图标 256×256，深海传说主题（锚+罗盘+浪花徽章·金+蓝），reskin 海皇铭牌保框型，透明底。
- 落地于 `KB\产出-本地化与美术\X3\深海节\01_深海罗盘_转盘抽奖+排行榜\传说铭牌_航者徽记_*.png`。
- **DK 入库待做**：选定版 → Unity 录 `DK_deepsea_icon_title`（大）+ `DK_icon_global_deepseatitle`（小）→ push client。

## 落地顺序
美术挑定 → 透明化+裁到 752×192 / 256×256 → DK 入库（2 个）→ PlayerTitle 插 105 行 → Text 插 2 条 i18n → xlsx+tsv 一致过 gate → commit → 导表。
**配置先走本备份，分支处理好后与深海节其余模块一起合并**（按用户要求）。

## ⚠️ 待确认 / 待补
1. 铭牌名「航者徽记」/ Obtain「深海罗盘排行榜顶端获取」措辞 → 待用户确认（可改）。
2. DK 大小图标命名暂定 `DK_deepsea_icon_title` / `DK_icon_global_deepseatitle`，入库时定最终 png 名。
3. 排行榜投放档位（Top 几名给）→ 跟 01 转盘 RankCfg186 一起定（01README 待确认②④）。
4. 史诗铭牌·航徽（02 BP）本次**未做**（用户只要 1 个）。

_生成 2026-06-22；分支后续与深海节一起合并。结构复用 104 世界之巅，无程序，美术+i18n 已备齐。_
