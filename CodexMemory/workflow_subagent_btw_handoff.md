# BTW / sub-agent 持久化回主对话

> **验收状态：部分通过（2026-08-03）。** 本机 Codex 0.146.0 App Server 已复核 9/9 hook 实例均为 `trusted`；不带 trust bypass 的全新 `codex exec` 成功完成并由 SessionStart 真实创建本机会话记录。真实交互 `/side` 与原生 Codex sub-agent E2E 仍未跑通，所以整套持久化机制尚不能宣称验收完成。另：`collaboration.spawn_agent` 不经过本机 CLI hooks，需单独的运行时接力层。

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

运维或探针需要定位会话目录时，必须查 `_index`，不要猜目录名：

```powershell
python C:\ADHD_agent\CodexMemory\scripts\subagent_handoff.py locate --session-id <session_id>
```

## 备份结构

每个主对话目录为 `日期_任务摘要_session短ID`，内部有 `sub-agent/` 和 `BTW/`。恢复真源是 `user-prompts.md`、`checkpoints.md`、`final-handoff.md` 与 `state.json`；`transcript-snapshot.jsonl` 只是尽力快照，不依赖其稳定格式。

## 关键边界

- `/side`/`/btw` 是 Codex 官方定义的 ephemeral side chat，不能依赖 `resume` 恢复。
- Ctrl+C 可能不触发 `Stop`/`SubagentStop`，所以用户输入必须在 `UserPromptSubmit` 先保存，关键结论要随形成随 checkpoint。
- 新增或修改 hooks 后，Codex 会按定义 hash 重新要求信任；在 CLI 执行 `/hooks` 审核并 trust，否则 hook 可能被跳过。
- handoff 不自动删除；清理前必须向用户给出保留/删除清单。
- `handoffs/` 下所有生成内容均为本机运行态，可能包含用户原话；禁止 Git 跟踪。仓库只保留该目录的 README 与 `.gitignore`。
- 当前实现对并发写使用全局文件锁和原子 JSON 替换。

## 验证

```powershell
python -m json.tool C:\Users\linkang\.codex\hooks.json
python -m py_compile C:\ADHD_agent\CodexMemory\scripts\subagent_handoff.py
python -m unittest discover -s C:\ADHD_agent\CodexMemory\tests -p test_subagent_handoff.py -v
```

2026-08-03 证据进展：7 项组件测试通过；早期带 `--dangerously-bypass-hook-trust` 的 smoke 只证明绕过信任时的接线。随后已按本机 Codex App Server 的 `currentHash` 补齐信任，独立查询确认 9/9 `trusted`，且不带 bypass 的最小 `codex exec` 在 37 秒内完成并由 SessionStart 创建记录。要求 spawn explorer 的原生 sub-agent E2E 及真实交互 `/side` 仍未通过，因此整套机制仍不得宣称验收完成。
