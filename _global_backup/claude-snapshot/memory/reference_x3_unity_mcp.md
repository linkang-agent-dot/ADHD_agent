---
name: reference_x3_unity_mcp
description: X3 客户端工程的 unity-mcp（Unity 自动化 MCP）现状与 Windows 起法
metadata: 
  node_type: memory
  type: reference
  originSessionId: b2f737cc-3f63-4bec-a64b-fe41d0162e6e
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

相关：[[reference_x3_project_repo]] [[reference_x3_client_new_ui_workflow]]
