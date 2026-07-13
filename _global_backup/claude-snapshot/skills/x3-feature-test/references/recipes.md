# 已验证端到端配方

测试前先翻这里：目标功能或同类是否已有配方可直接套。**新跑通一个功能就往这里加一节**（这是本 skill 越用越省的关键）。

格式：每个功能一节 = 触发条件 + 构造步骤 + 验证点 + 踩过的坑。

---

## 配方 1 · 新手累充首充弹窗（活动 101108，ActvType=5）
> 2026-06-19 在本地服 3080 跑通。功能：玩家累计真钱充值跨过门槛($0.99) → 服务端开活动 101108 → 客户端弹累充活动窗，每角色一次。

### 触发条件（评估那一刻须同时满足）
1. 玩家等级 ∈ `CActvOnline.I(101108).PlayerLv` = **[5,99]**
2. 在注册后 **8 天**内（`TimeCycle 1108`，注册相对触发）→ **要新号**
3. `TotalPayMoney` 由 `<RechargeAmount` **跨到** `>=RechargeAmount`（门槛 = 99 分 = $0.99）

### 链路
`买现金档(BuyGiftReq)` → 服务端 `GiftMeta.OnBuyGiftReq` `AddTotalPayMoney(Dollar)` → fire `PayOrder` → `ActivityMeta.OnPayOrder` 跨门槛 → `HandleNewPlayerActivityInfos` → `CheckActivityIsUnlock` 过 → 开活动 → ntf → 客户端 `ActivityTypeStateChanged` → `UIModule.OnActivityOpenForNewbieRecharge` → `UIHelper.PushActivityPanel` → dedup `ActvPopupCount_101108`。

### 纯 GM/eval 复现步骤（无需手点界面）
```
# 0. 前提：配置已生效（见下方"配置生效闭环"），客户端 RechargeAmount 读到 99
# 1. 建新号：Ctrl+G → [角色_账号]随机新建账号  （level1 / pay0 / 注册即时）
#    确认：Logic.G.PlayerID 变了、GetMeta("pay").TotalPayMoney==0、GetMeta("basic").Level==1
# 2. 升级到 ≥5（关键，否则卡等级关）：
client.py eval --code 'Logic.G.Player.GetMeta("basic").SendGmCmd("gmaddlevel","gmaddlevel 6",0)'   # → level 7
# 3.（可选）跳引导进主城（自然玩到主城更干净，跳引导会先弹引导奖励/VIP窗挡住）：
client.py eval --code 'Logic.G.Player.GetMeta("basic").SendGmCmd("gmskipallguide","gmskipallguide",0)'
# 4. 买 $4.99 现金档（giftID 2014001，Price键105 Dollar=499 Points=50）：
client.py eval --code 'Logic.G.Player.GetMeta("gift").ReqBuyGift(2014001, null)'
# 5. 验证：
client.py eval --code 'Logic.G.Player.GetMeta("pay").TotalPayMoney'                              # 0→499 跨门槛
client.py eval --code 'Logic.G.Player.GetMeta("activity").GetActivityIdsByCfgID(101108)'         # 非空=已开
client.py eval --code 'GamePlayerPrefs.GetIntByRole("ActvPopupCount_101108",0)'                  # 0→1 = handler 推窗了
# 6. 截弹窗（队列被引导/VIP窗挡时，直开面板截图）：
client.py eval --code 'UI.UIHelper.OpenActivityPanel(101108L, false)'
client.py invoke --type UnityEngine.ScreenCapture --member CaptureScreenshot --kind call --args '<path.png>'
```

### 验证点
- 代码路径：`dedup 0→1` + `GetActivityIdsByCfgID` 非空。
- UI：截图见"酒馆活动·累计储值"窗（档位 100/300/500/1000/3000，倒计时 ≈8天，$4.99→50 积分进度 50/100）。

### 坑（都踩过）
- 老号无法复现（pay 只增不减、已高于门槛）→ 必须新号。
- 新号 level1 买了也不开 → 卡 PlayerLv≥5；先升级。
- 顺序：先升级再买（在 level≥5 时跨门槛）；若先买后升级，充值事件已在 level1 评估失败，升级不补触发，得靠登录状态式重评估（重登一次，前提该活动在 `PlayerActivityIds`）。
- 别用"部署单服活动"GM 开 101108（玩家触发型，部署的 ServerActivity 不下发）。

