---
name: project-x3-voyage-permanent-remake
description: 航海之路常驻版换血——节日成就礼包版数值复刻为新活动102804接管老TC，102801转存量壳；分支feature/voyage-remake待合dev
metadata: 
  node_type: memory
  type: project
  originSessionId: 05b01d5d-257e-4342-b668-d5f9a867450f
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

## 未闭环（接手先看档案「待办/风险」）
待合 dev（MR 或自合）→ 测试服验：TC=0 老实例自然消亡(type28 未实测,BP 迁移先例)、互斥生效、珍珠贝组200代码定位发放、280003 dim.iap 主数据、珍宝罐16语手翻待精修。

关联：[[reference-x3-battlepass-type-migration]]（TC=0+互斥先例）· [[workflow_x3_multiagent_worktree]]（worktree/合并 SOP）
