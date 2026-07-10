# -*- coding: utf-8 -*-
"""马戏节换皮 批次8：拜访 AO105606 + 许愿池 AO105014(壳) + 外显(纪念卡81/铭牌106) + 榜奖占位swap
⚠️许愿池奖池组105/周卡奖池 = 深海在线中(至7/16)不能现在原位改 → 挂账上线前批次。"""
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

# ---- 1. Item：1212 马戏邀请函 + 180081 纪念卡 + 82006 铭牌道具 ----
f = "Item__Item.tsv"
lines = read(f)
assert_absent(lines, [1213, 180081, 82006], "Item")
i = find_idx(lines, 1151)
r = list(lines[i].split("\t"))
r[0] = "1213"; r[1] = "马戏邀请函"
r[3] = "持有邀请函拜访拥有【马戏庆典】门头装扮的酒馆，可获得额外奖励！"
row_inv = "\t".join(r)
i = find_idx(lines, 180080)
r = list(lines[i].split("\t"))
r[0] = "180081"; r[1] = "欢乐颂歌（纪念卡）"
if len(r) > 3:
    r[3] = "马戏庆典纪念卡，收录巡游中的欢乐记忆。"
row_card = "\t".join(r)
i = find_idx(lines, 82005)
r = list(lines[i].split("\t"))
r[0] = "82006"; r[1] = "欢庆之星（头衔）"
if len(r) > 3 and r[3]:
    r[3] = r[3].replace("深海", "马戏")
row_title = "\t".join(r)
i = find_idx(lines, 1210)
lines[i + 1:i + 1] = [row_inv, row_card, row_title]
write(f, lines)
print("Item OK: 1212邀请函/180081纪念卡/82006头衔 (icon DK 沿深海占位)")

# ---- 2. Reward：2069(每次拜访1209x1) 2070(里程碑1209x5) ----
f = "Reward__Reward.tsv"
lines = read(f)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[1] in ("2069", "2070"):
        raise AssertionError("Reward组已占: " + fl[1])
mx = 0
for ln in lines:
    fl = ln.split("\t")
    if fl[0].isdigit():
        mx = max(mx, int(fl[0]))
seq = mx + 1
out = []
for src_g, dst_g in ((2067, 2069), (2068, 2070)):
    for r in [ln.split("\t") for ln in lines if len(ln.split("\t")) > 1 and ln.split("\t")[1] == str(src_g)]:
        r = list(r)
        old = r[0]
        r[0] = str(seq); r[1] = str(dst_g)
        if r[3] == "1200":
            r[3] = "1209"; r[4] = "马戏门票"
        for j in range(4, len(r)):
            if r[j] == old:
                r[j] = str(seq)
            elif "深海" in r[j]:
                r[j] = "26马戏节-拜访"
        out.append("\t".join(r)); seq += 1
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(out)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Reward OK: 2069/2070 seq..%d" % (seq - 1))

# ---- 2b. 榜奖占位 swap：批次2的 30950-57(180080→180081) / 30960-66(82005→82006) ----
lines = read(f)
n_card = n_title = 0
for i, ln in enumerate(lines):
    fl = ln.split("\t")
    if len(fl) > 3 and fl[1].isdigit():
        g = int(fl[1])
        if 30950 <= g <= 30957 and fl[3] == "180080":
            fl[3] = "180081"; fl[4] = "欢乐颂歌（纪念卡）"; n_card += 1
        elif 30960 <= g <= 30966 and fl[3] == "82005":
            fl[3] = "82006"; fl[4] = "欢庆之星（头衔）"; n_title += 1
        else:
            continue
        lines[i] = "\t".join(fl)
write(f, lines)
print("榜奖swap OK: 纪念卡%d处→180081 / 头衔%d处→82006 (15065大奖仍占位待定案)" % (n_card, n_title))

# ---- 3. ItemObtain 1212（挂拜访 105606）----
f = "ItemObtain__ItemObtain.tsv"
lines = read(f)
assert_absent(lines, [1213], "ItemObtain")
src = None
for ln in lines:
    if ln.split("\t")[0] == "1151":
        src = ln.split("\t")
        break
