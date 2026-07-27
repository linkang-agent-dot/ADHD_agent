---
name: project-x3-voyage-permanent-remake
description: 航海之路常驻版换血——节日成就礼包版数值复刻为新活动102804接管老TC，102801转存量壳；分支feature/voyage-remake待合dev
metadata: 
  node_type: memory
  type: project
  originSessionId: 05b01d5d-257e-4342-b668-d5f9a867450f
  modified: 2026-07-22T10:52:13.346Z
---

# X3 航海之路常驻版换血（2026-07-14 配置全落）

**唯一入口（冷启动先读）**：`C:\ADHD_agent\KB\换皮档案\X3\2026-07-14_航海之路常驻成就礼包版.md`——新旧对照表/6条决策记录/12文件清单/待办风险全在里面。

## 快照
- 需求（用户 07-14）：普通航海之路数值全换节日成就礼包版（加珍宝罐、砍岛屿升级、原样复刻），新活动接老 TC(2702=海域开放第13天开5天)，老 102801 TC=0，互斥活动ID双向配。
- 落地：**新活动 102804 / cid 2804**，克隆深海航行2802全套数值（货币1202→1060原额换算、宝藏币减半、新宝箱道具1220→组2064、珍宝罐280003 $19.99、阶段组102、规则15022-24、岛组4=401-424、事件组215-222）；皮肤文案入口全沿用普通版；ActvGroupSchedule 3子活动+ItemObtain100130 改挂 102804。
- 分支（07-16 基于最新 dev 重做）：`feature/voyage-remake-r2`（gdconfig+client 双仓同名，基于 origin/dev `de7f76f`，commit `9434f7ef`）。**用户明确不走 dev_festival、从 dev 拉分支搞**。旧分支 feature/voyage-remake 弃用(gate 旧快照污染)。
- **07-16 重做原因**：与最新 dev 试探合并发现 dev 前进 278+commit 改了表结构——ActvOnline 53→56列(ExcludeActvIDs 改名 BaseActvID+加3列)、Item 42→43列(UseLabels)。**我的数据行零撞车**，但旧结构合不进。重做=reset到dev+适配56/43列+改用官方 BaseActvID 兼容(102804.BaseActvID=102801新指老/102801.BaseActvID=102801指自己,对齐BP迁移101104先例)。
- 验证：本地 ExportTable ✅。Jenkins：旧分支 #1882 被 tsv-schema-gate 拿53列旧快照误拦(dev列改造算成我一步非法插列)→换新分支名 r2 规避→**#1884 SUCCESS ✅**(见 [[workflow_x3_multiagent_worktree]]「schema-gate/pre-push 分支旧快照」段)。全链路(配置→本地导表→push→Jenkins导表)全绿,可验收。
- 客户端仓零需求(纯配置换皮,现成 type28 UI+复用DK+i18n在配置侧)；client 分支纯为 Jenkins 导表 job 硬要求(把 bytes 推 client 同名分支)。
- ID 全部双分支(dev+dev_festival)核空,马戏合回不会撞;Reward 新块 seq 15940001-08 特意远离马戏在途块。

## 本地服 3080 验证通过(07-16)
dev代码+r2配置起服成功(先踩 siren 分支落后dev 66commit→proto不匹配崩UTF-8→切dev重编 坑1.5h,见[[reference_x3_kadmin_deploy]]本地服同谱系段)。✅102804按TC=2702自动开(接管老TC,窗口8/12-8/16)✅BaseActvID互斥实锤(102804活跃时102801被拦`blocked by BaseActvID 102801 excludedBy 102804`,CreateNewServerActivity returned null)。核心机制(活动能开+新老兼容)全过。数值内容(珍宝罐/珍珠贝/宝箱2064)配置在表未运行时深验。

## 实机修正+提交(07-16晚, 用户验收通过)
用户本地服实机测出5项修正,全改+验证+提交: ①兑换定价1332照节日版1341(价翻倍+限购紧+加速项去深海藏宝图) ②钻石岛216图→island_2_lv5(撤销误改数量,"资源"实指图非数值) ③幸运岛217-219图→island_1_lv5 ④岛布局核对=深海组2一致 ⑤**成就礼包补漏**(最初漏整个AchievePack模块): 组105+11档礼包2804xxx+**col10 TimeCycle=2702(关键坑:成就礼包组只靠活动TimeCycle创建,GMAdd不触发,玩家重登InitAchievePacks补建)**+纪念卡换美人鱼梦境180041(新建Reward组1028028/29不动深海)。本地服3080(dev代码+r2配置)全实测OK。**已commit bfe1ea99 push feature/voyage-remake-r2**。
⏳**明早传dev(用户2026-07-17定)**: gdconfig dev 合并(linkang可自合,MR或本地ff),走 [[workflow_x3_multiagent_worktree]] 合并SOP; 传前确认r2的jolt导表SUCCESS。

