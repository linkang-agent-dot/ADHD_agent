---
name: x2-metro-minigame-rock-drop-link
description: "X2挖矿小游戏 关卡掉落链路(level→rock_drop) + fo/cn坑 + 导表漏导致服务端panic;查\"空地放不了工人/挖完不发奖/矿占格\"类bug先读"
metadata: 
  node_type: memory
  type: reference
  originSessionId: aa38e334-e3cc-44de-9267-81844ffc53fc
---

# X2 挖矿小游戏(metro_minigame) 掉落链路 + 经典 BUG

2026-06-08 排查 X2-43003【节日挖矿·空地无法放置工人】沉淀。

## 掉落链路
- `metro_minigame_level.tsv`(关卡) 每格 `{"unit":矿单位,"drop":掉落ID,"displaykey":..}` → `drop` 指向 `metro_minigame_rock_drop.tsv`(=表号**3514**) 的奖励配置。
- **关卡表有两套布局列**：`A_MAP_level_design`(col2/主) 和 `A_MAP_level_design_b`(col3/备用)。⚠️**design_b 会被服务端实际加载**(X2-43003 实证：主列已改成有效 drop，服务器仍 panic 在只存在于 design_b 列的 35143805)。改掉落必须**两列都改**，只改主列等于没改。
- 服务端 go 代码 `hmetromini.(*hotUseCase).miningDrop`：drop 查 rock_drop **空配置不做保护 → nil pointer panic**。后果：矿被 MarkFinish 标 finish=true 但不发奖、ReceiveRockDrop 不触发 → 矿实体不删一直占格 → 该格放工人报 `ErrCodeTargetInUnitRect`(=「空地放不了工人」表象)。建议给程序提:rock_drop 查空跳过发奖兜底,别 nil panic。

