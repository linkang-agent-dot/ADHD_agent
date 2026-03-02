---
name: event-review-overall
description: 节日整体数据 Review（Notion + Wiki 双版本）。分析活动整体营收趋势、模块表现、用户分层、子活动诊断。生成 3 张高清图表，输出 Notion + Wiki 双版本复盘报告。支持从 Notion MCP 读取或 Excel 模板输入。
---

# 节日整体数据 Review（Notion + Wiki 双版本）

## When to Use This Skill

当用户需要：

- 生成一份活动/节日复盘报告（支持 **Notion 页面** 和 **Wiki/Confluence Markdown** 双版本输出）
- 对比当期活动与历史活动的营收、ARPU、付费率等核心指标
- 可视化展示模块营收结构、用户分层 ARPU 趋势
- 自动诊断子活动表现（Keep / Optimize 分类）
- 从 Notion 数据库中读取活动数据并生成报告
- 用户提到"活动总结"、"复盘报告"、"节日 review"、"event review"等关键词时

## 执行流程

严格按照以下 4 个步骤顺序执行。**不要跳过任何步骤。**

---

### Step 1: 数据收集与校验

#### 1.1 数据来源

数据可以来自以下三种途径，根据用户意图选择：

- 用户提到 "Notion"、提供 Notion 页面链接 → **途径 A**
- 用户提到 "Excel"、"表格"、"模板" → **途径 C**
- 用户直接提供 JSON / 口述数据 → **途径 B**
- 未明确时，**主动询问用户**使用哪种输入方式

**途径 A: 从 Notion MCP 读取**

如果用户提到"从 Notion 获取"或提供了 Notion 页面链接：
1. 使用 Notion MCP 的 `search` 工具搜索相关活动数据页面
2. 使用 `fetch` 工具获取页面完整内容
3. 从 Notion 表格中解析出标准化数据（付费总额、ARPU、付费率、R级分层、模块付费等）
4. **从页面中识别或向用户确认模块分类映射**（每个子活动归属 外显/小游戏/养成/混合 哪个模块）
5. 将解析后的数据转换为下述标准 JSON 结构（包含 module_classification）

**途径 B: 用户直接提供数据**

如果用户尚未提供数据，使用以下模板引导用户提供。读取 `schema/input_template.json` 查看完整字段定义。

**途径 C: Excel 模板输入**

如果用户希望通过 Excel 填写数据：

1. **生成模板**：调用 `scripts/excel_handler.py` 生成空白 Excel 模板

```python
import sys
sys.path.insert(0, 'skills/generate_event_review/scripts')
from excel_handler import generate_template, parse_excel, save_as_json

# 生成模板到指定目录
generate_template('report_images/<event_name_safe>/event_review_template.xlsx')
```

或通过命令行：
```bash
python skills/generate_event_review/scripts/excel_handler.py generate -o <输出路径>
```

2. **等待用户填写**：告知用户模板已生成，模板包含 5 个 Sheet（Meta、核心大盘趋势、模块营收趋势、用户分层ARPU、子活动明细），每个 Sheet 有表头、字段说明行和示例数据。用户填完后通知 Agent。

3. **解析 Excel**：用户填好后，调用 `parse_excel()` 读取并转换为标准 JSON

```python
from excel_handler import parse_excel, save_as_json

data = parse_excel('<Excel文件路径>')
save_as_json(data, 'report_images/<event_name_safe>/input_data.json')
```

解析器会自动跳过说明行和空行，并调用 `validate_input()` 校验数据完整性。如果校验失败，会抛出详细的中文错误信息（指出哪个 Sheet 哪一行有问题），此时应将错误信息反馈给用户修正。

需要用户提供 **6 部分** 标准化数据：

**A. 基础信息 (Meta)**
```json
{
  "event_name": "活动名称，如 2026春节",
  "benchmark_event": "对标活动名称，如 2025春节"
}
```