---

## 配置生效闭环（任何"改了配置要验"的功能都用）
> 关键认知：改 tsv ≠ 生效。客户端读 `ProtoGen/*.bytes`，而提交进仓库的 bytes 可能是 stale 的（导表没重跑）。

1. 判 bytes 真实值（protobuf 手解）：int32 字段 N tag = `(N<<3)|0`；ID 字段(field1,tag 0x08) 定位行。例：RechargeAmount=field11→tag `0x58`，99=`58 63`、499=`58 f3 03`；id 101108 varint=`08 f4 95 06`。`python: data.find(b'\x08\xf4\x95\x06')` 定位行看后续 `0x58`。
2. 重导表（纯 Python，含全表校验）：`cd gdconfig/Tools/table_exporter && python ExportTable.py` → 产物 `gdconfig/temp_dev/ProtoGen/*.bytes`（成功标记：`protoc 成功`+`generate localization bytes success`+`MD5`，无 Exception）。
3. 覆盖 client：`cp temp_dev/ProtoGen/{表}.bytes client/Assets/Res/Config/ProtoGen/`（保留 .meta，GUID 不变）。本地服通过 `server/Resource/.../ProtoGen` symlink 读同一份。
4. Unity 重载：DebugUtils `editor_reload.py stop` → `client.py invoke UnityEditor.AssetDatabase Refresh` → `editor_reload.py start`（重进 Play，config 单例 reboot 重读）。
5. 服务端热更（本地服）：`x3_gm.py "!gm ReloadGameServer"`（日志 `Reload Finished` + `[Notify]reload[N] success`）。
6. 验证：客户端 `CActvOnline.I(id).字段` + 服务端（telnet 可达时）同字段都变新值。
7. 分支正式生效：`x3-config-export` 的 `jolt_verify.py <branch>`（CI 导表，校验 SUCCESS + 流水线重生成 committed bytes）。

> 注意客户端/服务端分离：客户端 bytes 改了只修客户端显示；活动开关判定在服务端，连远端服时需服务端也用上新配置。本地服因 symlink 读同一份，`ReloadGameServer` 即可。

---

## 配方 2 · 限时招募池 TimeCycle 永久循环验证（X3NEW-592，按服龄排程的功能通用）
> 2026-06-24 在本地服 3080 验证。功能：异国美酒(itemId=7002)英雄"限时招募池"原排程止于开服 173 天，174 天+ 断档；修复给 6 个返场池的 TimeCycle(71011/71021/72011/72021/73011/73021) 打开 `CycleType=1(间隔循环)/ReOpenTime=84d`，使其开服满 89 天后每 84 天(=6池×14天)轮播、永不断档。**纯配置改动。**

### 机制（决定怎么测的关键，全部静态读码确认）
- **招募池开/关是客户端自算的，不是服务端下发**：`GachaMeta.GetOpenCardPoolIDs()`(`Entity/Player/GachaMeta.cs:117`) 对每个池调 `TimeCycleMeta.IsTimeCycleOpen(timeCycleID)` → `TimeCycleManager.IsOpen()`(`Utils/TimerCycleManager.cs:90`)，靠 `startTime<=now<=endTime` 判定。
- 时间点 = `serverOpenTime`(开服时间，来自 `BasicMeta.ServerOpenTime`) + 当前 `GameTime.Time` + TimeCycle 配置算出。`TriggerType=2`=服务器开服相对(`TimeCycleConst.cs:11`)，`CycleType=1`=间隔循环(`:27`)。
- **推论：验"服龄>X天"不需要真老服——客户端按"开服时间+当前时间"算，把服务端时间往前推即可模拟。** `TimerCycleManager.cs:611` 的 expire-queue 专门处理"改时间导致开始/结束时间不正确"，所以单次大跳也能级联重算。
- DrawCards 池引用 TimeCycle：`cfg.ServerTimeCycles.GetValueOrDefault(serverId, cfg.Time)`；6 个返场池 DrawCards id=11011/11021/12011/12021/13011/13021，CostType 全=7002、PoolsType=1(限时)，Hero 轮换：凌霜→艾琳娜→夜玫瑰→爱莉希雅→星璃→露娜。

