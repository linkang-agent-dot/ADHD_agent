---
name: reference_x3_unity_mcp
description: X3 客户端工程的 unity-mcp（Unity 自动化 MCP）现状与 Windows 起法
metadata: 
  node_type: memory
  type: reference
  originSessionId: b2f737cc-3f63-4bec-a64b-fe41d0162e6e
  modified: 2026-07-24T10:17:17.510Z
---

X3 客户端 Unity 工程可用 **unity-mcp**（CoplayDev）做 Unity Editor 自动化，做 X3 客户端 GUI / prefab / 资源类活时可考虑走它。

**现状（2026-06-18 诊断）**：
- 包**已装**：`C:\x3-project\client\Packages\manifest.json` 已有 `com.coplaydev.unity-mcp`（无需再 Package Manager Add）。工程另有内部包 `com.tfw.unity-editor-debug-mcp`。
- **uv 已装**：`C:\Users\linkang\.local\bin\uv.exe`（0.11.21，官方装法 `irm https://astral.sh/uv/install.ps1 | iex`，**Windows 不能用 brew**）。uv 自带独立 Python，本机系统 Python 3.14 不影响。
- Unity 版本 2022.3.61f1c1。

**架构（关键，别被网传 Mac 指引误导）**：包里**只有 Unity C# 侧（Editor/Runtime），不含 Python server**；server 走 `uvx` 从 **PyPI** 现拉现跑（不是 git clone，避免 Windows 长路径）。Unity 窗口的「Register with Claude Code」本质就是跑 `claude mcp add`（见包内 `Editor/Clients/Configurators/ClaudeCodeConfigurator.cs` + `McpClientConfiguratorBase.cs:905`）。cc 要看到 server 只需注册成功，**Unity 不开也能连上**；但要工具真能操作 Unity，必须 Unity 开着且 **Bridge=Running**。

**✅ 已验证可用的注册法（2026-06-18，绕开 Unity 窗口，直接命令行）**：
```powershell
cd C:\x3-project
claude mcp add --scope local --transport stdio UnityMCP -- "C:\Users\linkang\.local\bin\uvx.exe" --prerelease explicit --from "mcpforunityserver>=0.0.0a0" mcp-for-unity
```
- 包名固定 `mcp-for-unity`；`--from` 源由包版本决定：**预发布版(如9.7.2-beta.4)→`--prerelease explicit --from mcpforunityserver>=0.0.0a0`**；正式版→`--from mcpforunityserver==<版本>`（逻辑在 `Editor/Helpers/AssetPathUtility.cs:213 GetMcpServerPackageSource`）。
- `--scope local` 写进 `~\.claude.json` 的 `projects["C:/x3-project"].mcpServers`（绑该工程，非全局）。撤销：`claude mcp remove UnityMCP`（在 `C:\x3-project` 下）。
- 冒烟验证：`uvx ... mcp-for-unity --help` 能输出 usage = PyPI 通+server 启得来。

**用起来 2 步**：
1. **必须在工程根 `C:\x3-project` 起 cc**（local scope 绑这；在 `client` 子目录或 `C:\Users\linkang` 起都看不到）；`/mcp` 应见 UnityMCP。
2. Unity 开 `C:\x3-project\client` 工程即可——**stdio 模式 bridge 自动启动，无需手动开**。

**⚠️ 9.7.2-beta.4 窗口纠正（README 老了，别照它找）**：这版是组件式 UI，**没有「Unity Bridge / Start Bridge」模块/按钮**（那是旧版或 HTTP 模式说法）。stdio 传输 bridge 永远自动起（代码 `McpAdvancedSection.cs:173` "stdio always auto-starts"）。窗口里只看**连接区的状态点+文字**：`No Session`=还没 cc 连上(正常初始态，非故障)、`Session Active(xxx)`=已连、`Resuming...`=重连中。cc 在 `C:\x3-project` 起、`/mcp` 连上的瞬间状态变绿。即「没看到 Bridge 模块」是正常，不是装错。

