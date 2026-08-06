# 子任务持久化 checkpoint 导致主线程补丁上下文失效

- 日期：2026-08-05
- 任务：归档 X3 英雄皮肤主动 BUFF 方案并推进 Claude memory 复核 checkpoint
- 现象：主线程按先前读取值更新 `CLAUDE_REVIEW_CHECKPOINT.md` 时，`apply_patch` 报 expected lines 不存在。
- 根因：两个只读验收子任务按 handoff 规范执行持久化 checkpoint，在主线程计算补丁后更新了同一 checkpoint 文件；主线程补丁上下文因此过期。
- 处理：停止覆盖，重新读取 checkpoint 当前内容，再基于最新值做最小补丁。今后存在 handoff 子任务时，把全局 review checkpoint 更新放到全部子任务结束之后。
- 状态：open

