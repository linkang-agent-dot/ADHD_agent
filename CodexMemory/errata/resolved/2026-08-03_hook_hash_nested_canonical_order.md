# Hook hash 复现遗漏嵌套对象递归排序

- 日期：2026-08-03
- 任务：自动补齐 Codex hooks 信任状态
- 现象：首次复现的 9 条哈希中，含 `additionalContextLimit` 的 SessionStart 和 UserPromptSubmit 被 App Server `hooks/list` 判为 `modified`，其余 7 条为 `trusted`。
- 根因：已按字典序构造顶层 identity，但 handler 嵌套对象仍沿插入顺序输出；Codex 的 `canonical_json` 会对每层对象递归排序。
- 处理：改用本机 Codex App Server 返回的 `currentHash` 作为最终权威值；复查结果 `TOTAL=9 TRUSTED=9 BAD=0`。
- 状态：resolved