**✅ 全程实测结论（2026-06-18~19，已跑通到 Connected）**：
- **scope 绑 git 根**：`--scope local` 注册在 `C:\x3-project`，但实际绑的是**git 仓根**，子目录 `client`（Unity 工程真身）里 `claude mcp list` 照样 `✔ Connected`，**无需在 /client 重复注册**（重注册会报 "already exists"）。所以 cc 在 `C:\x3-project` 或 `C:\x3-project\client` 起都能用。
- **红点 No Session = 正常态，不是故障**：Unity 窗口的绿点(`Session Active`)只在**有一个 cc 交互会话正活着连 Unity**时才亮；没开 cc 会话时就是红点 `No Session`。判断装没装好别看这红点，看 `claude mcp list` 出 `✔ Connected` 即成。开个 `claude` 交互会话挂着 → 窗口自动变绿。
- **窗口默认 Transport=HTTPLocal，必须手动切 `Stdio`** 才跟 CLI 注册的 stdio 对齐（切完显示 Unity Socket Port 如 6400；stdio 不用点 Start Session/Start Server）。窗口 Client Configuration 区可无视（CLI 已注册）。

**踩坑**：`.mcp.json`（项目根）只有 gitlab、没 unity；全局/项目 mcpServers 默认全空——「看不到」99% 是**根本没注册成功** + **transport 没对齐(窗口默认HTTP vs 注册stdio)**，不是 Unity 没装。包文件夹名带短 hash（`com.coplaydev.unity-mcp@e6d5df7bd1`）不含 "coplay" 全称，glob 用 `*coplay*` 能中、`*unity-mcp*` 反而中不了。

**📍 起 cc 的目录铁律（每次开新 MCP 会话先做）**：UnityMCP 是 **local scope**，写在 `~\.claude.json` 的 `projects["C:/x3-project"].mcpServers`，绑定 **git 仓根**。所以 `cd C:\x3-project`（或子目录 `C:\x3-project\client`）起 `claude` 都能 `/mcp` 看到 UnityMCP（绑 git 根，两处通用，别重注册=报 already exists）；在 `C:\Users\linkang` 等其他目录起**看不到**。要工具真操作 Unity：Unity 开 `client` 工程 + 窗口 Transport 切 `Stdio`（默认 HTTPLocal 不对齐）；红点 `No Session` 是正常初始态，cc 连上瞬间变绿。

**📸 运行时截图取证手法（验证「UI 真显示」用，2026-06-19 实战沉淀）**：验证某功能弹窗/界面**真显示在屏上**时，eval 读不到「当前已显示窗口集合」（`m_AllShownUI` 是 X2 字段，X3 没有；`WndMgr.Get` 要 Type/泛型，eval 给不了）——此时唯一手段是**截游戏画面**。走 `DebugUtils/scripts/client.py`（脚本已在仓，不依赖任何注册 skill），Bash 直接调：
```bash
cd /c/x3-project/client
python "../.claude/skills/DebugUtils/scripts/client.py" invoke --type UnityEngine.ScreenCapture --member CaptureScreenshot --kind call --args "<输出png路径>"
python "../.claude/skills/DebugUtils/scripts/client.py" eval --code "1+1"   # 空转一帧逼截图刷盘(CaptureScreenshot是帧末异步写文件,不tick一帧文件落不下来)
```
- 这是**单帧 PNG**，不是录屏；在不同状态各截一张串起来看像录屏，实为逐节点取证。
- 取证分两层：① 代码路径跑通(dedup key/flag/日志) ② UI 真显示(截图)。dedup=1 只证明「PushActivityPanel 推了窗入队」，X3 `WndMgr.Push` 是**队列式**，推窗≠立即显示(可能排在引导奖励等弹窗后)，所以截图才是显示层铁证。后来 `x3-feature-test` skill 第7步就是把此法固化。

**⚠️ Edit 模式自测的硬天花板(2026-06-26 派子agent自测220实测)**：DebugUtils 桥能连 Editor、反射求值正常(`Application.isPlaying`/`Time.frameCount` 等只读静态都读得到),但 **Editor 没进 Play 模式时**：①**无运行时**→`NetManager`(`Singleton<NetManager>`)单例**未实例化**,`Instance/RawInstance` 反射 "Member not found"→**读不到客户端连的环境(dev/beta)和 serverId**(连接信息只在运行时 `NetManager._address/_port`);②**无 Game View 渲染**→`ScreenCapture.CaptureScreenshot` 调用返回 ok 但 **PNG 永不落盘**(即便 tick 多帧),截图取证全废;③进不到任何 UI/界面→活动/礼包/奖励类**运行时验证一概够不到**。**结论:要做"某服运行时/界面/奖励"自测,必须先让 Editor 进 Play 并用测试账号登录到目标服(会改现场,需先确认)。光连桥+Edit模式只能验"桥通+是哪个工程",验不了任何服务端/运行时的东西。** 另:eval 表达式解析器**不认算术运算符 `+` 等**(报 FormatException),只能成员访问/属性读/静态方法调用,别写 `1+1`。继承自泛型基类 `Singleton<T>` 的静态 `Instance` 也解析不了(需 invoke-chain 或具体实例字段)。