### 复现步骤（GM 跳服龄，纯 eval 驱动）
```
# 0. 前提：配置已生效——客户端实读确认 6 个 TimeCycle 都是 CycleType=1/ReOpenTime=7257600000ms(=84d)/NeedCycle=True/EndTime=空
client.py eval --code 'GameCommon.Cfg.CTimeCycle.I(71011).CycleType'    # =1
client.py eval --code 'GameCommon.Cfg.CTimeCycle.I(71011).ReOpenTime'   # =7257600000 (84d)
client.py eval --code 'GameCommon.Cfg.CTimeCycle.I(71011).NeedCycle'    # =True (循环必须为真，否则不循环)
# 1. 推进服务器时间(forward-only，服务端GM，走客户端SendGmCmd)；target=1=仅Game服，避免牵连Center
client.py eval --code 'Logic.G.Player.GetMeta("basic").SendGmCmd("gmsetservertimebydhms","gmsetservertimebydhms 175 0 0 0 1",0)'
# 2. 读开放池：含 7002 的就是限时池
client.py eval --code 'Logic.G.Player.GetMeta("gacha").GetOpenCardPoolIDs()'   # 例 [1, 11011]；池1=御女酒宴常驻(7001)非证据
client.py eval --code 'GameCommon.Cfg.CDrawCards.I(11011).CostType'            # =7002 → 异国美酒限时池
```

### 验证点（代码路径）—— 实测结果
| 服龄 | GetOpenCardPoolIDs | 7002限时池 | 主打英雄 |
|---|---|---|---|
| 0d | [1,1101,1201] | 无(89天后才有，符合预期) | — |
| 175/180d | [1,11011] | ✅ 11011 | 凌霜(功夫妹) |
| 210d | [1,12011] | ✅ 12011 | 夜玫瑰(洛丽塔) |
| 250d | [1,13021] | ✅ 13021 | 露娜(黑萨满) |
| 300d | [1,12021] | ✅ 12021 | 爱莉希雅(白毛) |
每个服龄恰好 1 个 7002 限时池在线(不空不重叠)，英雄按设计轮换，300d(已过 257d 重开点)证明永久循环 → 🟢 修复生效。

### 坑（都踩过，血泪）
- **服务端是独立进程**：只杀 Unity，本地服仍保留时间偏移；要重置服龄须重启 GameServer 进程。`gmsetservertimebydhms` 不支持回退(只能往前)。
- **别反射强开招募 UI 截图**：`WndMgr.Show(typeof(UIHeroLottery))` 用 `forceNewRecord=true`、或先 `HideAll()`/`Clear()` 再 `Show`，会让招募 UI 跑死(内存飙 3GB+ / 主线程卡死，Unity 假死，HTTP 桥跟着死)。根因：`HideAll/Clear` 会 `CancelGlobalCts()`，之后 `Show` await 已取消的 cts；且强开绕过正常 data 装配。**截图走游戏真实入口**(见下方"运行时开 UI/关弹窗"配方)。
- **跳大服龄触发登录弹窗刷屏**：175/300 天登录会按 push-queue 连弹 `UIActvSevenLogin`(開業回饋)→`UIPackCommonPop`→`UIGameScore`(评分) 等一串，逐个 Hide 也会被队列续上，挡住招募界面。

---

## 配方 3 · 运行时开 UI / 关弹窗的正确姿势（桥操作通用）
> 配合 DebugUtils。核心教训：**能走游戏真实入口就别反射强开；强开 UIHeroLottery 会卡死 Editor。**

### 读"当前显示了哪些窗口"（eval 不能传 `UI.UILayer.Window` 字面量，改读 UIRoot 子节点）
```
client.py eval --code 'UnityEngine.GameObject.Find("UIRoot").transform.childCount'
client.py eval --code 'UnityEngine.GameObject.Find("UIRoot").transform.GetChild(6).name'
# 返回如 "UIActvSevenLogin [state: Shown_HasFocus, layer: Window]"，state 含 Shown_HasFocus 的就是当前挡住的窗口
```

