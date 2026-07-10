# -*- coding: utf-8 -*-
"""马戏节换皮 批次6：每日礼包 AO102994 + 酒馆 AO10071705
每日礼包: TC160101+Pack800010-014+ActvPack3003+Reward40520/40620+**MailID=101109**(修X3NEW-1829事故口径)
酒馆: ScoreID720(ScoreMulti 7201-07+ScoreGroup 72011-74+Reward786045-048)"""
import io

REPO = r"C:\x3\gdconfig-circus"
P = lambda f: REPO + "\\tsv\\" + f
read = lambda f: io.open(P(f), "r", encoding="utf-8", newline="").read().split("\n")
def write(f, lines):
    io.open(P(f), "w", encoding="utf-8", newline="").write("\n".join(lines))
def find_idx(lines, rid):
    for i, ln in enumerate(lines):
        if ln.split("\t")[0] == str(rid):
            return i
    raise AssertionError("源行缺失: %s" % rid)
def assert_absent(lines, ids, label, col=0):
    s = set(str(x) for x in ids)
    for ln in lines:
        fl = ln.split("\t")
        if len(fl) > col and fl[col] in s:
            raise AssertionError("%s 已存在: %s" % (label, fl[col]))

# ---- 1. Reward: 40520/40620(每日礼包) + 786045-048(酒馆) ----
f = "Reward__Reward.tsv"
lines = read(f)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[1] in ("40520", "40620", "786045", "786046", "786047", "786048"):
        raise AssertionError("Reward组已占: " + fl[1])
mx = 0
for ln in lines:
    fl = ln.split("\t")
    if fl[0].isdigit():
        mx = max(mx, int(fl[0]))
seq = mx + 1
print("Reward seq 起点:", seq)
out = []
def clone(src_g, dst_g, note):
    global seq
    src = [ln.split("\t") for ln in lines if len(ln.split("\t")) > 1 and ln.split("\t")[1] == str(src_g)]
    assert src, "源组空:%s" % src_g
    for r in src:
        r = list(r)
        old = r[0]
        r[0] = str(seq); r[1] = str(dst_g)
        if r[3] == "1200":
            r[3] = "1209"
            if r[4]:
                r[4] = "马戏门票"
        for i in range(4, len(r)):
            if r[i] == old:
                r[i] = str(seq)
            elif "深海" in r[i]:
                r[i] = note
        out.append("\t".join(r)); seq += 1
clone(40500, 40520, "马戏每日礼包")
clone(40600, 40620, "马戏每日礼包-买全终奖")
for i in range(4):
    clone(786035 + i, 786045 + i, "马戏酒馆-阶段积分奖")
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(out)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Reward OK: %d行 seq..%d" % (len(out), seq - 1))

# ---- 2. TimeCycle 160101 ----
f = "TimeCycle__TimeCycle.tsv"
lines = read(f)
assert_absent(lines, [160101], "TC")
i = find_idx(lines, 160100)
r = list(lines[i].split("\t"))
r[0] = "160101"
for j in range(1, len(r)):
    if "深海" in r[j]:
        r[j] = r[j].replace("深海", "马戏")
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("TC OK: 160101 (TrigT=5触发式/7天, type29合法)")

# ---- 3. Pack 800010-014 ----
f = "Pack__Pack.tsv"
lines = read(f)
assert_absent(lines, range(800010, 800015), "Pack")
rows = []
for i in range(5):
    idx = find_idx(lines, 800005 + i)
    r = list(lines[idx].split("\t"))
    r[0] = str(800010 + i)
    r[2] = "马戏每日礼包-第%d日" % (i + 1)
    r[13] = "40520"
    if len(r) > 35 and r[35]:
        r[35] = "马戏每日礼包"
    rows.append("\t".join(r))
anchor = find_idx(lines, 800009)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("Pack OK: 800010-014 ($4.99x5, content=40520)")

# ---- 4. ActvPack 3003 ----
f = "ActvPack__ActvPack.tsv"
lines = read(f)
assert_absent(lines, [3003], "ActvPack")
i = find_idx(lines, 3002)
r = list(lines[i].split("\t"))
r[0] = "3003"
r[2] = "|".join(str(x) for x in range(800010, 800015))
r[3] = "40620"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("ActvPack OK: 3003 (5包+Final=40620)")

