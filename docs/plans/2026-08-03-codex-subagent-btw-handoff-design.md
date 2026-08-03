# Codex sub-agent / BTW 回主对话机制设计

## 背景与目标

BTW 临时对话被 Ctrl+C 关闭后没有保存为可恢复会话，用户在其中完成的业务判断随之丢失。现有 sub-agent 正常结束时会向 parent 返回最终消息，但无法覆盖中断、窗口关闭、turn abort 或 agent 尚未形成 final 的情况。

目标是让所有子任务（BTW、default/worker/explorer、task-checker 及其他自定义 agent）都有统一、可审计、可由主对话自动接管的 handoff。恢复不依赖临时会话是否仍可 `resume`。

## 方案选择

采用“Codex lifecycle hooks + 持久化 handoff 台账 + agent 侧 checkpoint 指令”的混合方案。

- 不采用纯提示词方案：正常结束可用，但 Ctrl+C 时不可靠。
- 不采用后台 daemon 全量解析 JSONL：恢复能力强，但官方明确 transcript 格式不是稳定接口，版本升级维护风险高。
- 混合方案以稳定 hook 字段和自有 Markdown/JSON 为恢复真源；原始 transcript 仅做尽力快照，不作为唯一依赖。

## 目录结构

每个主对话建立独立目录：

```text
C:\ADHD_agent\CodexMemory\handoffs\
└─ YYYY-MM-DD_<首条任务摘要>_<主会话短ID>\
   ├─ main.json
   ├─ sub-agent\
   │  └─ <agent类型>_<agent短ID>\
   │     ├─ user-prompts.md
   │     ├─ checkpoints.md
   │     ├─ final-handoff.md
   │     ├─ state.json
   │     └─ transcript-snapshot.jsonl
   └─ BTW\
      └─ <BTW短ID>\
         ├─ user-prompts.md
         ├─ checkpoints.md
         ├─ final-handoff.md
         ├─ state.json
         └─ transcript-snapshot.jsonl
```

目录名由日期、首条有效用户任务的安全摘要和主 session 短 ID 组成。无法识别标题时使用 `untitled`。路径名会移除 Windows 非法字符并限制长度。

## 生命周期与数据流

### 子任务开始

`SubagentStart` hook 创建 agent 目录和 `state.json`，状态为 `active`，并向子 agent 注入以下约束：

1. 收到业务判断或完成物理改动后，立即调用 checkpoint 脚本。
2. final 必须包含结论、改动、未决项、主对话下一步。
3. 不把仅存在于推理上下文中的结论当作已保存。

原生 sub-agent 放入 `sub-agent/`。BTW/side chat 若没有 `SubagentStart` 事件，则由 `UserPromptSubmit` 根据 transcript/session 上下文建立 `BTW/` 记录。

### 运行中

`UserPromptSubmit` 将用户提示原样追加到对应 `user-prompts.md`。agent 使用统一 checkpoint CLI 将结构化进展追加到 `checkpoints.md`；脚本采用原子写入和文件锁，避免并发子 agent 相互覆盖。

每次 checkpoint 尽力复制当前 transcript 到 `transcript-snapshot.jsonl`。快照失败只记 warning，不影响主任务。

### 正常完成

`SubagentStop` 检查 handoff 是否完整：

- 有 final：写入 `final-handoff.md`，状态改为 `completed`。
- final 缺少必要字段：hook 要求 agent 继续一轮补齐结构化 handoff。
- task-checker 等只读验收 agent 同样执行，不豁免。

Codex 原生 parent 回传仍保留；持久化 handoff 是第二条恢复链路。

### 中断与恢复

如果 Ctrl+C 导致 `SubagentStop` 未执行，目录保持 `active` 或标记 `interrupted`，其中仍保存用户提示和最后一次 checkpoint。

`SessionStart`（startup/resume）和主线程 `UserPromptSubmit` 扫描当前 parent session 下未 `claimed` 的记录，将精简 handoff 作为 `additionalContext` 注入主对话。主 agent确认接管后，通过 CLI 将状态改为 `claimed`。文件保留，不自动删除。

## 状态模型

```text
active -> completed -> claimed
   |          |
   +-> interrupted -> claimed
   +-> failed ------> claimed
```

`state.json` 至少包含：schema_version、parent_session_id、agent_id、agent_type、channel、status、created_at、updated_at、claimed_at、transcript_path、warnings。

## 安全与边界

- 不自动删除 handoff；清理必须遵守“先列保留/删除清单给用户确认”。
- 不在 hook 输出中回显密钥、token 或整份超长 transcript。
- 主对话只注入结论、未决项和最近 checkpoint；完整记录通过本地路径查阅。
- Ctrl+C 发生在结论形成但尚未 checkpoint 的瞬间时，内部推理不能保证恢复；自动保存的用户提示和已执行动作仍可恢复。
- hooks 变更后需要在 Codex `/hooks` 中重新审核信任，这是启用机制的必要步骤。

## 验证标准

1. 模拟普通 sub-agent 正常完成：主对话收到原生结果，目录中存在 completed handoff。
2. 模拟 sub-agent 在 checkpoint 后中断：下次主对话输入自动收到未接管内容。
3. 模拟 BTW 只收到用户判断便 Ctrl+C：`user-prompts.md` 仍包含该判断。
4. 两个 agent 并发：目录隔离、无覆盖、状态正确。
5. handoff 已 claimed 后不重复注入，但文件仍保留。
6. hooks 脚本异常时不阻断正常任务，只输出明确 warning。
