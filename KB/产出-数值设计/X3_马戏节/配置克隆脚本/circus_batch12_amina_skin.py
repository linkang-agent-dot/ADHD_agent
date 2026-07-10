# -*- coding: utf-8 -*-
"""批次12：开箱大奖=阿米娜「猛兽驯服者」皮肤配置链（用户2026-07-10拍板方案B）
HeroSkin 102001(克隆足球宝贝104001) + Item 5302001 + ItemObtain 100365
+ 奖池116大奖位 5304001占位→5302001 + AO101026 c33=1209|5302001(照WC钩子结构) + i18n"""
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

# 1. HeroSkin 102001（克隆104001，DK 按 _20_Skin01 命名规律占位待美术）
f = "Hero__HeroSkin.tsv"
lines = read(f)
assert not any(ln.split("\t")[0] == "102001" for ln in lines)
i = find_idx(lines, 104001)
r = list(lines[i].split("\t"))
r[0] = "102001"; r[1] = "节庆-26马戏节"; r[2] = "猛兽驯服者·阿米娜"; r[3] = "1020"
r[5] = "DK_Img_C_H_20_Skin01"; r[6] = "DK_Role_F_20_Skin01"
r[8] = "DK_Role_Pirate"          # M 形态沿基础皮(同104001沿DK_Role_M_40惯例)
r[9] = "DK_Role_C_20_Skin01"
r[11] = "5302001"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("HeroSkin OK: 102001 猛兽驯服者·阿米娜 (皮肤DK按_20_Skin01规律占位待美术,属性组220003沿WC档)")

# 2. Item 5302001
f = "Item__Item.tsv"
lines = read(f)
assert not any(ln.split("\t")[0] == "5302001" for ln in lines)
i = find_idx(lines, 5304001)
r = list(lines[i].split("\t"))
r[0] = "5302001"; r[1] = "猛兽驯服者·阿米娜"; r[2] = "26马戏节"
r[3] = "使用后可获得阿米娜的专属皮肤——猛兽驯服者！"
r[8] = "102001|-1"; r[10] = "100365"; r[11] = "通过马戏福箱活动可获得"
r[20] = "DK_Img_C_H_20_Skin01"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("Item OK: 5302001")

# 3. ItemObtain 100365
f = "ItemObtain__ItemObtain.tsv"
lines = read(f)
assert not any(ln.split("\t")[0] == "100365" for ln in lines)
i = find_idx(lines, 100364)
r = list(lines[i].split("\t"))
r[0] = "100365"; r[1] = "26马戏-英雄皮肤"; r[7] = "猛兽驯服者"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("ItemObtain OK: 100365 → AO101026")

# 4. 奖池116 大奖位 swap
f = "ActvCrafting__ActvCraftingReward.tsv"
lines = read(f)
n = 0
for i, ln in enumerate(lines):
    fl = ln.split("\t")
    if len(fl) > 3 and fl[1] == "116" and fl[2] == "5304001":
        fl[2] = "5302001"; fl[3] = "猛兽驯服者·阿米娜(核心大奖)"
        lines[i] = "\t".join(fl); n += 1
assert n == 1, "预期1处大奖占位, 实际%d" % n
write(f, lines)
print("奖池116 OK: 大奖位→5302001")

# 5. AO101026 c33 → 券|皮肤(照WC钩子结构)
f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
i = find_idx(lines, 101026)
r = list(lines[i].split("\t"))
assert r[33] == "1209|1210", "c33 预期1209|1210, 实为" + r[33]
r[33] = "1209|5302001"
lines[i] = "\t".join(r)
write(f, lines)
print("AO101026 c33 OK: 1209|5302001 (券|皮肤钩子)")

# 6. i18n
f = "i18n/Text__Text.tsv"
lines = read(f)
existing = set()
for ln in lines:
    if ln:
        existing.update(ln.split("\t", 1)[0].split("|"))
NAME = ["猛兽驯服者·阿米娜","Beast Tamer Amina","Domadora de Fieras Amina","Dompteuse Amina","Penjinak Buas Amina","Bestienzähmerin Amina","맹수 조련사 아미나","猛獸馴服者·阿米娜","Укротительница Амина","Приборкувачка Аміна","猛獣使い・アミナ","Domatrice Amina","Poskramiaczka Amina","Domadora Amina","Vahşi Hayvan Terbiyecisi Amina","อามีนา ผู้ฝึกสัตว์ร้าย"]
rows = []
def add(key, l16):
    assert key not in existing, key
    rows.append("\t".join([key, "AI", ""] + l16 + [""] * 8))
    existing.add(key)
add("TXT_HeroSkin_Name_102001", NAME)
add("TXT_Item_Name_5302001", NAME)
add("TXT_Item_Desc_5302001",
    ["使用后可获得阿米娜的专属皮肤——猛兽驯服者！",
     "Use to obtain Amina's exclusive skin — Beast Tamer!"] + [""] * 14)
add("TXT_ItemObtain_ObtainName_100365", NAME)
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("i18n OK: 4 key")
print("ALL DONE batch12")
