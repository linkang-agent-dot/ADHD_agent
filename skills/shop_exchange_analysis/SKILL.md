---
name: shop-exchange-analysis
description: 兑换商店数据深度分析（Notion + Wiki 双版本）。五维分析 + 5 张图表 + 运营优化建议。支持自动道具分类、饱和度评估、代币消耗结构拆解、四象限定位。
---

# 兑换商店数据深度分析（Notion + Wiki 双版本）

## When to Use This Skill

当用户需要：

- 分析游戏内兑换商店的道具数据
- 评估兑换饱和度、代币消耗、商品结构
- 用户提到"兑换商店"、"商店分析"、"兑换数据"、"shop exchange"、"兑换饱和度"、"代币消耗"时
- 其他复盘 Skill（如 event-review-single）中涉及兑换商店子模块时

## 输入数据

### 必填字段

每条道具数据需包含以下字段：

| 字段 | 中文 | 类型 | 说明 |
|------|------|------|------|
| item_name | 道具名称 | string | 道具全称 |
| exchange_users | 兑换人次 | int | 兑换该道具的总人次 |
| exchange_count | 兑换次数 | int | 兑换该道具的总次数 |
| avg_exchanges_per_user | 人均兑换次数 | float | = exchange_count / exchange_users |
| avg_token_cost | 平均消耗代币 | float | 人均代币消耗 |
| token_price | 代币价格 | int | 单次兑换的代币单价 |
| purchase_limit | 限购数量 | int | 每人限购上限 |
| saturation_rate | 兑换饱和度 | float | = avg_exchanges_per_user / purchase_limit × 100% |

### 可选字段

| 字段 | 中文 | 类型 | 说明 |
|------|------|------|------|
| activity_name | 活动名称 | string | 所属活动（用于报告标题） |
| shop_name | 商店名称 | string | 商店名称（如有多个商店） |
| category | 道具类别 | string | 手动指定分类（留空则自动分类） |

## 数据输入方式

根据用户意图选择输入途径：

### 途径 A: 文本粘贴（最常用）

用户直接粘贴 Tab 分隔或表格格式的数据。Agent 解析后转为标准 JSON。

**解析规则：**
1. 自动识别表头行（包含"道具名称"或"item_name"）
2. 按 Tab / 空格 / | 分隔符切分
3. 数值列自动去除 % 符号并转 float
4. 重复道具名称自动添加序号后缀（如 ②③）

### 途径 B: JSON 直接输入

用户提供符合 `schema/input_schema.json` 的 JSON 数据。

### 途径 C: Excel 文件

1. 生成模板：

```python
import sys
sys.path.insert(0, 'skills/shop_exchange_analysis/scripts')
from data_parser import generate_excel_template

generate_excel_template('KB/产出-数据分析/<activity_name>/shop_template.xlsx')
```

2. 等待用户填写
3. 解析 Excel：

```python
from data_parser import parse_excel
data = parse_excel('<Excel文件路径>')
```

## 执行流程

严格按照以下 5 个步骤顺序执行。**不要跳过任何步骤。**

---

### Step 1: 数据收集与解析

1. 根据用户输入方式，调用对应的解析函数
2. 自动进行道具分类（详见分类规则）
3. 计算衍生指标（总代币消耗 = 兑换次数 × 代币价格）
4. 数据校验：检查必填字段、数值合法性

```python
import sys, json
sys.path.insert(0, 'skills/shop_exchange_analysis/scripts')
from data_parser import parse_text_input, auto_categorize

items = parse_text_input(raw_text)  # 或 parse_excel / parse_json
items = auto_categorize(items)
```

**道具自动分类规则：**

| 类别 | 关键词匹配 |
|------|-----------|
| 主城皮肤 | 皮肤 |
| 英雄养成 | 英雄, 升星, 碎片 |
| 军备养成 | 军备, T6 |
| 装备养成 | 装备, 纳米, 晶体, 重铸 |
| 加速道具 | 加速 |
| 收藏品 | 收藏品 |
| 核心材料 | 机能核心 |
| 资源/抽奖 | 资源, 奖池, 宝箱 |

> Agent 可根据实际游戏版本扩展分类规则。若遇到无法自动分类的道具，向用户确认。

---

### Step 2: 分析引擎

调用分析模块，生成五维分析结论：

```python
from analyzer import ShopExchangeAnalyzer

analyzer = ShopExchangeAnalyzer(items)
results = analyzer.run_all()
```

#### 2.1 五大分析维度

| # | 维度 | 分析内容 | 输出 |
|---|------|---------|------|
| 1 | 饱和度分析 | 排名、高/低饱和度分组、供需失衡检测 | 高需求/供过于求道具清单 |
| 2 | 消耗结构分析 | 各类别代币消耗占比、消耗集中度 | 类别占比表 + 核心发现 |
| 3 | 人次-消耗交叉分析 | 覆盖广度 vs 消耗深度 | 象限分布 |
| 4 | 四象限定位 | 人均消耗 × 饱和度 四象限 | 道具定位矩阵 |
| 5 | 皮肤专项分析 | 高价限量道具专项（如有） | 皮肤兑换情况 |

