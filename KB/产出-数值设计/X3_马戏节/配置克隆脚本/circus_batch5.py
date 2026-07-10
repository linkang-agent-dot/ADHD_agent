# -*- coding: utf-8 -*-
"""马戏节换皮 批次5：大富翁 AO102803 + 拼图 AO101829
Voyage2803(IslandGroup3/OtherReward组101/存钱罐280002) + Island组3(301-324) + Event组207-214
+ Puzzle1829(任务组110/奖励组1100直接沿用) + Schedule10006 + RuleTips15018/19/21 + i18n
沿用不克隆：ProgressReward组200 / 拼图组110/1100 / 抽奖阶段Reward 4200001-008 / 货币1057/1058/1202/1204/1206"""
import io

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

def assert_absent(lines, ids, label):
    s = set(str(x) for x in ids)
    for ln in lines:
        if ln.split("\t")[0] in s:
            raise AssertionError("%s 已存在: %s" % (label, ln.split("\t")[0]))

# 格子名映射（深海→马戏）
ISLE = {
    "启航港":   ("巡游大门", "扬帆巡游之地，回到此处可获得任意两个彩球摊或杂技台的奖励。"),
    "海风礁":   ("彩球摊",   "缤纷彩球高高挂起的幸运摊位，可获得一份随机奖励。"),
    "珊瑚秘境": ("杂技台",   "喝彩声不断的杂技舞台，可获得一份丰厚的随机奖励。"),
    "沉船宝藏": ("魔术宝箱", "魔术师留下的神秘宝箱，开启可获得珍贵宝藏。"),
    "迷雾漩涡": ("小丑迷阵", "小丑布下的奇妙迷阵，穿过它会发生什么呢？"),
}
ISLE_EN = {
    "巡游大门": ("Parade Gate", "The starting point of the parade. Return here to claim rewards from any two Balloon Stands or Acrobat Stages."),
    "彩球摊":   ("Balloon Stand", "A lucky stand with colorful balloons. Grants a random reward."),
    "杂技台":   ("Acrobat Stage", "A stage of endless applause. Grants a generous random reward."),
    "魔术宝箱": ("Magic Chest", "A mysterious chest left by the magician. Open it for precious treasures."),
    "小丑迷阵": ("Clown Maze", "A whimsical maze set by the clown. What will happen when you pass through?"),
}

# ---- 1. Island 组3：行 301-324（克隆 201-224，事件组 +8）----
f = "ActvVoyage__ActvVoyageIsland.tsv"
lines = read(f)
assert_absent(lines, range(301, 325), "Island")
rows = []
name_by_row = {}   # 新行id -> 马戏格名（i18n 用）
for rid in range(201, 225):
    i = find_idx(lines, rid)
    r = list(lines[i].split("\t"))
    r[0] = str(rid + 100)
    r[1] = "3"
    old_name = r[5]
    cn_name, cn_story = ISLE[old_name]
    r[5] = cn_name
    r[6] = cn_story
    if r[7]:
        r[7] = str(int(r[7]) + 8)   # 事件组 199-206 → 207-214
    rows.append("\t".join(r))
    name_by_row[rid + 100] = cn_name
anchor = find_idx(lines, 224)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("Island OK: 组3 行301-324")

# ---- 2. Event 组207-214：克隆 199-206（+8），DK 占位沿用 ----
f = "ActvVoyage__ActvVoyageEvent.tsv"
lines = read(f)
src = [ln.split("\t") for ln in lines if ln.split("\t")[0].isdigit() and len(ln.split("\t")) > 1 and 199 <= int(ln.split("\t")[1]) <= 206]
assert len(src) == 48
new_ids = set()
rows = []
for r in src:
    r = list(r)
    g = int(r[1])
    seqpart = int(r[0]) - g * 1000
    ng = g + 8
    nid = ng * 1000 + seqpart
    assert nid not in new_ids
    new_ids.add(nid)
    r[0] = str(nid)
    r[1] = str(ng)
    for j in range(2, len(r)):
        if "深海" in r[j]:
            r[j] = r[j].replace("深海", "马戏")
        if r[j] == "起始岛":
            r[j] = "巡游起点"
    rows.append("\t".join(r))
assert_absent(lines, sorted(new_ids), "Event")
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Event OK: 组207-214 共48行 (DK岛图沿深海占位)")

# ---- 3. VoyageOtherReward 组101：行1009-1016，Reward 沿用 4200001-008 ----
f = "ActvVoyage__ActvVoyageOtherReward.tsv"
lines = read(f)
assert_absent(lines, range(1009, 1017), "OtherReward")
rows = []
for i, rid in enumerate(range(1001, 1009)):
    idx = find_idx(lines, rid)
    r = list(lines[idx].split("\t"))
    r[0] = str(1009 + i)
    r[2] = "101"
    rows.append("\t".join(r))
