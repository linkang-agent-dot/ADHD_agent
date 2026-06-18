---
title: X3 活动代码架构 · customParam 驱动「可热部署活动」决策模板
kind: 方法论
domain: 代码架构/服务端
proj: X3
created: 2026-06-18
source: 逆向 zhangli(大哥) 的 X3NEW-1432「每日比赛竞猜代码重构」commit f6e2d08768a
范例实体: 世界杯竞猜 ActvType=64 (ActvOnline 102911~102982, 76个活动)
原始设计文档: C:\x3-project\docs\plans\2026-06-18-worldcup-guess-customparam-refactor-design.md
---

# X3「customParam 驱动可热部署活动」代码决策模板

> **一句话**：让活动的**可变运营参数**（如"哪两个礼包对阵"）通过 **iGame 后台 customParam(JSON)** 在部署时传入，服务端读 customParam 建活动数据 —— 换参数 = 改后台重部署，**零代码 / 零热更 / 零客户端打包**。
>
> 用它替代"参数写死在配表(ActvPack/ActvXxx)→改配表→服务端热更"的老套路。**何时套用**：活动结构固定、只有少量参数按场次/期次变（对阵、礼包ID、目标值、奖池ID…），且运营需要高频换。

---

## 0. 这套模式解决什么问题（动机）

老套路（以竞猜为例）的痛点：
1. 换参数仍要"改配表 + 服务端热更"，和"客户端零打包"不对称；
2. **借用语义不符的现成数据结构**（竞猜硬塞进"进度礼包 progressPackData"的 `day=0/day=1`）→ 语义模糊、易踩坑；
3. 配表得**为每场/每期维护一行**（竞猜 76 行 ActvPack）→ 配置层冗余；
4. 现成结构带着**本玩法不需要的逻辑**（进度礼包的"最终奖判定"对竞猜是死代码）。

customParam 模式把"可变参数"从配表搬到 iGame 部署参数，从根上消除上面 4 条。

---

## 1. 端到端数据流（照抄这条链）

```
iGame 后台 deploy 活动 102911
  customParam = {"packIdA":894071,"packIdB":894211}
        │
        ▼  (deploy handler 通用、不解析)
ActivityMgr.Ark.cs  OnDeployArkActivityReq
  → CreateNewServerActivity(..., arkCustomParam: activityData.customParam)
        │
        ▼  ActivityMgr.cs:797/849
  写入 server-side entity:  ServerActivityBasicData.arkCustomParam (原始JSON string持久化, 跨重启可复读)
        │
        ▼  活动激活/登录/重载时
ActivityWorldCupGuessCondition.OnAddActivity   ← 专属入口(按 TriggerType 路由)
  serverActivity.Data.arkCustomParam
  → JsonConvert.DeserializeObject<WorldCupGuessCustomParam>   (反序列化在 condition 层)
  → 校验 packIdA/B>0
  → GiftMeta.CreateActivityWorldCupGuess(packA, packB, endTime, activityItem.worldCupGuessData)
        │
        ▼  GiftMeta.Activity.cs
  CPack.I(pack) 校验 → IdGenerater 生成 giftId → 填 WorldCupGuessData.packA/packB(GuessPackInfo{packCfgId,giftId})
  → 复用 CreateActivityPack(giftId, packId, endTime) 底层 gift 原语
        │
        ▼  下发 ActivityData.worldCupGuessData (proto tag 62)
客户端 UIActvWorldCupGuess.RefreshView
  → ActivityMeta.GetWorldCupGuessData(activityId)  (partial 查询)
  → mPackList[0]=packA.packCfgId, mPackList[1]=packB.packCfgId
  → 队徽/队名/横幅/奖励 全从 Pack 配置在 UI 层渲染
```

---

## 2. 九条代码决策（可复用到任何同类活动）

> 每条都标了**为什么**和**被否决方案**——接手新功能时按这九条逐条做判断。

