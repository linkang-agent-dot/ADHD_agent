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

**坑**：X3 环境有 `UnityAutoQuitter` 伴生进程，会向编辑器发退出指令——用户没点关闭但编辑器进了退出流程时，先怀疑它。

关联：[[reference_x3_unity_mcp]]
