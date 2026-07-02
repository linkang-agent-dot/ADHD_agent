# -*- coding: utf-8 -*-
"""X3 深海节全量配置扫描（dev 分支 tsv 真源）
检查维度：
  A. ActvOnline 16 活动行的全部 FK 引用（TimeCycle/RuleTips/Mail/RankCfg/ChainPack/ActvGroup/白名单Pack）
  B. 各类型内容表存在性 + 内容表内 FK
  C. Pack 深检（Price 档位/Content→Reward 组/连锁包列表）
  D. Reward 组完整性（DropPara 必填 / 组内 ID 连续 / DisplayOrder 组内唯一 / ItemID 存在）
  E. i18n 完备性（key 存在 / cn 非空 / 语言覆盖数 / 英文泄漏）
  F. tsv 引号吞行检查（csv vs tab 行奇偶校验）
  G. 模块语义检查（档数/道具指向/已知坑复核）
"""
import csv, re, os, json, sys, glob
from collections import defaultdict, Counter

TSV = r"C:\x3\gdconfig\tsv"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deepsea_scan_result.json")

findings = []   # dict(level, module, title, detail)
evidence = {}   # 供报告引用的原始数据

def add(level, module, title, detail=""):
    findings.append({"level": level, "module": module, "title": title, "detail": detail})

# ---------- loaders ----------
_cache = {}
def read(fname):
    if fname in _cache: return _cache[fname]
    p = os.path.join(TSV, fname)
    with open(p, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh, delimiter="\t"))
    _cache[fname] = rows
    return rows

def drows(fname):
    return [r for r in read(fname) if r and re.match(r"^\d+$", r[0] or "")]

def keyset(fname, col=0):
    return {r[col] for r in drows(fname) if len(r) > col and r[col]}

def refs_row(fname):
    rows = read(fname)
    return rows[2] if len(rows) > 2 else []

def ints(v):
    if not v: return []
    return [x for x in re.split(r"[|;,]", v.strip()) if re.match(r"^\d+$", x)]

# ---------- key sets ----------
AO_F   = "ActvOnline__ActvOnline.tsv"
item_ids   = keyset("Item__Item.tsv")
pack_ids   = keyset("Pack__Pack.tsv")
chain_ids  = keyset("Pack__ChainPack.tsv")
price_ids  = {r[0] for r in read("Pack__PackPrice.tsv") if r and r[0].strip()}
tc_ids     = keyset("TimeCycle__TimeCycle.tsv")
rule_ids   = keyset("RuleTips__RuleTips.tsv")
rank_ids   = keyset("Rank__RankCfg.tsv")
mail_ids   = keyset("Mail__MailTemplate.tsv")
group_ids  = keyset("ActvOnline__ActvGroup.tsv")
ao_ids     = keyset(AO_F)
scoretask_ids = keyset("ActvScore__ActvScoreTask.tsv")

reward_rows = drows("Reward__Reward.tsv")
reward_groups = defaultdict(list)
for r in reward_rows:
    if len(r) > 1 and r[1]:
        reward_groups[r[1]].append(r)

# group-keyed sub tables: ref_name -> file；Group 列位置从表头字段名行自动探测
GROUP_TABLES = {
    "ActvLuckyWheelReward.Group": "ActvLuckyWheel__ActvLuckyWheelReward.tsv",
    "ActvLuckyWheelOtherReward.Group": "ActvLuckyWheel__ActvLuckyWheelOtherReward.tsv",
    "ActvVoyageOtherReward.Group": "ActvVoyage__ActvVoyageOtherReward.tsv",
    "ActvVoyageIsland.IslandGroup": "ActvVoyage__ActvVoyageIsland.tsv",
    "BattlePassScore.Group": "ActvBattlePassScore__BattlePassScoreReward.tsv",
    "BattlePassScoreReward.Group": "ActvBattlePassScore__BattlePassScoreReward.tsv",
    "ActvPuzzleReward.Group": "ActvPuzzle__ActvPuzzleReward.tsv",
    "ActvPuzzleTask.Group": "ActvPuzzle__ActvPuzzleTask.tsv",
    "ActvWishingPoolReward.Group": "ActvWishingPool__ActvWishingPoolReward.tsv",
    "ActvWishingPoolStageReward.Group": "ActvWishingPool__ActvWishingPoolStageReward.tsv",
}
def find_group_col(fname, names=("Group", "IslandGroup")):
    """在头部非数据行里找字段名为 Group 的列"""
    for r in read(fname)[:8]:
        if r and re.match(r"^\d+$", r[0] or ""): break
        for ci, c in enumerate(r):
            if (c or "").strip() in names: return ci
    return 1
