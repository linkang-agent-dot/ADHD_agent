---
name: project-x3-ship-siren-handbook
description: X3养成手册推广到船只(102703)+海妖(102704)两条养成线——配置链/TC/组137按钮坑/数值/本地化全接管入口
metadata:
  node_type: memory
  type: project
  originSessionId: 5437f395-handbook-promo
---

# X3 船只 + 海妖养成手册（英雄手册的推广扩展）

把 [[project-x3-hero-handbook]] 的 ActvType=27 登录购买制手册，推广到**船只**和**海妖**两条养成线。骨架完全克隆英雄手册双档结构（基础版+豪华版二选一互斥，豪华=基础×2）。2026-07 做，配置+客户端+美术+本地化已全上 dev。

## 两个活动（唯一入口）
- **船只手册 102703**（ContentID 2703）：基础礼包 220005 / 豪华 220006 / RewardGroup Group=102 / 30天奖励 Reward RewardID **4100301~4100330** / MainEntrance=**2**(有主屏HUD独立入口) / TimeController=**5921**(注册+**7天**30天循环,2026-07-16改,原2701注册+0天) / PlayerLv=7,99
  - 数值(2026-07-14 定稿·**保护液方案已撤**)：金属55101×180 + 木板55100×270 = 189,000钻 / **12.6x**；豪华×2。曾试混6个保护液(15000钻/个)+钻石10%,因保护液占比47.5%过高被否,回原方案。
- **海妖手册 102704**（ContentID 2704）：基础 220007 / 豪华 220008 / RewardGroup Group=137?→**见下** / MainEntrance=**空**(无独立主屏入口,靠海妖猎场框架/酒馆兜底) / TimeController=**5919**(注册+13天30天循环) / PlayerLv=14,99

## ★海妖手册开启时机（TC5919 的由来）
- 原用 TC2701=注册+**0天**→成熟服/满级号「第0天就开」(2026-07-15 330服暴露)。
- 修法=新建 **TC5919「海妖养成手册-注册13天开30天循环」**：克隆TC2701,仅 StartTime `00:00:00`→`13d 00:00:00`,保留30天循环(CycleType=1/ReOpenTime=30d)。→ 新号注册满13天才开。
- ⚠️ 手册**保留循环**(不是一次性)——它已移出组137,循环不影响任何HUD按钮。别再改回一次性。
- ~~船只手册 102703 不动(仍TC2701)~~ → **2026-07-16 船只改 D7，最终方案=程序兼容方案（活动克隆互斥，不是直改TC）**：
  - **第一版(直改TC，已被方案二取代但提交还在链上)**：新建 TC5921「船只养成手册-注册7天开30天循环」(克隆2701仅改StartTime=7d)，102703 直接指 5921。dev(246e4e7d)/qa(41b3acd2)/master(MR!113 merge 9b92210) 三分支都上了。
  - **终版(程序方案，防老玩家数据不兼容)**：**老 102703 TC改0 + BaseActvID[col52]=102703(自指)；新建 102705 整行克隆**(共用 ContentID 2703→ActvLoginPurchase/礼包220005/220006/奖励组102全不用克隆，ContentID 多活动共用有13组先例)，102705 挂 TC5921 + BaseActvID=102703(互斥老活动)；i18n 补 TXT_ActvOnline_ActvName/ActvDesc_102705(copy 102703 全语种)。dev=1e0bcde3 / qa=05cde969 已上；**master=MR!114 已建未合(用户要求等改动齐一起上)**。
  - 迁移范式=BP Type迁移同款(101102→102248 那批)：老活动 TC=0+BaseActvID自指、新活动 BaseActvID=老ID、双方 IsOn 都=1。老英雄手册 102701(TC=0,BaseActvID自指)→102702 也是此范式。**type27 TC=0 导表合法**(102701 先例+本地 ExportTable exit0 实证)。
  - ★**BaseActvID 互斥=「同值分组」不是「交叉指向」**(2026-07-16 差点配反)：服务端 `ActivityMeta.cs:441 otherCfg.BaseActvID == baseActvID`——**两行填同一个值才互斥**，交叉指向(103→105/105→103)两值不等=互斥失效双入口。组锚用哪个号无所谓(先例统一用老活动ID)。客户端对 BaseActvID 零逻辑引用(只有 proto 字段)，互斥纯服务端。
  - 三手册开启时机：英雄D0(TC2701) / 船只D7(TC5921,新102705) / 海妖D13(TC5919)。
- ⚠️传播姿势：**没走 dev→qa→master 全量合并**(当时dev有31个在途提交不能带上线)，走单提交传播——qa不受保护直接cherry-pick+push(tsv driver自动合并)；master受保护，把qa上的cherry-pick提交(父=qa tip=master祖先→MR diff纯净)push成 feature 分支 → API建MR → PUT /merge 自助合并(MR!113实证)。配方详见 [[x3-mr]](workflow_x3_protected_branch_mr)。
- ⚠️master 分支 Jenkins「X3导配置」当前**本来就在挂**：最后一步 bi_upload.py(仅master跑,BI数仓IAP上传) `get_reward_item_ids` 递归遇 None 崩(某Reward引用链有不存在的子RewardID)，#1893(15:59,早于本次改动)就是同错——**与手册改动无关**，配置门(consistency/schema gate)本身全过。修复归程序/导表工具侧。

