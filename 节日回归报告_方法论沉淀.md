# 节日回归报告 — 方法论沉淀

> 产出时间：2026-04  
> 对标报告：科技节 (03-13 ~ 04-03) vs 情人节 基准  
> 数据覆盖：近 7 期节日（万圣节 → 科技节，含 2 月独立周期）

---

## 一、报告产出清单

| 产出 | 路径 | 说明 |
|------|------|------|
| **最终报告** | `_tech_fest_report.html` | 交付物，含 11 个 Section |
| **合并规则** | `_tmp_merge_rules_v6.json` | 子活动合并规则（v6 最终版） |
| **排除名单** | `_tmp_kvk_exclude.json` | KVK 等错误数据排除列表 |
| **子活动数据** | `_tmp_subact_export_v4.json` | 7 期 × 57 个子活动的完整数据 |
| **趋势数据** | `_tmp_trend_data.json` | 增长/衰减趋势分析结果 |
| **历史模块数据** | `_tmp_hist_v4.json` | 7 期模块级汇总数据 |
| **整体 KPI** | `_tmp_hist_kpi_full.json` | 6 期整体营收/活跃/R 级数据 |
| **2 月独立周期** | `_tmp_feb_standalone.json` / `_tmp_feb_total_rev.json` | 拆分出的独立周期数据 |

---

## 二、完整流程（5 个阶段）

### 阶段 1：节日日期确定

**问题**：人工指定的节日日期范围不一定准确，会导致收入错算  
**方法**：用节日礼包的购买覆盖日期来实证确定日期范围

```sql
-- 探测某个节日礼包的实际购买日期分布
SELECT date(date_add('hour',-8, created_at)) AS buy_date,
       COUNT(*) AS orders,
       CAST(SUM(pay_price) AS DECIMAL(18,2)) AS revenue
FROM v1041.ods_user_order
WHERE iap_id IN (SELECT iap_id FROM v1041.dim_iap WHERE iap_type = '混合-节日活动')
  AND partition_date BETWEEN '2025-10-01' AND '2026-04-10'
  AND pay_status = 1
GROUP BY 1 ORDER BY 1
```

**关键决策记录**：
- 春节原始范围 01-13 ~ 02-08 → 拆分为 **春节(纯) 01-13 ~ 02-01** + **2 月独立周期 02-02 ~ 02-08**
- 原因：一番赏和推币机在 02-02 ~ 02-08 有独立上线周期，混入春节会干扰春节模块的纵向对比
- 2 月独立周期通过逐日收入查询确认了精确的 7 天窗口

### 阶段 2：数据查询

核心脚本和 SQL 模板：

**① 整体 KPI 查询** (`_tmp_hist_kpi_full.py`)
- 各节日全品类总营收、付费人数、付费率、ARPPU、ARPU
- 各节日 R 级（超R/大R/中R/小R）ARPU
- 活跃用户数来源表：`v1041.dl_active_user_d`（不是 `dws_user_daily_account`，后者不存在）

```sql
-- 核心查询模板：节日营收
SELECT COUNT(DISTINCT user_id) AS pay_users,
       CAST(SUM(pay_price) AS DECIMAL(18,2)) AS revenue
FROM v1041.ods_user_order
WHERE partition_date BETWEEN '{start_m1}' AND '{end}'
  AND date(date_add('hour',-8,created_at)) BETWEEN date '{start}' AND date '{end}'
  AND pay_status = 1
  AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
```

```sql
-- 活跃用户查询模板
SELECT COUNT(DISTINCT user_id) AS active_users
FROM v1041.dl_active_user_d
WHERE partition_date BETWEEN '{start}' AND '{end}'
  AND user_id NOT IN (SELECT user_id FROM v1041.dl_test_user WHERE 1=1)
```

**② 模块 & 礼包明细查询** (`_tmp_rebuild_7periods.py`)
- 按 `iap_type2` 分类到 4 大模块：节日特惠 / 节日皮肤 / 节日BP / 挖矿小游戏
- 分组粒度：`iap_id_name`（礼包名称）
- 过滤条件：`iap_type = '混合-节日活动'`

