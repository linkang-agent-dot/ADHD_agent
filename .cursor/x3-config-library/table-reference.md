# X3 配置表参考字典（table-reference）

> X3 专属 config-library 的表知识总纲。换皮 / 配活动 / 改数值前先读这份，定位表 → 看字段角色 → 追踪链 → 必检清单。
> 收编自 `memory/reference_x3_*.md` 全集 + 实际 tsv 表头扫描（2026-05-29）。
> 配套：活动形式目录见 `activity-forms.md`；操作规则见 `reskin-rules.md`；必检细则见 `must-check.md`。

---

## 0. 仓库与写入规则（铁律）

| 项 | 规则 |
|----|------|
| 配置仓 | `C:\x3\gdconfig\`（remote `https://git.tap4fun.com/x3/gdconfig`） |
| **配置真源** | **`C:\x3\gdconfig\tsv\`** —— 导表（Jenkins「X3导配置」）只读 tsv 缓存（2026-05-29 迁移） |
| **改表方式** | **直接改 tsv，不碰 xlsx**。`data\*.xlsx` 仅历史备份（下周删）；`C:\X3\`、`C:\x3dev\` 已弃用 |
| tsv 命名 | `tsv/{data下相对目录}/{xlsx文件名}__{Sheet名}.tsv`（顶层 data/ 无子目录前缀；如 `Pack__Pack.tsv`、`i18n/Text__Text.tsv`） |
| 安全改 tsv 工具 | `x3-config-export` skill 的 `scripts/tsv_edit.py`：`show` 定位列 → `set` 断言旧值改 → `remove` 从管道列表删 ID（保 LF、dry-run） |
| ⛔ 重生成禁令 | 对已 tsv-直接改过的表**绝不能** `xlsx_to_tsv.py` 重生成（xlsx 是旧的，会覆盖回旧值） |
| 唯一例外 | i18n 翻译走 `x3-translation-automatic`（CompositeI18n）会动 `data/i18n/Text.xlsx`，改完必须 `xlsx_to_tsv.py --files data/i18n/Text.xlsx` 重生成那一个 tsv，或直接改 tsv 语言列 |
| 改前 | `git branch --show-current` 确认分支（直接在当前活跃分支上改，别自建专属分支） |
| 改后 | `git diff` 看行级 diff（没串列、LF 没坏）→ commit → push → `python scripts/jolt_verify.py <分支>` 触发导表并验证 SUCCESS/FAILURE |

---

## 1. tsv 文件结构（读表必知）

每个 tsv 文件**前 7 行是元信息，不是数据**：

| 行 | 内容 |
|----|------|
| 行1 | 导出标记 `cs`/`c`（控制客户端/服务端导出） |
| 行2 | 字段数据类型（`int`/`string`/`bool`/`int[]`/`time`） |
| 行3 | 引用表名（该列引用哪张表，本文档标为 `→表名`） |
| 行4-5 | 中文说明（含换行，会撑乱 TSV 列对齐） |
| 行6 | 中文字段名 |
| **行7** | **英文字段名（真正的列 key）** |
| 行8+ | 数据 |

- 编码 **UTF-8**（不是 GBK）。用 Read 工具能正确读中文；用 Bash 管道捕获中文会乱码（控制台代码页问题），脚本输出中文务必落文件再 Read。
- `tsv_edit.py show` 用列号定位时，注意元信息行偏移。

---

## 2. 核心表速查（节日换皮强相关）

> 锚点原则：几乎所有 Actv* 玩法表第一列都是 `ActvOnline.ContentID`。换皮**先在 `ActvOnline__ActvOnline.tsv` 建活动行，再挂玩法表**。

### 2.1 活动主体

**ActvOnline → `ActvOnline__ActvOnline.tsv`**（在线活动总表，所有活动的入口与调度根）
关键列：`ID / ActvName / ActvDesc / ContentID / ActvType / IsOn / TimeController(→TimeCycle) / TriggerType / PlayerLv / RechargeAmount / MailID(→MailTemplate) / CrossServerRank / RankID(→RankCfg) / ActvIcon / ActvImg / ActvPrefab / PreviewBg / CalendarBg / ChainPackID(→ChainPack) / GroupId(→ActvGroup) / MainEffect / FullBg / ActvRechargePoints / RechargePointPackWhitelist(→Pack)`
- `TimeController`（H 列/第8列）= 活动时间绑定，**不是**看子表或编号相等；新增 TimeCycle 后必须改这里指过去
- `ActvType` 活动类型（决定走哪套玩法逻辑与 TimeCycle.TriggerType 限制）
- `MailID` 奖励补发邮件（**必填**，除 ActvType=8 外填 `101109`，见 §4）
- `CrossServerRank`（col19）1=跨服 / 空=本服；`RankID`（col21）→ RankCfg
- `RechargePointPackWhitelist`（col51）= 累充隔离白名单（→Pack，`|` 分隔，见 §4）
- 美术 DK：`ActvIcon / ActvImg / ActvPrefab / PreviewBg / CalendarBg / MainEffect`，`FullBg` 是否全屏背景

**ActvGroup → `ActvOnline__ActvGroup.tsv`**（活动聚合入口外观）
`ID / Calendar / MainEntranceName / MainEntranceIcon / Order / TopFrame / BottomFrame / ExitBtn / LightTab / DarkTab / BgMask` —— 一组活动共用的聚合界面：主入口名/图标、上下边框、亮/暗页签、mask 背景（节日聚合框换皮）

**ActvGroupSchedule → `ActvOnline__ActvGroupSchedule.tsv`**（活动组排期）
`ID / IsOn / MainActvID(→ActvOnline) / ActvID(→ActvOnline) / StartTime / DurationType / DurationTime` —— 主活动下挂多个子活动 + 各自起止

**ActvTask → `ActvTask__ActvTask.tsv`**（全活动通用任务池）
`ID / ContentID / TaskType(→TaskType) / Count / Parameter1 / Parameter2 / PreTrace / Reward(→Reward) / CustomTaskText / Order / Privilege`
- `ContentID` 绑定任务组；`TaskType` 事件类型；`Count` 目标值；`Parameter1/2` 任务参数

### 2.2 礼包族（Pack__*.tsv）

**Pack → `Pack__Pack.tsv`**（礼包主表）
关键列：`ID / Price(→PackPrice) / GemPrice / PackType / UIType / ContentID / IsOn / Content(→Reward) / TriggerType / TriggerParameter / TimeCycleID(→TimeCycle) / BuyCount / PlayerLv / VipLv / Prepack(→Pack) / ColdTime / Head / Icon / RoleImg / UseSpine / MainBg / BottomBg / OtherBottomBg / ContentBg / MallContentBg / Name / Desc / PopUp / Tag / Priority / RechargeAmount / Rally(→PackRally) / Group / PopUpImg / MainPackBtnBg / OpenActv(→ActvOnline) / Gift`
- `Price` 现金价 / `GemPrice` 钻石价；两者空=免费礼包（链式礼包用）
- `Content` 礼包内容物 →Reward；`TimeCycleID` 礼包自身开放时段
- 美术 DK 字段组（换皮重点改）：`Head / Icon / RoleImg / UseSpine / MainBg / BottomBg / OtherBottomBg / ContentBg / MallContentBg / PopUpImg / MainPackBtnBg`
- 本地化 TXT_：`Name / Desc / Tag / PopUpDialogue`
- ⚠️ `MainBg` 拜访/家具礼包**必须空**（见 §4 弹窗渲染优先级）

**ChainPack → `Pack__ChainPack.tsv`**（链式/阶梯礼包，1 父 + N 档子 Pack）
`ID / Name / IsOn / Icon / PackList(→Pack) / MainBtn / TimeCycle(→TimeCycle) / CustomParameters / Video / 备注`
- `PackList` 阶梯各档 Pack ID（list 顺序=展示顺序）
- `CustomParameters` 海妖连锁引用，格式 `类型|参数|值`（`4`=节日阶梯礼包，引用连锁阶梯样式+视频背景）
- `Video` DK_视频（节日阶梯礼包背景视频）

**PackTypeInfo → `Pack__PackTypeInfo.tsv`**（商城页签/礼包类型）
`ID / IsOn / Name / MallType / Icon / Sort / Content(→Pack) / RuleID(→RuleTips) / Desc / Fullbody / Spine`
- ⚠️ `Icon` = **底部商城页签 tab 按钮图**（用户最先看到的入口图，换皮最易漏，见 §4）

**其他 Pack 子表**：`Pack__OptionalPack`（N选一）/ `Pack__DailyPack`（每日礼包）/ `Pack__PackPrice`（价格：`Id / Dollar / Key(Google商城编号) / IOSKey / Points`）/ `Pack__PackRally`、`PackShip`、`PackStall`、`PackWeek`、`WeeklyCard`、`GrowthFund` 等

### 2.3 奖励 / 排行榜

**Reward → `Reward__Reward.tsv`**（奖励定义，唯一一张）
`seq / RewardID / ItemType / ItemID / Note / Num(MinNum) / [MaxNum] / DropType / DropPara / PreviewItem / GoodsQuality`
- 同一 `RewardID` 多行=一组奖励；外部表（Pack/活动）引用 RewardID
- ⚠️ `DropPara` 必填（必掉填 `10000`）；同 RewardID 内 `seq` 必须连续（见 §4）

**RankCfg → `Rank__RankCfg.tsv`**（排行榜配置）
`ID / RankName(TXT) / RankType / Sort / RankScoreIcon(DK) / MaxRankSize / RankRewardTitle / RankRewardTab / NeedSendMailReward / MailID(→MailTemplate,col11) / MailMaxRankNum / RuleTip / RankCondition(上榜门槛) / DailyRewardGroup(→SpecialRewardSettlement) / DailyMailID / WeekRewardGroup / WeekMailID`
- `RankType`：6=本服 / 12=跨服；⚠️ `MailID` 在 **col11** 不是 col13

**RankRewardSlotCfg → `Rank__RankRewardSlotCfg.tsv`**（名次奖励档）
`ID / RankType(→RankCfg) / RankSlotBegin / RankSlotEnd / RewardID(→Reward)` —— 名次区间→RewardID。改排名奖励 = 改这张
**SpecialRewardSettlement → `Rank__SpecialRewardSettlement.tsv`** —— RankCfg 日/周结算引用的名次奖励组
- 8 档常用分布：1 / 2 / 3 / 4-5 / 6-10 / 11-20 / 21-50 / 51-100
- ⚠️ 没有「显示奖励 vs 实发奖励」分列，每档统一一个 RewardID（既显示也实发）

### 2.4 时间循环

**TimeCycle → `TimeCycle__TimeCycle.tsv`**
`ID / IsOn / Attribution / TriggerType / StartTime / DurationType / Duration / CycleType / ReOpenTime / EndTimeType / EndTime`
- `TriggerType`：**1=绝对时间 / 2=开服时间 / 3=注册时间 / 4=海域开放 / 5=触发后计时 / 6=开服第N周**
- 判断用途看 StartTime/Duration 实际值，**别信名字**（可能是历史复用残留）
- ⚠️ ActvType 对 TriggerType 有隐性限制（见 §4）；跨服活动必须 TT=1

**TimePoint → `TimeCycle__TimePoint.tsv`** —— 绝对时间点定义，供 TimeCycle 引用

### 2.5 外观 / 皮肤 / 卡（换皮主角）

| 品类 | 表 / tsv | 关键字段 |
|------|---------|---------|
| 机甲/角色皮肤 | `Skin__Skin.tsv` | `ID / Name / SkinType / Unlock / Quality / Power / DK_Prefab / DK_Head / Buff` |
| 家具皮肤（主城整套外观） | `FurnitureSkin__FurnitureSkin.tsv` | `Type / Icon / CurrencyID / CurrencyValue / DoorDisplaykey / PillarDisplaykey / WallDisplaykey / FloorMaterial / ShowTime(→TimeCycle) / Pack(→Pack) / Buff` —— 门/柱/墙/地板各一个 DK key |
| 单件家具/装饰 | `FurnitureDecorate__FurnitureDecorate.tsv` | `DKPrefabs / Icon / Size / Prestige / GiftId(→Pack) / Pack(→Pack) / RewardID(→Reward) / Power / PropType / PropNum / ShowTime(→TimeCycle)` |
| 装饰物皮肤 | `FurnitureDecorate__FurnitureDecorateSkin.tsv` | `GetType / Value / SkinPfb / PropType / PropNum / Lv` |
| 装饰物等级产出 | `FurnitureDecorate__FurnitureLv.tsv` | `Lv / Group(→FurnitureDecorate) / RewardID / RewardTime / RewardMax` |
| 纪念卡/集卡 | `MemorialCard__MemorialCard.tsv` | `Name / Desc / DK_ImageSmall / DK_ImageBig / DK_Frame / GetTips / GetMoreTips / PropertyGroup(→MemorialCardLevel.Group)` |
| 纪念卡属性等级 | `MemorialCard__MemorialCardLevel.tsv` | `Group / Level / Num / PropType / PropNum / Power` |
| 英雄进阶礼包外观 | `PackHeroPromotion__PackHeroPromotion.tsv` | 纯美术：`BeforeHeroSpine / AfterHeroSpine / DK_BgBefore / DK_RewardBgBefore / DK_BgAfter / DK_RewardBgAfter` |

> ⚠️ X3 主城/岛屿皮肤是 `Item_81xxx`，**不在 Skin 表**；讨论 X3 皮肤先确认品类。

---

## 3. ID 编码规则

### 3.1 道具 Item ID 段（换皮逐个回 Item 表验证节日归属）

| 品类 | Item ID 格式 | 示例 |
|------|-------------|------|
| 岛屿皮肤（永久/限时） | `Item_81xxx` | 81001=南瓜灯岬，81051=柔情海湾，81151=金字塔之城 |
| 英雄晋升皮肤 | `Item_530xxxx` | 5301501=甜心咖啡师·海泽尔(26情人节)，530202=红绸剑姬·阿米娜(26春节) |
| 家具（摆件/地毯） | `Item_151xxx` | 151059-061=26情人节，151057-058=26尼罗 |
| 主城装饰三件套（地板/墙纸/横梁） | `Item_152xxx` | 152027-029=26春节，152024-026=25圣诞 |
| 纪念卡 | `Item_180xxx` | 180077=情人节，180078=春节，180076=尼罗 |
| 英雄信物（兑换源头） | `52001/52002/52003` | 稀有/史诗/传奇通用信物；51001-058=具体英雄信物 |

### 3.2 节日礼包 Pack ID 段（一套 = 210x01-210x18 量级）

| 节日 | Pack ID 范围 | ChainID | 结构（PackType） |
|------|------------|---------|------|
| 26尼罗之辉 | 210601-210617 | — | A线连锁(11)+锚点(15)+家具(1)+主城(16)；子模块圣甲虫返场 210619-629；装饰阶梯 210630-632 |
| 26情人节 | 210701-210718 | 484 | A线连锁11档(11)+B线锚点4档(15)+晋升皮肤(1,210716)+家具(16,210717)+常驻(15,210718) |
| 26新春特辑 | 210801-210816 | 485 | A线连锁(11)+锚点(15)+主城三件套(16,210816) |
| 26夏日恋语 | 210901-210921 | — | 复用情人节 Pack；拜访 210921；装饰阶梯 210917-919 |

PackType 速记：**11**=A线特惠连锁阶梯 / **15**=B线锚点/常驻 / **1**=皮肤礼包 / **16**=家具或主城装潢 / **3**=BP凭证。
通行证 BP Pack：130020/130021（女武神凭证类）。

> 完整节日 ID 段与各 Pack 明细见 `memory/reference_x3_config.md`，新换皮时核对最新一期实际值。

---

## 4. 必检清单（收编历史踩坑，换皮 / 配活动必过）

> 完整细则见 `must-check.md`，此处为速查。

1. **ActvOnline.MailID 必填** —— 除 ActvType=8（挑战）外统一填 `101109`。漏配则服务端补发链路 4 处 `MailID<=0` 守卫静默吞未领奖励（玩家无感知）。换皮复用历史行也要查。

2. **Reward 表三铁律**：
   - `DropPara` 必填（必掉填 `10000`），空则导表 `int('')` 报错
   - 同 RewardID 内 `seq` 必须连续（`reward_def.py` 强校验，断号报错）
   - **占位行陷阱**：模板奖励常藏 `MinNum=0` 装饰性占位行（见过 `52003` 通用传奇信物、`11002` 5分钟加速两种），换皮不清掉→客户端面板显 `×0` 空图标。换皮后**扫所有 MinNum=0 行**（不要按特定 ItemID 扫）。

3. **累充隔离（节日各算各的累充）** = 三表协同：
   - `TaskType` 定义 902（活动累充），`SPECIAL_PARAMS_COUNTS` 需 `902:2`（导表脚本自动算 ParamCount，配置侧不可见）
   - `ActvOnline.RechargePointPackWhitelist`（col51）填本节日 Pack ID（`|` 分隔），非空才启用隔离
   - `ActvTask` 累充各档位（通常 10 档）`TaskType` 改 902 + `Parameter1` 填本活动 ContentID（**全档位联动**）
   - ⚠️ 每次给节日新增付费 Pack，回头检查是否要加进该节日累充白名单（节日专属必加；跨节日通用 Pack 所有在用节日白名单都加；免费 Pack 一般不加）

4. **Pack.MainBg 渲染优先级** —— `Pack.MainBg` 一旦填值覆盖弹窗主视觉。**拜访礼包/家具礼包 MainBg 必须空**（走 ActvOnline.ActvImg 默认渲染）。误填通用模板（如 `DK_img_gift_bg_28`）会顶替节日主视觉。

5. **装饰阶梯礼包 3 处 Icon** —— ChainPack 形态换皮必同时改：① `Pack` sheet 各档子 pack `Icon` ② `ChainPack` sheet 父 `Icon` ③ **`PackTypeInfo` sheet 对应 ID 的 `Icon`**（底部商城 tab 图，最易漏，不在常规 Pack 关联检查里）。

6. **TimeCycle.TriggerType 限制**：
   - 跨服活动（`CrossServerRank=1`）**必须 TT=1 绝对时间**（`PostProcessData.py:1633` 校验；跨服需 CenterServer 绝对时间锚定）
   - ActvType=50 许愿池疑似硬编码要求 TT=1；ActvType=7 酒馆历史只用 TT=1/4；ActvType=13 兑换用 TT=1/3/4；ActvType=10 转盘 TT=2 有先例可用
   - 导表报错「应该是绝对时间」无行号，多为 ActvType 对 TriggerType 的硬编码校验

7. **ScoreID=603 陷阱** —— `ActvScore`（本服）ScoreID=603 是「运营大师」（声望排名 ActvType=6），**不是酒馆活动**。修最佳酒馆别动这行，酒馆配置全在 `ActvScoreMulti`。

8. **新增带 TXT_ 字段的任务/礼包必须同 commit 补翻译** —— 否则非中文服显中文母版。走 `x3-translation-automatic`。X3NEW-734 踩坑：只 commit 配置没补 Text → 俄服显中文。

9. **改 tsv 不碰 xlsx + 改前确认分支 + 改后 jolt 验证**（见 §0）。

---

## 5. 跨表 ID 联动规则（改一处要同步的下游）

- **ActvOnline 是锚点**：玩法表（ActvScore/ActvLuckyWheel/...）、ActvTask、Pack.OpenActv、累充白名单都引用 ActvOnline.ContentID。建活动先建 ActvOnline 行。
- **新增 TimeCycle 行** → 必须改 `ActvOnline.TimeController` 指过去（否则孤儿行）。
- **Pack ID 变** → 同步 `ChainPack.PackList`、`PackTypeInfo.Content`、`Reward`（Pack.Content）、累充白名单 `RechargePointPackWhitelist`。
- **道具 Item ID 变** → 所有引用表（Reward.ItemID、兑换/任务参数）同步。
- **跨服活动改造**只需改 4 处：ActvOnline(1行) + ActvScoreMulti(各 stage) + RankCfg(新增) + RankRewardSlotCfg(新增)。`ActvScoreMultiServer` 仅 KVK/远征登记，酒馆系列不用。

---

## 6. 翻译 / GSheet 侧

- TXT_ key 命名规则：`TXT_{Table}_{Field}_{ID}`（见 `memory/reference_x3_i18n_workflow.md`）
- 翻译走 `x3-translation-automatic`（扫配置 → 译 10 语言 → 写 GSheet + Text.xlsx → 重生成 `tsv/i18n/Text__Text.tsv` → 提交）
- 跑 CompositeI18n 前先把 `data/_backup_*.xlsx` 移出 data 目录（否则 key 冲突中断扫描）

---

## 关联 memory（深挖时回看）
- `reference_x3_config.md`（Item/Pack ID 段全表）· `reference_x3_tsv_export_migration.md`（tsv 迁移）
- `reference_x3_score_activity.md`（积分活动）· `reference_x3_reward_table_rules.md`（Reward 规则）
- `reference_x3_recharge_isolation.md`（累充隔离）· `reference_x3_timecycle.md`（时间循环）
- `reference_x3_pack_panel_rendering.md`（MainBg）· `reference_x3_pack_tab_icon.md`（tab 图）
- `feedback_x3_actv_mailid_check.md`（MailID）· `feedback_x3_branch_check.md`（分支）
- `reference_x3_i18n_workflow.md`（翻译）· `reference_x3_client_resources.md`（客户端资源/DK）
- `workflow_x3_decoration_video.md`（礼包美术全链路）· `workflow_x3_auto_jolt_export.md`（导表验证）
