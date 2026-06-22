# 客户端运行时入口（X3 Unity Editor）

通过 DebugUtils HTTP 桥（`client.py eval/invoke/describe`）读写客户端运行时状态。本文件是"怎么读 X 的速查"，桥怎么用见 DebugUtils skill。

> 实测环境：工程 TavernLegend，Unity 2022.3.61f1c1。命名空间与 X2 不同（别套 X2 的 `Logic.LPlayer` 等）。

## eval 语法约束（先记住，少走弯路）
- ✅ 支持：链式属性访问、**带括号的方法调用**（`CActvOnline.I(101108)`）、字符串/数字字面量、`null`、可选参数省略。
- ❌ 不支持：**泛型**（`GetMeta<T>()` 报 `无法识别字符 '<'`）、`typeof`、`new`、lambda。
- 泛型方法 → 改用**非泛型字符串重载**：`GetMeta("activity")`（eval 运行时反射会命中实际类型的方法，可继续链式调）。
- 判断"某方法/新代码是否已编译加载" → 用 `client.py describe --type <全名>` 列成员，**别用不带括号的裸方法名**（会 MissingMember 误判为不存在）。
- 全局命名空间类型不加前缀（`GamePlayerPrefs.GetIntByRole(...)`）。

## 玩家 / 全局
| 要读的东西 | eval |
|---|---|
| 玩家 ID | `Logic.G.PlayerID` |
| 服务器 ID | `Logic.G.ServerID` |
| 玩家实体 | `Logic.G.Player`（ClientPlayer，`Logic.G` 是入口，定义在 `Assets/Scripts/Global/G.cs`）|
| 是否 Play Mode | `UnityEditor.EditorApplication.isPlaying` |
| 是否编译中 | `UnityEditor.EditorApplication.isCompiling` |

> ping 通只证明 Editor 开着；读玩家状态需游戏真登进去（`G.PlayerID > 0`）。

## Meta（玩家功能组件）
- 取法：`Logic.G.Player.GetMeta("<名>")`，名字是字符串常量，定义在 `Assets/Scripts/CSShared/Common/Const/MetaConst.cs`。
- 已验证的名：`"activity"` (ActivityMeta)、`"pay"` (PayMeta)、`"basic"` (BasicMeta)。其余 grep `MetaConst.cs` 找（如 `"numeric"`、各功能名）。
- 例：
  - 等级 `Logic.G.Player.GetMeta("basic").Level`
  - 注册时间(ms) `Logic.G.Player.GetMeta("basic").Data.createTime`
  - 累计充值(分) `Logic.G.Player.GetMeta("pay").TotalPayMoney`（美元 = `RealTotalPayMoney` = /100）
  - 金砖余额 `Logic.G.Player.GetMeta("pay").InnerCurrency`
  - 购买模式 `...GetMeta("pay").Data.purchaseMode` / `IsGoldBrickMode`
  - 活动是否开（按配置 ID） `Logic.G.Player.GetMeta("activity").GetActivityIdsByCfgID(<cfgId>)`（返回 activity 实例 id 列表；空=未开。**玩家触发型活动的 activityId == cfgId**）

## 配置表
- 单条：`GameCommon.Cfg.C{表名}.I(<id>)` —— 返回整行对象，可继续读字段（`.RechargeAmount`、`.ActvType` 等）。
- 全表：`GameCommon.Cfg.C{表名}.Instance`（`.Configs` / `.SortedIDs` / 派生集合如 `.PlayerActivityIds`）。
- 例：`GameCommon.Cfg.CActvOnline.I(101108).RechargeAmount`、`GameCommon.Cfg.CTimeCycle.I(1108).Duration`（ms）。
- ⚠️ 运行时读到的是**客户端已加载的 bytes**，可能跟 tsv 不一致（见 SKILL 第 3 步 / recipes 配置生效闭环）。

## PlayerPrefs（本地存档，常用于 dedup / 弹一次）
- `GamePlayerPrefs.GetIntByRole("<key>", 0)` —— 按角色隔离（内部拼角色前缀）。
- 例：弹窗"每角色弹一次"的去重 key 形如 `ActvPopupCount_{cfgId}`，置 1 表示已推过。

## UI（WndMgr）
- 打开/关闭/查询走 `UI.WndMgr`；业务 UI 规则见项目 `client/CLAUDE.md`。
- ⚠️ eval 查"某窗是否显示"受限：`WndMgr.Get<T>()` 是泛型、`IsShow(typeof(...))` 需 typeof，**eval 都不支持**。可行替代：
  - 直接**截图**确认（最可靠，见下）。
  - `WndMgr.Get(int id)`（按 UI id，需知道 id）。
  - 反射读已显示集合（X3 字段名需 grep `WndMgr*.cs` 确认，**不是** X2 的 `m_AllShownUI`）。
- 队列式 `WndMgr.Push`（按优先级、进主场景才显示）：推窗 ≠ 立即显示。直开某活动面板截图：`UI.UIHelper.OpenActivityPanel(<activityId>L, false)`。

## 截图（视觉验证）
```
client.py invoke --type UnityEngine.ScreenCapture --member CaptureScreenshot --kind call --args "<绝对路径.png>"
# 等 1~2 帧（再发一个无副作用 eval 让主循环走一帧），再 Read 那个 png
```

## 驱动客户端方法（让真实链路跑）
- eval 能调 public 方法。Editor 下很多 SDK 走假实现，可直接驱动业务请求。例：
  - 买礼包：`Logic.G.Player.GetMeta("gift").ReqBuyGift(<giftID>, null)`（Editor 直发 BuyGiftReq，详见 recipes）。
- 玩家域 GM：`Logic.G.Player.GetMeta("basic").SendGmCmd(cmdName, rawCmd, 0)`（见 gm-commands.md）。