anchor = find_idx(lines, 1008)
lines[anchor + 1:anchor + 1] = rows
write(f, lines)
print("VoyageOtherReward OK: 组101 (Reward 4200001-008 内容同构直接沿用)")

# ---- 4. Pack 280002 存钱罐 ----
f = "Pack__Pack.tsv"
lines = read(f)
assert_absent(lines, [280002], "Pack")
i = find_idx(lines, 280001)
r = list(lines[i].split("\t"))
r[0] = "280002"
r[2] = "马戏大富翁存钱罐礼包"
if len(r) > 35 and r[35]:
    r[35] = "马戏珍宝罐"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("Pack OK: 280002 存钱罐(price档照280001)")

# ---- 5. ActvVoyage 2803 ----
f = "ActvVoyage__ActvVoyage.tsv"
lines = read(f)
assert_absent(lines, [2803], "Voyage")
i = find_idx(lines, 2802)
r = list(lines[i].split("\t"))
r[0] = "2803"; r[2] = "3"; r[6] = "101"; r[10] = "280002"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("Voyage OK: 2803 (货币1057/1058/宝箱1206/珍珠贝1204/进度组200 全沿用)")

# ---- 6. ActvPuzzle 1829 ----
f = "ActvPuzzle__ActvPuzzle.tsv"
lines = read(f)
assert_absent(lines, [1829], "Puzzle")
i = find_idx(lines, 1828)
r = list(lines[i].split("\t"))
r[0] = "1829"
r[4] = "小丑的梦境"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("Puzzle OK: 1829 (任务组110/奖励组1100沿用, 封面DK沿深海占位)")

# ---- 7. RuleTips 15018/15019/15021 ----
f = "RuleTips__RuleTips.tsv"
lines = read(f)
assert_absent(lines, [15018, 15019, 15021], "RuleTips")
mapping = [(15015, 15018), (15016, 15019), (15017, 15021)]
new_rows = []
for src_id, new_id in mapping:
    i = find_idx(lines, src_id)
    r = list(lines[i].split("\t"))
    r[0] = str(new_id)
    for j in range(1, len(r)):
        if r[j]:
            r[j] = r[j].replace("深海", "马戏").replace("航海之路", "马戏巡游")
    new_rows.append("\t".join(r))
anchor = find_idx(lines, 15017)
lines[anchor + 1:anchor + 1] = new_rows
write(f, lines)
print("RuleTips OK: 15018/15019/15021")

# ---- 8. AO 102803 + 101829 ----
f = "ActvOnline__ActvOnline.tsv"
lines = read(f)
assert_absent(lines, [102803, 101829], "AO")
i = find_idx(lines, 102802)
r = list(lines[i].split("\t"))
r[0] = "102803"; r[2] = "马戏巡游"; r[3] = "掷出骰子巡游马戏庆典，赢取珍稀大奖！"
r[4] = "2803"; r[13] = "15018|15019|15021"; r[38] = "143"
row_v = "\t".join(r)
i = find_idx(lines, 101828)
r = list(lines[i].split("\t"))
r[0] = "101829"; r[2] = "小丑的梦境"; r[3] = "完成任务点亮拼图，收集马戏庆典的美妙记忆！"
r[4] = "1829"; r[38] = "143"
row_p = "\t".join(r)
i = find_idx(lines, 102802)
lines[i + 1:i + 1] = [row_v, row_p]
write(f, lines)
print("AO OK: 102803马戏巡游 + 101829小丑的梦境 (hub143)")

# ---- 9. ActvGroupSchedule 10006 ----
f = "ActvOnline__ActvGroupSchedule.tsv"
lines = read(f)
assert_absent(lines, [10006], "Schedule")
i = find_idx(lines, 10005)
r = list(lines[i].split("\t"))
r[0] = "10006"; r[2] = "102803"; r[3] = "马戏巡游"; r[4] = "101829"; r[5] = "小丑的梦境"
lines.insert(i + 1, "\t".join(r))
write(f, lines)
print("Schedule OK: 10006 (102803→101829 子活动挂载)")

# ---- 10. i18n ----
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
def add2(key, cn, en):
    add(key, [cn, en] + [""] * 14)

