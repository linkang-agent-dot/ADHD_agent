# -*- coding: utf-8 -*-
"""深海节周卡投放合理性分析：周卡实际落表 + 全付费包ROI阶梯 + 核心道具投放汇总"""
import csv, re, os, io, sys, json, glob
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
TSV = r"C:\x3\gdconfig\tsv"

def load(f):
    return list(csv.reader(open(os.path.join(TSV, f), encoding="utf-8", newline=""), delimiter="\t"))
def data(rows):
    return [r for r in rows if r and re.match(r"^\d+$", r[0])]

# 价值锚（美元/个）
V = {"1200": 0.25, "1057": 0.5, "1002": 0.002, "1202": 0.02}
item_rows = {r[0]: r for r in data(load("Item__Item.tsv"))}
def iname(iid):
    r = item_rows.get(iid)
    return (r[1] if r else iid)[:10]

rew = data(load("Reward__Reward.tsv"))
G = defaultdict(list)
for r in rew: G[r[1]].append(r)

def gval(gid):
    """奖励组锚定价值 + 未锚定清单"""
    v, un = 0.0, []
    for r in G.get(gid, []):
        iid, qty = r[3], int(r[5] or 0)
        if iid in V: v += V[iid] * qty
        else: un.append(f"{iname(iid)}x{qty}")
    return v, un

def gitems(gid):
    return {r[3]: int(r[5] or 0) for r in G.get(gid, [])}

# PackPrice 精确美元
pp = {r[0]: int(r[1]) / 100 for r in data(load("Pack__PackPrice.tsv")) if r[1].isdigit()}
packs = {r[0]: r for r in data(load("Pack__Pack.tsv"))}

# ===== 1. 周卡 =====
print("=" * 30, "1. 周卡实际落表", "=" * 30)
tier_files = [f for f in os.listdir(TSV) if f.startswith("ActvWeeklyCard__")]
print("周卡相关表:", tier_files)
for f in tier_files:
    rows = load(f)
    hdr = next((r for r in rows[:8] if r and r[0].strip() in ("ID", "编号")), None)
    print(f"-- {f} 字段:", (hdr or ["?"])[:12])
    for r in data(rows)[:8]:
        print("   ", r[:12])

# 每日池 826311-340
print("-- 每日自选池(组: item qty 锚值$)")
pool = {}
for t, base in (("档1", 826311), ("档2", 826321), ("档3", 826331)):
    tot_best4 = []
    vals = []
    for gid in range(base, base + 10):
        g = str(gid)
        v, un = gval(g)
        it = gitems(g)
        vals.append((g, it, round(v, 2), un))
    vals_sorted = sorted(vals, key=lambda x: -x[2])
    best4 = sum(v for _, _, v, _ in vals_sorted[:4])
    pool[t] = {"pools": vals, "best4_daily": round(best4, 2)}
    print(f" {t}: best4日值=${best4:.2f} 池明细:", [(g, [f'{iname(i)}x{q}' for i, q in it.items()], v) for g, it, v, un in vals])

# 立即奖
imm = {}
for t, gid, price in (("档1", "826301", 9.99), ("档2", "826302", 19.99), ("档3", "826303", 29.99), ("打包", "826304", 49.99)):
    v, un = gval(gid)
    imm[t] = round(v, 2)
print("立即奖锚值:", imm)
roi = {}
for t, price in (("档1", 9.99), ("档2", 19.99), ("档3", 29.99)):
    total = pool[t]["best4_daily"] * 7 + imm[t]
    roi[t] = round(total / price, 2)
    print(f"周卡{t} ${price}: 7天best4={pool[t]['best4_daily']*7:.2f} + 立即奖{imm[t]} = ${pool[t]['best4_daily']*7+imm[t]:.2f} → ROI {roi[t]}x")
# 打包 = 三档全解锁
tot_bundle = sum(pool[t]["best4_daily"] for t in ("档1", "档2", "档3")) * 7 + sum(imm[t] for t in ("档1", "档2", "档3", "打包"))
print(f"打包$49.99(解锁全三档,含四份立即奖): 总值≈${tot_bundle:.2f} → ROI {tot_bundle/49.99:.2f}x  (若打包只给自身立即奖: {(tot_bundle-imm['档1']-imm['档2']-imm['档3'])/49.99:.2f}x~)")

# ===== 2. 全部深海付费包 ROI 阶梯 =====
print("=" * 30, "2. 深海付费包ROI阶梯", "=" * 30)
MODULES = {
    "每日礼包": ["800005", "800006", "800007", "800008", "800009"],
    "锚点包": ["13021", "13022", "13023", "13024"],
    "转盘连锁701": ["211022", "211024", "211026", "211028", "211030"],
    "大富翁连锁463": ["207104", "207106", "207108", "207110", "207112"],
    "装饰700": ["211016", "211017", "211018"],
    "头像框": ["211019"],
    "拜访": ["211020"],
    "成就礼包": [str(x) for x in range(2801001, 2801012)],
    "存钱罐": ["280001"],
    "许愿池包": ["1002001"],
    "BP远航日志": ["130046", "130035"],
    "BP航海通行证": ["130036", "130037"],
}
ladder = []
for mod, pids in MODULES.items():
    for pid in pids:
        pr = packs.get(pid)
        if not pr: continue
        usd = pp.get(pr[7], 0)
        if not usd: continue
        v, un = gval(pr[13])
        it = gitems(pr[13])
        ladder.append((mod, pid, usd, round(v, 2), round(v / usd, 2) if usd else 0,
                       {f"{iname(i)}": q for i, q in it.items()}, un))
