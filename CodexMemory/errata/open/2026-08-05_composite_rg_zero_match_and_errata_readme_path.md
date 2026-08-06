# 组合 rg 零匹配误报失败 + errata README 路径误判

- 日期：2026-08-05
- 任务：切 X3 客户端/配置到 dev，部署本地 3080 并开启 Bingo
- 现象：把三条 `rg` 串在同一 PowerShell 调用中，最后一条零匹配返回 exit 1，导致整次调用显示失败；随后按用户给出的 `errata/open/README.md` 读取格式说明时发现实际 README 位于 `errata/README.md`；配置仓 `git switch dev` 又因该分支已被 `C:/X3/wt_circus_float` worktree 占用而失败。
- 根因：未对探索性 `rg` 的“零匹配”退出码做隔离；未先用 `rg --files` 解析 errata README 的真实位置；切分支前只查了当前仓状态，没有先查 `git worktree list` 的分支占用。
- 处理：保留前两条有效搜索结果，后续搜索拆开运行；通过 `rg --files C:\ADHD_agent\CodexMemory\errata` 定位并读取真实 README；配置仓先审查占用 `dev` 的 worktree 状态，再决定复用或释放分支。

## 同轮 Unity bootstrap 超时

- 现象：切到 `dev` 后执行 DebugUtils `bootstrap.py --platform editor`，125 秒内无输出并超时。
- 根因：bootstrap 自动发现/拉起 Editor 的整段流程被一个外层长超时包住，无法区分 Editor 首次大规模导入与桥未启动。
- 处理：不并发重跑 bootstrap；改用 Unity 进程命令行、项目路径和 MCP 21891-21893 端口逐项只读检查，再按实际状态定向 `client.py --project`。

## 同轮 UIBase 成员误探

- 现象：`UI.WndMgr.GetByTypeName("UIActvPuzzle").gameObject.activeInHierarchy` 返回 `MissingMemberException`。
- 根因：`UIActvPuzzle` 是项目 `UIBase`，不是 `MonoBehaviour`；HTTP MCP 已直接展开其 `IsActive` / `HasFocus`，无需假设存在 `gameObject` 成员。
- 处理：以返回对象的 `IsActive=true`、`HasFocus=true` 和实际节点路径作为显示证据；后续控件从已展开字段或路径读取。

## 同轮 ScreenCapture 绝对路径未落盘

- 现象：MCP 调 `UnityEngine.ScreenCapture.CaptureScreenshot` 返回 `ok:true`，但 3 秒后目标绝对路径不存在。
- 根因：Unity `CaptureScreenshot` 的异步落盘位置/绝对路径处理未先用项目内短路径验证；仅凭调用返回无法证明文件已生成。
- 处理：先搜索实际落点；后续改用 Unity 工程内 ASCII 相对路径，等待文件出现并核对尺寸后再归档复制。

## 同轮 MCP eval 不支持嵌套 Type.GetType 参数

- 现象：在 `GetComponents(...)` 参数里嵌套 `System.Type.GetType(...)`，表达式解析报 `FormatException`。
- 根因：EditorDebugMCP 的表达式解析器只接受字面量/枚举/类型字面量作为调用参数，不支持在参数位置嵌套另一个方法调用。
- 处理：改用桥支持的类型字面量或 `invoke-chain`；不继续堆叠复杂 eval。

- 补充：改传 `UnityEngine.Component` 类型字面量后，`GameObject.GetComponents` 因 4 个重载返回 `AmbiguousMatchException`；eval 语法无法在该链上补 `argTypes`。本轮到此停止自动点格子的反射绕路，不把交互项虚报通过。

## 同轮 recipes.md 插入点落入代码块

- 现象：新增 Bingo 配方时只以首个三反引号作锚点，导致整段配方插到“模板”代码块内部。
- 根因：补丁上下文不够唯一，没有先重读模板开闭代码块的完整范围。
- 处理：重读目标段后整块重排为“模板代码块闭合 → Bingo 配方正文”，再用 `rg -C` 复核。

## 同轮 task-checker fork 参数冲突

- 现象：`spawn_agent(agent_type=task-checker, fork_turns=all)` 被编排器拒绝。
- 根因：显式 agent type 与 full-history fork 互斥。
- 处理：改用 `fork_turns=none`，在任务正文完整传递只读验收目标、路径和证据清单。

## 同轮再次把探索性 rg 零匹配当工具失败

- 现象：为定位 `client.py`/`probe.py` 执行 `rg --files ... | rg ...`，筛选结果为空并以 exit 1 结束，工具层显示失败。
- 根因：复核阶段重复使用了未隔离零匹配退出码的组合搜索，没直接使用已知 DebugUtils 路径。
- 处理：改用 `Get-ChildItem -Recurse -Filter client.py` 定位；后续已知路径直接访问，探索性筛选显式容忍零匹配。

