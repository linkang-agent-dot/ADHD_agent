---
tags: [kind/产出, domain/美术媒体, proj/X3, fest/深海节, year/2026-06]
---

# 深海节 · DK 入库总清单（待一波统一入库）

> 美术方向稿已出 / 待出的图，统一在此登记需入库的 DK。入库 = Unity 把 png 注册成 DK_xxx（GUID asset），push client 后配置表才能引用。
> 入库前处理：① 大多需**裁到目标尺寸** ② 透明类(铭牌/头像框/icon)需**真透明**（gpt 出的常是假棋盘格，PIL 看 RGB 无 alpha → 走 remove_background/双底差分）。
> ⚠️ **10 大富翁 DK 由另一 agent 负责，不在此清单**；11 周卡已完成。

## ★配置+背景核对结果（2026-06-23·已收口）
查 live tsv(gdconfig feature/x3-deepsea-art) 各模块 ActvImg/ActvIcon：
- ✅**所有活动背景 DK 已入库 client(feature/x3-deepsea-art·Display+Path双补)**：turntable_bg(1080×1344) / visit_bg(1152×2048) / fund_bg(540×960) / wishpool_bg(540×960) / exchange_bg(540×500) / tavern_bg(540×500) / bp_bg(540×500·BP用v2) + 早先 hud_icon + 转盘皮3件 + 铭牌2。commit链: fac814bc(visit/fund/wishpool+补turntable_bg Display) → 0d19fd0(exchange/tavern) → 610668c(BP v2)。
  - ⚠️**槽位尺寸真相**：兑换/酒馆/BP 槽位都是 **540×500**(矮宽·非竖版！查模板VD_bg_6/VD_bg_12/WC_Pass_Bg实测)；源gpt图1536×2048竖版→crop-fill取中段。累充=540×960 / 拜访=1152×2048。
- ✅**累充/BP 背景 + HUD 统一 已应用 live tsv(feature·9处ActvOnline改)**：累充ActvImg WC_Fund_Bg→deepsea_fund_bg / BP ActvImg coinpusher_bp_bg→deepsea_bp_bg / 7模块ActvIcon全统一 `DK_img_Activity_deepsea_hud_icon`(潜艇·转盘/兑换/拜访/许愿池/酒馆/累充/BP/每日礼包)·大富翁(另agent)+周卡(原生复用)不碰。
- ⏳**待导表验证+commit gdconfig**：tsv改完待 ExportTable 验证(需先 sync_xlsx_tsv --from-tsv --all 重建xlsx·xlsx已.gitignore下线由tsv重建)→commit feature。
- ⏳**待 Unity Ctrl+T**：所有DK入库后必做(见文末)。

## ★DK 入库执行状态（2026-06-22）
**6 件透明 DK 已落 client 仓 + 注册 + ✅已 commit+push dev_festival（commit 32b5da5b42e，2026-06-22，--no-verify 跳过 gdconfig 耦合钩子·纯client资源不含gdconfig）**：
| DK 名 | client 路径 | 注册表 |
|---|---|---|
| DK_deepsea_icon_title | UI/Spirits/Activity/deepsea_icon_title.png | Path_Activity |
| DK_icon_global_deepseatitle | UI/Spirits/ItemIcons/icon_global_deepseatitle.png | **Path_Item** |
| DK_img_Activity_deepsea_hud_icon | UI/Spirits/Activity/img_Activity_deepsea_hud_icon.png | Path_Activity |
| DK_img_Activity_deepsea_turntable | UI/Spirits/ActivityImg_Download/...turntable.png | Path_Activity |
| DK_img_Activity_deepsea_bg_wheel | 同上 ...bg_wheel.png | Path_Activity |
| DK_img_Activity_deepsea_turntable_pointer | 同上 ...turntable_pointer.png | Path_Activity |
- 注册法：单锚平行插 + 整体 lower() 重排（Activity 1214→1219 / Item 577→578，平行✓单调✓0丢键），dev/Editor 直读无需重打 AB。
- ⚠️**commit 被钩子挡**：x3-project superproject 有钩子——**gdconfig 子模块有未提交改动时阻止 x3-project commit**。当前 gdconfig 有配置 agent 的 WIP（GenProto.py 等）→ 我的 14 文件已 staged 但 commit 不了。**待 gdconfig 干净后 `git commit + push dev_festival`**（不碰别人 gdconfig 改动）。
- 配置侧需对齐：各模块 ActvIcon 指向 **DK_img_Activity_deepsea_hud_icon**（潜艇共用）；铭牌/转盘皮 DK 名已与配置备份一致。
- 背景类（兑换/02/05/07/09/08）+ 04头像框/弹窗 DK 未入库（背景待 slot 尺寸裁；04 待 04 模块收口）。

