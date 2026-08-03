---
name: reference_x3_actvgroupschedule_binding
description: X3 子活动要不要单独提 iGame 单的唯一判据——查 ActvGroupSchedule 有无绑定行；ActvGroupSchedule 管激活不只管 HUD 分组（推翻深海期间的错结论）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 549921cb-db7d-4567-bdb3-e36bd4b4e0c7
  modified: 2026-07-30T10:39:01.239Z
---

X3 部署活动时判断**某个子活动要不要单独提 iGame 单**的唯一判据。2026-07-30 马戏节案用代码+配置双向证实，**推翻了深海期间记下的错结论**。

## 判据（开工前查这个，别凭印象）
查 `tsv/ActvOnline__ActvGroupSchedule.tsv` 有没有该子活动的行、且 `IsOn=1`：
- **有 → 不要单独提单**（宿主自动创建实例，窗口自动继承）。提了会**撞出两个实例**。
- **没有 → 必须单独提单**。

## 机制（代码锚点）
`server\GameServer.Hotfix\ServerActivityMeta\ServerActivityBasicMeta.cs` 的 `CreateGroupActivityIds()`（约 line 45-85）：
宿主 ServerActivity 启动时，按 `CActvGroupSchedule.Instance.ContentIndexIds[Master.CfgId]` 取出所有绑定行，逐个
`activityMgr.CreateNewServerActivity(actvCfgId, Master.OriginSeaArea, actvStartTime, actvEndTime, arkActivityId: Master.ArkActivityId)`。
- 时间：`actvStartTime = 宿主StartTime + cfg.StartTime`（StartTime 是**相对宿主的偏移**）；
  `DurationType=2` ⇒ `actvEndTime = 宿主EndTime`（同始终）；`=1` ⇒ `actvStartTime + cfg.DurationTime`
- **子活动继承宿主的 `OriginSeaArea` 和 `ArkActivityId`** ⇒ **宿主跨服，子活动也是跨服实例**
- 表结构：`ID / IsOn / MainActvID(宿主) / 主活动(备注) / ActvID(子) / 活动名 / StartTime / DurationType / DurationTime`

## 为什么深海得出了相反结论（别再被它误导）
深海 memory 里曾记「ActvGroupSchedule 只管 HUD 分组不管激活，拼图 101828 必须单独提单」——**错的**。
真相：深海上线时 GroupSchedule 里那条绑定行（`10005`：102802 深海航行 → 101828 美人鱼的梦境）**还没配**
（行 ID 排在推币机 `10717` 之后＝后插入的），所以子活动没被自动带起，只能手动提单，于是把"当时的现象"记成了"机制"。
现在 10005 已存在且 IsOn=1，同样的活动**不再需要提单**。

## 已知绑定关系（2026-07-30 实查 origin/dev_festival）
| GS 行 | 宿主 | 子活动 | 时长继承 |
|---|---|---|---|
| 10005 | 102802 深海航行 | 101828 美人鱼的梦境（拼图） | Type2 同始终 |
| 10006 | 102803 马戏巡游（大富翁） | 101829 小丑的梦境（拼图） | Type2 同始终 |
| 10007 | 103101 马戏团寻宝（拓荒者之城） | 103102 寻宝门票特惠（门票阶梯） | Type2 同始终 |
| 10008 | 101027 马戏扭蛋机 | 101028 马戏庆功宴（积分） | Type2 同始终 |

⇒ 马戏节这三对（10006/10007/10008）**都不用单独提单**。其中 **101028 备注写的【本期不上线·勿部署】真意＝"不用你去部署"**，
它是扭蛋机的后台返利层（抽奖攒积分→到档回吐扭蛋币 1211，T1–T14 共 14 档），不出 UI，**IsOn=1 必须保留**（改 0 配置不导入、返利链直接断）。