## 复核时直接重开活动入口触发 NullReference

- 现象：checker 关闭/切离活动页面后，直接再次执行 `UI.UIHelper.OpenActivityPanel(7670528419974610944L, false)` 返回 `NullReferenceException`。
- 根因：复核时客户端当前会话对象或活动上下文已变化，未先重取当前玩家、服务器及最新活动实例就复用旧实例入口。
- 处理：先逐项探测 `Logic.G.Player` 与活动实例，再决定重登/重开；旧实例 ID 只作服务端证据，不盲目复用。

## 登录轮询使用未加载类型导致 TypeAccessException

- 现象：重新进入 Play 后等待 45 秒执行 `Logic.LLogin.I.IsLogin`，MCP 报无法解析类型起点。
- 根因：当前运行域尚未加载 HotFix 登录类型（或已退出有效游戏会话），直接把类型表达式当登录就绪探针不可靠。
- 处理：改查 `EditorApplication.isPlaying`、活动场景和 Editor.log 的启动/登录标记；仅在 `Logic` 类型可解析后读取玩家态。

## editor_reload 的 project 子串分隔符不匹配

- 现象：`editor_reload.py reload --project C:\x3-project\client` 未命中已发现的 `C:/x3-project/client/Assets`。
- 根因：工具的 project 子串匹配未归一化 Windows 反斜杠与 discovery 返回的正斜杠。
- 处理：改传稳定短子串 `x3-project/client`（或显式端口，如脚本支持），避免整条 Windows 路径。

## Select-String 扫完整 Editor.log 超时

- 现象：对完整 Unity `Editor.log` 用 `Select-String` 查登录标记，10 秒超时。
- 根因：日志体量大，PowerShell 全文件扫描不适合即时运行态复核。
- 处理：先 `Get-Content -Tail` 限定最近窗口再筛选，或使用 DebugUtils 日志采集脚本。

## 2026-08-06 组合搜索混入不存在目录

- 任务：定位马戏节排行榜奖励组内排序机制。
- 现象：并行搜索把仓库根下不存在的 `def` 与实际存在的 `Tools` 一起传给 `rg`，有效命中虽已出现，整次调用仍以 exit 1 报失败。
- 根因：未先用 `rg --files` 确认目录边界，又重复让探索性搜索的单项路径错误污染组合调用。
- 处理：后续只在确认存在的 `Tools/table_exporter/def` 和明确 TSV 文件中查；组合调用前先解析真实路径。

## 2026-08-06 PowerShell 下把通配路径直接交给 rg

- 任务：定位马戏寻宝排行榜和梦幻旋转木马道具。
- 现象：把 `tsv\Personalize*.tsv` 与错误猜测的 `tsv\Text__Text.tsv` 直接作为 `rg` 路径，Windows 报路径语法错误/文件不存在，污染并行结果。
- 根因：再次绕过 `rg --files` 做真实文件路由；Windows 下 `rg` 不负责展开这种路径通配。
- 处理：先用 `rg --files tsv | rg 'Personalize|Text'` 获取真实路径，再逐文件查询；有效结果仅保留 Item 中旋转木马 81152/81154/81156 的定位。

## 2026-08-06 空闲 ID 探针再次被零匹配污染

- 任务：为马戏寻宝新增排行榜档位/奖励组选择空闲 ID。
- 现象：用于证明候选 ID 未占用的 `rg` 返回 exit 1，导致并行调用整体失败且尾部上下文未返回。
- 根因：把“零匹配=候选 ID 空闲”的预期成功语义直接交给工具退出码。
- 处理：空闲 ID 检查改为 PowerShell 捕获 `rg` 结果并显式输出 `FREE`，不再让零匹配退出码外溢。

## 2026-08-06 ExportTable 从仓库根运行产生假 exit0

- 任务：马戏节排行榜配置本地全量导表。
- 现象：在 `C:\x3\gdconfig` 根目录运行 `python Tools\table_exporter\ExportTable.py` 返回 exit 0，但日志显示 `InputPath: C:\tsv / 源文件夹不存在，退出`，实际未导任何表。
- 根因：脚本按当前工作目录的相对层级推导输入路径，不能从仓库根直接调用；仅看退出码会是假绿。
- 处理：改从 `Tools\table_exporter` 目录按项目约定运行，并把“日志必须进入实际表处理、不能出现源文件夹不存在”列为成功条件。

## 2026-08-06 Reward TSV 审计跳错表头行

- 任务：对 81901~81908 奖励组做结构化复核。
- 现象：用 `Get-Content | Select-Object -Skip 5 | ConvertFrom-Csv` 后得到 `REWARD_ROWS=0`，与刚写入的 36 行矛盾。
- 根因：Reward TSV 的字段名行不在假设的位置，`ConvertFrom-Csv` 把错误行当表头，列名 `RewardID` 未建立。
- 处理：先带行号读取前 20 行确认真实字段名行，再按精确偏移解析；零行不得当作通过。