## fo/cn 坑（最大）
- X2 配置仓 `D:\UGit\x2gdconf\` 下分 **fo/**(海外·dev服实际用) 和 **cn/** 两套 config。
- ⚠️ **cn 是 2024-10-31 初始提交的死快照,这仓里就没再维护过**——别拿 cn 当「正确基准」对 diff(我第一轮就栽这,误以为"cn有fo无=从cn同步")。**真源是 GSheet,不是 cn。**

## 经典根因：换皮只导部分表(漏导 rock_drop)
- 拓荒节2026 更新(commit 改 2112/2130/3516)**导了 fo/level、漏导了 fo/rock_drop**(rock_drop tsv 冻结在更早日期)→ level 引用了一批新掉落 ID,rock_drop 里没有 → 整张挖矿玩法(常驻关+原矿/新月/循环/KVK矿洞)大量格子挖完即崩。
- 这就是 [[X2 配置表查询权威源]] 里记的「改了GSheet≠导了/低频表整张漏导」坑的实例。

## 修复决策：重导前先验真源有没有行
- **导表只能导出 GSheet 真源已有的行**。修 rock_drop 缺失前,先 `gsheet_query.py row 3514 <id>` 验真源:
  - 真源**有** → 纯漏导,**重新导表 metro_minigame_rock_drop(fo) 即补齐**(本次 320+ 个 ID 含 35142708/35142612/35142805 都属此类)。
  - 真源**也没有** → 导表导不出不存在的行,需**策划先在真源建行**或把 design_b 对应格改指已有 ID(本次 35143801/802/804/805 这 4 个 design_b 专用 ID 真源全无)。
- rock_drop 真源 SheetID=`1zoBK_3-eRBLcKgwWJ9_Z2GnmYRty5Dhip8EpCgDXVx8` / tab `metro_minigame_rock_drop`(`gsheet_query.py resolve 3514` 现解,别硬抄)。

## 修复执行（2026-06-08 实战闭环，commit 8e9746028 @dev_festival）
- **这类「整张表漏导/停在旧版」的 bugfix,仍用「行筛选模式」不用全表模式**:表停了5个月,全表会把别人未验证的改动全拉进提交/上线。只补「level 实际引用 ∩ rock_drop 缺失」的行。
- 流程:`Copy-Item tsv→.bak`(工作区干净时=HEAD基线) → `fwcli googlexlsx -f 3514`(下载全表覆盖 tsv,1000→1324行) → `merge_rows.py tsv "<id列表>"`(以.bak为主本只取目标行) → diff验证 → 格式校验 `check_tsv_format.py` → 精确 `git add <tsv>`(避开他人遗留.bak) → commit/push。
- 本次:114缺失里110个真源有→[added];4个 design_b 专用(35143801/802/804/805,含35143805)真源也无→merge_rows报`[WARN] not found anywhere`跳过,留策划在真源建行。
- ⚠️ **diff 出现 `-1/+1` 是 benign**:原最后一行无尾换行,merge 后补换行让新行接上,内容一致(逐字段比对确认);真实改动应是纯 `+N`。CRLF/LF warning 也正常(autocrlf,git diff 没整表炸即 OK)。
- ⚠️ **push ≠ 生效**:X2 配置改完要走 x2-kadmin 构建+部署+重开活动才在测试服生效。

## ⚠️ 「漏传」和「真源缺数据」是两个独立问题,别混(X2-43003 关单陷阱)
导一张缺行的表前,先把缺失 ID 拆成两类,**导表只能解决第一类**:
- **A. 漏传**(真源有/fo 没导)→ 行筛选导表即修(本次 110 个)。
- **B. 真源缺数据**(两套都没建,本次 35143801/802/804/805)→ 导表无能为力,需策划在真源建行或改 level 指向已有 drop。
🔑 **关键教训**:X2-43003 日志实际报的 `35143805` 属 B 类,**不在今天导的 110 行里**。今天补的是同批漏传里的 A 类,解决的是**其它**矿格崩溃,**X2-43003 那一格(关卡351610821 cell114)没被这次导表修到**。验收单务必按"日志报的具体 ID 是否真就位"判,别用"这批表导完了"当关单依据(`grep ^<日志ID> rock_drop.tsv` 实测)。
- 该格 MAIN(level_design)=35140207(有效) / BACKUP(level_design_b)=35143805(从无)。服务器读到 35143805 ⇒ 走的是 design_b(或部署的 level 是 5-22 修复前旧版)。收尾分叉仍卡在「design_b 加不加载」这个未决点(需 X2 服务端代码确认选 MAIN/design_b 的逻辑)。

## design_b 4个掉落的拓荒对应物(2026-06-08 策划建行后换皮收尾，commit dd3b8ae37)
策划在真源建了 35143801/802/804/805 但**整行从科技节/复活节复制、item+lc 没 reskin**(白/绿卡包实发养成自选箱/公会红包、骰子/BP是复活节的)。验收换皮残留:rock_drop 行的 `comment`/`lc_name` 声称 vs `A_MAP_drop` 实际 item 一对就露馅。换成拓荒对应物的查法:
- **集卡卡包** = 拓荒集卡册 Book `1108` 11081004「拓荒传奇」的 `CardPackID=[111111339(1-2星),111111340(1-3星),111111341(2-3星)]`(白→最低档339/绿→中档340，按品质序映射)。lc 用 item 自身 `LC_EVENT_item_card_pack_name_15/16`。
- **BP经验** = item 表搜 `battle_pass_exp` 类，三个年份(2024=11112150/2023=11117411/**2026=111111314**「纪念钻头-拓荒节2026活动BP道具」)取当年。lc `LC_EVENT_labor_2026_bp_EVENT_title`。
- **大富翁骰子** = **无拓荒专属**(搜「骰子」只有春节/复活节/战装版)，用户确认**复用 11112498**(漫游骰子-节日进度活动)不改。
- 写真源用 `gsheet_utils`: `backup_tab`→`find_row_by_value(SID,TAB,'A',id)`(行号比 gsheet_query 显示的差1,必按内容定位)→`update_cell` 改 **F列(A_MAP_drop)** + **I列(C_MAP_lc_name)**→复查。改完再行筛选重导这4行到fo。

## display_key 字段(矿块图标,本次未改·观感问题)
- rock_drop col5 `C_ARR_display_key`=`[{"plan":0,"displayKey":DK},{"plan":1,"displayKey":DK}]` = **矿块上盖的提示图标**(DK→Display_*.asset→sprite)，plan0/1 对应两套地图布局(=design/design_b)。
- level 格子内嵌的 `displaykey` 是**单格覆盖**，优先于 rock_drop 默认。
- ⚠️ 只决定矿块长相、**不决定发什么奖**(奖=A_MAP_drop, 名=lc_name)。换皮残留的 display_key 指旧节日图=矿块图不对题但功能正常,可暂不修(本次拓荒矿块图美术未确认,用户定先放着)。

## 快速排查命令
- 缺失面全量算: 遍历 level 表 col2/col3 收集所有 `drop` → 减去 rock_drop 现有 id 集合 = 会崩的格子(用 `python` 走 `D:/UGit/...` Windows 路径,bash 的 `/d/` 路径 python 读不到)。
- ⚠️⚠️ **metro 各表 Id 列位/表头行数不统一(2026-06-08 误判两次的坑)**——抓 id 前必先 `head -2 <表>` 看清:
  - `metro_minigame_level`: **Id 在 col1**(`A_INT_id`,无 p2_title)、**3 行表头**(`NR>3`)、col2=comment(名如"活动关卡1_1")、col3/4=level_design(A/B)、**col9=hero_in_mine**、col8=research_exitdoor、col11=research_checkpoint_actv。
  - `metro_minigame_hero_data`/`metro_minigame_activity_group`: **有 p2_title 列→Id 在 col2**、3 行表头、activity_group 的 **col10=HeroData**。
  - `metro_minigame_rock_drop`(3514): **Id 在 col1、单行表头(`NR>1`!)**——用 `NR>3` 会**漏掉前两条真数据**(35140101/102)致误报悬空。
  - 用错列/错表头行数 = 拿到空集 → comm 全标"悬空"假阳性。每次重建 id 集后先 `wc -l` 核数量(rock_drop 应 ~1114、research 3518 ~1192)非 0 再比。
- ⚠️ **level→research 用的是科技「组 id」(如 3518117)不是行 id**(行是 351811701~706)；拿 level 的 research 引用去 `comm` 减 research 行 id 会假性悬空，要减 **research_id(col3,组) 集**。
- ⚠️ **hero id 两套**:X2=8 位 `35251xxx`、P2 残留=9 位 `352513xxx`;别用 `35251[0-9]+` 贪婪正则(9 位被当 8 位前缀混抓)。

## ⚠️ 另一条独立根因：客户端内嵌配置 fo→Gen/bytes 停在旧版（2026-06-08，metro_minigame_hero_data）
跟上面 rock_drop(服务端·x2gdconf) **不是一回事**——这条在**客户端仓** `x2client\client\Assets\P2\Config\`（X2 客户端走 P2 命名空间），且**客户端有自己独立的导/生成管线**（`Config\scripts\gsheet_down.py`+`run.bat`+`gen_conf.py`，`gsheet_config.ini` 直连 GSheet，与服务端 `D:\UGit\x2gdconf` 分两套）。
- **三层文件**：`fo\config\*.tsv`(源·人改) → `Gen\tsv\metro\*.tsv`(生成·人读镜像) → `Gen\game\bytes\*.bytes`(运行时实际加载·二进制)。`cn\` 国服不用、`Res\config\` 无副本，dev 服运行时只认 `Gen\game\bytes`。
- **根因模式**：源 `fo` 更新了(`metro_minigame_hero_data` 43 行到 35251043)，但 fo→Gen 那步**没重新跑**→`Gen\tsv`+`bytes` 停在 15 行(35251015)。`hero_in_mine`(关卡 posKey→英雄id数组)引用 35251016~31，bytes 里没有 → 客户端 `CMetroMinigameHeroData.I(35251016)` 返回 **null** → 矿格英雄/工人加载失败(「空地放不了工人」表象的客户端分支)。
- **与 rock_drop 漏导的区别**：rock_drop 是**服务端 nil panic**；hero_data 是**客户端取 null**。两者可同时存在于同一挖矿玩法换皮里(都是"换皮只导/只 gen 了部分表")。
- **判据(逐文件核 Id 列)**：⚠️ 该族 tsv 是 **3 行表头**(p2_title/fwcli_name/fwcli_type)、**Id 在 col2 不是 col1**(col1 是 `fwcli_name`/`p2_title` 标记列，首数据行常是个 `A`)；数据行 `awk -F'\t' 'NR>3{print $2}'`。bytes 是二进制，`strings|grep` 抓不到数字 id(纯二进制存)，**改判 `Gen\tsv` 即可**(它与 bytes 同步生成，tsv 停在哪 bytes 就停在哪)。fo 比 Gen 多出的 id 集 = 会取 null 的引用。
- **修复**：fo 已全 → **不需重拉 GSheet**，只需把现有 fo 重新 gen 成 `Gen\tsv`+`Gen\game\bytes`。⚠️`.bytes` 是序列化产物，**改 tsv 补不了**，要跑客户端配置生成工具(gen/Unity 那一步)产 bytes，再提交客户端仓(分支 `dev_festival`)。最稳=交客户端同学重导这表/整批 metro 表的 gen。
- 🔑 **生成入口(命令行做不了,必须 Unity Editor)**：`Config\scripts\` 的两个 python 都不产 bytes(`gsheet_down.py`=GSheet→tsv 下载、`gen_conf.py`=tsv→MongoDB 服务端导入)。真正产 `Gen\tsv`+`Gen\game\bytes` 的是 Unity C# 工具 `ConfigGenerator.GenerateConfigBinaryAssets()`(封在框架 DLL,走 fwcli+`EditorUtility`/`Application.dataPath`,只能 Unity 进程内跑)，菜单 **`Config → Show GDBuild Tools`**(窗口"客户端配置表生成工具")；入口源码 `client\Assets\Editor\ConfigGenerate\GDConfigGenerate.cs`，打包侧同名调用在 `Assets\P2\Editor\BuildPipeline\Tasks\GenerateConfigScriptsAndAssets.cs`。该工具大概率全量重生成(无单表入口)，跑前确认 fo 里只该表新改或跑完只 review 该表 Gen 改动再提交。
- 🔑🔑 **真正根因(2026-06-08 续查，纠正上面"Gen没生成"判断)**：「空地放不了工人」真因 ≠ Gen 旧，而是 **`metro_minigame_activity_group` 的 `HeroData` 列(col10, A_ARR_hero_data) 填了 X2 不存在的 9 位 hero id**。
  - 实锤：拓荒**段位玩法 schema3/4/5**(精英/冠军档)三行 `35103322`/`35103422`/`35103522` 的 HeroData = 9 位 `352512xxx`/`352513xxx`(各 14 个)，这批 id 在 X2 所有 metro hero 表都不存在(X2 hero 用 8 位 `35251xxx`)——**从 P2 换皮没转 id 的残留**(P2 hero 用 9 位 352513xxx)。加载这三档→`CMetroMinigameHeroData.I(352513025)` 取 null→放不了工人。正常行(schema2 `35101201`)HeroData=8 位 `35251001~015`(15 基础档英雄)；全表仅这 3 行(末尾 22)悬空。
  - **与第一张图诊断的关系**：图盯 level.`hero_in_mine`(35251016~31)说"Gen 没生成"——那些 id 真源**有**(8 位齐到 43)、只是客户端 Gen/bytes 旧(停 15)，属**次要**；schema3/4/5 必崩的真因是 9 位悬空 id，**重生成 Gen 也救不了**。
  - **修复(2026-06-08 用户拍板"就用基础档位")**：3 行 HeroData 直接改成 schema2 同款基础档 `[35251001..35251015]`（精英/冠军不另配新英雄）。⚠️好处：35251001~015 在旧 Gen/bytes 里**本就存在**→改完连 Gen 重生成都不强依赖。改的是 `metro_minigame_activity_group` 表(非 hero_data 3525)。
  - 🔑 **排查范式**：挖矿"放不了工人/英雄不显示" → 核 `activity_group.HeroData`(col10) 引用的 hero id ⊆ hero_data 真源 id 集；`awk -F'\t' 'NR>3{print $10}' metro_minigame_activity_group.tsv` 抓出 `comm` 减真源。⚠️hero id 有 8 位(X2)/9 位(P2 残留)两套，别用 `35251[0-9]+` 贪婪正则混抓(9 位会被当 8 位前缀误匹配)。

## 第三类经典换皮漏配：科技解锁(metro_minigame_research)漏登记新关卡（2026-06-08 拓荒「障碍墙科技解不开」）
- **现象**：节日挖矿里 boss/障碍墙等点位的"活动科技"(免费矿工/产出倍率/矿工上限…)整批解锁不了；但**矿洞科技正常**。
- **机制**：`metro_minigame_research`(表 **3518**) 的科技按 lvl1 行 `requirement_metro` 解锁，分两种条件类型——
  - `metro_mineshaft_active_event`(查当前矿洞是否激活，**与关卡链无关**)→ 节日换皮不受影响，照常解锁(解释了"为啥矿洞科技好的")。
  - `metro_small_level_event`(条件是个 **OR**，列一串**关卡 id**，必须命中**当前活动用到的关卡**)→ OR 是"历代上线过的活动关卡清单"，**增量手工维护**。
- **根因**：节日换皮**新建了专属关卡**(拓荒 35161082x~85x；level_group 35171082~85，普通/精英/冠军多难度档)，但**没把新关卡 id 反向登记进各科技的 requirement_metro OR** → 该活动里所有 `metro_small_level_event` 型科技全部 CheckCondition 失败 → 不解锁。全静默。
- **关卡↔科技绑定来源**(metro_minigame_level 表)：col11 `research_checkpoint_actv`(清 checkpoint 授予) / col8 `research_exitdoor`(过出口门授予) 里的 `{"typ":"metro_minigame_research","id":<科技>}`；col10 是矿洞型(不受影响)，col5 `auto_requirement` 是前置门(metro_minigame_research_event 引用科技等级，非授予)。
- **必检/修法**：节日**全部关卡(各难度档全子关) × {col8,col11} 引用的科技** → 逐个查该科技 lvl1 行 OR 是否含**本关卡 id**；缺则给 OR `args` 追加 `{"op":"ge","typ":"metro_small_level_event","id":<本关卡id>,"val":1}`(照搬现有条目，op/val 不变)。拓荒实测漏 8 个科技组(3518116/117/118/119/121/124/125/127)各缺自己一关。
- **OR 条目==该关卡自己的 id**：旧节日关卡既配 col11→科技、又在该科技 OR 里(双向)；换皮只补了 col11 一侧。OR 成员按 _1/_2/_3 子关分流，但**以 col8/col11 实际引用为准**，别只按子关号猜。
- 🔑🔑 **写回真源页签陷阱（这表是"每节日一个工作副本"结构，最大坑）**：SID `1Ath_557I09R58in4w6PWbsOhD28NpenX6qcZoqBp8Ys` 里有 26 个页签——按节日命名的版本副本(615情人节/**69万圣节**/68登月节已合/63科技节已合…)、纯参考页 `metro_minigame_research`、工具页等。
  - **导表真源 = 含 fwcli 3 行表头(`p2_title`/`fwcli_name`/`fwcli_type`)的那个页签 = 当前是 `69万圣节`(gid 232875885)**，名字是历史复用残留(参 [[X3 TimeCycle 名字可能是历史复用残留]])，**别被名字误导**。判定法：`gsheet_utils.list_tabs(SID)`→读各页 A1:A3，A1=`p2_title`、A2=`fwcli_name`、A3=`fwcli_type` 的就是导表源。验证：该页 3518117 的 OR 应与本地 tsv **逐字一致**(本次 `…481,421,451` 对上)。
  - **真源页(69万圣节)布局 = 标准 tsv schema**：col A=p2_title(标记列)、**id 在 col B**、**`requirement_metro` 在 col O**(index14)、数据从第 4 行起。
  - ⚠️ **别信 gsheet_query 别名 `3518_x2_metro_minigame_research`**——它指向的 `metro_minigame_research` 页(index2)是**已分叉的纯参考副本**(无 p2_title→id 在 col A、requirement_metro 在 col N、OR 含 391 与 tsv 不一致)，**改它不进游戏**。`resolve 3518` 默认页也不可信。
  - 本次教训：第一轮误改了 metro_minigame_research 参考副本(col N)，经用户提醒才发现导表真源是 69万圣节(col O)——两个页都写了(参考副本无害留着)。
- 写回都用 `gsheet_utils.find_row_by_value(SID,TAB,'B'或'A',<id>)` 现定位行(各页行号有偏移，别抄 gsheet_query 的行号)。写前 `backup_tab` 备份。
- ⚠️ 改完仍需 **导表 metro_minigame_research → push → x2-kadmin 构建/部署 → 重开活动** 才生效；已清过 checkpoint 的玩家需再触发一次进度/重进活动才会补解锁。

## 全套挖矿配置表地图（2026-06-08 X2-43058 排查补全；表号按 id 前缀，查改前 `gsheet_query.py resolve` 现解）
| 表号 | 文件 | 管什么 |
|---|---|---|
| **3510** | metro_minigame_activity_group | 布局方案(plan)总表：一方案用哪些关卡组/科研/产出单位plan/地图单位/HeroData。拓荒 plan id `35101201~05`，各引 14 科研，union=26 |
| **3513** | metro_minigame_map_units | 地图单位(type 18 类)：type1=工人 / **type2=矿石(玩家挖的矿)** / 3洞 4阶 5底 6B大小 7鞭 13怪 17特殊矿石(只能斗工攻击) / boss障碍墙。字段 `rock_blood`血量 `occupied_area`占格 `display_key`外观 |
| **3514** | metro_minigame_rock_drop | 挖掉一格发什么奖(`A_MAP_drop`)+矿块图标(`C_ARR_display_key`) |
| **3515** | metro_minigame_production | **产出型"矿"数值**：铸造室(forge)+15 元素提炼仪(mineshaft_1~15)。按 `group`(矿种)×`plan`(布局) 拆，每矿每方案 **600 级**；字段 `gold_cost`升级费 `gold_output`产量 `cycle`周期 `research_id`挂3518 `buff_property` `icon_display_key`。⚠️拓荒用 **plan=1 → group 351516~531 → research 3518100~115** |
| **3516** | metro_minigame_level | 关卡格子布局(design主/design_b备,**design_b会被加载**)，每格 `{unit:3513id, drop:3514id}` |
| **3517** | metro_minigame_level_group | 关卡组 |
| **3518** | metro_minigame_research | 科研树 |
- 矿名/科研名 i18n 在 **GSheet 1011 `METRO` 页签**(gid 1399969408，SID `1YGVYG…bisZSyg`，key 在 col B/`ID`、cn 在 col C)：`forge`=铸造室、`mineshaft_1~15`=铁/铝/铜/氧/氯/氮/碳/磷/碘/镁/锌/钾/氖/银/金元素；`research_type_worker`=工人 `_ld`=障碍墙 `_production`=生产单位 `_rock`=矿石 `_award`=奖励；`research_label_profit`=产量 `_time`=生成时间 `_speed`=生产速度 `_num`=数量 `_discount`=折扣 `_crit`=暴击率。

## 科研面板「重复显示」诊断（2026-06-08 X2-43058，判定=非配置/疑客户端未去重）
- **现象**：节日挖矿科研「已激活」页签 铸造室/铁元素 等重复显示、消耗/展示不一致。
- **判定：客户端渲染未按 ResearchId 去重，不是配置错误**。证据链(以客户端实读 TSV 为准)：① 科研是全局永久池(面板顶写"永久生效、不会进入新关卡时重置"，顶部 x/26 按去重算)；② 用户点名的 铸造室=`LC_METRO_forge`=ResearchId **3518100**(唯一)、铁元素=`LC_METRO_mineshaft_1`=**3518101**(唯一)，配置里各只 1 个节点，不可能配重复；③ 拓荒 5 个 Plan(35101201~05)各引 14 科研、union 正好 26 distinct，**forge 在全部 5 个 Plan、mineshaft_1 在 3 个 Plan** → 客户端按 (Plan×Research) 渲染同一节点就会重复画出。
- **同名不同 id 组是设计、非 bug**：26 节点里唯一「同 LcName 不同 ResearchId」的是 worker(3518117/118/125)/production(119/120)/ld(121/122/124) 三组，靠 `LcLabel` 区分子项 → **P2 原生设计照搬**(P2 worker/ld 各 8 个共名)，看着重复实为设计。
- 🔑 **教训**：客户端类活动「显示重复/异常」先**按数据判型**——同 id 跨容器(Plan)重画→研发去重 bug；同名不同 id→设计/配置撞名。别一上来扎进配置改 LcName；并先确认测试端客户端是否最新版。

## 3514 拓荒掉落道具核查结论（2026-06-08）
- 186 个掉落行；4 个 design_b 节日专属已全部 reskin 到拓荒当期物、**无残留**：35143801/802 白绿卡包→`111111339`/`111111340`(拓荒传奇册11081004)、35143804 大富翁骰子→`11112498`(复用，无拓荒专属属正常)、35143805 BP→`111111314`(纪念钻头-拓荒BP道具)。
- 其余为通用资源池(节日+非节日共用)：`11111104`15分钟加速 / `11114329`中级资源宝箱 / `11116151`英雄粉尘 / `11116201`铁匠碎片 / `11116303`**万能英雄碎片-紫色** / `11116258` 周年艾玛碎片。
- ⚠️ `11116258`「周年艾玛碎片」在 item 表 1111 GSheet 查不到名字(疑遗留)，被 ~15 个通用掉落行(如 35142612)发放，非节日专属。
