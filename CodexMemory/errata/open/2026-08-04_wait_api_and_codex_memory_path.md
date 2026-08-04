# 等待接口层级与 Codex/Claude memory 路径差异

- 日期：2026-08-04
- 任务：建立 X3 节日养成线及投放方式迭代的全局认识
- 现象：后台 shell 返回 cell id 后，在 `functions.exec` 内误调用不存在的 `tools.wait`；随后按用户提供的 `.Codex\projects\...\memory` 路径查增量文件时目录不存在，实际共享 memory 位于 `.claude\projects\...\memory`；补查深海/世界杯资料时又把 `*.md` 直接写进 Windows `rg` 目录参数，触发路径语法错误。
- 根因：混淆了顶层 `functions.wait` 与 exec 内嵌工具命名空间；未先验证 Windows 本机实际 memory 根目录；把 shell glob 习惯套到 `rg` 的路径参数。
- 处理：改用顶层 `functions.wait` 接续后台任务；列目录确认后改读 `.claude` 下的共享 memory，并以 CLAUDE.md 当前真源路径为准；目录内筛选文件固定使用 `rg --glob '*.md' <pattern> <directory>`。
- 复发：同日验收修订后验证产物时，再次把 `*.md` 拼进目录参数，触发同一 Windows 路径语法错误；随后改回 `rg --glob '*.md' <pattern> <directory>`。后续含目录筛选的 `rg` 命令应先写目录、再显式加 `--glob`，不在路径字符串里写通配符。
- 状态：open