### ★关弹窗：可自动化的安全套路（下次同类直接照做，无需人工）
**根因**：跳大服龄/登录会经 `WndMgr` 的 **push-queue**(`WndMgr.Push.cs`) 连发登录弹窗(`UIActvSevenLogin`→`UIPackCommonPop`→`UIGameScore`→`UIPackFirst`...)；只 Hide 当前那个，队列会立刻 `Pop()` 续上下一个 → 永远清不完。

**正确顺序（实测安全，不碰全局 cts、不卡死）**：
```
# 1. 先清空待弹队列(只 Pushes.Clear()，不 CancelGlobalCts，安全)——断掉"续杯"
client.py invoke --type UI.WndMgr --member ClearPushes --kind call
# 2. 读 UIRoot 子节点，找 state 含 "Shown_HasFocus" 的弹窗(排除 UIMain/UIGMButton/UIHUD*/UITopResource/UIMarquee 这些常驻)
client.py eval --code 'UnityEngine.GameObject.Find("UIRoot").transform.childCount'
client.py eval --code 'UnityEngine.GameObject.Find("UIRoot").transform.GetChild(<i>).name'   # 返回 "UIXxx [state: Shown_HasFocus, layer: Window]"
# 3. 对每个在显示的弹窗 Hide(bare 名，即去掉"(Clone)"/去掉命名空间)；队列已清空，不会再续
client.py invoke --type UI.WndMgr --member Hide --kind call --args '"UIActvSevenLogin"' false --arg-types System.String System.Boolean
# 4. 循环 2-3 直到无 Shown_HasFocus 弹窗 → 干净主城
```
- `Hide(bareName)` 用 **GameObject 名去掉"(Clone)"** 作类型名即可命中(`WndMgr.Hide(string)` 遍历容器 `GetUI(typeName)`)；`GetByTypeName("UI.Xxx")` 全名反而常匹配不上，别纠结全名。
- ⚠️ **绝对禁用 `HideAll()` / `Clear()` 后再 `Show`**：二者会 `CancelGlobalCts()`，之后任何 `Show` await 已取消的 cts → 主线程跑死、内存飙 3GB+、Unity 假死、HTTP 桥同死。`ClearPushes()` 不在此列(它只 `Pushes.Clear()`)。

### ★截招募界面：真实入口打开没问题；卡死只来自"非法 Show 手段"（已纠正）
- **结论(2026-06-24 实测纠正)**：通过**游戏正常入口手动打开** `UIHeroLottery`，界面显示正确、可正常 `ScreenCapture` 截图，**不卡死**。服龄 175/210 天循环态的招募 UI 本身没问题；at-rest 210 天内存稳定在 ~3.2GB(用 PowerShell 盯，不刷桥)，freeze 全是**动作触发**不是被动泄漏。
- 卡死的真凶是**反射强开手段**，不是招募 UI 也不是倒计时：① `WndMgr.Show(typeof(UIHeroLottery), forceNewRecord=true)` 真实跑到内存 3GB+(死循环/狂分配)；② `HideAll()`/`Clear()` 后再 `Show`(CancelGlobalCts→Show 挂)；③ GM 一次猛跳服龄的同步爆发(几十次 day-update + 一次性下发 ~45 个 Ark 活动)叠在已加载态上。一度归因到 `GetFormatTime` 倒计时是**误判**(那段日志是更早 forceNewRecord 跑飞留下的)——教训：循环检测要锁定卡死那一刻的尾部日志，别把整段会话日志当现场。

