# -*- coding: utf-8 -*-
"""深海岛屿 i18n: 向 tsv/i18n/Text__Text.tsv 追加10行(5名+5故事·合并key·16语言)。--apply落盘。
列序: col4-19 = cn,en,sp,fr,id,de,kr,zh,ru,ua,jp,it,pl,po,tr,th"""
import sys
APPLY = "--apply" in sys.argv
P = r"C:\x3\gdconfig\tsv\i18n\Text__Text.tsv"

IDS = {
 "start":   [201],
 "treasure":[203,209,215,221],
 "mystery": [207,213,219],
 "diamond": [205,211,217,223],
 "lucky":   [202,204,206,208,210,212,214,216,218,220,222,224],
}
# 16语言: cn,en,sp,fr,id,de,kr,zh,ru,ua,jp,it,pl,po,tr,th
NAME = {
 "start":   ["启航港","Departure Harbor","Puerto de Partida","Port de Départ","Pelabuhan Keberangkatan","Abfahrtshafen","출항 항구","啟航港","Порт отплытия","Порт відплиття","出航港","Porto di Partenza","Port Wypłynięcia","Porto de Partida","Kalkış Limanı","ท่าเรือออกเดินทาง"],
 "treasure":["沉船宝藏","Sunken Treasure","Tesoro Hundido","Trésor Englouti","Harta Karun Tenggelam","Versunkener Schatz","침몰선 보물","沉船寶藏","Затонувшие сокровища","Затонулі скарби","沈没船の宝","Tesoro Sommerso","Zatopiony Skarb","Tesouro Afundado","Batık Hazine","สมบัติเรืออับปาง"],
 "mystery": ["迷雾漩涡","Misty Maelstrom","Vorágine Brumosa","Maelström Brumeux","Pusaran Berkabut","Nebliger Mahlstrom","안개 소용돌이","迷霧漩渦","Туманный водоворот","Туманний вир","霧の渦","Vortice Nebbioso","Mglisty Wir","Voragem Nebulosa","Sisli Girdap","วังวนหมอก"],
 "diamond": ["珊瑚秘境","Coral Sanctuary","Santuario de Coral","Sanctuaire de Corail","Suaka Karang","Korallenheiligtum","산호 성역","珊瑚秘境","Коралловое святилище","Кораловий притулок","サンゴの秘境","Santuario di Corallo","Sanktuarium Koralowe","Santuário de Coral","Mercan Tapınağı","วิหารปะการัง"],
 "lucky":   ["海风礁","Sea Breeze Reef","Arrecife de la Brisa","Récif de la Brise","Karang Angin Laut","Meeresbrisen-Riff","바닷바람 암초","海風礁","Риф морского бриза","Риф морського бризу","潮風の礁","Scogliera della Brezza","Rafa Morskiej Bryzy","Recife da Brisa Marinha","Deniz Meltemi Resifi","แนวปะการังสายลมทะเล"],
}
STORY = {
 "start":   ["扬帆启航之地，回到此处可获得任意两个海风礁或珊瑚秘境的奖励。","Set sail from here—return to claim rewards from any 2 Sea Breeze Reefs or Coral Sanctuaries","El punto de partida; regresa aquí para recibir recompensas de dos Arrecifes de la Brisa o Santuarios de Coral cualesquiera.","Le point de départ ; revenez ici pour recevoir les récompenses de deux Récifs de la Brise ou Sanctuaires de Corail au choix.","Titik berlayar; kembali ke sini untuk mendapatkan hadiah dari dua Karang Angin Laut atau Suaka Karang mana pun.","Der Ausgangspunkt; kehre hierher zurück, um Belohnungen von zwei beliebigen Meeresbrisen-Riffen oder Korallenheiligtümern zu erhalten.","출항하는 곳, 이곳으로 돌아오면 임의의 바닷바람 암초 또는 산호 성역 보상 2개를 획득할 수 있습니다.","揚帆啟航之地，回到此處可獲得任意兩個海風礁或珊瑚秘境的獎勵。","Место отплытия — вернитесь сюда, чтобы забрать награды с любых двух Рифов морского бриза или Коралловых святилищ.","Місце відплиття — поверніться сюди, щоб отримати нагороди з будь-яких двох Рифів морського бризу або Коралових притулків.","出航の地、ここに戻ると任意の潮風の礁またはサンゴの秘境の報酬を2つ獲得できます。","Punto di partenza; torna qui per richiedere le ricompense di 2 Scogliere della Brezza o Santuari di Corallo a scelta","Punkt wypłynięcia; wróć tutaj, by odebrać nagrody z dowolnych 2 Raf Morskiej Bryzy lub Sanktuariów Koralowych","Ponto de partida; volte aqui para reclamar recompensas de 2 Recifes da Brisa ou Santuários de Coral quaisquer","Yola çıkış noktası; buraya dönerek herhangi 2 Deniz Meltemi Resifi veya Mercan Tapınağı ödülü al","จุดออกเดินทาง กลับมาที่นี่เพื่อรับรางวัลจากแนวปะการังสายลมทะเลหรือวิหารปะการังใดก็ได้ 2 แห่ง"],
 "treasure":["深海沉船埋藏的宝库，可获得随机航海金币。","Treasure buried in a deep-sea shipwreck—get random Ocean Gold","Un tesoro enterrado en un naufragio de las profundidades; puedes obtener oro de navegación aleatorio.","Un trésor enfoui dans une épave des profondeurs ; vous pouvez obtenir de l'or de navigation aléatoire.","Harta karun yang terkubur di bangkai kapal laut dalam, bisa mendapatkan koin pelayaran secara acak.","Ein in einem Tiefsee-Schiffswrack vergrabener Schatz; du kannst zufälliges Segelgold erhalten.","심해 난파선에 묻힌 보물 창고에서 랜덤 항해 금화를 획득할 수 있습니다.","深海沉船埋藏的寶庫，可獲得隨機航海金幣。","Сокровища, погребённые в глубоководном кораблекрушении. Даёт случайное количество золота за плавание.","Скарби, поховані в глибоководному корабельному уламку. Надає випадкову кількість золота для плавання.","深海の沈没船に眠る宝庫、ランダムな航海金貨を獲得できます。","Tesoro sepolto in un relitto degli abissi—ottieni Oro Oceanico casuale","Skarb pogrzebany w głębinowym wraku — zdobądź losowe Złoto Oceaniczne","Tesouro enterrado em um naufrágio das profundezas — ganhe Ouro do Oceano aleatório","Derin deniz enkazına gömülü hazine—rastgele Okyanus Altını kazan","สมบัติที่ฝังอยู่ในซากเรือใต้ทะเลลึก—รับทองคำมหาสมุทรสุ่ม"],
 "mystery": ["被迷雾笼罩的未知海域，触发一个随机事件。","Fog-shrouded unknown waters—trigger a random event","Se desencadena un evento aleatorio en aguas desconocidas envueltas en niebla.","Un événement aléatoire se déclenche dans des eaux inconnues enveloppées de brouillard.","Perairan tak dikenal yang diselimuti kabut, memicu sebuah kejadian acak.","Ein zufälliges Ereignis wird in unbekannten, nebelverhangenen Gewässern ausgelöst.","안개에 휩싸인 미지의 해역에서 무작위 이벤트가 발생합니다.","被迷霧籠罩的未知海域，觸發一個隨機事件。","Неизвестные воды, окутанные туманом — вызывает случайное событие.","Невідомі води, оповиті туманом — спрацьовює випадкова подія.","霧に包まれた未知の海域、ランダムイベントが発生します。","Acque sconosciute avvolte nella nebbia—attiva un evento casuale","Nieznane wody spowite mgłą — wywołaj losowe zdarzenie","Águas desconhecidas envoltas em névoa — acione um evento aleatório","Sise bürünmüş bilinmeyen sular—rastgele bir olay tetikle","น่านน้ำลึกลับที่ปกคลุมด้วยหมอก—กระตุ้นเหตุการณ์สุ่ม"],
 "diamond": ["珊瑚丛中闪耀宝石光芒，到达后可获得随机钻石。","Coral aglow with gem light—get random diamonds","Los corales brillan con el resplandor de las gemas; al alcanzarlos, puedes obtener diamantes aleatorios.","Les coraux scintillent de l'éclat des gemmes ; en les atteignant, vous pouvez obtenir des diamants aléatoires.","Terumbu karang bersinar dengan cahaya permata, setelah mencapai dapat memperoleh berlian acak.","Die Korallen funkeln im Glanz von Edelsteinen; beim Erreichen kannst du zufällige Diamanten erhalten.","산호가 보석처럼 빛나고 있습니다. 도착하면 랜덤 다이아를 획득할 수 있습니다.","珊瑚叢中閃耀寶石光芒，到達後可獲得隨機鑽石。","Кораллы мерцают светом драгоценных камней. Доберитесь до них, чтобы получить случайные алмазы.","Корали мерехтять світлом коштовних каменів. Дістанься до них, щоб отримати випадкові діаманти.","宝石の輝きを放つサンゴ礁、到達するとランダムなダイヤモンドを獲得できます。","Coralli che brillano di luce gemmata—ottieni diamanti casuali","Koralowce lśniące blaskiem klejnotów — zdobądź losowe diamenty","Corais reluzentes com brilho de gemas — ganhe diamantes aleatórios","Mücevher ışıltılı mercanlar—rastgele elmas kazan","ปะการังที่เปล่งประกายอัญมณี—รับเพชรสุ่ม"],
 "lucky":   ["海风轻拂的幸运礁石，可获得一份随机奖励。","A lucky reef caressed by sea breeze—gain a random prize","Un arrecife afortunado acariciado por la brisa marina; otorga una recompensa aleatoria.","Un récif chanceux caressé par la brise marine ; accorde une récompense aléatoire.","Karang keberuntungan yang dibelai angin laut, dapat memperoleh hadiah acak.","Ein glückliches Riff, umweht von der Meeresbrise; gewährt eine zufällige Belohnung.","바닷바람이 어루만지는 행운의 암초에서 무작위 보상을 획득할 수 있습니다.","海風輕拂的幸運礁石，可獲得一份隨機獎勵。","Счастливый риф, овеваемый морским бризом: даёт случайную награду.","Щасливий риф, овіяний морським бризом: надає випадкову нагороду.","潮風がそよぐ幸運の礁、ランダム報酬を獲得できます。","Una scogliera fortunata accarezzata dalla brezza marina—ottieni un premio casuale","Szczęśliwa rafa muskana morską bryzą — zdobądź losową nagrodę","Um recife de sorte acariciado pela brisa marinha — ganhe um prêmio aleatório","Deniz meltemiyle okşanan şanslı resif—rastgele ödül kazan","แนวปะการังนำโชคที่สายลมทะเลพัดผ่าน—รับรางวัลสุ่ม"],
}

