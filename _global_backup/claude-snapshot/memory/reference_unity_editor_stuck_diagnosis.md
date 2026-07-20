---
name: unity-editor-stuck-diagnosis
description: Unity Editor 一直读条/卡死的诊断链路（进程CPU增量+日志三件套定位卡点，不用瞎等）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3b1aba42-1219-4e1a-9d3d-9e5abdfa0ef0
---

# Unity Editor「一直读条」诊断链路（2026-07-07 X3 客户端实战沉淀）

不猜、不瞎等，四步定位卡在哪：

1. **认清进程**：`Get-CimInstance Win32_Process -Filter "Name='Unity.exe'"` 看 CommandLine——带 `-name AssetImportWorkerN` 的是后台导入 worker（正常），真正的编辑器只有带 `-projectpath` 的那个。别被"好几个 Unity 进程"吓到。
2. **测活性**：对可疑 PID 取两次 `CPU` 差值（隔 8 秒）。单核满转(增量≈间隔的80%+)=在算东西或死循环；0 增量=挂起等待。忙碌弹窗标题 `Hold on (busy for mm:ss)` 计时器在走只说明 UI 活着，不代表有进展。
3. **看日志三件套**（都在 `<项目>\Logs\` + `%LOCALAPPDATA%\Unity\Editor\Editor.log`）：按 LastWriteTime 排序找最近在写的；`shadercompiler-*.log` 末尾 `Cmd: shutdown` = shader 编译已正常收工；**Editor.log 长时间（>10min）零写入 + 主线程满转 = 卡死在无日志的循环里**，基本不会自己好。
4. **识别退出流程**：Editor.log 出现 `SaveDefaultWindowPreferences` / `Killing ADB server` / `Input System Shutdown` / `Licensing channel disconnected` = 编辑器在执行退出。卡在这之后 = 卡在 quit 收尾；此时强杀风险较小（布局已保存、ADB 已关），最坏 Library 部分重导。

5b. **Editor.log 的 error CS 可能是上一轮编译的旧错误残留**：文件已修但 Unity 没获焦点没 Refresh 就不会重编，log 尾仍是旧错。判法=先核盘上文件是否已修（grep 报错行现值），已修→让用户切回 Unity 窗口重编（必要时 Ctrl+R），别照旧日志重复改代码（2026-07-17 扭蛋机实证）。
5. **「卡编译」可能根本不是卡**：主线程 CPU 0 增量 + Editor.log 见 `All compiler errors have to be fixed before you can enter playmode!`/`ShowCompileErrorNotification` = 编译错误挡 Play 非卡死——`Select-String Editor.log -Pattern "error CS"` 直接拿错误清单（2026-07-17 集结基金幽灵列实证）。

6. **「卡进度条 75%」可能是游戏内 loading 非编译**：Editor.log 秒级持续在写且内容是 TGS SDK 心跳/`Connect gateway` = 已进 Play，卡的是登录连服。反复 `Connect gateway <ip> <port>` 重连循环 = 网关不通。判共享服务挂 vs 本机网络/Clash：**同一台目标机多端口对比测**（如 151 的 Mongo:27017 通而 etcd:2379 不通 = 那边服务挂，非本机问题；ping 通 TCP 不通不足以定性）。etcd 挂 → 本地服 `InitDiscoveryAsync` gRPC DeadlineExceeded 起不来 → 找管共享基建的同事，本机无解（2026-07-18 实证：共享 Gate 172.20.90.171:10011 + etcd 172.20.90.151:2379 同时宕）。

**坑**：X3 环境有 `UnityAutoQuitter` 伴生进程，会向编辑器发退出指令——用户没点关闭但编辑器进了退出流程时，先怀疑它。

关联：[[reference_x3_unity_mcp]]