#### 2.2 分析阈值配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| HIGH_SATURATION_THRESHOLD | 10% | 高饱和度分界线 |
| MED_SATURATION_THRESHOLD | 5% | 中饱和度分界线 |
| LOW_SATURATION_THRESHOLD | 1% | 低饱和度分界线 |
| SKIN_PRICE_THRESHOLD | 50000 | 皮肤类高价道具分界线 |

> Agent 可根据实际数据分布动态调整阈值。

---

### Step 3: 图表生成

```python
from chart_generator import ShopChartGenerator

chart_gen = ShopChartGenerator(items, results, output_dir)
chart_gen.generate_all()
```

#### 5 张图表

| # | 图表 | 文件名 | 说明 |
|---|------|--------|------|
| 1 | 兑换饱和度排名 | chart1_saturation.png | 水平条形图 + 阈值线 + 分类着色 |
| 2 | 人次vs消耗气泡图 | chart2_bubble.png | 双对数轴 + 分类气泡 |
| 3 | 分类消费结构 | chart3_category_pie.png | 双饼图（消耗占比 + 人次占比） |
| 4 | 四象限定位 | chart4_quadrant.png | 散点图 + 中位数分割 + 象限标注 |
| 5 | 皮肤/高价道具专项 | chart5_special.png | 条形图（仅有高价道具时生成） |

图表风格：
- DPI: 150
- 中文字体: SimHei / Microsoft YaHei
- 颜色方案: 按类别统一配色
- 去除顶部/右侧边框

---

### Step 4: 报告生成 + 发布

#### 4.1 Notion 版本

```python
from report_generator import ShopReportGenerator

report_gen = ShopReportGenerator(items, results, chart_dir, activity_name)
notion_content = report_gen.generate_notion()
notion_title = report_gen.generate_title()
```

使用 Notion MCP `create-pages` 发布：

```
工具: Notion MCP create-pages
参数:
  pages: [{
    "properties": {"title": "<notion_title>"},
    "content": "<notion_content>"
  }]
```

**Notion 格式规则：**
- Executive Summary 用 `<callout icon="🏪" color="blue_bg">` 包裹
- 正向指标用 `<span color="green">`，负向用 `<span color="red">`
- 表格用 `<table><tr><td>` 格式
- 建议用 `<span color="red">` 标注高优先级，`<span color="orange">` 标注中优先级

#### 4.2 Wiki 版本

**直接在聊天框中输出完整报告内容**，用户复制粘贴到 Wiki 编辑器。

**Wiki 格式规则：**
- 不用 `**粗体**`、HTML、Emoji
- 用【】强调关键数字
- 表格用管道语法 `| col | col |`

#### 4.3 本地 Markdown 版本

同时保存一份到 `KB/产出-数据分析/<activity_name>/商店兑换数据分析报告.md`

---

### Step 5: 交付确认

交付物清单：

1. **5 张图表** - 保存在 `KB/产出-数据分析/{activity_name}/` 目录
2. **Notion 页面** - 已发布，返回页面 URL
3. **Wiki 报告** - 聊天框直接输出（用户要求时）
4. **本地 Markdown** - 保存在图表同目录

---

## 报告结构（双版本共用）

1. **Executive Summary** — 4 条核心发现摘要
2. **一、数据总览** — 关键指标汇总表
3. **二、兑换饱和度分析** — 高/低饱和度分组 + 图表
4. **三、代币消耗结构分析** — 类别占比 + 图表
5. **四、兑换人次 vs 代币消耗** — 象限解读 + 图表
6. **五、四象限定位分析** — 定位矩阵 + 图表
7. **六、高价道具/皮肤专项**（如有）— 专项分析 + 图表
8. **七、运营优化建议** — P1/P2/P3 分级建议
   - P1: 限购调整建议
   - P2: 定价策略建议
   - P3: 商品结构建议

---

## 与其他 Skill 的集成

本 Skill 可被其他复盘 Skill 作为子模块调用：

```python
# 在 event-review-single 或其他 Skill 中
import sys
sys.path.insert(0, 'skills/shop_exchange_analysis/scripts')
from main import run_shop_analysis

# 传入标准化数据
result = run_shop_analysis(
    items=items_list,          # List[dict] 道具数据
    activity_name='推币机',     # 活动名称
    output_dir='KB/产出-数据分析/推币机/',  # 输出目录
    output_format='both'       # 'notion' / 'wiki' / 'both'
)

# 返回
# result['charts']         → 图表文件路径列表
# result['analysis']       → 分析结论 dict
# result['notion_content'] → Notion 格式报告内容
# result['wiki_content']   → Wiki 格式报告内容
# result['markdown']       → 本地 Markdown 内容
```

---

## 依赖

- Python 3.9+
- matplotlib>=3.7.0, numpy>=1.24.0, pandas>=2.0.0, openpyxl>=3.1.0

```bash
pip install matplotlib numpy pandas openpyxl
```

## 错误处理

- 缺少依赖 → 自动安装
- 数据解析失败 → 提示用户检查格式，给出预期格式示例
- 图表生成失败 → 检查 matplotlib 中文字体，尝试 fallback 字体
- Notion 发布失败 → 重试或改为输出 Markdown 文本
- 道具无法自动分类 → 向用户确认分类