**B. 核心大盘趋势 (metrics_trend)** - 用于生成图1
```json
[
  {"event": "活动名", "revenue": 总营收, "arpu": ARPU值, "pay_rate": 付费率百分比},
  ...
]
```
要求：至少 6 个数据点（近 6 个月活动 + 对标活动作为最后一项）。

**C. 模块表现趋势 (module_trend)** - 用于生成图2
```json
[
  {"event": "活动名", "appearance": 外显营收, "minigame": 小游戏营收, "hybrid": 混合营收},
  ...
]
```
要求：时间节点与大盘趋势对应。

**D. 用户分层趋势 (user_tier_trend)** - 用于生成图3
```json
[
  {"event": "活动名", "super_r": 超R的ARPU, "big_r": 大R的ARPU, "mid_r": 中R的ARPU},
  ...
]
```
要求：至少 2 个数据点（当期 + 对标）。

**E. 子活动明细 (sub_activity_detail)** - 用于生成诊断表
```json
[
  {"name": "子活动名", "type": "类型", "revenue": 营收, "status": "Keep或Optimize", "reason": "诊断理由"},
  ...
]
```

**F. 模块分类映射 (module_classification)** - 必填，用于模块付费分析
```json
[
  {"name": "子活动名", "module": "外显/小游戏/养成/混合", "note": "备注（可选）"},
  ...
]
```
要求：每个子活动必须标注所属模块（外显 / 小游戏 / 养成 / 混合）。此映射用于：
1. 自动补全子活动明细中的 `type` 字段
2. 自动聚合计算当期各模块营收
3. 辅助模块付费结构分析（对比 module_trend 中的历史数据）

**注意：无论使用途径 A（Notion）还是途径 B/C（直接提供/Excel），都必须提供模块分类数据。** 从 Notion 读取时，如果页面中有模块/分类相关的表格，应解析出此映射；如果没有，需要向用户确认每个子活动的所属模块。

#### 1.2 数据校验

收到用户数据后，**必须**执行以下校验：

1. 检查所有 6 个部分是否完整（含 module_classification）
2. 检查 `metrics_trend` 是否至少有 6 个数据点
3. 检查 `module_trend` 时间节点是否与 `metrics_trend` 对应
4. 检查 `sub_activity_detail` 中 `status` 值是否为 `Keep` 或 `Optimize`
5. 检查 `module_classification` 中每条记录的 `module` 是否为 `外显/小游戏/养成/混合` 之一
6. 如果校验失败，**明确告知用户缺什么数据**，不要猜测

#### 1.3 数据格式兼容

用户可能以不同格式提供数据（JSON、Markdown 表格、口述要点）。无论哪种格式，都需要将其转换为上述标准 JSON 结构后再进行后续处理。

---

### Step 2: 图表生成

#### 2.1 准备数据文件

将校验通过的数据保存为临时 JSON 文件：

```bash
# 在项目根目录创建临时数据文件
# 文件路径: report_images/{event_name}/input_data.json
```

#### 2.2 调用图表生成脚本

运行 `scripts/chart_generator.py`:

```bash
python skills/generate_event_review/scripts/chart_generator.py --input <数据JSON路径> --output_dir report_images/<event_name_safe>/
```

其中 `<event_name_safe>` 是将活动名中的空格和特殊字符替换为下划线后的版本。

#### 2.3 生成产物

脚本将在输出目录中生成 3 张图片：

- `1_Revenue_Trend.png` - 核心大盘趋势折线图（双Y轴：营收+ARPU，含趋势拟合线和同比参考线）
- `2_Module_Structure.png` - 模块营收堆叠面积图
- `3_User_Growth.png` - 用户分层 ARPU 分组柱状图

同时脚本会输出计算指标（同比/环比变化率、趋势形态判断），用于 Step 3。

#### 2.4 错误处理

