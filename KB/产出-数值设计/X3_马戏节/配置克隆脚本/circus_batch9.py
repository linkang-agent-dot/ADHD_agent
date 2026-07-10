# -*- coding: utf-8 -*-
"""马戏节换皮 批次9(收口①)：补大富翁成就礼包链 + 累充白名单全量
成就包: Pack 2801012-022(11包) + Reward 1028031-036(6组) + AchievePack 105(挂CID2803)
白名单: AO100599 c49 = 全部马戏付费包39个一次配全"""
import io, sys
sys.stdout.reconfigure(encoding="utf-8")

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
def assert_absent(lines, ids, label):
    s = set(str(x) for x in ids)
    for ln in lines:
        if ln.split("\t")[0] in s:
            raise AssertionError("%s 已存在: %s" % (label, ln.split("\t")[0]))

NAME_MAP = {"深海寻宝礼包": "马戏寻宝礼包", "深海珍藏礼包": "马戏珍藏礼包", "深渊至宝礼包": "庆典至宝礼包"}

# ---- 1. Reward 组 1028031-036（克隆1028021-026, 纪念卡180080→180081, 罗盘沿用）----
f = "Reward__Reward.tsv"
lines = read(f)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[1].isdigit() and 1028031 <= int(fl[1]) <= 1028036:
        raise AssertionError("Reward组已占: " + fl[1])
mx = 0
for ln in lines:
    fl = ln.split("\t")
    if fl[0].isdigit():
        mx = max(mx, int(fl[0]))
seq = mx + 1
out = []
for g in range(1028021, 1028027):
    for r in [ln.split("\t") for ln in lines if len(ln.split("\t")) > 1 and ln.split("\t")[1] == str(g)]:
        r = list(r)
        old = r[0]
        r[0] = str(seq); r[1] = str(g + 10)
        if r[3] == "180080":
            r[3] = "180081"; r[4] = "纪念卡-欢乐颂歌"
        for j in range(4, len(r)):
            if r[j] == old:
                r[j] = str(seq)
            elif "深海" in r[j]:
                r[j] = "26马戏节-大富翁成就礼包"
        out.append("\t".join(r)); seq += 1
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(out)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Reward OK: 组1028031-036 %d行 seq..%d" % (len(out), seq - 1))

# ---- 2. Pack 2801012-022 ----
f = "Pack__Pack.tsv"
lines = read(f)
assert_absent(lines, range(2801012, 2801023), "Pack")
rows = []
for i in range(11):
    src_id = 2801001 + i
    idx = find_idx(lines, src_id)
    r = list(lines[idx].split("\t"))
    r[0] = str(2801012 + i)
    r[2] = r[2].replace("大富翁成就礼包", "马戏大富翁成就礼包")
    r[13] = str(int(r[13]) + 10)   # 1028021-026 → 1028031-036
    if len(r) > 35 and r[35] in NAME_MAP:
        r[35] = NAME_MAP[r[35]]
    rows.append("\t".join(r))
anchor = find_idx(lines, 2801011)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("Pack OK: 2801012-022 (价格档102..115照深海)")

# ---- 3. AchievePack 105 ----
f = "Pack__AchievePack.tsv"
lines = read(f)
assert_absent(lines, [105], "AchievePack")
i = find_idx(lines, 104)
r = list(lines[i].split("\t"))
r[0] = "105"
r[1] = "TXT_AchievePack_VoyageVoyage_Name_105"
r[4] = "|".join(str(x) for x in range(2801012, 2801023))
r[5] = "2803"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("AchievePack OK: 105 挂CID2803 (DK图沿深海占位)")

# ---- 4. 累充白名单全量（AO100599 c49 = 39包）----
f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
i = find_idx(lines, 100599)
r = list(lines[i].split("\t"))
whitelist = (
    [800010, 800011, 800012, 800013, 800014]                # 每日礼包5
    + [130044, 130045, 130047, 130048]                       # BP付费包4
    + [211032, 211033, 211034]                               # 装饰3
    + [211046]                                               # 拜访门头1
    + [211036, 211038, 211040, 211042, 211044]               # 转盘连锁付费5
    + [1002001]                                              # 许愿礼包(跨节日共用)
    + [2026101, 2026102, 2026103, 2026104]                   # 周卡4档(复用109101)
    + list(range(2801012, 2801023))                          # 大富翁成就11
    + [280002]                                               # 存钱罐1
    + [13025, 13026, 13027, 13028]                           # 锚点4
)
assert len(whitelist) == len(set(whitelist)) == 39
r[49] = "|".join(str(x) for x in whitelist)
lines[i] = "\t".join(r)
write(f, lines)
print("白名单 OK: AO100599 c49 = 39包")

# ---- 5. i18n ----
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
    return None
def add(key, l16):
    assert key not in existing, key
    rows.append("\t".join([key, "AI", ""] + l16 + [""] * 8))
    existing.add(key)

src = langs_of("TXT_AchievePack_VoyageVoyage_Name_104")
add("TXT_AchievePack_VoyageVoyage_Name_105", src or ["大富翁成就礼包", "Monopoly Achievement Packs"] + [""] * 14)
# 11 成就包名（三种：寻宝/珍藏/至宝）
n1 = ["马戏寻宝礼包","Circus Treasure Pack","Paquete de Tesoros del Circo","Pack de Trésors du Cirque","Paket Harta Sirkus","Zirkus-Schatzpaket","서커스 보물 팩","馬戲尋寶禮包","Цирковой набор сокровищ","Цирковий набір скарбів","サーカス宝探しパック","Pacchetto Tesori del Circo","Cyrkowy Pakiet Skarbów","Pacote de Tesouros do Circo","Sirk Hazine Paketi","แพ็คล่าสมบัติละครสัตว์"]
n2 = ["马戏珍藏礼包","Circus Collection Pack","Paquete de Colección del Circo","Pack de Collection du Cirque","Paket Koleksi Sirkus","Zirkus-Sammlerpaket","서커스 소장 팩","馬戲珍藏禮包","Цирковой коллекционный набор","Цирковий колекційний набір","サーカス珍蔵パック","Pacchetto Collezione del Circo","Cyrkowy Pakiet Kolekcjonerski","Pacote de Coleção do Circo","Sirk Koleksiyon Paketi","แพ็คสะสมละครสัตว์"]
n3 = ["庆典至宝礼包","Festival Jewel Pack","Paquete Joya del Festival","Pack Joyau du Festival","Paket Permata Festival","Festjuwelen-Paket","축제의 지보 팩","慶典至寶禮包","Праздничный набор драгоценностей","Святковий набір коштовностей","祭典至宝パック","Pacchetto Gioiello del Festival","Pakiet Klejnotów Festiwalu","Pacote Joia do Festival","Festival Mücevher Paketi","แพ็คสุดยอดสมบัติเทศกาล"]
# 深海命名分布: 2801001-004寻宝/2801005珍藏/2801006-011至宝 → 马戏同分布
for pid in range(2801012, 2801016):
    add("TXT_Pack_Name_%d" % pid, n1)
add("TXT_Pack_Name_2801016", n2)
for pid in range(2801017, 2801023):
    add("TXT_Pack_Name_%d" % pid, n3)
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Text OK: %d key" % len(rows))
print("ALL DONE batch9a")