_group_cache = {}
def group_set(ref):
    if ref == "Reward":
        return set(reward_groups.keys())
    if ref in _group_cache: return _group_cache[ref]
    f = GROUP_TABLES.get(ref)
    s = set()
    if f and os.path.exists(os.path.join(TSV, f)):
        gc = find_group_col(f)
        s = {r[gc] for r in drows(f) if len(r) > gc and r[gc]}
    _group_cache[ref] = s
    return s

FLAT_TARGETS = {
    "Item": item_ids, "Pack": pack_ids, "ChainPack": chain_ids, "PackPrice": price_ids,
    "TimeCycle": tc_ids, "RuleTips": rule_ids, "RankCfg": rank_ids,
    "MailTemplate": mail_ids, "ActvGroup": group_ids, "ActvOnline": ao_ids,
    "ActvScoreTask": scoretask_ids,
}

def fk_check(fname, row, module, rowdesc, skip_cols=()):
    """按表头第3行 FK 注释逐列校验该行引用"""
    refs = refs_row(fname)
    for ci, ref in enumerate(refs):
        if not ref or ci >= len(row) or ci in skip_cols: continue
        vals = ints(row[ci])
        for v in vals:
            if v == "0": continue
            tgt = None
            if ref in FLAT_TARGETS: tgt = FLAT_TARGETS[ref]
            elif ref in GROUP_TABLES: tgt = group_set(ref)
            if tgt is None:  # 未建目标集的引用类型，跳过
                continue
            if v not in tgt:
                add("P0", module, f"{fname} {rowdesc} 列{ci} 引用 {ref}={v} 不存在",
                    f"该列注释指向 {ref} 表，值 {v} 查无此 key")

# ---------- 深海活动清单 ----------
ao_rows = {r[0]: r for r in drows(AO_F)}
deep_aos = {}
for aid, r in ao_rows.items():
    grp = r[38] if len(r) > 38 else ""
    if grp in ("140", "141"):
        deep_aos[aid] = r
evidence["ao_rows"] = {aid: {"name": r[2], "cid": r[4], "type": r[5], "ison": r[6],
                             "tc": r[7], "rule": r[13], "mail": r[17], "rank": r[20],
                             "chain": r[31], "grp": r[38], "img": r[21], "icon": r[22],
                             "whitelist": r[49] if len(r)>49 else ""}
                       for aid, r in deep_aos.items()}

# 防漏：名字含深海关键词但不在 140/141 的活动（已人工核过的老活动列入白名单）
KNOWN_OLD = {"1018091": "老航海之路102801的子拼图(schedule10002)", "104801": "常驻远航战备,TC4801自2025-11-09,重名巧合"}
for aid, r in ao_rows.items():
    nm = r[2] or ""
    if aid not in deep_aos and any(k in nm for k in ("深海", "远航", "海滨之约", "航海通行证", "美人鱼的梦境")):
        if aid in KNOWN_OLD:
            add("INFO", "总览", f"活动 {aid}「{nm}」重名但非深海节模块", KNOWN_OLD[aid])
        else:
            add("P2", "总览", f"活动 {aid}「{nm}」名字像深海节但 ActvGroup={r[38]}(非140/141)",
                f"Type={r[5]} CID={r[4]} IsOn={r[6]}，确认是否老活动或漏挂组")

# ---------- A. ActvOnline 行级 FK ----------
for aid, r in deep_aos.items():
    fk_check(AO_F, r, f"AO{aid} {r[2]}", f"活动{aid}")
    if r[6] != "1":
        add("P1", f"AO{aid} {r[2]}", f"IsOn={r[6]!r} 未开启")

# AO=100000+CID 规则（纯命名惯例，CID 链接已单独校验；全部降级 INFO 附同类型佐证）
for aid, r in deep_aos.items():
    cid, ty = r[4], r[5]
    if aid != str(100000 + int(cid)):
        peers = [(a, rr[4]) for a, rr in ao_rows.items() if rr[5] == ty and a != aid]
        same_pattern = sum(1 for a, c in peers if c and a != str(100000 + int(c or 0)))
        add("INFO", f"AO{aid} {r[2]}", f"AO≠100000+CID（CID={cid}，Type={ty}）命名惯例偏离",
            f"同类型其余 {len(peers)} 行中 {same_pattern} 行同样不符；ContentID 实链已验证存在，无功能影响")

