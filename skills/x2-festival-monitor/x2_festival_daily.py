#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X2 占星节收入日监控 — 每日自动生成钉钉日报"""

import json
import os
import sys
from datetime import datetime, timedelta

# 复用 ai-to-sql 的 Datain API
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-to-sql", "scripts"))
from _datain_api import execute_sql

# ============ 配置 ============
DATASOURCE = "TRINO_HF"  # X2 = TRINO_HF (API侧为 A3_TRINO)
FESTIVAL_NAME = "占星节"
FESTIVAL_D0 = "2026-05-11"  # 节日上线日
BASELINE_START = "2026-04-27"  # 基线起始日
BASELINE_END = "2026-05-10"  # 基线截止日
SERVER_FILTER = "AND o.server_id >= '1001202' AND o.server_id <= '1007502'"  # 12-75服
SERVER_LABEL = "12-75服"
OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "_x2_festival_daily.txt")

# 节日模块关键词 → 模块名映射
MODULE_RULES = [
    ("GACHA", ["GACHA礼包", "随机GACHA"]),
    ("大富翁", ["大富翁", "骰子", "存钱罐"]),
    ("BP通行证", ["通行证", "bp集结", "节日活动BP"]),
    ("七日活动", ["七日活动", "连锁触发"]),
    ("行军表情", ["行军表情"]),
]


def query(sql, limit=200):
    """执行 SQL 并返回行列表"""
    rows = execute_sql(sql.strip().rstrip(";"), DATASOURCE)
    return rows[:limit] if rows else []


def calc_day_number(date_str):
    """计算节日第几天"""
    d0 = datetime.strptime(FESTIVAL_D0, "%Y-%m-%d")
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return (d - d0).days


def classify_module(iap_name):
    """根据 iap_id_name 分类到节日模块"""
    if not iap_name:
        return "其他"
    for module, keywords in MODULE_RULES:
        for kw in keywords:
            if kw in iap_name:
                return module
    return "其他"


def fmt_money(v):
    return f"${v:,.0f}" if v >= 1000 else f"${v:.0f}"


def fmt_pct(v):
    if v is None or v == 0:
        return "—"
    sign = "+" if v > 0 else ""
    return f"{sign}{v:.1f}%"


def fmt_delta(v):
    sign = "+" if v > 0 else ""
    return f"{sign}${v:.2f}"


