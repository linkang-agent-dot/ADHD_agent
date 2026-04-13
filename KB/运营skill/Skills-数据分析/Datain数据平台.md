---
aliases: [datain-skill, datain, 游戏数据查询]
tags: [skill, 数据分析, datain, clickhouse]
skill_path: .agents/skills/datain-skill/
trigger: 游戏数据、留存、DNU、Cohort、收入、ROI、DAU、ROAS
---

# Datain 数据平台

## 概述
面向 SLG 手游的数据分析工具，基于 ClickHouse 聚合宽表，支持三大查询能力。

## 三大能力

### 1. 游戏数据查询
通过指定维度、指标、标签查询运营与市场数据：
- DNU（新增用户）、DAU（日活）
- 留存率、付费率
- Cohort 成长曲线
- 收入、ROI

### 2. 发行素材查询
以素材为粒度的投放数据统计：
- 展示、点击、花费
- ROAS（广告回报率）
- 投放效果分析

### 3. Datain 知识库
基于文档 RAG 检索回答平台使用相关问题。

## 配置要求
需要 `DATAIN_API_KEY` 环境变量。

## 关键文件
- `cache/` — 维度值、指标、标签缓存（jsonl/json）
- `scripts/query_game.py` — 查询脚本
- `assets/` — 静态资源
- `references/` — 参考文档

## 触发词
`游戏数据` `留存` `付费` `DNU` `Cohort` `收入` `ROI` `DAU` `素材分析` `投放效果` `ROAS` `Datain` `datain帮助`