# MailID：与同类型老活动对比（同类型多数配了而本行没配 → 提示）
for aid, r in deep_aos.items():
    if r[17]: continue
    ty = r[5]
    peers = [rr for a2, rr in ao_rows.items() if rr[5] == ty and a2 != aid]
    with_mail = sum(1 for p in peers if len(p) > 17 and p[17])
    if peers and with_mail > len(peers) / 2:
        add("P1", f"AO{aid} {r[2]}", f"MailID 空，但同 Type{ty} 的 {with_mail}/{len(peers)} 个活动都配了邮件模板",
            "结算走邮件的类型漏配会静默吞奖励，需人工确认该类型是否需要")

# ---------- B. 内容表存在 + 模块语义 ----------
def get_row(fname, key, col=0):
    for r in drows(fname):
        if len(r) > col and r[col] == key: return r
    return None

# Type10 转盘 1025
lw = get_row("ActvLuckyWheel__ActvLuckyWheel.tsv", "1025")
if not lw:
    add("P0", "转盘", "ActvLuckyWheel 无 1025 行")
else:
    fk_check("ActvLuckyWheel__ActvLuckyWheel.tsv", lw, "转盘", "1025")
    evidence["luckywheel"] = lw[:16]
    if lw[2] != "1200":
        add("P1", "转盘", f"消耗道具={lw[2]}，预期 1200 深海藏宝图")
    # 转盘奖池
    pool = [r for r in drows("ActvLuckyWheel__ActvLuckyWheelReward.tsv") if r[1] == lw[6]]
    if not pool: add("P0", "转盘", f"转盘奖池组 {lw[6]} 在 ActvLuckyWheelReward 中无行")
    else:
        for r in pool:
            fk_check("ActvLuckyWheel__ActvLuckyWheelReward.tsv", r, "转盘奖池", f"行{r[0]}")
    other = [r for r in drows("ActvLuckyWheel__ActvLuckyWheelOtherReward.tsv") if r[1] == lw[5]]
    if not other: add("P0", "转盘", f"累计次数阶段奖组 {lw[5]} 无行")
    else:
        for r in other:
            fk_check("ActvLuckyWheel__ActvLuckyWheelOtherReward.tsv", r, "转盘阶段奖", f"行{r[0]}")
    evidence["lw_pool_n"] = len(pool); evidence["lw_other_n"] = len(other)
    # RankCfg 2000 上榜门槛（0-based c14）
    rk = get_row("Rank__RankCfg.tsv", "2000")
    if rk:
        evidence["rank2000"] = rk
        if len(rk) > 14 and rk[14] != "1000":
            add("P1", "转盘", f"RankCfg2000 c14 上榜条件={rk[14]!r}，2026-06-30 修复目标=1000")

# Type5 累充 598
task598 = [r for r in drows("ActvTask__ActvTask.tsv") if len(r) > 2 and r[2] == "598"]
evidence["task598_ids"] = [r[0] for r in task598]
if len(task598) != 10:
    add("P1", "累充", f"ActvTask ContentID=598 档数={len(task598)}，预期 10 档")
for r in task598:
    fk_check("ActvTask__ActvTask.tsv", r, "累充", f"档{r[0]}")
    grp = reward_groups.get(r[8], [])
    if grp and not any(x[3] == "1057" for x in grp):
        add("P1", "累充", f"档 {r[0]} 奖励组 {r[8]} 不含航海罗盘1057", "2026-06-30 曾漏第10档，复核")
# 白名单
wl = ints(deep_aos.get("100598", [""]*52)[49]) if "100598" in deep_aos else []
evidence["whitelist_598"] = wl
for p in wl:
    if p not in pack_ids:
        add("P0", "累充", f"白名单礼包 {p} 在 Pack 表不存在")
bad_wl = [p for p in wl if re.match(r"^894", p) or p in [str(x) for x in range(211002, 211016)]]
if bad_wl:
    add("P0", "累充", f"白名单残留世界杯礼包: {bad_wl}", "2026-07-01 修过，若复现=回退")

# 深海各连锁/模块付费包 ⊆ 累充白名单
pack_rows_pre = {r[0]: r for r in drows("Pack__Pack.tsv")}
def paid(pid):
    r = pack_rows_pre.get(pid)
    return bool(r and len(r) > 7 and r[7].strip())