```python
TYPE2_MODULE = {
    "混合-节日活动-节日特惠":   "节日特惠",
    "混合-节日活动-节日皮肤":   "节日皮肤",
    "混合-节日活动-节日BP":     "节日BP",
    "混合-节日活动-挖矿小游戏": "挖矿小游戏",
}
```

**③ R 级付费查询**
- 通过 `JOIN v1041.dim_user` 的 `rlevel` 字段关联
- R 级在节日开始日前一天的快照为准

### 阶段 3：子活动合并

**核心原则**（用户确认）：**清晰精准的定位单个模块**  
每个合并组应代表一个独立的游戏玩法/功能模块，方便横向对比。

**合并规则 v6 完整内容**（`_tmp_merge_rules_v6.json`）：

| 合并组 | 包含的礼包数 | 逻辑说明 |
|--------|-------------|----------|
| 大富翁（非异族） | 4 | 常规大富翁及其组队礼包 |
| 异族大富翁 | 5 | 异族大富翁全系列（体验卡/每日/随机/存钱罐） |
| 弹珠 GACHA | 3 | 每个节日算一套 |
| 推币机系列 | 2 | 推币机 + 随机 GACHA |
| 各节日皮肤 GACHA | 每节日 3 个 | 含随机 GACHA + 普通 GACHA + 每日礼包，按节日分组 |
| 节日通行证 | 多个 | 高级 + 初级 + 集结系列，全部归为一个模块 |
| 节日 BP | 多个 | 节日 BP 系列 |
| 挖矿小游戏 | 多个 | 挖矿相关（不含挖孔） |
| 砍价系列 | 2 | 砍价礼包（已移除与挖矿重叠的项） |
| 一番赏 | 2 | 一番赏 + 一番赏随机 GACHA |
| 钓鱼系列 | 2 | 钓鱼礼包 + 钓鱼随机 |
| 强消耗 | 多个 | 强消耗系列 |
| 累充服务器 | 多个 | 累充服务器 |
| 自选周卡 | 多个 | 自选周卡（含不同主题的变体） |
| 周年庆返场 | 多个 | 周年庆返场系列 |

**关键决策**：
- ❌ 挖孔 ≠ 挖矿：两个独立模块，分开统计
- ❌ 黑五系列不合并：内部活动形式各不相同，分开更有意义
- ✅ 集结系列 → 归入通行证：同一付费入口
- ✅ KVK 数据排除：属于错误数据，不参与分析
- ✅ 每日礼包 + GACHA 礼包合并：同属皮肤 GACHA 的子组件

**排除列表**（`_tmp_kvk_exclude.json`）：
- `kvk基因高级bp通行证`
- `kvk基因高级bp通行证-V81-kvk5`
- `kvk基因bp通行证`

**重叠处理**：
- `节日挖矿-砍价礼包-折扣5` 同时出现在"挖矿小游戏"和"砍价系列"→ 只保留在"挖矿小游戏"

### 阶段 4：HTML 报告生成

报告共 11 个 Section：

| # | Section | 内容 |
|---|---------|------|
| 1 | 概览 KPI | 科技节 vs 情人节核心指标对比 |
| 2 | 近期节日横向对比 | 7 期节日总营收/礼包营收/活跃/付费率/ARPPU/ARPU |
| 3 | ARPU 趋势迷你图 | 各 R 级 ARPU 横向折线 |
| 4 | 模块占比 | 4 大模块收入占比对比（甜甜圈图） |
| 5 | 礼包效率排行 | 按 ARPU 排序的完整礼包列表 |
| 6 | 分档分析 | 高/中/低效率分档 |
| 7 | 科技节特色 | 新增/改进/消失的模块 |
| 8 | 模块趋势 | 7 期 4 大模块堆叠柱状图 |
| 9 | 子活动横向对比 | 57 个子活动 × 7 期完整收入矩阵 |
| **10** | **子活动趋势分析** ← 新增 | 增长/衰减气泡图 + sparkline + 影响力排序 |
| 11 | 活动诊断 | Keep/Watch/Kill 建议 |
| 12 | Action Items | 可执行的优化建议 |

### 阶段 5：趋势分析

**算法**：线性回归（`_tmp_gen_trend_chart.py`）

```python
def linear_trend(points):
    """线性回归 → slope（每期变化绝对值）和 R²（趋势稳定性）"""
    # 标准化变化率 = slope / avg_rev
    # 影响力 = avg_rev × |标准化变化率|
```

