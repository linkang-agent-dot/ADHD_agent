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

相关：[[reference_x3_project_repo]] [[reference_x3_client_new_ui_workflow]]