chain_map = {r[0]: ints(r[4]) for r in drows("Pack__ChainPack.tsv")}
for cpid, owner in (("463", "大富翁102802连锁"), ("700", "装饰106103连锁"), ("701", "转盘101025连锁")):
    missing_paid = [p for p in chain_map.get(cpid, []) if paid(p) and p not in wl]
    if missing_paid:
        prices = {p: pack_rows_pre[p][6] or pack_rows_pre[p][7] for p in missing_paid}
        add("P1", "累充", f"{owner}(ChainPack{cpid}) 付费档不在累充598白名单: {missing_paid}",
            f"玩家购买这些档位不计深海累充积分；价格备注={prices}。对照 463/700 的付费档均已在白名单")

# Type22 BP 2244/2246
for cid, pks_expect in (("2244", {"130046", "130035"}), ("2246", {"130036", "130037"})):
    bp = get_row("ActvBattlePassScore__BattlePassScore.tsv", cid)
    if not bp:
        add("P0", "BP", f"BattlePassScore 无 {cid} 行"); continue
    fk_check("ActvBattlePassScore__BattlePassScore.tsv", bp, f"BP{cid}", cid)
    evidence[f"bp{cid}"] = [c for c in bp[:9]]
    pks = set(ints(bp[4]))
    if pks != pks_expect:
        add("P1", "BP", f"BP{cid} Pack列={sorted(pks)}，记忆预期={sorted(pks_expect)}", "确认双档礼包指向")
    rg = [r for r in drows("ActvBattlePassScore__BattlePassScoreReward.tsv") if r[1] == bp[5]]
    if not rg: add("P0", "BP", f"BP{cid} 奖励组 {bp[5]} 无行")
    else:
        for r in rg:
            fk_check("ActvBattlePassScore__BattlePassScoreReward.tsv", r, f"BP{cid}奖励", f"行{r[0]}")
    evidence[f"bp{cid}_reward_n"] = len(rg)

# Type28 大富翁 2802
voy = get_row("ActvVoyage__ActvVoyage.tsv", "2802")
if not voy:
    add("P0", "大富翁", "ActvVoyage 无 2802 行")
else:
    fk_check("ActvVoyage__ActvVoyage.tsv", voy, "大富翁", "2802")
    evidence["voyage2802"] = voy
    if voy[3] == voy[4]:
        add("P0", "大富翁", f"LotteryItemID1==LotteryItemID2=={voy[3]}，精准抽卡会被随机覆盖（2026-06-30 撞号 BUG 同款）")
    # OtherReward 组
    vgc = find_group_col("ActvVoyage__ActvVoyageOtherReward.tsv")
    other = [r for r in drows("ActvVoyage__ActvVoyageOtherReward.tsv") if len(r) > vgc and r[vgc] == voy[6]]
    evidence["voy_other_n"] = len(other)
    evidence["voy_other_rewards"] = [(r[0], r[3], r[4] if len(r) > 4 else "") for r in other]
    for r in other:
        fk_check("ActvVoyage__ActvVoyageOtherReward.tsv", r, "大富翁阶段奖", f"行{r[0]}")
    # ProgressReward：曾为 1204×1 占位，验证是否已填真奖励（列：ID/Group/ItemID/ItemCount/NeedTime）
    prog = drows("ActvVoyage__ActvVoyageProgressReward.tsv")
    placeholder = [r for r in prog if len(r) > 2 and r[2] == "1204"]
    evidence["voy_prog_n"] = len(prog)
    evidence["voy_prog_items"] = [(r[2], r[3], r[4]) for r in prog]
    if placeholder:
        add("P1", "大富翁", f"珍珠贝进度奖励仍有 {len(placeholder)} 档发珍珠贝1204（收贝奖贝占位）", "待策划定真奖励")
    # 兑换店 134111 藏宝图排序修复复核（c9=排序）
    ex134111 = get_row("ActvExchange__ActvExchange.tsv", "134111")
    if ex134111:
        evidence["ex134111_order"] = ex134111[9]
    # ChainPack 463 双挂检查
    co_owners = [a for a, rr in ao_rows.items() if rr[31] == "463"]
    evidence["chain463_owners"] = co_owners
    if len(co_owners) > 1:
        add("P2", "大富翁", f"ChainPack463 被多个活动共挂: {co_owners}",
            "深海102802与老航海之路102801共用同一条连锁礼包；与「小骰子链677」方向分歧未定论(2026-06-30)，接手先问最终定463还是677")
    # Event 组 204/205 深海代币
    ev = [r for r in drows("ActvVoyage__ActvVoyageEvent.tsv")]
    evidence["voy_event_headers"] = read("ActvVoyage__ActvVoyageEvent.tsv")[2][:12]