if src:
    r = list(src)
    r[0] = "1213"; r[5] = "105606"
    for j in (1, 7, 8):
        if len(r) > j and r[j]:
            r[j] = r[j].replace("深海", "马戏").replace("海滨之约", "马戏庆典之约")
    i = find_idx(lines, 1151)
    lines.insert(i + 1, "\t".join(r))
    write(f, lines)
    print("ItemObtain OK: 1212 → AO105606")
else:
    print("ItemObtain 1151 无源行, 跳过(邀请函获取走活动内发放)")

# ---- 4. Pack 211046 拜访门头包 ----
f = "Pack__Pack.tsv"
lines = read(f)
assert_absent(lines, [211046], "Pack")
i = find_idx(lines, 211020)
r = list(lines[i].split("\t"))
r[0] = "211046"; r[2] = "马戏庆典-拜访门头礼包99.99"
r[13] = "211046"
if len(r) > 35 and r[35]:
    r[35] = "马戏庆典之约"
assert not r[30], "MainBg 非空! 源行违反铁律"
row_pack = "\t".join(r)
lines.insert(i + 1, row_pack)
write(f, lines)
print("Pack OK: 211046 (MainBg空铁律断言过)")

# 4b. Reward 组 211046（克隆 211020 组内容）
f = "Reward__Reward.tsv"
lines = read(f)
for ln in lines:
    fl = ln.split("\t")
    if len(fl) > 1 and fl[1] == "211046":
        raise AssertionError("Reward组211046已占")
mx = 0
for ln in lines:
    fl = ln.split("\t")
    if fl[0].isdigit():
        mx = max(mx, int(fl[0]))
seq = mx + 1
out = []
for r in [ln.split("\t") for ln in lines if len(ln.split("\t")) > 1 and ln.split("\t")[1] == "211020"]:
    r = list(r)
    old = r[0]
    r[0] = str(seq); r[1] = "211046"
    for j in range(4, len(r)):
        if r[j] == old:
            r[j] = str(seq)
        elif "深海" in r[j]:
            r[j] = "26马戏节-拜访门头包"
    out.append("\t".join(r)); seq += 1
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(out)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Reward OK: 组211046 %d行 (三件套/钻/VIP照深海)" % len(out))

# ---- 5. VisitPack 5607 + VisitPackReward 组7 ----
f = "ActvVisitPack__ActvVisitPack.tsv"
lines = read(f)
assert_absent(lines, [5607], "VisitPack")
i = find_idx(lines, 5606)
r = list(lines[i].split("\t"))
r[0] = "5607"; r[1] = "马戏节-庆典之约"; r[2] = "211046"; r[3] = "7"; r[4] = "1213"; r[6] = "2069"
r[7] = "活动期间，每天可领取一份<color=#5C9729>马戏邀请函</color>。拜访拥有<color=#5C9729>马戏庆典</color>门头装扮的酒馆，可获得额外奖励！"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("VisitPack OK: 5607")

f = "ActvVisitPack__ActvVisitPackReward.tsv"
lines = read(f)
assert_absent(lines, [145, 146, 147, 148], "VisitPackReward")
rows = []
for n, rid in enumerate((137, 138, 139, 140)):
    i = find_idx(lines, rid)
    r = list(lines[i].split("\t"))
    r[0] = str(145 + n); r[1] = "7"; r[5] = "2070"
    rows.append("\t".join(r))
anchor = find_idx(lines, 140)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("VisitPackReward OK: 组7 行145-148 (拜访10/20/30/50次→2070)")

# ---- 6. WishingPool 5014（壳；奖池组105沿用=上线前原位改内容,挂账）----
f = "ActvWishingPool__ActvWishingPool.tsv"
lines = read(f)
assert_absent(lines, [5014], "WishingPool")
i = find_idx(lines, 5013)
r = list(lines[i].split("\t"))
r[0] = "5014"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("WishingPool OK: 5014 (奖池组105/阶段组103/礼包1002001全沿用; ⚠️组105内容=上线前深海下线后原位改)")