| # | 决策 | 为什么 / 被否决方案 |
|---|------|---------------------|
| **D1** | **专属 Condition 入口，绝不动通用流程** | 新玩法走自己的 `ActivityXxxCondition`；通用入口(如 `ActivityProgressPackCondition`)、其 proto、`CreateActivityProgressPack`、最终奖逻辑、相关错误码、旧配表类**全部物理保留不动**。→ 回滚=rollback MR 即可，旧链路完整可用；不连累别的 ActvType。 |
| **D2** | **customParam payload 取最薄** | 只传**数据本质**(两个 packId)。❌否决：传国家 code `{teamA:"BRA"}`(把命名约定刻进代码、扩国不便)；❌传 matchupId(又回到改配表)。"队伍"等业务概念**不进数据层**，由 UI 从 Pack 配置渲染。 |
| **D3** | **不复用现成 customParam DTO，新建独立 DTO** | 别塞进 KvK 的 `ActivityCustomParamsData`(含无关 mapServerID)。新建 `WorldCupGuessCustomParam{long packIdA;long packIdB;}`，字段干净。 |
| **D4** | **proto 新 tag 顺序追加，绝不复用/改旧 tag** | 旧 tag(如 progressPackData=35)永久保留。新增前**先查当前最大 tag**(竞猜初版误以为 36 空闲，实际 36 被 donateData 占，最终用 62)。改/复用旧 tag = 上下游全链路兼容灾难。 |
| **D5** | **proto 字段名贴数据本质，不假装服务端懂业务** | 字段叫 `packA/packB` 不叫 `teamA/teamB`——服务端只认 packId。业务语义(队伍)留 UI 层。 |
| **D6** | **customParam 反序列化+校验放 Condition 层** | ❌不放 deploy handler(它是所有 ActvType 共享的，不该知道每种 customParam 格式)。`OnAddActivity` 自己 Deserialize + `CPack.I` 校验；失败打 Error 日志并 return(活动数据建不起来)。 |
| **D7** | **原始 customParam JSON 持久化到 server-side entity Data** | 写进 `ServerActivityBasicData.arkCustomParam`，**不放 proto ActivityData**(客户端不需要看原始JSON)。→ `OnLogin/OnReload` 能复读，跨重启稳定。 |
| **D8** | **复用底层原语，挂专属数据结构** | gift 创建复用现成 `CreateActivityPack(giftId,packId,endTime)`(不重造轮子)，但数据挂在**专属** `WorldCupGuessData` 而非借用 progressPackData。"复用机制 + 专属语义"。 |
| **D9** | **配套 GM 命令本地复现 deploy 链路** | 加 `[GMHandler] GMDeployWorldCupGuess(cfgId,packA,packB,durationSec)`：本地 `JsonConvert.SerializeObject(new{packIdA,packIdB})` → 走同一条 `CreateNewServerActivity(arkCustomParam:...)`。无需 iGame 即可端到端验收。 |

附加工程惯例：
- **共享 hotfix 代码用 `#if _SERVERLOGIC_` / `#if _CLIENTLOGIC_` 分割**(同一个 Condition 文件，服务端段管建数据/删gift，客户端段管 GetActivityUIType/预览)。
- **单服活动** `ActvOnline.CrossServerRank=null` → 只改 `GameServer.Hotfix`+客户端，`CenterServer` 完全不动。

---

## 3. 新增一个此类活动的「文件改动 checklist」（copy-and-swap 骨架）

把下面"竞猜"换成你的新玩法名(Xxx)，逐文件做：

| 步 | 文件 | 改动 |
|---|------|------|
| 1 | `docs/plans/{日期}-xxx-design.md` | **先写设计文档**(套本模板九决策) |
| 2 | `client/Assets/TFWConfig/Protobuf/activity.proto` | 加 `message XxxData{...}` + `ActivityData` 末尾追加新 tag(先查最大 tag!) → 跑 proto 生成同步 `Protos/activity.cs` + `msgid.def` |
| 3 | `client/Assets/Scripts/CSShared/.../ArkModel.Activity.cs` | 加 `class XxxCustomParam{...}` DTO |
| 4 | `server/GameServer/Modules/ActivityMgr.Ark.cs` | deploy handler 调 `CreateNewServerActivity` 处透传 `arkCustomParam: activityData.customParam`(若已有通用透传则免改) |
| 5 | `server/GameServer.Hotfix/PlayerMeta/Gift/GiftMeta.Activity.cs` | 加 `CreateActivityXxx(...args, long endTime, XxxData data)`：校验 CPack→IdGenerater→填 data→复用底层原语 |
| 6 | `server/GameServer.Hotfix/PlayerMeta/Activity/ActivityMeta.Xxx.cs`【新文件】 | `partial class ActivityMeta` + `GetXxxData(activityId)=>GetActivityData(activityId)?.xxxData;` |
| 7 | `client/Assets/Scripts/Entity/Player/Activity/ActivityMeta.Xxx.cs`【新文件】 | 客户端同名 partial(namespace Logic) |
| 8 | `client/.../ActivityTriggerConditions/ActivityXxxCondition.cs`【新文件】 | `[ActivityTriggerCondition(TRIGGER_TYPE_XXX)]`；`_SERVERLOGIC_` 段 OnAddActivity(读customParam→反序列化→校验→CreateActivityXxx) + OnRemoveActivity(RemoveGift)；`_CLIENTLOGIC_` 段 GetActivityUIType |
| 9 | `client/Assets/Scripts/UI/Actv/UIActvXxx.cs` | RefreshView 读 `GetXxxData` 而非配表 |
| 10 | `server/GameServer/Modules/ActivityMgr.Ark.cs` | 加 `[GMHandler] GMDeployXxx(...)` 本地复现 |
| 11 | 验收 | `dotnet build server.sln` 全绿 + Unity 编译过 + GM 命令端到端 + **静态扫描旧共享链路仍在(没误删)** |

---

## 4. 范例实体（世界杯竞猜 ActvType=64，落地坐标）

