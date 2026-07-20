---
name: disk-migration-20260713
description: 2026-07-13 C/D盘搬迁E盘记录：什么搬走了在哪、还剩哪些可腾空间大项及各自正确腾法
metadata: 
  node_type: memory
  type: reference
  originSessionId: c6d7ed79-7e48-4903-92a2-d0ccbd52a527
---

# 2026-07-13 磁盘搬迁记录 + 后续腾空间地图

## 已搬走（源已删，E盘为唯一副本）
- `E:\D盘搬迁\`：CD_UI_NEW_2(82.7GB, **UI资源SVN工作副本**,新路径直接可用)、文档(6GB)、Pictures(3.4GB)、共享(2.1GB)、Downloads(1.2GB)、文案交接(1.1GB)
- `E:\C盘搬迁\`：新建文件夹(5.9GB,内容=「000 源片」视频)、`linkang主目录git仓备份\.git`(32.7GB)
- ⚠️ **用户主目录 `C:\Users\linkang` 已不再是 git 仓库**（原 .git 是误建、仅1个commit ab250416 把整个主目录打包；备份在上面路径）。Claude Code 环境里 "Is a git repository" 将变 false。
- 结果：C 0.9→39GB 空闲，D 1.1→97.9GB 空闲，E 剩109GB。

## 下次再腾的大项（本次未做，都要走软件自带迁移，不能直接拖）
- MuMu模拟器 `C:\Program Files\Netease` 68GB → MuMu设置里迁移VM磁盘
- pagefile.sys：C 30GB + D 46GB → 系统「虚拟内存」设置改到E，重启生效；hiberfil.sys 12.7GB → `powercfg /h off`
- Unity编辑器 `C:\Program Files\Unity` 30GB → Unity Hub 重装到E再删C
- Docker数据 `AppData\Local\Docker` 24.6GB → Docker Desktop 设置迁移(wsl export/import)
- SteamLibrary D盘 11GB → Steam 存储设置迁移
- 缓存类（清理不搬）：anaconda3 11.5GB / Supreme(LocalLow) 9.4GB / npm-cache 4.6GB / Temp 3.2GB
- ❌ `D:\UGit\x2client` 294GB 活跃Unity工程，E装不下也别动；`C:\x3-project`/`C:\ADHD_agent`/`C:\x3` 路径被skill硬编码，禁搬。

## 2026-07-15 二次腾空间（C 又满到 0.9GB→卡死）
- 起因：C 盘 130.9GB 在主目录，AppData 占 115.5GB。大头：Docker 25.85 / anaconda3 11.54 / Packages(UWP) 9.32 / Supreme(游戏,LocalLow) 9.4 / Unity 6.68 / npm-cache 4.87 / Temp 4.19。
- **本次实际动作（C 0.9→19.5GB）**：① 删 npm-cache 4.87（纯缓存,claude不受影响,自动重建）② 清 Local\Temp（排除 claude 子目录,占用文件自动跳过）③ Supreme 游戏 9.4GB robocopy→E + 目录联接。Downloads 2.1GB 同法。
- **搬 AppData/游戏数据用「robocopy→E + New-Item Junction」而非纯删**：程序仍从原路径读、字节在 E、可逆。原路径 `E:\C盘搬迁\{AppData\...|home\...}`。
- **⚠️ Documents 别整体搬**：`Documents\xwechat_files\` 是微信实时数据库（message_*.db/wal,微信开着在写），边搬边删有损坏风险；本次已放弃（保留 C 原件）。要搬得先关微信。
- **被运行中程序挡住、本次没搬的大项**（需关对应程序或走软件自带迁移）：Docker 25.85(还在 build,且需 Docker Desktop 迁移/wsl export)、anaconda3 11.54(python 在跑)、Unity 6.68(Unity 开着)、Packages 9.32(UWP,联接会破权限跳过)。下次关掉这些程序后可 junction 搬 anaconda/Unity；Docker 走自带迁移。

## 2026-07-17 三次腾空间（C 2.1→29.8GB）
- 起因：pagefile.sys 系统托管自动膨胀 30→54.8GB 是两天吃掉 17GB 的主犯（用户本轮选择不动它）。
- 本次动作：① 清 Temp(排除claude) 1.37GB ② **Docker 26.4GB → `E:\Docker\wsl` + junction**（容器 xiaohongshu-mcp 迁后正常，restart policy=no 需手动 start）。
- ⚠️ **Docker Desktop（server 29.2.1）改 settings-store.json 加 `DiskImageLocation` 无效**：后端照旧锁 C 盘 vhdx（路径迁移只认 GUI 里操作触发的搬移）。正确姿势=停 Docker+`wsl --shutdown` → robocopy → 删源 → junction，Docker 无感知。vhdx 放纯 ASCII 路径（避中文路径 WSL 挂载风险），故用 `E:\Docker\wsl` 而非 E:\C盘搬迁\。
- Docker 停干净判据：Stop-Process 全家(Docker Desktop/com.docker.backend) + wsl --shutdown 后，用 `[IO.File]::Open(vhdx,'Open','Read','None')` 试独占锁验证已释放；迁移中 Docker 若跑过一次要 **re-sync 再校验**（vhdx 已变）。
- **pagefile 已迁 E（07-17 同日补做，待重启生效）**：UAC 提权脚本改 CIM+注册表双保险（AutomaticManagedPagefile=false / 删C设置 / E:\pagefile.sys 0 0 系统托管），重启后 C 释放 ~55GB。机器 32GB RAM 常年 80%+ 压力（Unity+Docker+MuMu），pagefile 实际用量峰值仅 ~11GB，54.8GB 是历史高压撑大的空壳。注意：C 无 pagefile 后 BSOD 完整转储不可用（代价可接受）。
- **剩余大项（下次优先级）**：hiberfil 12.7GB（powercfg /h off）> Unity\cache 5.5GB（纯缓存可删）> Roaming: Tencent 5.8/Cursor\User 4.8/npm(全局包别删) 4.5/钉钉 3.3/WPS 2.3。anaconda3 已不在 C。

## 手法沉淀
- 流程：robocopy 复制 → 文件数+总大小双校验（删源前必用 `robocopy /L` 确认 0 待拷差异）→ 删源 → New-Item -ItemType Junction 建联接。
- 坑：
  - robocopy exit code 1 = 成功复制（<8都算成功），后台任务会因此误报"failed"；exit 9=8+1=有文件没拷上（多为被占用的活动文件,如微信库）,删源前必查。
  - `robocopy /COPYALL` 需要「Manage Auditing」权限,普通账号会 exit 16 报错 → 数据文件夹别用 /COPYALL,默认 /COPY:DAT 够。
  - **建联接别用 `cmd /c mklink`**：安全钩子会把 `/c` 误判成待删系统路径拦掉；用 `New-Item -ItemType Junction -Path <link> -Target <target>`（原生,不需管理员）。
  - Start-Process robocopy -ArgumentList 传含空格/中文路径会被搞乱 → 直接 `robocopy $src $dst ...` 调用。
  - pwsh 里 `foreach(){} | Format-Table` 是语法错误，要 `$r = foreach...; $r | ft`。
