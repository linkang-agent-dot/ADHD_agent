# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TSV = r'C:\x3\gdconfig\tsv\i18n\Text__Text.tsv'

# 每条: ID -> [cn, en, sp, fr, id, de, kr, zh(繁), ru, ua, jp, it, pl, po(葡), tr, th]
# 15语言顺序严格对齐 col4-18
T = {
10028: ['沙漠之狐','Desert Foxes','Zorros del Desierto','Renards du Désert','Rubah Gurun','Wüstenfüchse','사막의 여우','沙漠之狐','Лисы пустыни','Лиси пустелі','砂漠の狐','Volpi del Deserto','Lisy Pustyni','Raposas do Deserto','Çöl Tilkileri','จิ้งจอกทะเลทราย'],
10029: ['潘帕雄鹰','Pampas Eagles','Águilas de la Pampa','Aigles de la Pampa','Elang Pampas','Pampa-Adler','팜파스의 독수리','潘帕雄鷹','Орлы пампасов','Орли пампасів','パンパの鷲','Aquile della Pampa','Orły Pampy','Águias do Pampa','Pampa Kartalları','อินทรีปัมปัส'],
10030: ['袋鼠之环','Socceroos Ring','Anillo Socceroos','Anneau Socceroos','Cincin Socceroos','Socceroos-Ring','사커루 링','袋鼠之環','Кольцо Соккеруз','Кільце Соккеруз','サッカルーズの環','Anello Socceroos','Pierścień Socceroos','Anel Socceroos','Socceroos Halkası','วงแหวนซอคเกอรูส์'],
10031: ['阿尔卑斯之鹰','Alpine Eagle','Águila Alpina','Aigle Alpin','Elang Alpen','Alpenadler','알프스 독수리','阿爾卑斯之鷹','Альпийский орёл','Альпійський орел','アルプスの鷲','Aquila Alpina','Alpejski Orzeł','Águia Alpina','Alp Kartalı','อินทรีแอลป์'],
10032: ['欧陆红魔','Red Devils','Diablos Rojos','Diables Rouges','Setan Merah','Rote Teufel','붉은 악마','歐陸紅魔','Красные дьяволы','Червоні дияволи','赤い悪魔','Diavoli Rossi','Czerwone Diabły','Diabos Vermelhos','Kırmızı Şeytanlar','ปีศาจแดง'],
10033: ['巴尔干之龙','Balkan Dragons','Dragones Balcánicos','Dragons des Balkans','Naga Balkan','Balkan-Drachen','발칸의 용','巴爾幹之龍','Балканские драконы','Балканські дракони','バルカンの竜','Draghi Balcanici','Bałkańskie Smoki','Dragões dos Balcãs','Balkan Ejderhaları','มังกรบอลข่าน'],
10034: ['桑巴军团','Samba Squad','Escuadrón Samba','Escouade Samba','Skuad Samba','Samba-Truppe','삼바 군단','桑巴軍團','Самба-команда','Самба-команда','サンバ軍団','Squadra Samba','Drużyna Samby','Esquadrão Samba','Samba Takımı','ทีมแซมบ้า'],
10035: ['枫叶之环','Maple Ring','Anillo de Arce','Anneau Érable','Cincin Maple','Ahorn-Ring','단풍의 고리','楓葉之環','Кленовое кольцо','Кленове кільце','メープルの環','Anello d\'Acero','Klonowy Pierścień','Anel de Bordo','Akçaağaç Halkası','วงแหวนเมเปิล'],
10036: ['非洲大象','The Elephants','Los Elefantes','Les Éléphants','Gajah','Die Elefanten','코끼리 군단','非洲大象','Слоны','Слони','象の軍団','Gli Elefanti','Słonie','Os Elefantes','Filler','ช้าง'],
10037: ['豹之环','Leopards Ring','Anillo Leopardos','Anneau Léopards','Cincin Macan Tutul','Leoparden-Ring','표범의 고리','豹之環','Кольцо леопардов','Кільце леопардів','豹の環','Anello dei Leopardi','Pierścień Lampartów','Anel dos Leopardos','Leoparlar Halkası','วงแหวนเสือดาว'],
10038: ['黄色咖啡','Yellow Coffee','Café Amarillo','Café Jaune','Kopi Kuning','Gelber Kaffee','옐로 커피','黃色咖啡','Жёлтый кофе','Жовта кава','イエローコーヒー','Caffè Giallo','Żółta Kawa','Café Amarelo','Sarı Kahve','กาแฟเหลือง'],
10039: ['蓝色海角','Blue Sharks','Tiburones Azules','Requins Bleus','Hiu Biru','Blaue Haie','블루 샤크','藍色海角','Голубые акулы','Блакитні акули','ブルーシャーク','Squali Blu','Niebieskie Rekiny','Tubarões Azuis','Mavi Köpekbalıkları','ฉลามน้ำเงิน'],
10040: ['格子军团','Checkered Squad','Escuadrón Ajedrezado','Escouade à Damier','Skuad Kotak-kotak','Karierte Truppe','체크무늬 군단','格子軍團','Клетчатый отряд','Картатий загін','チェック軍団','Squadra a Scacchi','Drużyna w Kratę','Esquadrão Xadrez','Damalı Takım','ทีมตาราง'],
10041: ['加勒比之蓝','Caribbean Blue','Azul Caribe','Bleu Caraïbe','Biru Karibia','Karibisches Blau','카리브의 블루','加勒比之藍','Карибский синий','Карибський синій','カリブの青','Blu Caraibico','Karaibski Błękit','Azul do Caribe','Karayip Mavisi','สีฟ้าแคริบเบียน'],
10042: ['波西米亚之环','Bohemian Ring','Anillo Bohemio','Anneau Bohémien','Cincin Bohemia','Böhmischer Ring','보헤미안 링','波西米亞之環','Богемское кольцо','Богемське кільце','ボヘミアの環','Anello Boemo','Czeski Pierścień','Anel Boêmio','Bohem Halkası','วงแหวนโบฮีเมียน'],
10043: ['赤道之环','Equator Ring','Anillo Ecuatorial','Anneau Équateur','Cincin Khatulistiwa','Äquator-Ring','적도의 고리','赤道之環','Экваторное кольцо','Екваторіальне кільце','赤道の環','Anello Equatoriale','Pierścień Równika','Anel do Equador','Ekvator Halkası','วงแหวนเส้นศูนย์สูตร'],
10044: ['法老雄鹰','Pharaoh Eagle','Águila Faraónica','Aigle Pharaon','Elang Firaun','Pharaonenadler','파라오의 독수리','法老雄鷹','Орёл фараона','Орел фараона','ファラオの鷲','Aquila del Faraone','Orzeł Faraona','Águia do Faraó','Firavun Kartalı','อินทรีฟาโรห์'],
10045: ['三狮之环','Three Lions Ring','Anillo Tres Leones','Anneau Trois Lions','Cincin Tiga Singa','Drei-Löwen-Ring','삼사자 링','三獅之環','Кольцо трёх львов','Кільце трьох левів','スリーライオンズの環','Anello dei Tre Leoni','Pierścień Trzech Lwów','Anel dos Três Leões','Üç Aslan Halkası','วงแหวนสามสิงโต'],
10046: ['红色斗牛士','Red Matadors','Matadores Rojos','Matadors Rouges','Matador Merah','Rote Matadore','붉은 투우사','紅色鬥牛士','Красные матадоры','Червоні матадори','赤い闘牛士','Matador Rossi','Czerwoni Matadorzy','Matadores Vermelhos','Kırmızı Matadorlar','มาทาดอร์แดง'],
10047: ['高卢雄鸡','Gallic Rooster','Gallo Galo','Coq Gaulois','Ayam Jago Galia','Gallischer Hahn','갈리아의 수탉','高盧雄雞','Галльский петух','Галльський півень','ガリアの雄鶏','Gallo Gallico','Galijski Kogut','Galo Gaulês','Galya Horozu','ไก่กอล'],
10048: ['日耳曼战车','Germanic Chariot','Carro Germánico','Char Germanique','Kereta Jermanik','Germanischer Streitwagen','게르만 전차','日耳曼戰車','Германская колесница','Германська колісниця','ゲルマンの戦車','Carro Germanico','Germański Rydwan','Carruagem Germânica','Cermen Savaş Arabası','รถม้าศึกเยอรมานิก'],
10049: ['黑色之星','Black Star','Estrella Negra','Étoile Noire','Bintang Hitam','Schwarzer Stern','블랙 스타','黑色之星','Чёрная звезда','Чорна зірка','ブラックスター','Stella Nera','Czarna Gwiazda','Estrela Negra','Kara Yıldız','ดาวดำ'],
10050: ['加勒比之环','Caribbean Ring','Anillo Caribeño','Anneau Caraïbe','Cincin Karibia','Karibik-Ring','카리브의 고리','加勒比之環','Карибское кольцо','Карибське кільце','カリブの環','Anello Caraibico','Karaibski Pierścień','Anel do Caribe','Karayip Halkası','วงแหวนแคริบเบียน'],
10051: ['波斯之环','Persian Ring','Anillo Persa','Anneau Persan','Cincin Persia','Persischer Ring','페르시아의 고리','波斯之環','Персидское кольцо','Перське кільце','ペルシアの環','Anello Persiano','Perski Pierścień','Anel Persa','Pers Halkası','วงแหวนเปอร์เซีย'],
10052: ['美索之环','Mesopotamia Ring','Anillo Mesopotamia','Anneau Mésopotamie','Cincin Mesopotamia','Mesopotamien-Ring','메소포타미아 링','美索之環','Месопотамское кольцо','Месопотамське кільце','メソポタミアの環','Anello Mesopotamico','Mezopotamski Pierścień','Anel da Mesopotâmia','Mezopotamya Halkası','วงแหวนเมโสโปเตเมีย'],
10053: ['契斯特之环','Chestnut Ring','Anillo Castaño','Anneau Châtaigne','Cincin Cokelat','Kastanien-Ring','체스트넛 링','契斯特之環','Каштановое кольцо','Каштанове кільце','チェスナットの環','Anello Castano','Kasztanowy Pierścień','Anel Castanho','Kestane Halkası','วงแหวนเชสต์นัท'],
10054: ['蓝色武士','Blue Samurai','Samurái Azul','Samouraï Bleu','Samurai Biru','Blauer Samurai','블루 사무라이','藍色武士','Синий самурай','Синій самурай','青い侍','Samurai Blu','Niebieski Samuraj','Samurai Azul','Mavi Samuray','ซามูไรสีน้ำเงิน'],
10055: ['太极之虎','Taeguk Tigers','Tigres Taeguk','Tigres Taeguk','Harimau Taeguk','Taeguk-Tiger','태극 호랑이','太極之虎','Тигры Тэгук','Тигри Тегук','テグクの虎','Tigri Taeguk','Tygrysy Taeguk','Tigres Taeguk','Taeguk Kaplanları','เสือแทกุก'],
10056: ['绿鹰之环','Green Falcons','Halcones Verdes','Faucons Verts','Elang Hijau','Grüne Falken','녹색 매','綠鷹之環','Зелёные соколы','Зелені соколи','緑の鷹','Falchi Verdi','Zielone Sokoły','Falcões Verdes','Yeşil Şahinler','เหยี่ยวเขียว'],
10057: ['阿特拉斯雄狮','Atlas Lions','Leones del Atlas','Lions de l\'Atlas','Singa Atlas','Atlas-Löwen','아틀라스 사자','阿特拉斯雄獅','Атласские львы','Атлаські леви','アトラスのライオン','Leoni dell\'Atlante','Lwy Atlasu','Leões do Atlas','Atlas Aslanları','สิงโตแอตลาส'],
10058: ['阿兹特克鹰','Aztec Eagle','Águila Azteca','Aigle Aztèque','Elang Aztek','Azteken-Adler','아즈텍 독수리','阿茲特克鷹','Ацтекский орёл','Ацтекський орел','アステカの鷲','Aquila Azteca','Aztecki Orzeł','Águia Asteca','Aztek Kartalı','อินทรีแอซเท็ก'],
10059: ['橙衣军团','Oranje Squad','Escuadrón Oranje','Escouade Oranje','Skuad Oranye','Oranje-Truppe','오라녜 군단','橙衣軍團','Оранжевая команда','Помаранчева команда','オランイェ軍団','Squadra Oranje','Drużyna Oranje','Esquadrão Oranje','Oranje Takımı','ทีมออรานเย'],
10060: ['北欧海盗','Norse Vikings','Vikingos Nórdicos','Vikings Nordiques','Viking Nordik','Nordische Wikinger','북유럽 바이킹','北歐海盜','Скандинавские викинги','Скандинавські вікінги','北欧のヴァイキング','Vichinghi Nordici','Nordyccy Wikingowie','Vikings Nórdicos','İskandinav Vikingleri','ไวกิงนอร์ส'],
10061: ['全白之环','All Whites Ring','Anillo All Whites','Anneau All Whites','Cincin All Whites','All-Whites-Ring','올 화이트 링','全白之環','Кольцо All Whites','Кільце All Whites','オールホワイツの環','Anello All Whites','Pierścień All Whites','Anel All Whites','All Whites Halkası','วงแหวนออลไวต์ส'],
10062: ['运河之环','Canal Ring','Anillo del Canal','Anneau du Canal','Cincin Kanal','Kanal-Ring','운하의 고리','運河之環','Кольцо канала','Кільце каналу','運河の環','Anello del Canale','Pierścień Kanału','Anel do Canal','Kanal Halkası','วงแหวนคลอง'],
10063: ['瓜拉尼之环','Guarani Ring','Anillo Guaraní','Anneau Guarani','Cincin Guarani','Guarani-Ring','과라니 링','瓜拉尼之環','Кольцо гуарани','Кільце гуарані','グアラニの環','Anello Guaraní','Pierścień Guarani','Anel Guarani','Guarani Halkası','วงแหวนกวารานี'],
10064: ['五盾之心','Five Shields','Cinco Escudos','Cinq Écus','Lima Perisai','Fünf Schilde','다섯 방패','五盾之心','Пять щитов','П\'ять щитів','五つの盾','Cinque Scudi','Pięć Tarcz','Cinco Escudos','Beş Kalkan','ห้าโล่'],
10065: ['栗红之环','Maroon Ring','Anillo Granate','Anneau Bordeaux','Cincin Marun','Kastanienroter Ring','마룬 링','栗紅之環','Бордовое кольцо','Бордове кільце','マルーンの環','Anello Bordeaux','Bordowy Pierścień','Anel Grená','Bordo Halkası','วงแหวนสีแดงเลือดหมู'],
10066: ['彩虹之国','Rainbow Nation','Nación Arcoíris','Nation Arc-en-ciel','Bangsa Pelangi','Regenbogennation','무지개 국가','彩虹之國','Радужная нация','Веселкова нація','虹の国','Nazione Arcobaleno','Tęczowy Naród','Nação Arco-íris','Gökkuşağı Ulusu','ชาติสายรุ้ง'],
10067: ['蓟花之环','Thistle Ring','Anillo de Cardo','Anneau Chardon','Cincin Thistle','Disteln-Ring','엉겅퀴 링','薊花之環','Кольцо чертополоха','Кільце будяка','アザミの環','Anello del Cardo','Pierścień Ostu','Anel do Cardo','Devedikeni Halkası','วงแหวนทิสเซิล'],
10068: ['特兰加雄狮','Teranga Lions','Leones de Teranga','Lions de la Teranga','Singa Teranga','Teranga-Löwen','테랑가 사자','特蘭加雄獅','Львы Теранги','Леви Теранги','テランガのライオン','Leoni della Teranga','Lwy Terangi','Leões da Teranga','Teranga Aslanları','สิงโตเทรังกา'],
10069: ['十字劲旅','Cross Squad','Escuadrón de la Cruz','Escouade de la Croix','Skuad Salib','Kreuz-Truppe','크로스 군단','十字勁旅','Крестовый отряд','Хрестовий загін','クロス軍団','Squadra della Croce','Drużyna Krzyża','Esquadrão da Cruz','Haç Takımı','ทีมกางเขน'],
10070: ['北欧蓝黄','Nordic Blue-Yellow','Azul y Amarillo Nórdico','Bleu-Jaune Nordique','Biru-Kuning Nordik','Nordisches Blau-Gelb','북유럽 블루옐로','北歐藍黃','Скандинавский сине-жёлтый','Скандинавський синьо-жовтий','北欧の青と黄','Blu-Giallo Nordico','Nordycki Niebiesko-Żółty','Azul-Amarelo Nórdico','İskandinav Mavi-Sarı','น้ำเงินเหลืองนอร์ดิก'],
10071: ['迦太基之鹰','Carthage Eagles','Águilas de Cartago','Aigles de Carthage','Elang Kartago','Karthago-Adler','카르타고의 독수리','迦太基之鷹','Орлы Карфагена','Орли Карфагена','カルタゴの鷲','Aquile di Cartagine','Orły Kartaginy','Águias de Cartago','Kartaca Kartalları','อินทรีคาร์เธจ'],
10072: ['新月之环','Crescent Ring','Anillo Creciente','Anneau du Croissant','Cincin Bulan Sabit','Halbmond-Ring','초승달 링','新月之環','Кольцо полумесяца','Кільце півмісяця','三日月の環','Anello della Mezzaluna','Pierścień Półksiężyca','Anel do Crescente','Hilal Halkası','วงแหวนพระจันทร์เสี้ยว'],
10073: ['天蓝荣光','Sky Blue Glory','Gloria Celeste','Gloire Céleste','Kejayaan Biru Langit','Himmelblauer Ruhm','하늘색 영광','天藍榮光','Небесно-голубая слава','Небесно-блакитна слава','スカイブルーの栄光','Gloria Azzurra','Błękitna Chwała','Glória Azul-Celeste','Gök Mavisi Zafer','รัศมีฟ้าคราม'],
10074: ['星条之环','Stars Stripes Ring','Anillo Barras y Estrellas','Anneau Étoilé','Cincin Bintang Garis','Stars-Stripes-Ring','성조기 링','星條之環','Кольцо звёзд и полос','Кільце зірок і смуг','星条旗の環','Anello a Stelle e Strisce','Pierścień Gwiazd i Pasów','Anel das Estrelas e Listras','Yıldız-Çizgi Halkası','วงแหวนดาวและริ้ว'],
10075: ['白狼之环','White Wolves','Lobos Blancos','Loups Blancs','Serigala Putih','Weiße Wölfe','하얀 늑대','白狼之環','Белые волки','Білі вовки','白い狼','Lupi Bianchi','Białe Wilki','Lobos Brancos','Beyaz Kurtlar','หมาป่าขาว'],
}

