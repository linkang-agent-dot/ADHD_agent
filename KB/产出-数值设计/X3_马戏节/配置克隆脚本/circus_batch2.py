# -*- coding: utf-8 -*-
"""马戏节换皮 批次2：转盘族全套
AO101026 + LuckyWheel1026 + 奖池组322 + 阶段奖组3021/Reward30940-46
+ 双榜2002/2003 + SlotCfg + 榜奖组30950-57/30960-66
+ ChainPack703 + Pack211035-045 + 锚点13025-028 + 同号Reward组
+ ItemObtain1209 + RuleTips16043 + i18n
铁律：全部纯新增行零改旧行；Reward seq 连续块；写前断言目标 ID 不存在。"""
import io

REPO = r"C:\x3\gdconfig-circus"
P = lambda f: REPO + "\\tsv\\" + f

def read(f):
    with io.open(P(f), "r", encoding="utf-8", newline="") as fh:
        return fh.read().split("\n")

def write(f, lines):
    with io.open(P(f), "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines))

def rows_where(lines, pred):
    return [(i, ln.split("\t")) for i, ln in enumerate(lines) if ln and pred(ln.split("\t"))]

def assert_absent(lines, ids, col=0, label=""):
    s = set(str(x) for x in ids)
    for ln in lines:
        f = ln.split("\t")
        if len(f) > col and f[col] in s:
            raise AssertionError("%s 目标ID已存在: %s" % (label, f[col]))

def find_idx(lines, rid, col=0):
    for i, ln in enumerate(lines):
        f = ln.split("\t")
        if len(f) > col and f[col] == str(rid):
            return i
    raise AssertionError("源行缺失: %s" % rid)

SWAP_ITEM = {"1200": "1209", "1201": "1210"}
SWAP_NAME = {"深海藏宝图": "马戏门票", "深海宝珠": "马戏勋章", "女王恩典卷 ": "马戏门票", "女王恩典卷": "马戏门票"}

# ============ 1. Reward__Reward.tsv：五族新组 ============
f = "Reward__Reward.tsv"
lines = read(f)
new_groups = list(range(30940, 30947)) + list(range(30950, 30958)) + list(range(30960, 30967)) + list(range(211035, 211046)) + list(range(13025, 13029))
gset = set(str(g) for g in new_groups)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[1] in gset:
        raise AssertionError("Reward 组已存在: " + fl[1])

seq = 15905099
out_rows = []
def clone_group(src_gid, dst_gid, note):
    """整组克隆：换 seq/组号/道具/名/备注；权重结构照抄"""
    global seq
    src = rows_where(lines, lambda r: len(r) > 1 and r[1] == str(src_gid))
    assert src, "源组空: %s" % src_gid
    for _, r in src:
        r = list(r)
        old_seq = r[0]
        r[0] = str(seq)
        r[1] = str(dst_gid)
        if r[3] in SWAP_ITEM:
            r[3] = SWAP_ITEM[r[3]]
        for k, v in SWAP_NAME.items():
            if r[4] == k:
                r[4] = v
        for i in range(4, len(r)):
            if "深海" in r[i] or "尼罗之辉" in r[i]:
                r[i] = note
        for i in range(5, len(r)):
            if r[i] == old_seq:
                r[i] = str(seq)
        out_rows.append("\t".join(r))
        seq += 1

# 阶段奖 30920-26 → 30940-46（1201→1210）
for i in range(7):
    clone_group(30920 + i, 30940 + i, "马戏大转盘-转盘阶段奖")
# 本服榜 30910-17 → 30950-57（180080纪念卡=占位待换马戏卡）
for i in range(8):
    clone_group(30910 + i, 30950 + i, "马戏大转盘-本服积分排名(卡占位待换)")
# 跨服榜 30930-36 → 30960-66（15065皮/82005头衔=占位待定案）
for i in range(7):
    clone_group(30930 + i, 30960 + i, "马戏大转盘-全服积分排名(大奖占位待定)")
# 连锁 211021-31 → 211035-45（1200→1209）
for i in range(11):
    clone_group(211021 + i, 211035 + i, "26马戏节活动-连锁礼包")
# 锚点 13021-24 → 13025-28
for i in range(4):
    clone_group(13021 + i, 13025 + i, "马戏门票-道具获取")

tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(out_rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Reward OK: %d 行新增, seq %d..%d" % (len(out_rows), 15905099, seq - 1))

# ============ 2. LuckyWheelReward 组322 ============
f = "ActvLuckyWheel__ActvLuckyWheelReward.tsv"
lines = read(f)
assert_absent(lines, range(32200, 32210), 0, "LWReward")
src = rows_where(lines, lambda r: len(r) > 1 and r[1] == "321")
assert len(src) == 10
rows = []
for _, r in src:
    r = list(r)
    r[0] = str(32200 + int(r[0]) - 32100)
    r[1] = "322"
    if r[2] in SWAP_ITEM:
        r[2] = SWAP_ITEM[r[2]]
    r[3] = r[3].replace("深海宝珠", "马戏勋章").replace("深海猎手·潜艇行军皮(核心大奖)", "大奖占位待定(沿深海潜艇皮,定案后换)")
    rows.append("\t".join(r))
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("LuckyWheelReward OK: 组322 x10")

# ============ 3. OtherReward 组3021 ============
f = "ActvLuckyWheel__ActvLuckyWheelOtherReward.tsv"
lines = read(f)
assert_absent(lines, range(302101, 302108), 0, "OtherReward")
src = rows_where(lines, lambda r: len(r) > 1 and r[1] == "3020")
assert len(src) == 7
rows = []
for _, r in src:
    r = list(r)
    r[0] = str(302101 + int(r[0]) - 302001)
    r[1] = "3021"
    r[2] = str(30940 + int(r[2]) - 30920)
    r[5] = "马戏门票"
    rows.append("\t".join(r))
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("OtherReward OK: 组3021 x7 → Reward 30940-46")

# ============ 4. ActvLuckyWheel 1026 ============
f = "ActvLuckyWheel__ActvLuckyWheel.tsv"
lines = read(f)
assert_absent(lines, [1026], 0, "LuckyWheel")
i = find_idx(lines, 1025)
r = list(lines[i].split("\t"))
r[0] = "1026"; r[2] = "1209"; r[5] = "3021"; r[6] = "322"; r[12] = "2002"
if len(r) > 16:
    r[16] = "马戏节"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("LuckyWheel OK: 1026 (Consume=1209, 榜=2002, DK沿深海占位)")

# ============ 5. RankCfg 2002/2003 ============
f = "Rank__RankCfg.tsv"
lines = read(f)
assert_absent(lines, [2002, 2003], 0, "RankCfg")
i0, i1 = find_idx(lines, 2000), find_idx(lines, 2001)
r = list(lines[i0].split("\t")); r[0] = "2002"; r[1] = "活动-26马戏节-本服积分排名"
row2002 = "\t".join(r)
r = list(lines[i1].split("\t")); r[0] = "2003"; r[1] = "活动-26马戏节-全服积分排名"
row2003 = "\t".join(r)
lines.insert(max(i0, i1) + 1, row2003)
lines.insert(max(i0, i1) + 1, row2002)
write(f, lines)
print("RankCfg OK: 2002/2003 (col4沿97同构,客户端分类异常再核)")

# ============ 6. RankRewardSlotCfg ============
f = "Rank__RankRewardSlotCfg.tsv"
lines = read(f)
assert_absent(lines, range(100438, 100453), 0, "SlotCfg")
src_local = rows_where(lines, lambda r: len(r) > 1 and r[1] == "2000")
src_cross = rows_where(lines, lambda r: len(r) > 1 and r[1] == "2001")
assert len(src_local) == 8 and len(src_cross) == 7
rows, nid = [], 100438
for _, r in src_local:
    r = list(r); r[0] = str(nid); r[1] = "2002"
    r[4] = str(30950 + int(r[4]) - 30910)
    r[5] = "马戏大转盘-本服积分排名"
    rows.append("\t".join(r)); nid += 1
for _, r in src_cross:
    r = list(r); r[0] = str(nid); r[1] = "2003"
    r[4] = str(30960 + int(r[4]) - 30930)
    r[5] = "马戏大转盘-全服积分排名"
    rows.append("\t".join(r)); nid += 1
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("SlotCfg OK: 100438-100452 (本服8+跨服7)")

# ============ 7. Pack 211035-045 + 13025-028 ============
f = "Pack__Pack.tsv"
lines = read(f)
assert_absent(lines, list(range(211035, 211046)) + list(range(13025, 13029)), 0, "Pack")
rows = []
for i in range(11):
    src_i = find_idx(lines, 211021 + i)
    r = list(lines[src_i].split("\t"))
    n = i + 1
    r[0] = str(211035 + i)
    kind = "付费" if r[7] else "免费"
    r[2] = "26马戏节活动-礼包%s%d" % (kind, (n + 1) // 2)
    r[13] = str(211035 + i)
    if len(r) > 35 and r[35]:
        r[35] = "马戏门票礼包"
    rows.append("\t".join(r))
for i in range(4):
    src_i = find_idx(lines, 13021 + i)
    r = list(lines[src_i].split("\t"))
    price = {0: "4.99", 1: "19.99", 2: "49.99", 3: "99.99"}[i]
    r[0] = str(13025 + i)
    r[2] = "马戏门票抽奖券-道具获取" + price
    r[13] = str(13025 + i)
    if len(r) > 35:
        r[35] = "马戏门票"  # c35 主数据名=所发券道具名,无尾空格
    rows.append("\t".join(r))
anchor = find_idx(lines, 211031)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("Pack OK: 211035-045 + 13025-028 (DK图字段沿深海占位)")

# ============ 8. ChainPack 703 ============
f = "Pack__ChainPack.tsv"
lines = read(f)
assert_absent(lines, [703], 0, "ChainPack")
i = find_idx(lines, 701)
r = list(lines[i].split("\t"))
r[0] = "703"
r[4] = "|".join(str(x) for x in range(211035, 211046))
for j in range(5, len(r)):
    if r[j] == "深海节":
        r[j] = "马戏节"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("ChainPack OK: 703 → 211035-045")

# ============ 9. ItemObtain 1209 ============
f = "ItemObtain__ItemObtain.tsv"
lines = read(f)
assert_absent(lines, [1209], 0, "ItemObtain")
i = find_idx(lines, 1200)
r = list(lines[i].split("\t"))
r[0] = "1209"; r[1] = "马戏大转盘-道具获取"; r[5] = "101026"
r[7] = "马戏大转盘"; r[8] = "通过马戏大转盘活动获取"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("ItemObtain OK: 1209 → AO101026")

# ============ 10. RuleTips 16043 ============
f = "RuleTips__RuleTips.tsv"
lines = read(f)
assert_absent(lines, [16043], 0, "RuleTips")
i = find_idx(lines, 16040)
r = list(lines[i].split("\t"))
r[0] = "16043"
for j in range(1, len(r)):
    if r[j]:
        r[j] = r[j].replace("深海藏宝图", "马戏门票").replace("深海罗盘", "马戏大转盘").replace("深海", "马戏")
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("RuleTips OK: 16043 (cell仅备注,真文本走TXT key)")

# ============ 11. ActvOnline 101026 ============
f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
assert_absent(lines, [101026], 0, "AO")
i = find_idx(lines, 101025)
r = list(lines[i].split("\t"))
r[0] = "101026"; r[2] = "马戏大转盘"
r[3] = "马戏大转盘转动，有机会赢取马戏节珍稀外显！"
r[4] = "1026"; r[13] = "16043"; r[20] = "2003"; r[31] = "703"
r[33] = "1209|1210"; r[38] = "142"; r[44] = "1209,2022"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("AO OK: 101026 (TC=1830沿深海占位口径,c33=1209|1210,hub=142)")

# ============ 12. i18n ============
f = "i18n/Text__Text.tsv"
lines = read(f)
key_of = lambda ln: ln.split("\t", 1)[0]
existing = set()
for ln in lines:
    if ln:
        existing.update(key_of(ln).split("|"))

def langs_of(key):
    """从(可能复合key的)现有行提取16语列"""
    for ln in lines:
        if ln and key in key_of(ln).split("|"):
            fl = ln.split("\t")
            return fl[3:19]
    raise AssertionError("找不到源key: " + key)

new_rows = []
def add(key, langs16):
    assert key not in existing, key + " 已存在"
    assert len(langs16) == 16
    new_rows.append("\t".join([key, "AI", ""] + langs16 + [""] * 8))
    existing.add(key)

# 12.1 从现有翻译直接复制（零翻译风险）
add("TXT_RankCfg_RankName_2002", langs_of("TXT_RankCfg_RankName_2000"))       # 海域排名
add("TXT_RankCfg_RankName_2003", langs_of("TXT_RankCfg_RankName_2001"))       # 世界排名
add("TXT_RankCfg_RankRewardTitle_2002", langs_of("TXT_RankCfg_RankRewardTitle_2000"))
add("TXT_RankCfg_RankRewardTitle_2003", langs_of("TXT_RankCfg_RankRewardTitle_2000"))
free_pack = langs_of("TXT_Pack_Name_211021")                                   # 免费礼包
for pid in (211035, 211037, 211039, 211041, 211043, 211045):
    add("TXT_Pack_Name_%d" % pid, free_pack)
ticket = langs_of("TXT_Item_Name_1209")                                        # 马戏门票(batch1已建)
for pid in (13025, 13026, 13027, 13028):
    add("TXT_Pack_Name_%d" % pid, ticket)

# 12.2 手写16语短词
wheel = ["马戏大转盘","Circus Wheel","Ruleta del Circo","Roue du Cirque","Roda Sirkus","Zirkus-Glücksrad","서커스 룰렛","馬戲大轉盤","Цирковое колесо","Циркове колесо","サーカスルーレット","Ruota del Circo","Cyrkowe Koło","Roleta do Circo","Sirk Çarkı","วงล้อละครสัตว์"]
add("TXT_ActvOnline_ActvName_101026", wheel)
add("TXT_RuleTips_Title_16043", wheel)
add("TXT_ItemObtain_ObtainName_1209", wheel)
for n, pid in enumerate((211036, 211038, 211040, 211042, 211044), 1):
    add("TXT_Pack_Name_%d" % pid,
        ["马戏礼包%d" % n, "Circus Pack %d" % n, "Paquete del Circo %d" % n, "Pack de Cirque %d" % n,
         "Paket Sirkus %d" % n, "Zirkuspaket %d" % n, "서커스 팩 %d" % n, "馬戲禮包%d" % n,
         "Цирковой набор %d" % n, "Цирковий набір %d" % n, "サーカスパック%d" % n,
         "Pacchetto del Circo %d" % n, "Pakiet Cyrkowy %d" % n, "Pacote de Circo %d" % n,
         "Sirk Paketi %d" % n, "แพ็คละครสัตว์ %d" % n])

# 12.3 cn+en 先行、其余留空（收口批 x3-translation-automatic 统一补,禁照抄英文伪完整）
def add_cn_en(key, cn, en):
    add(key, [cn, en] + [""] * 14)

add_cn_en("TXT_ActvOnline_ActvDesc_101026",
    "马戏大转盘转动，有机会赢取<color=#2FFF2D>马戏节珍稀外显</color>等豪华奖励！",
    "Spin the Circus Wheel for a chance to win <color=#2FFF2D>rare Circus Festival cosmetics</color> and more!")
add_cn_en("TXT_RuleTips_Content_16043",
    "盛大的马戏庆典拉开帷幕，命运的大转盘已经转动，为勇敢的冒险者备好了珍稀的宝藏！\\n\\n<color=#18962D>【活动介绍】</color>\\n1.活动期间，可消耗【马戏门票】进行抽奖。\\n2.每抽奖1次，可累计1积分，达到指定积分可领取阶段奖励。\\n3.活动结束后，未使用的【马戏门票】将被按照每个100钻石的价格进行回收。\\n4.活动期间，将根据累计获得的积分进行排名，在活动结束时，排名奖励将通过邮件发放。",
    "The grand Circus Festival begins! The Wheel of Fortune is spinning, with rare treasures prepared for brave adventurers!\\n\\n<color=#18962D>[Event Info]</color>\\n1. During the event, spend [Circus Ticket] to draw.\\n2. Each draw grants 1 point. Reach point milestones to claim stage rewards.\\n3. After the event, unused [Circus Ticket] will be recycled at 100 Diamonds each.\\n4. Rank by total points earned; ranking rewards will be sent via mail when the event ends.")
add_cn_en("TXT_ItemObtain_ObtainDesc_1209", "通过马戏大转盘活动获取", "Obtain from the Circus Wheel event")

tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(new_rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Text OK: %d key 新增(3个长文本仅cn+en,收口批补14语)" % len(new_rows))
print("ALL DONE batch2")