### ★★桥能力边界：为什么"手动能开招募、桥开不了"（同类截图任务必看）
- `UIHeroLottery` 进入 `Shown` 必须拿到**非空 `UIHeroLotteryData`**(带 `selectedDrawCardID`)。真实入口(上架英雄气泡→对话→`ShowHeroRecruitUI`、`UIItemInfo`、`FunctionJump(HeroRecruit=17)`)都在 C# 侧 `new UIHeroLotteryData{...}` 传进去 → 正常显示。
- **桥(HTTP/MCP reflection)做不到**：① `ConvertArg` 用 `Convert.ChangeType`，**无法从 JSON 构造自定义类**(`UIHeroLotteryData`)→ 反射 `Show` 只能传 `null` → UI 卡在 `Loaded` 永不 `Shown`(`forceNewRecord=false` 不崩但不显示；`=true` 直接跑死)。② 想改走真实入口 GMJump/FunctionJump 也够不着：`Singleton<T>.Instance`(如 `GMDebug.GMDebug.Instance`、`TimeCycleManager.Instance`)和泛型 `GameApp.I.GetModule<T>()` **反射桥都报 "Member not found"/无法调泛型**。
- **所以**：用桥给"需要 UIData 的业务 UI"全自动截图是结构性做不到的。两条出路 —— (a) **让真人手点一下真实入口**(传数据、秒开)，我只管 `ScreenCapture`(最省，凌霜那张就是这么来的)；(b) 写一个**窄口径 C# 调试探针**(在 C# 侧 `new UIHeroLotteryData{selectedDrawCardID=开放池}` 再 `WndMgr.Show`)绕过桥不能造对象的限制——但要改脚本+重编译(退 Play、丢当前服龄态)。
- **下次同类怎么办**：核心验证一律靠代码(`GetOpenCardPoolIDs()`+`CDrawCards.I().CostType`)定论，**不依赖截图**；要界面截图就走真人手点或 C# 探针，**别指望桥反射能开带数据的 UI**，更别用 `forceNewRecord=true` / `HideAll`+`Show`。

### 开 UI：优先真实入口
- 招募真实入口 = 主城"上架英雄气泡" `UIHUDUpHeroBubble`(`UI/HUD/HUDMap/Element/UIHUDUpHeroBubble.cs:44`)：点气泡→NPC对话→对话结束才 `Show<UIHeroLottery>(selectedDrawCardID=开放池)`。或 `FunctionJump.Jump(FunctionJumpType.HeroRecruit=17)` 走行为树 `ShowHeroRecruitUI`。
- 反射强开 `WndMgr.Show(Type,...)`：非泛型重载有 3 个(Type/int/泛型各 8 参)，**必须给全 `--arg-types`** 才能消歧：`System.Type UI.UIData System.Boolean "System.Action`2[[System.Object, mscorlib...],[UI.UIBase, Framework...]]" System.Object System.String System.String System.Int32`。**且只用 `forceNewRecord=false`、不要在 HideAll 后调**——即便如此对 UIHeroLottery 仍不稳，优先真实入口。

---

## 模板（新增配方时复制）
```
## 配方 N · <功能名>（关键 ID / ActvType）
### 触发条件（同时满足）
### 链路
### 复现步骤（GM/eval）
### 验证点（代码路径 + UI）
### 坑
```

---

## 配方 12 · 折扣券/装扮大转盘 UI 验证（LuckyWheel，ActvOnline 10102x / LuckyWheel 102x）
2026-06-24 X3NEW-737 验证沉淀。转盘面板 `UIActvLuckyWheel`，渲染在全屏活动中心 `UIActvMainPanel` 内。

### 关键映射
- `ActvOnline 101024` → `CActvOnline.I(101024).ContentID` = LuckyWheel cfg `1024`（`mContentID`）。`mActivityId` = 活动实例 id（雪花，≠ cfgId，说明是**服务器部署型**活动，非玩家触发型）。
- 是否有每日免费：`CActvLuckyWheel.I(<contentID>).CloseDailyFree`（true=无免费，如折扣券 1024；false=有免费，如尼罗之辉 1023）。

### 开活动（服务器部署型，本地服）
- `telnet :26080(=23000+serverID)` → `!gm DeployServerActivity <cfgId> <start秒> <end秒>`（`GMDeployServerActivity`，仅单服活动）。
- ⚠️**坑：用服务器时间，不是真实时间**。本地服时间常被其他流程跳进（服龄模拟），end<服务器now 会报 `errCode=1017050 endTime already passed`，报错里 `now(ms)=...` 就是服务器当前时间，按它换算秒重新部署。
- 部署成功后客户端自动收到活动：`Logic.G.Player.GetMeta("activity").GetActivityIdsByCfgID(101023)` 由 `[]` 变为 `[实例id]`。