## ★★海妖猎场(组137)主屏按钮「活动结束后不消失」——真因+修法
- 现象:三个框架活动(转盘106002/赠礼106003/争锋106004,都开服+13~21天有界)结束后,主屏「海妖猎场」组按钮还在,**重登也在**。
- **真因=测试服跑「收敛前」旧配置**:那份配置里 102704.GroupId=137,而手册滚动TC永不结束→被服务端一直当组137活跃成员推给客户端→按钮永不消失(重登照样在,因服务端数据里它真活跃)。
- **修法=移出组137**(dev 已改,提交 `59f87c19`「海妖手册收敛为单活动102704·去猎场组」,102704.GroupId 现为空)→**测试服重新部署最新dev即解决**,不用改代码。
- 关键机制:`RealGroupID => 服务端groupID!=0 ? 服务端groupID : 配置GroupId`(client `ActivityEx.cs:52`);服务端 `ActivityMeta.cs:1994` `actvGroupId=cfg.GroupId`(仅关联活动带groupID时覆盖)。手册GroupId空+非组关联→groupID=0→不进组。组137成员纯靠 ActvOnline.GroupId(非ActvGroupSchedule)。
- 组按钮显隐:`UIMainLeftPart.cs:509` `EnumerateActivityInfos(checkActvEndShowTime:true)` 组内任一成员在[start,actvEndShowTime]就显示;`actvEndShowTime=endTime+ConstCfg.ActvEndShowTime(24h,排名活动结束展示)`;隐藏靠 `GetGroupActivityEndTime`(裸endTime)定时器。
- ⚠️ 客户端 **MR!774**(feature/siren-hud-hide-fix,给组按钮补endShow隐藏定时器) **不是这个bug的解**——重登还在已证明是服务端/配置问题非客户端刷新时机。**建议关掉别合**(它只修「同次登录内endShow窗残留」的次要问题)。

## 可达性兜底(已确认无需改)
手册30天会活过框架季(框架8天),框架季后海妖猎场按钮消失。**活动无专属入口时会自动落到酒馆界面**(用户确认),买家仍能进手册领剩余日奖。无需再配独立入口。

## 本地化
10个手册key×16语已补齐并推dev(Text__Text.tsv):TXT_ActvOnline_ActvName/Desc_102703/102704 + TXT_Pack_Name_220005~220008 + Pack_Desc_220006/220008。译法沿用英雄手册(基础版·/豪华版·后缀,豪华Desc="含基础版全部奖励,每日奖励翻倍!")。船名=Ship Cultivation Handbook/艦船育成手帳;海妖=Siren Cultivation Handbook/セイレーン育成手帳。

## 待办
- [ ] 测试服重新部署最新dev,验:①新号第13天才开手册 ②框架活动结束后海妖猎场按钮消失。部署后还不消失才挖服务端活动关闭链路。
- [ ] MR!774 关闭(确认非此bug)。
- [ ] **船只D7当前态(2026-07-16 深夜)——master 回退中/dev·qa 兼容方案保留待定**：
  - **master**：✅回退已落地——MR!119(102703回TC2701+删TC5921)管理员已合(merge e7f481ef)，master 恢复船只手册D0原状。MR!114(兼容方案上master)继续挂着，将来要上时再合。**07-17 用户令：TC5921 单独加回 master——MR!121(feature/restore-tc5921-timecycle,4a17cfe9,仅TimeCycle表+1行=部分revert 0b59ecab,ActvOnline 102703不动,本地ExportTable exit0)已建等管理员合**；master tip 0be5a9fe 已有人修好 bi_upload 崩溃(get_reward_item_ids)。**另一笔独立回退 MR!120**(revert hehaofei 31f2f091 奇观首占奖励包修复,用户要求直提未做本地导表验证)等管理员合并。master 导表验证被用户叫停未跑。
  - **dev/qa**：兼容方案(102703 TC=0+BaseActvID自指 / 102705@TC5921+互斥)**保留(用户2026-07-16裁决)**；MR!114(兼容方案→master)继续挂着，等验证完+master回退落定再合。互斥配法有争议：用户/程序说"102703互斥应填102705"，但服务端两处代码(ActivityMeta.cs:441/ActivityMgr.cs:746)都是**同值分组**判定、现役先例(102701/102702→102701等)也是同值——交叉指向会互斥失效。若程序确认要换锚，两行都改成102705(功能等价)。
  - **服务端链路已全程验证通过**(330)：新配置生效+TC5921 D7触发+102705实例创建+互斥兼容(旧实例挡新活动)全对；测试号14548(建号时间被拨到07-26、旧实例已清、已有102705实例)。**没验完的只剩客户端展示**——用户Unity编辑器本地工程配置旧(落后16提交,工作区有脏ProtoGen挡pull)，用户对pull本地仓有顾虑暂停。
  - ⚠️330游戏时钟=2026-08-02/开服07-31。排查工具箱见[[reference_x3_kadmin_deploy]]。

## 关联
[[project-x3-hero-handbook]](骨架源·ActvType27双档机制/程序方案A) · [[reference-x3-actvtype-enum]](27=养成手册) · [[reference-x3-gdconfig-repo]] · [[workflow-x3-auto-jolt-export]]
