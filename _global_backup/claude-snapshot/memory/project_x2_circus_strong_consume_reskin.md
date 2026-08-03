---
name: project-x2-circus-strong-consume-reskin
description: 马戏节·强消耗扭蛋机 X2→X3 搬运案——⚠️目标项目=X3(勿当X2内换皮)；唯一入口=X2换皮档案2026-07-08_马戏节
metadata: 
  node_type: memory
  type: project
  originSessionId: cd228f8f-4607-4cf7-8606-1ab0bf68ce0c
  modified: 2026-07-31T07:14:09.747Z
---

# 2026马戏节 强消耗扭蛋机 X2→X3 搬运（进行中，2026-07-08 开案）

## 🛑 目标项目 = X3（2026-07-08 用户拍板；此前按"X2 内换皮"做的落表方案作废）
- X2 扭蛋机玩法搬到 X3 新做：程序按协议配置规格文档在 X3 实现协议+配置结构；prefab 资产（`D:\newX2\Copy\UIactvfesstrong\`）导入 X3 客户端；X2 占星2025 配置只当**数值基准**。
- **马戏节有大富翁（=深海大富翁 102802 那套承接）**→ 奖池骰子位映射马戏大富翁抽奖道具；节日代币位（X2 的 BP 代币 111111314）→ **换别的**（X3 没有 BP 积分），X2→X3 道具映射方案进行中。
- 排期未定 → 配置时间 tc 填 0。扭蛋机本体资源全部沿用，外围美术 3 张（banner×2+图标）。

**唯一入口**：换皮档案 `C:\ADHD_agent\KB\换皮档案\X2\2026-07-08_马戏节.md`（进度/决策/坑全在这）＋方案总览 HTML `KB\产出-数值设计\X2_2026马戏节\X2_2026马戏节_强消耗扭蛋机_换皮方案总览.html`（⚠️HTML 的落表章节还是 X2 版待改向）

## 支撑文档（骨的知识，别重挖）
- 协议+配置规格（proto tag 全表/表schema/2025真实模板行，X3 程序实现蓝图）：`C:\ADHD_agent\KB\方法论\活动程序开发\X2_强消耗扭蛋机_协议与配置规格.md`
- 客户端链路（皮全在prefab静态/4个LC key/rank硬编码坑）：[[x2-strong-consume-client]]
- X2 数值基准（占星2025 全链：4奖池权重/14档积分/5+5礼包/排行/回收）：`KB\产出-数值设计\X2_2026马戏节\X2_2026马戏节_强消耗扭蛋机_数值方案.md` + 原始数据 `config-library\cases\2026_circus_strong_consume\baseline\`
- 原始策划案：GSheet `13eHiIX48L7Y865XLGOBxJqWloXiirNC43djoK17i2II` 页签 `v66宝箱版本`

## 进度（2026-07-09）
映射✅（罗盘1057本尊合并槽/冒险阅历=英雄经验/排行无信物，均用户拍板）→ 数值定稿✅（task-checker 11/12 零blocker，`X3_马戏节扭蛋机_数值定稿.md`）→ **v2.1（07-09拍板）：取消分阶段，普通/高级两套固定池，整活动ROI=7.82x纯线性，程序不用做dropID切换**；高级池单抽期望$1.95/成本$0.25券，对外报数只用高级池 → **v2.2（07-09）：普通池下调**——三方免付比对比(P2 11-18%/X2 15-29%/X3原45.5%超标)→三专项加速×2→×1，普通池EV 241钻*/免付比24.6%回X2带，罗盘槽不动；方法论(平移价值占比非件数)已沉淀 x3-numerical-design memory→ 新道具定名✅（**1207节日扭蛋币**用户拍板 / 1208高级扭蛋券默认沿X2名）→ 交接总览HTML已刷成X3终版（同名文件覆盖）。
## 配置进度
- **✅第一批已落地（07-09）**：Item **1211节日扭蛋币/1212高级扭蛋券**（🛑原1207/1208被整节日案转盘道具占：1207外圈票/1208彩虹星/1209大转盘票/1210勋章——引用别搞混）+Text cn/en，dev_festival commit 4dc2ea4，jolt#1690 SUCCESS；worktree 已拆。
## X3 客户端落地（07-21 已迁入）
- 主 prefab（一体版）：`C:\x3-project\client\Assets\Res\UI\Prefab\Activity\UIActvCircusGacha.prefab`，分支 dev_festival（迁移提交 8e11ea9c73f 合规化迁移+DK注册 / 56fad4e3447 UI三处调整）；贴图在 `Assets\Res\UI\Sprite\UIActvCircusGacha\Images\`（21张）
- ⚠️手动改 prefab 须知：顶部标题栏 Top 在 prefab 编辑模式下"掉到画面中间"是**正常现象**（拉伸锚定+负sizeDelta，克隆源 LaborGacha 同样表现），别拖回去；Game 视图切竖屏分辨率(1080×2337)重开 prefab 即显示统一。原理+工具见 KB\方法论\活动程序开发\X3客户端GUI知识.md 对应条目
- **缺背景图根因（=X3NEW-2366）**：根节点下子节点 `BG`（1640×2560 全屏底图，当前 inactive）的 m_Sprite 引用 guid `fd139905db61e7349b3559b7d867043f` 全工程不存在；该 guid 在 X2 导出包和 X2 客户端 tracked meta 里也搜不到（疑似 X2 公共图集里的图没跟着拷）→ 修法=Unity 里给 BG 重新指一张背景图并激活。prefab 其余 69 个 sprite 引用全部完好

## ⏳ 在途（07-21）②：客户端 prefab 手调批次（磁盘已改未提交，x3-project client dev_festival）
- 用户手改（已在磁盘）：BG 背景修复激活、双标题白字+深描边、AutoTrain 挪位
- 奖池格子 6ICON 排版（07-21，多轮定稿）：两台机器终值——**Grid cellSize 105 / ItemMid localScale 0.64 / Scale 节点 0.8(标准勿动) / Constraint=FixedColumnCount 3列居中 / 列表区 488×210 原位**；图标比原始(cell100/0.5)大~27%又不超蓝面板框。⚠️两坑教训：①放大只调 ItemMid 别调 Scale 节点（Scale 不含 Count/Lv，动它数字偏小脱位）②cell×行数超面板可视高会超框（120×2=240 超，105×2=210 刚好）。规律见 GUI KB「调格子大小的正确层级」。积分轨道格未动
- ✅三批改动已重做落地（07-21 二次，用户退出编辑态后执行，验证=对象数1606/coin×3/缺失无）：①道具格占位图 ②英雄层全关 ③BtnBlue+GiftEntry 接回。可复跑脚本=`C:\ADHD_agent\skills\unity-prefab-tools\examples\circus_prefab_batch.py`（子树手术+孤儿回写范例实现，断言写目标态不写动作数）。改动在磁盘未 git 提交，随用户后续手调一起提
- 后续待办：①用户自调 BtnBlue 透明度 ②GiftEntry/icon 是劳动节旧图待换马戏图（用户已确认不对；可先顶 icon_global_circus_gachacoin 或进美术清单）③✅6-ICON 已双侧落地（07-21）：prefab 排版见上；**奖池 v2.4**（dev_festival `bb44b0b5`）=每池 7→6 行——免费池删通用加速(w15匀给三专项60/45/45)/付费池驯养经验并入冒险阅历(w200)，总权重不变期望持平；**删行保EV手法=权重匀给同类行而非全体**（匀全体会把权重漂给高价值行抬EV）；引用检查注意撞号≠引用（BP基金表主键820105与被删行同号不相干）
- **✅已裁定（07-21）：礼包入口不挂 UIBtnGift**——GiftEntry 已走 `SetActivityBaseInfo(goGiftEntry:)` 通用链路（UIActvCircusGacha.cs:131），ChainPackID=**707**（高级扭蛋券，PackList 13031/13032/13033）已配，显隐/红点/弹窗全通；🔴**2026-07-28 纠正：本文此前记的 704 已过期**——合并让号时 `ChainPack 702/704→706/707`（见 [[workflow_x3_merge_conflict_audit]] 让号总表），704 现在是「藏品屋」完全无关的活动。**通用教训：让号后必须回头改所有引用旧 ID 的 memory/文档**，否则后续排查按旧号找会查到别人的活动上去（本次派 agent 就是拿 704 交底的，靠 agent 自己查实才没走偏）。UIBtnGift 挂件=同逻辑另一套壳，重复。两套壳对比见 GUI KB §4.5

## ✅本地化已闭环（07-21）：Probability 文案=「高级奖励预览」
- dev_festival commit `a166767c`（16语言含ua，泄漏审计过），jolt build #2000 SUCCESS，worktree 已删。付费机顶部标题运行时显示「高级奖励预览」。
- ⚠️ TXT_ActvCircusGacha_* 这批 UI key **只存在 Text tsv**（无 CoderTID/配置表源），扫描不会回滚也不会自动补——直改 Text tsv 即可，但严格说应该补登 CoderTID（待办）。
- prefab 道具格结构：图标节点=`ItemMid/Scale/Icon`（代码 CircusGachaItem.cs 运行时按道具ID填图，改图去改配置不改prefab）；奖池列表排版=Content 的 GridLayoutGroup(100×100)；标题字色已调白字+深描边（355B82/986D2E）
- **✅已裁定（07-21）：格子全套=X3标准件，勿再纠结**——品质框指 X3 公共图集 `NewSprite/Common/frame/IconBox2_*`，发光 Fx_UI_JiangLiKeLingQu_Glow 与 X3 公共 `Common/Item/ItemBig|Mid|Small.prefab` 同源；编辑器里"X2感"来自占位假数据(Lv99头像/555数量)，运行时按X3道具ID填真图。X2 皮只在机器本体（机身/扭蛋球/按钮，按方案沿用）。判归属法=查引用面（是否被 X3 公共 Item prefab/Common 图集引用）

## 浮动礼包改随机组合包（07-22，进行中）
- ✅浮动 704 已改：CustomParameters=`5`(COMBINATION 3列宝箱)、PackList=`13031|13032|13033`(砍到19.99/49.99/99.99)、券做随机区间(80~208/200~520/400~1040)EV=480%=锚点400%×1.2。dev_festival `51301063`+build#2014 SUCCESS+本地服已reload
- ✅路由BUG修复(.cs未提交,随client)：`UIHelper.OpenChainPack` 原把 mode5 也丢礼包墙 UIRecharge→已拆出 COMBINATION→UICombinationPack(对齐OpenChainPackByGiftID)。详见 [[reference_x3_pack_open_mechanisms]]。⚠️通用修复非马戏专属
- ✅客户端4文件已提交推送（x3-project dev_festival `55a95ffbc78`）：prefab修复+免费机标红+礼包入口UIChainPackFullScreen+OpenChainPack路由修复。用户确认竖排列表"是这个意思"（UIChainPackFullScreen独立弹实测OK，先前的渲染风险已排除）
- 🔄用户最终要**全档竖排列表**(非3列/非商城,像开箱那种)。已改扭蛋机点击(`UIActvCircusGacha.ScoreTrack.cs:162`)直接 `WndMgr.Show<UIChainPackFullScreen>`(绕开逐档UIChainPack+商城)——**待用户实机验证**：UIChainPackFullScreen独立弹无先例,可能依赖商城宿主渲染不对;不对的后备=补独立弹支持/或加免费档改用UIChainPack。若显示对→清理**707**(原704,已让号)残留CustomParameters=5(现绕开无害但语义错,改回空)+落锚点。界面类映射全在 [[reference_x3_pack_open_mechanisms]]
- ✅锚点礼包5档已落地生效（07-22，dev_festival `d035cebe`+build#2021 SUCCESS+本地服reload OK）：PackType15 包 13034-13038(4.99/9.99/19.99/49.99/99.99,券+钻+VIP固定三件套ROI400%,Max留空显示干净,BuyCount0不限购)+ItemObtain type7(100413)+Item1212 ObtainID=100413。跟随机浮动礼包并存。构建脚本归档=skills\unity-prefab-tools\examples\circus_build_anchor_packs.py(克隆链式包改PackType11→15+建掉落包+ItemObtain双挂钩,可复跑范例)。⚠️热更本地服踩LFS坑=checkout ProtoGen后必 git lfs pull(见 [[workflow_x3_local_server_gm_telnet]])
- ✅浮动礼包钻/VIP改固定显示（07-22 `20859ec4`+#2024+reload OK）：13031/13032/13033的1002/2022行MaxNum清空(仅券1212保留随机区间)。热更带lfs pull无坑。"礼包不存在"重登自解(CreateChainGift随登录同步)
- 🔧本地服已清库重启（07-23）：之前 GM churn 把活动实例散到海域38(玩家海域4)+坏记录=死锁，清库重启清干净。⚠️重启时 --no-build 起服 preload 崩(InvalidProtocolBuffer,binary vs config schema 不匹配)→补重编 GameServer/MapServer.Hotfix 后 preload 过、双服起(telnet 26080/26081)。清库后号/活动全清空。**下一步**：用户登号(空库自动重建)→我 GMAdd 101027+101028→用户完整重登→测。测试期铁律见 [[workflow_x3_local_server_gm_telnet]](GM别churn+清库必重编)
- 🛑本地测试闪退（07-22，非功能bug）：点礼包入口闪退=链式gift null(GetGiftInfoByID→CloseSelf)。根因=GM重开活动是新实例无gift，且玩家只**重连(OnReconnected)没完整登录(OnPostInit)**→gift没建。修=让玩家**完整退账号重登**(不是重连)。GM别再churn实例(越弄越乱,会留GetPersistentData NullRef坏记录)。若完整重登后UIChainPackFullScreen仍闪→换UICombinationPack(三列,验证过能独立弹)。机制详见 [[workflow_x3_local_server_gm_telnet]]「GM重开活动礼包闪退」
- ⏳收尾待办：①704残留CustomParameters=5清理(扭蛋机已直弹UIChainPackFullScreen绕开,无害语义错) ②临时活动下线(转盘103006/开箱101516/福箱101026/寻宝103101等)

## ✅ 2026-07-28 体验修复批（5 项，配置已上线/代码待编译）
> 用户实机验收提的问题，一次收口。配置侧两笔已推 dev_festival：`bf94263d`(jolt#2190) + `f5ac83d1`(jolt#2192)，均本地 ExportTable exit0。

| # | 问题 | 根因 | 处置 |
|---|---|---|---|
| 1 | 底部积分条只在跨档时跳、档内不走 | 段内比例填充从没实现（`mRectFillPartial` 被无条件 SetActive(false)） | 代码，照抄 BP 口径，见 [[project-x3-circus-festival]] 在途条目 |
| 2 | 积分获取太难 | **奖励表逐档照抄 X2（满档同为 430 枚），门槛却抬高 2–9 倍**，前 3 档达 8–9.3× 而这几档两边都只发 3 枚 = 开局零反馈 | 配置：前 7 档改用 X2 占星2025 值 `5k/1w/3w/6w/10w/15w/20w`（用户拍板）。⚠️**遗留断层：第7档20万→第8档100万=5×跳**（X2 那里是 1.75×），待实玩后定 |
| 3 | 缺扭蛋币点抽奖不跳获取途径 | `Item.1211.ObtainID` 空一格 → 代码其实**已调** `ShowItemObtain`，但 `UIHelper.ItemObtain.cs:62` 判 ObtainID 空则降级成飘字 | 配置：`ObtainID=1211` + `ItemObtain.1211` 补 `JumpType=24/FunctionUnlockID=1022`（该行早存在指向 101028，三格空且从没被引用）。⚠️验证前提=**101028 必须真开着**，否则症状与未修一致 |
| 4 | 礼包弹窗标题空白 | 缺 `TXT_ChainPack_Name_707`（708 同病） | 配置：两个 key 都补齐，机制进 [[reference_x3_pack_open_mechanisms]] |
| 5 | 买完礼包再点没反应 | 三档买空 → `UICombinationPack` 开窗 8ms 内自关；入口按钮显隐只在 OnShown 刷一次 | 代码：订阅 `BuyGiftSuccess` 当场重刷入口 + 缺券跳转前先判买空。**判据用 `CheckChainPackFullyExhaustedForShop` 不是 `CheckBuyAllChainGift`**，详见礼包机制 memory |

| 6 | 券礼包只给券、币只能靠攒分 | — | **配置（用户 07-28 追加）**：`Reward 13031/13032/13033` 各加一行节日扭蛋币 1211，**数量与券 1212 等量**（80~208 / 200~520 / 400~1040，券保留随机故币跟随同区间）。`6d0025fa` jolt#2199 |
| 7 | 扭蛋币获取途径指向庆功宴活动 | 6 之后应改指礼包 | **配置**：新建 `ItemObtain 100512「节日扭蛋币-赠礼包」`(type7 快捷购买, Value=`13031\|13032\|13033`, 分组号537)；`Item.1211.ObtainID` 1211→100512。原 ItemObtain 1211（跳 101028）回孤儿态、行保留不删 |

> **闭环后的链路**：买券礼包 → 同时拿券和币 → 币不够点抽奖 → 跳回该礼包。
> 🪤 加 Reward 行踩到「同 RewardID 内 seq 必须连续」铁律：原块 15930160-168 后紧邻 13034，只剩 1 空位放不下 3 行 → 三组整体迁表尾 fresh 块 16001218-16001229。**已把这套做法固化成通用工具** `~\.claude\skills\x3-config-export\scripts\reward_group_migrate.py`（精确 max/原子写/写后双校验，以后别再现写脚本）。
> 🪤 `ItemObtain 100508`（券的快捷购买）描述字段是克隆残留「通过阅读技能书…」，与扭蛋券无关，**待清理**（新建 100512 时已避开没抄）。

- **顺带**：公会礼 `Pack.UnionGiftCfg` 对齐同价位主流（13031 203→204、13032 204→205；依据=全表分布 $19.99 挂204的384个包 vs 203的16个）。
- **用户已裁定不动**：券的随机区间（80~208/200~520/400~1040）**保留随机**，先试。
- **⏳待编译提交（3 个 .cs，主工作区未提交）**：`UIActvCircusGacha.cs`（买空后入口当场消失 + 缺券跳转前判买空）/ `UIActvCircusGacha.CircusScoreNodeItem.cs`（积分条段内填充）/ `UIActvCircusGacha.ScoreTrack.cs`（礼包入口改走 `OpenChainPack`，之前会话留下的，同一链路要一起提交；注释里的 704 已改正为 707）。⚠️**未经 Unity 编译验证**，新增调用 `GiftMeta.CheckChainPackFullyExhaustedForShop` / `TEventType.BuyGiftSuccess` 签名已对源码核过但没实机编译过。x3-project 有 commit message 格式钩子（须 `X3NEW-` 开头）。
- **客户端已整仓同步到 origin/dev_festival（07-28）**：31 文件更新零冲突，51 个在途改动全保留，本地未推送的地块图规格化提交也在。**扭蛋币获取途径「没生效」的真因就是本地没拉**（Item.bytes/ItemObtain.bytes 是旧的），不是配置错——查这类"配置改了游戏里没变"先比 `git hash-object <本地bytes>` vs `git rev-parse origin/<br>:<路径>`。
- **数值对比页（可复跑结论）**：`KB\产出-数值设计\X3_马戏节\_扭蛋机积分门槛_X2对比.html`（14 档双向对照＋等效达成量＋计分口径两表）。关键换算已钉死：`$1≈10充值积分`（PackPrice）×`任务1801 每积分150分` = **$1≈1500分**；且 **X3 计分表里没有"抽扭蛋得分"项**，积分全来自活动外通用消耗，玩扭蛋机本身不产分。

## ✅ 2026-07-29 庆功积分101028 定型为「扭蛋机旁挂数据源活动」（4 项配齐）
> 需求（用户口径）：**积分活动本身不显示，但扭蛋机的进度条要正常显示，且它是扭蛋机的副活动要一起开**。
> 🪤 中间走过一次弯路：先按"废弃防误开"把 `IsOn=0`（`3e3296cb`）→ **扭蛋机进度条整条消失** → 撤回（`60e1f576`）。根因=IsOn=0 清实例、宿主界面 `InitScoreTrack` 拿不到实例即隐藏整条轨道。通用范式已沉淀 GUI KB「第四种情况：旁挂数据源活动」+ [[reference_x3_timecycle]] IsOn=0 核对清单第⑤条。

| # | 目的 | 落点 | commit |
|---|---|---|---|
| ① | 数据在 | `IsOn=1`（**不能用 IsOn=0 藏它**） | `60e1f576` |
| ② | 不进活动集合界面 | 客户端 `ActivityConst.DataSourceOnlyActivityCfgIds`（新建常量）+ `UIActvMainPanel` 加排除；**按 cfgID 不按 ActvType**（type7 会误伤马戏酒馆 10071705） | ⏳未提交 |
| ③ | 不进活动日历 | `ActvOnline.Calendar 1→0`（`UIActvCalendar` 独立链路，最易漏） | `9baa7f90` |
| ④ | 随扭蛋机一起开 | `ActvGroupSchedule` 行 **10008**：Main=101027 → Sub=101028，Start=0/DurType=2，参数照抄 10006/10007 | `0e42b8ab` |

- 主城左侧入口第三条链路无需处理（`MainEntrance` 本就空）。
- **iGame 只需部署 101027**，101028 随主活动自动起（继承圈服+ArkActivityId）。
- ⏳**绑定④尚未实机验证**：`CreateGroupActivityIds` 只在主活动实例**创建那一刻**拉起子活动，已在跑的实例不追溯 → 验证须 `remove 101028` → `remove 101027` → `add 101027`，代价=扭蛋机数据+积分重置。
- **本地 3080 已就位（07-29）**：ProtoGen 取 robot 产物 `e2257325d99` + `git lfs pull` + `ReloadGameServer`(errCode=0)；`GMAdd 101028` 返 created(originSeaArea=1 与被测号同海域)=**双重验证配置真加载**（若 IsOn 没热更进去会报 1017001）。覆盖前的 76 个本地 ProtoGen 改动备份在 scratchpad/protogen_backup_20260729/。
- **✅客户端已推送（07-29，用户令）**：x3-project `dev_festival` @ **`3308eab98d5`**，走 sparse worktree cherry-pick 法（主工作区 50+ 在途改动零影响）。六处修复逐条 grep 核实全在（cherry-pick 只报 2 files/22 insertions 是因为其中 3 文件远端已有，**别被这个数字误导**，详见 [[reference_x3_project_repo]]）。
- 🔴**但未经 Unity 编译验证**（`Assembly-CSharp.dll` 停在 07-27、源码 07-29，一次都没编过）。已做静态核查并通过：`HashSet` 需的 `using System.Collections.Generic` 在 / `GiftMeta` 属 `namespace Logic` 且 UIActvCircusGacha.cs 已 `using Logic` / `ActivityConst` 在 UIActvMainPanel 已用过 8 次 / `Mathf`+`Vector2` 属已 using 的 UnityEngine。**静态核查≠编译通过**——出包若报 CS 错先看这四处。判编译状态法=比 `Library/ScriptAssemblies/Assembly-CSharp.dll` 与源码 mtime。
- ⏳**beta 验收前置**：配置侧已导表可直接验；**客户端改动要等 Jenkins 重新出包**才会进 beta 包，否则实机看到的仍是旧逻辑（易误判成"没修好"）。

## ✅ 2026-07-29 积分门槛断层修平（已闭环）
- T7 20万 → T8 100万 的 **5× 断层**（07-28 前7档回抄X2时留下的）已修：T8-T14 `100/125/160/200/250/310/400万` → **`50/100/150/200/260/330/400万`**，倍数链 2.5/2.0/1.5/1.33/1.30/1.27/1.21 单调递减。**逐档奖励与满档 430 枚一字未动**。
- dev_festival `47696ee0`（隔离 worktree `gdconfig-scoretier`/`feature/circus-score-tier` 推送，主仓在别的分支未碰）+ 本地 ExportTable exit0 + **jolt #2265 SUCCESS**。
- 触发礼包榜分(3w/20w)与排行 min_score 对应 T1下方/T7，**不受本次改动影响，无需同步缩放**。

## 🔴 2026-07-29 实际美刀 ROI 复算（用户"抽起来奇怪"→ 查实，方案待拍板未落表）
> 复算工具已固化 = `~\.claude\skills\x3-numerical-design\scripts\pool_roi.py`（`--demo` 即本案样例，别再现写脚本）。
> 汇率实锤 **1钻=$0.002**（锚点包 $4.99 给 2500 钻，钻石面值1:1）。ROI 基准 = 券设计锚 125钻/抽。

**查实的现状（实配非文档）**：付费池 82012 = 977.3钻/抽 = **782%** = $1.955；免费池 82011 = 127.4钻 = 102%；免付比 13.0%。端到端（含礼包钻+VIP）：锚点包 **10.8x**、浮动包 **17.1x**（参照深海锚点包设计口径 4.0x）。

**三个真问题**：
1. 🪤**「抽起来奇怪」根因＝冒险阅历 w200/352 命中 56.8%、占池EV 52.3%**——10连里平均5.7格是同一个道具。病根是 07-21「7行砍6行」把驯养经验整行删掉、权重并进冒险阅历（w100+w100→w200）：**EV 守恒做到了，命中分布没人验**。通用规律已沉淀 [[reference_x3_numerical_design_skill]]。
2. **两套券包套利差 1.8 倍**：锚点包 4.00 券/$ vs 浮动随机包期望 7.20 券/$（$0.25 vs $0.139/张），浮动包还白送等量币 → 单抽 ROI 7.82x vs 14.08x。买锚点包纯吃亏。
3. **浮动包实际 664% 不是记录在案的 480%**——07-22 定 480%（券做随机区间）后，07-28 追加等量扭蛋币那一步**没重算**：币按免费池 EV 折 18,346钻，$19.99 包实际 66,346钻。

**✅ 奖池重配平 v3.0 已落地（07-29，用户拍板 → dev_festival `d92b860c` + 本地 ExportTable exit0 + jolt #2277 SUCCESS）**
> 表=`ActvCircusGacha__ActvCircusGachaReward.tsv`（列：0=ID 1=Group 2=ItemID 3=备注 4=数量 5=权重 6=排序）。免费池组 82011 / 付费池组 82012。

> ⚠️ 中间经过 v3.0(8行) → **v3.1 用户拍板回 6 行**（`5efb5c88`+jolt **#2279**，**这是终态**）。回 6 行的动机＝**不为两个低占比槽去改 prefab 排版**；砍的是**神秘金属+内圈券**（用户拍板：先提砍罗盘被否，改砍金属）。

**终态 = v3.2**（gdconfig `f3139ed3`→dev_festival，jolt **#2280 SUCCESS**；导表产物 x3-project `a306cc6cbe8`）。⚠️**该提交随后被 zhangli 的真3-way merge `58ced4bc` 收敛进另一条线**，已跑双向丢行审计＝**我侧零差异、对方无独立改动被覆盖**（他那侧原是我更早的 v3.0，属正常版本推进，判读要点见 [[workflow_x3_merge_conflict_audit]] 假阳性0）；**已在更晚的 HEAD `9d52b5f9` 上复验两池内容仍为终态**。接手时别按 `f3139ed3` 找，直接读 `git show origin/dev_festival:tsv/ActvCircusGacha__ActvCircusGachaReward.tsv`。付费池 82012 总权重 **192**，EV **876.0钻 = 700.8%** = $1.752/抽，**按界面 Order 排**：

| Order | 行 | 终态内容 | 数量 | 权重 | 命中% |
|---|---|---|---|---|---|
| ① | 820108 | **新增** `1207马戏团门票`（寻宝外圈券） | ×1 | 5 | 2.6% |
| ② | 820101 | 1057 航海罗盘（保留） | ×3 | 12 | 6.3% |
| ③ | 820107 | 52003 万能传奇信物（唯一大奖） | ×1 | 10→**5** | 2.6% |
| ④ | 820102 | 19003 传奇技能书（保留） | ×1 | 30 | 15.6% |
| ⑤ | 820103 | `1008冒险阅历 → 1142驯养经验`（=**海妖经验**） | **17,000** | 200→**70** | 36.5% |
| ⑥ | 820104 | `52002万能史诗信物 → 11004通用加速1小时` | **×1** | 50→**70** | 36.5% |
| — | 820006 | 免费池 `1025啤酒 → 1008冒险阅历` | 10,000 | 50 | 18.9% |

- ⚠️**口径标注（07-31 全节日横比时发现）**：本段 700.8% 是**案内口径**（传奇书1000/1h加速800/门票2500）；换 [[reference_x3_roi_valuation]] 统一商店价（书500/加速400/门票750外圈口径）= **485%**。两口径都自洽但**跨模块对比必须统一用后者**（横比结论：扭蛋机485% > 福箱293% > 寻宝外圈132%端到端）。
- **付费池 782%→700.8%**；**免费池 102%→147.2%**（184.0钻，权重结构一格没动）；**免付比 21.0%** 回 X2 带中部；**最高单项命中率 56.8%→36.5%**（用户接受；6行下只剩经验/加速两个高频槽扛权重，压不下去，想再降=提传奇技能书权重30→40）。
- 🪤**加速档位换算连锁**（v3.2 用户嫌 `5m×8` 显示难看要求改 `1小时×1`）：1小时=800钻 vs 5m×8=533钻，**贵 1.5 倍**，直接换 ROI 顶到 776% → 靠**万能传奇信物权重 10→5**（大奖更稀有）腾出预算才回 700%。**换加速档位不是纯显示改动，必须重配平**；若想显示干净又不动别的，`30分钟×1`(400钻) 是零代价解。
- **两池各喂一条养成线**：付费池给海妖（1142驯养经验），免费池给英雄（1008冒险阅历）。付费池**已无船只养成材料**（神秘金属砍掉了）。
- 🪤 删行后 **Order 列（col6）会断号**（1,2,3,4,6,7），已手工补连续；删奖池行记得顺手修排序号。
- ~~v3.0 中间态（8行含内圈券+神秘金属，jolt#2277）已被 v3.1 覆盖，勿按它接手~~。
- 🆕**55101 神秘金属定价 = 500钻/个**（不是商店零售价 600）：三档"道具获取"包 $4.99→20 / $29.99→120 / $49.99→200 按 ROI 4x 反推**三档一致 500**，比单点商店价可靠。
- ✅**1207=2500钻 被远端 `ff4cd7ab` 反向验证**：该提交给寻宝阶梯三档补了钻10000+VIP点(2022×100)后，$19.99 包 = 10000 + 4×2500 + 100×200 = 40000钻 = 正好 **4.0x**，券价假设自洽。
- ✅**客户端零改动**：终态每池 6 行，正好填满 prefab 的 `Constraint=FixedColumnCount 3列 / cellSize 105 / 列表区488×210`（卡死 6 格）。**奖池行数是被 prefab 排版硬约束的，加行必配套改客户端**——这条是本轮回 6 行的唯一动机，接手改奖池前先记住。真要加行：改 3列×3行+缩 cell 到~70 / 列表加滚动，层级规律见 GUI KB「调格子大小的正确层级」（改 ItemMid 别改 Scale 节点）。

**🔄 寻宝103101 改造案进行中（07-31 用户定方向）**：①内圈抽空不锁→循环、第2轮起换降配池（建议新列 InnerLoopRewardGroup，死字段 InnerPoolCompleteTimes 接上=轮次上限）②大奖皮肤移外圈排行榜、纯展示不配属性。⚠️程序侧头号坑=GrandRewardItemID=0 时必须跳过大奖roll，否则第12抽白吞一星"中空奖"。**代码由程序处理（用户已喊人），数值/配置侧归我**；循环池推荐B档50%(13.5万钻/轮)，待拍板4点=纯展示语义/排行Top几/轮次上限/档位，方案+三档对比图=`KB\产出-数值设计\X3_马戏节\寻宝ROI模拟_20260731.html` §④⑤。

**🆕 寻宝103101 机制/ROI 全程模拟已做（07-31，别重跑）**：结论+复跑工具=`~\.claude\skills\x3-numerical-design\scripts\pioneer_city_sim.py`，报告=`KB\产出-数值设计\X3_马戏节\寻宝ROI模拟_20260731.md`，口径细节在 [[reference_x3_roi_valuation]] §四。三个机制硬事实（服务端 ActivityMeta.PioneerCity.cs 核过）：①内圈抽空=本期永久锁（:487），**无重置逻辑**；②配置字段 `InnerPoolCompleteTimes` 两端都没读=死字段（多轮内圈要加代码）；③**外圈不看内圈状态**→内圈毕业后彩虹星照掉但没处花=死货币，大R刷排行会攒废星（客诉隐患）。付费深度焊死在全清≈$445（寻宝累充AO100600 十档返200票+335罗盘把裸价$645压下来的）。

**🆕 内外圈券定价锚（跨案通用，别重挖）**：**「内外圈 gacha」＝马戏团寻宝 103101（ActvPioneerCity 骨架，拓荒者之城换皮），不是转盘也不是扭蛋机**——`外圈券=1207马戏团门票 / 内圈券=1208彩虹星`（AO103101.TopResource=1207|1208 实锤）。**1207 定价 = 2500钻 = $5/张**（寻宝门票阶梯 Pack81320 纯票档 $19.99 换 4 张实锤），是扭蛋券($0.25)的 **20 倍**——所以往任何奖池里投它必须极低权重，w5/312 已经吃掉 4.6% 的池EV。

## ✅ 2026-07-29 数值批（开箱奖池 / 回收 / 兑换商店，全部已推 dev_festival）
| # | 改动 | commit / jolt |
|---|---|---|
| 1 | 马戏福箱 `PackDailyRefresh 0→1`（礼包限购改每日刷新）。**换皮漏改**：全表 15 个 =1 的全是抽奖类，马戏福箱是同类里唯一的 0（元旦101513/情人节101514/春节101515/世界杯101516 全=1） | `6bf633d2` #2281 |
| 2 | 开箱奖池 116 新增 `11610`＝勋章×10、权重 **11111**（＝正好 10.000%；取 10000 会被稀释成 9.09%）。原 11602-11609 Order 各+1 | `9d52b5f9` #2282 |
| 3 | 回收补偿降为 1 钻：新建**马戏专属组 2100**＝钻石×1（⚠️不能改共享组 2022，它被 22 个活动跨节日共用）；扭蛋机同时补上漏配的 1212 高级扭蛋券 | `bd99d499` #2266 |
| 4 | 回收范围收敛（用户修正）：累充/抢购**不回收**、福箱回退 `1209,2022`(100钻)、仅扭蛋机走 2100(1钻) | `dca47e12` #2269 |
| 5 | 兑换商店新增「返场船只皮肤自选宝箱」`Item 1216`＝15000 勋章，自选池 Reward 组 `30996`（天马启航号15155 / 炽焰龙舟15135 两款永久） | `95d3166c` #2285 |

**🔑 开箱勋章产出有两个来源（算 ROI 必须都算，只看奖池会少一半）**：
`ActvCrafting.Product=1210` **每抽必得 1 个**（服务端 `ActivityMeta.Crafting.cs:41` `rewards={cfg.Product, req.num}`）＋奖池 116 随机档。
- 加档前 = 1 + 500×(500/100001) = **3.50 个/抽**
- 加档后 = 1 + 500×(500/111112) + 10×(11111/111112) = **4.25 个/抽**（+21.4%，其余道具概率被稀释至 90%）
- 门票性价比 **4 张/$**（锚点包 13025-13028＝20/80/200/400 张线性）→ 800 刀 = 3200 抽 = **13,600 勋章**；15000 勋章 ≈ 882 刀（自选溢价，用户定价）
- 参照系：组 1343 原最贵单品 1000 勋章、**全店买满 91,548**

**返场选品依据**＝投放史审计：15155/15135 都是活动限定且已投放过（30461-63 / 30351-53）；**商店在售的 6 款未选入**（感恩之翼/菌伞幽航/熊猫之旅/风暴王座/回声圣鳐/梦幻王蝶，在 `Shop__ShopItemCfg`），避免开一个绕过商店的口子。审计工具已固化＝`~\.claude\skills\x3-config-export\scripts\recycle_audit.py`。

⏳**待定**：①1212 是付费道具却只补 1 钻（补偿率<1%），有客诉风险 ②大富翁 `4200101`(钻石×100) 被 102801/102802/102803/102804 四活动共用（含常驻航海之路），要降补偿得另建组。

## 客户端调试遗留（07-21）
- ✅代码修复：`UIActvCircusGacha.cs RefreshButtons` 原只给付费机 SetAffordColor，补了免费机两行（mTFWTextFreeSingleNum/FreeMultiNum 按 coin>=ItemNum 标红）——.cs 改动在磁盘未提交，随 client 一起提
- ✅布局：左池 NormalItemRecycle y 373.6→385.6（青框比金框矮，右池不动）；两池几何本相同
- ✅礼包"全售罄"真因=**BuyCount=0 BUG 已修**（07-22，dev_festival `1689d0dc`，build#2010 SUCCESS，本地服已热更 Pack.bytes reloaded）：5档 13029-13033 的 Pack.BuyCount 0→1（0 使 purchaseNum>=0 恒真→ErrCodeGiftBuyLimit 永久售罄，干净号也中招）。**⚠️上一轮"非bug=测试号买满"是误判**，真因见 [[reference_x3_pack_open_mechanisms]]「链式礼包每档 BuyCount 必须≥1」。不用清号（当时没买成 purchaseNum=0，改完直接能买）
- 本地服 3080 在跑（telnet26080），活跃 uid=28240
- ⏳临时开了两个活动给用户看参考(3080/@28240,30天窗口),看完一起下线：远征大转盘 **103006**(残留奖励来源=其底部额外奖励条"阶段奖励-拉维耶") + 世界杯开箱 **101516**(链式高级礼包678界面参考,BuyCount=1正常)。`GMRemoveServerActivityByCfgId <id>` 下掉
- ✅高级券礼包5档内容=**已正确配好,新做的**(dev_festival commit `133bc438` 2026-07-20"扭蛋券常驻礼包5档 克隆深海锚点包 ROI4.0x")：13029($4.99)=券1212×20+钻1002×2500+VIP点2022×25(+公会礼物),逐档四件套符合数值定稿§4。**内容无需改。**
- 🔴🔴**纠错(07-22,两次乌龙作废)：Reward 表 `col0=ID(行唯一号) ≠ col1=RewardID(掉落包组号)`；Pack.Content 引用的是 col1 掉落包组，查内容必须按 col1 聚合**。我曾按 col0 查 13029→撞到无关老行(远征大转盘-拉维耶单道具)→误报"礼包内容是残留/四件套从没落过",全错。正确:按 col1=13029 聚合出券/钻/VIP 四件套(行id 15930154-56)。以后查任何礼包内容一律按 col1。
- ⏳唯一待办(纯显示,待用户定)：掉落行 MaxNum(col6)被填成=MinNum→客户端显示"20~20"区间;表规则"MaxNum留空=固定发MinNum",清空 col6 即显示干净"20"。5档所有掉落行同此(实际发放正确,仅显示难看)

## Jira 单（07-21）
- 需求树：需求 X3NEW-2243 / 服务器 2258 / 客户端 2259 / 配置 2261 / 测试 2257（配置/服务器/客户端都在林康名下，状态开发中）
- 开发BUG：X3NEW-2366 活动界面缺背景图（C级，经办林康）；建单规格见 [[Jira API Access]] 的 X3NEW 段

## 待办
1. 交程序（规格+prefab包+定稿；要程序回答扣费AND/OR、10连折扣、X3表结构）→ 2. 配置第二批（活动主体/奖池/礼包/排行，等程序定表结构）→ 3. 文案i18n（活动文案等key方案；道具名已有cn/en，16语待翻）→ 4. 美术5张（banner×2+活动图标+道具图标1211/1212）→ 5. 测试（触发链/积分尺度三处同缩放）

## 扭蛋机美术两处坑（2026-07-28 复查确认，接手先看）
- **✅界面缺背景 X3NEW-2366 已修（2026-07-28）**：新出专属底图 `img_Activity_circus_gacha_bg`（**1640×2560**，红金帐篷内景/四周金柱帷幕压边/中间留白给机器和按钮/下半沙地铺彩纸）→ 落 `Res\UI\Spirits\ActivityImg_Download\`（**背景大图放 _Download，图标才放 ActivityImg**）+ Display_Activity/Path_Activity 双注册 → **prefab 里那个死 guid 单点替换**（`fd139905…`→新 guid，全文件仅 1 处命中）。产物在 `KB\产出-本地化与美术\X3\马戏节\扭蛋机\`。**已推 x3-project dev_festival `f7e8800911c`**（sparse worktree 推送，未碰用户主工作区）。
- ~~原问题描述（留档）~~：**X3NEW-2366 表现**：prefab `UIActvCircusGacha.prefab` 的 `BG` 节点**现在 m_IsActive=1（已激活）**，但 `m_Sprite` 仍引用 guid `fd139905db61e7349b3559b7d867043f`，**该 guid 全工程搜不到**（`Res\UI\Spirits` 下所有 .meta 零命中）→ 底图整个是空的。~~旧记录写"BG 当前 inactive"已过时~~。
  - 修法＝出一张专属全屏底图（**1640×2560**）落库 → 把 prefab 第 ~58102 行那个 guid 换成新图 guid（YAML 单点替换，安全）。2026-07-28 已派图生成 `img_Activity_circus_gacha_bg`。
  - ⚠️配置层 `AO101027.ActvImg` 借的是**大富翁的** `DK_img_Activity_circus_monopoly_bg`（马戏全表无 `circus_gacha_bg`）；限时抢购 101029 连 icon 也借扭蛋机的。
- **活动图标 `img_Activity_circus_gacha_icon` 抠不了透明，别再试**：它 `transp 0.0% / border 0.0%`＝整张全不透明，但**根因不是"忘了抠"，而是这张图本身是满幅设计**——放射光芒底纹＋花纹边框画死在画面里，没有可分离的纯色背景，grfal `remove_background` 判不出前景/背景边界（两次调用均 success 但产物与原图 byte-identical）。**要修只能按活动图标规范重新生成一张透明底的**（124×136，对照 `circus_box_icon` 44.3%/97.7% 基准）。
