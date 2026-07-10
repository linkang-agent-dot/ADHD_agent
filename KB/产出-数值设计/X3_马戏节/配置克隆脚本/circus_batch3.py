# -*- coding: utf-8 -*-
"""马戏节换皮 批次3：累充 AO100599 + ActvTask 59911-20 + Reward组59950-59 + RuleTips16044 + i18n
白名单 c49 先填已建的 9 个付费包(连锁5+锚点4),其余收口批补全。"""
import io

REPO = r"C:\x3\gdconfig-circus"
P = lambda f: REPO + "\\tsv\\" + f

def read(f):
    with io.open(P(f), "r", encoding="utf-8", newline="") as fh:
        return fh.read().split("\n")

def write(f, lines):
    with io.open(P(f), "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines))

def find_idx(lines, rid):
    for i, ln in enumerate(lines):
        f = ln.split("\t")
        if f and f[0] == str(rid):
            return i
    raise AssertionError("源行缺失: %s" % rid)

def assert_absent(lines, ids, label):
    s = set(str(x) for x in ids)
    for ln in lines:
        f = ln.split("\t")
        if f and f[0] in s:
            raise AssertionError("%s 已存在: %s" % (label, f[0]))

# ---- 1. Reward 组 59950-59（clone 59850-59, 1200→1209, 1057 沿用）----
f = "Reward__Reward.tsv"
lines = read(f)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[1].isdigit() and 59950 <= int(fl[1]) <= 59959:
        raise AssertionError("Reward组已占: " + fl[1])
# 精确查全表真 max（must-check 新铁律）
mx = 0
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[0].isdigit():
        mx = max(mx, int(fl[0]))
seq = mx + 1
print("Reward seq 起点(真max+1):", seq)
out = []
for g in range(59850, 59860):
    src = [ln.split("\t") for ln in lines if ln.split("\t")[0].isdigit() and len(ln.split("\t")) > 1 and ln.split("\t")[1] == str(g)]
    assert src, "源组空:%d" % g
    for r in src:
        r = list(r)
        old = r[0]
        r[0] = str(seq)
        r[1] = str(g + 100)
        if r[3] == "1200":
            r[3] = "1209"; r[4] = "马戏门票"
        for i in range(5, len(r)):
            if r[i] == old:
                r[i] = str(seq)
            elif "深海" in r[i]:
                r[i] = "26马戏节-累充"
        out.append("\t".join(r))
        seq += 1
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(out)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Reward OK: 组59950-59 共%d行 seq..%d" % (len(out), seq - 1))

# ---- 2. ActvTask 59911-20 ----
f = "ActvTask__ActvTask.tsv"
lines = read(f)
assert_absent(lines, range(59911, 59921), "ActvTask")
rows = []
for tid in range(59811, 59821):
    i = find_idx(lines, tid)
    r = list(lines[i].split("\t"))
    r[0] = str(tid + 100)
    r[2] = "599"; r[5] = "599"
    r[8] = str(int(r[8]) + 100)
    rows.append("\t".join(r))
anchor = find_idx(lines, 59820)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("ActvTask OK: 59911-20 (CID599, 阈值照深海100..20000, 奖励组59950-59)")

# ---- 3. RuleTips 16044 ----
f = "RuleTips__RuleTips.tsv"
lines = read(f)
assert_absent(lines, [16044], "RuleTips")
i = find_idx(lines, 16041)
r = list(lines[i].split("\t"))
r[0] = "16044"
for j in range(1, len(r)):
    if r[j]:
        r[j] = r[j].replace("深海", "马戏")
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("RuleTips OK: 16044")

# ---- 4. AO 100599 ----
f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
assert_absent(lines, [100599], "AO")
i = find_idx(lines, 100598)
r = list(lines[i].split("\t"))
r[0] = "100599"; r[2] = "马戏累充"
r[3] = "累计充值领取马戏节珍稀奖励！"
r[4] = "599"; r[13] = "16044"
r[33] = "1209|1057"; r[38] = "142"; r[44] = "1209,2022"
r[49] = "211036|211038|211040|211042|211044|13025|13026|13027|13028"  # 白名单先填已建9包,收口批补全
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("AO OK: 100599 (TC=0, 白名单9包待收口补全)")

# ---- 5. i18n ----
f = "i18n/Text__Text.tsv"
lines = read(f)
existing = set()
for ln in lines:
    if ln:
        existing.update(ln.split("\t", 1)[0].split("|"))
new_rows = []
def add(key, langs16):
    assert key not in existing, key + " 已存在"
    new_rows.append("\t".join([key, "AI", ""] + langs16 + [""] * 8))
    existing.add(key)

recharge = ["马戏累充","Circus Top-Up Bonus","Bono de Recarga del Circo","Bonus de Recharge du Cirque","Bonus Isi Ulang Sirkus","Zirkus-Aufladebonus","서커스 누적 충전","馬戲累充","Цирковой бонус пополнения","Цирковий бонус поповнення","サーカスチャージ特典","Bonus Ricarica del Circo","Cyrkowy Bonus Doładowania","Bônus de Recarga do Circo","Sirk Yükleme Bonusu","โบนัสเติมเงินละครสัตว์"]
add("TXT_ActvOnline_ActvName_100599", recharge)
add("TXT_RuleTips_Title_16044", recharge)
add("TXT_ActvOnline_ActvDesc_100599",
    ["累计充值领取马戏节珍稀奖励！", "Top up to earn rare Circus Festival rewards!"] + [""] * 14)
add("TXT_RuleTips_Content_16044",
    ["活动期间，购买【马戏】节日系列礼包及节日通行证可获得充值积分，达到指定积分可领取丰厚奖励。",
     "During the event, purchase [Circus] festival packs and festival passes to earn top-up points. Reach point milestones to claim generous rewards."] + [""] * 14)
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(new_rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Text OK: 4 key (2长文本cn+en收口补)")
print("ALL DONE batch3")