NAME16 = {
    "巡游大门": ["巡游大门","Parade Gate","Puerta del Desfile","Porte de la Parade","Gerbang Parade","Paradentor","퍼레이드 게이트","巡遊大門","Парадные ворота","Парадні ворота","パレードゲート","Porta della Parata","Brama Parady","Portão do Desfile","Geçit Kapısı","ประตูพาเหรด"],
    "彩球摊":   ["彩球摊","Balloon Stand","Puesto de Globos","Stand de Ballons","Kios Balon","Ballonstand","풍선 가게","彩球攤","Лоток с шарами","Ятка з кульками","バルーン屋台","Bancarella dei Palloncini","Stoisko z Balonami","Barraca de Balões","Balon Standı","แผงลูกโป่ง"],
    "杂技台":   ["杂技台","Acrobat Stage","Escenario Acrobático","Scène d'Acrobates","Panggung Akrobat","Akrobatenbühne","곡예 무대","雜技台","Сцена акробатов","Сцена акробатів","アクロバット舞台","Palco degli Acrobati","Scena Akrobatów","Palco de Acrobatas","Akrobat Sahnesi","เวทีกายกรรม"],
    "魔术宝箱": ["魔术宝箱","Magic Chest","Cofre Mágico","Coffre Magique","Peti Ajaib","Magische Truhe","마법 상자","魔術寶箱","Волшебный сундук","Чарівна скриня","マジックチェスト","Forziere Magico","Magiczna Skrzynia","Baú Mágico","Sihirli Sandık","หีบเวทมนตร์"],
    "小丑迷阵": ["小丑迷阵","Clown Maze","Laberinto del Payaso","Labyrinthe du Clown","Labirin Badut","Clownslabyrinth","광대 미로","小丑迷陣","Лабиринт клоуна","Лабіринт клоуна","ピエロの迷路","Labirinto del Pagliaccio","Labirynt Klauna","Labirinto do Palhaço","Palyaço Labirenti","เขาวงกตตัวตลก"],
}
for rid, cn_name in name_by_row.items():
    add("TXT_ActvVoyageIsland_IslandName_%d" % rid, NAME16[cn_name])
    story_cn = dict((v[0], v[1]) for v in ISLE.values())[cn_name]
    add2("TXT_ActvVoyageIsland_IslandStory_%d" % rid, story_cn, ISLE_EN[cn_name][1])

add("TXT_ActvOnline_ActvName_102803",
    ["马戏巡游","Circus Parade","Desfile del Circo","Parade du Cirque","Parade Sirkus","Zirkusparade","서커스 퍼레이드","馬戲巡遊","Цирковой парад","Цирковий парад","サーカスパレード","Parata del Circo","Parada Cyrkowa","Desfile de Circo","Sirk Geçidi","ขบวนพาเหรดละครสัตว์"])
dream = ["小丑的梦境","Clown's Dream","Sueño del Payaso","Rêve du Clown","Mimpi Badut","Traum des Clowns","광대의 꿈","小丑的夢境","Сон клоуна","Сон клоуна","ピエロの夢","Sogno del Pagliaccio","Sen Klauna","Sonho do Palhaço","Palyaçonun Rüyası","ความฝันของตัวตลก"]
add("TXT_ActvOnline_ActvName_101829", dream)
add("TXT_ActvPuzzle_PuzzleName_1829", dream)
add2("TXT_ActvOnline_ActvDesc_102803", "掷出骰子巡游马戏庆典，赢取珍稀大奖！", "Roll the dice to tour the Circus Festival and win rare grand prizes!")
add2("TXT_ActvOnline_ActvDesc_101829", "完成任务点亮拼图，收集马戏庆典的美妙记忆！", "Complete tasks to light up the puzzle and collect wonderful memories of the Circus Festival!")
add2("TXT_RuleTips_Title_15018", "马戏巡游", "Circus Parade")
add2("TXT_RuleTips_Title_15019", "巡游奖励", "Parade Rewards")
add2("TXT_RuleTips_Title_15021", "巡游宝箱", "Parade Chest")
add2("TXT_RuleTips_Content_15018",
     "活动期间，消耗【航海罗盘】掷骰前进，途经各格可获得对应奖励；抵达魔术宝箱可开启珍贵宝藏。累计掷骰次数达到指定值还可领取阶段奖励！",
     "During the event, spend [Voyage Compass] to roll dice and advance. Each tile grants its reward; reach the Magic Chest to open precious treasures. Reach dice-roll milestones to claim stage rewards!")
add2("TXT_RuleTips_Content_15019",
     "巡游途中获得的【马戏勋章】等道具可在活动商店兑换珍稀奖励，活动结束后未使用的活动道具将被回收。",
     "Items such as [Circus Medal] earned during the parade can be exchanged for rare rewards in the event store. Unused event items will be recycled after the event ends.")
add2("TXT_RuleTips_Content_15021",
     "开启巡游宝箱可获得马戏庆典珍稀奖励，宝箱奖励随进度逐步提升！",
     "Open Parade Chests for rare Circus Festival rewards. Chest rewards improve as you progress!")
tail = lines.pop() if lines and lines[-1] == "" else None
lines.extend(rows)
if tail is not None:
    lines.append(tail)
write(f, lines)
print("Text OK: %d key" % len(rows))
print("ALL DONE batch5")
