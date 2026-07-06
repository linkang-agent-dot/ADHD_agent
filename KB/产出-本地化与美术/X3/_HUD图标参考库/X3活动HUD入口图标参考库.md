---
tags: [kind/产出, domain/美术媒体, proj/X3, year/2026]
---

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

## ★HUD图标造型=参考同类型活动·不强求圆框(2026-06-23用户纠正)
**别把所有HUD都做成圆形徽章**——不同活动类型有各自造型惯例,**出图前先拉同类型(同ActvType)现有图标看造型**(本目录`_类型参考_累充BP.png`):
- **累充(type5)**=主题物件:尼罗黄金沙漏=**宝箱+沙漏**(`Egypt_icon_1`)·非圆框。
- **BP(type22)**=物件+小爆闪底:圣甲虫(`Egypt_icon_3`)/航海**旅程记录册=罗盘**(`navigation_icon_3`·最贴深海远航日志)/情人节=**戒指盒**(`VD_icon_2`)。
- 先前9张都做圆徽章=偏了;累充/BP已改物件造型重出。

## ★累充/BP HUD 进度(2026-06-23)
- **图标已出+抠透明+入库双补**:`deepsea_fund_icon`(累充·宝箱沙漏)/`deepsea_bp_icon`(BP·金罗盘)·124×136·Path_Activity+Display_Activity双补·bg已入库(deepsea_fund_bg/bp_bg)。
- **gdconfig改指**:AO100598 ActvIcon→deepsea_fund_icon / AO102244→deepsea_bp_icon(原deepsea_hud_icon占位·未提交)。
- **⚠️commit落错分支**:client我的累充/BP DK commit `7aebdf` **误落 dev_festival**(被另一agent切了工作目录分支·违反"深海只走feature/x3-deepsea-art"规则)→**待cherry-pick到feature/x3-deepsea-art再push**;数据没丢(commit在dev_festival)。
- **★踩坑(回写)**:多agent共享client仓·**别人会切你的工作目录分支**→提交前必`git branch --show-current`确认;落错branch=cherry-pick到对分支别在脏并发分支上做手术。