**✅ Play 模式下 eval 查「连的哪个服/哪个玩家」固定姿势（2026-07-22 源码复核）**：优先读 `Logic.G.ServerID`（当前登录服，`G.cs` 的静态属性）+ `Logic.G.PlayerID`（当前玩家 ID）；先断言 `Logic.G.PlayerID > 0`，否则只代表 Editor/桥在线、玩家尚未登录。G 类必须带 `Logic.` 全限定（裸 `G.Player` 报"无法解析类型起点"）。本会话不在 x3-project 目录起也能用——DebugUtils 桥走 client.py，不依赖 MCP local scope。

**✅ DebugUtils 桥 `recompile` 验代码改动能否编译（不进 Play，2026-07-24 士兵装备服龄门 T2 实测）**：验"某处代码/生成码改动 Unity 整体编译过不过"不用进 Play、不用开第二个 editor——`python "../.claude/skills/DebugUtils/scripts/client.py" recompile --timeout 180` 会触发脚本重编译并等完成，返回 `{success:bool, hasErrors:bool, compilationTime:秒, message}`。手法：把改动落到 .cs（如往 `FunctionType.cs` 插一个枚举成员）→ recompile → 看 `hasErrors:false` = 编译过 → `git checkout` 还原 → 再 recompile 回基线。CSSharedHotfix 这类 hotfix 程序集重编译 ~120s（会超单次 120s 前台超时，跑进后台等通知即可）。纯加法且无引用的枚举成员编译必过,是低风险可逆验证。

**⚠️⚠️ 验"配置分支的运行时/T4"必须对齐基线:开着的 client editor 基线常≠配置分支基线（2026-07-24 血泪）**：X3 配置分支多基于 gdconfig `dev`,但手头开着的 client 工程常在 `dev_festival`（节日线）。二者**分叉极大**——实测 client `dev` vs `dev_festival` **6485 文件不同(5972 在 Assets)** → 把开着的 dev_festival editor 切到 dev 基线 = 近 6000 资源重导入,不现实；且 gdconfig `dev` vs `dev_festival` 的 ActvOnline 差 **391/399 行**,基于 dev 导的 bytes 硬盖 dev_festival 会破坏其节日活动。**结论:dev 基线的配置分支,其运行时/Play-mode(T4)必须在 dev 基线的 client 上跑,不能借用 dev_festival 的 editor**。先例 `talent-awaken-gate-35d`(35天门)的 client 同名分支就是**基于 client `dev`** 建的——这是"配置分支→client 同名分支带配置制品"的标准模式,新配置分支照建。**怎么建+填充(2026-07-24 士兵装备实操)**:① `cd x3-project && git branch <name> origin/dev && git push origin <name>`(只建 ref+push,不 checkout,不碰当前分支/WIP;client 的 ProtoGen .bytes 走 **Git LFS**,别手动塞 bytes) ② 跑 `jolt_verify.py <name>`——它传 `branch=<name> code_branch=<name>` 给 Jenkins「X3导配置」job,**导表会把生成配置(ActvOnline/FunctionUnlock/TimeCycle/i18n×18语 bytes + AllTableDataMd5 + FunctionType.cs)push 到 client 同名分支**(实测 build SUCCESS→client 分支 tip 前进+22文件配置提交)。这一步的 Jenkins SUCCESS 也是导表产物层最权威的 T1 确认(比本地导表硬)。之后 dev 基线出包该 client 分支即可跑 Play-mode/T4。**导表产物层(bytes/枚举/i18n)的验证不受此限**(那是纯数据校验,基线无关,走本地导表+python 解 bytes,见 [[reference_x3_actvonline_serverlist_merged_gate]])。

