---
name: reference-xlsx-git-diff-tool
description: "对比 xlsx 配置表 git HEAD vs 工作区单元格差异的脚本，用户问\"看变更差异/diff\"时调用"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8f9ba486-2d39-4c18-a630-3d4119185d5e
---

xlsx 是二进制，`git diff` 看不了内容。用户问"看看当前修改的变更差异 / diff / 改了啥"且改动是 .xlsx 时，调用此脚本。

**脚本**：`C:\Users\linkang\xlsx_git_diff.py`

**用法**：
- `python C:\Users\linkang\xlsx_git_diff.py` — 默认仓库 `C:\x3\gdconfig`，自动对比 git status 里所有改动的 .xlsx
- `python C:\Users\linkang\xlsx_git_diff.py <仓库路径>` — 指定仓库，自动扫所有改动 xlsx
- `python C:\Users\linkang\xlsx_git_diff.py <仓库路径> <文件相对路径> ...` — 只对比指定文件

**输出**：逐页签逐单元格 `[ID=xxx] 列(字段名) 行N: 旧值 -> 新值`，自动取该行 ID 列与表头字段名（注释行）标注。

原理：`git show HEAD:<rel>` 取旧版二进制 → openpyxl 内存加载 → 与工作区逐 cell 对比。

相关：[[reference-x3-timecycle]]（Pack 表 TriggerType/TimeCycle 含义）。
