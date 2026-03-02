---
name: event-review-single
description: 节日单体数据 Review（Notion + Wiki 双版本）。七维深度分析：触达转化/行为/付费整体/R级/付费转化/核心奖励/礼包。生成 7 张高清图表，包含 AI 分析（异常检测/区间自动划分/活动定位/合理性评估）。支持三种数据输入方式：1) Notion MCP 读取；2) Excel 模板填写；3) JSON 直接输入。当用户提到"单体数据复盘"、"节日单体review"、"single review"、"触达分析"、"R级分析"、"礼包分析"时使用。
---

# 节日单体数据 Review（Notion + Wiki 双版本）

本文件为入口引用，完整 Skill 指令请读取以下文件：

**请立即使用 Read 工具读取以下文件，然后严格按照其中的指令执行：**

1. 完整 Skill 指令: `skills/generate_event_review_v2/SKILL.md`
2. 输入数据 Schema: `skills/generate_event_review_v2/schema/input_schema.json`
3. 示例数据（可用于测试）: `skills/generate_event_review_v2/schema/example_data.json`
4. 数据校验模块: `skills/generate_event_review_v2/scripts/data_validator.py`
5. Excel 模板生成与解析: `skills/generate_event_review_v2/scripts/excel_handler.py`
6. 分析引擎: `skills/generate_event_review_v2/scripts/analyzers/`
7. 图表生成器: `skills/generate_event_review_v2/scripts/charts/`
8. 报告生成模块: `skills/generate_event_review_v2/scripts/report_generator.py`
9. 主入口: `skills/generate_event_review_v2/scripts/main.py`
10. Wiki 报告模板: `skills/generate_event_review_v2/assets/report_template_wiki.md`
11. Notion 报告模板: `skills/generate_event_review_v2/assets/report_template_notion.md`