## ★活动 Banner(ActvImg)格式规范(2026-06-24用户纠正·可复用)
活动背景图(ActvImg)**不是满幅场景**——标准 = **540×500 RGBA·单主题物件居中偏上 + 大气背景 + 下半~40%/四边渐隐透明**(透出下方活动面板)。锚:`img_Activity_bbq_bg_3`/`summer_bg_3`/`VD_bg_14`(都540×500·下半不透明~64-71%·物件聚焦留白)。**误区**:做成满幅不透明场景(铺到底·硬边方块)=糊/方/不聚焦(深海初版踩此坑)。
- **拜访礼包(ActvVisitPack.DK_PackIcon)** = **368×260**·门头建筑居中 + 简洁底 + 橙banner ribbon(参考VD誓言之门`VD_bg_14`)·别堆杂乱岛基/珊瑚/道具(深海初版下半太花踩坑)。
- **出图法(可复用)**:GRFal gpt banner模板="single deep-sea focal object in UPPER-CENTER + atmospheric bg + LOWER 40%/edges fade to airy emptiness/vignette, NOT edge-to-edge scene"(用现有bg当reference保色调)→后处理:resize 540×500 + alpha mask(opaque顶~50%·行0.5H→0.88H线性到0·边缘50px渐隐)。脚本`scratchpad/gen_banner_redo.py`+处理逻辑。
- **★深海bg最终入库(2026-06-24·dev_festival commit f18094c)·分两类别一刀切**:
  - **透明banner型(5张·540×500 RGBA下半透明)**=兑换/酒馆/BP/累充/许愿池(exchange/tavern/bp/fund/wishpool)。这类ActvImg是「物件居中+下半透出活动面板」的banner。
  - **全屏背景型(2张·540×960 RGB不透明)**=转盘(turntable·AO101025·对齐尼罗Egypt_bg_10)+拜访(visit_bg)。这类是9:16满幅活动背景,**绝不做透明**(用户两轮纠:"转盘/拜访之前就不是透明的版本·还原")。
  - **visit_pack(368×260 RGB)**=拜访礼包小图(ActvVisitPack 5606 DK_礼包图标)·**用户明确不用改·保原图**(还原到61e7e1c)。
  - ⚠️**踩坑(回写·别再犯)**:① 我一度把7张全统一成540×500透明=**错**,转盘/拜访是全屏背景型不能透明→还原到改动前版本(git checkout <旧commit> -- <file>)。② 透明蒙版剖面照bbq/queen参考:**上0-68%完全实心alpha=255(填满!)+68-85%急速线性渐隐+85%以下全透**;别从中部就开始淡(=太透·上方没填满,初版踩此)。③ visit_bg(大背景540×960)≠visit_pack(礼包小图368×260),门头观感问题改大背景,小图别动。
  - 最终透明banner留`KB\...\深海节\_banner_重出\_最终\`(预览`_预览_重做蒙版.png`)。同名覆盖·DK/Path注册已在不动。
- **★代码证实的渲染机制(2026-06-24查尼罗转盘101023配置+代码)**:ActvOnline 字段名行=line 101,**col22=ActvIcon(HUD入口小图)·col23=ActvImg(背景)·col24=ActvPrefab(可选Spine角色)·col25=Hero**(数列号别off-by-one)。客户端 `UIHelper.Activity.cs:246-248` = `SetImageWithDisplayKey(bgImage, cfg.ActvImg)` → **ActvImg 直接贴全屏 bgImage 层**(满铺·不做透明·非banner槽)。
  - **全屏背景型活动(转盘ActvType10/拜访)**:ActvImg=540×960满幅不透明(尼罗`Egypt_bg_10`540×960 RGB实证)。尼罗在bg上**再叠ActvPrefab Spine角色**(`DK_Role_Spine_23_Skin01`猫女仆)当主视觉;**深海无角色(ActvPrefab空·定调"背景不出现人物")→这张540×960 bg要自己撑全画面主视觉**(潜艇+祭坛场景)。这是它不能做"物件居中+下半透明"banner的根因(banner靠下半透出活动面板,全屏背景是满铺底图)。
  - 判别新活动该用哪种:看复用源同类活动的ActvImg实际尺寸/透明度(540×960不透=全屏背景型/540×500下半透=banner型),别一刀切。
- **★转盘(ActvType10/LuckyWheel)有「三层背景」·别只看ActvImg(2026-06-24查代码+假透明事故)**:转盘界面背景**不走ActvOnline.ActvImg**(那是外层活动框背景)，盘面/指针/界面底图走**另一张表 `ActvLuckyWheel`**(`UIActvLuckyWheel.cs:133-135` SetImageWithDisplayKey)：
  | ActvLuckyWheel列 | 字段 | 作用 | 透明要求 |
  |---|---|---|---|
  | col14 | `DK_Turntable` | 盘面(转盘圆盘) | 透明(圆盘外) |
  | col15 | `DK_TurntablePointer` | 指针 | 透明 |
  | col16 | **`DK_BG`(底部背景图)** | 转盘下方界面底图(~1080×984) | **上半透明渐隐+下半石台不透明** |
  - ⚠️**假透明事故(回写·珍贵)**:深海`DK_BG`=`deepsea_bg_wheel`顶部40%被AI/导出做成**白色不透明(alpha=255+RGB白)**而非透明→在转盘下方**盖住下层underwater背景=界面中段一条白带**(用户报"转盘下半空荡")。这是典型假透明([[feedback_transparent_asset_diff_check]])——单看缩略图像有渐变，实则顶部是实心白。**验真=查alpha逐行**(对标尼罗`Egypt_bg_11`:上25%alpha=0真透明/中段渐入/底部255)。**修=顶部白区alpha改0**;浅灰区只能全透(半透明的浅灰仍显灰雾·尼罗能渐隐是因其内容极暗能融背景)；二值阈值`sat>45`保珊瑚/金框、下半石台强制opaque。
  - **换皮转盘必查这3个DK是否都真透明**，尤其`DK_BG`顶部别baked白。
- **★拜访(ActvType56/VisitPack)bg范式=「门头浮岛+干净底板」(2026-06-24查代码+夏日/尼罗范式)**:界面主背景=`ActvOnline.ActvImg`(`UIActvVisitPack.cs:115` SetActivityBaseInfo→mTFWImageBG)，**无独立底板DK**;礼包图走`ActvVisitPack.DKPackIcon`(→mTFWImagePackRewardBg·368×260小图)。**bg标准构图(夏日`VD_bg_13`/尼罗`Egypt_bg_7`最清晰)=上~40%「被拜访的门头建筑」浮在小岛上(框景foliage在顶角)+下~60%干净空渐变底板(UI奖励/按钮坐这块·别堆杂乱场景)**。各节日:尼罗=金字塔城(Egypt_bg_7)/夏日=红顶小屋(VD_bg_13)/春节=新春典藏(CNY_bg_12)/深海=海滨假日热带小屋(deepsea_visit_bg)。⚠️深海初版下半铺成杂乱海洋底=错(没留干净底板),重出对齐范式即可。这跟全屏背景型(转盘满铺)不同:拜访下半要**空/干净**给UI,但底板是**不透明渐变**(非透明banner)。

## 换皮建议
深海活动阵容（转盘/兑换/酒馆/拜访/许愿池）≈ **尼罗 Egypt(12最全) / 夏日 summer / 情人节 VD** 的阵容 → **拿这三套之一当 reskin 源**逐个对最省事；海主题叠 `navigation_icon` 的海航元素。本目录 `参考_*` 子图 = 拷出来的几张类型参考。