# ---- 7. MemorialCard 81 + PlayerTitle 106 ----
f = "MemorialCard__MemorialCard.tsv"
lines = read(f)
assert_absent(lines, [81], "MemorialCard")
i = find_idx(lines, 80)
r = list(lines[i].split("\t"))
r[0] = "81"; r[2] = "欢乐颂歌"
r[3] = "灯火与欢笑交织的庆典夜，巡游的乐声穿过帐篷——马戏庆典的珍藏，只属于最欢乐的观众。"
row81 = "\t".join(r)
lines.insert(i + 1, row81)
write(f, lines)
print("MemorialCard OK: 81 欢乐颂歌 (卡面DK沿80占位,属性组沿用)")

f = "PlayerTitle__PlayerTitle.tsv"
lines = read(f)
assert_absent(lines, [106], "PlayerTitle")
i = find_idx(lines, 105)
r = list(lines[i].split("\t"))
r[0] = "106"; r[1] = "欢庆之星"
if len(r) > 5:
    r[5] = "马戏大转盘排行榜顶端获取"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("PlayerTitle OK: 106 欢庆之星 (图标DK沿105占位)")

# ---- 8. RuleTips 16045 + AO 105606/105014 ----
f = "RuleTips__RuleTips.tsv"
lines = read(f)
assert_absent(lines, [16045], "RuleTips")
i = find_idx(lines, 16042)
r = list(lines[i].split("\t"))
r[0] = "16045"
for j in range(1, len(r)):
    if r[j]:
        r[j] = r[j].replace("深海", "马戏").replace("海滨假日", "马戏庆典").replace("海滨之约", "马戏庆典之约")
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("RuleTips OK: 16045")

f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
assert_absent(lines, [105606, 105014], "AO")
i = find_idx(lines, 105605)
r = list(lines[i].split("\t"))
r[0] = "105606"; r[2] = "马戏庆典之约"; r[3] = "领取马戏邀请函拜访酒馆，赢取珍稀奖励！"
r[4] = "5607"; r[13] = "16045"; r[33] = "1209|1057"; r[38] = "142"
row_visit = "\t".join(r)
i = find_idx(lines, 105013)
r = list(lines[i].split("\t"))
r[0] = "105014"; r[2] = "许愿池"
r[4] = "5014"; r[33] = "1209|1210"; r[38] = "142"
row_wish = "\t".join(r)
i = find_idx(lines, 105605)
lines[i + 1:i + 1] = [row_visit, row_wish]
write(f, lines)
print("AO OK: 105606拜访(16045) + 105014许愿池(RT16026通用沿用)")

# ---- 9. i18n ----
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
def add2(key, cn, en):
    add(key, [cn, en] + [""] * 14)

add("TXT_Item_Name_1213",
    ["马戏邀请函","Circus Invitation","Invitación del Circo","Invitation du Cirque","Undangan Sirkus","Zirkuseinladung","서커스 초대장","馬戲邀請函","Цирковое приглашение","Циркове запрошення","サーカス招待状","Invito del Circo","Cyrkowe Zaproszenie","Convite de Circo","Sirk Davetiyesi","บัตรเชิญละครสัตว์"])
add2("TXT_Item_Desc_1213", "持有邀请函拜访拥有【马戏庆典】门头装扮的酒馆，可获得额外奖励！",
     "Visit taverns decorated with the [Circus Festival] entrance while holding an invitation to earn extra rewards!")
add("TXT_Item_Name_180081",
    ["欢乐颂歌（纪念卡）","Ode to Joy (Card)","Oda a la Alegría (Carta)","Ode à la Joie (Carte)","Ode Sukacita (Kartu)","Ode an die Freude (Karte)","환희의 송가 (카드)","歡樂頌歌（紀念卡）","Ода радости (карта)","Ода радості (картка)","歓喜の頌歌（カード）","Inno alla Gioia (Carta)","Oda do Radości (Karta)","Ode à Alegria (Carta)","Neşe Kasidesi (Kart)","บทเพลงแห่งความสุข (การ์ด)"])