### 导航 + 读控件（纯 HTTP/MCP，无需 feval）
- 开面板：`UI.UIHelper.OpenActivityPanel(<活动实例id>)`（`OpenActivityPanel(long, bool=false)`，走真实入口经 UIActvMainPanel）。
- 拿活动面板实例：`UI.WndMgr.GetByTypeName("UIActvLuckyWheel")` —— **用短类名命中**（`GetByTypeName` 遍历容器，全名 `"UI.UIActvLuckyWheel"` 反而返回 null）。eval 可链式读其**私有字段**（reflection 桥能读 private）。
- 关键控件：`.mTFWTextRefreshTime.gameObject.activeInHierarchy` / `.text`（"下次免费"倒计时）、`.mGoUIBtnFree.activeSelf`（免费抽）、`.mGoUIBtnGem.activeSelf`（钻石付费抽）、`.mContentID`（确认是哪个转盘）。

### 驱动真实免费抽（构造"用完免费"态）
- `Logic.G.Player.GetMeta("activity").ReqStartLuckyWheel(<活动实例id>, 1, true)` → 返回 `errCode {code:0}` 即真实发包成功（等价点免费抽按钮 `OnBtnUIBtnFreeTrigger`→`ReqStartLuckyWheel(1,true)`）。抽完转盘动画+服务端回包后 UI 自动 refresh：免费按钮隐藏、付费按钮显示、倒计时按 `CloseDailyFree` 决定是否显示。
- 抽完会弹"收到物品"奖励窗盖住转盘；等其消失（或真人点确认）再 `ScreenCapture` 截干净的倒计时图。倒计时 `text` 实时递减，直接读值即定论，不必非要截图。

### 验证点（X3NEW-737 修复语义）
- `CloseDailyFree=true`（1024）：免费抽不可用分支下，倒计时控件应 **隐藏**（`activeInHierarchy=false`、`text=""`），只显示付费抽。
- `CloseDailyFree=false`（1023）：未用免费→免费按钮显示、倒计时隐藏；用完免费→付费按钮+倒计时显示且实时递减。回归不被误伤。

### 坑
- `probe.py windows/click` 走 feval(9999)，本环境 feval CLI 不在 PATH → 用不了；UI 状态一律走 HTTP/MCP `GetByTypeName` + 字段实读，截图走 `ScreenCapture.CaptureScreenshot`。
- 切分支后 Unity 在跑 reload，HTTP 桥会短暂 connection refused，等几秒重 ping 即恢复；务必 `editor_reload.py reload` 强制重编译确保跑的是分支代码（实测编译 1.61s）。

---

## 配方 5 · 英雄养成手册双版本 102702（ActvType=27 付费登录，双档二选一）
> 2026-07-06 本地服 3080 端到端跑通（QA 指引 23 项自动化 18 项）。功能：二选一购买 基础220003($29.99)/豪华220004($49.99)，购后每日登录领奖；豪华=日奖×2+第30天满勤大奖4100231；双向互斥（客户端隐藏+服务端 CheckPaySignExclusive 硬拦截）。

### 关键配置（运行时实读锚点）
- `CActvOnline.I(102702)`: ActvType=27, RechargeAmount=999(累充门禁,分), PlayerLv=[5,99], ContentID=2702, ExcludeActvIDs=[102701]（102701 反向=[102702]，双向互斥）
- `CActvLoginPurchase.I(2702)`: Pack=220003, Pack2=220004, FinalReward=4100231, Group=101；老单档 `I(2701).Pack2=0` → 新代码全旁路
- `CPack.I(220003).Price="112"`($29.99) / `I(220004).Price="116"`($49.99)
- giftId 规则：基础 giftId==activityId；豪华 giftId **按玩家实例化**，`GiftMeta.GetGiftIdByPackCfgId(activityId, 220004)` 反查（别拿别人的豪华 giftId 发包，服务器直接忽略）

### 复现步骤（纯 GM/eval）
```
# 开活动（玩家域 Meta GM，TC=0 必须给分钟数）
SendGmCmd("gmaddserveractivitybycfgid","gmaddserveractivitybycfgid 102702 43200",0)
# 过门禁：⚠️ GMBypassActivityUnlock 只补 RequireFunction/FinshTask/RechargeAmount，不补等级！新号还要 gmaddlevel
SendGmCmd("gmbypassactivityunlock","gmbypassactivityunlock 102702",0)   # 累充真实充到999（副作用：其他累充向活动会开）
SendGmCmd("gmaddlevel","gmaddlevel 6",0)                                # 升级事件即触发活动重评估，无需重登
# 购买（Editor 假支付直发 BuyGiftReq）
Logic.G.Player.GetMeta("gift").ReqBuyGift(<giftId>L, null)
# 领奖（=点日奖格，一键领全部可领天）
Logic.G.Player.GetMeta("activity").ReceiveActivityAllReward(<activityId>L)
# 跨天：gmsetservertimebydhms 1 0 0 0 1（前进式）→ 直接再领，无需重登
```