**排序逻辑**：
1. **影响力 = 期均收入 × |标准化斜率|**
2. 基础收入高 + 变动大 → 高影响力 → 优先展示
3. 基础收入低 → 低影响力 → 后置
4. R² 作为辅助指标衡量趋势的确定性

**可视化**：
- 气泡散点图：X = 变化率, Y = 期均收入, 大小 = 影响力, 颜色 = 增长/衰减
- Sparkline 趋势线（SVG 内联）
- 自动洞察生成（最强增长/最大衰减/稳定增长/潜力新星）

---

## 三、数据管线依赖

```
v1041.ods_user_order      ← 订单明细（pay_status=1）
v1041.dim_iap             ← 礼包元数据（iap_type, iap_type2, iap_id_name）
v1041.dl_test_user        ← 测试号排除
v1041.dl_active_user_d    ← 日活跃用户
v1041.dim_user            ← 用户维度（含 rlevel）
```

API 入口：`datain-api.tap4fun.com/public_api`（Trino SQL 执行）  
调用工具：`_datain_api.py`（位于 `.agents/skills/ai-to-sql/scripts/`）

---

## 四、踩过的坑

| 问题 | 原因 | 解法 |
|------|------|------|
| 挖孔小游戏 2 月收入偏低 | 节日日期范围不准，春节窗口未覆盖 2 月 | 用礼包购买覆盖日期实证探测 |
| 活跃用户查询报错 | 使用了不存在的 `dws_user_daily_account` 表 | 改用 `dl_active_user_d` |
| 子活动收入与内部报告不符 | 内部报告用了 `control_id` + `schema` 过滤 | 改为用 `iap_type = '混合-节日活动'` 全量统计 |
| 增长率被 0 值扭曲 | 简单 (last-first)/first 计算遇到中间 $0 爆炸 | 改用线性回归斜率 |
| 挖矿/砍价 重叠 | 一个礼包同时出现在两个合并组 | 手工指定唯一归属（挖矿优先） |
| 弹珠/通行证/异族大富翁 未完全合并 | 合并规则遗漏了部分变体名称 | 逐轮 review 补齐 |

---

## 五、复用指南

### 下一个节日出报告时的步骤

1. **更新节日列表**：修改 `_tmp_rebuild_7periods.py` 中的 `FESTIVALS`，加入新节日、移除最早的
2. **运行数据查询**：
   ```bash
   python _tmp_hist_kpi_full.py     # 整体 KPI
   python _tmp_rebuild_7periods.py  # 模块 & 礼包明细
   ```
3. **检查合并规则**：新增礼包名称可能需要加入 `_tmp_merge_rules_v6.json`
4. **生成子活动表**：`python _tmp_gen_subact_v4.py`
5. **生成趋势图**：`python _tmp_gen_trend_chart.py`
6. **组装报告**：复制 `_tech_fest_report.html` 为新模板，替换 Section 数据

### 如果要做成自动化 Skill

建议路径：`.cursor/skills/festival-regression-report/`

```
SKILL.md           ← 触发词 + 入口
scripts/
  query_kpi.py     ← 阶段 2-①
  query_packs.py   ← 阶段 2-②
  merge_rules.json ← 阶段 3
  gen_subact.py    ← 阶段 4
  gen_trend.py     ← 阶段 5
  gen_report.py    ← HTML 组装
templates/
  report.html      ← HTML 模板
```

---

## 六、7 期节日配置（可直接复用）

```python
FESTIVALS = [
    {"name": "万圣节",      "start": "2025-10-17", "end": "2025-11-06"},
    {"name": "感恩节",      "start": "2025-11-13", "end": "2025-12-04"},
    {"name": "圣诞节",      "start": "2025-12-12", "end": "2026-01-01"},
    {"name": "春节",        "start": "2026-01-13", "end": "2026-02-01"},
    {"name": "2月独立周期",  "start": "2026-02-02", "end": "2026-02-08"},
    {"name": "情人节",      "start": "2026-02-11", "end": "2026-03-05"},
    {"name": "科技节",      "start": "2026-03-13", "end": "2026-04-03"},
]
```