add2("TXT_Item_Desc_180081", "马戏庆典纪念卡，收录巡游中的欢乐记忆。",
     "A Circus Festival memorial card, capturing joyful memories of the parade.")
add("TXT_Item_Name_82006",
    ["欢庆之星（头衔）","Star of Revelry (Title)","Estrella de la Fiesta (Título)","Étoile de la Fête (Titre)","Bintang Pesta (Gelar)","Stern des Festes (Titel)","축제의 별 (칭호)","歡慶之星（頭銜）","Звезда торжества (титул)","Зірка свята (титул)","歓祭の星（称号）","Stella della Festa (Titolo)","Gwiazda Festynu (Tytuł)","Estrela da Festa (Título)","Şenlik Yıldızı (Unvan)","ดาวแห่งงานเฉลิมฉลอง (ฉายา)"])
add2("TXT_Item_Desc_82006", "马戏大转盘排行榜顶端专属头衔。", "An exclusive title for the top ranks of the Circus Wheel leaderboard.")
add("TXT_PlayerTitle_Name_106", langs_of("TXT_Item_Name_82006") or [""] * 16)
add("TXT_MemorialCard_Name_81", langs_of("TXT_Item_Name_180081") or [""] * 16)
add2("TXT_MemorialCard_Story_81", "灯火与欢笑交织的庆典夜，巡游的乐声穿过帐篷——马戏庆典的珍藏，只属于最欢乐的观众。",
     "A festival night woven with lights and laughter, parade music drifting through the tents — the Circus Festival's treasure belongs to its most joyful audience.")
add("TXT_ActvOnline_ActvName_105606",
    ["马戏庆典之约","Circus Rendezvous","Cita del Circo","Rendez-vous du Cirque","Janji Sirkus","Zirkus-Rendezvous","서커스의 약속","馬戲慶典之約","Цирковое свидание","Циркове побачення","サーカスの約束","Appuntamento al Circo","Cyrkowe Spotkanie","Encontro no Circo","Sirk Buluşması","นัดพบละครสัตว์"])
add2("TXT_ActvOnline_ActvDesc_105606", "领取马戏邀请函拜访酒馆，赢取珍稀奖励！", "Claim Circus Invitations to visit taverns and win rare rewards!")
add("TXT_ActvOnline_ActvName_105014", langs_of("TXT_ActvOnline_ActvName_105013") or [""] * 16)
src_desc = langs_of("TXT_ActvOnline_ActvDesc_105013")
if src_desc:
    add("TXT_ActvOnline_ActvDesc_105014", src_desc)
add("TXT_RuleTips_Title_16045", langs_of("TXT_ActvOnline_ActvName_105606") or [""] * 16)
add2("TXT_RuleTips_Content_16045",
     "活动期间，每天可领取一份【马戏邀请函】。拜访拥有【马戏庆典】门头装扮的酒馆可兑换额外奖励；累计被拜访次数达到指定值，还可领取里程碑奖励！",
     "During the event, claim one [Circus Invitation] daily. Visit taverns decorated with the [Circus Festival] entrance to exchange for extra rewards. Reach visit milestones to claim milestone rewards!")
add("TXT_Pack_Name_211046",
    ["马戏庆典礼包","Circus Festival Pack","Paquete del Festival","Pack du Festival","Paket Festival Sirkus","Zirkusfest-Paket","서커스 축제 팩","馬戲慶典禮包","Набор Циркового фестиваля","Набір Циркового фестивалю","サーカス祭パック","Pacchetto del Festival","Pakiet Festiwalu","Pacote do Festival","Sirk Festivali Paketi","แพ็คเทศกาลละครสัตว์"])
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Text OK: %d key" % len(rows))
print("ALL DONE batch8")
