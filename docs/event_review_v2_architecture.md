# 活动复盘报告 V2 - 项目架构方案

> 本文档为下一个 Agent 编码的技术规范。请严格按照本文档的目录结构、数据 Schema、模块接口、图表规格进行实现。

---

## 1. 需求概述

### 1.1 与 V1 的核心差异

| 维度 | V1（现有） | V2（新需求） |
|------|-----------|-------------|
| 输入数据 | 6 类（Meta/大盘趋势/模块趋势/用户分层/子活动/模块分类） | 7 类（触达转化/行为/付费整体/R级/付费转化/核心奖励/礼包） |
| 输出图表 | 3 张（营收趋势/模块堆叠/用户分层柱状） | 7 张（漏斗/行为/付费整体/R级/转化对比/预期对比/礼包对比） |
| 分析深度 | 指标计算 + 趋势判断 | AI 分析（异常检测/区间自动划分/活动定位/合理性评估） |
| 输出报告 | Notion + Wiki 双版本 | Notion + Wiki 双版本（保留） |

### 1.2 七大输入数据

| # | 数据名称 | 说明 |
|---|---------|------|
| 1 | 玩家触达转化数据 | 全量触达漏斗：展示→点击→进入→参与，各阶段人数/转化率 |
| 2 | 玩家行为数据 | 活动期间 DAU、参与率、关键行为次数、日均时长等 |
| 3 | 付费整体数据 | 付费总额/付费率/ARPU/ARPPU，含同比+环比，至少6个月 |
| 4 | R级付费数据 | 按 R 级拆分的付费总额/付费率/ARPU/ARPPU，至少6个月 |
| 5 | 付费转化数据 | 各价位档位的购买人数/购买次数，AI 自动划分价位区间 |
| 6 | 核心奖励数据 | 关键奖励的预期产出 vs 实际产出 |
| 7 | 商业化礼包数据 | 每个礼包的付费总额/付费人数/价格 |

### 1.3 七大输出分析

| # | 分析内容 | 配套图表 |
|---|---------|---------|
| 1 | 触达是否有问题 | 触达漏斗图 |
| 2 | 行为数据是否有异常 | 行为数据图（多维对比） |
| 3 | 付费整体数据效果评估 | 付费整体趋势图（多指标+同比环比） |
| 4 | 各R级付费效果评估 + 活动定位分析 | R级付费对比图 |
| 5 | 活动转化对比 + 异常检测 | 转化对比图 |
| 6 | 数值设计是否符合预期 | （嵌入报告表格，可选附图） |
| 7 | 礼包设计合理性 | 礼包付费对比图 |

---

## 2. 项目目录结构

```
skills/generate_event_review_v2/
├── SKILL.md                              # Skill 入口指令文档
├── schema/
│   ├── input_schema.json                 # 完整的 JSON Schema 定义（7 大数据块）
│   └── example_data.json                 # 示例数据（可直接运行测试）
├── scripts/
│   ├── requirements.txt                  # Python 依赖
│   ├── __init__.py
│   ├── data_validator.py                 # 数据校验模块
│   ├── excel_handler.py                  # Excel 模板生成 & 解析
│   ├── analyzers/                        # 分析引擎（7 个分析器）
│   │   ├── __init__.py
│   │   ├── base_analyzer.py              # 分析器基类
│   │   ├── reach_analyzer.py             # 分析器1: 触达转化分析
│   │   ├── behavior_analyzer.py          # 分析器2: 行为数据分析
│   │   ├── payment_overview_analyzer.py  # 分析器3: 付费整体分析
│   │   ├── r_tier_analyzer.py            # 分析器4: R级付费分析
│   │   ├── conversion_analyzer.py        # 分析器5: 付费转化分析
│   │   ├── reward_analyzer.py            # 分析器6: 核心奖励分析
│   │   └── package_analyzer.py           # 分析器7: 礼包分析
│   ├── charts/                           # 图表生成器（7 个图表）
│   │   ├── __init__.py
│   │   ├── base_chart.py                 # 图表基类（字体/样式/DPI统一配置）
│   │   ├── chart_reach_funnel.py         # 图表1: 触达漏斗图
│   │   ├── chart_behavior.py             # 图表2: 行为数据图
│   │   ├── chart_payment_overview.py     # 图表3: 付费整体趋势图
│   │   ├── chart_r_tier.py               # 图表4: R级付费对比图
│   │   ├── chart_conversion.py           # 图表5: 转化对比图
│   │   ├── chart_reward.py               # 图表6: 预期vs实际对比图（可选）
│   │   └── chart_package.py              # 图表7: 礼包付费对比图
│   ├── report_generator.py               # 报告组装（Notion + Wiki 双版本）
│   └── main.py                           # 主入口：编排整个流程
└── assets/
    ├── report_template_wiki.md           # Wiki 报告模板
    └── report_template_notion.md         # Notion 报告模板
```

