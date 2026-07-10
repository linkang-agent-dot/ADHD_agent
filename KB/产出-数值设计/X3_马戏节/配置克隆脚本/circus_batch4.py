# -*- coding: utf-8 -*-
"""马戏节换皮 批次4：双BP
AO102250/102251 + BattlePassScore 2250/2251 + 等级组148/149(满级重算3000/级=6万)
+ 轨道Reward克隆 4034段→4036段 / 4035段→4037段 + 付费包130044/045/047/048 + i18n
铁律：BP行id=组×100+等级；克隆新Reward块禁改共享；任务组501-506|601|602共享沿用(Count不动,分数端解决满级)。"""
import io, re

REPO = r"C:\x3\gdconfig-circus"
P = lambda f: REPO + "\\tsv\\" + f

def read(f):
    return io.open(P(f), "r", encoding="utf-8", newline="").read().split("\n")

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

SWAP = {"1200": "1209", "1201": "1210"}
NAME = {"深海藏宝图": "马戏门票", "深海宝珠": "马戏勋章", "深海罗盘券": "马戏门票"}

# ---- 1. Reward 轨道块：4034xxx→4036xxx(BP①) / 4035xxx→4037xxx(BP②) ----
f = "Reward__Reward.tsv"
lines = read(f)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and re.match(r"^403[67]\d{3}$", fl[1]):
        raise AssertionError("4036/4037 段已占: " + fl[1])
mx = 0
for ln in lines:
    fl = ln.split("\t")
    if fl[0].isdigit():
        mx = max(mx, int(fl[0]))
seq = mx + 1
print("Reward seq 起点:", seq)
out = []
n34 = n35 = 0
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and re.match(r"^403[45]\d{3}$", fl[1]):
        r = list(fl)
        old = r[0]
        r[0] = str(seq)
        newg = str(int(r[1]) + 2000)  # 4034xxx+2000=4036xxx / 4035xxx+2000=4037xxx
        r[1] = newg
        if r[3] in SWAP:
            r[3] = SWAP[r[3]]
            if r[4] in NAME:
                r[4] = NAME[r[4]]
        for i in range(4, len(r)):
            if "深海" in r[i] or "航海通行证" in r[i]:
                r[i] = "26马戏节-BP轨道奖励"
            if r[i] == old:
                r[i] = str(seq)
        out.append("\t".join(r))
        seq += 1
        if newg.startswith("4036"):
            n34 += 1
        else:
            n35 += 1
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(out)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Reward OK: 4036段%d行 + 4037段%d行, seq..%d" % (n34, n35, seq - 1))

# ---- 2. BPScoreReward 组148/149（满级重算：3000/级×20=60000 世界杯口径）----
f = "ActvBattlePassScore__BattlePassScoreReward.tsv"
lines = read(f)
assert_absent(lines, list(range(14801, 14821)) + list(range(14901, 14921)), "BPScoreReward")
src142 = {int(ln.split("\t")[2]): ln.split("\t") for ln in lines if len(ln.split("\t")) > 2 and ln.split("\t")[1] == "142"}
src144 = {int(ln.split("\t")[2]): ln.split("\t") for ln in lines if len(ln.split("\t")) > 2 and ln.split("\t")[1] == "144"}
assert len(src142) == 20 and len(src144) == 20
rows = []
for grp, src, base in ((148, src142, 4036000 - 4034000), (149, src144, 4037000 - 4035000)):
    for lv in range(1, 21):
        r = list(src[lv])
        r[0] = str(grp * 100 + lv)          # 硬契约: 行id=组×100+等级
        r[1] = str(grp)
        r[3] = "3000"                        # 满级重算: 3000/级 平铺(世界杯口径)
        r[4] = str(int(r[4]) + base)
        r[5] = str(int(r[5]) + base)
        r[6] = str(int(r[6]) + base)
        rows.append("\t".join(r))
anchor = find_idx(lines, 14420)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("BPScoreReward OK: 组148/149 各20级, Count=3000/级(满级6万)")

# ---- 3. Pack 130044/045/047/048 ----
f = "Pack__Pack.tsv"
lines = read(f)
assert_absent(lines, [130044, 130045, 130047, 130048], "Pack")
spec = [
    (130046, 130044, "马戏节-高级通行证", "马戏节高级通行证"),
    (130035, 130045, "马戏节-至尊通行证", "马戏节至尊通行证"),
    (130036, 130047, "马戏巡游-高级通行证", "马戏巡游高级通行证"),
    (130037, 130048, "马戏巡游-至尊通行证", "马戏巡游至尊通行证"),
]
rows = []
for src_id, new_id, note, c35 in spec:
    i = find_idx(lines, src_id)
    r = list(lines[i].split("\t"))
    r[0] = str(new_id); r[2] = note
    if len(r) > 35:
        r[35] = c35
    rows.append("\t".join(r))
anchor = find_idx(lines, 130046)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("Pack OK: 130044/045(BP1) 130047/048(BP2), price档照深海107/111")