## ⚠️ 区分两种"窗口跟随"
- **有绑定行** → 自动创建 + 自动继承窗口 ⇒ **不提单**
- **只是人为排了同一个窗口**（无绑定行）⇒ **照旧各自提单**。马戏节例：巡游 BP 102251 / 巡游集市 101344 窗口跟大富翁一致，但没有绑定行，**都要自己提**。

相关：[[project_x3_deepsea_festival]] · [[project_x3_circus_festival]] · [[reference_x3_actvonline_serverlist_merged_gate]]

## ★上一层判据：这个活动到底需不需要 iGame 部署（2026-07-30 马戏节事故补充）
上面讲的是"子活动"，但**先要判活动本身属于哪一类**——判错会漏出线上事故（本案实证）：

| 类型 | 机制 | 要不要提 iGame 单 |
|---|---|---|
| **服务器活动** | 靠 iGame 建 ServerActivity 实例才激活 | **要** |
| **玩家活动（TC 驱动）** | 玩家登录时按 `TimeCycle` 窗口直接判开关（`ActivityMeta.cs:83-89` 登录批量兜底 → `CheckActivityTimeCycleIsOpen`:1461），**TC 窗口一开就全服可见** | **不要**，提了会开出**第二个重复实例**（两个页签/两份进度） |

- **判别**：看该 ActvType 是否落 `PlayerActivityIds`（`Tools/table_exporter/actvonline_def.py:516` 附近的分类）。**Type=18（拼图）就是玩家活动**。
- ⚠️**玩家活动的两个致命特性**：① **不受你排的 iGame 窗口控制**，只认 TC ② `Open/CloseServerList` 为空 ⇒ **开在全部服**，不受部署名单限制。
- ⚠️**别把 TC 当"占位"**：本案 `TC 1831` 备注写着"宽窗占位(实际开关靠iGame部署)"——**这句备注是错的**，它是真实激活器。`TriggerType=1 + StartTime 2026-07-01 + Duration 89d` ⇒ 7/1 起就是打开状态。
- **想改成纯部署驱动（TC=0）不一定可行**：导表会校验 `TimeController≠0`，除非该 ActvType 在 `SKIP_TIMECYCLE_CHECK_ACTIVITY_TYPE` 白名单或活动在 `ScheduleActvIDS` 里（`PostProcessData.py:1684/1817`）。Type=18 两者都不在 ⇒ 只能改 TC 窗口，不能置 0。

### ★占位 TC 必须填未来时间（本案真正的引爆点）
被导表校验逼着必须填 TC、但排期还没定时，**占位值一律填未来的远期时间**（如次年 01-01 起），绝不能填当前或过去的日期。同样是"占位"，两种写法的后果完全不同：
- 填未来 ⇒ 配置进发布分支+导表成功也不会开，等排期定了再收窄，安全。
- 填过去（本案填 `2026-07-01`，配的时候已是 7 月）⇒ **等于配了一个"立即生效"的开关**，只要配置进 master 并导表，当场全服打开。
配套两条：① **排期未定的活动，带激活器的配置别急着合进发布分支**（本案 07-28 合 master 时档期还没定，等于把雷埋进发布线，只等一次导表就炸）② **备注里写的"实际开关靠 iGame"这类断言不可信**，看到就去验该 ActvType 到底是玩家活动还是服务器活动——本案就是这句备注把后面所有人带偏。

### ★活动级别全貌表（判"要不要提单 / 能不能 GM 下 / 是不是跨服"的唯一依据）
定义在 `client/Assets/Scripts/CSShared/Common/Const/ActivityConst.cs`（**CSShared，服务端也用同一份**）。
`AllServerActivityTypes` 在静态构造函数里 `UnionWith` 四个集合拼出来（定义处是空 HashSet，**别只看定义处就下结论**）：

