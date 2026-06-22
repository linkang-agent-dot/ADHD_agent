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

## 模板（新增配方时复制）
```
## 配方 N · <功能名>（关键 ID / ActvType）
### 触发条件（同时满足）
### 链路
### 复现步骤（GM/eval）
### 验证点（代码路径 + UI）
### 坑
```
