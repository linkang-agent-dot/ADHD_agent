# -*- coding: utf-8 -*-
"""批次10：转盘→开箱返工（克隆源=世界杯101516，用户2026-07-10拍板）+ BP改名
拆：ActvLuckyWheel 1026 / LWReward组322 / LWOtherReward组3021（全部为批次2自建行）
建：ActvCrafting 1517 + CraftingReward组116 + CraftingOtherReward组1016(→复用Reward30940-46)
改：AO 101026 转 type15 开箱；i18n 马戏大转盘→马戏福箱；BP 马戏手记→马戏通行证
保留复用：双榜2002/2003 / 连锁703 / 锚点13025-028 / ItemObtain1209 / Reward组30940-46"""
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

# ---- 1. 拆转盘三件（只删自建行，断言计数）----
f = "ActvLuckyWheel__ActvLuckyWheel.tsv"
lines = read(f)
n0 = len(lines)
lines = [ln for ln in lines if ln.split("\t")[0] != "1026"]
assert n0 - len(lines) == 1
write(f, lines)

f = "ActvLuckyWheel__ActvLuckyWheelReward.tsv"
lines = read(f)
n0 = len(lines)
lines = [ln for ln in lines if not (len(ln.split("\t")) > 1 and ln.split("\t")[1] == "322")]
assert n0 - len(lines) == 10
write(f, lines)

f = "ActvLuckyWheel__ActvLuckyWheelOtherReward.tsv"
lines = read(f)
n0 = len(lines)
lines = [ln for ln in lines if not (len(ln.split("\t")) > 1 and ln.split("\t")[1] == "3021")]
assert n0 - len(lines) == 7
write(f, lines)
print("拆除 OK: LuckyWheel1026 + 组322x10 + 组3021x7")

# ---- 2. CraftingReward 组116（克隆115：金币→勋章，皮肤大奖占位保留）----
f = "ActvCrafting__ActvCraftingReward.tsv"
lines = read(f)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[1] == "116":
        raise AssertionError("组116已占")
src = [ln.split("\t") for ln in lines if len(ln.split("\t")) > 1 and ln.split("\t")[1] == "115"]
assert len(src) == 9
rows = []
for r in src:
    r = list(r)
    r[0] = str(11600 + int(r[0]) - 11500)
    r[1] = "116"
    if r[2] == "1147":
        r[2] = "1210"; r[3] = "马戏勋章"
    elif r[2] == "5304001":
        r[3] = "英雄皮肤大奖占位(待定英雄,足球宝贝暂占)"
    rows.append("\t".join(r))
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("CraftingReward OK: 组116 x9 (保底勋章x500/大奖5304001占位待英雄定案)")

# ---- 3. CraftingOtherReward 组1016（NeedTime 照WC 50..1500，奖励=复用组30940-46）----
f = "ActvCrafting__ActvCraftingOtherReward.tsv"
lines = read(f)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[1] == "1016":
        raise AssertionError("组1016已占")
mx = 0
for ln in lines:
    fl = ln.split("\t")
    if fl[0].isdigit():
        mx = max(mx, int(fl[0]))
src = [ln.split("\t") for ln in lines if len(ln.split("\t")) > 1 and ln.split("\t")[1] == "1015"]
assert len(src) == 7
rows = []
for n, r in enumerate(src):
    r = list(r)
    r[0] = str(mx + 1 + n)
    r[1] = "1016"
    r[2] = str(30940 + n)   # 复用批次2阶段奖组(马戏勋章50..3000)
    rows.append("\t".join(r))
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("CraftingOtherReward OK: 组1016 x7 → Reward30940-46 复用")

# ---- 4. ActvCrafting 1517 ----
f = "ActvCrafting__ActvCrafting.tsv"
lines = read(f)
for ln in lines:
    if ln.split("\t")[0] == "1517":
        raise AssertionError("1517已占")
i = find_idx(lines, 1516)
r = list(lines[i].split("\t"))
r[0] = "1517"; r[1] = "1209"; r[3] = "1210"; r[4] = "116"; r[5] = "1016"; r[6] = "2002"
if len(r) > 10:
    r[10] = "马戏福箱"
# [7][8]开关箱DK沿WC占位待美术; [9]BottomBg沿用
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("ActvCrafting OK: 1517 (耗1209/产1210/池116/阶梯1016/本服榜2002; 箱体DK沿WC占位)")

# ---- 5. AO 101026 改造成开箱（照 WC 101516 形状原位改列）----
f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
i = find_idx(lines, 101026)
r = list(lines[i].split("\t"))
assert r[5] == "10", "AO101026 type非10?"
r[2] = "马戏福箱"
r[3] = "开启马戏福箱，有机会赢取马戏节珍稀外显！"
r[4] = "1517"      # CID → ActvCrafting
r[5] = "15"        # type 转盘10→开箱15
r[7] = "0"         # TC 1830→0 (WC口径部署驱动)
r[9] = ""          # 转盘专属参数清空(照WC列形)
wc = None
for ln in lines:
    if ln.split("\t")[0] == "101516":
        wc = ln.split("\t")
        break