## 2026-08-06 冲突解完后空闲段复核又未捕获 exit1

- 现象：检查最新 `origin/dev` 是否占用 `16040000~16040035` 时，零匹配本应证明空闲，却再次让工具以 exit 1 报失败。
- 处理：结论仍是远端未占用该段；后续所有“应为空”探针统一包成显式 `FREE` 输出，不再直接运行裸 `rg`。
- 状态：open

## 2026-08-06 本地双服探测再次把通配路径交给 rg

- 任务：为马戏寻宝世界榜准备 3080 + 第二本地服跨服验证。
- 现象：组合探测使用 `rg ... tsv\Server* tsv -g "*.tsv"`，PowerShell 未展开传入的通配路径，`rg` 报 Windows 路径语法错误；同时扫描整个 `tsv` 命中超宽表头，输出严重膨胀并截断了其他并行结果。
- 根因：没有先用 `rg --files tsv | rg 'Server'` 路由真实文件，又把宽范围探索和关键配置读取放在同一个并行输出中。
- 处理：关键输出改为独立、限行调用；先解析真实 Server 表文件名，再按精确文件与精确列查询。

## 2026-08-06 误把 skill 脚本当成配置仓脚本

- 任务：查询 AO103101 的完整活动引用链。
- 现象：在 `C:\x3-project\gdconfig` 调用 `scripts\actv_lookup.py`，文件不存在。
- 根因：复用了工具名但未复核脚本实际归属；该查询器来自 `x3-config-export` skill，不在配置仓 `scripts` 下。
- 处理：后续先用 `Get-ChildItem`/已读 SKILL.md 的绝对路径确认脚本，再调用；简单字段查询可直接结构化解析 TSV。

## 2026-08-06 RankMeta 搜索第三次直接传通配路径

- 任务：定位本地跨服榜造分 GM。
- 现象：把 `GameServer.Hotfix\PlayerMeta\RankMeta*` 作为 `rg` 的路径参数，Windows 再次报路径语法错误。
- 根因：虽然同轮已经记录过 Windows `rg` 不展开路径通配，仍在后续探索中复发，说明只记录未落实为调用前检查。
- 处理：立即改为先 `rg --files GameServer.Hotfix\PlayerMeta | rg 'RankMeta'`，后续精确文件列表再交给搜索。

## 2026-08-06 把 x3_gm.py 当成 argparse CLI 调 help

- 任务：确认本地 telnet GM helper 的端口参数。
- 现象：执行 `python x3_gm.py --help`；脚本把 `--help` 当 GM 正文发往默认端口并等待，最终超时。
- 根因：未先读 helper 源码确认它没有 argparse/help 语义。
- 处理：改为只读脚本源码获取环境变量/端口参数，随后用明确命令调用。

## 2026-08-06 foreach 语句后直接接管道触发 PowerShell 解析错误

- 任务：比对本地导表产物与客户端 ProtoGen 的 MD5。
- 现象：`foreach (...) { ... } | Format-Table` 被 PowerShell 解析为包含空管道元素，命令未执行。
- 根因：没有把 foreach 输出先赋值/用子表达式包裹，直接在语句块后接管道。
- 处理：改用 `$rows = foreach (...) {...}; $rows | Format-Table`。

## 2026-08-06 再次未读源码就对无 argparse 脚本传 --help

- 任务：确认 `sync_client_manifest.py` 参数。
- 现象：脚本忽略 `--help` 并直接执行默认同步，输出“更新行数 0”。
- 根因：刚记录过同类 `x3_gm.py --help` 错误后仍重复假设任意 Python 工具都有 argparse help。
- 处理：对仓内 helper 先读顶部/主函数；只有确认 argparse 后才传 `--help`。

## 2026-08-06 PlayerMgr 搜索第四次直接传 rg 通配路径

- 任务：用本地 Roslyn telnet 对两个玩家写跨服榜测试分。
- 现象：再次把 `GameServer\Modules\PlayerMgr*.cs` 作为 `rg` 路径，Windows 报语法错误。
- 根因：同轮重复性操作没有把“先列文件”变成机械习惯，errata 记录没有阻止复发。
- 处理：停止在路径参数中使用任何 `*`；固定把搜索根限定为真实目录 `GameServer\Modules`，仅用 `-g 'PlayerMgr*.cs'` 过滤文件。
- 补充：改用 `-g` 后模式零匹配又直接返回 exit 1；探索性查询仍应捕获并输出 `NO_MATCH`，不能把“无此命名 API”留成工具失败。
- 再补充：读取 `ServerPlayer.cs` 与后续方法搜索组合调用时，前者已成功输出、后者零匹配仍让整体 exit 1。后续不再把确定性读取与探索性 `rg` 放进同一 shell 命令。
