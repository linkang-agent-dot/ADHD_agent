# Browser finalize 误带已不受当前会话管理的旧标签

- 日期：2026-08-06
- 任务：X3 周年限定皮肤表现策划案预览交付
- 现象：finalize 时同时保留新策划案标签和上一轮已交付的旧 Demo 标签，工具返回 `cannot keep unknown tab`。
- 根因：把持久变量仍可引用误判为标签仍属于本轮 finalize 管理集合。
- 处理：仅保留本轮新建且仍受管理的周年策划案标签；后续 finalize 不跨轮携带旧 tab 变量。
- 状态：open