| 集合 | 成员（2026-07-30 实查） |
|---|---|
| `SeaAreaActivityTypes`(14) | SINGLE_STAGE_RANK · MULTI_STAGE_RANK · EXERCISE · UNION_SINGLE_RANK · CRAFTING · FISHING · VOYAGE · RANK_POWER_CAP · HERO_SECRET · HERO_SKILL_SELL · HERO_SKILL_TRY_OUT · DWARF · RED_PACK · WONDER_SCORE |
| `SingleServerActivityTypes`(8) | LUCKY_WHEEL · HERO_CHAMPION_ROAD · MECHA_WHEEL · COIN_PUSHER · **PIONEER_CITY(81)** · BP_FUND · **CIRCUS_GACHA(83)** · ALLIANCE_IPO |
| `SeaAreaUnionActivityTypes`(9) | UNION_SINGLE_RANK · BOUNTY · DONATE · TRANSPORT · UNION_TASK · KVK_MONUMENT · UNION_MERGE · SCORE_GUILD_INTERNAL · GVG |
| `CrossServerActivityTypes` | KVK · INVADE · CROSS_PREPARE · KVK_SEASON · **WISHING_POOL** · GVG · SLG_METEOR_WAR · BP_FUND |
| `CenterHostedSingleActivityTypes` | COIN_PUSHER · LUCKY_WHEEL（单服活动但走 Center 托管，为了复用跨服榜链路） |

**不在以上任何集合 ⇒ 玩家个人级**。实例：**`TRIGGER_TYPE_PUZZLE = 18` 四个集合全都不在** ⇒ 拼图是玩家个人级活动。

### ★玩家个人级活动关不掉：iGame 撤单无效、GM 也救不了（2026-07-30 实证）
| 手段 | 玩家个人级 | 服务器级 / 跨服级 |
|---|---|---|
| **iGame 撤单** | ❌ 无效（从没被 iGame 部署过，没有单可撤） | ✅ |
| **GM 下架** `GMRemoveServerActivityByCfgId` | ❌ 基本无效：注释原文「无服务端实体，只能对当前路由到的玩家删」⇒ 要 `!gm @<playerId> ...` **逐个玩家跑**；更致命的是**删完玩家一登录、TC 窗口还开着就立刻又回来** | ✅ 一条命令：服务器级广播 `OnSeaAreaActivityEnd`（在线即时清+客户端撤掉+离线登录兜底）；跨服级转发 Center 下推各服 |
| **改 TC 窗口 + 导表 + 热更** | ⚠️**改内容不生效**（TimeCycle 热更只处理 ID 差集，见下节）；改 TC **ID** 才生效，且只对新登录玩家 | ✅ |
| **改代码 `IsActivityBlockedOnServer` + 代码热更** | ✅✅ **唯一能立刻清掉所有人（含在线）** | ✅ |
代码锚点：`ActivityMeta.Gm.cs:20-39`（三级自动识别）+ `:45-63`（个人级只删当前玩家）。
- ⚠️**止损必须改在漏出的那个分支上**：本案 BINGO 从 master 漏（配置 7/28 进 master + master 导表 #2348 生效），改 dev_festival 对已漏出的完全无效。**先确认生产读哪个分支再动手。**
- ⇒ 排期原则：**玩家活动的窗口只能靠配置控制，没有运营侧应急阀门**。给它配 TC 要比服务器活动更保守（占位填未来时间），因为配错了没有 iGame 兜底。

### ★改 TC 止损的生效边界（2026-07-30 实战补充，比"改 TC 是唯一手段"更重要）
改 TC 能关掉玩家活动，但**不是立刻、不是对所有人**：

代码（`ActivityMeta.cs` 的 `OnPostInit` → `HandleNewPlayerActivityInfos`）：
```csharp
if (CheckActivityTimeCycleIsOpen(cfgId, now) != ErrCodeCommon.ErrCodeSuccess) {
    if (activityItem != null) RemoveActivity(activityId, cfgId, now: now);  // 判不过才删
    continue;
}
```
⇒ **只在玩家上线那一刻用最新 TC 重判**。所以：

| 玩家状态 | 热更后表现 |
|---|---|
| 从没进过 | ✅ 不再创建实例，看不到活动 |
| **当前在线** | ⚠️ **活动继续挂着**，要等他下线再上线才清 |
| 已下线 | ✅ 下次登录时实例被删 |

