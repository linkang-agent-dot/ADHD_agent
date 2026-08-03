# BTW / sub-agent 持久化回主对话

## 入口

- Hook 配置：`C:\Users\linkang\.codex\hooks.json`
- Hook 真源片段：`C:\ADHD_agent\CodexMemory\config\subagent_handoff_hooks.fragment.json`
- 执行脚本：`C:\ADHD_agent\CodexMemory\scripts\subagent_handoff.py`
- 备份目录：`C:\ADHD_agent\CodexMemory\handoffs\`
- 自动化测试：`C:\ADHD_agent\CodexMemory\tests\test_subagent_handoff.py`

## 工作方式

1. `SessionStart` 登记主 session 和主 transcript。
2. `UserPromptSubmit` 若发现 transcript 与主 transcript 不同，按 BTW/side chat 保存用户输入；主线程则注入未接管 handoff。
3. `SubagentStart` 为任意 agent 类型建目录，并注入 checkpoint 命令。
4. `Stop` 保存 BTW 或唯一活动子 agent 的最近回复；`SubagentStop` 保存 final 与 transcript 快照。
5. 主 agent 吸收 `[SUBAGENT_HANDOFF_RECOVERY]` 后执行：

```powershell
python C:\ADHD_agent\CodexMemory\scripts\subagent_handoff.py claim --session-id <session_id>
```

## 备份结构

每个主对话目录为 `日期_任务摘要_session短ID`，内部有 `sub-agent/` 和 `BTW/`。恢复真源是 `user-prompts.md`、`checkpoints.md`、`final-handoff.md` 与 `state.json`；`transcript-snapshot.jsonl` 只是尽力快照，不依赖其稳定格式。

## 关键边界

- `/side`/`/btw` 是 Codex 官方定义的 ephemeral side chat，不能依赖 `resume` 恢复。
- Ctrl+C 可能不触发 `Stop`/`SubagentStop`，所以用户输入必须在 `UserPromptSubmit` 先保存，关键结论要随形成随 checkpoint。
- 新增或修改 hooks 后，Codex 会按定义 hash 重新要求信任；在 CLI 执行 `/hooks` 审核并 trust，否则 hook 可能被跳过。
- handoff 不自动删除；清理前必须向用户给出保留/删除清单。
- 当前实现对并发写使用全局文件锁和原子 JSON 替换。

## 验证

```powershell
python -m json.tool C:\Users\linkang\.codex\hooks.json
python -m py_compile C:\ADHD_agent\CodexMemory\scripts\subagent_handoff.py
python -m unittest discover -s C:\ADHD_agent\CodexMemory\tests -p test_subagent_handoff.py -v
```

2026-08-03 首次实现：6 项测试通过；带 `--dangerously-bypass-hook-trust` 的冷启动在模型响应前成功创建 smoke 对话目录，证明 SessionStart/UserPromptSubmit 接线生效。真实模型 sub-agent E2E 因本机 `codex exec` 首 prompt 后无响应超时，不能据此判 handoff 失败；待 hooks 信任后在正常交互会话复测。
