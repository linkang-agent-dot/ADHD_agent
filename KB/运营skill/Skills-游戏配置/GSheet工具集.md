---
aliases: [google-workspace-cli, gws, gsheet-replace, branch-diff]
tags: [skill, 游戏配置, gsheet, gws, google-workspace]
---

# GSheet 工具集

## 一、Google Workspace CLI（gws）
**路径**：`.cursor/skills/google-workspace-cli/`
**触发**：`gsheet` `gws` `读gsheet` `写gsheet` `Google表格` `Google Drive`

统一 CLI 工具，支持：
- **Sheets** — 读写 Google 表格
- **Docs** — 创建/编辑 Google 文档
- **Drive** — 文件管理/上传
- **Forms** — 表单操作
- **Keep** — 笔记管理
- **Slides** — 演示文稿

### gws 子技能一览

| 子技能 | 路径 | 功能 |
|--------|------|------|
| gws-shared | `.cursor/skills/gws-shared/` | 认证、全局参数、输出格式 |
| gws-sheets | `.cursor/skills/gws-sheets/` | Sheets v4 全功能 |
| gws-sheets-read | `.cursor/skills/gws-sheets-read/` | 读取范围 |
| gws-sheets-append | `.cursor/skills/gws-sheets-append/` | 追加行 |
| gws-docs | `.cursor/skills/gws-docs/` | Docs API |
| gws-docs-write | `.cursor/skills/gws-docs-write/` | 追加文本 |
| gws-drive | `.cursor/skills/gws-drive/` | Drive v3 |
| gws-drive-upload | `.cursor/skills/gws-drive-upload/` | 上传文件 |
| gws-forms | `.cursor/skills/gws-forms/` | Forms API |
| gws-keep | `.cursor/skills/gws-keep/` | Keep API |
| gws-slides | `.cursor/skills/gws-slides/` | Slides API |

---

## 二、GSheet 批量替换（gsheet-config-replace）
**路径**：`.cursor/skills/gsheet-config-replace/`
**触发**：`批量替换` `ID替换` `配置替换` `gsheet replace`

在 GSheet 配置表内做精确字符串替换（含 JSON 内的 ID 替换），支持 dry-run 预览。

### 脚本
- `scripts/gsheet_replace.py` — 替换主脚本

---

## 三、分支差异对比（branch-diff-gsheet）
**路径**：`.cursor/skills/branch-diff-gsheet/`
**触发**：`分支差异` `差异汇总` `对比分支` `diff到表格`

对比 `x2gdconf` 两个分支的 `fo/config` 差异，生成带颜色标注的 Google Sheet。

### 脚本
- `scripts/create_diff_sheet.py` — 差异生成脚本
