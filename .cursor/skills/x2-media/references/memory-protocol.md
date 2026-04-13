# Memory Protocol（与 MCP 可选集成）

本文件与 `rules/x2-media.mdc` 第 5 条一致，供同事查阅字段约定。

## 前提

仅在 Cursor 中**已连接**提供 `memory_search` / `memory_write` 的 MCP（如团队自建的 agent-memory）时执行；**无工具则跳过**，不影响 `--download-dir` 与 `history.jsonl`。

## 任务开始（可选）

1. 调用 `memory_search`，查询与当前任务相关的历史（如：同类型默认模型、常见失败原因）。
2. （可选）创建 `state/.media_session.json`，内容示例：`{"started_at": "ISO8601", "type_key": "ui_extract"}`。

## 任务结束（可选）

1. 调用 `memory_write`，写入可复用经验（如：某模型对九宫格不稳定、某后端超时阈值）。
2. 删除 `state/.media_session.json`（若曾创建）。

## 与本地 history 的关系

- **`state/history.jsonl`**：每次生成的**事实记录**（时间、类型、路径、URL），**不依赖 MCP**，建议始终追加。
- **MCP memory**：偏**经验与检索**，可选。