def mkrow(field, key_ids, langs):
    key = "|".join(f"TXT_ActvVoyageIsland_{field}_{i}" for i in key_ids)
    row = [key, "AI", ""] + langs       # col1 key, col2 status, col3 备份空, col4-19 langs
    row += [""] * (27 - len(row))        # 补足到27列
    return "\t".join(row)

raw = open(P, "rb").read(); crlf = b"\r\n" in raw
text = raw.decode("utf-8"); eol = "\r\n" if crlf else "\n"
trail = text.endswith(eol); lines = text.split(eol)
if trail and lines and lines[-1] == "": lines = lines[:-1]

# 防重: 确认这些key还没存在
exist = sum(1 for l in lines if "ActvVoyageIsland_IslandName_201" in l or "ActvVoyageIsland_IslandStory_201" in l)
assert exist == 0, f"key已存在({exist})·别重复加"

new = []
for k in ["start","treasure","mystery","diamond","lucky"]:
    new.append(mkrow("IslandName",  IDS[k], NAME[k]))
for k in ["start","treasure","mystery","diamond","lucky"]:
    new.append(mkrow("IslandStory", IDS[k], STORY[k]))

print(f"新增 {len(new)} 行 (应10)。校验每行列数:")
for r in new:
    n = r.split("\t")
    print(f"  {n[3]:8s} cols={len(n)} key={n[0][:55]}…")
assert all(len(r.split('\t')) == 27 for r in new)
assert len(new) == 10

if APPLY:
    out = eol.join(lines + new) + (eol if trail else "")
    open(P, "wb").write(out.encode("utf-8"))
    print("\n*** APPLIED ***")
else:
    print("\n--- DRY-RUN ---")
