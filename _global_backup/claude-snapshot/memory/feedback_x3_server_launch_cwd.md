---
name: feedback-x3-server-launch-cwd
description: 手工启动 X3 GameServer.exe 必须把 cwd 设到 server\Resource\，不是 server\，否则启动期 log4net 加载抛 DirectoryNotFoundException
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 660873db-122f-4e9f-84f0-77d522e033b9
---

手工启动 X3 服务端进程时（`GameServer.exe` / `MapServer.exe` / `CenterServer.exe`），cwd 必须是 `C:\x3-project\server\Resource\`，不能是 `C:\x3-project\server\`。

**Why:** 三个 csproj（GameServer/MapServer/CenterServer）都设了 `<RunWorkingDirectory>../Resource</RunWorkingDirectory>`，所以 `dotnet run --project ...` 或 `start_local_server.bat` 启动时 cwd 自动是 `Resource\`。代码里 `ServerCommon\Logging\LoggerUtils.cs:55` 用 `new FileInfo("config/log4net.xml")` 相对 cwd 加载 log4net 配置 — `Resource\config\log4net.xml` 是真实文件，`server\config\` 不存在。cwd 错了启动就抛 `DirectoryNotFoundException`，进程立即崩，但 `Start-Process` 不重定向 stderr 时看不到错误，进程会以 HasExited=False 的僵尸状态挂着，看起来像 hang。

**How to apply:**
- 用 `Start-Process` 启 GameServer.exe：`-WorkingDirectory 'C:\x3-project\server\Resource'`
- 一定加 `-RedirectStandardError 'C:\path\to\err.log'`，启动失败时第一时间看到 .NET 异常
- 完整启动命令行从原进程拷（`Get-CimInstance Win32_Process -Filter "ProcessId=<pid>"`）：
  ```
  GameServer.exe -sid <sid> -nid <sid> -csid <centerid> -e local -ll debug -lf logs/game-<sid>.log
  ```
- 重启单个 GameServer：`Stop-Process -Id <pid> -Force` → `Start-Process ... -WorkingDirectory server\Resource ...` → 轮询 `Test-NetConnection 127.0.0.1 <23000+sid>`
- 想省事就直接跑 `server\Tools\start_local_server.bat skip-link`，但 bat 会同时起 GameServer+MapServer 两个（按 local_conf.ini 里的 sid）；只想动一个进程时不能用 bat
- bat 会先 `dotnet build` 两个 Hotfix 工程（连带重编主程序，约 40s，带上最新代码），再 `start` 两个新窗口跑 `dotnet run`，末尾有 `pause`。非交互环境（Claude Code 后台跑）必须喂掉 pause，否则永久挂起：用 `echo. | cmd /c "...bat skip-link"`。**别用 `< nul` 重定向** —— cmd 的 pause 会报 `ERROR: Input redirection is not supported` 然后立即退（虽然 servers 在 pause 前已起好、不影响结果，但日志难看）。建议 `run_in_background` 跑，完成后轮询 26080/26081 确认。

**telnet 端口公式（来自 [[reference_x3_project_repo]]）：** `23000 + NodeID`
- GameServer: `23000 + sid`（sid=3080 → 26080）
- MapServer: `23000 + sid + 1`（sid=3080 → 26081）
- CenterServer: `23000 + centerid`

热重载用 telnet 发 `!gm ReloadGameServer` 就够（3.8s 不掉玩家），只有 core/proto 改动才需要进程重启。判断标准在 [[reference_x3_project_repo]] 提到的 server_reload.py classify。

## ⚠️ Claude Code headless 后台「重新Build接入最新配置」别用 start_local_server.bat

`start_local_server.bat` 用 `start "title" dotnet run`（行53/56）开**新控制台窗口**跑服，外加结尾 `pause`。在 Claude Code 的无窗口站后台环境里：① Bash 工具里 `echo. | cmd /c "...bat skip-link"` 的 `echo.` 不是 bash 命令（`command not found`），pause 喂不进去；② 即便喂进去，`start` 开的新窗口在 headless 下存活不了。实测后果：bat 秒退（根本没跑 ~40s 的 dotnet build）、两个服直接挂掉、端口不监听。

**✅ 一键脚本（2026-06-17 沉淀，下次"重新部署/接入最新配置"直接用，别再手敲）**：`pwsh C:\Users\linkang\x3_redeploy.ps1 [-Sid 3080] [-CenterId 61] [-ForceBuild]` —— 自动跑完下面整条链路：查 gdconfig 新旧 → mtime 预检(config .bytes vs dll, 新就重编) → `stop_gs` → 按需重编双 Hotfix → `Start-Process` 起 Game+Map → 轮询端口 + 验日志 `PlayService started` 无 protobuf 异常。不清库、GM 活动(MongoDB)重启保留。**用 `run_in_background` 跑**(含 dotnet build ~2-3min + 轮询)，完成看输出尾部 `[OK]`/`[FAIL]`。

**headless 可靠链路（脚本背后的手动步骤，排障时参考）**：
1. 先把两个 Hotfix build 出来（`dotnet build` 在 server 目录，~40s+35s）：
   ```
   cd C:\x3-project\server
   dotnet build GameServer.Hotfix\GameServer.Hotfix.csproj   # 确认 0 错误
   dotnet build MapServer.Hotfix\MapServer.Hotfix.csproj      # 确认 0 错误
   ```
2. 停旧进程：`Stop-Process -Id <GameServer pid>,<MapServer pid> -Force`
3. 用 `Start-Process` detached 拉起（`--no-build` 复用步骤1产物，**必带 `-RedirectStandardError`** 否则启动崩了看不到异常，`-WorkingDirectory` 用 `server`，dotnet run 会按 csproj RunWorkingDirectory 自动切到 Resource）：
   ```powershell
   Start-Process dotnet -ArgumentList 'run','--project','GameServer','--no-build','--','-sid','3080','-nid','3080','-csid','61','-e','local','-ll','debug','-lf','logs/game-3080.log' -WorkingDirectory 'C:\x3-project\server' -RedirectStandardError '...\game-err.log' -WindowStyle Hidden
   # 等 ~5s 再起 MapServer：nid=3081（=sid+1），其余同
   ```
4. 轮询 `Test-NetConnection 127.0.0.1 -Port 26080/26081` 至 True；不 up 就 tail err.log。干净启动 err.log = 0 字节。

`-csid`=local_conf.ini 的 centerid（3080 服=61），`-nid` GameServer=sid、MapServer=sid+1。配置真源：服务端读**内嵌** `C:\x3-project\gdconfig\`，重启前确认它已 ff 到最新（`cd gdconfig; git rev-list --left-right --count @{u}...HEAD` = `0 0`）。
