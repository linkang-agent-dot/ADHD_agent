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
