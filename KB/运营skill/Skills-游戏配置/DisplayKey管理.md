---
aliases: [x2-dk-manager, DK, DisplayKey]
tags: [skill, 游戏配置, X2, unity, dk]
skill_path: .cursor/skills/x2-dk-manager/
trigger: DK、display key、录入DK、ctrl+t搜不到
---

# DisplayKey 管理

## 概述
X2 Unity DisplayKey (DK) 管理工具，支持三大功能。

## 三大功能

### 0. DK 诊断
给定图片路径 → 读取 `.meta` GUID → 搜索所有 `Display_*.asset` → 判断是否已录入。
未录入则自动进入录入流程（自动判断类型，无需用户二次确认）。

### 1. 上传/录入 DK
- 自动分配全局唯一 key（跨所有 `Display_*.asset` 取最大值+1）
- 复制图片到目标目录
- 自动修正 `.meta`：`textureType:8`、`spriteMode:1`、iOS/Android 128px 压缩覆盖
- 写入 `Display_*.asset`
- Ctrl+Shift+E 导出
- 多图自动识别配套组合（Icon+IconBg 等 24 种）共用同一 key

### 2. 查询远端 DK
给定 key → 搜索本地和远端分支的录入状态。

## 触发词
`DK` `display key` `录入DK` `上传DK` `添加DK` `查DK` `查询DK` `dk远端` `ctrl+t搜不到` `检查DK`
