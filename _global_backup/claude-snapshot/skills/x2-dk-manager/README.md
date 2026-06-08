# X2 DisplayKey (DK) 管理工具

X2 Unity 项目 DisplayKey 录入与查询工具，适用于 Cursor Agent。

## 功能

### 1. 录入 DK
- 给定图片 + type，自动分配**全局唯一 key**（跨所有 Display_*.asset 取最大值+1）
- 自动将 `.meta` 修正为 **Sprite (2D and UI)** 类型（含 iOS/Android 128px 压缩覆盖，13 项差异字段全部处理）
- 写入 `Display_{type}.asset`，Ctrl+Shift+E 导出后双重确认
- 多图自动识别 **24 种配套组合**（Icon+IconBg / 英雄套件 / 小游戏等），共用同一 key；不确定时询问

### 2. 查询 DK
- 给定 key，搜索本地和远端分支的录入状态

## 触发词

`录入DK` / `上传DK` / `添加DK` / `查DK` / `查询DK` / `DK远端` / `ctrl+t`

## 24 种配套组合（同 key 不同 type）

| 频次 | 组合 |
|------|------|
| 743 | Icon + IconBg |
| 256 | Icon + Prefab + UIPrefab |
| 249 | Icon + UIPrefab |
| 205 | Icon + IconFront |
| 147 | Icon + Portrait |
| ... | （共 24 种，详见 SKILL.md） |

`references/combo-examples/` 目录提供每种组合的真实参考图。
