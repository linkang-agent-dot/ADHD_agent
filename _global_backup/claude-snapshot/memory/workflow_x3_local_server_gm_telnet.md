---
name: workflow-x3-local-server-gm-telnet
description: X3 本地服调时间/发GM命令的 telnet 链路（端口算法、分包协议坑、设D30），调本地服时间或本地发GM时用
metadata: 
  node_type: memory
  type: project
  originSessionId: bc47406f-de36-414c-b81a-a24b401015f1
---

X3 **本地服**（`-e local`，`Tools/start_local_server.bat`）发 GM 命令、调服务器时间走 telnet。helper 脚本：`C:\Users\linkang\x3_gm.py`（`python x3_gm.py "!gm @<uid> <cmd args>" ...`）。

**关键参数**
- telnet 端口 = `23000 + NodeID`（`TelnetModule.cs`，port = 23*1000+NodeID）。3080 服 `-nid 3080` → **端口 26080**。NodeID 看启动命令行（`Get-CimInstance Win32_Process` 查 GameServer 进程 CommandLine）。
- 时间相关 GM（`GMSetServerTime`/`GMGetServerTime`/`GMSetServerTimeOffset`）都在 `BasicMeta`，是 **player-scope** → 必须 `!gm @<uid> <cmd>`，纯 `!gm <cmd>` 是 server-scope 找不到。uid 随便挑个该服玩家：从 BI 日志 `server\GameServer\bin\Debug\net8.0\logs\game-<sid>.bi.log` 的 user_event 行取（如 3080 服 uid=27065）。

**❗telnet 分包协议大坑**（`ServerCommon/TelnetServer/Server.cs` receiveData）：服务端**每个 recv 包只看 data[0]**，仅当包**首字节是 CR(0x0D)** 才判定为回车并派发命令。所以 `!cmd\r\n` 一个包发出去 = 首字节是 `!`，CR 被埋在中间，永远只回显不执行。**必须把命令体和 `\r\n` 分两个包发**（先发 body，sleep 0.3s，再发 `b"\r\n"`）。x3_gm.py 已处理。另：首字节 ≥0xF0 的包被当 IAC 丢弃。

**设到 D30 的算法**（D-day = passDay，开服满 N 天）
1. `GMGetServerTime` 读 `ServerOpenDate` + `passDay`。
2. 目标时间 = ServerOpenDate + N 天，格式 `yyyy-MM-dd/HH:mm:ss`。
3. `GMSetServerTimeOffset <目标>`（DEBUG+local 限定，**持久化、重启仍生效**）；只想本次生效用 `GMSetServerTime`。`GMSetServerTimeByDHM day hour min` 是相对当前**加**天数，不是设绝对天。
4. 复验 `GMGetServerTime` 看 passDay。

**限制**：时间只能前进，`delta<0` 被拒（`ErrorCodePlayerDisallowRewindTime`）。要回退得 `GMClearServerTimeOffset`(下次重启生效) 或重启清库。

实例（2026-06-05）：3080 开服 2026-05-27 09:31:06，D8 → set 2026-06-26/09:31:06 → passDay 30。

## 重启本地服流程（+ 一个大坑）

**停**：`python C:\x3-project\server\Tools\stop_gs.py --server_id 3080 --grace 10`（按 sid 同时停 Game+Map，优雅 CTRL_BREAK→超时强杀）。**依赖 psutil**（已 `pip install` 进 C:\Python314）。
**起**（脱离会话、不重建用 --no-build）：cwd=`C:\x3-project\server`，先 Game 再隔 ~5s 起 Map（Map 的 nid=sid+1，3080→3081）：
```
Start-Process dotnet -ArgumentList 'run --no-build --project GameServer -- -sid 3080 -nid 3080 -csid 61 -e local -ll debug -lf logs/game-3080.log' -WorkingDirectory 'C:\x3-project\server'
Start-Process dotnet -ArgumentList 'run --no-build --project MapServer  -- -sid 3080 -nid 3081 -csid 61 -e local -ll debug -lf logs/map-3080.log'  -WorkingDirectory 'C:\x3-project\server'
```
启动需 ~6s 端口起、~20s telnet 脚本引擎(Roslyn)编译完才能跑 GM（GM 早发会回 `ScriptEngine is not ready`）。看启动结果 grep 日志 `PlayService started`/`Server Start Failed`（`game-3080.<日期>.log`）。

**✅ GMSetServerTimeOffset 真的持久化**：重启后服务器**直接从 D30 起**（日志游戏时间戳 `[2026-06-26 ...]`），不用再 set；也 set 不了（已是 D30，再 set 同一秒=rewind 被拒）。

**❗大坑：导表后裸 --no-build 重启会崩**。本地服 config 读 `server\Resource\Assets\Res\Config\ProtoGen\*.bytes`；这目录被 config 导出/同步覆盖后（一批 .bytes + `AllTableDataMd5.txt` 同一时刻刷新），若 server 二进制没跟着重编 → 启动期 config 预载抛 `InvalidProtocolBufferException: input ended unexpectedly`（栈：`CfgHelper.StartPreloadData → CConstCfg.get_Instance`），日志 `Server Start Failed`。**现象很迷惑**：telnet 端口照常起（crash 在端口之后），连得上、脚本引擎也 ready，但所有 `!gm`/`!dump` 只回显不返结果（游戏逻辑没起来）。老进程没事只因 config 在内存里，一重启就暴露。
**修**：重编 Hotfix 工程再起（即 start_local_server.bat 干的事）——
`dotnet build GameServer.Hotfix\GameServer.Hotfix.csproj` + `MapServer.Hotfix\MapServer.Hotfix.csproj`（会连带编主工程，别用 server.sln——CLAUDE.md 警告它会还原未提交代码）。**重编前必须先 stop**：崩溃的 GameServer 是僵尸进程仍锁着 bin 里的 dll，不杀会 `MSB3021 文件被锁` 编译失败。server 工作树干净时重编零风险。