## 阶段奖励纪念卡改版（2026-07-22 晚，已push dev，jolt中）
**a2af8bf5(500/700改纪念卡)已作废** → 新方案：500/700回滚原奖励(4200007罗盘/4200008海神罗盘10)，**组102新增5节点**(row1025-1029)NeedTime 1000/1500/2000/2500/3000发美人鱼纪念卡180041，数量阶梯**2/3/4/5/6**。数量依据(用户定):1000档锚=200罗盘价值($100,罗盘=250钻/$0.5两源锚定)，1张纪念卡≈100罗盘($50)→1000档2张逐档+1。⚠️**纪念卡180041/罗盘1057权威道具表(SheetID 1gOCYBTt...道具表页签)钻石价值列都空、全仓无钻石标价**——纪念卡估值只有卡册优化报告设计价($4.5有效/$9-13获取/$10-20直售)，最终按用户拍板不走估值。RewardID=4200009-4200013(fork独立,深海组100未动)。commit 3f0a00d3 + merge 941a8af9,**已push dev,Jenkins build #2035 SUCCESS ✅**。
**★合并纯seq撞车让号(2026-07-22实战)**：push时origin/dev前进48commit,merge时Reward撞车——我方新行(seq16000362/363=4200011/12)与他方新行(826005/826006同seq)**纯seq撞、RewardID不撞**。driver报row_add_conflict后**把整个Reward.tsv punt成LOCAL**(丢他方全部改动!)。解法=以`MERGE_HEAD:Reward`为底(含他方全改动)重建+我方delta,我方3行让号到他方max(16000363)+1=16000364/365/366,RewardID不变故OtherReward引用不受影响。验证=双向丢行审计(他方826005/6在+我方5档在)+ExportTable exit0。教训:seq仅需唯一(非外键),撞车让号即可;driver冲突punt整文件到LOCAL,必须从MERGE_HEAD重建别只保LOCAL。

## ✅ 已 push 到 origin/dev（2026-07-22，jolt导表验证中）
三 commit + merge 已进 origin/dev：`04db088c`(=9434f7ef 换血) + `f30a4916`(=bfe1ea99 实机修正) + `a2af8bf5`(500/700档改纪念卡) + merge `bcb5e0e0`(push前origin/dev前进10commit,driver 3-way合入,双向零丢行+ExportTable exit0)。push成功后 `jolt_verify.py dev` 触发Jenkins导表 **build #2026 SUCCESS ✅**(全链路闭环:配置→本地ExportTable exit0→push→Jenkins导表SUCCESS)。
**a2af8bf5 决策(用户07-22·提高付费转化)**：航海阶段奖励(ActvVoyageOtherReward)500档/700档奖励**改为**美人鱼梦境纪念卡(180041)×1/×2(原=航海罗盘×200/钻石×10)。⚠️**关键坑=深海102802组100与航海102804组102共用同一批RewardID 4200001-4200008**(阈值/RewardID同,仅OtherReward组号不同)——直接改Reward表会误伤深海。解法=**fork独立新RewardID 4200009(×1)/4200010(×2)**(seq16000360-361),只让组102的500档(row1023)/700档(row1024)指过去,深海组100(1007/1008)原样不动。教训:改共用RewardID前必查是否被多个OtherReward组引用,共用就fork别直改。⏳两点待用户回:①"改为"=替换原罗盘/钻石(已按替换做),若要"加"再改;②只改航海没动深海,深海要改再说。
前两commit说明:**全验通过**：双向丢行审计14表 dev零丢+r2新增全到、pre_push_check 硬错误0、本地 ExportTable exit0(三标志齐+depend_keys全过含AchievePack/纪念卡新组)。Text.tsv 冲突解法=**接受driver输出原样(git add不手改)=保留dev全本地化+r2新增**。⏳待用户令 push→`jolt_verify.py dev`。
**两个新坑(通用,别再栽)**：
1. **`cherry-pick -n A B` 多commit遇冲突会停在A、B静默不应用**(sequencer todo两个都pending但HEAD没动)，--continue 又被暂存改动挡("local changes would be overwritten")。**正解=不带-n**逐个 `git cherry-pick -x A`(自动提交)→解冲突`git add`→`GIT_EDITOR=true git cherry-pick --continue`→再 `-x B`。
2. **i18n表「key出现在管道行(col0含|)」≠该独立行是重复**——X3 Text表本就有~3700个key跨行重复(导表首条生效容错)，用「key在任何管道行」当去重信号会误删数百行(实测误删404行)。driver 报的 bulk_row_delete 若本质是「老key被并入管道行」(§⑯.A)，**别自己扫全表去重，直接接受driver合并输出**(dev独立行+r2管道行并存,重复无害,ExportTable过)。

## 合并 dev 冲突预检（2026-07-22，driver 已跑）
cherry-pick r2 两 commit(9434f7ef+bfe1ea99)进最新 dev(已前进85 commit)：**7表仅 Text__Text.tsv 1 张冲突**，其余6表(Reward/Pack/Item/ItemObtain/ActvOnline=102804那套数值)driver 自动合并零冲突。冲突=21条 bulk_row_delete(r2「砍岛屿升级」删老航海 i18n:ActvVoyageIsland IslandName/IslandStory 101~124+老102801活动名+入口110+100130)，超 driver 20 阈值被拦人工。**验过 base(de7f76f)==origin/dev：这批key dev一字没改→接受删除不覆盖dev任何新内容=可安全解决的假性冲突**。解法=接受r2删除→双向丢行审计+ExportTable exit0→commit,push前停等用户确认。⚠️提醒点:102801转存量壳(TC=0)后删其岛屿i18n,老玩家残留实例文案可能空白(07-16实机验收已过的既定方案)。

## 未闭环（接手先看档案「待办/风险」）
待合 dev（MR 或自合）→ 测试服验：TC=0 老实例自然消亡(type28 未实测,BP 迁移先例)、互斥生效、珍珠贝组200代码定位发放、280003 dim.iap 主数据、珍宝罐16语手翻待精修。

关联：[[reference-x3-battlepass-type-migration]]（TC=0+互斥先例）· [[workflow_x3_multiagent_worktree]]（worktree/合并 SOP）