- **已创建实例的 start/end 是创建时固化的**：数仓 `activity_start_time/end_time` 改 TC 后仍显示旧窗口（本案仍是 7/1→9/29），因为改 TC 不去改实例字段，只会在登录时**整个删掉实例**。看到这个别以为热更失败。
- ⇒ **完全清干净要等一个自然登录轮换周期**（多数玩家一天内会重登）。想立刻全清只能 GM 逐玩家删——**且必须先把 TC 改过期再删**，否则删完立刻重建（TC 还开着）等于白删。这也是"TC 过期"和"GM 删"的正确顺序。
- ⚠️**热更链路是三步，缺一步都不生效**：① MR 合并 ② **master 导表(jolt) 产出新 bytes** ③ 配置热更下发到生产服。②没跑的话热更下发的还是旧 bytes。**"MR 合了"≠"改动上线了"**。

### ★★紧急下架活动的手段库（2026-07-30 实战挖到底，比上面那张表更完整）

#### 1. 为什么"改 TC 内容 + 热更"不生效 —— TimeCycle 热更只认 ID 差集
```csharp
// TimeCycleMeta.OnReload
if (!reloadTables.Contains("TimeCycle.bytes")) return;
var reloadCfgIDs = GetModule<TimeCycleMgr>().ReloadPlayerReloadCfgIDs;  // ← 差集
if (reloadCfgIDs.Count == 0) return;      // 同 ID 改内容 ⇒ 不进差集 ⇒ 整个跳过
InitPlayerCreateTimes(reloadCfgIDs); InitTimeCycleInfo(reloadCfgIDs);
```
⇒ **改已有 TC 行的 StartTime/Duration，配置热更后服务器仍用旧值**（本案实测：TC 1831 改完导表成功、热更后玩家重登活动照旧）。
`TimeCycleMgr` 定义在 HEngine 框架层，仓内只有调用处。

#### 2. ActvOnline 的 OnReload 是**全量**的（不受差集限制）
```csharp
// ActivityMeta.OnReload —— 每次配置热更都全量跑这三个
InitTriggerConditions();
RemoveBlockedActivities();          // IsActivityBlockedOnServer 命中 → RemoveActivity(force:true) + 通知客户端
HideInvisibleActivitiesOnClient();  // 仅前端隐藏，服务器数据不动
```

#### 3. `IsActivityBlockedOnServer` 是**硬编码 switch**，不是配置（`ActivityMeta.cs:1108`）
```csharp
switch (cfgId) {
    case 106003: return serverID is 1770 or 1780;
    case 101023: case 102234: case 105602: case 101825:
    case 10071801: case 101334: case 100594: return serverID is >= 1770 and <= 1790;
    case 106102: return serverID is 1880;
    default: return false; }
```
- 已有 8 个活动在用 ⇒ **是项目既定手段**。文件在 `GameServer.Hotfix` ⇒ **可代码热更**。
- 加一个 `case <cfgId>: return true;` + 代码热更 ⇒ **热更那一刻所有玩家（含在线）的实例被 force 删除 + 客户端界面即时撤掉**。

#### 4. 第四条路：`ReloadGameServer force=1` — 全量重载，绕过差集（最轻）
```csharp
[GMHandler("[程序_热更]ReloadGameServer", GMAuthorityType.GM_OP_SUPER)]   // GameServer/Modules/PlayPreloadModule.cs:91
private async ValueTask<...> GMReloadGameServer(string scriptMd5 = null, int force = 0)
    => await GameServer.Instance.Service.ReloadAllAsync(true, scriptMd5, force: force != 0);
```
`ReloadAllAsync` 是**整个 GameServer 的全量重载**（配置+脚本），不走 `TimeCycleMeta.OnReload` 的差集路径 ⇒ **配置已导表就位、只是没被加载时，跑一次 force=1 就能让新值生效，什么都不用改**。
- 权限 **`GM_OP_SUPER`**（高于普通 GM）。对线上有动作，**先在单服试**再推全服。
- 同类：`ReloadCenterServer` / `ReloadKvkServer` / `ReloadMapServer`。