for row in ladder:
    print(f"{row[0]:8s} {row[1]} ${row[2]:6.2f} 锚值${row[3]:7.2f} ROI={row[4]:5.2f}x 内容:{row[5]} 未锚:{row[6]}")

# ===== 3. 核心道具投放汇总(1200/1057/1058/1202) =====
print("=" * 30, "3. 核心道具投放汇总", "=" * 30)
def sum_groups(gids, label, store, src):
    for gid in gids:
        for r in G.get(str(gid), []):
            iid, qty = r[3], int(r[5] or 0)
            if iid in ("1200", "1057", "1058", "1202"):
                store[iid][src] += qty

tot = {k: defaultdict(int) for k in ("1200", "1057", "1058", "1202")}
# 付费源
for mod, pids in MODULES.items():
    for pid in pids:
        pr = packs.get(pid)
        if pr: sum_groups([pr[13]], None, tot, "付费:" + mod)
# 周卡付费: 7天×各档全池(上限口径:每天4选,取纯坑1藏宝图/坑3罗盘极值另算) → 用"每天必选坑1+坑3"口径
for t, base, mult in (("档1", 826311, 1), ("档2", 826321, 1), ("档3", 826331, 1)):
    for gid in range(base, base + 10):
        for r in G.get(str(gid), []):
            iid, qty = r[3], int(r[5] or 0)
            if iid in tot: tot[iid]["付费:周卡" + t + "(7天若每日选此坑)"] += qty * 7
sum_groups(["826301", "826302", "826303", "826304"], None, tot, "付费:周卡立即奖")
# BP 奖励轨(142/144)
bpr = data(load("ActvBattlePassScore__BattlePassScoreReward.tsv"))
bph = load("ActvBattlePassScore__BattlePassScoreReward.tsv")
# 找到 reward 引用列(第3行 refs)
refs = bph[2]
rcols = [i for i, c in enumerate(refs) if c == "Reward"]
for r in bpr:
    if len(r) > 1 and r[1] in ("142", "144"):
        for c in rcols:
            if c < len(r) and r[c] and r[c] != "0":
                sum_groups([r[c]], None, tot, f"付费:BP组{r[1]}全轨")
# 免费源
sum_groups(["59813", "59814"], None, tot, "免费:签到(6天+第7天)")
sum_groups(["603704"], None, tot, "免费:拼图小格子(×25)")
for r in G.get("603704", []):
    pass
# 拼图小格子是25个任务各发603704?→ 实际是每格一次: 25次
for iid in tot:
    if tot[iid].get("免费:拼图小格子(×25)"): tot[iid]["免费:拼图小格子(×25)"] *= 25
sum_groups(["603702", "603703"], None, tot, "免费:拼图连线集齐")
# 拼图连线奖励组1100→ ActvPuzzleReward rows reward refs
pzr = data(load("ActvPuzzle__ActvPuzzleReward.tsv"))
for r in pzr:
    if len(r) > 3 and r[3] == "1100" and len(r) > 4 and r[4]:
        sum_groups([r[4]], None, tot, "免费:拼图连线11档")
# 进度奖励(珍珠贝)
prog = data(load("ActvVoyage__ActvVoyageProgressReward.tsv"))
for r in prog:
    if r[2] in tot: tot[r[2]]["免费:珍珠贝17档"] += int(r[3] or 0)
# 大富翁按次阶段奖
sum_groups([f"420000{i}" for i in range(1, 9)], None, tot, "半免费:大富翁抽奖阶段奖8档")
# 累充
for gid in range(59850, 59860):
    sum_groups([gid], None, tot, "半免费:累充10档")
# 转盘累计阶段奖(组3020)
lwo = data(load("ActvLuckyWheel__ActvLuckyWheelOtherReward.tsv"))
lwh = load("ActvLuckyWheel__ActvLuckyWheelOtherReward.tsv")
lrefs = lwh[2]
lrcols = [i for i, c in enumerate(lrefs) if c == "Reward"]
gc = None
for hr in lwh[:8]:
    for i, c in enumerate(hr):
        if (c or "").strip() == "Group": gc = i
for r in lwo:
    if gc is not None and len(r) > gc and r[gc] == "3020":
        for c in lrcols:
            if c < len(r) and r[c] and r[c] != "0":
                sum_groups([r[c]], None, tot, "免费:转盘累计次数阶段奖")
for iid, srcs in tot.items():
    print(f"--- {iid} {iname(iid)} 总计 {sum(srcs.values())}")
    for s, q in sorted(srcs.items(), key=lambda x: -x[1]):
        if q: print(f"    {s}: {q}")