lines = open(TSV, encoding='utf-8').read().split('\n')
# 列宽=27, 构造新行: col0=key col1=AI col2='' col3-18=cn+15语 col19-26=''
new_rows = []
for tid, vals in sorted(T.items()):
    assert len(vals) == 16, f'{tid} 语言数{len(vals)}'  # cn+15
    key = f'TXT_PersonalizeAvatarFrameCfg_Name_{tid}'
    row = [key, 'AI', ''] + vals + [''] * 8  # 3+16+8=27
    assert len(row) == 27, f'{tid} 列数{len(row)}'
    new_rows.append('\t'.join(row))

while lines and lines[-1].strip() == '':
    lines.pop()
import shutil
shutil.copy(TSV, TSV + '.bak_wc48')
lines.extend(new_rows)
open(TSV, 'w', encoding='utf-8', newline='').write('\n'.join(lines) + '\n')
print('追加', len(new_rows), '行到 Text__Text.tsv')

# 校验
chk = [l for l in open(TSV, encoding='utf-8').read().split('\n') if l.strip()]
bad = [l.split('\t')[0] for l in chk if 'AvatarFrameCfg_Name_100' in l and int(l.split('\t')[0].split('_')[-1].split('|')[0])>=10028 and len(l.split('\t'))!=27]
print('列数异常:', bad)
print('样例:', new_rows[0].split('\t')[:6])