#### 5. 改 TC 的正确姿势：**只加不删**
差集认的是「TimeCycle 表的 ID 变化」⇒ **新增一个 ID 就够，不必删旧行**：
保留旧 TC 行不动（变孤儿行，无害）→ 新建 TC 新ID = 目标窗口 → `ActvOnline.<活动>.TimeController` 指向新 ID。
- 差集识别到新增 ⇒ TimeCycleMeta 处理 ✅；ActvOnline 改动走全量 `InitTriggerConditions()` ⇒ 新指向立即生效 ✅
- **零删除** ⇒ 导表不可能因悬空引用失败，回滚只需把指向改回去。

#### 6. 「TC 行不存在」的安全性（三层，2026-07-30 查实）
| 层 | 后果 |
|---|---|
| **导表** | **硬校验**：`if not timeCycleData: raise ActvOnline配置错误...未能查找到相关TimeCycle配置`。同类校验在 Pack / PackWeek / ChainPack / FunctionUnlock / DateEvent / ActvOnline(单服+跨服+普通) 共 8 处 ⇒ **悬空引用进不了生产** |
| **玩家已有实例** | ✅ 不受影响 — 实例存**固化的 start/end 时间戳**，不存 TC 引用 |
| **登录重判** | 走 ActvOnline 指向的新 TC，行存在 ⇒ 正常判断，不会 null |
- ⚠️**删 TC 行 ≠ `IsOn=0`**：后者让 ActvOnline 整行不导入 ⇒ `CActvOnline.I(cfgId)` 返回 null ⇒ **服重启时 DeleteActivity 清实例丢数据**（铁律禁用）；删 TC 行只要同时改指向，ActvOnline 行还在、cfg 不为 null，**无此风险**。

#### ⇒ 紧急下架某活动的四条路（优先级：4 全量重载 > 5 只加不删换TC > 代码屏蔽 > 等重启）
| 方案 | 做法 | 生效范围 | 代价 |
|---|---|---|---|
| **代码屏蔽（最强）** | `IsActivityBlockedOnServer` 加 case + 代码热更 | **所有玩家含在线，立刻** | 改服务端代码 + MR + 代码热更 |
| 配置绕差集 | **删旧 TC 行 + 新建新 ID**，活动的 `TimeController` 指新 ID | 差集能识别 ⇒ 新登录玩家被清；**在线的仍要等重登** | 配置改动 + 导表 + 配置热更 |
| 等服重启 | 什么都不做 | 重启全量加载 ⇒ 已改的 TC 内容自然生效 | 零成本，但要等 |
- ⚠️**"改 TC 内容"这条单独用是无效的**（差集吃掉），只有配合"改 ID"或"等重启"才成立。

#### ⚠️ 选方案前先问：这个活动之后还要不要再开
三条路的"现在清得干净"和"以后重开要几步"是**反向的**，选错会多付两次热更：

| 方案 | 现在清得干净吗 | 以后重开要几步 | 玩家进度 |
|---|---|---|---|
| **代码屏蔽** | ✅ 所有人（含在线）立刻 | **2 步**：删 `case` + 代码热更；**且仍要新建 TC ID**（旧 TC 已过期、改内容无效） | **force 删除，进度清零** |
| **删旧 TC 行 + 建新 ID** | ⚠️ 新登录的清，在线的等重登 | **0 步**（新 TC 窗口到点自动开） | 同样清零（登录时 RemoveActivity） |
| 等重启 | 重启后生效 | 视 TC 窗口而定 | — |