如果脚本执行失败：
- 检查 Python 环境是否安装了 `matplotlib` 和 `numpy`（如未安装则执行 `pip install matplotlib numpy`）
- 检查输入 JSON 文件格式是否正确
- 查看错误输出信息并修复后重试

---

### Step 3: 报告组装（Wiki + Notion 双版本）

本步骤生成两个版本的报告。可使用 `scripts/notion_publisher.py` 中的函数自动生成，也可手动按模板填充。

#### 3.0 使用脚本自动生成（推荐）

```python
import sys
sys.path.insert(0, 'skills/generate_event_review/scripts')
from notion_publisher import generate_notion_content, generate_notion_title, generate_wiki_content
from chart_generator import compute_metrics

# metrics 来自 Step 2 的 generate_all_charts() 返回值中的 metrics 字段
notion_content = generate_notion_content(data, metrics)
notion_title = generate_notion_title(data)
wiki_content = generate_wiki_content(data, metrics, chart_dir='report_images/<event_name_safe>/')
```

#### 3.0a Wiki 版本

读取 `assets/report_template.md` 模板，然后根据数据和计算结果**逐项填充**。

#### 3.1 模板变量替换规则

| 变量 | 填充逻辑 |
|------|----------|
| `{{EVENT_NAME}}` | meta.event_name |
| `{{BENCHMARK_EVENT}}` | meta.benchmark_event |
| `{{GENERATED_AT}}` | 当前日期时间 |
| `{{EXECUTIVE_SUMMARY}}` | 基于趋势判断和关键指标自动生成 2-3 句总结 |
| `{{CHART_1_PATH}}` | 图1的相对路径 |
| `{{CHART_2_PATH}}` | 图2的相对路径 |
| `{{CHART_3_PATH}}` | 图3的相对路径 |
| `{{TREND_PATTERN}}` | 趋势形态（上升通道/V型反转/下降通道/横盘震荡） |
| `{{TREND_DESCRIPTION}}` | 趋势描述文案 |
| `{{CURRENT_REVENUE}}` | 当期营收，格式化为千分位 |
| `{{CURRENT_ARPU}}` | 当期 ARPU |
| `{{MOM_REVENUE_CHANGE}}` | 环比营收变化率，如 "+5.2%" 或 "-3.1%" |
| `{{MOM_ARPU_CHANGE}}` | 环比 ARPU 变化率 |
| `{{YOY_REVENUE_CHANGE}}` | 同比营收变化率 |
| `{{YOY_ARPU_CHANGE}}` | 同比 ARPU 变化率 |
| `{{MODULE_*_SHARE}}` | 各模块占比百分比 |
| `{{MODULE_INSIGHT}}` | 模块洞察文案（自动生成） |
| `{{USER_TIER_INSIGHT}}` | 用户分层洞察文案（自动生成） |
| `{{KEEP_TABLE}}` | Keep 子活动列表 |
| `{{OPTIMIZE_TABLE}}` | Optimize 子活动列表 |
| `{{ACTION_ITEMS}}` | 基于诊断结果自动生成行动建议 |

#### 3.2 自动文案生成规则

**Executive Summary 生成逻辑：**
- 如果同比增长 > 20%: "表现强劲，大幅超越同期"
- 如果同比增长 0-20%: "稳健增长，略优于同期"
- 如果同比下降 0-20%: "表现平稳但略低于同期，需关注"
- 如果同比下降 > 20%: "表现不及预期，需深入分析原因"

**趋势形态判断（基于 chart_generator.py 的 compute_metrics 输出）：**
- `上升通道`: 营收持续走高
- `V型反转`: 经历前期下滑后强势反弹
- `下降通道`: 营收呈下滑趋势
- `横盘震荡`: 营收波动较小

**模块洞察 (MODULE_INSIGHT) 生成逻辑：**
- 找到占比最高的模块，指出"XX类是主力营收来源"
- 如果某模块环比增长显著（>10%），指出"XX类表现亮眼"
- 如果某模块占比下降，提出关注建议

