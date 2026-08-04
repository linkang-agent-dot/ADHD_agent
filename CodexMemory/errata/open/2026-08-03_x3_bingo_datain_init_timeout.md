# X3 BINGO 补偿调查 Datain 初始化超时

- 日期：2026-08-03
- 任务：查询 101830 拼图事故中的钻石消耗玩家
- 现象：`get_game_info.py` 请求 `datain-api.tap4fun.com` 在 15 秒读取超时；随后 wiki RAG 请求 `172.20.90.13:8000` 也在 30 秒读取超时。
- 根因：Datain 辅助元数据/RAG 接口网络读取不稳定，尚无证据表明鉴权或 SQL 有误；PowerShell 60 秒直连 games API 已成功确认 X3=1090/A3_TRINO。
- 处理：保留原查询口径；辅助检索超时后不阻塞，使用已验证的 X3 `TRINO_HF / v1090` 视图做小样本探查并逐步恢复。
- 后续绕道：在 PowerShell 参数中嵌套 JSON 双引号时，`query_trino.py --sql` 被拆成多参数并报 `unrecognized arguments`；改用不含嵌套引号的 `LIKE '%actvType%18%'`，避免 shell 转义层干扰。
- 状态：open