# Type18 拼图 1828
pz = get_row("ActvPuzzle__ActvPuzzle.tsv", "1828")
if not pz:
    add("P0", "拼图", "ActvPuzzle 无 1828 行")
else:
    fk_check("ActvPuzzle__ActvPuzzle.tsv", pz, "拼图", "1828")
    tgc = find_group_col("ActvPuzzle__ActvPuzzleTask.tsv")
    rgc = find_group_col("ActvPuzzle__ActvPuzzleReward.tsv")
    tasks = [r for r in drows("ActvPuzzle__ActvPuzzleTask.tsv") if len(r) > tgc and r[tgc] == pz[2]]
    rews  = [r for r in drows("ActvPuzzle__ActvPuzzleReward.tsv") if len(r) > rgc and r[rgc] == pz[1]]
    evidence["puzzle"] = {"task_group": pz[2], "task_n": len(tasks), "reward_group": pz[1], "reward_n": len(rews)}
    if len(tasks) != 25: add("P1", "拼图", f"小格子任务组 {pz[2]} 行数={len(tasks)}，预期 25")
    for r in tasks: fk_check("ActvPuzzle__ActvPuzzleTask.tsv", r, "拼图任务", f"行{r[0]}")
    for r in rews:  fk_check("ActvPuzzle__ActvPuzzleReward.tsv", r, "拼图连线奖", f"行{r[0]}")

# Type29 每日礼包 3002
ap = get_row("ActvPack__ActvPack.tsv", "3002")
if not ap:
    add("P0", "每日礼包", "ActvPack 无 3002 行")
else:
    fk_check("ActvPack__ActvPack.tsv", ap, "每日礼包", "3002")
    evidence["actvpack3002"] = ap[:6]
    if len(ints(ap[2])) != 5:
        add("P1", "每日礼包", f"PackList 档数={len(ints(ap[2]))}，预期 5")

# Type14 签到 1406
lg = [r for r in drows("ActvLogin__ActvLogin.tsv") if len(r) > 1 and r[1] == "1406"]
evidence["login1406_n"] = len(lg)
if len(lg) != 7: add("P1", "签到", f"ActvLogin ContentID=1406 行数={len(lg)}，预期 7 天")
for r in lg: fk_check("ActvLogin__ActvLogin.tsv", r, "签到", f"行{r[0]}")

# Type70 周卡 61001
wc = get_row("ActvWeeklyCard__ActvWeeklyCard.tsv", "61001")
if not wc:
    add("P0", "周卡", "ActvWeeklyCard 无 61001 行")
else:
    fk_check("ActvWeeklyCard__ActvWeeklyCard.tsv", wc, "周卡", "61001")
    evidence["weeklycard"] = wc

# Type7 酒馆 719（多阶段酒馆内容表=ScoreMulti，ContentID 列=c2；老酒馆701/717同惯例不在ActvScore主表）
sm719 = [r for r in drows("ActvScore__ActvScoreMulti.tsv") if len(r) > 2 and r[2] == "719"]
if not sm719:
    add("P0", "酒馆", "ActvScoreMulti 无 ContentID=719 行")
else:
    evidence["tavern_stages"] = [(r[0], r[4], r[5], r[6], r[8]) for r in sm719]
    dur = sum(int(r[5]) for r in sm719 if r[5].isdigit())
    if dur != 10:
        add("P1", "酒馆", f"7 阶段时长合计={dur} 天，预期 10 天（对齐节日排期）")
sm = [r for r in drows("ActvScore__ActvScoreMulti.tsv") if r[0] in {str(x) for x in range(7191, 7198)}]
sg_file = "ActvScore__ActvScoreGroup.tsv"
sg = [r for r in drows(sg_file) if len(r) > 1 and r[1] in {str(x) for x in range(7191, 7198)}]
evidence["tavern"] = {"scoremulti_n": len(sm), "scoregroup_n": len(sg)}
if len(sm) != 7: add("P1", "酒馆", f"ScoreMulti 7191-7197 行数={len(sm)}，预期 7")
for r in sm: fk_check("ActvScore__ActvScoreMulti.tsv", r, "酒馆", f"行{r[0]}")
for g in ("786035", "786036", "786037", "786038"):
    if g not in reward_groups:
        add("P0", "酒馆", f"奖励组 {g} 在 Reward 不存在")

