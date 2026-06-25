---
aliases: [X3实机验证, DebugUtils实机验证, 客户端功能验证方法论]
tags: [kind/方法论, proj/X3, type/实机验证, tool/DebugUtils]
created: 2026-06-24
---

# X3 客户端功能实机验证（DebugUtils HTTP/MCP 桥）

> 场景：拿到一个客户端改动/MR，要在 Unity Editor + 本地服上验证"显示对不对、有没有误伤"，而不是只读代码下结论。
> 首次沉淀来自 X3NEW-737 折扣券大转盘 NextFree 验证（见 [[_README|产出归档]]）。
> 本文是**人看的方法论 + 踩坑清单**；可执行的桥用法见 live skill `DebugUtils`，按功能配方见 `x3-feature-test/references/recipes.md`。

## 核心打法：能实读控件值就别只靠肉眼截图
验证 UI 显示，**最强证据是运行时实读控件状态**（`activeInHierarchy` / `text` / 按钮 `activeSelf`），截图只作视觉佐证。游戏窗口小、截图文字糊，肉眼"看着差不多"会误判；实读值是确定的。

标准链路（8 步裁剪）：
1. 切分支 → `git diff dev...HEAD` 确认改动面。
2. **强制 recompile** 确保跑的是分支代码：`editor_reload.py reload`（实测 X3 编译 ~1.6s）。看返回 `hasErrors=false` 即"① 编译通过"。
3. 实读配置前提（`GameCommon.Cfg.C{表}.I(id).{字段}`），确认 bug 触发条件在配置上成立。
4. 实读运行时控件状态（见下"拿 UI 实例"）。
5. 不满足前置就用 GM 构造（开活动 / 升级 / 加资源）。
6. 走**真实业务入口**驱动（发真实请求，别强塞数据）。
7. 截图 + 控件实读双取证。
8. 报告分档 + 沉淀配方。

## 关键手法（X3 实测可用）
- **登录/玩家**：`Logic.G.PlayerID`、`Logic.G.ServerID`、`Logic.G.Player.GetMeta("activity"/"basic"/"pay"...)`（Meta 名是字符串，见 `MetaConst.cs`）。
- **拿已显示的 UI 实例**：`UI.WndMgr.GetByTypeName("UIXxx")` —— ⚠️**用短类名**（全名 `"UI.UIXxx"` 反而返回 null）。返回 `UIBase`，eval 可链式读其**私有字段**（reflection 桥能读 private，如 `.mTFWTextRefreshTime.gameObject.activeInHierarchy`）。
- **开活动面板（真实入口）**：`UI.UIHelper.OpenActivityPanel(<活动实例id>)`。
- **活动是否开**：`...GetMeta("activity").GetActivityIdsByCfgID(<cfgId>)`，`[]`=未开。
- **截图**：`UnityEngine.ScreenCapture.CaptureScreenshot(<绝对路径>)`，之后再发几个无副作用 eval 走帧让文件落盘，再 Read png。
- **本地服 GM**：telnet `23000+serverID` → `!gm <Cmd> <args>`（server-scope）/ `!gm @<pid> <Cmd>`（player-scope）。玩家域 GM 也可走客户端 `GetMeta("basic").SendGmCmd(...)`。

## ★坑清单（这次真踩的，按出现频率排）
1. **`DeployServerActivity` 要用服务器时间，不是真实时间**。本地服时间常被其它流程跳进（服龄模拟，这次被跳到 2026-09-27）。end < 服务器now 会报 `errCode=1017050 endTime already passed`，**报错文本里 `now(ms)=...` 就是服务器当前时间**，按它换算秒重发即可。
2. **`probe.py windows/click` 走 feval(9999)，本机 feval CLI 不在 PATH → 用不了**。所有 UI 状态/窗口枚举改走 HTTP/MCP（`client.py eval` + `GetByTypeName` + 字段实读），点击类操作改用 `OpenActivityPanel`/直调业务方法。Editor 默认就该走 HTTP/MCP，别等 feval。
3. **切分支后 Editor 在跑 domain reload，HTTP 桥短暂 connection refused**（不是挂了），等几秒重 `client.py ping` 即恢复；端口 21891 起，fallback 21892/21893。
4. **`GetByTypeName` 全名匹配不上**（见上，用短名）。
5. **`WndMgr.GetLayerUIs(layer)` 经 eval 序列化 list 不展开**（拿不到层内窗口清单）；要定位某弹窗类名时，靠 grep UI 源码（按标题文案/Auto_* 生成类）比枚举层更快。
6. **奖励弹窗盖住目标面板**：真实抽奖后会弹 `UIItemObtain` 之类"收到物品"窗；等它消失或真人点确认再截干净图。但**判定别依赖这张图**——控件 `text` 实读值已定论（如倒计时 `"下次免費：HH:MM:SS"` 在实时递减就证明 timer 活着）。

## 报告与归档
- 自包含 HTML（截图 base64 内嵌）一份即可转发，无需另发图。
- 归档到 `KB/产出-验证报告/<单号_功能名>/`，挂首页"产出归档"。
- 透明交代环境改动（测试分支未提交、GM 临时开的活动、测试号被改的状态），供回滚判断。
