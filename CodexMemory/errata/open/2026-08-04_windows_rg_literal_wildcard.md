# Windows rg 不接受将通配符当文件路径

- 日期：2026-08-04
- 任务：搜索 FCOL 历史生成脚本。
- 现象：向 `rg` 传入 `gen_*final.py` 作为路径参数，Windows 返回 OS error 123。
- 根因：`rg` 的路径参数不由 PowerShell 自动展开该通配符，Windows 又不允许文件名包含 `*`。
- 处理：改用 `rg --glob 'gen_*final.py' <pattern> <directory>`，或先用 `rg --files` 筛选；不再把通配符直接当路径传入。
- 状态：resolved