# Type13 兑换 1340/1341
ex_rows = drows("ActvExchange__ActvExchange.tsv")
for cid in ("1340", "1341"):
    rows = [r for r in ex_rows if len(r) > 1 and r[1] == cid]
    evidence[f"exchange{cid}_n"] = len(rows)
    if not rows: add("P0", "兑换", f"ActvExchange 无 ContentID={cid} 行"); continue
    for r in rows:
        fk_check("ActvExchange__ActvExchange.tsv", r, f"兑换{cid}", f"行{r[0]}")

# Type56 拜访 5606
vp = get_row("ActvVisitPack__ActvVisitPack.tsv", "5606")
if not vp: add("P0", "拜访", "ActvVisitPack 无 5606 行")
else:
    fk_check("ActvVisitPack__ActvVisitPack.tsv", vp, "拜访", "5606")
    evidence["visit5606"] = vp

# Type50 许愿池 5013
wp = get_row("ActvWishingPool__ActvWishingPool.tsv", "5013")
if not wp: add("P0", "许愿池", "ActvWishingPool 无 5013 行")
else:
    fk_check("ActvWishingPool__ActvWishingPool.tsv", wp, "许愿池", "5013")
    evidence["wish5013"] = wp

# ---------- C. Pack 深检 ----------
deep_packs = set()
# 连锁包
chain_rows = {r[0]: r for r in drows("Pack__ChainPack.tsv")}
for cpid in ("463", "700", "701"):
    cp = chain_rows.get(cpid)
    if not cp:
        add("P0", "礼包", f"ChainPack {cpid} 不存在"); continue
    lst = ints(cp[4])
    evidence[f"chain{cpid}"] = lst
    deep_packs.update(lst)
# 各模块直接引用的 pack
if "100598" in deep_aos: deep_packs.update(wl)
if ap: deep_packs.update(ints(ap[2]))
for cid in ("2244", "2246"):
    bp = get_row("ActvBattlePassScore__BattlePassScore.tsv", cid)
    if bp: deep_packs.update(ints(bp[4]))
if voy and voy[10]: deep_packs.add(voy[10])       # 存钱罐
if vp and vp[2]: deep_packs.add(vp[2])            # 拜访礼包
if wp and len(wp) > 5 and wp[5]: deep_packs.add(wp[5])  # 许愿池
if lw and lw[11]: deep_packs.add(lw[11])
deep_packs.update(["13021", "13022", "13023", "13024"])  # 锚点包
deep_packs.discard("0"); deep_packs.discard("")

pack_rows = {r[0]: r for r in drows("Pack__Pack.tsv")}
pack_info = {}
for pid in sorted(deep_packs, key=lambda x: int(x)):
    pr = pack_rows.get(pid)
    if not pr:
        add("P0", "礼包", f"Pack {pid} 不存在（被深海活动引用）"); continue
    price, content = pr[7], pr[13]
    pack_info[pid] = {"price": price, "content": content, "usd_note": pr[6] if len(pr) > 6 else ""}
    if price and price not in price_ids:
        add("P0", "礼包", f"Pack {pid} Price 档位 {price} 在 PackPrice 不存在")
    if content and content != "0":
        if content not in reward_groups:
            add("P0", "礼包", f"Pack {pid} Content={content} 在 Reward 无对应掉落组", "礼包内容为空，买了不发东西")
    elif pid not in ("130046", "130035", "130036", "130037"):
        add("P1", "礼包", f"Pack {pid} Content 为空", "确认该礼包是否走其他发放渠道")
evidence["pack_info"] = pack_info
evidence["deep_packs_n"] = len(deep_packs)
# 礼包中文名（供报告价目表）
_tmp_key2row = {}
with open(os.path.join(TSV, "i18n", "Text__Text.tsv"), encoding="utf-8", newline="") as fh:
    for r in csv.reader(fh, delimiter="\t"):
        if r and r[0].startswith("TXT_"):
            for k in r[0].split("|"): _tmp_key2row[k] = r
for pid in pack_info:
    r = _tmp_key2row.get(f"TXT_Pack_Name_{pid}")
    pack_info[pid]["cn"] = (r[3] if r and len(r) > 3 else "")
    pack_info[pid]["in_wl"] = pid in wl

# 677 孤儿确认
ref677 = [aid for aid, r in ao_rows.items() if r[31] == "677"]
evidence["chain677_refs"] = ref677

# ---------- D. Reward 组完整性 ----------
touched_groups = set()
for pid, inf in pack_info.items():
    if inf["content"] and inf["content"] != "0": touched_groups.add(inf["content"])
