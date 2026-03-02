---
name: event-review-single
description: 节日单体数据 Review（Notion + Wiki 双版本）。七维深度分析（触达/行为/付费整体/R级/转化/奖励/礼包）+ 7 张图表 + AI 分析（异常检测/区间划分/活动定位/合理性评估）。支持多对标活动对比。
---

# 节日单体数据 Review（Notion + Wiki 双版本）

## When to Use This Skill

当用户需要：

- 生成活动/节日复盘报告（支持 Notion + Wiki 双版本输出）
- 七维数据分析：触达转化、行为数据、付费整体、R级付费、付费转化、核心奖励、商业化礼包
- AI 自动分析：异常检测、价位区间自动划分、活动定位判断、数值合理性评估
- 用户提到"单体数据复盘"、"单体review"、"single review"、"触达分析"、"R级分析"时

## 与「节日整体数据 Review」的差异

| 维度 | 整体数据 Review | 单体数据 Review |
|------|----------------|----------------|
| 输入数据 | 6 类（营收趋势/模块/分层/子活动等） | 7 类（触达/行为/付费整体/R级/转化/奖励/礼包） |
| 输出图表 | 3 张（营收趋势/模块堆叠/用户分层） | 7 张（漏斗/行为/付费趋势/R级/转化/偏差/礼包） |
| 分析深度 | 指标计算+趋势判断 | AI 分析（异常检测/区间划分/定位/评估） |
| 输出报告 | Notion + Wiki | Notion + Wiki |

## 执行流程

严格按照以下 5 个步骤顺序执行。**不要跳过任何步骤。**

---

### Step 1: 数据收集与校验

#### 1.1 数据来源

根据用户意图选择输入途径：

- 用户提到 "Notion"、提供 Notion 页面链接 → **途径 A**
- 用户提到 "Excel"、"表格"、"模板" → **途径 C**
- 用户直接提供 JSON / 口述数据 → **途径 B**
- 未明确时，**主动询问用户**

**途径 A: 从 Notion MCP 读取**

1. 使用 Notion MCP `search` 搜索活动数据页面
2. 使用 `fetch` 获取页面完整内容
3. 从页面表格中解析出 7 大数据块的标准 JSON 结构
4. 对于无法从页面获取的数据，向用户确认补充

**途径 B: 用户直接提供数据**

引导用户提供 7 部分数据。读取 `schema/input_schema.json` 查看完整字段定义。

**途径 C: Excel 模板输入**

1. 生成模板：

```bash
python skills/generate_event_review_v2/scripts/main.py --generate-template --output_dir report_images/<event_name_safe>/
```

2. 等待用户填写（8 个 Sheet: Meta/触达转化/行为数据/付费整体/R级付费/付费转化/核心奖励/商业化礼包）
3. 解析 + 分析一步完成（无需临时脚本）：

```bash
python skills/generate_event_review_v2/scripts/main.py --excel <Excel文件路径> --output_dir report_images/<event_name_safe>/
```

> **注意**：`--excel` 模式内置以下自动处理，无需额外脚本：
> - Windows 中文路径编码自动修复（UTF-8/GBK 错位检测 + 目录扫描匹配）
> - 空 Sheet（如行为数据为空）仅警告，不阻断分析
> - Excel 中 `#DIV/0!` 等公式错误自动转为 0，ARPU/ARPPU 为 0 时自动从触达数据反算
> - 解析后自动保存中间 JSON 到 `output_dir/input_data.json`（便于排查）

#### 1.2 七大输入数据

| # | 数据块 | 关键字段 |
|---|--------|---------|
| 1 | meta | event_name, change_description |
| 2 | reach_conversion | stages(漏斗各阶段人数), comparisons(多对标) |
| 3 | behavior_data | metrics(行为指标列表), daily_trend(可选) |
| 4 | payment_overview | time_series(至少6个月), yoy_benchmarks(多对标) |
| 5 | r_tier_payment | tiers(R级列表), time_series(至少6个月), benchmarks(多对标) |
| 6 | payment_conversion | current(各价位购买数据), comparisons(多对标) |
| 7 | core_reward | items(奖励预期vs实际) |
| 8 | gift_packages | packages(礼包列表), comparisons(多对标) |

#### 1.3 多对标活动支持

系统支持同时对比多个对标活动。在 Excel 中标注方式：

- 在对标列填写 `对标-2025春节`、`对标-2025圣诞节` 等标签
- 或在 `数据类型` 列写入 `对标活动-AAA`、`对标活动-BBB`
- 触达转化 Sheet 可添加多组"对标活动名称"+"对标人数"列

系统会自动识别并解析所有标注的对标活动，在分析、图表和报告中全部展示对比。

#### 1.3 数据校验

> 使用 `--excel` 模式时，校验已内置在流程中，无需手动调用。仅在途径 A/B 时需手动校验：

```python
from data_validator import validate_input
result = validate_input(data)
if not result["valid"]:
    # 向用户反馈 result["errors"] 中的错误信息
for w in result.get("warnings", []):
    print(f"[WARN] {w}")
```