**用户分层洞察 (USER_TIER_INSIGHT) 生成逻辑：**
- 对比各层级 ARPU 的同比变化
- 如果超R增长而中R下降，指出"头部用户贡献增强，但需关注中层流失"
- 反之亦然

#### 3.3 诊断表格格式

**严禁使用 Markdown 表格语法**（因为部分 Wiki 平台渲染有兼容性问题）。使用列表格式替代：

```markdown
### 5.1 Keep - 表现优秀，建议保留

- **活动名称A** (外显类) - 营收 $XX,XXX
  - 诊断理由说明文字
- **活动名称B** (小游戏) - 营收 $XX,XXX
  - 诊断理由说明文字

### 5.2 Optimize - 待优化项

- **活动名称C** (养成类) - 营收 $XX,XXX
  - 诊断理由说明文字 + 优化建议
```

#### 3.4 Wiki 平台适配规则

Wiki 编辑器对 Markdown 支持有限，必须严格遵循以下规则：

**可用的格式（已验证能渲染）：**
- `# ` `## ` `### ` 标题
- `> ` 引用块
- `---` 分隔线
- `| col | col |` 管道表格（表头用 `| --- |` 分隔）
- `- ` 无序列表
- `1. ` 有序列表

**严禁使用（不能渲染）：**
1. `**粗体**` — 改用【】括号强调关键数字，如 `【$938,757】`
2. `![alt](url)` 图片语法 — 改用 `> [图表] 请手动插入: xxx.png` 占位
3. 任何 HTML 标签（`<b>`, `<table>`, `<font>` 等）— 会当纯文本显示
4. 任何 Emoji 表情（📊, ✅, ⚠️ 等）— 改用文字标记 `[+]`, `[!]`, `[图表]`, `[洞察]`
5. 深层嵌套列表 — 用 `∟` 符号表示从属关系，或改用表格

**输出方式：直接在聊天框中输出**，用户复制粘贴到 Wiki 编辑器。不写入 .md 文件。

#### 3.0b Notion 版本

读取 `assets/report_template_notion.md` 模板，或使用 `scripts/notion_publisher.py` 的 `generate_notion_content()` 函数自动生成。

#### 3.5 Notion 格式规则

Notion 版本使用 **Notion-flavored Markdown**，与 Wiki 版本的关键差异：

1. **表格** - 使用 Notion 原生 `<table>` 语法（支持 header-row、颜色等属性）
2. **高亮块** - 使用 `<callout icon="⭐" color="yellow_bg">` 包裹 Executive Summary
3. **颜色标记** - 使用 `<span color="red">` / `<span color="blue">` / `<span color="green">` / `<span color="orange">`
4. **Keep/Optimize 标记**:
   - Keep 项: `<span color="green">**活动名**</span>`
   - Optimize 项: `<span color="orange">**活动名**</span>`
5. **正向/负向指标**:
   - 正向（增长）: `<span color="red">**+XX.X%**</span>`
   - 负向（下降）: `<span color="blue">**-XX.X%**</span>`
6. **Action Items** - 使用 `### P0/P1/P2` 子标题分级

---

### Step 4: 发布输出

#### 4.1 Notion 版本发布

使用 Notion MCP 的 `create-pages` 工具将报告发布到 Notion 工作区：

```
工具: Notion MCP create-pages
参数:
  parent: {"page_id": "<数据源页面的父页面ID>"}
  pages: [{
    "properties": {"title": "<generate_notion_title() 的返回值>"},
    "content": "<generate_notion_content() 的返回值>"
  }]
```

**获取 parent_page_id 的方法：**
- 如果是从 Notion 页面读取的数据，使用 `fetch` 返回结果中的 `<ancestor-path>` 中的父页面 URL/ID
- 如果用户指定了目标位置，使用用户提供的页面 ID
- 如果都没有，创建为工作区顶层页面（省略 parent 参数）