for r in task598: touched_groups.add(r[8])
if ap and ap[3]: touched_groups.add(ap[3])
for r in lg:
    if len(r) > 7 and r[7]: touched_groups.add(r[7])
touched_groups.update(["4200001","4200002","4200003","4200004","4200005","4200006","4200007","4200008",
                       "603702","603703","603704","59813","59814","786035","786036","786037","786038","40500","40600","2063"])
touched_groups = {g for g in touched_groups if g and g != "0"}
evidence["touched_reward_groups_n"] = len(touched_groups)

miss_groups, drop_issues, cont_issues, dup_disp, bad_item = [], [], [], [], []
for g in sorted(touched_groups, key=lambda x: int(x)):
    rows = reward_groups.get(g)
    if not rows:
        if g == "2063": continue  # 神秘宝箱独立化 worktree 未合，允许缺
        miss_groups.append(g); continue
    ids = sorted(int(r[0]) for r in rows)
    if ids[-1] - ids[0] != len(ids) - 1:
        cont_issues.append(f"组{g}: id {ids[0]}..{ids[-1]} 共{len(ids)}行不连续")
    disp = [r[14] if len(r) > 14 and r[14] else "0" for r in rows]
    dd = [d for d, c in Counter(disp).items() if c > 1]
    if dd: dup_disp.append(f"组{g}: DisplayOrder 重复 {dd}")
    for r in rows:
        if not (len(r) > 8 and r[8].strip()):
            drop_issues.append(f"组{g} 行{r[0]} DropPara 空")
        if len(r) > 3 and r[2] == "1" and r[3] not in item_ids:
            bad_item.append(f"组{g} 行{r[0]} ItemID={r[3]} 不在 Item 表")
for g in miss_groups: add("P0", "Reward", f"奖励组 {g} 不存在但被引用")
for m in cont_issues: add("P0", "Reward", "组内 ID 不连续（pre-push 硬拦截口径）", m)
for m in dup_disp:   add("P0", "Reward", "组内 DisplayOrder 重复（pre-push 硬拦截口径）", m)
for m in drop_issues: add("P1", "Reward", "DropPara 为空", m)
for m in bad_item:   add("P0", "Reward", "奖励指向不存在的道具", m)

# ---------- E. i18n ----------
TXT = os.path.join(TSV, "i18n", "Text__Text.tsv")
with open(TXT, encoding="utf-8", newline="") as fh:
    trows = list(csv.reader(fh, delimiter="\t"))
lang_hdr = trows[0]
# 只统计有语言代码表头的列（c19+ 为无表头预留列，不算缺失）
lang_cols = [i for i in range(3, len(lang_hdr)) if lang_hdr[i].strip()]
key2row = {}
for r in trows:
    if r and r[0].startswith("TXT_"):
        for k in r[0].split("|"):
            key2row[k] = r
evidence["lang_n"] = len(lang_cols)

def i18n_check(key, module, required=True):
    r = key2row.get(key)
    if not r:
        if required: add("P1", "i18n", f"缺 key: {key}", module)
        return
    filled = sum(1 for c in lang_cols if c < len(r) and r[c].strip())
    if not (len(r) > 3 and r[3].strip()):
        add("P1", "i18n", f"{key} 简体中文为空", module)
    elif filled < len(lang_cols) - 2:
        add("P2", "i18n", f"{key} 仅 {filled}/{len(lang_cols)} 语言有值", module)
    # 英文泄漏：非英语列与英文完全一致的 >=6 个
    if len(r) > 4:
        en = None
        for c in lang_cols:
            if c < len(lang_hdr) and lang_hdr[c].strip().lower() in ("en", "english"):
                en = r[c].strip() if c < len(r) else ""
        if en and len(en) > 3:
            same = sum(1 for c in lang_cols
                       if c < len(r) and r[c].strip() == en and (lang_hdr[c].strip().lower() not in ("en", "english")))
            if same >= 8:
                add("P2", "i18n", f"{key} 疑似英文泄漏（{same} 个非英语列 = 英文）", module)

for aid, r in deep_aos.items():
    i18n_check(f"TXT_ActvOnline_ActvName_{aid}", f"AO{aid} {r[2]}")
    i18n_check(f"TXT_ActvOnline_ActvDesc_{aid}", f"AO{aid} {r[2]}", required=False)
for pid in sorted(deep_packs, key=lambda x: int(x)):
    if pid in pack_rows:
        i18n_check(f"TXT_Pack_Name_{pid}", f"Pack{pid}")
