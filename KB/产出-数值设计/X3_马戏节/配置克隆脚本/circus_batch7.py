# -*- coding: utf-8 -*-
"""马戏节换皮 批次7：装饰链 AO106104/ChainPack702/Pack211032-034 + 兑换×2 AO101343/101344
装饰家具复用椰风遮阳椅(用户拍板);兑换货币 1201→1210 / 1202 沿用;纪念卡槽180080占位待批次8。"""
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

# ---- 1. Reward 组211032-034（装饰3档：椅子沿用+1209券+钻+VIP）----
f = "Reward__Reward.tsv"
lines = read(f)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[1] in ("211032", "211033", "211034"):
        raise AssertionError("Reward组已占: " + fl[1])
mx = 0
for ln in lines:
    fl = ln.split("\t")
    if fl[0].isdigit():
        mx = max(mx, int(fl[0]))
seq = mx + 1
out = []
for i in range(3):
    src_g = str(211016 + i)
    for r in [ln.split("\t") for ln in lines if len(ln.split("\t")) > 1 and ln.split("\t")[1] == src_g]:
        r = list(r)
        old = r[0]
        r[0] = str(seq); r[1] = str(211032 + i)
        if r[3] == "1200":
            r[3] = "1209"; r[4] = "马戏门票"
        for j in range(4, len(r)):
            if r[j] == old:
                r[j] = str(seq)
            elif "深海" in r[j] or "夏日" in r[j]:
                r[j] = "26马戏节-装饰礼包"
        out.append("\t".join(r)); seq += 1
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(out)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Reward OK: 装饰组211032-034 %d行 seq..%d" % (len(out), seq - 1))

# ---- 2. Pack 211032-034 ----
f = "Pack__Pack.tsv"
lines = read(f)
assert_absent(lines, [211032, 211033, 211034], "Pack")
rows = []
for i in range(3):
    idx = find_idx(lines, 211016 + i)
    r = list(lines[idx].split("\t"))
    r[0] = str(211032 + i)
    r[2] = "马戏装饰特惠%d" % (i + 1)
    r[13] = str(211032 + i)
    if len(r) > 35 and r[35]:
        r[35] = "马戏庆典特惠"
    rows.append("\t".join(r))
anchor = find_idx(lines, 211031)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("Pack OK: 211032-034 ($19.99x3, MainBg等图字段照源)")

# ---- 3. ChainPack 702 ----
f = "Pack__ChainPack.tsv"
lines = read(f)
assert_absent(lines, [702], "ChainPack")
i = find_idx(lines, 700)
r = list(lines[i].split("\t"))
r[0] = "702"
r[1] = "马戏庆典-装饰礼包"
r[4] = "211032|211033|211034"
for j in range(5, len(r)):
    if "深海" in r[j] or "夏日" in r[j]:
        r[j] = r[j].replace("深海", "马戏").replace("夏日647", "深海700")
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("ChainPack OK: 702 (入口图/视频DK沿深海占位——美需+2张:装饰入口图+装饰视频)")

# ---- 4. Exchange 组1343(克隆1340,币1201→1210) + 组1344(克隆1341,币1202沿用) ----
f = "ActvExchange__ActvExchange.tsv"
lines = read(f)
label_rows = {}   # 新行id -> 源行id（标签key复制用）
def clone_ex(src_g, dst_g, coin_map):
    src = [ln.split("\t") for ln in lines if len(ln.split("\t")) > 1 and ln.split("\t")[1] == str(src_g)]
    assert src, "源组空:%s" % src_g
    rows = []
    for r in src:
        r = list(r)
        old_id = r[0]
        new_id = str(int(old_id) + (int(dst_g) - int(src_g)) * 100)
        r[0] = new_id
        r[1] = str(dst_g)
        if r[6] in coin_map:
            r[6] = coin_map[r[6]]
        if len(r) > 11 and r[11]:
            label_rows[new_id] = old_id
        rows.append("\t".join(r))
    return rows
new1343 = clone_ex(1340, 1343, {"1201": "1210"})
new1344 = clone_ex(1341, 1344, {})
ids = [r.split("\t")[0] for r in new1343 + new1344]
assert_absent(lines, ids, "Exchange")
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(new1343 + new1344)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Exchange OK: 组1343 %d行(币1210) + 组1344 %d行(币1202沿用); 标签行%d个" % (len(new1343), len(new1344), len(label_rows)))