---

## 3. 数据 Schema 设计

### 3.1 顶层结构

```json
{
  "meta": { ... },
  "reach_conversion": { ... },
  "behavior_data": { ... },
  "payment_overview": { ... },
  "r_tier_payment": { ... },
  "payment_conversion": { ... },
  "core_reward": { ... },
  "gift_packages": { ... }
}
```

### 3.2 各数据块详细定义

#### 3.2.1 meta — 基础信息

```json
{
  "meta": {
    "event_name": "2026春节活动",
    "event_type": "节日活动",
    "event_start_date": "2026-01-25",
    "event_end_date": "2026-02-08",
    "change_description": "本期新增了XX玩法，调整了YY概率",
    "benchmark_event": "2025春节活动"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| event_name | string | 是 | 当期活动名称 |
| event_type | string | 否 | 活动类型（节日/周年/联动等） |
| event_start_date | string | 否 | 活动开始日期 ISO |
| event_end_date | string | 否 | 活动结束日期 ISO |
| change_description | string | 是 | 本期改动内容简述 |
| benchmark_event | string | 否 | 对标活动名称 |

#### 3.2.2 reach_conversion — 触达转化数据

```json
{
  "reach_conversion": {
    "stages": [
      {"stage": "推送触达", "users": 1000000, "note": "全服推送"},
      {"stage": "弹窗展示", "users": 800000, "note": ""},
      {"stage": "点击进入", "users": 350000, "note": ""},
      {"stage": "活动参与", "users": 200000, "note": "至少完成1次任务"},
      {"stage": "付费转化", "users": 50000, "note": "产生付费行为"}
    ],
    "comparison": {
      "benchmark_event": "2025春节活动",
      "stages": [
        {"stage": "推送触达", "users": 950000},
        {"stage": "弹窗展示", "users": 750000},
        {"stage": "点击进入", "users": 300000},
        {"stage": "活动参与", "users": 180000},
        {"stage": "付费转化", "users": 42000}
      ]
    }
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| stages | array | 是 | 当期漏斗各阶段，至少3层 |
| stages[].stage | string | 是 | 阶段名称 |
| stages[].users | number | 是 | 该阶段人数 |
| stages[].note | string | 否 | 备注 |
| comparison | object | 否 | 对比数据（历史活动） |

#### 3.2.3 behavior_data — 行为数据

```json
{
  "behavior_data": {
    "metrics": [
      {
        "metric_name": "日均DAU",
        "current_value": 500000,
        "benchmark_value": 480000,
        "unit": "人"
      },
      {
        "metric_name": "活动参与率",
        "current_value": 45.2,
        "benchmark_value": 42.0,
        "unit": "%"
      },
      {
        "metric_name": "人均参与次数",
        "current_value": 8.5,
        "benchmark_value": 7.2,
        "unit": "次"
      },
      {
        "metric_name": "平均参与时长",
        "current_value": 25.3,
        "benchmark_value": 22.1,
        "unit": "分钟"
      }
    ],
    "daily_trend": [
      {"date": "2026-01-25", "dau": 520000, "participate_rate": 46.1, "avg_actions": 9.0},
      {"date": "2026-01-26", "dau": 510000, "participate_rate": 45.5, "avg_actions": 8.8}
    ]
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| metrics | array | 是 | 核心行为指标列表 |
| metrics[].metric_name | string | 是 | 指标名称 |
| metrics[].current_value | number | 是 | 当期值 |
| metrics[].benchmark_value | number | 否 | 对标值 |
| metrics[].unit | string | 是 | 单位 |
| daily_trend | array | 否 | 日维度趋势（如提供，可生成日趋势图） |

#### 3.2.4 payment_overview — 付费整体数据

```json
{
  "payment_overview": {
    "time_series": [
      {
        "event": "2025-08活动",
        "revenue": 850000,
        "pay_rate": 11.2,
        "arpu": 45.6,
        "arppu": 120.3
      },
      {
        "event": "2025-09活动",
        "revenue": 920000,
        "pay_rate": 12.0,
        "arpu": 48.2,
        "arppu": 125.8
      }
    ],
    "yoy_benchmark": {
      "event": "2025春节活动",
      "revenue": 800000,
      "pay_rate": 10.5,
      "arpu": 42.0,
      "arppu": 115.0
    }
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| time_series | array | 是 | 至少6个月的付费数据序列，按时间升序，最后一条为当期 |
| time_series[].event | string | 是 | 活动/月份名称 |
| time_series[].revenue | number | 是 | 付费总额 |
| time_series[].pay_rate | number | 是 | 付费率（%） |
| time_series[].arpu | number | 是 | ARPU |
| time_series[].arppu | number | 是 | ARPPU |
| yoy_benchmark | object | 否 | 去年同期数据（用于同比计算） |

#### 3.2.5 r_tier_payment — R级付费数据

```json
{
  "r_tier_payment": {
    "tiers": ["超R", "大R", "中R", "小R", "非R"],
    "time_series": [
      {
        "event": "2025-08活动",
        "data": {
          "超R": {"revenue": 300000, "pay_rate": 95.0, "arpu": 5000, "arppu": 5263},
          "大R": {"revenue": 250000, "pay_rate": 80.0, "arpu": 1200, "arppu": 1500},
          "中R": {"revenue": 180000, "pay_rate": 55.0, "arpu": 300, "arppu": 545},
          "小R": {"revenue": 80000, "pay_rate": 25.0, "arpu": 50, "arppu": 200},
          "非R": {"revenue": 40000, "pay_rate": 5.0, "arpu": 5, "arppu": 100}
        }
      }
    ]
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tiers | array | 是 | R级名称列表 |
| time_series | array | 是 | 至少6个月的时序数据 |
| time_series[].event | string | 是 | 活动名 |
| time_series[].data | object | 是 | 每个R级的 revenue/pay_rate/arpu/arppu |

#### 3.2.6 payment_conversion — 付费转化数据

```json
{
  "payment_conversion": {
    "current": {
      "event": "2026春节活动",
      "price_tiers": [
        {"price": 6, "purchases": 50000, "payers": 45000},
        {"price": 30, "purchases": 30000, "payers": 22000},
        {"price": 68, "purchases": 18000, "payers": 12000},
        {"price": 128, "purchases": 8000, "payers": 5000},
        {"price": 328, "purchases": 3000, "payers": 1800},
        {"price": 648, "purchases": 1500, "payers": 900},
        {"price": 1288, "purchases": 500, "payers": 300},
        {"price": 3288, "purchases": 100, "payers": 60}
      ]
    },
    "comparison": {
      "event": "2025春节活动",
      "price_tiers": [
        {"price": 6, "purchases": 48000, "payers": 43000},
        {"price": 30, "purchases": 28000, "payers": 20000},
        {"price": 68, "purchases": 16000, "payers": 11000},
        {"price": 128, "purchases": 7500, "payers": 4500},
        {"price": 328, "purchases": 2800, "payers": 1600},
        {"price": 648, "purchases": 1200, "payers": 700}
      ]
    }
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| current | object | 是 | 当期数据 |
| current.price_tiers | array | 是 | 各价位的购买笔数(purchases)和购买人数(payers) |
| current.price_tiers[].price | number | 是 | 价位（元） |
| comparison | object | 否 | 对比活动数据 |

**AI 区间划分逻辑说明**：分析器需要根据 `price_tiers` 的分布自动判断合适的价位区间分组（如 0-30, 30-128, 128-648, 648+），分组策略如下：
1. 对价位列表按升序排列
2. 计算相邻价位之间购买人数的下降幅度（衰减率）
3. 在衰减率出现明显断层（>40%）处划分区间边界
4. 兜底策略：如果无法检测到断层，按 对数等距 方式分为 3~5 组
5. 输出分组标签（如 "低额(≤30)", "中额(30-128)", "高额(128-648)", "超高额(>648)"）

#### 3.2.7 core_reward — 核心奖励数据

```json
{
  "core_reward": {
    "items": [
      {
        "reward_name": "SSR角色碎片",
        "expected_value": 100,
        "actual_value": 95,
        "unit": "个",
        "expected_cost": 3280,
        "actual_cost": 3450,
        "cost_unit": "元"
      },
      {
        "reward_name": "限定皮肤",
        "expected_value": 1,
        "actual_value": 1,
        "unit": "件",
        "expected_cost": 648,
        "actual_cost": 680,
        "cost_unit": "元"
      }
    ]
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| items | array | 是 | 核心奖励列表 |
| items[].reward_name | string | 是 | 奖励名称 |
| items[].expected_value | number | 是 | 预期产出数量 |
| items[].actual_value | number | 是 | 实际产出数量 |
| items[].unit | string | 是 | 产出单位 |
| items[].expected_cost | number | 否 | 预期获取成本 |
| items[].actual_cost | number | 否 | 实际获取成本 |
| items[].cost_unit | string | 否 | 成本单位 |

#### 3.2.8 gift_packages — 商业化礼包数据

```json
{
  "gift_packages": {
    "packages": [
      {
        "package_name": "新春超值礼包",
        "price": 128,
        "revenue": 640000,
        "payers": 5000,
        "description": "含SSR碎片x10+金币x100000"
      },
      {
        "package_name": "每日特惠礼包",
        "price": 6,
        "revenue": 300000,
        "payers": 50000,
        "description": "含体力x120+抽奖券x5"
      }
    ],
    "comparison_packages": [
      {
        "package_name": "去年同款超值礼包",
        "price": 128,
        "revenue": 580000,
        "payers": 4500
      }
    ]
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| packages | array | 是 | 当期所有商业化礼包 |
| packages[].package_name | string | 是 | 礼包名称 |
| packages[].price | number | 是 | 礼包价格 |
| packages[].revenue | number | 是 | 付费总额 |
| packages[].payers | number | 是 | 付费人数 |
| packages[].description | string | 否 | 礼包内容描述 |
| comparison_packages | array | 否 | 对标活动礼包（用于对比） |

---

## 4. 模块设计

### 4.1 数据校验模块 — `data_validator.py`

```python
def validate_input(data: dict) -> dict:
    """
    校验输入数据完整性和合法性。
    
    校验规则：
    1. meta 必填字段检查
    2. reach_conversion.stages 至少 3 层
    3. payment_overview.time_series 至少 6 条
    4. r_tier_payment.time_series 至少 6 条
    5. payment_conversion.current.price_tiers 至少 3 条
    6. core_reward.items 至少 1 条
    7. gift_packages.packages 至少 1 条
    8. 数值合法性（revenue >= 0, pay_rate 0~100, users >= 0 等）
    
    Returns:
        {"valid": True} 或 {"valid": False, "errors": ["错误描述1", ...]}
    """
```

### 4.2 Excel 处理模块 — `excel_handler.py`

沿用 V1 的设计模式，但 Sheet 结构调整为 8 个：

| Sheet | 名称 | 对应数据块 |
|-------|------|-----------|
| 1 | Meta | meta |
| 2 | 触达转化 | reach_conversion |
| 3 | 行为数据 | behavior_data |
| 4 | 付费整体趋势 | payment_overview |
| 5 | R级付费数据 | r_tier_payment |
| 6 | 付费转化 | payment_conversion |
| 7 | 核心奖励 | core_reward |
| 8 | 商业化礼包 | gift_packages |

每个 Sheet 保持 V1 的模式：第1行表头、第2行字段说明、第3行起示例数据。使用 openpyxl 设置样式和数据验证。

接口设计：

```python
def generate_template(output_path: str) -> str:
    """生成空白 Excel 模板，返回文件路径"""

def parse_excel(excel_path: str) -> dict:
    """解析填好的 Excel，返回标准 JSON 结构"""

def save_as_json(data: dict, output_path: str) -> str:
    """保存数据为 JSON 文件，返回文件路径"""
```

### 4.3 分析引擎 — `analyzers/`

#### 4.3.1 分析器基类 — `base_analyzer.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AnalysisResult:
    """分析结果标准结构"""
    module_name: str           # 模块名称（如 "触达分析"）
    conclusion: str            # 核心结论（1-2 句话）
    severity: str              # 严重程度: "正常" / "关注" / "异常" / "严重"
    details: List[str]         # 详细分析要点（列表）
    suggestions: List[str]     # 改进建议（列表）
    chart_data: Optional[dict] # 传递给图表生成器的数据（已处理）
    raw_metrics: dict          # 计算出的原始指标

class BaseAnalyzer(ABC):
    """分析器基类"""
    
    @abstractmethod
    def analyze(self, data: dict) -> AnalysisResult:
        """执行分析，返回标准化结果"""
        pass
    
    def _calc_change_rate(self, current, previous) -> float:
        """计算变化率"""
        if previous == 0:
            return 0.0
        return round((current - previous) / previous * 100, 2)
    
    def _detect_anomaly(self, values: list, threshold: float = 2.0) -> List[int]:
        """基于 Z-score 的异常检测，返回异常索引"""
        pass
```

#### 4.3.2 分析器1: 触达转化分析 — `reach_analyzer.py`

```python
class ReachAnalyzer(BaseAnalyzer):
    """
    分析逻辑：
    1. 计算各阶段转化率（stage N+1 / stage N）
    2. 如有 comparison，对比各阶段转化率变化
    3. 找到转化率最低的环节（瓶颈点）
    4. 判断是否存在异常流失（某环节转化率 < 30% 或相比对标下降 > 15%）
    
    输出：
    - conclusion: "触达通路正常" / "XX环节存在显著流失"
    - chart_data: 漏斗图所需数据
    """
```

#### 4.3.3 分析器2: 行为数据分析 — `behavior_analyzer.py`

```python
class BehaviorAnalyzer(BaseAnalyzer):
    """
    分析逻辑：
    1. 对比各行为指标的当期 vs 对标值
    2. 检测日趋势中的异常点（如某天 DAU 骤降）
    3. 判断参与率/时长是否在合理区间
    4. 如果参与率高但付费转化低，标记为"行为-付费脱节"
    
    输出：
    - conclusion: "行为数据正常/存在XX异常"
    - chart_data: 行为对比图所需数据
    """
```

#### 4.3.4 分析器3: 付费整体分析 — `payment_overview_analyzer.py`

```python
class PaymentOverviewAnalyzer(BaseAnalyzer):
    """
    分析逻辑：
    1. 计算环比变化（time_series 最后一条 vs 倒数第二条）
    2. 计算同比变化（当期 vs yoy_benchmark）
    3. 趋势形态判断（上升/V型/下降/震荡），基于最近6期数据的拟合
    4. 四大指标（revenue/pay_rate/arpu/arppu）各自评估
    5. 综合评估：效果"超预期"/"符合预期"/"低于预期"
    
    输出：
    - conclusion: 整体效果评估
    - raw_metrics: {yoy_changes, mom_changes, trend_pattern}
    - chart_data: 趋势图所需数据
    """
```

#### 4.3.5 分析器4: R级付费分析 — `r_tier_analyzer.py`

```python
class RTierAnalyzer(BaseAnalyzer):
    """
    分析逻辑：
    1. 各R级 revenue/pay_rate/arpu/arppu 的环比、同比变化
    2. 各R级占总营收比例，分析付费结构是否健康
    3. 活动定位判断：
       - 如果超R贡献占比 > 50%: "高R向活动"
       - 如果中小R付费率提升显著: "普惠型活动"
       - 如果各级均衡增长: "全面提升型活动"
    4. 基于定位评估活动设计是否达到预期目标
    5. 检测R级之间的异常（如大R下降但小R上升等交叉现象）
    
    输出：
    - conclusion: R级分析结论 + 活动定位
    - raw_metrics: {tier_shares, tier_changes, activity_positioning}
    - chart_data: R级对比图数据
    """
```

#### 4.3.6 分析器5: 付费转化分析 — `conversion_analyzer.py`

```python
class ConversionAnalyzer(BaseAnalyzer):
    """
    分析逻辑：
    1. AI 区间自动划分（详见 3.2.6 说明）：
       a. 按 price 升序排列
       b. 计算相邻档位 payers 衰减率
       c. 在衰减率断层处划分区间
       d. 兜底：对数等距分 3~5 组
    2. 每个区间统计：总购买笔数、总购买人数、区间营收贡献
    3. 与 comparison 对比：各区间的变化率
    4. 检测异常：某区间人数异常增减（>30%）
    5. 转化漏斗分析：从低额到高额的流失情况
    
    输出：
    - conclusion: 转化效率评估
    - raw_metrics: {intervals, interval_stats, anomalies}
    - chart_data: 转化对比图数据
    """
```

#### 4.3.7 分析器6: 核心奖励分析 — `reward_analyzer.py`

```python
class RewardAnalyzer(BaseAnalyzer):
    """
    分析逻辑：
    1. 对比每个核心奖励的 expected vs actual
    2. 偏差率计算：(actual - expected) / expected * 100%
    3. 判断标准：
       - 偏差率 < ±10%: "符合预期"
       - 偏差率 ±10%~±30%: "轻微偏差"
       - 偏差率 > ±30%: "显著偏差，需排查"
    4. 如果提供了 cost 数据，评估成本偏差
    5. 综合所有奖励得出数值设计的整体评判
    
    输出：
    - conclusion: "数值设计整体符合预期" / "XX项存在显著偏差"
    - details: 每个奖励的偏差分析
    """
```

#### 4.3.8 分析器7: 礼包分析 — `package_analyzer.py`

```python
class PackageAnalyzer(BaseAnalyzer):
    """
    分析逻辑：
    1. 计算每个礼包的人均消费（revenue / payers）
    2. 按 revenue 排序，找到营收 Top3 礼包
    3. 计算各礼包占总礼包营收的比例
    4. 如有 comparison_packages，计算同类礼包的变化
    5. 合理性评估：
       - 低价礼包是否承担了引流功能（人数占比高）
       - 高价礼包是否承担了营收主力（营收占比高）
       - 是否存在"鸡肋礼包"（人数少+营收低）
    6. 给出调整建议
    
    输出：
    - conclusion: 礼包设计合理性评估
    - suggestions: 调整建议
    - chart_data: 礼包对比图数据
    """
```

### 4.4 图表生成器 — `charts/`

#### 4.4.1 图表基类 — `base_chart.py`

```python
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

class BaseChart:
    """图表基类，统一配置"""
    
    # 全局配置
    DPI = 150
    FIGSIZE_STANDARD = (12, 7)
    FIGSIZE_WIDE = (14, 7)
    FONT_FAMILY = None  # 运行时检测中文字体
    
    # 配色方案
    COLORS = {
        'primary': '#E74C3C',      # 红色（主色）
        'secondary': '#3498DB',    # 蓝色
        'success': '#2ECC71',      # 绿色
        'warning': '#F39C12',      # 橙色
        'info': '#9B59B6',         # 紫色
        'gray': '#95A5A6',         # 灰色
        'tier_colors': {           # R级专用色
            '超R': '#E74C3C',
            '大R': '#F39C12',
            '中R': '#3498DB',
            '小R': '#2ECC71',
            '非R': '#95A5A6'
        }
    }
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self._detect_chinese_font()
    
    def _detect_chinese_font(self):
        """检测可用中文字体（沿用 V1 逻辑）"""
        pass
    
    def save(self, fig, filename: str) -> str:
        """保存图表为 PNG，返回路径"""
        pass
```

#### 4.4.2 图表1: 触达漏斗图 — `chart_reach_funnel.py`

```
图表类型: 水平漏斗图（trapezoid funnel）
布局:
  - 从上到下递减的梯形条
  - 每个梯形右侧标注人数和转化率
  - 如有 comparison，在左侧用虚线标注对标的漏斗边界
配色: 从深色（顶部）到浅色（底部）的渐变
尺寸: 12 x 8 (FIGSIZE_STANDARD偏高)
文件名: 1_Reach_Funnel.png
```

#### 4.4.3 图表2: 行为数据图 — `chart_behavior.py`

```
图表类型: 分组柱状图 + 变化率标注
布局:
  - X轴: 各行为指标名称
  - Y轴: 指标值
  - 每组2根柱子: 当期(红) vs 对标(灰)
  - 柱子顶部标注变化率百分比（绿色=正向，红色=负向）
备选: 如提供 daily_trend，额外生成日趋势折线图
文件名: 2_Behavior_Data.png
```

#### 4.4.4 图表3: 付费整体趋势图 — `chart_payment_overview.py`

```
图表类型: 多Y轴折线图（类似 V1 的 Chart1，但包含4个指标）
布局:
  - 主Y轴(左): 付费总额（柱状图背景 + 折线）
  - 副Y轴(右): ARPU（折线）
  - 第二副轴(右2): 付费率（虚线）
  - X轴: 时间序列活动名
  - 当期数据点用★标注
  - 同比参考线（水平虚线）
  - 数据标注: 环比/同比变化率
配色: revenue(红柱+红线), arpu(蓝线), pay_rate(绿虚线)
文件名: 3_Payment_Overview.png
```

#### 4.4.5 图表4: R级付费对比图 — `chart_r_tier.py`

```
图表类型: 热力图矩阵 或 分组柱状图（根据数据量自动选择）
方案A（≤3个活动对比时）—— 分组柱状图:
  - X轴: R级层级
  - 每组N根柱子（N=活动数）
  - 4个子图: revenue / pay_rate / arpu / arppu
方案B（>3个活动时）—— 热力图:
  - 行: R级层级, 列: 时间序列活动
  - 颜色深浅: 指标值大小
  - 4个子图: 分别展示4个指标
文件名: 4_RTier_Payment.png
```

#### 4.4.6 图表5: 转化对比图 — `chart_conversion.py`

```
图表类型: 双层柱状图 + 区间分组
布局:
  - X轴: AI自动划分的价位区间
  - Y轴(左): 购买人数（柱状图，当期 vs 对标 分组）
  - Y轴(右): 区间营收贡献（折线）
  - 柱子顶部标注变化率
  - 下方子图: 明细散点图（每个价位点的 payers 分布）
配色: 当期(红), 对标(灰)
文件名: 5_Conversion_Compare.png
```

#### 4.4.7 图表6: 预期vs实际对比图 — `chart_reward.py`（可选）

```
图表类型: 偏差对比图（Tornado / Bullet chart）
布局:
  - Y轴: 各奖励名称
  - X轴: 偏差率（%）
  - 水平条形图，预期值为基准线(0%)
  - 实际值的偏差用颜色区分: 绿色(符合), 橙色(轻微), 红色(显著)
  - 如果数据量 < 3 项，改用简洁表格 + 内嵌在报告中
文件名: 6_Reward_Deviation.png（仅在 items ≥ 3 时生成）
```

#### 4.4.8 图表7: 礼包付费对比图 — `chart_package.py`

```
图表类型: 气泡图 或 双维柱状图
方案A —— 气泡图:
  - X轴: 礼包价格
  - Y轴: 付费人数
  - 气泡大小: 营收
  - 颜色: 当期(红) vs 对标(灰)
  - 标签: 礼包名称
方案B —— 双维柱状图:
  - X轴: 礼包名称（按营收降序）
  - Y轴(左): 营收（柱状）
  - Y轴(右): 人数（折线）
  - 如有 comparison，叠加对标数据
文件名: 7_Package_Compare.png
```

### 4.5 报告生成模块 — `report_generator.py`

```python
class ReportGenerator:
    """
    负责将 7 个分析结果组装为完整报告。
    支持 Notion + Wiki 双版本输出。
    """
    
    def __init__(self, data: dict, analysis_results: list[AnalysisResult], chart_dir: str):
        self.data = data
        self.results = {r.module_name: r for r in analysis_results}
        self.chart_dir = chart_dir
    
    def generate_notion_content(self) -> str:
        """
        生成 Notion-flavored Markdown 报告。
        
        报告结构：
        1. Executive Summary（callout 块，总结性评价）
        2. 一、触达分析（结论 + 漏斗图）
        3. 二、行为分析（结论 + 行为图）
        4. 三、付费整体分析（结论 + 趋势图 + 同比环比表格）
        5. 四、R级付费分析（结论 + R级图 + 活动定位评价）
        6. 五、付费转化分析（结论 + 转化图 + 区间明细表）
        7. 六、数值设计评估（结论 + 偏差表格/图）
        8. 七、礼包分析（结论 + 礼包图 + 调整建议）
        9. 综合建议（汇总各模块 suggestions，按 P0/P1/P2 分级）
        """
        pass
    
    def generate_wiki_content(self) -> str:
        """
        生成 Wiki 兼容 Markdown 报告。
        规则同 V1：不用 **粗体**，不用 emoji，不用 HTML，
        用【】强调，用 > [图表] 占位，用管道表格。
        """
        pass
    
    def generate_notion_title(self) -> str:
        """生成 Notion 页面标题"""
        pass
    
    def _generate_executive_summary(self) -> str:
        """
        基于 7 个分析结果生成 Executive Summary。
        规则：
        - 提取各模块 severity，如果有"严重"则总结为"需重点关注"
        - 如果多数为"正常"则总结为"整体表现良好"
        - 列出 Top3 关键发现
        """
        pass
    
    def _aggregate_suggestions(self) -> dict:
        """
        汇总所有模块的 suggestions，按优先级分类：
        - P0 (severity=严重): 必须立即处理
        - P1 (severity=异常): 下期重点优化
        - P2 (severity=关注): 持续观察
        """
        pass
```

### 4.6 主入口 — `main.py`

```python
"""
主入口脚本。编排完整的分析流程。
支持命令行调用和模块化调用两种方式。
"""

import argparse
import json
import os
import sys

def run_analysis(input_data: dict, output_dir: str) -> dict:
    """
    主流程编排函数。
    
    Args:
        input_data: 标准化输入数据（已校验）
        output_dir: 输出目录
    
    Returns:
        {
            "charts": [图表路径列表],
            "analysis_results": [AnalysisResult列表],
            "notion_content": "Notion报告内容",
            "notion_title": "Notion页面标题",
            "wiki_content": "Wiki报告内容"
        }
    
    执行步骤:
    1. data_validator.validate_input(input_data)
    2. 实例化 7 个分析器，逐一调用 analyze()
    3. 实例化 7 个图表生成器，逐一生成图表
    4. 实例化 ReportGenerator，生成双版本报告
    5. 返回完整结果
    """
    pass

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='活动复盘报告生成器 V2')
    parser.add_argument('--input', required=True, help='输入数据 JSON 文件路径')
    parser.add_argument('--output_dir', required=True, help='输出目录')
    parser.add_argument('--format', choices=['all', 'notion', 'wiki'], default='all')
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = run_analysis(data, args.output_dir)
    
    # 保存报告文件
    # ...

if __name__ == '__main__':
    main()
```

---

## 5. 数据流程图

```
┌──────────────────────────────────────────────────────┐
│                    数据输入层                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ Notion   │  │ Excel    │  │ 直接 JSON 输入   │    │
│  │ MCP 读取 │  │ 模板解析 │  │                  │    │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘    │
│       └──────────────┼────────────────┘               │
│                      ▼                                │
│           ┌──────────────────┐                        │
│           │ data_validator   │                        │
│           │ 数据校验         │                        │
│           └────────┬─────────┘                        │
└────────────────────┼─────────────────────────────────┘
                     ▼
┌──────────────────────────────────────────────────────┐
│                    分析引擎层                          │
│  ┌──────────┐ ┌──────────┐ ┌───────────────────────┐ │
│  │ 触达分析 │ │ 行为分析 │ │ 付费整体分析          │ │
│  └────┬─────┘ └────┬─────┘ └───────────┬───────────┘ │
│  ┌────┴─────┐ ┌────┴─────┐ ┌───────────┴───────────┐ │
│  │ R级分析  │ │ 转化分析 │ │ 奖励分析              │ │
│  └────┬─────┘ └────┬─────┘ └───────────┬───────────┘ │
│  ┌────┴──────────────────────────────────────────┐    │
│  │ 礼包分析                                      │    │
│  └────┬──────────────────────────────────────────┘    │
│       ▼                                               │
│  7 x AnalysisResult                                   │
└────────────────────┬─────────────────────────────────┘
                     ▼
┌──────────────────────────────────────────────────────┐
│                    图表生成层                          │
│  chart_1  chart_2  chart_3  chart_4                   │
│  chart_5  chart_6(可选)  chart_7                      │
│  → 输出 6~7 张 PNG (150DPI, 12x7)                     │
└────────────────────┬─────────────────────────────────┘
                     ▼
┌──────────────────────────────────────────────────────┐
│                    报告生成层                          │
│  ┌────────────────────┐  ┌─────────────────────┐      │
│  │ Notion 版本        │  │ Wiki 版本           │      │
│  │ (Notion Markdown)  │  │ (Wiki Markdown)     │      │
│  └────────┬───────────┘  └──────────┬──────────┘      │
│           ▼                         ▼                 │
│  Notion MCP create-pages     聊天框直接输出           │
└──────────────────────────────────────────────────────┘
```

---

## 6. SKILL.md 执行流程概要

供 Agent 调用时的执行流程：

```
Step 1: 数据收集
├── 途径A: Notion MCP search/fetch → 解析表格 → 标准JSON
├── 途径B: 用户直接提供 JSON
└── 途径C: generate_template() → 用户填写 → parse_excel() → 标准JSON

Step 2: 数据校验
└── validate_input() → 通过则继续 / 失败则反馈用户修正

Step 3: 分析 + 图表生成
└── run_analysis() 内部编排:
    ├── 7 个分析器依次执行 → 7 个 AnalysisResult
    └── 6~7 个图表生成器 → 6~7 张 PNG

Step 4: 报告组装
├── generate_notion_content() → Notion 页面内容
└── generate_wiki_content() → Wiki 报告内容

Step 5: 发布输出
├── Notion MCP create-pages 发布
├── Wiki 内容在聊天框输出
└── 告知图表存储路径
```

---

## 7. 依赖与环境

### requirements.txt

```
matplotlib>=3.7.0
numpy>=1.24.0
openpyxl>=3.1.0
scipy>=1.10.0
```

新增 `scipy` 用于统计分析（Z-score 异常检测、趋势拟合等）。

### Python 版本

Python 3.9+

---

## 8. 编码约定

### 8.1 代码规范

- 所有函数/类使用中英文混合 docstring（功能描述用中文，参数/返回值用英文标注类型）
- 错误信息全部用中文输出（方便用户理解）
- 使用 dataclass 定义数据结构
- 类型标注（type hints）完整
- 每个分析器/图表是独立文件，便于单独测试和修改

### 8.2 图表规范

- 所有图表标题使用中文
- 数值格式化：金额千分位分隔，百分比保留1位小数
- 颜色方案统一使用 BaseChart.COLORS
- DPI 统一 150
- 字体检测中文字体，fallback 到 SimHei / Microsoft YaHei / PingFang SC

### 8.3 报告规范

**Notion 版本：**
- 使用 `<callout>` / `<span color="">` / `<table header-row="true">` 等 Notion 语法
- 图表位置用 `<callout icon="📊">请在此处插入图表: X_Name.png</callout>` 占位

**Wiki 版本：**
- 不用 `**粗体**`、HTML、Emoji
- 用 `【】` 强调关键数字
- 用 `> [图表] 请手动插入: X_Name.png` 占位
- 表格使用管道语法 `| col | col |`

---

## 9. 测试策略

### 9.1 example_data.json

提供一套完整的 7 大数据块示例数据（见 Schema 第3节中的示例），确保：
- 所有字段都有值
- 数据量满足最低要求（6个月时序、3层漏斗等）
- 包含正常和异常场景（如某个奖励偏差>30%，某个R级营收下降>20%）

### 9.2 验证方法

```bash
# 1. 生成 Excel 模板
python scripts/main.py --generate-template --output_dir test_output/

# 2. 使用示例数据运行完整流程
python scripts/main.py --input schema/example_data.json --output_dir test_output/

# 3. 检查输出
# - test_output/ 目录下应有 6~7 张 PNG
# - 控制台输出 Notion content + Wiki content
```

---

## 10. 与 V1 的兼容性

- V2 为**独立项目**，放在 `skills/generate_event_review_v2/` 目录
- V1 保留不动（`skills/generate_event_review/`）
- V2 的 SKILL.md 入口文件放在 `.cursor/skills/generate-event-review-v2/SKILL.md`
- 两者可以共存，通过不同的 skill 名称触发