### 验证点（服务端日志 game-<sid>.<date>.log 一行定论）
- 豪华双份：`EndowReward gids: 4100201,4100201,4100202,4100202,...` 每组恰好2次
- 满勤：day30 全领时 gids 末尾追加 `4100231` 恰好1次；基础买家 30 组各1次且无 4100231
- 互斥硬拦截：持一档买另一档 → `BuyGiftAck errCode=1010005`(ErrCodeGiftBuyLimit)，不扣费
- 门禁：新号(Lv1/pay0) `GetActivityIdsByCfgID(102702)==[]`；配置互斥：开 102701 时持 102702 玩家日志 `OnSeaAreaActivityCreate blocked: cfgId=102701`
- 弹窗已购态（代码锚点 UIActvLoginChoice.RefreshPurchaseState）：已购档 Owned、另一档购买键隐藏、-17%角标+划线价 showPromo=false 一并隐藏
- 豪华列预览数值 = 基础×2 + 满勤大奖内容（150=60×2+30、2500=1200×2+100），**有意设计**（UIActvLoginChoice.cs:20 注释），别当 bug

### UI 驱动
- 开主界面：`UI.UIHelper.OpenActivityPanel(<activityId>L, false)`；购买按钮路径 `UIRoot/UIActvMainPanel [state:...]/Panel/Pages/UIActvLogin [state:...]/Root/Animation/Top/choice`（probe.py click）
- 二选一弹窗带 UIData，桥反射开法：feval `new UI.UIActivityData()` + 赋 ActivityId/CfgId + `UI.WndMgr.Show(typeof(UI.UIActvLoginChoice), __d, false, null, null, "qa","qa",0)`（Show(type,null,...) 会静默不显示）
- 找按钮全路径：feval `UnityEditor.AnimationUtility.CalculateTransformPath(go.transform, null)`

### 坑（本次踩过）
- **别用 GMDebug 的"随机新建账号"**：它换 UDID+清 fast-login，本地环境新 TGS 账号默认选服 3010（本地没有）→ 断线循环，且 robot 账号被 `ErrCodeRobotLoginForbidden(1001017)` 禁登。恢复：PlayerPrefs 清 `universal_udid_key`/`udid_suffix_key`/`LoginFlag` 后重进 Play。
- **正确建新号**：登录页 feval 构造 `UICreateRoleServerData{ServerId=3080}` → `WndMgr.Show(typeof(UI.UICreateRoleTips),...)` → probe 点 `Root/btn_confirm` → 真实建号流入本地服（Lv1/pay0 干净号）。
- 服务器时间被本配方推进 +26 天且不可回退；重置需重启 GameServer 进程。
- 清理：玩家域 `gmremoveserveractivitybycfgid` 只删"玩家持有的"活动；玩家没拿到的服务器活动用 telnet(26080) `!gm ForceRemoveServerActivity <activityId>`。

### 补充（2026-07-07）：gmaddserveractivitybycfgid 适用面
- 对 **ActvType=29 进度礼包（触发式玩家活动）同样有效**（实测深海节每日礼包 102993：CreateNewServerActivity + AddNewActivityIds 直接下发给发 GM 的玩家，无需重登）——此前只在 ActvType=27 上验证过。
- 活动自带 TimeCycle（TC≠0）时 duration 分钟参数照给不冲突（102993 TC=160100 部署起算 7d，给 10080 正常开出 9/1-9/8）。
- 速查锚点：深海节每日礼包 = ActvOnline **102993**（备注"深海进度礼包"，入口组 140=深海节 Abyssal Festival，ContentID=3002，每日免费奖励 16205）。
- 102993 的界面 = **UIActvSchedulePack**（ActvType=29 进度礼包通用页，prefab `Assets/Res/UI/Prefab/Activity/UIActvSchedulePack.prefab`，嵌 UIActvMainPanel/Panel/Pages 下；partial: DayTab/LineItem）。**待确认**：部署第 6 天时页签停在 Day4 且 Day5 锁——Day 解锁像是"购买推进"而非纯天数推进，未买任何档，未验证。

