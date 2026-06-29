# 桥调试踩坑 · 便携精简版（随 skill 传播）

> 这是本 skill **自包含**的精简知识，复制/分享 skill 时这些就跟着走。下面 5 条是"开箱即用"的最小集。

## 想要更全 / 接入自动提醒？拿到这份 skill 后这样整合（按需，自助）
本文件只是精简版。**更全的内容不打包进来**（避免过期、避免和你本地环境冲突），由你按需自己接：
1. **配方全文**：同目录 `recipes.md` 配方 2（GM 跳服龄验证法全流程）/ 配方 3（关弹窗 + 桥能力边界），是这 5 条的展开版，先读它。
2. **接入 preflight 自动提醒**：若你本地装了 `DebugUtils` skill，本会话已把对应教训写进它的 `memory/lessons.jsonl`（tags：`wndmgr-trap` / `popup-close` / `editor-hang` / `bridge-limit`）。换机器/换仓库要带走的话，把这些条目 `grep` 出来追加到你那份 `DebugUtils/memory/lessons.jsonl`，之后 `preflight_check.py` 就会在同类场景自动捞出来。
3. **跨会话事实**：项目 memory `~/.claude/projects/<proj>/memory/x3-recruit-pool-*.md`（招募池开关客户端算 + GM 跳服龄法），要带走就复制该 md 并在 `MEMORY.md` 加一行索引。
4. **不确定就反过来**：先只用本文件 + `recipes.md` 干活，撞到本文件没覆盖的坑，再去上面三处翻——别一上来就整合一大坨。

源头：2026-06-24 验 X3NEW-592（限时招募池断档）。适用于一切"用 DebugUtils 桥给 X3 业务 UI 取证/截图"的任务。

## 1. 验"按服龄排程"的功能 → GM 推进服务器时间，别找老服
- 招募池/TimeCycle 这类开关是**客户端按"开服时间+当前时间"自算**的，把服务端时间往前推即可模拟服龄。
- `Logic.G.Player.GetMeta("basic").SendGmCmd("gmsetservertimebydhms","gmsetservertimebydhms <天> 0 0 0 1",0)`（**前进式，不支持回退**；target=1=仅 Game 服）。
- 重置服龄要重启 GameServer 进程（独立于 Unity，只杀 Unity 不复位时间）。

## 2. 关登录弹窗 → ClearPushes() 先停，再 Hide(bareName) 逐个
- 跳服龄/登录会经 `WndMgr` 的 **push-queue** 连发弹窗（`UIActvSevenLogin`→`UIPackCommonPop`→`UIGameScore`…），只 Hide 一个会被队列 `Pop()` 续上，清不完。
- 安全顺序：① `invoke WndMgr.ClearPushes`（只 `Pushes.Clear()`，不碰 cts，安全）→ ② 读 `UnityEngine.GameObject.Find("UIRoot").transform.GetChild(i).name` 找 `Shown_HasFocus` 的弹窗 → ③ `Hide(bare类型名)` 逐个（bare 名=GameObject 名去"(Clone)"/去命名空间）。
- **禁忌**：`HideAll()` / `Clear()` 后再 `Show` → 它们 `CancelGlobalCts()`，之后 `Show` await 已取消的 cts → **主线程跑死、内存 3GB+、Unity 假死、HTTP 桥同死**。

## 3. 带 UIData 的业务 UI（如 UIHeroLottery）→ 桥反射开不了，别硬开
- 这类 UI 进 `Shown` 必须拿到**非空 UIData**；桥的 `ConvertArg`（`Convert.ChangeType`）**无法从 JSON 造自定义类** → 反射 `Show` 只能传 `null` → UI 卡 `Loaded` 不显示（`forceNewRecord=true` 还直接跑死 3GB）。
- 想改走真实入口 `GMJump`/`FunctionJump` 也够不着：`Singleton<T>.Instance`、泛型 `GameApp.I.GetModule<T>()` 反射桥都报 "Member not found"。
- **正解**：核心验证靠**代码读运行时值**（`GetOpenCardPoolIDs()` + `CDrawCards.I().CostType` 等），不靠截图；要截图就 (a) 真人手点真实入口（传数据、秒开）我只 `ScreenCapture`，或 (b) 写窄口径 C# 探针在 C# 侧 `new` 好 data 再 `Show`。

## 4. Editor 假死 → 先读磁盘游戏日志做循环检测，别瞎猜
- 三大诱因：① `forceNewRecord=true` 反射强开带数据 UI；② `HideAll/Clear` 后 `Show`；③ GM 一次猛跳服龄的同步爆发（几十次 day-update + 一次性下发 ~45 个 Ark 活动，其倒计时同帧狂转）。**at-rest（不操作）状态是稳定的**，假死全是动作触发。
- 定位：`tail` 磁盘游戏日志（`%USERPROFILE%/AppData/LocalLow/<co>/<game>/Logs/log-*.txt`）做 `uniq -c` 循环检测，找每帧刷屏的调用链。**锁定假死那一刻的尾部日志**，别把整段会话日志当现场（我就误把更早的 `GetFormatTime` 刷屏当现场、错怪了倒计时）。
- 用 PowerShell 查 Unity 进程 `Responding`/`WorkingSet64`（不刷桥）判断是真死还是在啃负载。

## 5. 出带截图的 HTML 报告 → 用 scripts/make_html_report.py
- 别手写 base64 内联 HTML。`make_html_report.py <spec.json>` 读 JSON、把本地 PNG 内联成 data URI（Artifact CSP 禁外链图）、出单文件 HTML。范例 `samples/x3new-592/`。