# ---- 5. 酒馆 ScoreMulti 7201-07 + ScoreGroup ----
f = "ActvScore__ActvScoreMulti.tsv"
lines = read(f)
assert_absent(lines, range(7201, 7208), "ScoreMulti")
rows = []
for i in range(7):
    idx = find_idx(lines, 7191 + i)
    r = list(lines[idx].split("\t"))
    r[0] = str(7201 + i)
    r[1] = "26马戏节-跨服酒馆"
    r[2] = "720"
    r[6] = str(7201 + i)
    rows.append("\t".join(r))
anchor = find_idx(lines, 7197)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("ScoreMulti OK: 7201-07 (CID720, 阶段时长1+1+2+1+2+1+2=10天硬约束, 任务/榜共享沿用)")

f = "ActvScore__ActvScoreGroup.tsv"
lines = read(f)
new_ids = [int("72%d%d" % (g, d)) for g in range(1, 8) for d in range(1, 5)]
assert_absent(lines, new_ids, "ScoreGroup")
rows = []
for g in range(7):
    for d in range(4):
        src_id = int("719%d%d" % (g + 1, d + 1))
        idx = find_idx(lines, src_id)
        r = list(lines[idx].split("\t"))
        r[0] = str(int("72%d%d" % (g + 1, d + 1)))
        r[1] = str(7201 + g)
        r[3] = str(786045 + d)
        r[4] = "26马戏节-跨服酒馆-阶段%d" % (g + 1)
        rows.append("\t".join(r))
anchor = find_idx(lines, 71974)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("ScoreGroup OK: 7211-7274 共28行 (AimScore照深海1/3/5/7万)")

# ---- 6. AO 102994 + 10071705 ----
f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
assert_absent(lines, [102994, 10071705], "AO")
i = find_idx(lines, 102993)
r = list(lines[i].split("\t"))
r[0] = "102994"; r[2] = "马戏每日礼包"
r[4] = "3003"; r[7] = "160101"
r[17] = "101109"   # ★MailID 兜底(深海102993留空→X3NEW-1829终奖无人领事故)
r[38] = "142"
row_daily = "\t".join(r)
i = find_idx(lines, 10071704)
r = list(lines[i].split("\t"))
r[0] = "10071705"; r[2] = "马戏酒馆"
r[3] = "参与马戏庆典活动，为你的酒馆赢得声誉！"
r[4] = "720"; r[33] = "1209|1210"; r[38] = "142"
row_tav = "\t".join(r)
i = find_idx(lines, 10071704)
lines[i + 1:i + 1] = [row_daily, row_tav]
write(f, lines)
print("AO OK: 102994(MailID=101109已配!) + 10071705(CID720)")

# ---- 7. i18n ----
f = "i18n/Text__Text.tsv"
lines = read(f)
existing = set()
for ln in lines:
    if ln:
        existing.update(ln.split("\t", 1)[0].split("|"))
rows = []
def langs_of(key):
    for ln in lines:
        if ln and key in ln.split("\t", 1)[0].split("|"):
            return ln.split("\t")[3:19]
    raise AssertionError("找不到源key: " + key)
def add(key, l16):
    assert key not in existing, key
    rows.append("\t".join([key, "AI", ""] + l16 + [""] * 8))
    existing.add(key)

add("TXT_ActvOnline_ActvName_102994", langs_of("TXT_ActvOnline_ActvName_102993"))  # 每日礼包 通用词复制
tavern = ["马戏酒馆","Circus Tavern","Taberna del Circo","Taverne du Cirque","Kedai Sirkus","Zirkustaverne","서커스 주점","馬戲酒館","Цирковая таверна","Циркова таверна","サーカス酒場","Taverna del Circo","Cyrkowa Tawerna","Taverna do Circo","Sirk Tavernası","โรงเตี๊ยมละครสัตว์"]
add("TXT_ActvOnline_ActvName_10071705", tavern)
add("TXT_ActvOnline_ActvDesc_102994", ["马戏庆典期间每日超值礼包，买满5日更有豪华大奖！","Daily value packs during the Circus Festival. Purchase all 5 days for a luxurious grand prize!"] + [""] * 14)
add("TXT_ActvOnline_ActvDesc_10071705", ["参与马戏庆典活动，为你的酒馆赢得声誉！","Join Circus Festival events to win fame for your tavern!"] + [""] * 14)
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Text OK: 4 key")
print("ALL DONE batch6")
