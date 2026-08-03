# 自动同步在 ignore 落地前提交了 skill quarantine

- 日期：2026-08-03
- 任务：Codex 旧元流程 skill 清理
- 现象：13 个卸载目录移入 `CodexMemory\skill-quarantine\2026-08-03` 后，18:00 自动同步在 `.gitignore` 创建前提交并推送了隔离内容，其中包含约 39 MB 的 x3-media 备份。
- 根因：先移动大目录、后创建忽略规则，留下了并发自动提交窗口。
- 处理：用 `git rm --cached` 仅从索引移除隔离内容，本地备份保留；提交 `.gitignore` 与 README。以后先落 ignore 并用 `git check-ignore` 验证，再移动任何运行态/隔离目录。
- 状态：open
