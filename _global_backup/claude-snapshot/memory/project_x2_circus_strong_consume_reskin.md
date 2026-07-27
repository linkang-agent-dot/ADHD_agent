---
name: project-x2-circus-strong-consume-reskin
description: 马戏节·强消耗扭蛋机 X2→X3 搬运案——⚠️目标项目=X3(勿当X2内换皮)；唯一入口=X2换皮档案2026-07-08_马戏节
metadata: 
  node_type: memory
  type: project
  originSessionId: cd228f8f-4607-4cf7-8606-1ab0bf68ce0c
  modified: 2026-07-23T02:31:04.036Z
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
- **✅已裁定（07-21）：礼包入口不挂 UIBtnGift**——GiftEntry 已走 `SetActivityBaseInfo(goGiftEntry:)` 通用链路（UIActvCircusGacha.cs:131），ChainPackID=704（高级扭蛋券5档）已配，显隐/红点/弹窗全通；UIBtnGift 挂件=同逻辑另一套壳，重复。两套壳对比见 GUI KB §4.5

## ✅本地化已闭环（07-21）：Probability 文案=「高级奖励预览」
- dev_festival commit `a166767c`（16语言含ua，泄漏审计过），jolt build #2000 SUCCESS，worktree 已删。付费机顶部标题运行时显示「高级奖励预览」。
- ⚠️ TXT_ActvCircusGacha_* 这批 UI key **只存在 Text tsv**（无 CoderTID/配置表源），扫描不会回滚也不会自动补——直改 Text tsv 即可，但严格说应该补登 CoderTID（待办）。
- prefab 道具格结构：图标节点=`ItemMid/Scale/Icon`（代码 CircusGachaItem.cs 运行时按道具ID填图，改图去改配置不改prefab）；奖池列表排版=Content 的 GridLayoutGroup(100×100)；标题字色已调白字+深描边（355B82/986D2E）
- **✅已裁定（07-21）：格子全套=X3标准件，勿再纠结**——品质框指 X3 公共图集 `NewSprite/Common/frame/IconBox2_*`，发光 Fx_UI_JiangLiKeLingQu_Glow 与 X3 公共 `Common/Item/ItemBig|Mid|Small.prefab` 同源；编辑器里"X2感"来自占位假数据(Lv99头像/555数量)，运行时按X3道具ID填真图。X2 皮只在机器本体（机身/扭蛋球/按钮，按方案沿用）。判归属法=查引用面（是否被 X3 公共 Item prefab/Common 图集引用）

## 浮动礼包改随机组合包（07-22，进行中）
- ✅浮动 704 已改：CustomParameters=`5`(COMBINATION 3列宝箱)、PackList=`13031|13032|13033`(砍到19.99/49.99/99.99)、券做随机区间(80~208/200~520/400~1040)EV=480%=锚点400%×1.2。dev_festival `51301063`+build#2014 SUCCESS+本地服已reload
- ✅路由BUG修复(.cs未提交,随client)：`UIHelper.OpenChainPack` 原把 mode5 也丢礼包墙 UIRecharge→已拆出 COMBINATION→UICombinationPack(对齐OpenChainPackByGiftID)。详见 [[reference_x3_pack_open_mechanisms]]。⚠️通用修复非马戏专属
- ✅客户端4文件已提交推送（x3-project dev_festival `55a95ffbc78`）：prefab修复+免费机标红+礼包入口UIChainPackFullScreen+OpenChainPack路由修复。用户确认竖排列表"是这个意思"（UIChainPackFullScreen独立弹实测OK，先前的渲染风险已排除）
- 🔄用户最终要**全档竖排列表**(非3列/非商城,像开箱那种)。已改扭蛋机点击(`UIActvCircusGacha.ScoreTrack.cs:162`)直接 `WndMgr.Show<UIChainPackFullScreen>`(绕开逐档UIChainPack+商城)——**待用户实机验证**：UIChainPackFullScreen独立弹无先例,可能依赖商城宿主渲染不对;不对的后备=补独立弹支持/或加免费档改用UIChainPack。若显示对→清理704残留CustomParameters=5(现绕开无害但语义错,改回空)+落锚点。界面类映射全在 [[reference_x3_pack_open_mechanisms]]
- ✅锚点礼包5档已落地生效（07-22，dev_festival `d035cebe`+build#2021 SUCCESS+本地服reload OK）：PackType15 包 13034-13038(4.99/9.99/19.99/49.99/99.99,券+钻+VIP固定三件套ROI400%,Max留空显示干净,BuyCount0不限购)+ItemObtain type7(100413)+Item1212 ObtainID=100413。跟随机浮动礼包并存。构建脚本归档=skills\unity-prefab-tools\examples\circus_build_anchor_packs.py(克隆链式包改PackType11→15+建掉落包+ItemObtain双挂钩,可复跑范例)。⚠️热更本地服踩LFS坑=checkout ProtoGen后必 git lfs pull(见 [[workflow_x3_local_server_gm_telnet]])
- ✅浮动礼包钻/VIP改固定显示（07-22 `20859ec4`+#2024+reload OK）：13031/13032/13033的1002/2022行MaxNum清空(仅券1212保留随机区间)。热更带lfs pull无坑。"礼包不存在"重登自解(CreateChainGift随登录同步)
- 🔧本地服已清库重启（07-23）：之前 GM churn 把活动实例散到海域38(玩家海域4)+坏记录=死锁，清库重启清干净。⚠️重启时 --no-build 起服 preload 崩(InvalidProtocolBuffer,binary vs config schema 不匹配)→补重编 GameServer/MapServer.Hotfix 后 preload 过、双服起(telnet 26080/26081)。清库后号/活动全清空。**下一步**：用户登号(空库自动重建)→我 GMAdd 101027+101028→用户完整重登→测。测试期铁律见 [[workflow_x3_local_server_gm_telnet]](GM别churn+清库必重编)
- 🛑本地测试闪退（07-22，非功能bug）：点礼包入口闪退=链式gift null(GetGiftInfoByID→CloseSelf)。根因=GM重开活动是新实例无gift，且玩家只**重连(OnReconnected)没完整登录(OnPostInit)**→gift没建。修=让玩家**完整退账号重登**(不是重连)。GM别再churn实例(越弄越乱,会留GetPersistentData NullRef坏记录)。若完整重登后UIChainPackFullScreen仍闪→换UICombinationPack(三列,验证过能独立弹)。机制详见 [[workflow_x3_local_server_gm_telnet]]「GM重开活动礼包闪退」
- ⏳收尾待办：①704残留CustomParameters=5清理(扭蛋机已直弹UIChainPackFullScreen绕开,无害语义错) ②临时活动下线(转盘103006/开箱101516/福箱101026/寻宝103101等)

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