# ---- 4. BattlePassScore 2250/2251 ----
f = "ActvBattlePassScore__BattlePassScore.tsv"
lines = read(f)
assert_absent(lines, [2250, 2251], "BattlePassScore")
i44 = find_idx(lines, 2244)
i46 = find_idx(lines, 2246)
r = list(lines[i44].split("\t"))
r[0] = "2250"; r[1] = "26马戏节-BP"; r[4] = "130044|130045"; r[5] = "148"
row2250 = "\t".join(r)
r = list(lines[i46].split("\t"))
r[0] = "2251"; r[1] = "马戏巡游-BP"; r[4] = "130047|130048"; r[5] = "149"
row2251 = "\t".join(r)
pos = max(i44, i46) + 1
lines[pos:pos] = [row2250, row2251]
write(f, lines)
print("BattlePassScore OK: 2250/2251 (任务组501-506|601|602共享沿用)")

# ---- 5. AO 102250/102251 ----
f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
assert_absent(lines, [102250, 102251], "AO")
i = find_idx(lines, 102244)
r = list(lines[i].split("\t"))
r[0] = "102250"; r[2] = "马戏手记"; r[3] = "完成马戏庆典任务，领取豪华奖励！"
r[4] = "2250"; r[33] = "1209|1210"; r[38] = "142"
row_a = "\t".join(r)
i = find_idx(lines, 102246)
r = list(lines[i].split("\t"))
r[0] = "102251"; r[2] = "巡游通行证"; r[3] = "参与马戏巡游，解锁通行证豪华奖励！"
r[4] = "2251"; r[33] = "1057|1202"; r[38] = "143"
row_b = "\t".join(r)
i = find_idx(lines, 102246)
lines[i + 1:i + 1] = [row_a, row_b]
write(f, lines)
print("AO OK: 102250马戏手记(hub142) / 102251巡游通行证(hub143); RuleTips1017通用沿用")

# ---- 6. i18n ----
f = "i18n/Text__Text.tsv"
lines = read(f)
existing = set()
for ln in lines:
    if ln:
        existing.update(ln.split("\t", 1)[0].split("|"))
rows = []
def add(key, l16):
    assert key not in existing, key
    rows.append("\t".join([key, "AI", ""] + l16 + [""] * 8))
    existing.add(key)

add("TXT_ActvOnline_ActvName_102250",
    ["马戏手记","Circus Journal","Diario del Circo","Carnet du Cirque","Jurnal Sirkus","Zirkustagebuch","서커스 일지","馬戲手記","Цирковой дневник","Цирковий щоденник","サーカス手記","Diario del Circo","Dziennik Cyrkowy","Diário de Circo","Sirk Günlüğü","บันทึกละครสัตว์"])
add("TXT_ActvOnline_ActvName_102251",
    ["巡游通行证","Parade Pass","Pase del Desfile","Pass de Parade","Tiket Parade","Paraden-Pass","퍼레이드 패스","巡遊通行證","Парадный пропуск","Парадна перепустка","パレードパス","Pass della Parata","Przepustka Parady","Passe de Desfile","Geçit Bileti","บัตรผ่านพาเหรด"])
def pass_names(prefix_cn, prefix_tw, adv):
    if adv:
        return [prefix_cn+"高级通行证","Advanced Pass","Pase Avanzado","Pass Avancé","Tiket Lanjutan","Premium-Pass","고급 패스",prefix_tw+"高級通行證","Продвинутый пропуск","Просунута перепустка","上級パス","Pass Avanzato","Przepustka Zaawansowana","Passe Avançado","Gelişmiş Bilet","บัตรผ่านขั้นสูง"]
    return [prefix_cn+"至尊通行证","Supreme Pass","Pase Supremo","Pass Suprême","Tiket Tertinggi","Supreme-Pass","최상급 패스",prefix_tw+"至尊通行證","Высший пропуск","Найвища перепустка","極上パス","Pass Supremo","Przepustka Najwyższa","Passe Supremo","Üstün Bilet","บัตรผ่านสูงสุด"]
add("TXT_Pack_Name_130044", pass_names("马戏节","馬戲節", True))
add("TXT_Pack_Name_130045", pass_names("马戏节","馬戲節", False))
add("TXT_Pack_Name_130047", pass_names("马戏巡游","馬戲巡遊", True))
add("TXT_Pack_Name_130048", pass_names("马戏巡游","馬戲巡遊", False))
add("TXT_ActvOnline_ActvDesc_102250", ["完成马戏庆典任务，领取豪华奖励！","Complete Circus Festival tasks to claim luxurious rewards!"] + [""] * 14)
add("TXT_ActvOnline_ActvDesc_102251", ["参与马戏巡游，解锁通行证豪华奖励！","Join the Circus Parade and unlock luxurious pass rewards!"] + [""] * 14)
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Text OK: 8 key")
print("ALL DONE batch4")