**✅ Play 模式验「活动/功能门」显隐的实战手法（2026-07-24 士兵装备60天门 T4 实测，一整套跑通）**：
- **进/退 Play**：`client.py invoke --type UnityEditor.EditorApplication --member EnterPlaymode/ExitPlaymode --kind call`。进 Play 触发域重载，桥短暂"连接被拒"，游戏 GameBoot 引导~75s 后自动登录（清库后建新号）。登录成功判据=`Logic.G.PlayerID`>0（服务器日志 `UID[x] OnLogin`+`LoginAck errCode:0`）。
- **🔴 eval/invoke 解析器硬限（踩了一圈）**：①**不支持 `typeof`**（"无法解析字面量 typeof"）②**不支持泛型**（`GetMeta<T>()` 调不了）③**重载歧义**（`GetComponent(Type)` vs `GetComponent(String)` 报"请提供 argTypes"，但 eval 表达式和 invoke-chain 的 step 都没法带 argTypes）④**invoke 返回对象是整体序列化、无实例句柄**（拿不到 instanceId 去 `--target-instance-id` 链式）⑤ Singleton<T>.Instance 解不了。**逃生门=找【静态方法/静态扩展方法】直接调**——玩家 meta 的实例方法够不到时，翻 `UIHelper.*` 等静态包装。
- **✅ 查功能门解锁状态的确定性姿势**：`client.py invoke --type "UI.UIHelper" --member IsUnlock --kind call --args <functionID> false --arg-types "GameCommon.Const.FunctionType" "System.Boolean"` → 返 true/false。`UIHelper.IsUnlock(this FunctionType,bool)` 是**静态扩展方法**（`UI/Tools/UIHelper.FunctionUnlock.cs:8`），绕开了取玩家 FunctionUnlockMeta 实例的所有障碍。这是验 FunctionUnlock 门（如服龄门 RequireFunction→FunctionUnlock→TimeCycle）最干脆的一招。
- **活动渲染位置判定**：`ActvOnline.MainEntrance=空 + Calendar=1` → 活动在**活动日历**（`UIActvMainPanel`/`UIActvCalendar`）里显示，**不在主城 HUD 悬浮**。所以某活动"主城看不到"未必是门关，先查 MainEntrance/Calendar 列判断它本该在哪显示。打开活动中心=静态 `UI.UIHelper.OpenActivityPanel(long activityId, bool)`。日历过滤用 `ActivityMeta.CheckActivityIsUnlock/CheckCanShowActivityErr(cfgId)`（`ActivityMeta.cs:447`，含 RequireFunction→FunctionUnlock 门）。
- **GM 造门测试态**：本地服 GM（`x3_gm.py "!gm @<uid> ..."`）`GMAddServerActivityByCfgId <cfg> <分钟>` 开活动 → `GMSetServerTimeOffset <开服日+N天>` 推服龄过门（**只能前进不能退**；跳时间后原活动窗口若被跨过要 Remove+重开）→ **退登重进** Play 让客户端重新评估门 → `UIHelper.IsUnlock` + 截图取证。dev 基线配置分支的完整实机链=切分支(6000资源重导~90s)→重编 Hotfix→drop_db 清库→起 Game→wait_server_info→起 Map→Play 登号→GM 造态，见 [[workflow_x3_local_server_gm_telnet]]。

相关：[[reference_x3_project_repo]] [[reference_x3_client_new_ui_workflow]] [[reference_x3_actvonline_serverlist_merged_gate]] [[workflow_x3_local_server_gm_telnet]]

## Unity 官方 CLI：X3 当前定位（2026-07-22 实测）

- 本机已安装官方实验版 `unity.exe 1.0.0-beta.2`：`C:\Users\linkang\AppData\Local\Unity\bin\unity.exe`，用户 PATH 已写入。
- `unity editors -i --format json` 可识别本机三套 Unity 2022.3；X3 工程版本为 `2022.3.61f1c1`。
- CLI 本体可用于编辑器/模块管理、打开项目、批处理 `run`、`build`、EditMode/PlayMode `test`、日志与诊断。
- 官方 `com.unity.pipeline`、`unity command`、`unity status` 连接、官方 `unity mcp` 和实时 C# eval 依赖 Unity 6.0 LTS+；**X3 当前禁止尝试安装 Pipeline**。CLI 帮助里出现这些命令，不代表 Unity 2022 项目侧可用。
- X3 已有构建入口：`TFWEditor.X3Builder.BuildAndroid`、`BuildAndroidAAB`、`BuildExeChoice`。CLI 只负责批处理启动，SDK/签名/资源/HybridCLR/产物路径仍由 X3 构建链负责。
- Codex 托管 PowerShell 可能缺 `ALLUSERSPROFILE`，CLI 会报 `Unable to resolve config folder`；仅对当前进程补 `$env:ALLUSERSPROFILE='C:\ProgramData'`，不要为此改系统级配置。

**固定路由**：编辑器外层生命周期/批处理 → Unity CLI；场景/Prefab/当前 Editor → CoplayDev Unity MCP；Play Mode 玩家状态/截图/运行时取证 → DebugUtils；官方 Pipeline/eval → 仅 Unity 6+。详细执行门见 `C:\Users\linkang\.agents\skills\x3-feature-test\references\unity-cli-routing.md`。