# ---- 5. AO 106104 + 101343 + 101344 ----
f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
assert_absent(lines, [106104, 101343, 101344], "AO")
i = find_idx(lines, 106103)
r = list(lines[i].split("\t"))
r[0] = "106104"; r[2] = "马戏庆典装饰"; r[3] = "限时装饰礼包，马戏庆典主题家具超值入手！"
r[4] = "702"; r[31] = "702"; r[38] = "142"
row_dec = "\t".join(r)
i = find_idx(lines, 101340)
r = list(lines[i].split("\t"))
r[0] = "101343"; r[2] = "马戏珍宝集市"; r[3] = "消耗马戏勋章，兑换珍稀道具与外显！"
r[4] = "1343"; r[33] = "1209|1210"; r[38] = "142"
row_ex1 = "\t".join(r)
i = find_idx(lines, 101341)
r = list(lines[i].split("\t"))
r[0] = "101344"; r[2] = "巡游珍宝集市"; r[3] = "消耗巡游代币，兑换珍稀道具与外显！"
r[4] = "1344"; r[38] = "143"
row_ex2 = "\t".join(r)
i = find_idx(lines, 101341)
lines[i + 1:i + 1] = [row_dec, row_ex1, row_ex2]
write(f, lines)
print("AO OK: 106104(RT15007通用沿用/hub142) + 101343(hub142) + 101344(hub143)")

# ---- 6. i18n ----
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

add("TXT_ChainPack_Name_702",
    ["马戏庆典装饰","Circus Décor","Decoración del Circo","Décor du Cirque","Dekorasi Sirkus","Zirkusdekor","서커스 장식","馬戲慶典裝飾","Цирковой декор","Цирковий декор","サーカス装飾","Decorazioni del Circo","Dekoracje Cyrkowe","Decoração de Circo","Sirk Dekoru","ของตกแต่งละครสัตว์"])
add("TXT_ActvOnline_ActvName_106104", langs_of("TXT_ChainPack_Name_702") or [""] * 16)
market1 = ["马戏珍宝集市","Circus Treasure Market","Mercado de Tesoros del Circo","Marché aux Trésors du Cirque","Pasar Harta Sirkus","Zirkus-Schatzmarkt","서커스 보물 시장","馬戲珍寶集市","Цирковой рынок сокровищ","Цирковий ринок скарбів","サーカス宝物市場","Mercato dei Tesori del Circo","Cyrkowy Targ Skarbów","Mercado de Tesouros do Circo","Sirk Hazine Pazarı","ตลาดสมบัติละครสัตว์"]
market2 = ["巡游珍宝集市","Parade Treasure Market","Mercado del Desfile","Marché de la Parade","Pasar Parade","Paraden-Markt","퍼레이드 보물 시장","巡遊珍寶集市","Парадный рынок","Парадний ринок","パレード市場","Mercato della Parata","Targ Parady","Mercado do Desfile","Geçit Pazarı","ตลาดพาเหรด"]
add("TXT_ActvOnline_ActvName_101343", market1)
add("TXT_ActvOnline_ActvName_101344", market2)
for k, cn, en in (("TXT_ActvOnline_ActvDesc_106104", "限时装饰礼包，马戏庆典主题家具超值入手！", "Limited-time décor packs! Get Circus Festival themed furniture at great value!"),
                  ("TXT_ActvOnline_ActvDesc_101343", "消耗马戏勋章，兑换珍稀道具与外显！", "Spend Circus Medals to exchange for rare items and cosmetics!"),
                  ("TXT_ActvOnline_ActvDesc_101344", "消耗巡游代币，兑换珍稀道具与外显！", "Spend parade tokens to exchange for rare items and cosmetics!")):
    add(k, [cn, en] + [""] * 14)
# Pack 名（装饰3档）
for pid in (211032, 211033, 211034):
    src = langs_of("TXT_Pack_Name_%d" % (pid - 16))
    if src:
        add("TXT_Pack_Name_%d" % pid, src)
# Exchange 标签 key（源标签非空的行,16语复制）
for new_id, old_id in sorted(label_rows.items()):
    src = langs_of("TXT_ActvExchange_Label_%s" % old_id)
    if src:
        add("TXT_ActvExchange_Label_%s" % new_id, src)
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Text OK: %d key" % len(rows))
print("ALL DONE batch7")
