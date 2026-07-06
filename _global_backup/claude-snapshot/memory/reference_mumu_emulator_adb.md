---
name: reference_mumu_emulator_adb
description: 本机 MuMu 12 模拟器的 ADB 连接地址、内部安卓 IP 查法、安卓启动失败排查链路
metadata: 
  node_type: memory
  type: reference
  originSessionId: 805500a7-7234-4c38-89f7-274c26d7e57a
---

本机装的是 **MuMu 12**（进程 `MuMuVMMHeadless`），不是老版 MuMu 6。

**ADB 调试地址（连 Appium/自动化/装包/adb shell 用这个）**：`127.0.0.1:16384`
- 多开实例端口依次 +32：16384 / 16416 / 16448 …
- 老版兼容端口 `127.0.0.1:7555` 也在监听，一般也能连。
- adb 自带在：`C:\Program Files\Netease\MuMu\nx_device\12.0\shell\adb.exe`
- 连接：`& "<adb路径>" connect 127.0.0.1:16384`

**模拟器内部安卓系统 IP**：`10.0.2.15`（wlan0，NAT 网段 10.0.2.0/24）——固定值、只在模拟器内部有意义，宿主机/外部访问不到。App 里读「本机 WiFi IP」拿到的就是它。

查端口的稳妥法（不靠猜）：`Get-NetTCPConnection -State Listen | ? LocalPort -ge 7555` 看 `MuMuVMMHeadless` 占的端口。

## 安卓启动不了的排查链路（2026-07-02 实战）

日志两层：服务层 `C:\Users\linkang\.MUMUVMM\MuMuVMMSVC.log`（只看到 Launched VM 不代表成功），**真死因看 VM 层** `C:\Program Files\Netease\MuMu\vms\MuMuPlayer-12.0-0\Logs\VBox.log` 的尾部。日志短时间内连滚多个 `.1/.2/.3` = 启动崩溃循环。

**已踩坑：`Unhandled error 1455` + `VERR_UNRESOLVED_ERROR` = Windows 提交内存耗尽**（1455=ERROR_COMMITMENT_LIMIT 页面文件太小），VM 要一次性申请配置的 RAMSize（本机配 6G，见 .nemu 文件 `<Memory RAMSize="6144"/>`）分配不出就瞬间掉电。核查：`Get-Counter '\Memory\Committed Bytes','\Memory\Commit Limit'`，余量 < RAMSize+1G 就是它。解法=关大户腾内存（Unity 编辑器每个 2-7G / `wsl --shutdown` 回收 vmmem / 多余 claude 会话各 ~1G），或治本把 MuMu 设置里内存 6G→4G。

注意：VBox.log 里 `netIfGetBoundAdapters could not find MuMuVMMNetLwf` 和 `No hardware-virtualization capability detected`（NEM/Hyper-V 模式正常现象）都是烟雾弹，不是死因。