#### 4.2 Wiki 版本输出

**直接在聊天框中输出完整报告内容**，不写入 .md 文件。用户从聊天框复制粘贴到 Wiki 编辑器。

输出时不要用代码块包裹，直接作为普通文本输出，这样用户复制后粘贴到 Wiki 编辑器能正确渲染标题、表格、引用等格式。

---

## 交付物

Skill 执行完毕后，向用户返回以下交付物：

### 交付物 1: 图片文件

3 张高清图表，已保存在 `report_images/{event_name}/` 目录：
- `1_Revenue_Trend.png`
- `2_Module_Structure.png`
- `3_User_Growth.png`

告知用户图片保存路径。

### 交付物 2: Notion 页面

已创建到 Notion 工作区的报告页面。告知用户：
- 页面标题
- 页面 URL（从 create-pages 返回值获取）
- 所在位置（父页面名称）

### 交付物 3: Wiki 报告（聊天框直接输出）

**直接在聊天框中输出完整 Wiki 报告**，不写 .md 文件，不用代码块包裹。

用户从聊天框复制后粘贴到 Wiki 编辑器即可正确渲染。报告内容不含任何 `**粗体**`、HTML 标签、Emoji 表情，仅使用标题/表格/引用/列表/【】括号等 Wiki 编辑器可渲染的格式。

### 交付物 4（仅 Excel 模式）: Excel 模板文件

当使用途径 C 时，额外交付 `.xlsx` 模板文件，包含 5 个 Sheet（Meta、核心大盘趋势、模块营收趋势、用户分层ARPU、子活动明细），每个 Sheet 带表头说明、字段提示和示例数据。告知用户文件路径。

---

## 依赖

- Python 3.9+
- matplotlib
- numpy
- openpyxl（Excel 模板模式需要）

如果运行环境缺少依赖，先执行：
```bash
pip install matplotlib numpy openpyxl
```

或使用 requirements.txt：
```bash
pip install -r skills/generate_event_review/scripts/requirements.txt
```

---

## 示例

**示例 A: 从 Notion 读取数据**

用户输入：
> "帮我根据 Notion 中的圣诞节数据生成复盘报告"

Agent 执行流程：
1. Notion MCP search 搜索"圣诞节" -> fetch 获取页面内容 -> 解析表格数据 -> 转换为标准 JSON
2. 保存为 JSON -> 调用 chart_generator.py -> 生成 3 张图表
3. 调用 notion_publisher.py 生成双版本内容
4. Notion MCP create-pages 发布 Notion 版本 + 输出 Wiki 版本

**示例 B: 用户直接提供数据**

用户输入：
> "帮我生成 2026 春节的复盘报告，以下是数据..."
> (附带 JSON 或表格数据)

Agent 执行流程：
1. 解析数据 -> 校验完整性
2. 保存为 JSON -> 调用 chart_generator.py -> 生成 3 张图表
3. 调用 notion_publisher.py 生成双版本内容
4. 发布 Notion 版本 + 输出 Wiki 版本

**示例 C: Excel 模板输入**

用户输入：
> "生成一个 Excel 模板，我填好了再给你"

Agent 执行流程：
1. 调用 `excel_handler.generate_template()` 生成空白模板 -> 告知用户路径
2. （等待用户填写并确认）
3. 调用 `excel_handler.parse_excel()` 解析填好的 Excel -> 校验通过后保存为 JSON
4. 调用 chart_generator.py -> 生成 3 张图表
5. 调用 notion_publisher.py 生成双版本内容
6. 发布 Notion 版本 + 输出 Wiki 版本

最终返回（三种示例均适用）：
- 3 张图表存储路径
- Notion 页面链接
- 聊天框直接输出 Wiki 报告（用户复制粘贴到 Wiki 编辑器）