---

## 配方 6 · 储蓄罐HUD挂件跨天行为验证（UIWidget挂件/UTC自然日CD类通用）
> 2026-07-07 本地服 3080 全自动跑通（无人工点击）。功能：UIHeroLottery 内 UIPiggyBankHudEntry 挂件（美酒池显示/红点/CD倒计时/登录弹窗/BI）。

### 关键手法（同类"跨UTC日重置"功能全适用）
1. **跨天 = `gmsetservertimebydhms 1 0 0 0 1`**（前进式,+1天;客户端GameTime跟服务器走,倒计时/UTC日判定立即联动）。⚠️跳天会触发登录弹窗队列(UIActvSevenLogin等)抢焦点挡住后续Show——跳完先 `ClearPushes`+`Hide(bareName)`。
2. **开 UIHeroLottery（带UIData的UI）**：feval 三条命令（lint禁分号,拆开;同一 run 会话变量共享）：
   `var __d = new UI.UIHeroLotteryData()` / `__d.selectedDrawCardID = <池id>` / `UI.WndMgr.Show(typeof(UI.UIHeroLottery), __d, false, null, null, "qa", "qa", 0)`
3. **读挂件状态（不靠截图定论）**：client.py eval 链式读私有 `UI.WndMgr.GetByTypeName("UIHeroLottery").mUIPiggyHud.mGoRedPoint.activeSelf` / `.mTxtCd.text` / `.mGo.activeSelf`。⚠️GetByTypeName 对 Hidden 实例可能返 null,读之前确保 Shown。
4. **模拟点击**：`probe.py click --path "PiggyBankHud"`——**节点激活时裸名就行**（GameObject.Find 全局搜），不用拼全路径（窗口GO名带动态"[state:...]"后缀拼不了）。
5. **BI 断言看日志**：`%LOCALAPPDATA%/Unity/Editor/Editor.log`——TraceUserClick 渲染为 `BI UserClick:ctrlID <id>`（明文可 grep）；TraceApplicationLog 渲染为 `[BI] pb_client_application_log`+调用栈（事件名在pb载荷不外显，靠栈行 attribution）。
6. **编译核验**：`System.Type.GetType("UI.<新类>, GameMainLogic")`——Assets/Scripts 下的类在 **GameMainLogic** 程序集，不是 Assembly-CSharp（查错程序集永远 null 假阴性）。命令行 commit 后 Editor 不自动编译，先 `editor_reload.py reload`（hasErrors:false 即真编译过）。

### 实测结果（2026-07-07,7项）
美酒池HUD显示✓ / 非美酒池隐藏(池1,7001)✓ / 均CD态=倒计时17:49:11到明日UTC0点+红点灭✓ / **界面开着跨0点:倒计时onEnd自动切回红点态✓** / 弹窗(可买+美酒0+每登录一次:重进弹一次、再进不弹)✓+均CD时不弹(负例)✓ / 点击(红点熄+GamePlayerPrefs记日20703+跳获取途径)✓ / 跨天红点重亮✓ / BI三事件留痕✓。未测：低等级隐藏(需新号,逻辑复用CheckCanShowGift)、重登弹窗复弹(static标记,双审过)、真机BI上报。

### 配方6补充：feval 表达式两坑（2026-07-07 实测）
- **float 后缀 `120f` 不吃**（`Syntax Error: unexpected token 'f'`）→ 写整数 `120`，隐式转换。
- **运行时校准 UI 位置的手法**：feval `GameObject.Find("<激活节点名>").transform.localPosition = new UnityEngine.Vector3(x, y, 0)` 挪 → 截图裁底部 3x 放大看效果 → 收敛后把**磁盘 prefab 里的 m_AnchoredPosition** 按同 Δ 改掉再 commit（⚠️别直接抄运行时 anchored 值——先 grep prefab 确认磁盘当前值，按增量改；本案磁盘值 755,94 与子代理报告的 81,260 不一致，盲信报告会改错）。
