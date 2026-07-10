# -*- coding: utf-8 -*-
"""马戏节换皮 批次1：Item 1209/1210 + ActvGroup 142/143 + i18n 6 key
克隆深海源行，字段级替换；LF 写盘；写前断言目标 ID/key 不存在。"""
import io, sys

REPO = r"C:\x3\gdconfig-circus"
ITEM = REPO + r"\tsv\Item__Item.tsv"
GRP  = REPO + r"\tsv\ActvOnline__ActvGroup.tsv"
TEXT = REPO + r"\tsv\i18n\Text__Text.tsv"

def read(p):
    with io.open(p, "r", encoding="utf-8", newline="") as f:
        return f.read().split("\n")

def write(p, lines):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))

def find_row(lines, rid):
    for i, ln in enumerate(lines):
        if ln.startswith(rid + "\t"):
            return i
    return -1

# ---------- 1. Item ----------
lines = read(ITEM)
assert find_row(lines, "1209") == -1 and find_row(lines, "1210") == -1, "1209/1210 已存在"
i1200, i1201, i1206 = find_row(lines, "1200"), find_row(lines, "1201"), find_row(lines, "1206")
assert i1200 > 0 and i1201 > 0, "源行缺失"

r = lines[i1200].split("\t")
r[0], r[1] = "1209", "马戏门票"
r[3] = "马戏门票，凭票参与马戏大转盘抽奖，赢取珍稀奖励！"
# [20] DK_Icon 沿深海占位，美术落地后换（已记档案待办）
row1209 = "\t".join(r)

r = lines[i1201].split("\t")
r[0], r[1] = "1210", "马戏勋章"
r[3] = "马戏庆典的纪念勋章，可用于马戏活动商店兑换珍稀道具与外显。"
row1210 = "\t".join(r)

anchor = i1206 if i1206 > 0 else i1201
lines[anchor + 1:anchor + 1] = [row1209, row1210]
write(ITEM, lines)
print("Item OK: 1209/1210 插在行%d后" % (anchor + 1))

# ---------- 2. ActvGroup ----------
lines = read(GRP)
assert find_row(lines, "142") == -1 and find_row(lines, "143") == -1, "142/143 已存在"
i140, i141 = find_row(lines, "140"), find_row(lines, "141")
assert i140 > 0 and i141 > 0

r = lines[i140].split("\t")
r[0], r[2] = "142", "马戏节"   # [3] DK 图标沿深海占位待美术
row142 = "\t".join(r)
r = lines[i141].split("\t")
r[0], r[2] = "143", "马戏巡游"
row143 = "\t".join(r)
lines[i141 + 1:i141 + 1] = [row142, row143]
write(GRP, lines)
print("ActvGroup OK: 142/143 插在141后")

