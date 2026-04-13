---
aliases: [ai-to-sql, Trino SQL, 写SQL]
tags: [skill, 数据分析, trino, sql]
skill_path: .agents/skills/ai-to-sql/
trigger: 写SQL、生成SQL、trino、玩家日志、wiki、业务定义
---

# AI-to-SQL

## 概述
公司数据平台 Datain 的自然语言生成 Trino SQL 技能。默认只返回 SQL 不自动执行，仅当用户明确要求时才执行查询并返回数据。

## 核心能力
1. **SQL 生成** — 根据自然语言描述生成 Trino SQL
2. **SQL 执行** — 用户明确要求时执行并返回结果
3. **辅助检索** — 指标参考 SQL、wiki 知识库 RAG、表结构探索、权限校验

## 覆盖场景
- 玩家明细日志：登录、行为、活动、资产变动、付费订单、战斗
- 业务概念、游戏活动、数据定义等优先通过知识库检索

## 触发词
`写SQL` `生成SQL` `数仓查询` `trino` `玩家日志` `登录日志` `资产变动` `活动参与` `游戏行为` `wiki` `文档` `业务定义` `活动说明`

## 关键文件
- `SKILL.md` — 主技能定义
- `config.json` — 配置
- `scripts/` — `_datain_api.py`、`get_game_info.py`、`rag_search.py`、`query_trino.py`、`explore_tables.py`、`search_tables.py`

## 相关技能
- [[Datain数据平台]] — 聚合宽表查询（另一种数据查询路径）
- [[Dashboard看板]] — 查询结果可视化