for iid in ("1057", "1058", "1059", "1200", "1201", "1202", "1204"):
    i18n_check(f"TXT_Item_Name_{iid}", f"Item{iid}")
    i18n_check(f"TXT_Item_Desc_{iid}", f"Item{iid}", required=False)
# RuleTips 引用的 TXT key
rt_rows = {r[0]: r for r in drows("RuleTips__RuleTips.tsv")}
for aid, r in deep_aos.items():
    for rid in ints(r[13]):
        rt = rt_rows.get(rid)
        if not rt:
            add("P0", f"AO{aid} {r[2]}", f"RuleTips {rid} 不存在"); continue
        for cell in rt[1:4]:
            for m in re.findall(r"TXT_[A-Za-z0-9_]+", cell or ""):
                i18n_check(m, f"RuleTips{rid}")

# 同类型 AO/CID 惯例参考
evidence["type_peers"] = {ty: [(a, r[4]) for a, r in ao_rows.items() if r[5] == ty]
                          for ty in ("29", "56", "63", "70")}

# ---------- F. 引号吞行 ----------
CHECK_FILES = [AO_F, "ActvExchange__ActvExchange.tsv", "ActvLuckyWheel__ActvLuckyWheelReward.tsv",
               "Pack__Pack.tsv", "Pack__ChainPack.tsv", "Reward__Reward.tsv",
               "ActvVoyage__ActvVoyage.tsv", "ActvVoyage__ActvVoyageEvent.tsv",
               "ActvScore__ActvScoreGroup.tsv", "ActvTask__ActvTask.tsv"]
multiline_cells = []
for f in CHECK_FILES:
    p = os.path.join(TSV, f)
    if not os.path.exists(p): continue
    txt = open(p, encoding="utf-8").read()
    if txt.count('"') % 2 == 1:
        add("P0", "格式", f"{f} 引号总数为奇数（存在未闭合游离引号）",
            "最后一个未配对引号会把文件尾部全部吞掉（1341 同款事故）")
    for r in drows(f):
        segs = [seg for c in r if "\n" in c for seg in c.split("\n")[1:]]
        if not segs: continue
        # 被吞内容以「数字+tab」开头 = 真的吃掉了数据行；否则是合法多行 cell
        eaten = [s for s in segs if re.match(r"^\d+\t", s)]
        if eaten:
            add("P0", "格式", f"{f} 行 {r[0]} 引号吞掉了数据行",
                f"被吞行首: {[s.split(chr(9))[0] for s in eaten]}")
        else:
            multiline_cells.append(f"{f}:{r[0]}")
if multiline_cells:
    add("P2", "格式", f"存量多行 cell 共 {len(multiline_cells)} 处（引号配对完整，数据不丢）",
        "行内文案含换行属合法写法；但用行级工具(awk/sed)编辑这些行会破坏配对，改表绕开: " + ", ".join(multiline_cells[:25]))

# ---------- G. 其他已知坑复核 ----------
# ItemObtain 1200 获取路径
io_rows = [r for r in drows("ItemObtain__ItemObtain.tsv") if r[0] == "1200"]
evidence["itemobtain_1200"] = io_rows
if not io_rows:
    add("P0", "转盘", "ItemObtain 无 1200（藏宝图无获取路径跳转），2026-06-30 修过，复现=回退")
# ActvGroupSchedule 10005
gs = [r for r in drows("ActvOnline__ActvGroupSchedule.tsv")]
gs10005 = [r for r in gs if r[0] == "10005"]
evidence["schedule10005"] = gs10005
deep_sched = [r for r in gs if any(x in ("102801", "102802", "101828") for x in r[:4])]
evidence["deep_sched"] = deep_sched
# TimeCycle 明细
for tcid in ("1830", "160100"):
    row = get_row("TimeCycle__TimeCycle.tsv", tcid)
    if row: evidence[f"tc{tcid}"] = row[:12]

# Item 存在性（核心道具）
for iid in ("1057", "1058", "1059", "1200", "1201", "1202", "1204"):
    if iid not in item_ids:
        add("P0", "道具", f"Item {iid} 不存在")
evidence["item1206_exists"] = "1206" in item_ids

out = {"findings": findings, "evidence": evidence}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
print(f"findings: {len(findings)}")
for lv in ("P0", "P1", "P2", "INFO"):
    n = sum(1 for f in findings if f["level"] == lv)
    print(f"  {lv}: {n}")
for f in findings:
    if f["level"] in ("P0", "P1"):
        print(f"[{f['level']}] {f['module']} | {f['title']} | {f['detail'][:80]}")