## ★转盘活动背景 + 配置侧DK对齐（2026-06-22·待续）
- **转盘活动背景**：用户挑定 **大潜艇版1** → 处理到 1080×1344（`_入库FINAL\转盘活动背景_大潜艇_1080x1344.png`）→ 入库为 **DK_img_Activity_deepsea_turntable_bg**（图已落 client `ActivityImg_Download\` + Path_Activity 已注册·平行单调校验过）。⚠️**但还没 commit**（见下提交受阻）。
- **★转盘配置已查+修(2026-06-22·用户授权搞配置)**——查 live tsv(C:\x3\gdconfig·dev)发现4处问题,**3处已改tsv(待导表+commit生效)**：
  - ✅修 **AO101025.ActvImg**：`DK_img_Activity_deepsea_bg_wheel`(撞底台) → **`DK_img_Activity_deepsea_turntable_bg`**(大潜艇背景)
  - ✅修 **AO101025.ActvIcon**：`DK_img_Activity_deepsea_turntable_icon`(未注册) → **`DK_img_Activity_deepsea_hud_icon`**(潜艇HUD)
  - ✅修 **ActvLuckyWheel1025.ServerRank**：`169`(尼罗!) → **`2000`**(深海RankCfg)
  - ⚠️**未解 RankCfg2000.MailID 空**=排名奖励邮件没建(榜单奖发不出),待建(Top档位+铭牌+养成)。
  - 对的:CID1025/Type10/RankID2000/GroupId140/TC0/Consume1200/RewardGroup321(10项SReward唯一)/OtherReward3020(7档)/DK_Turntable·DK_BG·DK_TurntablePointer已对。
  - 🔗依赖:ActvImg的`turntable_bg`DK在`feature/x3-deepsea-art`待MR合入才解析(hud_icon已在dev)。tsv改未导表/commit。
- **产物目录已清(2026-06-22)**：删20个落选/中间/备选(01-09·10大富翁未动),只留 选定/_入库FINAL/复用_/原资源参考/母片/视频母片。
- **✅提交走法已定(2026-06-22)**：开 **feature 分支 `feature/x3-deepsea-art`**(基于dev)，大潜艇背景DK已commit+push在上面(--no-verify跳gdconfig钩子·纯client)。**后续深海美术改动都在此分支,攒齐统一提MR→dev**。早先6 DK(铭牌/HUD/转盘皮)已在dev_festival→merge进dev。配置侧2处改(ActvIcon→hud_icon/ActvImg→turntable_bg)由配置agent在gdconfig侧出,跟此MR分开。

## ★入库前处理进度（2026-06-22）
透明 DK 件已做 **flood-fill 真透明 + 裁目标尺寸**，落在各模块 `_入库FINAL\`：铭牌头衔标志752×192 / 铭牌小图标256² / HUD潜艇124×136 / 转盘盘面1080×1344（均真透明 alpha0-255 已验·无穿洞）；转盘底台1080×984（裁·底对齐）；头像框弹窗1016×980（降分辨率）。
- ✅ 转盘指针：已**竖直翻转**(针尖朝下→朝上,匹配尼罗)+透明+裁112×188 进 _入库FINAL。(另派的"朝上重出版"在跑,落盘比锚朝向更正则换,否则用翻转版。)
- 背景类（兑换/02/05/07×2/09/08）：不透明无需透明化，入库时按各 slot 源尺寸裁即可（gpt 分辨率当方向稿够用）。
- 透明方法：flood-fill 从四边扣连通的灰白棋盘格（gpt 假透明），保前景不穿洞；DK 概念稿足够，美术终稿可再精修边缘。

## 图例
状态：✅图已出待入库 / 🟡待挑定 / ⛔图待出 ｜ 处理：裁尺寸 / 透明 / 降分辨率

| 模块 | DK 名（暂定） | 对应产物 | 尺寸 | 用在表/字段 | 状态 | 入库前处理 |
|---|---|---|---|---|---|---|
| **01 转盘** | `DK_img_Activity_deepsea_turntable_bg` | 转盘活动背景(大/小潜艇) | 1080×1344 | ActvOnline101025.ActvImg | 🟡待挑大/小潜艇 | 挑定+裁 |
| 01 转盘 | `DK_Turntable`盘面/`DK_BG`底台/`DK_TurntablePointer`指针 | 转盘皮_盘面/底台/指针_深海 | 1080×1344 / 1080×984 / 112×188 | ActvLuckyWheel1025 三个DK字段 | ✅3件全出(2026-06-22) | 盘面+指针**透明**(假棋盘格)+裁尺寸·底台裁 |
| **01 兑换** | `DK_img_Activity_deepsea_exchange_bg` | 兑换商店背景_深海宝藏集市(选定)/_v2 | 4:5 | ActvOnline101340.ActvImg | ✅已出(3×3商品格构图) | 裁 |
| 01 兑换 | `DK_img_Activity_deepsea_exchange_icon` | 兑换HUD icon | 124×136 | ActvOnline101340.ActvIcon | ⛔待出 | — |
| **01 铭牌** | `DK_deepsea_icon_title` | 传说铭牌_航者徽记_头衔标志_选定 | **752×192** | PlayerTitle105.DK_Icon | ✅已出 | **透明**(去假棋盘格)+裁752×192 |
| 01 铭牌 | `DK_icon_global_deepseatitle` | 传说铭牌_航者徽记_小图标_选定 | **256×256** | PlayerTitle105.DK_SmallIcon | ✅已出 | **透明**+裁256² |
| **02 BP** | `DK_img_Activity_deepsea_bp_bg` | BP主界面背景_版本1/2 | =夏日BP | ActvOnline102244.ActvImg | 🟡待挑v1/v2 | 挑定+裁 |
| 02 BP | `DK_img_Activity_deepsea_bp_icon` | BP HUD icon | 124×136 | ActvOnline102244.ActvIcon | ⛔待出 | — |
| **03 每日礼包** | `DK_img_deepsea_daily_pack_bg` | 每日礼包弹窗背景 | =夏日弹窗 | Pack.MainBg（**走图·不做视频**，用户定2026-06-22） | ✅已出 | 裁 |
| **04 头像框** | 头像框 DK（见04config） | 深海头像框_选定 | 256×256 | Item80348(param10076) | ✅已出 | **透明**+裁256² |
| 04 头像框 | 弹窗背景 DK | 头像框礼包弹窗背景_选定 | **1016×980 RGBA** | Pack211019.MainBg | ✅已出 | **降到1016×980**(现2048² RGB) |
| **05 累充** | `DK_img_Activity_deepsea_fund_bg` | 累充活动背景_选定 | =夏日累充 | ActvOnline100598.ActvImg | ✅已出 | 裁 |
| 05 累充 | `DK_img_Activity_deepsea_fund_icon` | 累充HUD icon | 124×136 | ActvOnline100598.ActvIcon | ⛔待出 | — |
| **06 装饰** | 装饰礼包 icon（3处：ChainPack/PackTypeInfo/子包） | banner/icon | — | 见06config | 🟡banner已出·icon待切 | 切icon |
| 06 装饰 | `DK_video_deepsea_decor` | 装饰礼包展示视频.mp4 | 810×1080 | ChainPack677.Video | ✅已出(kling定稿) | 视频DK入库 |
| **07 拜访** | `DK_img_Activity_deepsea_visit_bg` | 拜访活动背景_选定 | =夏日拜访 | ActvOnline105605.ActvImg | ✅已出 | 裁 |
| 07 拜访 | `DK_img_Activity_deepsea_visit_pack` | 拜访礼包图_选定 | =拜访礼包图 | Pack211020.Icon/Head | ✅已出 | 裁 |
| 07 拜访 | `DK_img_Activity_deepsea_visit_icon` | 拜访HUD icon | 124×136 | ActvOnline105605.ActvIcon | ⛔待出 | — |
| **★festival HUD icon** | `DK_img_Activity_deepsea_hud_icon`（潜艇徽章） | 深海节HUD入口icon_潜艇 | 124×136 | **各模块 ActvIcon 共用**（用户定2026-06-22:HUD就用潜艇行军皮） | ✅已出 | **透明**+裁124×136 |
| **08 许愿池** | `DK_img_Activity_deepsea_wishpool_bg` | 许愿池活动背景_深海 | =许愿池原bg | ActvOnline105013.ActvImg | ✅已出 | 裁 |
| 08 许愿池 | 水池图 DK_PoolImg | **复用现成喷泉**(img_Activity_fountain_bg_*) | — | ActvWishingPool5013.DK_PoolImg | ✅复用(用户定2026-06-22·不出新·全屏深海背景已够) | 无需处理 |
| 08 许愿池 | `DK_img_Activity_deepsea_wishpool_icon` | HUD icon | 124×136 | ActvOnline105013.ActvIcon | ⛔待出 | — |
| **09 酒馆** | `DK_img_Activity_deepsea_tavern_bg` | 最佳酒馆背景_选定 | =夏日酒馆 | ActvOnline10071704.ActvImg | ✅已出 | 裁 |
| 09 酒馆 | `DK_img_Activity_deepsea_tavern_icon` | 酒馆HUD icon | 124×136 | ActvOnline10071704.ActvIcon | ⛔待出 | — |

## 入库批次建议（一波搞）
1. **✅图已出·可直接处理入库**（8件）：兑换背景 / 铭牌大图+小图(需透明) / 04头像框+弹窗(需降分辨率) / 05累充bg / 06视频 / 07拜访bg+礼包图 / 09酒馆bg。
2. **🟡待挑定再入库**（2件）：01转盘bg(大/小潜艇) / 02 BP bg(v1/v2)。
3. **⛔图待出**：基本清零。转盘皮 3 件(盘面/底台/指针)已出(指针出图中)；许愿池水池图复用现成；HUD icon 共用潜艇。剩按需补即可。
4. ✅**HUD icon 已解**：用户定「各模块 HUD 入口统一用潜艇 icon」→ `深海节HUD入口icon_潜艇` 一个共用，铺到各模块 ActvIcon，不再零散出。兑换/02BP/05累充/07拜访/09酒馆 的 HUD icon 槽都填这个。

## DK 命名 / 入库链路参考
- DK→GUID asset 注册 + tableResInfo + push client：见 [[reference_x3_client_resources]]。
- 透明处理：铭牌/头像框/icon 走 remove_background 或双底差分（gpt 假棋盘格不是真 alpha）。
- 入库后回填各模块配置备份的 DK 字段（现为占位名），再插表过 gate。

_生成 2026-06-22。待美术挑定 + HUD icon 补齐后一波入库。大富翁 DK 另一 agent 负责。_

## ★DK 入库后必做：Unity DisplayKey 面板刷新（用户嘱 2026-06-23·含正确按钮顺序）
手编/脚本注册 DK 进 Path_*.asset(+Display_*.asset) 后，**必须在 Unity 编辑器 Ctrl+T 打开 DisplayKey 面板刷新**，否则编辑器内存里的旧 DK 字典不认新 DK → **运行时 ActvImg 等解析失败、显示上一个活动的残留背景**（2026-06-23 转盘背景实证：配置/png/guid/Path/Display 全对，但游戏显示旧室内图 = 运行时字典没刷新；盘面对是因为那 DK 早在 dev、新加的背景 DK 没进字典）。
- **★面板按钮正确顺序（防 e255 清 DK）= 先 `LoadFromDisk` → 再 `Save And Generate Code`**：
  1. 先 `git pull` 确保磁盘有所有最新 DK（自己的+别人的）。
  2. 点 **LoadFromDisk**：把磁盘上的 Display/Path asset 读进面板内存（此时面板内存 = 磁盘最新，含新 push 的 DK）。Search 框搜新 DK 名确认加载到了。
  3. 点 **Save And Generate Code**：把内存写回 asset + 生成运行时字典/代码 → DK 生效。
  4. 重新 Play（或重打 AB）。
- **⚠️ 绝不能跳过 LoadFromDisk 直接 Save**：面板初始内存是旧状态（没新 DK），直接 Save = 旧内存**覆盖**磁盘 → 清掉新 push 的 DK（= e255 全量重导出清 DK 的同一机制，见 [[reference_x3_client_resources]]）。LoadFromDisk 的作用就是先把磁盘最新灌进内存，让 Save 不会倒退。