校验规则：
1. meta 必填字段（event_name, change_description）
2. reach_conversion.stages 至少 3 层
3. **behavior_data: 可选**（空数据仅产生警告，不阻断流程）
4. payment_overview.time_series 至少 6 条
5. r_tier_payment.time_series 至少 6 条
6. payment_conversion.current.price_tiers 至少 3 条
7. core_reward.items 至少 1 条
8. gift_packages.packages 至少 1 条
9. 数值合法性（revenue >= 0, pay_rate 0~100 等）

---

### Step 2: 分析 + 图表生成

**途径 C（推荐）**：`--excel` 模式已在 Step 1 中完成分析，此步自动执行。

**途径 A/B**：需手动调用主入口：

```bash
# 命令行（从 JSON 输入）
python skills/generate_event_review_v2/scripts/main.py --input <数据JSON路径> --output_dir report_images/<event_name_safe>/
```

```python
# 或 Python 模块调用
import sys
sys.path.insert(0, 'skills/generate_event_review_v2/scripts')
from main import run_analysis

result = run_analysis(input_data, 'report_images/<event_name_safe>/')
```

#### 2.1 七大分析模块

| # | 分析器 | 分析内容 | 输出图表 |
|---|--------|---------|---------|
| 1 | ReachAnalyzer | 漏斗转化率+瓶颈检测 | 1_Reach_Funnel.png |
| 2 | BehaviorAnalyzer | 行为指标对比+日趋势异常 | 2_Behavior_Data.png |
| 3 | PaymentOverviewAnalyzer | 环比/同比/趋势形态判断 | 3_Payment_Overview.png |
| 4 | RTierAnalyzer | R级结构+活动定位 | 4_RTier_Payment.png |
| 5 | ConversionAnalyzer | AI价位区间划分+异常检测 | 5_Conversion_Compare.png |
| 6 | RewardAnalyzer | 预期vs实际偏差评估 | 6_Reward_Deviation.png(可选) |
| 7 | PackageAnalyzer | 礼包合理性+调整建议 | 7_Package_Compare.png |

每个分析器返回标准化 `AnalysisResult`:
- `conclusion`: 核心结论
- `severity`: 正常/关注/异常/严重
- `details`: 详细分析要点
- `suggestions`: 改进建议
- `chart_data`: 图表所需数据

---

### Step 3: 报告组装

```python
from report_generator import ReportGenerator

generator = ReportGenerator(data, analysis_results, chart_dir)
notion_content = generator.generate_notion_content()
notion_title = generator.generate_notion_title()
wiki_content = generator.generate_wiki_content()
```

#### 报告结构（双版本共用）

1. Executive Summary（综合评价 + Top3 关键发现）
2. 一、触达分析（结论 + 漏斗图）
3. 二、行为分析（结论 + 行为图）
4. 三、付费整体分析（结论 + 趋势图 + 同比环比表）
5. 四、R级付费分析（结论 + R级图 + 活动定位）
6. 五、付费转化分析（结论 + 转化图 + 区间明细表）
7. 六、数值设计评估（结论 + 偏差表/图）
8. 七、礼包分析（结论 + 礼包图 + 调整建议）
9. 综合建议（P0/P1/P2 分级）

#### Wiki 版本格式规则

- 不用 `**粗体**`、HTML、Emoji
- 用【】强调关键数字
- 用 `> [图表] 请手动插入: X_Name.png` 占位
- 表格用管道语法 `| col | col |`

#### Notion 版本格式规则

- 使用 `<callout>` / `<span color="">` / `<table>` 等 Notion 语法
- 正向指标: `<span color="red">**+XX.X%**</span>`
- 负向指标: `<span color="blue">**-XX.X%**</span>`

---

### Step 4: 发布输出

#### 4.1 Notion 版本

使用 Notion MCP `create-pages` 发布：

```
工具: Notion MCP create-pages
参数:
  parent: {"page_id": "<父页面ID>"}
  pages: [{
    "properties": {"title": "<notion_title>"},
    "content": "<notion_content>"
  }]
```

#### 4.2 Wiki 版本

**直接在聊天框中输出完整报告内容**，不写入文件。用户复制粘贴到 Wiki 编辑器。

---

### Step 5: 交付确认

交付物清单：

1. **7 张图表** - 保存在 `report_images/{event_name}/` 目录
2. **Notion 页面** - 已发布，返回页面 URL
3. **Wiki 报告** - 聊天框直接输出
4. **Excel 模板**（仅途径 C）- 告知文件路径

---

## 依赖

- Python 3.9+
- matplotlib>=3.7.0, numpy>=1.24.0, openpyxl>=3.1.0, scipy>=1.10.0

```bash
pip install -r skills/generate_event_review_v2/scripts/requirements.txt
```

## 错误处理

- 缺少依赖 → 自动安装 requirements.txt
- 数据校验失败 → 反馈具体错误，引导用户修正
- behavior_data 为空 → 自动跳过行为分析（警告，不阻断）
- ARPU/ARPPU 为 0（Excel `#DIV/0!`） → 自动从触达数据反算
- Windows 中文路径乱码 → 自动编码修复（支持 UTF-8/GBK 错位 + 目录扫描匹配）
- 图表生成失败 → 检查 matplotlib 中文字体配置
- Notion 发布失败 → 重试或改为输出 Markdown 文本
