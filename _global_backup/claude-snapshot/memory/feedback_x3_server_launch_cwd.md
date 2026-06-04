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

**telnet 端口公式（来自 [[reference_x3_project_repo]]）：** `23000 + NodeID`
- GameServer: `23000 + sid`（sid=3080 → 26080）
- MapServer: `23000 + sid + 1`（sid=3080 → 26081）
- CenterServer: `23000 + centerid`

热重载用 telnet 发 `!gm ReloadGameServer` 就够（3.8s 不掉玩家），只有 core/proto 改动才需要进程重启。判断标准在 [[reference_x3_project_repo]] 提到的 server_reload.py classify。
