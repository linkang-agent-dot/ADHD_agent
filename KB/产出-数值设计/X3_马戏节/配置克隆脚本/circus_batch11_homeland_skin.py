# -*- coding: utf-8 -*-
"""批次11：主城皮肤「梦幻旋转木马」gdconfig 接线
Skin 1017(DK_Prefab=DK_Homeland_Circus·客户端已落) + Item 81152(永久) + ItemObtain 100364
+ 跨服榜奖组30960-66 的 15065 占位→81152 + i18n
奖池116大奖位仍留英雄皮肤占位(待定英雄,与本皮肤是两个奖)。"""
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

# 1. Skin 1017（克隆金字塔之城1016）
f = "Skin__Skin.tsv"
lines = read(f)
assert not any(ln.split("\t")[0] == "1017" for ln in lines)
i = find_idx(lines, 1016)
r = list(lines[i].split("\t"))
r[0] = "1017"; r[1] = "梦幻旋转木马"
r[5] = "马戏庆典活动获取"
r[7] = "DK_Homeland_Circus"          # 客户端已 Display+Path 双注册
r[8] = "DK_icon_island_Egypt"        # 2D头像图标占位待出(美需),出图后换 DK_icon_island_Circus
r[9] = str(int(r[9]) + 1)            # 展示顺序顺延
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("Skin OK: 1017 梦幻旋转木马 (头像图标占位待出)")

# 2. Item 81152（克隆81151）
f = "Item__Item.tsv"
lines = read(f)
assert not any(ln.split("\t")[0] == "81152" for ln in lines)
i = find_idx(lines, 81151)
r = list(lines[i].split("\t"))
r[0] = "81152"; r[1] = "梦幻旋转木马（永久）"
r[2] = "岛屿皮肤-26马戏节"
r[3] = "使用后可获得传说级岛屿皮肤。主城化作旋转的马戏乐园，灯火与乐声昼夜不息。"
r[8] = "1017|1|-1"
r[10] = "100364"
r[11] = "通过马戏庆典活动可获得"
# [20]图标占位沿金字塔,待美术
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("Item OK: 81152 (UseParam=1017|1|-1, Obtain=100364)")

# 3. ItemObtain 100364（克隆100316,跳马戏福箱101026）
f = "ItemObtain__ItemObtain.tsv"
lines = read(f)
assert not any(ln.split("\t")[0] == "100364" for ln in lines)
i = find_idx(lines, 100316)
r = list(lines[i].split("\t"))
r[0] = "100364"; r[1] = "26马戏-岛屿皮肤"
r[5] = "101026"; r[7] = "梦幻旋转木马"
if len(r) > 8:
    r[8] = "通过马戏福箱活动获取"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("ItemObtain OK: 100364 → AO101026")

# 4. 榜奖组30960-66 的 15065→81152
f = "Reward__Reward.tsv"
lines = read(f)
n = 0
for i, ln in enumerate(lines):
    fl = ln.split("\t")
    if len(fl) > 4 and fl[1].isdigit() and 30960 <= int(fl[1]) <= 30966 and fl[3] == "15065":
        fl[3] = "81152"; fl[4] = "梦幻旋转木马（岛屿皮肤·永久）"
        lines[i] = "\t".join(fl)
        n += 1
assert n == 6, "预期6处占位, 实际%d" % n
write(f, lines)
print("榜奖swap OK: %d处 15065→81152 (组30960-65有大奖,30966末档无·同深海)" % n)

# 5. i18n
f = "i18n/Text__Text.tsv"
lines = read(f)
existing = set()
for ln in lines:
    if ln:
        existing.update(ln.split("\t", 1)[0].split("|"))
rows = []
CAROUSEL = ["梦幻旋转木马","Dream Carousel","Carrusel de Ensueño","Carrousel de Rêve","Komidi Putar Impian","Traumkarussell","꿈의 회전목마","夢幻旋轉木馬","Карусель мечты","Карусель мрії","ドリームメリーゴーランド","Giostra dei Sogni","Karuzela Marzeń","Carrossel dos Sonhos","Rüya Atlıkarınca","ม้าหมุนแห่งความฝัน"]
def add(key, l16):
    assert key not in existing, key
    rows.append("\t".join([key, "AI", ""] + l16 + [""] * 8))
    existing.add(key)
add("TXT_HeroSkin_Name_1017", CAROUSEL)   # Skin 表名 key 族(照1016=TXT_HeroSkin_Name)
add("TXT_Item_Name_81152", [x + ("（永久）" if i == 0 else " (Permanent)" if i == 1 else "") for i, x in enumerate(CAROUSEL)])
add("TXT_Item_Desc_81152",
    ["使用后可获得传说级岛屿皮肤。主城化作旋转的马戏乐园，灯火与乐声昼夜不息。",
     "Use to obtain a Legendary island skin. Your city becomes a spinning circus wonderland, alive with lights and music day and night."] + [""] * 14)
add("TXT_ItemObtain_ObtainName_100364", CAROUSEL)
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("i18n OK: 4 key")
print("ALL DONE batch11")