r[9] = wc[9]       # 该列照WC值
r[17] = "101109"
r[18] = wc[18]     # 跨服=1
r[28] = wc[28]; r[29] = wc[29]; r[30] = wc[30]  # 显示类列照WC
# 保留: [13]=16043 [20]=2003 [31]=703 [33]=1209|1210 [38]=142 [44]=1209,2022
lines[i] = "\t".join(r)
write(f, lines)
print("AO OK: 101026 → type15开箱 CID1517 TC=0 跨服榜2003 本服榜挂Crafting")

# ---- 6. ItemObtain 1209 文本 + RuleTips 16043 备注 ----
f = "ItemObtain__ItemObtain.tsv"
lines = read(f)
i = find_idx(lines, 1209)
r = list(lines[i].split("\t"))
r[1] = "马戏福箱-道具获取"; r[7] = "马戏福箱"; r[8] = "通过马戏福箱活动获取"
lines[i] = "\t".join(r)
write(f, lines)

f = "RuleTips__RuleTips.tsv"
lines = read(f)
i = find_idx(lines, 16043)
r = list(lines[i].split("\t"))
for j in range(1, len(r)):
    if r[j]:
        r[j] = r[j].replace("马戏大转盘", "马戏福箱").replace("转动", "开启").replace("抽奖", "开箱")
lines[i] = "\t".join(r)
write(f, lines)
print("ItemObtain/RuleTips备注 OK")

# ---- 7. i18n：福箱改名 + BP改名 ----
f = "i18n/Text__Text.tsv"
lines = read(f)
BOX = ["马戏福箱","Circus Lucky Box","Caja de la Suerte del Circo","Boîte Chance du Cirque","Kotak Keberuntungan Sirkus","Zirkus-Glücksbox","서커스 행운 상자","馬戲福箱","Цирковой счастливый сундук","Цирковий щасливий сундук","サーカスラッキーボックス","Scatola Fortunata del Circo","Cyrkowa Skrzynia Szczęścia","Caixa da Sorte do Circo","Sirk Şans Kutusu","กล่องนำโชคละครสัตว์"]
PASS = ["马戏通行证","Circus Pass","Pase del Circo","Pass du Cirque","Tiket Sirkus","Zirkus-Pass","서커스 패스","馬戲通行證","Цирковой пропуск","Циркова перепустка","サーカスパス","Pass del Circo","Przepustka Cyrkowa","Passe de Circo","Sirk Bileti","บัตรผ่านละครสัตว์"]
def replace_langs(key, langs16):
    for i, ln in enumerate(lines):
        f0 = ln.split("\t")
        if f0[0] == key:
            lines[i] = "\t".join(f0[:3] + langs16 + f0[19:])
            return True
    raise AssertionError("key缺失: " + key)
def replace_cn_en(key, cn, en):
    for i, ln in enumerate(lines):
        f0 = ln.split("\t")
        if f0[0] == key:
            lines[i] = "\t".join(f0[:3] + [cn, en] + [""] * 14 + f0[19:])
            return True
    raise AssertionError("key缺失: " + key)

replace_langs("TXT_ActvOnline_ActvName_101026", BOX)
replace_langs("TXT_RuleTips_Title_16043", BOX)
replace_langs("TXT_ItemObtain_ObtainName_1209", BOX)
replace_langs("TXT_ActvOnline_ActvName_102250", PASS)   # 马戏手记→马戏通行证(用户拍板)
replace_cn_en("TXT_ActvOnline_ActvDesc_101026",
    "开启马戏福箱，有机会赢取<color=#2FFF2D>马戏节珍稀外显</color>等豪华奖励！",
    "Open the Circus Lucky Box for a chance to win <color=#2FFF2D>rare Circus Festival cosmetics</color> and more!")
replace_cn_en("TXT_RuleTips_Content_16043",
    "盛大的马戏庆典拉开帷幕，神秘的福箱已经就位，为勇敢的冒险者备好了珍稀的宝藏！\\n\\n<color=#18962D>【活动介绍】</color>\\n1.活动期间，可消耗【马戏门票】开启福箱。\\n2.每开箱1次，可累计1积分，达到指定积分可领取阶段奖励。\\n3.活动结束后，未使用的【马戏门票】将被按照每个100钻石的价格进行回收。\\n4.活动期间，将根据累计获得的积分进行排名，在活动结束时，排名奖励将通过邮件发放。",
    "The grand Circus Festival begins! Mysterious lucky boxes await, filled with rare treasures for brave adventurers!\\n\\n<color=#18962D>[Event Info]</color>\\n1. During the event, spend [Circus Ticket] to open boxes.\\n2. Each opening grants 1 point. Reach point milestones to claim stage rewards.\\n3. After the event, unused [Circus Ticket] will be recycled at 100 Diamonds each.\\n4. Rank by total points earned; ranking rewards will be sent via mail when the event ends.")
replace_cn_en("TXT_Item_Desc_1209",
    "马戏门票，凭票开启马戏福箱，赢取珍稀奖励！",
    "A Circus Ticket. Use it to open the Circus Lucky Box and win rare rewards!")
write(f, lines)
print("i18n OK: 福箱16语x3 + 马戏通行证16语 + 3长文本cn+en")

# Item desc cell 同步
f = "Item__Item.tsv"
lines = read(f)
i = find_idx(lines, 1209)
r = list(lines[i].split("\t"))
r[3] = "马戏门票，凭票开启马戏福箱，赢取珍稀奖励！"
lines[i] = "\t".join(r)
write(f, lines)
print("Item1209 desc cell OK")
print("ALL DONE batch10")