- **proto**：`activity.proto:315` `GuessPackInfo{packCfgId,giftId}` / `:321` `WorldCupGuessData{packA,packB}` / `:501` `ActivityData.worldCupGuessData = 62`(progressPackData=35 不动)
- **DTO**：`ArkModel.Activity.cs:153` `WorldCupGuessCustomParam{packIdA,packIdB}`
- **Condition**：`CSSharedHotfix/.../ActivityWorldCupGuessCondition.cs`(124行，全文范本)
- **GiftMeta**：`GiftMeta.Activity.cs:165` `CreateActivityWorldCupGuess`
- **Meta partial**：server `GameServer.Hotfix/PlayerMeta/Activity/ActivityMeta.WorldCupGuess.cs` + client `Entity/Player/Activity/ActivityMeta.WorldCupGuess.cs`
- **UI**：`UIActvWorldCupGuess.cs:80` RefreshView
- **GM**：`ActivityMgr.Ark.cs:380` `GMDeployWorldCupGuess(cfgId,packIdA,packIdB,durationSec)`
- **持久化**：`ServerActivityBasicData.cs:29 arkCustomParam` ←写← `ActivityMgr.cs:797/849 CreateNewServerActivity`
- **部署参数**：`{"packIdA":894071,"packIdB":894211}`(=BRA vs GER)；换对阵=改这串重部署
- **互斥**：两包同时可买，"已锁定"是**客户端表现**(买一侧隐藏另一侧购买按钮防对冲)，服务端只靠 `Pack.BuyCount` 限购、不做互斥
- **无最终奖**：运营从 BI 筛"两包都买"玩家统一邮件发奖，服务端不判定(proto 无 finalReward 字段)

---

## 5. 陷阱 & 回滚

**陷阱**：
1. **proto tag 必须先查最大值再追加**——别信设计稿里的空闲假设(竞猜踩过 36→实占→改 62)。
2. **客户端版本必须同步上线**：tag 是新的，旧客户端忽略该字段→UI 拿不到数据显示空。`VersionControl.cs` 版本号要联动。
3. **iGame customParam 错填**(894071→894701)：靠 `CPack.I` 校验在 deploy 时回滚，运营收失败回执；务必保留校验。
4. **旧配表数据保留不读有误用风险**(76行 ActvPack 还在但已被绕开)：建议加备注"已被 customParam 替代，勿改"。

**回滚**：rollback MR → 旧 `progressPackData` 链路(tag 35)完整保留立即可用；已部署活动需 iGame 重新 deploy 一次让旧链路重建数据。

---

## 6. 复盘：我们当时为什么没做到这套设计（约束框定教训）

> 这套 customParam 设计不是大哥才想得到——是**第一版（复用 progressPackData 的 hack）做的人（含本 AI）把一条约束抬成了死墙，于是绕过去而不是穿过去**。记下来，避免下次再漏。

**当时第一版怎么做的**：要让"换对阵可热更"，复用已有的 `progressPackData` proto 字段，用 `day=0/day=1` 硬塞两队。换对阵纯服务端热更、**零客户端改动**。

**为什么没做成 customParam 版**——不是 proto 技术卡住（proto 改动是机械活，生成工具自动出 250 行 activity.cs），而是**自设了一堵硬墙**：

> "新增 proto 字段 = 走客户端打包（proto 是客户端 bundle、热更只服务端）= **不可接受**"

在"绝不能动客户端"这个前提下，复用 progressPackData 是局部最优。

**大哥怎么穿过去的**：他没把"新增 proto"当死墙，而是识别出它只是**一次性成本**——付一次客户端打包上线专属 proto，换来永久干净架构 + 未来所有对阵切换照样零打包。

**三条可复用教训**：
1. **分清"永久红线"还是"一次性成本"**：遇到"绝不能动 X"，先问——动 X 是**每次都要付**，还是**付一次就翻篇**？一次性成本常常付一次更划算（一次客户端打包 vs 永久 hack 债）。
2. **警惕红线范围蔓延**：合理目标"换对阵时零客户端打包"被无意识扩成绝对禁令"任何时候都不准动客户端"，然后为守这条自抬的禁令接受 hack。定期回看自己的红线是不是被悄悄放大了。
3. **hack ≠ 错，长期当正解才错**：当下没发版窗口/只能先发车时，复用 progressPackData 是合理的"先上线"动作（大哥的设计文档也把第一版客户端改动 `4bd6029` 当成前置台阶）。但要留 TODO：有窗口了做对。

（同款教训另存 memory `[[feedback_constraint_framing_onetime_cost]]` 供自动召回。）

---

## 7. 接手提示

- 想加同类活动 → 看 §3 checklist + §2 九决策。
- 想懂竞猜具体实现 → 看 §4 坐标 + 大哥原始设计文档(frontmatter 路径)。
- 配置侧(礼包池 894CCT/累充白名单/ActvPack)在 gdconfig，见 memory `[[project_x3_worldcup_activity]]`(世界杯唯一入口) + `[[reference_x3_recharge_isolation]]`。
- 本模式是**代码架构层**沉淀；GUI 拼界面另见 `KB\方法论\X3客户端GUI知识.md`。
