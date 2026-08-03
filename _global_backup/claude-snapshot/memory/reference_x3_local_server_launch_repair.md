---
name: reference_x3_local_server_launch_repair
description: X3 本地服(Center/Game/Map)起服链路、csid 来源、以及 make-links 被中断导致软链全丢→编译爆 295 错误的事故与 junction 免提权修复法
metadata: 
  node_type: memory
  type: reference
  originSessionId: 02f4c1d2-2636-47db-b1a2-19dc8f572944
  modified: 2026-07-29T07:15:50.239Z
---

# X3 本地服起服链路 + 软链事故修复（2026-07-29 实证）

## 三服拓扑与端口

| 服 | 起法 | sid/nid | 端口 = 23000+nid |
|---|---|---|---|
| Center | `Tools\start_local_center.bat` | 65/65 | 23065 |
| Game | `Tools\start_local_server.bat` | 3080/3080 | 26080 |
| Map | 同上（一个脚本起两个） | 3080/3081 | 26081 |

**csid 唯一来源 = `C:\x3-project\server\Tools\local_conf.ini` 的 `[server] centerid`**，所有启动脚本 `call :readini` 从这里读 `%vcid%`，**代码/脚本里没有任何硬编码**。改 Center ID 只改这一处即可；Center 段(<100) 在 `Server__Server.tsv` **无配置行**、Mongo 里也**不建独立库**（`gs_game_65` 不存在是正常的），所以换 ID 不需要建库建表。
⚠️ 这个 ini 观察到会**被还原成 71**（疑似 template 覆盖或他人改动）——起服前先确认一次实际值。

## ★事故：kill 掉 make-links.bat = 删光全部软链

`start_local_*.bat` 开头有 `start /wait make-links.bat`，而 `make-links.bat` 会 **mshta+runas 弹 UAC 提权**再调 `MakeLink.py`。**非交互环境下卡在 UAC 弹窗上**，看起来像死机。

**致命点**：`MakeLink.py` 的 main 是 `DelLink()` → `MakeLink()`——**先遍历整个 server 目录删光所有软链，再重建**。此时 kill 它 = 停在"删完没建"的空档，20 条软链全没。

**症状（极具迷惑性）**：`dotnet build` 爆 **295 个 CS0246**，全是 `IResponse`/`IRequest`/`IEntity`/`IMessage`/`MsgHandlerAttribute`/`EventType<,,,,>`/`SubjectList`/`IMQModule` 这类**框架基础类型找不到**。容易误判成"source generator(RoslynAnalyzer) 没跑"或"proto 没生成"，实际是 `ServerCommon/Common → client/Assets/TFWCore/Script/Common` 这条软链没了，框架源码整个不在编译输入里。
**判据**：`Libs/TfwProtobuf/bin/.../TfwProtobuf.dll` 能编译成功但**导出 0 个类型**（空壳 dll）= 源目录是空的 = 软链丢了。用反射 `[Reflection.Assembly]::LoadFrom($dll).GetTypes().Count` 一秒确认。

## 修复：用 junction 代替 symlink（免管理员权限）

`MakeLink.py` 用 `os.symlink`，**需要管理员权限**（非管理员报 `WinError 1314 客户端没有所需的特权`）。但这 20 条目标**全是目录**，可以用 **junction** 代替——**普通权限即可创建**，对编译器/Unity 完全等效：

```powershell
New-Item -ItemType Junction -Path $linkPath -Target $targetPath
```

固化脚本：**`C:\ADHD_agent\KB\方法论\活动程序开发\tools\relink_server_junctions.ps1`**（内含与 MakeLink.py 一一对应的 20 条链接表，幂等：已存在则跳过，目标缺失会报 MISSING-TARGET）。跑完 `dotnet build` 即恢复 0 错误。

⚠️ 副作用：Python 的 `os.path.islink()` 对 junction 返回 **False**，所以下次跑 `MakeLink.py` 时 `DelLink()` 不会清掉这些 junction，`MakeLink()` 建 symlink 会因"目录已存在"失败。要回到原生 symlink，需**管理员**跑一次 `make-links.bat`（会先删后建）。

## 起服正确姿势（绕开两个卡点）

```powershell
# 1) 跳过 make-links（软链已在就不必重建），用完整路径 + PowerShell 调
& cmd.exe /c "C:\x3-project\server\Tools\start_local_center.bat skip-link"
```
- **必须用 PowerShell 工具调 bat**——Bash 工具会把 `cmd /c` 的 `/c` 改写成 `C:/`（见 [[feedback_atomic_write_and_escape_pitfalls]] 第三坑）。
- bat 末尾有 `pause`，非交互会挂住；若只想起服可跳过 bat，直接照抄它最后一行：
```powershell
Start-Process dotnet -ArgumentList "run","--project","CenterServer","--no-build","--",
  "-sid","65","-nid","65","-csid","65","-e","local","-ll","debug","-lf","logs/center.log" `
  -WorkingDirectory "C:\x3-project\server"
```
- Hotfix 与主程序集**版本必须匹配**：只 build Hotfix 而 CenterServer.dll 是旧的 → 启动报 `ReflectionTypeLoadException: Could not load type 'cspb.XXX' from assembly 'CenterServer'`（Hotfix 引用了新类型、主程序集没有）。修法=`dotnet build CenterServer.Hotfix`（经项目引用连带重编主程序集）。

## 验收判据（三层，缺一不可）

1. 各服日志出 `******** Server Start Success ********`（在 `<Srv>/bin/Debug/net8.0/logs/`）
2. 端口通：23065 / 26080 / 26081
3. **跨服链路真连上**：Center 日志有 `OnServiceUp, ServerID: 3080` + `CrossActivity.OnSync, followerServerID=3080`；Game 日志有 `ActivityMgr.OnSyncCenterData: GlobalActivities`

Center 启动时刷屏的 `CrossServerActivity - InitFromData error ... NullReferenceException` 是 **Mongo 里历史遗留跨服活动数据反序列化失败**，不阻断启动（后面照常 `CenterService started`），别误判成起服失败。

## 遗留未解

跨服活动 GM `gmaddcrossserveractivitybycfgid <cfgid>`（实现在 `CenterServer/CenterService.Gm.cs:78` → `CrossActivityMgr.Ark.cs:366`）对 105014/108201 返回 **errCode=6**，且 **Center 日志无任何对应记录**=请求没走到 Center。

**已排除业务层（重要，别重复验）**：该方法内部只有两种失败返回——`ErrCodeActivityCfgNotFound = 1017001`（`CSShared/Common/ErrCode/ErrCode.Activity.cs:11`）和 `ErrCodeParamError = 10`（`TFWCore/Script/Common/ErrCode/ErrCode.cs:154`）。收到的 6 两者都不是，而是框架层的 **`ErrCodeAsyncCallMethodNotExisted`**（同文件 :134）=**方法压根没被调到**。所以与配置是否存在、活动是不是跨服类型、TimeCycle 配没配**全都无关**，纯粹是 Center 侧 GM 方法注册/转发派发问题。

排查入口：`HandleGMServerCmdAsync` 只对**类名以 "Service" 结尾**的命令走 Service 作用域派发，否则被误判成 entity 命令——这正是该 GM 特意挂在 `CenterService` 而非 Module 上的原因（代码注释见 `CrossActivityMgr.Ark.cs:363-365`）。从"CenterService 的 GM 方法表在 Game 侧转发时有没有注册上"查起。

相关：[[workflow_x3_local_server_gm_telnet]]（GM/调时间）· [[reference_x3_tsv_export_migration]]（配置导入本地服）