⇒ **判据**：
- **之后不再开** ⇒ 代码屏蔽是终态，一步到位最省事。
- **之后还要开**（如挪到下一周期）⇒ **直接用「删旧 TC + 建新 ID，新 ID 窗口设成目标档期」**：一次配置改动同时办"现在关"和"到点自动开"，不用改代码、不用代码热更、也不用事后改回来。
- ⚠️ 两条路**都会清掉玩家已有进度**（`RemoveActivity(force:true)` / 登录重判时的 `RemoveActivity` 都是真删数据），且**未领奖励无兜底**（`GetUnclaimedPuzzleRewardIds` 无调用点）。已领到手的不受影响。

#### 7. ★占位 TC 的标准写法＝StartTime 填 2099-01-01（项目内既有正例）
排期未定但被导表逼着必须填 TC 时，**照抄这条**：
```
TC 1516（AO 100702 酒馆争霸）：TriggerType=1 · StartTime 2099-01-01 00:00:00 · Duration 6d23h59m59s
```
起始时间填 **2099-01-01** ⇒ 配置随便进发布分支、导表、热更，窗口永远轮不到，**不会自己开**；排期定了再把 StartTime 改成真实日期（注意：改内容受差集限制，见本文 §1，要么换 ID 要么全量 reload）。

**反例＝本案 TC 1831**：`StartTime 2026-07-01`（配的时候已经是 7 月了）+ `Duration 89d` ⇒ **等于配了个立即生效的开关**，配置一进 master 并导表就当场全服打开，漏出 26,658 玩家 / 121 服。
- 同一个项目里两种写法并存 ⇒ **不是不知道怎么写，是那次写岔了**。
- 2026-07-30 全表扫描（master）：`TriggerType=1 且当前窗口开着` 的活动 **0 个**（1831 已修），`窗口在未来` 的 1 个（就是 TC 1516）⇒ **2099 写法是项目内唯一在用的占位范式**。
- 扫描方法（以后排查同类雷可复用）：读 `TimeCycle` 取 `TriggerType=1` 的行，算 `StartTime + Duration` 区间，与当前时间比对，再 join `ActvOnline.TimeController` 找出对应活动；重点看「窗口已开 + 跨度异常大」的。

#### 8. ★IsOn=0 关活动：对玩家个人级同样有效，且能绕开差集（2026-07-30 查证）
`HandleExpirePlayerActivityInfos()`（`OnPostInit` 里跑，玩家上线触发）：遍历 `Data.activityDict`，`var cfg = CActvOnline.I(activity.cfgID);` **若 `cfg == null` 就进 removeIds**，收尾统一 `RemoveActivity(..., force: true)`。

⇒ **`IsOn=0` 改的是「配置行存不存在」而非「行内容」**：ActvOnline 的 bytes 里直接没这行 ⇒ `CActvOnline.I()` 必然 null ⇒ **完全绕开 TimeCycle 的差集机制**（这正是改 TC 失效、而 IsOn=0 能生效的原因）。玩家上线即 force 删实例、进度清零；想重开只需改回 1。

⚠️ **与「IsOn=0 铁律」的边界**（见 [[reference_x3_timecycle]]）：铁律禁用它，是因为**活动还要继续跑**时用 IsOn=0 会造成意外的数据清除（服务器活动重启时 DeleteActivity）。**若目的本来就是关掉活动、且接受进度清零，IsOn=0 是有效且可控的手段** —— 判据是「你是否还想让这个活动继续」。

### 事故复盘（教训在这）
马戏节 BINGO 拼图 `101830`：配置 07-28 进 master、master 导表 #2348 成功（07-30 16:44）⇒ **当天就对生产全量可见**。
数仓实测（`ods_user_activity`）：**26,658 玩家 · 121 个服**（超出计划部署的 118 服）· `ods_user_activity_result` 已有 **17 人领奖**（含计划外发出的鎏金魅影纪念卡）。
**根因链**：把 TC 当占位 → 以为靠 iGame 控窗口 → 排期写 W2(D7–D13) → 实际 TC 从 7/1 就开 → 配置一进 master 并导表就漏。
**⇒ 排期前必须先判活动类型**：玩家活动的窗口＝TC 窗口，配置进发布分支+导表成功那一刻就生效，**没有"提单前不会开"这回事**。
