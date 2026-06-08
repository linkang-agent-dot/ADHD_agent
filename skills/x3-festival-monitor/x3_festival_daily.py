#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X3 节日收入日监控 — 全天页签 HTML 日报（移植自 X2 x2-festival-monitor）

口径差异（vs X2）：
  - 数仓：TRINO_HF / v1090.ods_user_order + v1090.dim_iap（X2 是 v1089.dl_user_order）
  - 收入：USD 口径 = pay_status=1；仅 currency_type='usd' 取 actual_charge，其余(含 TOKEN)取 pay_price(USD归一价)
    （TOKEN 的 actual_charge 自 2026-06-02 起改记代币单位=USD×100，再取 actual_charge 会放大 100 倍）
  - 节日判定：X3 的 dim_iap.iap_type 不是干净的节日标记，改用 Pack ID 前缀圈定（见 FESTIVAL_IAP_PREFIXES）
  - 服段：默认全服（X3 节日按服龄分服上线，无统一日历服段）；如需限服改 SERVER_FILTER
  - 模块：先按 iap_id_name 关键词命中 MODULE_RULES，未命中则回退 dim_iap.iap_type2 末段

换节日时只改下方 ====== 配置 ====== 区块。
"""

import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-to-sql", "scripts"))
from _datain_api import execute_sql

# ============ 配置 ============
DATASOURCE = "TRINO_HF"
FESTIVAL_NAME = "夏日节"
# 夏日恋语在 1-88 服的真实开场日 = 2026-05-29（05-28 在 88 服节日流水为 0，05-25 的 $30 是复用包尾单噪声）
FESTIVAL_D0 = "2026-05-29"
# ⚠️ 节日活动下线时点（必填）：累充活动 100595 在 2026-06-08 08:00(北京时间) 下线。
# 数仓 created_at/partition_date 均为北京时间（开场日 hour=8 暴涨、下线日 hour=8 起零成交，已实测验证）。
# 必须加这道时间上界：白名单里的复用包(情人节连锁 2107xx / 通用通行证 130020·130021 / 许愿池 1002001)
# 下个活动会被重新挂上来卖，没有时间卡口会把下线后的常态流水继续误算成本届节日收入。
# 对 D0~D9 无影响(全在卡口前)，仅精确收口 06-08 当天到 08:00 + 防未来误算。
FESTIVAL_END_TS = "2026-06-08 08:00:00"
FEST_TIME_GUARD = f"o.created_at < TIMESTAMP '{FESTIVAL_END_TS}'"
BASELINE_START = "2026-05-15"       # 基线 14 日（节日前）
BASELINE_END = "2026-05-28"
# 双服段（核心：同期对比要"服务器生命周期一致" = 各期取「D0 时距开服天数(服龄)处于同一阶段」的服，
#   排除新服爆发期对对比的干扰。**按服龄阈值匹配，不是同一批物理服**）：
# - 夏日(本期，主报告+对比夏日侧) = 1-88服(server_id 1000~1870)：节日实际投放到 1870 服为止；
#   均为夏日 D0(05-29) 已过 D35 的成熟服（1880 开服 04-27、D0 时仅服龄 32 天未达 D35，且未上节日，排除）。
# - 情人节(对比上期侧) = 1-55服(1000~1540)：情人节 D0(02-06) 已过 D35 的成熟服
#   （1550+ 在情人节时未开服/未过 D35 = 爆发期新服，排除）。
# 两期各取"D0 已过 D35 的成熟服"（服龄阶段一致），物理服可以不同 → 排除生命周期影响。
SERVER_FILTER = "AND TRY_CAST(o.server_id AS INTEGER) BETWEEN 1000 AND 1870"      # 夏日 88服(节日投放到1870/过D35成熟盘)
SERVER_FILTER_VAL = "AND TRY_CAST(o.server_id AS INTEGER) BETWEEN 1000 AND 1540"  # 情人节 55服(过D35成熟盘)
SERVER_LABEL = "本期夏日 1-88服(1000-1870)；上期情人节 1-55服(1000-1540)。各取D0已过D35的成熟服(服龄阶段一致，非同一批服)，排除生命周期影响"
OUTPUT_DIR = os.path.expanduser("~")

# === 节日礼包口径：从配置表读，不靠名字/前缀猜 ===
# 礼包全集来源 = ActvOnline 累充活动的 RechargePointPackWhitelist（权威：哪些 Pack 算本节日）
# 累充活动 ContentID：夏日恋语 = 100595（行名"26情人节-累充"是 TimeCycle 复用的历史残留）
# 模块分类 = Pack.PackType（config 原生分类），不用名字关键词
GDCONFIG_TSV = r"C:\x3\gdconfig\tsv"
RECHARGE_ACTV_ID = "100595"
# 强制并入的节日礼包（累充白名单口径是"算不算累充积分"，装饰礼包本期可能不入累充，
# 但属夏日恋语-装饰礼包链 ChainPack 647，收入监控必须算；不受累充配置抖动影响）
ALWAYS_INCLUDE_PACKS = ["210917", "210918", "210919"]

# PackType → 模块名（Pack.xlsx 的 PackType 列；11=链式特惠/15=抽奖券锚点/16=家具外观/18=通行证）
PACKTYPE_MODULE = {
    "11": "特惠连锁", "15": "抽奖券", "16": "家具/外观",
    "18": "通行证", "3": "常规礼包", "7": "每日特惠", "1": "皮肤礼包",
}
# 个别 Pack 单独成模块（PackType 相同但语义不同，拆开更可读）
# 210917/918/919 是 PackType=11 但属"夏日恋语-装饰礼包"链(ChainPack 647)，与情人节复用的特惠连锁分开
PACK_OVERRIDE = {
    "210717": "家具礼包", "1002001": "许愿池", "210921": "拜访皮肤",
    "210917": "装饰礼包", "210918": "装饰礼包", "210919": "装饰礼包",
}
# 配置读不到时的兜底快照（2026-05-29 ActvOnline 100595 白名单，17 包）
FALLBACK_PACK_IDS = ["210702", "210704", "210706", "210708", "210710",
                     "210712", "210713", "210714", "210715", "210717",
                     "210917", "210918", "210919", "210921",
                     "130020", "130021", "1002001"]

# USD 收入表达式（X3 口径）
# ⚠️ TOKEN 货币的 actual_charge 自 2026-06-02 起改记代币单位(=USD×100)，不能再取 actual_charge。
# pay_price 始终是 USD 归一价（usd/TOKEN/本地币皆然）；usd 的 actual==pay，故只有 usd 取 actual_charge。
# （旧口径 currency_type IN('usd','TOKEN') 取 actual_charge 会把 TOKEN 订单放大 100 倍，D4/D5 整份日报灌水。）
REV_EXPR = "(CASE WHEN o.currency_type = 'usd' THEN o.actual_charge ELSE o.pay_price END)"

# R级分层：v1090.dl_user_rlevel_all_info 按日快照 user_id→rlevel(chaoR/daR/zhongR/xiaoR)。
# ⚠️ 该分级表不全：会漏掉一部分真实付费用户（任何日期/game_cd 都查不到）。
# 分类口径：① 快照命中 → 用快照档；② 快照漏掉但有累充 → 按累充金额(USD)估算档；③ 零充 → 非R。
# 累充阈值由分级表已分级用户的累充分布反推（各档中位 小R$4.7/中R$344/大R$825/超R$2064，取中点近似）。
RLEVEL_ORDER = ["超R", "大R", "中R", "小R", "非R"]
RLEVEL_THRESH = "1500/500/50"  # 超R≥1500 / 大R≥500 / 中R≥50 / 小R>0（USD 累充估算，仅用于快照漏掉者）
# 累充兜底落档（USD，截至窗口末）
_LTV_CASE = ("CASE WHEN lt.ltv >= 1500 THEN '超R' WHEN lt.ltv >= 500 THEN '大R' "
             "WHEN lt.ltv >= 50 THEN '中R' WHEN lt.ltv > 0 THEN '小R' ELSE '非R' END")
# 最终 R级 = 快照优先，漏掉则累充兜底
RCLASS = f"COALESCE(rl.rb, {_LTV_CASE})"

# 基础配色（未列出的模块从调色板自动分配）
BASE_COLORS = {
    "特惠连锁": "#6c63ff", "抽奖券": "#ffd166", "家具礼包": "#34d399",
    "拜访皮肤": "#a78bfa", "许愿池": "#38bdf8", "通行证": "#fb923c",
    "装饰礼包": "#e879f9", "皮肤礼包": "#f43f5e", "常规礼包": "#00d4aa", "每日特惠": "#f472b6", "其他": "#8892a4",
}
PALETTE = ["#00d4aa", "#ff6b6b", "#f59e0b", "#ec4899", "#22c55e", "#60a5fa",
           "#c084fc", "#fbbf24", "#fb7185", "#2dd4bf", "#818cf8", "#facc15"]

# 上期节日首日对比基准（X3 26情人节 D0=2026-02-06，1-88服）
# 两节日均 08:00 开场（节日流水从该时起跳），对比按"已跑小时数"对齐，避免拿夏日10h比情人节整天
BENCHMARK_NAME = "情人节"
BENCHMARK_D0 = "2026-02-06"
# 情人节节日礼包判定（2107xx 情人节专属 + 复用的通用通行证/许愿池）
BENCHMARK_FEST_PRED = "(o.iap_id LIKE '2107%' OR o.iap_id IN ('130020','130021','1002001'))"
LAUNCH_HOUR = 8  # 两节日开场时点（created_at 时）


def query(sql, limit=2000):
    rows = execute_sql(sql.strip().rstrip(";"), DATASOURCE)
    return rows[:limit] if rows else []


def calc_day_number(date_str):
    d0 = datetime.strptime(FESTIVAL_D0, "%Y-%m-%d")
    return (datetime.strptime(date_str, "%Y-%m-%d") - d0).days


def fmt_money(v):
    return f"${v:,.0f}" if v >= 1000 else f"${v:.0f}"


def load_festival_packs():
    """从配置表读节日礼包：ActvOnline 累充白名单 → Pack 清单；Pack.PackType → 模块。
    读不到（配置仓缺失/列变动）时回退 FALLBACK_PACK_IDS 快照。
    返回 (pack_ids:list, pack_module:dict{id->模块名})。"""
    import csv
    pack_type = {}
    pack_ids = []
    try:
        # Pack__Pack.tsv → {pack_id: PackType}
        prows = list(csv.reader(open(os.path.join(GDCONFIG_TSV, "Pack__Pack.tsv"),
                                     encoding="utf-8"), delimiter="\t"))
        hdr = next(r for r in prows[:40] if "PackType" in r)
        ci_type = hdr.index("PackType")
        for r in prows:
            if r and r[0].isdigit() and len(r) > ci_type:
                pack_type[r[0]] = r[ci_type]
        # ActvOnline__ActvOnline.tsv → RECHARGE_ACTV_ID 行的累充白名单列
        arows = list(csv.reader(open(os.path.join(GDCONFIG_TSV, "ActvOnline__ActvOnline.tsv"),
                                     encoding="utf-8"), delimiter="\t"))
        whcol = None
        for r in arows[:12]:
            for ci, c in enumerate(r):
                if "RechargePointPackWhitelist" in c:
                    whcol = ci
        for r in arows:
            if r and r[0] == RECHARGE_ACTV_ID and whcol is not None and len(r) > whcol:
                pack_ids = [p for p in r[whcol].split("|") if p.strip()]
                break
    except Exception as e:
        print(f"WARN 读配置表失败({e})，回退兜底快照")
    if not pack_ids:
        pack_ids = list(FALLBACK_PACK_IDS)
    # 强制并入节日礼包（不受累充白名单抖动影响）
    for p in ALWAYS_INCLUDE_PACKS:
        if p not in pack_ids:
            pack_ids.append(p)
    pack_module = {}
    for pid in pack_ids:
        if pid in PACK_OVERRIDE:
            pack_module[pid] = PACK_OVERRIDE[pid]
        else:
            pack_module[pid] = PACKTYPE_MODULE.get(pack_type.get(pid, ""), "其他")
    return pack_ids, pack_module


def load_pack_type_map():
    """读 Pack__Pack.tsv → {pack_id: PackType}，给对比用（含情人节包）。读不到返回空。"""
    import csv
    try:
        prows = list(csv.reader(open(os.path.join(GDCONFIG_TSV, "Pack__Pack.tsv"),
                                     encoding="utf-8"), delimiter="\t"))
        hdr = next(r for r in prows[:40] if "PackType" in r)
        ci = hdr.index("PackType")
        return {r[0]: r[ci] for r in prows if r and r[0].isdigit() and len(r) > ci}
    except Exception:
        return {}


def module_of(pid, pack_type_map):
    if pid in PACK_OVERRIDE:
        return PACK_OVERRIDE[pid]
    return PACKTYPE_MODULE.get(pack_type_map.get(pid, ""), "其他")


def query_window(d0_date, fest_pred, h_start, h_end, pack_type_map, sf=SERVER_FILTER):
    """取某节日 D0 在 [h_start, h_end] 小时窗内的 总/节日/付费/节日付费 + 模块构成。sf=服段过滤。"""
    sql = f"""
    SELECT count(distinct o.user_id) total_payers,
      round(sum({REV_EXPR}),0) total_rev,
      round(sum(CASE WHEN {fest_pred} THEN {REV_EXPR} ELSE 0 END),0) fest_rev,
      count(distinct CASE WHEN {fest_pred} THEN o.user_id END) fest_payers
    FROM v1090.ods_user_order o
    WHERE o.pay_status=1 AND o.partition_date='{d0_date}'
      AND hour(o.created_at) BETWEEN {h_start} AND {h_end}
    {sf}
    """
    agg = query(sql)
    if not agg:
        return None
    a = agg[0]
    sql_mod = f"""
    SELECT o.iap_id, round(sum({REV_EXPR}),0) rev
    FROM v1090.ods_user_order o
    WHERE o.pay_status=1 AND o.partition_date='{d0_date}'
      AND hour(o.created_at) BETWEEN {h_start} AND {h_end}
      AND {fest_pred}
    {sf}
    GROUP BY o.iap_id
    """
    mods = {}
    for r in query(sql_mod):
        m = module_of(str(r["iap_id"]), pack_type_map)
        mods[m] = mods.get(m, 0) + round(float(r["rev"] or 0))
    return {
        "total": round(float(a["total_rev"] or 0)),
        "festival": round(float(a["fest_rev"] or 0)),
        "payers": int(a["total_payers"] or 0),
        "fest_payers": int(a["fest_payers"] or 0),
        "modules": mods,
    }


def cum_date_pred(start_date, last_date, prev_last_date, last_max_hr, partial):
    """累计窗口的 partition_date 谓词：完成日整日 + 进行中当天首 last_max_hr 小时。"""
    if partial:
        return (f"(o.partition_date BETWEEN '{start_date}' AND '{prev_last_date}' "
                f"OR (o.partition_date='{last_date}' AND hour(o.created_at) <= {last_max_hr}))")
    return f"o.partition_date BETWEEN '{start_date}' AND '{last_date}'"


def query_cum(date_pred, fest_pred, pack_type_map, sf=SERVER_FILTER):
    """按累计日期窗口取 总/节日/去重付费/去重节日付费 + 模块构成（人数为整窗去重，非按天相加）。sf=服段过滤。"""
    sql = f"""
    SELECT count(distinct o.user_id) total_payers,
      round(sum({REV_EXPR}),0) total_rev,
      round(sum(CASE WHEN {fest_pred} THEN {REV_EXPR} ELSE 0 END),0) fest_rev,
      count(distinct CASE WHEN {fest_pred} THEN o.user_id END) fest_payers
    FROM v1090.ods_user_order o
    WHERE o.pay_status=1 AND {date_pred}
    {sf}
    """
    agg = query(sql)
    if not agg:
        return None
    a = agg[0]
    sql_mod = f"""
    SELECT o.iap_id, round(sum({REV_EXPR}),0) rev
    FROM v1090.ods_user_order o
    WHERE o.pay_status=1 AND {date_pred} AND {fest_pred}
    {sf}
    GROUP BY o.iap_id
    """
    mods = {}
    for r in query(sql_mod):
        m = module_of(str(r["iap_id"]), pack_type_map)
        mods[m] = mods.get(m, 0) + round(float(r["rev"] or 0))
    return {
        "total": round(float(a["total_rev"] or 0)),
        "festival": round(float(a["fest_rev"] or 0)),
        "payers": int(a["total_payers"] or 0),
        "fest_payers": int(a["fest_payers"] or 0),
        "modules": mods,
    }


def rl_join(asof_date):
    """R级 join 子查询：用 <= asof_date 的最近一份快照分类（各期用各期当期档位，才公平对打）。"""
    return ("(SELECT user_id, CASE rlevel WHEN 'chaoR' THEN '超R' WHEN 'daR' THEN '大R' "
            "WHEN 'zhongR' THEN '中R' WHEN 'xiaoR' THEN '小R' ELSE '非R' END AS rb "
            "FROM v1090.dl_user_rlevel_all_info "
            f"WHERE partition_date=(SELECT max(partition_date) FROM v1090.dl_user_rlevel_all_info "
            f"WHERE partition_date<='{asof_date}') AND game_cd=1090)")


def ltv_join(asof_date):
    """累充兜底子查询：每个 user 截至 asof_date 的历史累充(USD)，用于分级表漏掉者的估算落档。"""
    return ("(SELECT user_id, sum(CASE WHEN currency_type = 'usd' "
            "THEN actual_charge ELSE pay_price END) AS ltv "
            "FROM v1090.ods_user_order "
            f"WHERE pay_status=1 AND partition_date <= '{asof_date}' GROUP BY user_id)")


def query_by_r(date_where, fest_pred, asof_date, sf=SERVER_FILTER):
    """按 R级 拆某窗口的 节日流水/总付费/节日付费（人数整窗去重）。返回 {rb: {...}}，补齐全 5 档。
    分类 = 快照优先 + 累充兜底（分级表漏掉的付费用户按累充估档，不再误归非R）。sf=服段过滤。"""
    sql = f"""
    SELECT {RCLASS} rb,
      round(sum(CASE WHEN {fest_pred} THEN {REV_EXPR} ELSE 0 END),0) fest_rev,
      count(distinct o.user_id) total_payers,
      count(distinct CASE WHEN {fest_pred} THEN o.user_id END) fest_payers
    FROM v1090.ods_user_order o
    LEFT JOIN {rl_join(asof_date)} rl ON o.user_id = rl.user_id
    LEFT JOIN {ltv_join(asof_date)} lt ON o.user_id = lt.user_id
    WHERE o.pay_status=1 AND {date_where}
    {sf}
    GROUP BY {RCLASS}
    """
    out = {}
    for r in query(sql):
        out[r["rb"]] = {
            "festival": round(float(r["fest_rev"] or 0)),
            "payers": int(r["total_payers"] or 0),
            "fest_payers": int(r["fest_payers"] or 0),
        }
    return {rb: out.get(rb, {"festival": 0, "payers": 0, "fest_payers": 0}) for rb in RLEVEL_ORDER}


def query_active_by_r(date_where, asof_date):
    """按 R级 取窗口内去重活跃人数（登录口径），用于付费率/ARPU 的分母。date_where 用 o.* 前缀。"""
    sql = f"""
    SELECT {RCLASS} rb, count(distinct o.user_id) au
    FROM v1090.ods_user_login o
    LEFT JOIN {rl_join(asof_date)} rl ON o.user_id = rl.user_id
    LEFT JOIN {ltv_join(asof_date)} lt ON o.user_id = lt.user_id
    WHERE {date_where}
    {SERVER_FILTER}
    GROUP BY {RCLASS}
    """
    out = {}
    for r in query(sql, limit=64):
        out[r["rb"]] = int(r["au"] or 0)
    return {rb: out.get(rb, 0) for rb in RLEVEL_ORDER}


def build_module_case(id2mod):
    """把 iap_id→模块 的映射拼成 SQL CASE（用于在库里直接按模块去重买家，不在 Python 端汇总避免重复计人）。"""
    if not id2mod:
        return "'其他'"
    whens = " ".join(f"WHEN '{k}' THEN '{v}'" for k, v in id2mod.items())
    return f"CASE o.iap_id {whens} ELSE '其他' END"


def query_module_r(date_pred, fest_pred, asof_date, case_sql, sf=SERVER_FILTER):
    """按 R级 × 模块 取 节日流水 + 去重买家。返回 {rb: {module: {buyers, rev}}}。sf=服段过滤。"""
    sql = f"""
    SELECT {RCLASS} rb, {case_sql} module,
      count(distinct o.user_id) buyers, round(sum({REV_EXPR}),0) rev
    FROM v1090.ods_user_order o
    LEFT JOIN {rl_join(asof_date)} rl ON o.user_id = rl.user_id
    LEFT JOIN {ltv_join(asof_date)} lt ON o.user_id = lt.user_id
    WHERE o.pay_status=1 AND {date_pred} AND {fest_pred}
    {sf}
    GROUP BY {RCLASS}, {case_sql}
    """
    out = {}
    for r in query(sql, limit=400):
        out.setdefault(r["rb"], {})[r["module"]] = {
            "buyers": int(r["buyers"] or 0), "rev": round(float(r["rev"] or 0))}
    return out


def main():
    # 报告日：默认今天（每小时刷新看当天实时累积）；支持回算 —— 命令行传日期 或 环境变量 X3_REPORT_DATE
    report_date = datetime.now().strftime("%Y-%m-%d")
    if len(sys.argv) > 1:
        report_date = sys.argv[1]
    elif os.environ.get("X3_REPORT_DATE"):
        report_date = os.environ["X3_REPORT_DATE"]
    day_num = calc_day_number(report_date)
    pack_ids, pack_module = load_festival_packs()
    fest_cond = "(o.iap_id IN (" + ",".join(f"'{p}'" for p in pack_ids) + ") AND " + FEST_TIME_GUARD + ")"
    print(f"节日礼包口径：ActvOnline {RECHARGE_ACTV_ID} 累充白名单 {len(pack_ids)} 个 Pack")

    # ---- 1. 每日汇总（基线期 + 节日期） ----
    sql_daily = f"""
    SELECT o.partition_date,
      sum(CASE WHEN {fest_cond} THEN {REV_EXPR} ELSE 0 END) as festival_rev,
      sum({REV_EXPR}) - sum(CASE WHEN {fest_cond} THEN {REV_EXPR} ELSE 0 END) as non_festival_rev,
      sum({REV_EXPR}) as total_rev,
      count(distinct o.user_id) as payers
    FROM v1090.ods_user_order o
    WHERE o.pay_status = 1
      AND o.partition_date BETWEEN '{BASELINE_START}' AND '{report_date}'
    {SERVER_FILTER}
    GROUP BY o.partition_date
    ORDER BY o.partition_date
    """
    rows_daily = query(sql_daily)
    if not rows_daily:
        print("ERROR: 未查到数据"); sys.exit(1)

    # ---- 2. 每天的模块明细（仅节日期，按 Pack ID 聚合后按 PackType 归模块） ----
    sql_modules = f"""
    SELECT o.partition_date, o.iap_id, sum({REV_EXPR}) as revenue
    FROM v1090.ods_user_order o
    WHERE o.pay_status = 1
      AND o.partition_date BETWEEN '{FESTIVAL_D0}' AND '{report_date}'
      AND {fest_cond}
    {SERVER_FILTER}
    GROUP BY o.partition_date, o.iap_id
    """
    rows_modules = query(sql_modules)

    # 聚合模块数据: {date: {module: revenue}}（模块来自配置 Pack.PackType）
    mod_by_date = {}
    all_mod_names = set()
    for r in rows_modules:
        d = r["partition_date"]
        mod = pack_module.get(str(r["iap_id"]), "其他")
        rev = float(r["revenue"] or 0)
        mod_by_date.setdefault(d, {})
        mod_by_date[d][mod] = mod_by_date[d].get(mod, 0) + rev
        all_mod_names.add(mod)

    # ---- 3. 基线 ----
    baseline_rows = [r for r in rows_daily if BASELINE_START <= r["partition_date"] <= BASELINE_END]
    n_bl = max(len(baseline_rows), 1)
    bl_total = sum(float(r["total_rev"] or 0) for r in baseline_rows) / n_bl
    bl_nonfest = sum(float(r["non_festival_rev"] or 0) for r in baseline_rows) / n_bl
    bl_payers = sum(int(r["payers"] or 0) for r in baseline_rows) / n_bl

    baseline = {
        "total": round(bl_total, 2),
        "non_festival": round(bl_nonfest, 2),
        "payers": round(bl_payers, 1),
        "arpu_total": round(bl_total / max(bl_payers, 1), 2),
        "arpu_nonfest": round(bl_nonfest / max(bl_payers, 1), 2),
    }

    # ---- 4. 配色（动态分配未知模块） ----
    module_colors = dict(BASE_COLORS)
    pi = 0
    for m in sorted(all_mod_names):
        if m not in module_colors:
            module_colors[m] = PALETTE[pi % len(PALETTE)]
            pi += 1

    # ---- 5. 构建 allDays ----
    festival_rows = [r for r in rows_daily if r["partition_date"] >= FESTIVAL_D0]
    all_days = []
    for r in festival_rows:
        d = r["partition_date"]
        dn = calc_day_number(d)
        modules = {}
        for m in sorted(all_mod_names):
            modules[m] = round(mod_by_date.get(d, {}).get(m, 0))
        all_days.append({
            "date": d,
            "day_label": f"D{dn}",
            "day_num": dn,
            "total": round(float(r["total_rev"] or 0)),
            "festival": round(float(r["festival_rev"] or 0)),
            "non_festival": round(float(r["non_festival_rev"] or 0)),
            "payers": int(r["payers"] or 0),
            "modules": modules,
        })

    if not all_days:
        print("ERROR: 无节日期数据"); sys.exit(1)

    # ---- 5a. 分时收入立方（天 × 小时 × R级 → 总/节日流水），驱动分时图 R级筛选 ----
    sql_cube = f"""
    SELECT o.partition_date AS d, hour(o.created_at) AS hr, {RCLASS} AS rb,
      round(sum({REV_EXPR}),0) AS total_rev,
      round(sum(CASE WHEN {fest_cond} THEN {REV_EXPR} ELSE 0 END),0) AS fest_rev
    FROM v1090.ods_user_order o
    LEFT JOIN {rl_join(report_date)} rl ON o.user_id = rl.user_id
    LEFT JOIN {ltv_join(report_date)} lt ON o.user_id = lt.user_id
    WHERE o.pay_status = 1
      AND o.partition_date BETWEEN '{FESTIVAL_D0}' AND '{report_date}'
    {SERVER_FILTER}
    GROUP BY o.partition_date, hour(o.created_at), {RCLASS}
    ORDER BY o.partition_date, hr
    """
    # cube[date][rb] = {hr: (total, fest)}
    cube = {}
    for r in query(sql_cube, limit=24 * 6 * 90):
        cube.setdefault(r["d"], {}).setdefault(r["rb"], {})[int(r["hr"])] = (
            round(float(r["total_rev"] or 0)), round(float(r["fest_rev"] or 0)))
    hourly_data = []
    for day in all_days:
        dct = cube.get(day["date"], {})
        max_hr = -1  # 当天截到最后有数据的小时（今天可能不满 24h）
        for hm in dct.values():
            if hm:
                max_hr = max(max_hr, max(hm.keys()))

        def arr_for(rkeys):
            tot = [0] * (max_hr + 1); fes = [0] * (max_hr + 1)
            for rb in rkeys:
                for h, (t, f) in dct.get(rb, {}).items():
                    if h <= max_hr:
                        tot[h] += t; fes[h] += f
            return tot, fes

        byR = {}
        t, f = arr_for(RLEVEL_ORDER); byR["全部"] = {"total": t, "festival": f}
        for rb in RLEVEL_ORDER:
            t, f = arr_for([rb]); byR[rb] = {"total": t, "festival": f}
        hourly_data.append({
            "date": day["date"], "day_label": day["day_label"], "byR": byR,
        })

    # ---- 5a2. R级分层累计（D0~当前，节日流水/付费人数/层ARPU；人数整窗去重） ----
    sql_rlevel = f"""
    SELECT {RCLASS} AS rb,
      round(sum({REV_EXPR}),0) AS total_rev,
      round(sum(CASE WHEN {fest_cond} THEN {REV_EXPR} ELSE 0 END),0) AS fest_rev,
      count(distinct o.user_id) AS total_payers,
      count(distinct CASE WHEN {fest_cond} THEN o.user_id END) AS fest_payers
    FROM v1090.ods_user_order o
    LEFT JOIN {rl_join(report_date)} rl ON o.user_id = rl.user_id
    LEFT JOIN {ltv_join(report_date)} lt ON o.user_id = lt.user_id
    WHERE o.pay_status = 1
      AND o.partition_date BETWEEN '{FESTIVAL_D0}' AND '{report_date}'
    {SERVER_FILTER}
    GROUP BY {RCLASS}
    """
    rl_raw = {r["rb"]: r for r in query(sql_rlevel)}
    rlevels_data = []
    for rb in RLEVEL_ORDER:
        r = rl_raw.get(rb)
        rlevels_data.append({
            "rlevel": rb,
            "total": round(float(r["total_rev"] or 0)) if r else 0,
            "festival": round(float(r["fest_rev"] or 0)) if r else 0,
            "payers": int(r["total_payers"] or 0) if r else 0,
            "fest_payers": int(r["fest_payers"] or 0) if r else 0,
        })

    # ---- 5b. 按日同期对比（夏日 Dn 对 情人节 Dn，逐日整日对整日；进行中的当天按已跑小时对齐才公平） ----
    ptm = load_pack_type_map()
    summer_pred = "(o.iap_id IN (" + ",".join(f"'{p}'" for p in pack_ids) + ") AND " + FEST_TIME_GUARD + ")"
    now_date = datetime.now().strftime("%Y-%m-%d")
    # 进行中当天的已跑小时上限（仅 report_date == 今天 时才算"进行中"，否则整日）
    report_max_hr = 23
    if report_date == now_date:
        mh = query(f"SELECT max(hour(o.created_at)) mh FROM v1090.ods_user_order o "
                   f"WHERE o.pay_status=1 AND o.partition_date='{report_date}' {SERVER_FILTER}")
        if mh and mh[0].get("mh") is not None:
            report_max_hr = min(int(mh[0]["mh"]), 23)
    bench_d0 = datetime.strptime(BENCHMARK_D0, "%Y-%m-%d")
    cmp_days = []
    for day in all_days:
        sdate = day["date"]
        dn = day["day_num"]
        vdate = (bench_d0 + timedelta(days=dn)).strftime("%Y-%m-%d")
        partial = (sdate == now_date)
        h0, h1 = 0, (report_max_hr if partial else 23)
        win = f"首{h1 + 1}h" if partial else "整日"
        s = query_window(sdate, summer_pred, h0, h1, ptm)
        v = query_window(vdate, BENCHMARK_FEST_PRED, h0, h1, ptm, sf=SERVER_FILTER_VAL)
        if s and v:
            # R级对打：各期用各期当期快照分类（夏日 as-of sdate，情人节 as-of vdate）
            s_where = f"o.partition_date='{sdate}' AND hour(o.created_at) BETWEEN {h0} AND {h1}"
            v_where = f"o.partition_date='{vdate}' AND hour(o.created_at) BETWEEN {h0} AND {h1}"
            cmp_days.append({
                "day_label": day["day_label"], "win": win,
                "summer_date": sdate, "val_date": vdate,
                "summer": s, "valentine": v,
                "summer_r": query_by_r(s_where, summer_pred, sdate),
                "valentine_r": query_by_r(v_where, BENCHMARK_FEST_PRED, vdate, sf=SERVER_FILTER_VAL),
            })
            for src in (s, v):
                for m in src["modules"]:
                    if m not in module_colors:
                        module_colors[m] = PALETTE[pi % len(PALETTE)]; pi += 1
    compare = None
    if cmp_days:
        # ---- 累计对比（D0 ~ 当前日，整窗去重；进行中当天按首 N 小时对齐） ----
        n_days = len(all_days)
        s_start = all_days[0]["date"]
        s_last = all_days[-1]["date"]
        s_partial = (s_last == now_date)
        s_prev_last = (datetime.strptime(s_last, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        v_start = BENCHMARK_D0
        v_last = (bench_d0 + timedelta(days=n_days - 1)).strftime("%Y-%m-%d")
        v_prev_last = (bench_d0 + timedelta(days=n_days - 2)).strftime("%Y-%m-%d")
        s_pred = cum_date_pred(s_start, s_last, s_prev_last, report_max_hr, s_partial)
        v_pred = cum_date_pred(v_start, v_last, v_prev_last, report_max_hr, s_partial)
        cum_summer = query_cum(s_pred, summer_pred, ptm)
        cum_val = query_cum(v_pred, BENCHMARK_FEST_PRED, ptm, sf=SERVER_FILTER_VAL)
        cumulative = None
        if cum_summer and cum_val:
            win = f"D0~{all_days[-1]['day_label']}" + ("·首{}h".format(report_max_hr + 1) if s_partial else "")
            cum_summer_r = query_by_r(s_pred, summer_pred, s_last)
            cum_val_r = query_by_r(v_pred, BENCHMARK_FEST_PRED, v_last, sf=SERVER_FILTER_VAL)
            cumulative = {
                "day_label": "累计", "win": win,
                "summer_date": f"{s_start}~{s_last}", "val_date": f"{v_start}~{v_last}",
                "summer": cum_summer, "valentine": cum_val,
                "summer_r": cum_summer_r, "valentine_r": cum_val_r,
            }
            for src in (cum_summer, cum_val):
                for m in src["modules"]:
                    if m not in module_colors:
                        module_colors[m] = PALETTE[pi % len(PALETTE)]; pi += 1
        compare = {
            "summer_name": FESTIVAL_NAME, "val_name": BENCHMARK_NAME, "val_d0": BENCHMARK_D0,
            "days": cmp_days, "cumulative": cumulative,
        }

    # ---- 5c. 模块 × R级 对比（累计同期，付费率/ARPU/ARPPU，R级可筛选） ----
    module_rlevel = None
    if compare and compare.get("cumulative"):
        # 情人节节日包 → 模块映射（动态取当期节日 iap 再按 PackType 归模块）
        val_iaps = [str(r["iap_id"]) for r in query(
            f"SELECT distinct o.iap_id FROM v1090.ods_user_order o "
            f"WHERE o.pay_status=1 AND {v_pred} AND {BENCHMARK_FEST_PRED} {SERVER_FILTER_VAL}")]
        val_id2mod = {i: module_of(i, ptm) for i in val_iaps}
        s_modr = query_module_r(s_pred, summer_pred, s_last, build_module_case(pack_module))
        v_modr = query_module_r(v_pred, BENCHMARK_FEST_PRED, v_last, build_module_case(val_id2mod), sf=SERVER_FILTER_VAL)
        mods_union = set()
        for byR in (s_modr, v_modr):
            for rb in byR:
                mods_union.update(byR[rb].keys())
        # 模块排序：按两期合计节日流水降序
        def mod_total(mname):
            t = 0
            for byR in (s_modr, v_modr):
                for rb in byR:
                    if mname in byR[rb]:
                        t += byR[rb][mname]["rev"]
            return t
        mods_sorted = sorted(mods_union, key=lambda mm: -mod_total(mm))
        module_rlevel = {
            "summer_name": FESTIVAL_NAME, "val_name": BENCHMARK_NAME, "win": cumulative["win"],
            "modules": mods_sorted,
            "summer": {"byR": s_modr, "payers": {rb: cum_summer_r[rb]["payers"] for rb in RLEVEL_ORDER}},
            "valentine": {"byR": v_modr, "payers": {rb: cum_val_r[rb]["payers"] for rb in RLEVEL_ORDER}},
        }

    # ---- 6. 生成 HTML ----
    all_days_json = json.dumps(all_days, ensure_ascii=False)
    hourly_json = json.dumps(hourly_data, ensure_ascii=False)
    rlevels_json = json.dumps(rlevels_data, ensure_ascii=False)
    modr_json = json.dumps(module_rlevel, ensure_ascii=False)
    baseline_json = json.dumps(baseline, ensure_ascii=False)
    module_colors_json = json.dumps(module_colors, ensure_ascii=False)
    benchmark_json = json.dumps(compare, ensure_ascii=False)
    bl_total_int = int(baseline["total"])
    bl_total_str = fmt_money(baseline["total"])
    pack_count = len(pack_ids)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>X3{FESTIVAL_NAME}日报 D{day_num}</title>
<style>
  :root {{
    --bg: #0f1117; --surface: #1a1d27; --surface2: #222536; --border: #2e3248;
    --accent: #6c63ff; --accent2: #00d4aa; --accent3: #ff6b6b; --accent4: #ffd166;
    --text: #e2e8f0; --text-muted: #8892a4; --green: #22c55e; --orange: #f97316; --red: #ef4444;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; font-size: 14px; }}
  .header {{ background: linear-gradient(135deg, #1a1d27 0%, #0f1117 100%); border-bottom: 1px solid var(--border); padding: 28px 40px 20px; }}
  .header h1 {{ font-size: 24px; font-weight: 700; }}
  .header h1 .hl {{ color: var(--accent); }}
  .meta-row {{ margin-top: 6px; display: flex; gap: 20px; font-size: 12px; color: var(--text-muted); }}
  .meta-row b {{ color: var(--text); }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 28px 40px 60px; }}
  .section {{ margin-bottom: 36px; }}
  .section-title {{ font-size: 14px; font-weight: 700; color: var(--accent); border-left: 3px solid var(--accent); padding-left: 10px; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; }}
  .day-tabs {{ display: flex; gap: 0; margin-bottom: 24px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; flex-wrap: wrap; }}
  .day-tab {{ flex: 1; min-width: 70px; padding: 12px 0; text-align: center; cursor: pointer; font-size: 13px; font-weight: 600; color: var(--text-muted); border-right: 1px solid var(--border); transition: all .15s; }}
  .day-tab:last-child {{ border-right: none; }}
  .day-tab:hover {{ background: var(--surface2); color: var(--text); }}
  .day-tab.active {{ background: var(--accent); color: #fff; }}
  .day-tab .day-date {{ font-size: 10px; font-weight: 400; opacity: .7; display: block; margin-top: 2px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }}
  .kpi-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 18px; border-top: 3px solid var(--accent); }}
  .kpi-label {{ font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .8px; }}
  .kpi-value {{ font-size: 24px; font-weight: 800; margin: 4px 0 2px; font-variant-numeric: tabular-nums; }}
  .kpi-change {{ font-size: 12px; }}
  .up {{ color: var(--green); }} .down {{ color: var(--red); }} .muted {{ color: var(--text-muted); }}
  .row-2col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .table-wrap {{ border-radius: 10px; border: 1px solid var(--border); overflow: hidden; }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{ background: var(--surface2); padding: 10px 14px; font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .6px; border-bottom: 1px solid var(--border); text-align: left; white-space: nowrap; }}
  tbody td {{ padding: 10px 14px; border-bottom: 1px solid var(--border); }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover {{ background: rgba(108,99,255,.05); }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .conclusion {{ margin-top: 10px; padding: 10px 14px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; font-size: 13px; }}
  .mod-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
  .mod-name {{ width: 96px; font-size: 12px; color: var(--text-muted); text-align: right; flex-shrink: 0; }}
  .mod-bar-wrap {{ flex: 1; background: var(--surface2); border-radius: 4px; height: 24px; }}
  .mod-bar {{ height: 100%; border-radius: 4px; min-width: 2px; transition: width .25s; }}
  .mod-val {{ width: 64px; font-size: 13px; font-variant-numeric: tabular-nums; text-align: right; flex-shrink: 0; font-weight: 600; }}
  .mod-pct {{ width: 36px; font-size: 11px; color: var(--text-muted); text-align: right; flex-shrink: 0; }}
  .mod-chg {{ width: 56px; font-size: 11px; text-align: right; flex-shrink: 0; }}
  .mod-hdr {{ display: flex; gap: 10px; font-size: 10px; color: var(--text-muted); margin-bottom: 10px; padding-left: 106px; }}
  .mod-hdr span {{ text-align: right; }}
  .chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .chart-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }}
  .chart-label {{ font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }}
  canvas {{ width: 100%; display: block; }}
  .canvas-200 {{ height: 200px; }} .canvas-220 {{ height: 220px; }} .canvas-280 {{ height: 280px; }}
  .mod-tabs {{ display: flex; gap: 4px; margin-bottom: 14px; flex-wrap: wrap; }}
  .mod-tab {{ padding: 6px 16px; border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--text-muted); font-size: 12px; font-weight: 600; cursor: pointer; transition: all .15s; }}
  .mod-tab:hover {{ background: var(--surface2); color: var(--text); }}
  .mod-tab.active {{ color: #fff; border-color: transparent; }}
  .alert {{ padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; font-size: 13px; display: flex; align-items: flex-start; gap: 8px; }}
  .alert-icon {{ flex-shrink: 0; }}
  .alert-warn {{ background: rgba(249,115,22,.08); border: 1px solid rgba(249,115,22,.2); }}
  .alert-info {{ background: rgba(108,99,255,.06); border: 1px solid rgba(108,99,255,.15); }}
  .footer {{ text-align: center; color: var(--text-muted); font-size: 11px; padding: 20px 0; }}
</style>
</head>
<body>
<div class="header">
  <h1>X3 <span class="hl">{FESTIVAL_NAME}</span> 日报</h1>
  <div class="meta-row">
    <span>{SERVER_LABEL}</span>
    <span>基线 {BASELINE_START} ~ {BASELINE_END} (14日均值)</span>
    <span>生成于 {datetime.now().strftime("%H:%M")}</span>
  </div>
</div>
<div class="container">
  <div class="day-tabs" id="dayTabs"></div>
  <div class="section"><div class="kpi-grid" id="kpiGrid"></div></div>
  <div class="section row-2col">
    <div>
      <div class="section-title">ARPU 增量分析</div>
      <div class="table-wrap"><table>
        <thead><tr><th>指标</th><th class="num">当日</th><th class="num">基线</th><th class="num">净增</th></tr></thead>
        <tbody id="arpuBody"></tbody>
      </table></div>
      <div class="conclusion" id="arpuConclusion"></div>
    </div>
    <div>
      <div class="section-title">节日模块构成</div>
      <div class="mod-hdr"><span>模块</span><span style="flex:1"></span><span style="width:64px">当日</span><span style="width:36px">占比</span><span style="width:56px">环比</span></div>
      <div id="modBars"></div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">节日模块构成 · 全程累计总量</div>
    <div class="mod-hdr"><span>模块</span><span style="flex:1"></span><span style="width:64px">累计</span><span style="width:36px">占比</span><span style="width:56px">日均</span></div>
    <div id="modTotalBars"></div>
    <div class="conclusion" id="modTotalNote" style="margin-top:12px"></div>
  </div>
  <div class="section">
    <div class="section-title">每日流水趋势</div>
    <div class="chart-row">
      <div class="chart-box"><div class="chart-label">总流水</div><canvas id="totalChart" class="canvas-200"></canvas></div>
      <div class="chart-box"><div class="chart-label">节日流水（独立坐标轴）· 点下标注当日占比(节日/总流水)</div><canvas id="festChart" class="canvas-200"></canvas></div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">模块变化趋势</div>
    <div class="chart-box"><div class="mod-tabs" id="modTabs"></div><canvas id="modTrendChart" class="canvas-220"></canvas></div>
  </div>
  <div class="section">
    <div class="section-title">分时收入趋势</div>
    <div class="chart-box">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap">
        <span style="font-size:11px;color:var(--text-muted);flex-shrink:0">R级筛选</span>
        <div class="mod-tabs" id="hrRFilter" style="margin-bottom:0"></div>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px">
        <div class="mod-tabs" id="hrDayChips" style="margin-bottom:0"></div>
        <div class="mod-tabs" id="hrModeToggle" style="margin-bottom:0"></div>
      </div>
      <div id="hrLegend" style="display:flex;gap:18px;flex-wrap:wrap;font-size:11px;color:var(--text-muted);margin-bottom:6px"></div>
      <canvas id="hourlyChart" class="canvas-280"></canvas>
      <div style="margin-top:18px;border-top:1px solid var(--border);padding-top:14px">
        <div class="chart-label" style="margin-bottom:8px">D0–D3 全程分时（总流水实线 / 节日虚线，随上方「每时 · 累计」与「R级筛选」切换）</div>
        <canvas id="hourlyAllChart" class="canvas-280"></canvas>
      </div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">节日收入 · R级分层（累计到当前）</div>
    <div class="mod-hdr"><span>R级</span><span style="flex:1"></span><span style="width:64px">节日累计</span><span style="width:36px">占比</span><span style="width:56px">付费人数</span><span style="width:64px">层节日ARPU</span></div>
    <div id="rlevelBars"></div>
    <div class="conclusion" id="rlevelNote" style="margin-top:12px"></div>
  </div>
  <div class="section" id="rgainSection" style="display:none">
    <div class="section-title">R级付费玩家付费率 & ARPU · 本期 vs 上期<span id="rgainName"></span>（累计同期·排除免费玩家）</div>
    <div class="conclusion" id="rgainNote" style="margin-bottom:14px"></div>
    <div class="table-wrap"><table>
      <thead><tr>
        <th>R级</th>
        <th class="num">总付费人数<br>上→本</th>
        <th class="num">付费玩家付费率<br>上→本</th>
        <th class="num">付费ARPU<br>上→本</th>
        <th class="num">ARPPU<br>上→本</th>
        <th class="num">节日流水<br>上→本</th>
      </tr></thead>
      <tbody id="rgainBody"></tbody>
    </table></div>
    <div class="chart-label" style="margin-top:8px;font-size:11px">付费玩家付费率 = 节日付费人数 / 当期总付费人数（分母仅付费玩家，排除非R免费玩家占比干扰）；付费ARPU = 节日流水 / 总付费人数；ARPPU = 节日流水 / 节日付费人数。同期窗口 = 累计 D0~当前（进行中当天首 N 小时两边对齐）。↑绿=本期更高。<br>R级口径：分级表快照优先；分级表漏收的付费用户按累充(USD)估档（≥$1500超R/≥$500大R/≥$50中R/&gt;0小R）。非R 为零充免费玩家、无付费，本表已剔除。</div>
  </div>
  <div class="section" id="modrSection" style="display:none">
    <div class="section-title">节日模块 · R级对比 · 本期 vs 上期<span id="modrName"></span>（付费率 / ARPU / ARPPU）</div>
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap">
      <span style="font-size:11px;color:var(--text-muted);flex-shrink:0">R级筛选</span>
      <div class="mod-tabs" id="modrFilter" style="margin-bottom:0"></div>
    </div>
    <div class="conclusion" id="modrNote" style="margin-bottom:14px"></div>
    <div class="table-wrap"><table>
      <thead><tr>
        <th>模块</th>
        <th class="num">付费率 上→本</th>
        <th class="num">ARPU 上→本</th>
        <th class="num">ARPPU 上→本</th>
        <th class="num">节日流水 上→本</th>
      </tr></thead>
      <tbody id="modrBody"></tbody>
    </table></div>
    <div class="chart-label" style="margin-top:8px;font-size:11px">选定 R级下：付费率 = 买该模块人数 / 该R级总付费人数；ARPU = 模块节日流水 / 该R级总付费人数；ARPPU = 模块节日流水 / 买该模块人数。「全部」= 付费档合计。同期窗口 = 累计 D0~当前（进行中当天首 N 小时两边对齐）。↑绿=本期更高。</div>
  </div>
  <div class="section" id="compareSection" style="display:none">
    <div class="section-title">按日同期对比 · 本期 vs 上期<span id="cmpName"></span>（D 对 D，逐日同序对齐）</div>
    <div class="day-tabs" id="cmpDayTabs" style="margin-bottom:18px"></div>
    <div class="conclusion" id="cmpNote" style="margin-bottom:14px"></div>
    <div class="table-wrap" style="margin-bottom:18px"><table>
      <thead><tr><th id="cmpHdr">指标</th><th class="num" id="cmpColA"></th><th class="num" id="cmpColB"></th><th class="num">差异</th></tr></thead>
      <tbody id="cmpBody"></tbody>
    </table></div>
    <div class="row-2col">
      <div><div class="chart-label" id="cmpModBLabel" style="font-weight:600"></div><div class="mod-hdr"><span>模块</span><span style="flex:1"></span><span style="width:64px">收入</span><span style="width:36px">占比</span></div><div id="cmpModB"></div></div>
      <div><div class="chart-label" id="cmpModALabel" style="font-weight:600"></div><div class="mod-hdr"><span>模块</span><span style="flex:1"></span><span style="width:64px">收入</span><span style="width:36px">占比</span></div><div id="cmpModA"></div></div>
    </div>
    <div id="cmpRSection" style="margin-top:20px;display:none">
      <div class="chart-label" style="font-weight:600;margin-bottom:8px">R级对打 · 节日流水 / 层ARPU（上期情人节 → 本期夏日，各期按当期 R级档位）</div>
      <div class="table-wrap"><table>
        <thead><tr><th>R级</th><th class="num" id="cmpRColV"></th><th class="num" id="cmpRColS"></th><th class="num">节日Δ</th><th class="num" id="cmpRArpuV"></th><th class="num" id="cmpRArpuS"></th></tr></thead>
        <tbody id="cmpRBody"></tbody>
      </table></div>
    </div>
  </div>
  <div class="section">
    <div class="section-title">关注点</div>
    <div id="alertsBox"></div>
  </div>
</div>
<div class="footer">X3 {FESTIVAL_NAME} | 数据口径：{SERVER_LABEL}，节日收入 = ActvOnline {RECHARGE_ACTV_ID} 累充白名单 {pack_count} 个 Pack（USD口径，pay_status=1）；模块按 Pack.PackType 归类</div>
<script>
const allDays = {all_days_json};
const hourly = {hourly_json};
const rlevels = {rlevels_json};
const moduleR = {modr_json};
const baseline = {baseline_json};
const modColors = {module_colors_json};
const compare = {benchmark_json};
const dpr = window.devicePixelRatio || 1;
let currentDayIdx = allDays.length - 1;
let currentMod = null;
const dayPalette = ['#6c63ff', '#00d4aa', '#ff6b6b', '#ffd166', '#a78bfa', '#38bdf8', '#fb923c', '#22c55e'];
let hrSelDays = new Set([hourly.length - 1]);  // 默认选最新一天
let hrMode = 'hourly';  // 'hourly' 每时 | 'cum' 累计
let currentR = '全部';  // 分时图 R级筛选：全部/超R/大R/中R/小R/非R
let currentModR = '全部';  // 模块×R级对比的 R级筛选
const rLevelColors = {{ '全部': '#6c63ff', '超R': '#f43f5e', '大R': '#fb923c', '中R': '#ffd166', '小R': '#38bdf8', '非R': '#8892a4' }};
let cmpDayIdx = 0;  // 按日对比当前选中的节日日序

function $(id) {{ return document.getElementById(id); }}
function fmtMoney(v) {{ return v >= 1000 ? '$' + v.toLocaleString('en-US', {{maximumFractionDigits:0}}) : '$' + Math.round(v); }}
function fmtPct(v) {{ if (v == null || v === 0) return '—'; return (v > 0 ? '+' : '') + v.toFixed(1) + '%'; }}
function fmtDelta(v) {{ return (v >= 0 ? '+$' : '-$') + Math.abs(v).toFixed(2); }}
function pctChg(a, b) {{ return b ? (a - b) / b * 100 : null; }}

function buildDayTabs() {{
  const el = $('dayTabs'); el.innerHTML = '';
  allDays.forEach((d, i) => {{
    const div = document.createElement('div');
    div.className = 'day-tab' + (i === currentDayIdx ? ' active' : '');
    div.innerHTML = d.day_label + '<span class="day-date">' + d.date + '</span>';
    div.onclick = () => {{ currentDayIdx = i; renderAll(); }};
    el.appendChild(div);
  }});
}}

function renderKPI() {{
  const d = allDays[currentDayIdx];
  const prev = currentDayIdx > 0 ? allDays[currentDayIdx - 1] : null;
  const cum_total = allDays.slice(0, currentDayIdx + 1).reduce((s, x) => s + x.total, 0);
  const cum_fest = allDays.slice(0, currentDayIdx + 1).reduce((s, x) => s + x.festival, 0);
  const festRatio = cum_total > 0 ? (cum_fest / cum_total * 100) : 0;
  const items = [
    {{ label: '总流水', value: fmtMoney(d.total), chg: prev ? pctChg(d.total, prev.total) : null, color: 'var(--accent)' }},
    {{ label: '付费人数', value: d.payers, chg: prev ? pctChg(d.payers, prev.payers) : null, color: 'var(--accent2)' }},
    {{ label: '节日流水', value: fmtMoney(d.festival), chg: prev ? pctChg(d.festival, prev.festival) : null, color: 'var(--accent4)' }},
    {{ label: '非节日流水', value: fmtMoney(d.non_festival), chg: prev ? pctChg(d.non_festival, prev.non_festival) : null, color: 'var(--green)' }},
    {{ label: '节日累计流水', value: fmtMoney(cum_fest), chg: null, sub: 'D0~' + d.day_label, color: 'var(--accent3)' }},
    {{ label: '节日累计占比', value: festRatio.toFixed(1) + '%', chg: null, sub: fmtMoney(cum_fest) + ' / ' + fmtMoney(cum_total), color: 'var(--orange)' }},
  ];
  $('kpiGrid').innerHTML = items.map(it => {{
    const chgCls = it.chg == null ? 'muted' : it.chg > 0 ? 'up' : it.chg < 0 ? 'down' : 'muted';
    const chgStr = it.chg != null ? fmtPct(it.chg) + ' vs 昨日' : (it.sub || 'D0~' + d.day_label);
    return '<div class="kpi-card" style="border-top-color:' + it.color + '"><div class="kpi-label">' + it.label + '</div><div class="kpi-value">' + it.value + '</div><div class="kpi-change ' + chgCls + '">' + chgStr + '</div></div>';
  }}).join('');
}}

function renderARPU() {{
  const d = allDays[currentDayIdx];
  const fa = d.festival / Math.max(d.payers, 1), nfa = d.non_festival / Math.max(d.payers, 1), ta = d.total / Math.max(d.payers, 1);
  const rows = [['节日 ARPU', fa, 0, fa], ['非节日 ARPU', nfa, baseline.arpu_nonfest, nfa - baseline.arpu_nonfest], ['综合 ARPU', ta, baseline.arpu_total, ta - baseline.arpu_total]];
  $('arpuBody').innerHTML = rows.map(r => {{
    const cls = r[3] > 0.5 ? 'up' : r[3] < -0.5 ? 'down' : 'muted';
    return '<tr><td>' + r[0] + '</td><td class="num">$' + r[1].toFixed(2) + '</td><td class="num muted">$' + r[2].toFixed(2) + '</td><td class="num ' + cls + '">' + fmtDelta(r[3]) + '</td></tr>';
  }}).join('');
  const nfD = nfa - baseline.arpu_nonfest; let c, cl;
  if (nfD > 1) {{ c = '节日纯增量 +$' + fa.toFixed(2) + '/人，非节日被带动 +$' + nfD.toFixed(2) + '/人'; cl = 'up'; }}
  else if (nfD < -1) {{ c = '节日纯增量 +$' + fa.toFixed(2) + '/人，非节日被挤占 ' + fmtDelta(nfD) + '/人'; cl = 'down'; }}
  else {{ c = '节日纯增量 +$' + fa.toFixed(2) + '/人，非节日基本持平'; cl = 'muted'; }}
  $('arpuConclusion').className = 'conclusion ' + cl; $('arpuConclusion').textContent = c;
}}

function renderModBars() {{
  const d = allDays[currentDayIdx], prev = currentDayIdx > 0 ? allDays[currentDayIdx - 1] : null;
  const mods = d.modules, modNames = Object.keys(mods).sort((a, b) => mods[b] - mods[a]);
  const maxRev = Math.max(...Object.values(mods), 1), modTotal = Object.values(mods).reduce((s, v) => s + v, 0);
  $('modBars').innerHTML = modNames.map(m => {{
    const rev = mods[m], pct = modTotal > 0 ? rev / modTotal * 100 : 0, barW = rev / maxRev * 100;
    const color = modColors[m] || '#8892a4', prevRev = prev ? (prev.modules[m] || 0) : 0;
    const chg = pctChg(rev, prevRev), chgCls = chg != null ? (chg > 0 ? 'up' : 'down') : 'muted';
    return '<div class="mod-row"><div class="mod-name">' + m + '</div><div class="mod-bar-wrap"><div class="mod-bar" style="width:' + barW.toFixed(1) + '%;background:' + color + '"></div></div><div class="mod-val">' + fmtMoney(rev) + '</div><div class="mod-pct">' + pct.toFixed(0) + '%</div><div class="mod-chg"><span class="' + chgCls + '">' + (chg != null ? fmtPct(chg) : '—') + '</span></div></div>';
  }}).join('');
}}

function drawTrend(canvasId, key, color, areaColor, blVal, blLabel, showPct) {{
  const canvas = $(canvasId), W0 = canvas.offsetWidth, H = 200;
  canvas.width = W0 * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);
  const pad = {{ top: 20, right: 16, bottom: 32, left: 52 }};
  const cW = W0 - pad.left - pad.right, cH = H - pad.top - pad.bottom;
  const series = allDays.map(d => d[key]), n = series.length, maxVal = Math.max(...series, 1) * 1.3;
  function xp(i) {{ return pad.left + (n > 1 ? i / (n - 1) * cW : cW / 2); }}
  function yp(v) {{ return pad.top + cH - (v / maxVal * cH); }}
  ctx.strokeStyle = '#2e3248'; ctx.lineWidth = 0.5;
  for (let i = 0; i <= 4; i++) {{ const yy = pad.top + cH * i / 4; ctx.beginPath(); ctx.moveTo(pad.left, yy); ctx.lineTo(W0 - pad.right, yy); ctx.stroke(); ctx.fillStyle = '#8892a4'; ctx.font = '10px -apple-system,sans-serif'; ctx.textAlign = 'right'; ctx.fillText('$' + Math.round(maxVal * (4 - i) / 4).toLocaleString(), pad.left - 6, yy + 3); }}
  if (blVal > 0) {{ const blY = yp(blVal); ctx.setLineDash([4,4]); ctx.strokeStyle = '#f97316'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(pad.left, blY); ctx.lineTo(W0 - pad.right, blY); ctx.stroke(); ctx.setLineDash([]); ctx.fillStyle = '#f97316'; ctx.font = '10px -apple-system,sans-serif'; ctx.textAlign = 'right'; ctx.fillText(blLabel, W0 - pad.right, blY - 5); }}
  ctx.beginPath(); ctx.moveTo(xp(0), yp(series[0])); for (let i = 1; i < n; i++) ctx.lineTo(xp(i), yp(series[i])); ctx.lineTo(xp(n-1), yp(0)); ctx.lineTo(xp(0), yp(0)); ctx.closePath(); ctx.fillStyle = areaColor; ctx.fill();
  ctx.beginPath(); ctx.moveTo(xp(0), yp(series[0])); for (let i = 1; i < n; i++) ctx.lineTo(xp(i), yp(series[i])); ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
  for (let i = 0; i < n; i++) {{ const sel = (i === currentDayIdx), r = sel ? 6 : 4; ctx.beginPath(); ctx.arc(xp(i), yp(series[i]), r, 0, Math.PI * 2); ctx.fillStyle = color; ctx.fill(); ctx.strokeStyle = sel ? '#fff' : '#1a1d27'; ctx.lineWidth = sel ? 2.5 : 2; ctx.stroke(); ctx.fillStyle = sel ? '#fff' : '#e2e8f0'; ctx.font = (sel ? 'bold 12px' : '11px') + ' -apple-system,sans-serif'; ctx.textAlign = 'center'; ctx.fillText('$' + series[i].toLocaleString(), xp(i), yp(series[i]) - (sel ? 16 : 12)); ctx.fillStyle = sel ? '#fff' : '#8892a4'; ctx.font = (sel ? 'bold ' : '') + '10px -apple-system,sans-serif'; ctx.fillText(allDays[i].day_label, xp(i), H - pad.bottom + 14); if (showPct) {{ const tot = allDays[i].total || 0, pct = tot ? (allDays[i].festival / tot * 100) : 0; ctx.fillStyle = sel ? '#ffd166' : '#caa84a'; ctx.font = (sel ? 'bold ' : '') + '10px -apple-system,sans-serif'; ctx.textAlign = 'center'; ctx.fillText('占比 ' + pct.toFixed(0) + '%', xp(i), yp(series[i]) + 16); }} }}
}}

function buildModTabs() {{
  const mods = Object.keys(allDays[0].modules);
  let best = mods[0], bestSum = 0;
  mods.forEach(m => {{ const s = allDays.reduce((a, d) => a + (d.modules[m] || 0), 0); if (s > bestSum) {{ bestSum = s; best = m; }} }});
  currentMod = currentMod || best;
  const el = $('modTabs'); el.innerHTML = '';
  mods.sort((a, b) => {{ const sa = allDays.reduce((a2, d) => a2 + (d.modules[a] || 0), 0), sb = allDays.reduce((a2, d) => a2 + (d.modules[b] || 0), 0); return sb - sa; }});
  mods.forEach(m => {{ const btn = document.createElement('div'); btn.className = 'mod-tab' + (m === currentMod ? ' active' : ''); btn.style.background = m === currentMod ? (modColors[m] || '#8892a4') : ''; btn.style.borderColor = m === currentMod ? 'transparent' : ''; btn.textContent = m; btn.onclick = () => {{ currentMod = m; buildModTabs(); drawModTrend(); }}; el.appendChild(btn); }});
}}

function drawModTrend() {{
  const mod = currentMod, series = allDays.map(d => d.modules[mod] || 0), color = modColors[mod] || '#8892a4';
  const canvas = $('modTrendChart'), W0 = canvas.offsetWidth, H = 220;
  canvas.width = W0 * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);
  const pad = {{ top: 28, right: 20, bottom: 32, left: 52 }}, cW = W0 - pad.left - pad.right, cH = H - pad.top - pad.bottom;
  const n = series.length, maxVal = Math.max(...series, 1) * 1.35;
  function xp(i) {{ return pad.left + (n > 1 ? i / (n - 1) * cW : cW / 2); }}
  function yp(v) {{ return pad.top + cH - (v / maxVal * cH); }}
  ctx.strokeStyle = '#2e3248'; ctx.lineWidth = 0.5;
  for (let i = 0; i <= 4; i++) {{ const yy = pad.top + cH * i / 4; ctx.beginPath(); ctx.moveTo(pad.left, yy); ctx.lineTo(W0 - pad.right, yy); ctx.stroke(); ctx.fillStyle = '#8892a4'; ctx.font = '10px -apple-system,sans-serif'; ctx.textAlign = 'right'; ctx.fillText('$' + Math.round(maxVal * (4 - i) / 4).toLocaleString(), pad.left - 6, yy + 3); }}
  ctx.beginPath(); ctx.moveTo(xp(0), yp(series[0])); for (let i = 1; i < n; i++) ctx.lineTo(xp(i), yp(series[i])); ctx.lineTo(xp(n-1), yp(0)); ctx.lineTo(xp(0), yp(0)); ctx.closePath();
  const grad = ctx.createLinearGradient(0, pad.top, 0, H - pad.bottom); grad.addColorStop(0, color + '30'); grad.addColorStop(1, color + '05'); ctx.fillStyle = grad; ctx.fill();
  ctx.beginPath(); ctx.moveTo(xp(0), yp(series[0])); for (let i = 1; i < n; i++) ctx.lineTo(xp(i), yp(series[i])); ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
  for (let i = 0; i < n; i++) {{ const sel = (i === currentDayIdx), r = sel ? 6 : 4; ctx.beginPath(); ctx.arc(xp(i), yp(series[i]), r, 0, Math.PI * 2); ctx.fillStyle = color; ctx.fill(); ctx.strokeStyle = sel ? '#fff' : '#1a1d27'; ctx.lineWidth = sel ? 2.5 : 2; ctx.stroke(); ctx.fillStyle = sel ? '#fff' : '#e2e8f0'; ctx.font = (sel ? 'bold 12px' : 'bold 11px') + ' -apple-system,sans-serif'; ctx.textAlign = 'center'; ctx.fillText('$' + series[i].toLocaleString(), xp(i), yp(series[i]) - 18); if (i > 0 && series[i-1] > 0) {{ const chg = (series[i] - series[i-1]) / series[i-1] * 100; ctx.fillStyle = chg >= 0 ? '#22c55e' : '#ef4444'; ctx.font = '10px -apple-system,sans-serif'; ctx.fillText((chg >= 0 ? '+' : '') + chg.toFixed(0) + '%', xp(i), yp(series[i]) - 30); }} ctx.fillStyle = sel ? '#fff' : '#8892a4'; ctx.font = (sel ? 'bold ' : '') + '11px -apple-system,sans-serif'; ctx.fillText(allDays[i].day_label, xp(i), H - pad.bottom + 16); }}
  const cum = series.reduce((a, b) => a + b, 0); ctx.fillStyle = color; ctx.font = 'bold 13px -apple-system,sans-serif'; ctx.textAlign = 'left'; ctx.fillText(mod, pad.left, 18); ctx.fillStyle = '#8892a4'; ctx.font = '12px -apple-system,sans-serif'; ctx.fillText('累计 $' + cum.toLocaleString(), pad.left + ctx.measureText(mod + '  ').width + 8, 18);
}}

function hrSeries(dayIdx, key) {{
  const byR = hourly[dayIdx] && hourly[dayIdx].byR, slot = byR && (byR[currentR] || byR['全部']);
  const arr = (slot && slot[key]) ? slot[key].slice() : [];
  if (hrMode === 'cum') {{ let s = 0; for (let i = 0; i < arr.length; i++) {{ s += arr[i]; arr[i] = s; }} }}
  return arr;
}}

function buildHrChips() {{
  const el = $('hrDayChips'); el.innerHTML = '';
  hourly.forEach((h, i) => {{
    const on = hrSelDays.has(i), color = dayPalette[i % dayPalette.length];
    const btn = document.createElement('div');
    btn.className = 'mod-tab' + (on ? ' active' : '');
    if (on) {{ btn.style.background = color; btn.style.borderColor = 'transparent'; }}
    btn.textContent = h.day_label;
    btn.onclick = () => {{
      if (hrSelDays.has(i)) {{ if (hrSelDays.size > 1) hrSelDays.delete(i); }} else hrSelDays.add(i);
      buildHrChips(); drawHourly();
    }};
    el.appendChild(btn);
  }});
}}

function buildHrModeToggle() {{
  const el = $('hrModeToggle'); el.innerHTML = '';
  [['hourly', '每时'], ['cum', '累计']].forEach(([k, label]) => {{
    const on = hrMode === k, btn = document.createElement('div');
    btn.className = 'mod-tab' + (on ? ' active' : '');
    if (on) {{ btn.style.background = 'var(--accent)'; btn.style.borderColor = 'transparent'; }}
    btn.textContent = label;
    btn.onclick = () => {{ hrMode = k; buildHrModeToggle(); drawHourly(); drawHourlyAll(); }};
    el.appendChild(btn);
  }});
}}

function drawHourly() {{
  const sel = [...hrSelDays].sort((a, b) => a - b);
  // 图例
  $('hrLegend').innerHTML = sel.map(i => {{
    const c = dayPalette[i % dayPalette.length], lab = hourly[i].day_label;
    return '<span><span style="display:inline-block;width:18px;height:0;border-top:2.5px solid ' + c + ';vertical-align:middle;margin-right:5px"></span>' + lab + ' 总流水</span>'
      + '<span><span style="display:inline-block;width:18px;height:0;border-top:2px dashed ' + c + ';vertical-align:middle;margin-right:5px"></span>' + lab + ' 节日</span>';
  }}).join('') + '<span style="margin-left:auto">' + (currentR === '全部' ? '' : 'R级：' + currentR + ' · ') + (hrMode === 'cum' ? '当日累计流水（按小时）' : '每小时流水') + '</span>';

  const canvas = $('hourlyChart'), W0 = canvas.offsetWidth, H = 280;
  canvas.width = W0 * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);
  const pad = {{ top: 16, right: 20, bottom: 30, left: 56 }};
  const cW = W0 - pad.left - pad.right, cH = H - pad.top - pad.bottom;
  const HOURS = 24;
  let maxVal = 1;
  sel.forEach(i => {{ ['total', 'festival'].forEach(k => {{ const s = hrSeries(i, k); s.forEach(v => {{ if (v > maxVal) maxVal = v; }}); }}); }});
  maxVal *= 1.15;
  function xp(h) {{ return pad.left + h / (HOURS - 1) * cW; }}
  function yp(v) {{ return pad.top + cH - (v / maxVal * cH); }}
  // 网格 + y 轴
  ctx.strokeStyle = '#2e3248'; ctx.lineWidth = 0.5;
  for (let g = 0; g <= 4; g++) {{ const yy = pad.top + cH * g / 4; ctx.beginPath(); ctx.moveTo(pad.left, yy); ctx.lineTo(W0 - pad.right, yy); ctx.stroke(); ctx.fillStyle = '#8892a4'; ctx.font = '10px -apple-system,sans-serif'; ctx.textAlign = 'right'; ctx.fillText('$' + Math.round(maxVal * (4 - g) / 4).toLocaleString(), pad.left - 6, yy + 3); }}
  // x 轴小时刻度（每 3h）
  ctx.fillStyle = '#8892a4'; ctx.font = '10px -apple-system,sans-serif'; ctx.textAlign = 'center';
  for (let h = 0; h < HOURS; h += 3) ctx.fillText(h + ':00', xp(h), H - pad.bottom + 16);
  // 画线
  function drawLine(series, color, dashed) {{
    if (!series.length) return;
    ctx.beginPath();
    for (let h = 0; h < series.length; h++) {{ const x = xp(h), y = yp(series[h]); if (h === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }}
    ctx.strokeStyle = color; ctx.lineWidth = dashed ? 2 : 2.5;
    ctx.setLineDash(dashed ? [5, 4] : []); ctx.stroke(); ctx.setLineDash([]);
    // 末端标值
    const last = series.length - 1;
    ctx.fillStyle = color; ctx.font = 'bold 10px -apple-system,sans-serif'; ctx.textAlign = 'left';
    ctx.fillText('$' + series[last].toLocaleString(), Math.min(xp(last) + 5, W0 - pad.right - 36), yp(series[last]) - 2);
  }}
  sel.forEach(i => {{ const c = dayPalette[i % dayPalette.length]; drawLine(hrSeries(i, 'festival'), c, true); drawLine(hrSeries(i, 'total'), c, false); }});
}}

function hrAllSeries(key) {{
  const out = []; let cum = 0;
  hourly.forEach(h => {{ const slot = h.byR[currentR] || h.byR['全部']; (slot[key] || []).forEach(v => {{ if (hrMode === 'cum') {{ cum += v; out.push(cum); }} else out.push(v); }}); }});
  return out;
}}

function drawHourlyAll() {{
  const total = hrAllSeries('total'), fest = hrAllSeries('festival'), N = total.length;
  if (!N) return;
  // 各天边界（按各天已有的小时数累计）
  const bounds = []; let acc = 0;
  hourly.forEach(h => {{ const len = h.byR['全部'].total.length; bounds.push({{ label: h.day_label, start: acc, len: len }}); acc += len; }});
  const canvas = $('hourlyAllChart'), W0 = canvas.offsetWidth, H = 280;
  canvas.width = W0 * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext('2d'); ctx.scale(dpr, dpr);
  const pad = {{ top: 16, right: 20, bottom: 30, left: 56 }};
  const cW = W0 - pad.left - pad.right, cH = H - pad.top - pad.bottom;
  let maxVal = Math.max(...total, ...fest, 1) * 1.15;
  function xp(i) {{ return pad.left + (N > 1 ? i / (N - 1) * cW : cW / 2); }}
  function yp(v) {{ return pad.top + cH - (v / maxVal * cH); }}
  // 网格 + y 轴
  ctx.strokeStyle = '#2e3248'; ctx.lineWidth = 0.5;
  for (let g = 0; g <= 4; g++) {{ const yy = pad.top + cH * g / 4; ctx.beginPath(); ctx.moveTo(pad.left, yy); ctx.lineTo(W0 - pad.right, yy); ctx.stroke(); ctx.fillStyle = '#8892a4'; ctx.font = '10px -apple-system,sans-serif'; ctx.textAlign = 'right'; ctx.fillText('$' + Math.round(maxVal * (4 - g) / 4).toLocaleString(), pad.left - 6, yy + 3); }}
  // 日界分隔线 + 标签
  bounds.forEach((b, bi) => {{
    if (bi > 0) {{ const x = xp(b.start); ctx.strokeStyle = '#3a3f5a'; ctx.lineWidth = 1; ctx.setLineDash([3, 3]); ctx.beginPath(); ctx.moveTo(x, pad.top); ctx.lineTo(x, H - pad.bottom); ctx.stroke(); ctx.setLineDash([]); }}
    const midX = xp(b.start + Math.max(b.len - 1, 0) / 2);
    ctx.fillStyle = '#8892a4'; ctx.font = 'bold 11px -apple-system,sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(b.label, midX, H - pad.bottom + 16);
  }});
  function drawLine(series, color, dashed) {{
    ctx.beginPath();
    for (let i = 0; i < series.length; i++) {{ const x = xp(i), y = yp(series[i]); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }}
    ctx.strokeStyle = color; ctx.lineWidth = dashed ? 2 : 2.5;
    ctx.setLineDash(dashed ? [5, 4] : []); ctx.stroke(); ctx.setLineDash([]);
    const last = series.length - 1;
    ctx.fillStyle = color; ctx.font = 'bold 11px -apple-system,sans-serif'; ctx.textAlign = 'right';
    ctx.fillText('$' + series[last].toLocaleString(), W0 - pad.right, yp(series[last]) - 4);
  }}
  drawLine(fest, '#ffd166', true);
  drawLine(total, '#6c63ff', false);
  // 图例
  ctx.textAlign = 'left'; ctx.font = '11px -apple-system,sans-serif';
  ctx.fillStyle = '#6c63ff'; ctx.fillText('— 总流水', pad.left, pad.top + 4);
  ctx.fillStyle = '#ffd166'; ctx.fillText('-- 节日流水', pad.left + 70, pad.top + 4);
}}

function buildRFilter() {{
  const el = $('hrRFilter'); el.innerHTML = '';
  ['全部', '超R', '大R', '中R', '小R', '非R'].forEach(rl => {{
    const on = currentR === rl, btn = document.createElement('div');
    btn.className = 'mod-tab' + (on ? ' active' : '');
    if (on) {{ btn.style.background = rLevelColors[rl] || 'var(--accent)'; btn.style.borderColor = 'transparent'; }}
    btn.textContent = rl;
    btn.onclick = () => {{ currentR = rl; buildRFilter(); drawHourly(); drawHourlyAll(); }};
    el.appendChild(btn);
  }});
}}

function renderRLevels() {{
  const data = rlevels.slice();
  const sumFest = data.reduce((s, r) => s + r.festival, 0);
  const maxFest = Math.max(...data.map(r => r.festival), 1);
  $('rlevelBars').innerHTML = data.map(r => {{
    const w = r.festival / maxFest * 100, pct = sumFest ? r.festival / sumFest * 100 : 0;
    const arpu = r.payers ? r.festival / r.payers : 0, c = rLevelColors[r.rlevel] || '#8892a4';
    return '<div class="mod-row"><div class="mod-name">' + r.rlevel + '</div>'
      + '<div class="mod-bar-wrap"><div class="mod-bar" style="width:' + w.toFixed(1) + '%;background:' + c + '"></div></div>'
      + '<div class="mod-val">' + fmtMoney(r.festival) + '</div>'
      + '<div class="mod-pct">' + pct.toFixed(0) + '%</div>'
      + '<div class="mod-chg muted" style="width:56px">' + r.payers + '人</div>'
      + '<div class="mod-chg" style="width:64px">$' + arpu.toFixed(2) + '</div></div>';
  }}).join('');
  const paying = data.filter(r => r.rlevel !== '非R');
  const payFest = paying.reduce((s, r) => s + r.festival, 0);
  const top = data.slice().sort((a, b) => b.festival - a.festival)[0];
  let note = '全程累计节日收入 ' + fmtMoney(sumFest) + '：付费 R 级（超/大/中/小 R）贡献 ' + fmtMoney(payFest)
    + '（' + (sumFest ? (payFest / sumFest * 100).toFixed(0) : 0) + '%）';
  if (top && top.festival > 0) note += '，其中 ' + top.rlevel + ' 单层 ' + fmtMoney(top.festival) + '（' + (top.festival / sumFest * 100).toFixed(0) + '%）领跑';
  note += '。层节日ARPU = 该层节日流水 / 该层总付费人数。';
  $('rlevelNote').textContent = note;
}}

function renderRGain() {{
  if (!compare || !compare.cumulative || !compare.cumulative.summer_r || !compare.cumulative.valentine_r) return;
  const cu = compare.cumulative, sr = cu.summer_r, vr = cu.valentine_r, order = ['超R', '大R', '中R', '小R'];  // 非R无付费玩家,剔除
  $('rgainSection').style.display = '';
  $('rgainName').textContent = compare.val_name;
  const payRate = o => (o.payers ? o.fest_payers / o.payers * 100 : 0);  // 付费玩家付费率% = 节日付费/总付费
  const arpu = o => (o.payers ? o.festival / o.payers : 0);             // 付费ARPU = 节日流水/总付费人数
  const arppu = o => (o.fest_payers ? o.festival / o.fest_payers : 0);  // ARPPU = 节日流水/节日付费人数
  // 上→本 单元格：值变化 + 涨跌色
  function cell(vOld, vNew, fmt) {{
    const up = vNew > vOld, dn = vNew < vOld, cls = (up ? 'up' : dn ? 'down' : 'muted');
    return '<td class="num"><span class="muted">' + fmt(vOld) + '</span> → <span class="' + cls + '">' + fmt(vNew) + '</span></td>';
  }}
  const money = v => fmtMoney(v), pct = v => v.toFixed(1) + '%', usd = v => '$' + v.toFixed(2), usd0 = v => '$' + v.toFixed(0), int0 = v => Math.round(v).toLocaleString();
  const rows = order.map(rb => {{
    const S = sr[rb] || {{}}, V = vr[rb] || {{}};
    return '<tr><td style="color:' + (rLevelColors[rb] || '#8892a4') + ';font-weight:600">' + rb + '</td>'
      + cell(V.payers || 0, S.payers || 0, int0)
      + cell(payRate(V), payRate(S), pct)
      + cell(arpu(V), arpu(S), usd)
      + cell(arppu(V), arppu(S), usd0)
      + cell(V.festival || 0, S.festival || 0, money) + '</tr>';
  }}).join('');
  // 合计行（付费四档；档位互斥，人数/流水可直接相加）
  const agg = src => order.reduce((a, rb) => {{ const o = src[rb] || {{}}; a.payers += o.payers || 0; a.fest_payers += o.fest_payers || 0; a.festival += o.festival || 0; return a; }}, {{payers: 0, fest_payers: 0, festival: 0}});
  const oS = agg(sr), oV = agg(vr);
  const totalRow = '<tr style="font-weight:700"><td>合计</td>'
    + cell(oV.payers, oS.payers, int0) + cell(payRate(oV), payRate(oS), pct)
    + cell(arpu(oV), arpu(oS), usd) + cell(arppu(oV), arppu(oS), usd0) + cell(oV.festival, oS.festival, money) + '</tr>';
  $('rgainBody').innerHTML = rows + totalRow;
  // 结论：聚焦付费玩家付费率（已排除免费玩家）
  const rImp = order.filter(rb => payRate(sr[rb] || {{}}) > payRate(vr[rb] || {{}}));
  const dPP = payRate(oS) - payRate(oV);
  let note = '累计同期（' + cu.win + '）整体付费玩家付费率 <b>' + payRate(oV).toFixed(1) + '% → '
    + '<span class="' + (dPP >= 0 ? 'up' : 'down') + '">' + payRate(oS).toFixed(1) + '%</span></b>（' + (dPP >= 0 ? '+' : '') + dPP.toFixed(1) + 'pp，已排除免费玩家），'
    + '付费ARPU <b>$' + arpu(oV).toFixed(2) + ' → <span class="' + (arpu(oS) >= arpu(oV) ? 'up' : 'down') + '">$' + arpu(oS).toFixed(2) + '</span></b>。';
  note += '提升集中在中低档：' + (rImp.length ? rImp.map(rb => rb + '（' + payRate(vr[rb]).toFixed(0) + '%→' + payRate(sr[rb]).toFixed(0) + '%）').join('、') : '无') + '。高档本就接近饱和。';
  $('rgainNote').className = 'conclusion ' + (dPP >= 0 ? 'up' : 'down');
  $('rgainNote').innerHTML = note;
}}

function buildModrFilter() {{
  const el = $('modrFilter'); el.innerHTML = '';
  ['全部', '超R', '大R', '中R', '小R'].forEach(rl => {{
    const on = currentModR === rl, btn = document.createElement('div');
    btn.className = 'mod-tab' + (on ? ' active' : '');
    if (on) {{ btn.style.background = rLevelColors[rl] || 'var(--accent)'; btn.style.borderColor = 'transparent'; }}
    btn.textContent = rl;
    btn.onclick = () => {{ currentModR = rl; buildModrFilter(); renderModR(); }};
    el.appendChild(btn);
  }});
}}

function renderModR() {{
  if (!moduleR) return;
  $('modrSection').style.display = '';
  $('modrName').textContent = moduleR.val_name;
  const tiers = ['超R', '大R', '中R', '小R', '非R'];
  // 取某侧在当前R级筛选下：denom(总付费人数) + 各模块 buyers/rev
  function side(srcKey) {{
    const src = moduleR[srcKey], byR = src.byR, pay = src.payers;
    const sel = (currentModR === '全部') ? tiers : [currentModR];
    let denom = 0; const mod = {{}};
    sel.forEach(rb => {{
      denom += pay[rb] || 0;
      const mb = byR[rb] || {{}};
      for (const mm in mb) {{ mod[mm] = mod[mm] || {{buyers: 0, rev: 0}}; mod[mm].buyers += mb[mm].buyers; mod[mm].rev += mb[mm].rev; }}
    }});
    return {{denom, mod}};
  }}
  const S = side('summer'), V = side('valentine');
  const payRate = (m, d) => (d && m ? m.buyers / d * 100 : 0);
  const arpu = (m, d) => (d && m ? m.rev / d : 0);
  const arppu = m => (m && m.buyers ? m.rev / m.buyers : 0);
  function cell(vOld, vNew, fmt) {{
    const cls = vNew > vOld ? 'up' : vNew < vOld ? 'down' : 'muted';
    return '<td class="num"><span class="muted">' + fmt(vOld) + '</span> → <span class="' + cls + '">' + fmt(vNew) + '</span></td>';
  }}
  const pct = v => v.toFixed(1) + '%', usd = v => '$' + v.toFixed(2), usd0 = v => '$' + v.toFixed(0), money = v => fmtMoney(v);
  const rows = moduleR.modules.map(mm => {{
    const sm = S.mod[mm], vm = V.mod[mm];
    if (!sm && !vm) return '';
    const c = modColors[mm] || '#8892a4';
    return '<tr><td style="color:' + c + ';font-weight:600">' + mm + '</td>'
      + cell(payRate(vm, V.denom), payRate(sm, S.denom), pct)
      + cell(arpu(vm, V.denom), arpu(sm, S.denom), usd)
      + cell(arppu(vm), arppu(sm), usd0)
      + cell(vm ? vm.rev : 0, sm ? sm.rev : 0, money) + '</tr>';
  }}).join('');
  $('modrBody').innerHTML = rows || '<tr><td colspan="5" class="muted">无数据</td></tr>';
  $('modrNote').className = 'conclusion';
  $('modrNote').innerHTML = 'R级筛选【<b style="color:' + (rLevelColors[currentModR] || '#fff') + '">' + currentModR + '</b>】下，各节日模块在该人群的付费率/ARPU/ARPPU（上期' + moduleR.val_name + ' → 本期' + moduleR.summer_name + '）。分母总付费人数：上期 ' + V.denom + ' 人 → 本期 ' + S.denom + ' 人。';
}}

function renderModTotals() {{
  const tot = {{}};
  allDays.forEach(d => {{ for (const [m, v] of Object.entries(d.modules)) tot[m] = (tot[m] || 0) + v; }});
  const names = Object.keys(tot).sort((a, b) => tot[b] - tot[a]);
  const maxR = Math.max(...Object.values(tot), 1), sum = Object.values(tot).reduce((s, v) => s + v, 0);
  const nDays = allDays.length;
  if (!names.length) {{ $('modTotalBars').innerHTML = '<div class="muted" style="padding:8px 0">无数据</div>'; return; }}
  $('modTotalBars').innerHTML = names.map(m => {{
    const rev = tot[m], w = rev / maxR * 100, pct = sum ? rev / sum * 100 : 0, avg = rev / nDays, c = modColors[m] || '#8892a4';
    return '<div class="mod-row"><div class="mod-name">' + m + '</div><div class="mod-bar-wrap"><div class="mod-bar" style="width:' + w.toFixed(1) + '%;background:' + c + '"></div></div><div class="mod-val">' + fmtMoney(rev) + '</div><div class="mod-pct">' + pct.toFixed(0) + '%</div><div class="mod-chg muted">' + fmtMoney(avg) + '/d</div></div>';
  }}).join('');
  const top = names[0], top2 = names[1];
  let note = '全程（' + allDays[0].day_label + '~' + allDays[nDays - 1].day_label + '）累计节日收入 ' + fmtMoney(sum) + '，' + top + ' 以 ' + fmtMoney(tot[top]) + '（' + (tot[top] / sum * 100).toFixed(0) + '%）领跑';
  if (top2) note += '，其次 ' + top2 + ' ' + fmtMoney(tot[top2]) + '（' + (tot[top2] / sum * 100).toFixed(0) + '%）';
  note += '。';
  $('modTotalNote').textContent = note;
}}

function renderAlerts() {{
  const d = allDays[currentDayIdx], prev = currentDayIdx > 0 ? allDays[currentDayIdx - 1] : null;
  const nfArpu = d.non_festival / Math.max(d.payers, 1), nfDelta = nfArpu - baseline.arpu_nonfest;
  const modTotal = Object.values(d.modules).reduce((s, v) => s + v, 0);
  const alerts = [];
  if (prev) {{ for (const [m, rev] of Object.entries(d.modules)) {{ const p = prev.modules[m] || 0; if (p > 100 && rev < p * 0.5) alerts.push(['warn', m + '从' + prev.day_label + '的' + fmtMoney(p) + '降至' + d.day_label + '的' + fmtMoney(rev) + '，降幅' + Math.abs(pctChg(rev, p)).toFixed(0) + '%']); if (p < 50 && rev > 500) alerts.push(['info', m + '今日新开即贡献' + fmtMoney(rev) + '，占节日收入' + (rev / modTotal * 100).toFixed(0) + '%']); }} }}
  if (nfDelta < -2) alerts.push(['warn', '非节日ARPU下降' + fmtDelta(nfDelta) + '/人，存在挤占风险']);
  else if (nfDelta > 2) alerts.push(['info', '非节日ARPU上升' + fmtDelta(nfDelta) + '/人，节日带动日常消费']);
  else alerts.push(['info', '非节日消费持平，节日为纯增量模型']);
  $('alertsBox').innerHTML = alerts.map(([t, msg]) => '<div class="alert ' + (t === 'warn' ? 'alert-warn' : 'alert-info') + '"><span class="alert-icon">' + (t === 'warn' ? '&#9888;&#65039;' : '&#128204;') + '</span>' + msg + '</div>').join('');
}}

function modBarsHTML(mods) {{
  const names = Object.keys(mods).sort((a, b) => mods[b] - mods[a]);
  const maxR = Math.max(...Object.values(mods), 1), tot = Object.values(mods).reduce((s, v) => s + v, 0);
  if (!names.length) return '<div class="muted" style="padding:8px 0">无数据</div>';
  return names.map(m => {{
    const rev = mods[m], w = rev / maxR * 100, pct = tot ? rev / tot * 100 : 0, c = modColors[m] || '#8892a4';
    return '<div class="mod-row"><div class="mod-name">' + m + '</div><div class="mod-bar-wrap"><div class="mod-bar" style="width:' + w.toFixed(1) + '%;background:' + c + '"></div></div><div class="mod-val">' + fmtMoney(rev) + '</div><div class="mod-pct">' + pct.toFixed(0) + '%</div></div>';
  }}).join('');
}}

function renderCompare() {{
  if (!compare || !compare.days || !compare.days.length) return;
  $('compareSection').style.display = '';
  $('cmpName').textContent = compare.val_name + '（D0 ' + compare.val_d0 + '）';
  $('cmpColA').textContent = '上期 ' + compare.val_name;
  $('cmpColB').textContent = '本期 ' + compare.summer_name;
  $('cmpRColV').textContent = compare.val_name + ' 节日';
  $('cmpRColS').textContent = compare.summer_name + ' 节日';
  $('cmpRArpuV').textContent = compare.val_name + ' 层ARPU';
  $('cmpRArpuS').textContent = compare.summer_name + ' 层ARPU';
  const tabs = compare.days.slice();
  if (compare.cumulative) tabs.push(compare.cumulative);  // 末尾追加「累计」tab
  if (cmpDayIdx > tabs.length - 1) cmpDayIdx = tabs.length - 1;
  const tabsEl = $('cmpDayTabs'); tabsEl.innerHTML = '';
  tabs.forEach((cd, i) => {{
    const div = document.createElement('div');
    div.className = 'day-tab' + (i === cmpDayIdx ? ' active' : '');
    div.innerHTML = cd.day_label + '<span class="day-date">' + cd.win + '</span>';
    div.onclick = () => {{ cmpDayIdx = i; renderCompareDay(); }};
    tabsEl.appendChild(div);
  }});
  renderCompareDay();
}}

function cmpTabs() {{ const t = compare.days.slice(); if (compare.cumulative) t.push(compare.cumulative); return t; }}

function renderCompareDay() {{
  const tabs = cmpTabs();
  const cd = tabs[cmpDayIdx], S = cd.summer, V = cd.valentine, isCum = (cd.day_label === '累计');
  [...$('cmpDayTabs').children].forEach((c, i) => {{ c.className = 'day-tab' + (i === cmpDayIdx ? ' active' : ''); }});
  $('cmpHdr').textContent = cd.day_label + '（' + cd.win + '）';
  const vArpu = V.payers ? V.festival / V.payers : 0, sArpu = S.payers ? S.festival / S.payers : 0;  // 分母=当日总付费人数
  const vRatio = V.total ? V.festival / V.total * 100 : 0, sRatio = S.total ? S.festival / S.total * 100 : 0;
  const vPayRate = V.payers ? V.fest_payers / V.payers * 100 : 0, sPayRate = S.payers ? S.fest_payers / S.payers * 100 : 0;  // 付费玩家付费率 = 节日付费/总付费
  const vArppu = V.fest_payers ? V.festival / V.fest_payers : 0, sArppu = S.fest_payers ? S.festival / S.fest_payers : 0;  // ARPPU = 节日流水/节日付费人数
  function dCell(pct) {{ if (pct == null) return '<td class="num muted">—</td>'; const cls = pct > 0 ? 'up' : pct < 0 ? 'down' : 'muted'; return '<td class="num ' + cls + '">' + (pct > 0 ? '+' : '') + pct.toFixed(1) + '%</td>'; }}
  const ppCls = (sRatio - vRatio) > 0 ? 'up' : (sRatio - vRatio) < 0 ? 'down' : 'muted';
  const prCls = (sPayRate - vPayRate) > 0 ? 'up' : (sPayRate - vPayRate) < 0 ? 'down' : 'muted';
  const rows = [
    ['总流水', fmtMoney(V.total), fmtMoney(S.total), dCell(pctChg(S.total, V.total))],
    ['总付费人数', V.payers, S.payers, dCell(pctChg(S.payers, V.payers))],
    ['节日流水', fmtMoney(V.festival), fmtMoney(S.festival), dCell(pctChg(S.festival, V.festival))],
    ['节日占比', vRatio.toFixed(1) + '%', sRatio.toFixed(1) + '%', '<td class="num ' + ppCls + '">' + ((sRatio - vRatio) >= 0 ? '+' : '') + (sRatio - vRatio).toFixed(1) + 'pp</td>'],
    ['节日付费人数', V.fest_payers, S.fest_payers, dCell(pctChg(S.fest_payers, V.fest_payers))],
    ['付费率(节日付费人数/总付费人数)', vPayRate.toFixed(1) + '%', sPayRate.toFixed(1) + '%', '<td class="num ' + prCls + '">' + ((sPayRate - vPayRate) >= 0 ? '+' : '') + (sPayRate - vPayRate).toFixed(1) + 'pp</td>'],
    ['节日ARPU(节日流水/总付费人数)', '$' + vArpu.toFixed(2), '$' + sArpu.toFixed(2), dCell(pctChg(sArpu, vArpu))],
    ['ARPPU(节日流水/节日付费人数)', '$' + vArppu.toFixed(2), '$' + sArppu.toFixed(2), dCell(pctChg(sArppu, vArppu))],
  ];
  $('cmpBody').innerHTML = rows.map(r => '<tr><td>' + r[0] + '</td><td class="num">' + r[1] + '</td><td class="num">' + r[2] + '</td>' + r[3] + '</tr>').join('');
  $('cmpModBLabel').textContent = '上期 ' + compare.val_name + ' ' + cd.day_label + ' 模块（' + cd.val_date + '）';
  $('cmpModB').innerHTML = modBarsHTML(V.modules);
  $('cmpModALabel').textContent = '本期 ' + compare.summer_name + ' ' + cd.day_label + ' 模块（' + cd.summer_date + '）';
  $('cmpModA').innerHTML = modBarsHTML(S.modules);
  const dPR = sPayRate - vPayRate, dArppu = (vArppu ? (sArppu - vArppu) / vArppu * 100 : 0);
  const note = cd.day_label + '（' + cd.win + '）：本期' + compare.summer_name + '节日 ' + fmtMoney(S.festival) + '（占比 ' + sRatio.toFixed(0) + '%、' + S.fest_payers + ' 人付费）vs 上期' + compare.val_name + ' ' + fmtMoney(V.festival) + '（占比 ' + vRatio.toFixed(0) + '%、' + V.fest_payers + ' 人）。'
    + (sRatio >= vRatio ? '本期节日吸金占比更高' : '本期节日吸金占比偏低') + '（' + ((sRatio - vRatio) >= 0 ? '+' : '') + (sRatio - vRatio).toFixed(1) + 'pp），'
    + (S.fest_payers >= V.fest_payers ? '节日付费人数更多' : '节日付费人数更少') + '，节日ARPU(节日流水/总付费人数) $' + sArpu.toFixed(2) + ' vs $' + vArpu.toFixed(2) + '。'
    + '付费率 ' + vPayRate.toFixed(1) + '%→' + sPayRate.toFixed(1) + '%（' + (dPR >= 0 ? '+' : '') + dPR.toFixed(1) + 'pp）、ARPPU $' + vArppu.toFixed(2) + '→$' + sArppu.toFixed(2) + '（' + (dArppu >= 0 ? '+' : '') + dArppu.toFixed(1) + '%）：'
    + (dPR > 0 && dArppu < 0 ? '增长靠扩大付费人群（铺广度），人均深度略降——属"宽口浅底"，下一步应补深度款把 ARPPU 拉起来。'
     : dPR > 0 && dArppu >= 0 ? '付费面与人均深度双升，结构最健康。'
     : dPR <= 0 && dArppu > 0 ? '靠加深人均拉动，付费面未扩——需补低门槛款拉新付费。'
     : '付费面与人均深度双降，节日吸引力走弱。');
  $('cmpNote').className = 'conclusion ' + (sRatio >= vRatio ? 'up' : 'down');
  $('cmpNote').textContent = note;

  // R级对打表
  const sr = cd.summer_r, vr = cd.valentine_r;
  if (sr && vr) {{
    $('cmpRSection').style.display = '';
    const order = ['超R', '大R', '中R', '小R', '非R'];
    let sFestSum = 0, vFestSum = 0, sPaySum = 0, vPaySum = 0;
    const body = order.map(rb => {{
      const Sx = sr[rb] || {{festival: 0, payers: 0}}, Vx = vr[rb] || {{festival: 0, payers: 0}};
      sFestSum += Sx.festival; vFestSum += Vx.festival; sPaySum += Sx.payers; vPaySum += Vx.payers;
      const sA = Sx.payers ? Sx.festival / Sx.payers : 0, vA = Vx.payers ? Vx.festival / Vx.payers : 0;
      const d = pctChg(Sx.festival, Vx.festival);
      const dcell = d == null ? '<td class="num muted">—</td>' : '<td class="num ' + (d > 0 ? 'up' : d < 0 ? 'down' : 'muted') + '">' + (d > 0 ? '+' : '') + d.toFixed(0) + '%</td>';
      return '<tr><td>' + rb + '</td><td class="num">' + fmtMoney(Vx.festival) + '</td><td class="num">' + fmtMoney(Sx.festival) + '</td>' + dcell
        + '<td class="num muted">$' + vA.toFixed(2) + '</td><td class="num">$' + sA.toFixed(2) + '</td></tr>';
    }}).join('');
    const dSum = pctChg(sFestSum, vFestSum);
    const dSumCell = dSum == null ? '<td class="num muted">—</td>' : '<td class="num ' + (dSum > 0 ? 'up' : dSum < 0 ? 'down' : 'muted') + '">' + (dSum > 0 ? '+' : '') + dSum.toFixed(0) + '%</td>';
    const sArpuAll = sPaySum ? sFestSum / sPaySum : 0, vArpuAll = vPaySum ? vFestSum / vPaySum : 0;
    const totalRow = '<tr style="font-weight:700"><td>合计</td><td class="num">' + fmtMoney(vFestSum) + '</td><td class="num">' + fmtMoney(sFestSum) + '</td>' + dSumCell
      + '<td class="num muted">$' + vArpuAll.toFixed(2) + '</td><td class="num">$' + sArpuAll.toFixed(2) + '</td></tr>';
    $('cmpRBody').innerHTML = body + totalRow;
  }} else {{
    $('cmpRSection').style.display = 'none';
  }}
}}

function renderAll() {{
  buildDayTabs(); renderKPI(); renderARPU(); renderModBars();
  drawTrend('totalChart', 'total', '#6c63ff', 'rgba(108,99,255,.1)', {bl_total_int}, '基线 {bl_total_str}');
  drawTrend('festChart', 'festival', '#ffd166', 'rgba(255,209,102,.1)', 0, '', true);
  renderModTotals();
  buildModTabs(); drawModTrend();
  buildRFilter(); buildHrChips(); buildHrModeToggle(); drawHourly(); drawHourlyAll();
  renderRLevels();
  renderRGain();
  buildModrFilter(); renderModR();
  renderAlerts();
}}
renderAll();
renderCompare();
</script>
</body>
</html>"""

    filename = f"X3{FESTIVAL_NAME}日报_D{day_num}_{report_date}.html"
    output_path = os.path.join(OUTPUT_DIR, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    # 固定名"最新"副本，方便长期开着同一链接（每小时被覆盖刷新）
    latest_path = os.path.join(OUTPUT_DIR, f"X3{FESTIVAL_NAME}日报_latest.html")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(html)

    last_day = all_days[-1]
    print(f"HTML 日报已生成: {output_path}")
    print(f"最新副本: {latest_path}")
    print(f"D{day_num} | {report_date} | 总流水 {fmt_money(last_day['total'])} | 节日 {fmt_money(last_day['festival'])} | 付费 {last_day['payers']}人")


if __name__ == "__main__":
    main()
