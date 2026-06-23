# X3 活动 HUD 入口图标参考库

> 2026-06-23 建。汇总 X3 现有所有活动 HUD 入口图标（节日活动列表里每个活动的小图标），给换皮/新活动出图挑参考用。
> **规格**：124×136、RGBA 透明底、自由形状主题物件（**图里不画圆框**，外圈圆是 UI 层 `UIActivityListItem.mIconBgImage` 通用底自动套）。出图走高分辨率(1024)再缩 124×136。详见 [[reference_x3_client_resources]]。
> **位置**：`C:\x3-project\client\Assets\Res\UI\Spirits\ActivityImg\`（少量在 `ActivityImg_Download\` / `Activity\`）。命名 `img_Activity_{主题}_icon_{N}.png`。
> **DK**：`DK_img_Activity_{主题}_icon_{N}` → 注册 `Path_Activity.asset` + `Display_Activity.asset`（**必双补**，否则 Ctrl+T「生成dk」清，见 e255 事故 [[reference_x3_client_resources]]）。

## 按节日分组（每套≈该节日全活动的入口图）
| 节日 | 前缀 | 数量 | 节日 | 前缀 | 数量 |
|---|---|---|---|---|---|
| 周年庆 | anniversary | 13 | 元旦 | NewYear | 7 |
| **尼罗(埃及)** | **Egypt** | **12** | 美人鱼 | mermaid | 7 |
| **情人节** | **VD** | **10** | 冰雪 | ice / ice_Christmas | 6+7 |
| **春节** | **CNY** | 9 | 鲸鱼 | whale | 6 |
| 美食节 | MF | 8 | 感恩节 | Thanksgiving | 6 |
| 龙节 | dragon | 8 | 独立日 | Independence | 6 |
| 酿酒节 | winemaking | 7 | 万圣节 | halloween | 7 |
| **夏日恋语** | **summer** | 7 | 通用(无主题) | img_Activity_icon_{N} | ~50 |

## 按「活动类型」直接对得上的图标（换皮首选参考）
| 活动类型 | 现有图标 | 说明 |
|---|---|---|
| 许愿池 | `img_Activity_icon_wishingfountain` | 许愿池专用·直接参考 |
| 海航/大富翁(海) | `img_Activity_navigation_icon_1/2/3` | 航海之路·**最贴深海** |
| 大富翁 | `img_Activity_icon_Monopoly_6` | 程序大富翁现用通用 |
| 兑换 | `img_Activity_icon_Heroexchange_1/2` | 英雄兑换 |
| 拼图(BINGO) | `img_Activity_CNY_icon_4`/`Egypt_icon_8` 等 | 拼图块+节日纹饰(见 [[12_拼图BINGO]] 清单) |

## 深海节 HUD 现状（2026-06-23）
- **已入库**：`img_Activity_deepsea_hud_icon`（转盘）、`img_Activity_deepsea_icon_decor`（装饰）。
- **还缺（Unity 报 displayKey not found·美术待出+入库）**：兑换/酒馆/拜访/许愿池/红包 的 deepsea HUD icon + 大富翁 `icon_Monopoly_deepsea`、珍珠贝道具 `icon_Monopoly_pearl`（大富翁那几个归美术 agent）。
- ⚠️转盘还有配置/客户端引用旧名 `deepsea_turntable_icon`（未入库）但实际入库的是 `deepsea_hud_icon`→要么出图、要么改引用指向已入库的。

## ★尼罗(Egypt)全套分类 = 深海各活动 HUD reskin 源对照（权威·交叉ActvOnline.col21查得）
**总入口图标**（节日主按钮·ActvGroup 132「尼罗之辉：王后盛典」col4）= `Egypt_icon_7`（与转盘共用）。
**各活动图标**（ActvOnline.ActvIcon col21）：
| Egypt 图标 | 尼罗活动 | ActvType | → 深海对应活动(reskin源) |
|---|---|---|---|
| `Egypt_icon_1` | 累充 黄金沙漏 | 5 | 深海累充 |
| `Egypt_icon_2` | 酒馆 蓝莲花宴 | 7 | 深海酒馆 |
| `Egypt_icon_3` | BP 圣甲虫试炼 | 22 | 深海远航日志(BP) |
| `Egypt_icon_4` | 兑换 方尖碑集市 | 13 | 深海宝藏集市(兑换) |
| `Egypt_icon_6` | 许愿池 | 50 | 深海许愿池 |
| `Egypt_icon_7` | 转盘 黄金卷轴(+总入口) | 10 | 深海转盘(已有 deepsea_hud_icon) |
| `Egypt_icon_8` | 拼图 象形密文 | 18 | 深海拼图(BINGO) |
| `Egypt_icon_11` | 拜访 金字塔之城 | 56 | 海滨之约(拜访) |
| `Egypt_icon_9` | 返场商店兑换 | 13 | （深海无） |
| `Egypt_icon_5/10/12` | 未在 ActvOnline 引用（装饰/头像框/红包 或闲置）| - | - |

## ★深海 HUD 批量生成(2026-06-23·9候选已出待挑)
- **9张候选已出**(每张2 cand·`KB\产出-本地化与美术\X3\深海节\_HUD图标\`·九宫格预览`_九宫格预览_cand0.png`):兑换/酒馆/转盘/拜访/许愿池/大富翁icon_Monopoly_deepsea/红包icon_redpack/珍珠贝道具icon_Monopoly_pearl/许愿池水池wishingpool_pool。
- **生成范式(可复用·脚本`scratchpad/gen_deepsea_hud.py`)**:GRFal gpt + **对应尼罗Egypt图当reference**(见上对照表) + prompt="game activity icon, single isolated object on plain bg, no text/border/UI frame, RESKIN reference的motif成深海主题(ocean blue+gold+pearl/coral/shell)"·1:1出→后续抠白+裁124×136(珍珠贝道具256)。
- **待办**:用户挑cand→抠白透明(`flood_remove_white_bg.py`·白高光主体改洋红幕色键)→裁124×136→入库Path_Activity+**Display_Activity双补**(防Ctrl+T·见[[reference_x3_client_resources]])。

## 换皮建议
深海活动阵容（转盘/兑换/酒馆/拜访/许愿池）≈ **尼罗 Egypt(12最全) / 夏日 summer / 情人节 VD** 的阵容 → **拿这三套之一当 reskin 源**逐个对最省事；海主题叠 `navigation_icon` 的海航元素。本目录 `参考_*` 子图 = 拷出来的几张类型参考。
