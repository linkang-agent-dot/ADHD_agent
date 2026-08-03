# BTW / sub-agent handoff backups

此目录由 `scripts/subagent_handoff.py` 和 Codex lifecycle hooks 自动维护。

每个主对话一个目录，内部按 `sub-agent/` 与 `BTW/` 分开保存：

- `user-prompts.md`：子对话中的用户输入。
- `checkpoints.md`：关键结论、实际改动和阶段进展。
- `final-handoff.md`：正常结束时回主对话的最终总结。
- `state.json`：active/completed/interrupted/claimed 状态。
- `transcript-snapshot.jsonl`：尽力生成的本机原始记录快照，不作为恢复唯一真源，也不进入 Git。

运行时文件不自动删除。需要清理时先列出保留/删除清单，经用户确认后再处理。
