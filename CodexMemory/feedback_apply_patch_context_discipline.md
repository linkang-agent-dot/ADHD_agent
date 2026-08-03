# apply_patch 上下文纪律

- 日期：2026-08-03（由 Claude 巡检自 3 条 errata 归并：apply_patch_context_mismatch_html、handoff_hook_patch_context_mismatch、codex_memory_migration_patch_context）
- 规律：apply_patch 的预期上下文与磁盘实际内容稍有出入就**整个补丁失败**——一次补丁改多个文件时，一个文件的漂移会连累其他本可落地的文件。
- How to apply：①改前**必先重读目标文件当前内容**（尤其是 AGENTS.md 这类多方并行在改的文件）；②多文件改动拆成每文件一个小补丁，逐个验证；③单行长内容（压缩 HTML/CSS）补丁要带整行完整上下文，不能只带片段。
