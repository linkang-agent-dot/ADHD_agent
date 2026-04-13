# 节日整体 Review 一键生成链路

## 概述

给我**节日时间范围** + **节日ID（control_id）**，我自动完成所有数据查询和报告生成。

---

## 需要你提供的信息

| 信息 | 示例 | 说明 |
|------|------|------|
| 节日开始日期 | `2026-03-13` | 含当天 |
| 节日结束日期 | `2026-04-03` | 含当天 |
| 节日 control_id | `%2112%` | 模糊匹配，对应当期节日ID前缀 |
| 节日名称 | `2026科技节` | 用于报告标题 |
| 对标节日 | `2026情人节` | 可选，默认上一期节日 |

**需要你确认的一件事：** `iap_type like '%节日活动%'` 是否正确覆盖了本期所有节日礼包？
（可以在 pkg_breakdown 输出里核对 `混合-节日活动` 的金额是否合理）

---

## 完整查询脚本

### Step 0: 初始化（首次运行）
```bash
python .agents/skills/ai-to-sql/scripts/get_game_info.py
# 确认 game_cd=1041 (P2), datasource=TRINO_AWS, full_access=false → 用 v1041.xxx 视图
```

### Step 1: 图表5 - R级分层付费数据
脚本：`_tmp_exec_all_charts.py`（已存）

关键参数：
```python
START = '2026-03-13'   # 改为实际开始日
END   = '2026-04-03'   # 改为实际结束日
START_PART = '2026-03-12'  # START 前一天（覆盖UTC边界）
END_PART   = '2026-04-03'
FESTIVAL_ID = '%2112%'     # 改为实际节日ID
```

产出字段：
- `chart5_rlevel`: 全体/付费/xiaoR/zhongR/daR/chaoR 各层 log_num, buy_num, pay_price, pay_total, price_ratio, buy_ratio, arppu, arpu
- `daily_revenue`: 每天 festival_revenue + total_revenue
- `pkg_breakdown`: 按 iap_type 的收入分类汇总（用于验证礼包统计正确性）

### Step 2: 历史趋势数据（metrics_trend）
通过 Datain Public API 查 6 期历史节日总收入（已有脚本 `_tmp_history_query.py`）
或直接更新 `_tech_fest_input.json` 的 `metrics_trend[当期]` 的 `revenue` 字段。

---

## 需要填写 / 更新的 input JSON 字段

文件：`_tech_fest_input.json`

| 字段 | 来源 | 查询/更新方式 |
|------|------|--------------|
| `meta.event_name` | 手动 | 改节日名称 |
| `metrics_trend[当期].revenue` | Trino daily_revenue 总和 | Step 1 输出 |
| `metrics_trend[当期].arpu/arppu/pay_rate` | Datain Public API | 保持或用 Public API 更新 |
| `core_metrics_by_tier.total` | Trino chart5_rlevel | Step 1 输出（全体玩家行） |
| `core_metrics_by_tier.chaoR/daR/zhongR/xiaoR` | Trino chart5_rlevel | Step 1 输出（各R级行） |
| `daily_revenue` | Trino daily_revenue | Step 1 输出（22行 total_revenue） |
| `user_tier_trend[当期]` | Trino chart5_rlevel | 各R级 arppu 字段 |
| `module_detail` | 暂用估算 / 需要单独礼包查询 | ⚠️ 需要确认 |
| `sub_activity_detail.revenue` | 暂用估算 | ⚠️ 需要确认 |

---

## 待改进项（礼包模块拆分）

当前 `module_detail` 的各模块收入是估算值，精确值需要额外查询：

```sql
-- 按 iap_id 前缀/礼包ID范围区分节日各模块
-- 例如：科技节特惠礼包 vs 通行证BP vs 外显皮肤
-- 需要有 P2 礼包 ID 范围或礼包命名规则才能做精准拆分
```

目前的处理方式：
- `混合-节日活动` 总收入 = **$855,102**（已确认）
- 皮肤/BP/小游戏 收入来自 Datain Public API 估算
- 特惠礼包系列 = 总节日礼包 - 其他模块（倒推）

如果需要精确模块拆分，提供礼包 iap_id 范围即可。

---

## 报告生成命令

```bash
# 1. 生成图表（3张PNG）
python skills/generate_event_review/scripts/chart_generator.py --input _tech_fest_input.json --output_dir .

# 2. 生成报告 Markdown
python _tmp_gen_report.py   # 或直接调用 notion_publisher.py

# 3. 发布到 Notion（使用 Notion MCP）
# parent_page_id: 节日复盘页面ID
```

---

## 字段映射参考（Trino → input JSON）

| Trino chart5 列 | input JSON 字段 | 说明 |
|-----------------|----------------|------|
| `log_num`（全体） | `core_metrics_by_tier.total.active` | 节日参与活跃玩家数 |
| `buy_num`（全体） | `core_metrics_by_tier.total.buyers` | 购买节日礼包人数 |
| `pay_price`（全体） | `core_metrics_by_tier.total.event_revenue` | 节日礼包收入 |
| `pay_total`（全体） | `core_metrics_by_tier.total.total_revenue` | 期间全品收入 |
| `price_ratio`（全体） | `core_metrics_by_tier.total.event_share` | 节日礼包占比% |
| `arppu`（全体） | `core_metrics_by_tier.total.arppu` | 节日礼包 ARPPU |
| `arpu`（全体） | `core_metrics_by_tier.total.arpu` | 节日礼包 ARPU |
| `buy_ratio`（实际=buy_num/log_num×100）| `core_metrics_by_tier.total.buy_rate` | 购买率% |
| 各R级同理 | `core_metrics_by_tier.chaoR/daR/zhongR/xiaoR` | - |
| `arppu`（各R级） | `user_tier_trend[当期].super_r/big_r/mid_r/small_r` | ARPPU用于趋势对比图 |
| `total_revenue`（daily_revenue) | `daily_revenue[].revenue` | 每日全品收入 |
| 期间 total_revenue 总和 | `metrics_trend[当期].revenue` | 当期节日总收入 |

---

*最后更新：2026-04-07，基于科技节（3.13-4.03）验证*
