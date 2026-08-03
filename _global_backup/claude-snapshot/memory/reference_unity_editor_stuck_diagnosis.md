---
name: unity-editor-stuck-diagnosis
description: Unity Editor 一直读条/卡死的诊断链路（进程CPU增量+日志三件套定位卡点，不用瞎等）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3b1aba42-1219-4e1a-9d3d-9e5abdfa0ef0
  modified: 2026-07-29T13:56:13.638Z
---

# Unity Editor「一直读条」诊断链路（2026-07-07 X3 客户端实战沉淀）

## 🔴 情形 A：不是卡死，是**大批量 reimport**——定位「谁动了盘」三步法（2026-07-29 实战）
症状＝Editor.log **秒级持续在写** `Start importing Assets/... -> (artifact id ...) in 0.xx seconds`，一跑一个多小时。这不是卡死，是真在干活，**别强杀**（中断会让 Library 半残，下次重来更久）。查元凶：
1. **看在导什么**：`Get-Content Editor.log -Tail 25` → 本次是 `Assets/Res/Audio/Voice/*.mp3`，每个 0.2~0.8s × 数千个＝小时级。
2. **看资源何时落盘**（关键一步，直接指认时间点）：
   ```powershell
   Get-ChildItem <资源目录> -Recurse -Filter *.mp3 |
     Group-Object { $_.LastWriteTime.ToString("MM-dd HH:00") } | Sort-Object Name -Descending
   ```
   出现「今天某小时突然 N 百个文件」＝那个时间窗有人动了盘。
3. **用 reflog 对时间**：`git reflog --date=format:"%m-%d %H:%M"` → 本次命中 `reset: moving to origin/dev_festival`，`git diff <旧> <新> --stat` 显示 **4385 files / 286225 insertions** ＝ 全量 reimport 的真凶。
- 🪤**判反了的两个坑**（本次都踩过，别重蹈）：①**看到 `M xxx.mp3.meta` 别当成原因**——`.meta` 被改是 Unity import 的**产物**不是起因；②**先查 `.gitattributes` 再赖 LFS**——本次 mp3 **不是** LFS 跟踪（只有 `*.bytes` 是），所以 `git lfs pull` 根本碰不到它，怀疑方向一开始就错了。**mtime 变但 `git status` 不报内容改 ＝ 文件被同内容重写**（reset/checkout 的典型副作用），Unity 只认 mtime 就会重导。
- ✅**预防**：Unity 项目里**别对整仓 `git reset --hard origin/<br>`** 去拿几个产物文件——它重写数千文件 mtime＝必然触发小时级 reimport。只要某几个文件就用 **`git checkout <ref> -- <精确路径>`**（本次取 ProtoGen 两个 .bytes 即此法，只重导几个 TextAsset，秒级）。

## 🪤 附带：`git merge-base --is-ancestor` 判「提交丢没丢」会**假阳性**
reset 后拿 `--is-ancestor <commit> origin/<br>` 判断，返回 false **不等于工作丢了**——若那些改动是被 **cherry-pick / 别人重新提交**进远端的，**commit hash 变了但内容在**。**必须验内容**：`git show origin/<br>:<文件> | grep <关键符号>`、`git cat-file -e origin/<br>:<新增文件>`、`git diff origin/<br> <commit> -- <文件>`（空输出＝内容一致）。本次三笔"丢失"提交经此法验证内容全在。

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
