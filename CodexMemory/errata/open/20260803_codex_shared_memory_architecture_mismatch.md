# Codex 与 Claude 共用行为记忆导致能力边界混淆
- 日期：2026-08-03
- 任务：沉淀 Browser 恢复经验。
- 现象：Codex 将自身 Browser/Chrome 运行时经验写入 Claude 共用 memory；用户指出两种模型能力边界不同，共用一套行为记忆不够适配。
- 根因：原 Codex 薄壳规定全部记忆写入 Claude memory，没有区分“跨模型项目事实”和“模型专属工具经验”。
- 处理：建立 `C:\Users\linkang\.codex\memory\` 独立索引与 Claude 增量复核 checkpoint；Codex 专属经验写本地 memory，项目事实继续写共享 KB。
- 状态：resolved