# ---------- 3. Text i18n（27列：key|AI|备份|cn..th 16语|尾8空） ----------
T = {
 "TXT_Item_Name_1209": ["马戏门票","Circus Ticket","Boleto del Circo","Billet de Cirque","Tiket Sirkus","Zirkusticket","서커스 티켓","馬戲門票","Цирковой билет","Цирковий квиток","サーカスチケット","Biglietto del Circo","Bilet Cyrkowy","Ingresso de Circo","Sirk Bileti","ตั๋วละครสัตว์"],
 "TXT_Item_Desc_1209": ["马戏门票，凭票参与马戏大转盘抽奖，赢取珍稀奖励！","A Circus Ticket. Use it to spin the Circus Wheel and win rare rewards!","Un boleto del circo. Úsalo para girar la Ruleta del Circo y ganar recompensas raras.","Un billet de cirque. Utilisez-le pour tourner la Roue du Cirque et gagner de rares récompenses !","Tiket Sirkus. Gunakan untuk memutar Roda Sirkus dan memenangkan hadiah langka!","Ein Zirkusticket. Nutze es, um am Zirkus-Glücksrad zu drehen und seltene Belohnungen zu gewinnen!","서커스 티켓. 서커스 룰렛을 돌려 희귀 보상을 획득하세요!","馬戲門票，憑票參與馬戲大轉盤抽獎，贏取珍稀獎勵！","Цирковой билет. Используйте его, чтобы крутить Цирковое колесо и выигрывать редкие награды!","Цирковий квиток. Використовуйте його, щоб крутити Циркове колесо та вигравати рідкісні нагороди!","サーカスチケット。サーカスルーレットを回して、レアな報酬を手に入れよう！","Un biglietto del circo. Usalo per girare la Ruota del Circo e vincere ricompense rare!","Bilet cyrkowy. Użyj go, aby zakręcić Cyrkowym Kołem i zdobyć rzadkie nagrody!","Ingresso de circo. Use-o para girar a Roleta do Circo e ganhar recompensas raras!","Sirk bileti. Sirk Çarkını çevirmek ve nadir ödüller kazanmak için kullan!","ตั๋วละครสัตว์ ใช้หมุนวงล้อละครสัตว์เพื่อลุ้นรับรางวัลหายาก!"],
 "TXT_Item_Name_1210": ["马戏勋章","Circus Medal","Medalla del Circo","Médaille de Cirque","Medali Sirkus","Zirkusmedaille","서커스 메달","馬戲勳章","Цирковая медаль","Циркова медаль","サーカスメダル","Medaglia del Circo","Medal Cyrkowy","Medalha de Circo","Sirk Madalyası","เหรียญละครสัตว์"],
 "TXT_Item_Desc_1210": ["马戏庆典的纪念勋章，可用于马戏活动商店兑换珍稀道具与外显。","A commemorative medal of the Circus Festival. Exchange it for rare items and cosmetics in the circus event store.","Una medalla conmemorativa del Festival del Circo. Canjéala por objetos raros y aspectos en la tienda del evento.","Une médaille commémorative du Festival du Cirque. Échangez-la contre des objets rares et des apparences dans la boutique de l'événement.","Medali peringatan Festival Sirkus. Tukarkan dengan item langka dan kosmetik di toko event sirkus.","Eine Gedenkmedaille des Zirkusfests. Tausche sie im Event-Shop gegen seltene Gegenstände und Skins ein.","서커스 축제 기념 메달. 서커스 이벤트 상점에서 희귀 아이템과 치장 아이템으로 교환할 수 있습니다.","馬戲慶典的紀念勳章，可用於馬戲活動商店兌換珍稀道具與外顯。","Памятная медаль Циркового фестиваля. Обменяйте её на редкие предметы и украшения в магазине события.","Пам'ятна медаль Циркового фестивалю. Обміняйте її на рідкісні предмети та прикраси в магазині події.","サーカス祭典の記念メダル。サーカスイベントショップでレアアイテムや装飾と交換できる。","Una medaglia commemorativa del Festival del Circo. Scambiala con oggetti rari e ornamenti nel negozio dell'evento.","Pamiątkowy medal Festiwalu Cyrkowego. Wymień go na rzadkie przedmioty i ozdoby w sklepie wydarzenia.","Medalha comemorativa do Festival de Circo. Troque-a por itens raros e visuais na loja do evento.","Sirk Festivali'nin hatıra madalyası. Sirk etkinlik mağazasında nadir eşyalar ve kozmetiklerle takas et.","เหรียญที่ระลึกของเทศกาลละครสัตว์ ใช้แลกไอเทมหายากและของตกแต่งได้ที่ร้านค้ากิจกรรม"],
 "TXT_ActvGroup_MainEntranceName_142": ["马戏节","Circus Festival","Festival del Circo","Festival du Cirque","Festival Sirkus","Zirkusfest","서커스 축제","馬戲節","Цирковой фестиваль","Цирковий фестиваль","サーカス祭","Festival del Circo","Festiwal Cyrkowy","Festival de Circo","Sirk Festivali","เทศกาลละครสัตว์"],
 "TXT_ActvGroup_MainEntranceName_143": ["马戏巡游","Circus Parade","Desfile del Circo","Parade du Cirque","Parade Sirkus","Zirkusparade","서커스 퍼레이드","馬戲巡遊","Цирковой парад","Цирковий парад","サーカスパレード","Parata del Circo","Parada Cyrkowa","Desfile de Circo","Sirk Geçidi","ขบวนพาเหรดละครสัตว์"],
}
lines = read(TEXT)
existing = set(ln.split("\t", 1)[0] for ln in lines if ln)
for k in T:
    assert k not in existing, k + " 已存在"
    assert len(T[k]) == 16, k + " 语言数不对"
tail = lines.pop() if lines and lines[-1] == "" else None  # 保留末尾空行状态
for k, langs in T.items():
    lines.append("\t".join([k, "AI", ""] + langs + [""] * 8))
if tail is not None:
    lines.append(tail)
write(TEXT, lines)
print("Text OK: 6 key x16语 追加")
print("ALL DONE")