def main():
    # 每天早上跑，查的是昨天（完整数据）和前天
    report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")  # 昨天
    compare_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")  # 前天
    day_num = calc_day_number(report_date)

    # ---- 1. 每日收入拆分（基线期 + 节日期） ----
    sql_daily = f"""
    SELECT o.partition_date,
      sum(CASE WHEN i.iap_type IN ('混合-节日活动','活动礼包') THEN o.pay_price ELSE 0 END) as festival_rev,
      sum(CASE WHEN i.iap_type NOT IN ('混合-节日活动','活动礼包') OR i.iap_type IS NULL THEN o.pay_price ELSE 0 END) as non_festival_rev,
      sum(o.pay_price) as total_rev,
      count(distinct o.user_id) as payers
    FROM v1089.dl_user_order o
    LEFT JOIN v1089.dim_iap i ON o.iap_id = i.iap_id
    WHERE (o.partition_date BETWEEN '{BASELINE_START}' AND '{report_date}')
    {SERVER_FILTER}
    GROUP BY o.partition_date
    ORDER BY o.partition_date
    """

    rows_daily = query(sql_daily)
    if not rows_daily:
        print("ERROR: 未查到数据，请检查日期和权限")
        sys.exit(1)

    # 分离基线/报告日/对比日
    baseline_rows = [r for r in rows_daily if BASELINE_START <= r["partition_date"] <= BASELINE_END]
    today_row = next((r for r in rows_daily if r["partition_date"] == report_date), None)
    yesterday_row = next((r for r in rows_daily if r["partition_date"] == compare_date), None)

    if not today_row:
        print(f"ERROR: 报告日({report_date})数据不存在")
        sys.exit(1)

    # 基线计算
    n_baseline = len(baseline_rows)
    bl_total = sum(float(r["total_rev"]) for r in baseline_rows) / max(n_baseline, 1)
    bl_nonfest = sum(float(r["non_festival_rev"]) for r in baseline_rows) / max(n_baseline, 1)
    bl_payers = sum(int(r["payers"]) for r in baseline_rows) / max(n_baseline, 1)
    bl_arpu_total = bl_total / max(bl_payers, 1)
    bl_arpu_nonfest = bl_nonfest / max(bl_payers, 1)

    # 今日
    t_total = float(today_row["total_rev"])
    t_fest = float(today_row["festival_rev"])
    t_nonfest = float(today_row["non_festival_rev"])
    t_payers = int(today_row["payers"])
    t_arpu_fest = t_fest / max(t_payers, 1)
    t_arpu_nonfest = t_nonfest / max(t_payers, 1)
    t_arpu_total = t_total / max(t_payers, 1)

    # 昨日
    if yesterday_row:
        y_total = float(yesterday_row["total_rev"])
        y_fest = float(yesterday_row["festival_rev"])
        y_nonfest = float(yesterday_row["non_festival_rev"])
        y_payers = int(yesterday_row["payers"])
        y_arpu_fest = y_fest / max(y_payers, 1)
        y_arpu_nonfest = y_nonfest / max(y_payers, 1)
        y_arpu_total = y_total / max(y_payers, 1)
    else:
        y_total = y_fest = y_nonfest = y_arpu_fest = y_arpu_nonfest = y_arpu_total = 0
        y_payers = 0

    # 环比
    def pct_change(new, old):
        return (new - old) / old * 100 if old else None

    # 累计（D0到报告日）
    festival_rows = [r for r in rows_daily if r["partition_date"] >= FESTIVAL_D0 and r["partition_date"] <= report_date]
    cum_total = sum(float(r["total_rev"]) for r in festival_rows)
    cum_fest = sum(float(r["festival_rev"]) for r in festival_rows)
    cum_nonfest = sum(float(r["non_festival_rev"]) for r in festival_rows)

    # ---- 2. 节日模块明细 ----
    sql_modules = f"""
    SELECT o.partition_date, i.iap_id_name,
      sum(o.pay_price) as revenue
    FROM v1089.dl_user_order o
    LEFT JOIN v1089.dim_iap i ON o.iap_id = i.iap_id
    WHERE o.partition_date IN ('{report_date}', '{compare_date}')
      AND i.iap_type IN ('混合-节日活动','活动礼包')
    {SERVER_FILTER}
    GROUP BY o.partition_date, i.iap_id_name
    ORDER BY o.partition_date, revenue DESC
    """
    rows_modules = query(sql_modules)

    # 按模块聚合
    modules_today = {}
    modules_yesterday = {}
    for r in rows_modules:
        mod = classify_module(r.get("iap_id_name", ""))
        rev = float(r["revenue"])
        if r["partition_date"] == report_date:
            modules_today[mod] = modules_today.get(mod, 0) + rev
        elif r["partition_date"] == compare_date:
            modules_yesterday[mod] = modules_yesterday.get(mod, 0) + rev

    # 模块排序
    all_modules = sorted(set(list(modules_today.keys()) + list(modules_yesterday.keys())),
                         key=lambda m: modules_today.get(m, 0), reverse=True)
    mod_total_today = sum(modules_today.values())
    mod_total_cum = sum(modules_today.values()) + sum(modules_yesterday.values())

    # ---- 3. 生成钉钉消息 ----
    lines = []
    lines.append(f"**X2{FESTIVAL_NAME}日报 | D{day_num}（{report_date}）| {SERVER_LABEL}**")
    lines.append("")

    # 核心指标
    lines.append("**📊 核心指标**")
    lines.append("```")
    lines.append(f"总流水    今日 {fmt_money(t_total)} | 昨日 {fmt_money(y_total)} | {fmt_pct(pct_change(t_total, y_total))}")
    lines.append(f"付费人数  今日 {t_payers}     | 昨日 {y_payers}     | {fmt_pct(pct_change(t_payers, y_payers))}")
    lines.append(f"节日流水  今日 {fmt_money(t_fest)} | 昨日 {fmt_money(y_fest)} | {fmt_pct(pct_change(t_fest, y_fest))}")
    lines.append(f"非节日    今日 {fmt_money(t_nonfest)} | 昨日 {fmt_money(y_nonfest)} | {fmt_pct(pct_change(t_nonfest, y_nonfest))}")
    lines.append(f"基线(14日均): {fmt_money(bl_total)}/日 | 累计(D0~D{day_num}): {fmt_money(cum_total)}")
    lines.append("```")
    lines.append("")

    # ARPU
    lines.append("**💰 ARPU增量（分母=总付费人数）**")
    lines.append("```")
    lines.append(f"节日ARPU    ${t_arpu_fest:.2f} (基线$0)     净增 +${t_arpu_fest:.2f}")
    lines.append(f"非节日ARPU  ${t_arpu_nonfest:.2f} (基线${bl_arpu_nonfest:.2f}) 净增 {fmt_delta(t_arpu_nonfest - bl_arpu_nonfest)}")
    lines.append(f"综合ARPU    ${t_arpu_total:.2f} (基线${bl_arpu_total:.2f}) 净增 {fmt_delta(t_arpu_total - bl_arpu_total)}")
    lines.append("```")

    # 增量结论
    nonfest_delta = t_arpu_nonfest - bl_arpu_nonfest
    if nonfest_delta > 1:
        conclusion = f"节日纯增量+${t_arpu_fest:.2f}/人，非节日被带动+${nonfest_delta:.2f}/人"
    elif nonfest_delta < -1:
        conclusion = f"节日纯增量+${t_arpu_fest:.2f}/人，⚠️非节日被挤占{fmt_delta(nonfest_delta)}/人"
    else:
        conclusion = f"节日纯增量+${t_arpu_fest:.2f}/人，非节日基本持平"
    lines.append(f"结论：{conclusion}")
    lines.append("")

    # 模块明细
    lines.append("**🎯 节日模块TOP**")
    lines.append("```")
    for mod in all_modules:
        t_rev = modules_today.get(mod, 0)
        y_rev = modules_yesterday.get(mod, 0)
        cum_rev = t_rev + y_rev
        pct = t_rev / mod_total_today * 100 if mod_total_today > 0 else 0
        tag = ""
        if y_rev < 10 and t_rev > 100:
            tag = " ← 新开"
        lines.append(f"{mod:<8} {fmt_money(t_rev):>7} ({pct:.0f}%) | 累计{fmt_money(cum_rev)}{tag}")
    lines.append("```")
    lines.append("")

    # 关注点（自动生成）
    lines.append("**⚠️ 关注点**")
    alerts = []
    # 大富翁爆发检测
    for mod in all_modules:
        y_rev = modules_yesterday.get(mod, 0)
        t_rev = modules_today.get(mod, 0)
        if y_rev < 50 and t_rev > 500:
            alerts.append(f"• {mod}今日新开即贡献{fmt_money(t_rev)}，占节日收入{t_rev / mod_total_today * 100:.0f}%")
    # GACHA占比变化
    if "GACHA" in modules_today and "GACHA" in modules_yesterday:
        gacha_pct_today = modules_today["GACHA"] / mod_total_today * 100 if mod_total_today else 0
        gacha_pct_yesterday = modules_yesterday["GACHA"] / sum(modules_yesterday.values()) * 100 if sum(modules_yesterday.values()) else 0
        if gacha_pct_yesterday > gacha_pct_today + 10:
            alerts.append(f"• GACHA占比从D{day_num-1}的{gacha_pct_yesterday:.0f}%降到{gacha_pct_today:.0f}%，收入结构分散化")
    # 非节日挤占
    if nonfest_delta < -2:
        alerts.append(f"• ⚠️ 非节日ARPU下降{fmt_delta(nonfest_delta)}/人，存在挤占风险")
    elif nonfest_delta > 2:
        alerts.append(f"• 非节日ARPU上升{fmt_delta(nonfest_delta)}/人，节日带动日常消费")
    else:
        alerts.append("• 非节日消费持平，节日为纯增量模型")
    # 数据口径
    alerts.append(f"• 数据口径：{SERVER_LABEL}，节日模块=dim_iap中iap_type为\"混合-节日活动\"+\"活动礼包\"")

    lines.extend(alerts)

    report = "\n".join(lines)

    # 输出到文件和控制台
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\n--- 已保存到 {OUTPUT_PATH} ---")


if __name__ == "__main__":
    main()
