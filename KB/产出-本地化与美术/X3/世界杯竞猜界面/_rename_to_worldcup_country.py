# -*- coding: utf-8 -*-
import io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CFG = r'C:\x3\gdconfig\tsv\Personalize__PersonalizeAvatarFrameCfg.tsv'
TXT = r'C:\x3\gdconfig\tsv\i18n\Text__Text.tsv'

# "世界杯" 15语 (顺序: cn,en,sp,fr,id,de,kr,zh繁,ru,ua,jp,it,pl,po葡,tr,th)
WC = ['世界杯','World Cup','Mundial','Coupe du Monde','Piala Dunia','WM','월드컵','世界盃',
      'Чемпионат мира','Чемпіонат світу','ワールドカップ','Mondiali','Mistrzostwa Świata',
      'Copa do Mundo','Dünya Kupası','ฟุตบอลโลก']

# 三字码 -> 国名 15语 (同顺序)
C = {
'ALG':['阿尔及利亚','Algeria','Argelia','Algérie','Aljazair','Algerien','알제리','阿爾及利亞','Алжир','Алжир','アルジェリア','Algeria','Algieria','Argélia','Cezayir','แอลจีเรีย'],
'ARG':['阿根廷','Argentina','Argentina','Argentine','Argentina','Argentinien','아르헨티나','阿根廷','Аргентина','Аргентина','アルゼンチン','Argentina','Argentyna','Argentina','Arjantin','อาร์เจนตินา'],
'AUS':['澳大利亚','Australia','Australia','Australie','Australia','Australien','호주','澳大利亞','Австралия','Австралія','オーストラリア','Australia','Australia','Austrália','Avustralya','ออสเตรเลีย'],
'AUT':['奥地利','Austria','Austria','Autriche','Austria','Österreich','오스트리아','奧地利','Австрия','Австрія','オーストリア','Austria','Austria','Áustria','Avusturya','ออสเตรีย'],
'BEL':['比利时','Belgium','Bélgica','Belgique','Belgia','Belgien','벨기에','比利時','Бельгия','Бельгія','ベルギー','Belgio','Belgia','Bélgica','Belçika','เบลเยียม'],
'BIH':['波黑','Bosnia','Bosnia','Bosnie','Bosnia','Bosnien','보스니아','波赫','Босния','Боснія','ボスニア','Bosnia','Bośnia','Bósnia','Bosna','บอสเนีย'],
'BRA':['巴西','Brazil','Brasil','Brésil','Brasil','Brasilien','브라질','巴西','Бразилия','Бразилія','ブラジル','Brasile','Brazylia','Brasil','Brezilya','บราซิล'],
'CAN':['加拿大','Canada','Canadá','Canada','Kanada','Kanada','캐나다','加拿大','Канада','Канада','カナダ','Canada','Kanada','Canadá','Kanada','แคนาดา'],
'CIV':['科特迪瓦','Ivory Coast','Costa de Marfil','Côte d\'Ivoire','Pantai Gading','Elfenbeinküste','코트디부아르','科特迪瓦','Кот-д\'Ивуар','Кот-д\'Івуар','コートジボワール','Costa d\'Avorio','Wybrzeże Kości Słoniowej','Costa do Marfim','Fildişi Sahili','ไอวอรีโคสต์'],
'COD':['刚果','DR Congo','RD Congo','RD Congo','RD Kongo','DR Kongo','콩고민주공화국','剛果','ДР Конго','ДР Конго','コンゴ民主共和国','RD Congo','DR Konga','RD Congo','DR Kongo','คองโก'],
'COL':['哥伦比亚','Colombia','Colombia','Colombie','Kolombia','Kolumbien','콜롬비아','哥倫比亞','Колумбия','Колумбія','コロンビア','Colombia','Kolumbia','Colômbia','Kolombiya','โคลอมเบีย'],
'CPV':['佛得角','Cape Verde','Cabo Verde','Cap-Vert','Tanjung Verde','Kap Verde','카보베르데','維德角','Кабо-Верде','Кабо-Верде','カーボベルデ','Capo Verde','Republika Zielonego Przylądka','Cabo Verde','Cabo Verde','เคปเวิร์ด'],
'CRO':['克罗地亚','Croatia','Croacia','Croatie','Kroasia','Kroatien','크로아티아','克羅地亞','Хорватия','Хорватія','クロアチア','Croazia','Chorwacja','Croácia','Hırvatistan','โครเอเชีย'],
'CUW':['库拉索','Curaçao','Curazao','Curaçao','Curaçao','Curaçao','퀴라소','庫拉索','Кюрасао','Кюрасао','キュラソー','Curaçao','Curaçao','Curaçao','Curaçao','คูราเซา'],
'CZE':['捷克','Czechia','Chequia','Tchéquie','Ceko','Tschechien','체코','捷克','Чехия','Чехія','チェコ','Cechia','Czechy','Chéquia','Çekya','เช็ก'],
'ECU':['厄瓜多尔','Ecuador','Ecuador','Équateur','Ekuador','Ecuador','에콰도르','厄瓜多爾','Эквадор','Еквадор','エクアドル','Ecuador','Ekwador','Equador','Ekvador','เอกวาดอร์'],
'EGY':['埃及','Egypt','Egipto','Égypte','Mesir','Ägypten','이집트','埃及','Египет','Єгипет','エジプト','Egitto','Egipt','Egito','Mısır','อียิปต์'],
'ENG':['英格兰','England','Inglaterra','Angleterre','Inggris','England','잉글랜드','英格蘭','Англия','Англія','イングランド','Inghilterra','Anglia','Inglaterra','İngiltere','อังกฤษ'],
'ESP':['西班牙','Spain','España','Espagne','Spanyol','Spanien','스페인','西班牙','Испания','Іспанія','スペイン','Spagna','Hiszpania','Espanha','İspanya','สเปน'],
'FRA':['法国','France','Francia','France','Prancis','Frankreich','프랑스','法國','Франция','Франція','フランス','Francia','Francja','França','Fransa','ฝรั่งเศส'],
'GER':['德国','Germany','Alemania','Allemagne','Jerman','Deutschland','독일','德國','Германия','Німеччина','ドイツ','Germania','Niemcy','Alemanha','Almanya','เยอรมนี'],
'GHA':['加纳','Ghana','Ghana','Ghana','Ghana','Ghana','가나','加納','Гана','Гана','ガーナ','Ghana','Ghana','Gana','Gana','กานา'],
'HAI':['海地','Haiti','Haití','Haïti','Haiti','Haiti','아이티','海地','Гаити','Гаїті','ハイチ','Haiti','Haiti','Haiti','Haiti','เฮติ'],
'IRN':['伊朗','Iran','Irán','Iran','Iran','Iran','이란','伊朗','Иран','Іран','イラン','Iran','Iran','Irã','İran','อิหร่าน'],
'IRQ':['伊拉克','Iraq','Irak','Irak','Irak','Irak','이라크','伊拉克','Ирак','Ірак','イラク','Iraq','Irak','Iraque','Irak','อิรัก'],
'JOR':['约旦','Jordan','Jordania','Jordanie','Yordania','Jordanien','요르단','約旦','Иордания','Йорданія','ヨルダン','Giordania','Jordania','Jordânia','Ürdün','จอร์แดน'],
'JPN':['日本','Japan','Japón','Japon','Jepang','Japan','일본','日本','Япония','Японія','日本','Giappone','Japonia','Japão','Japonya','ญี่ปุ่น'],
'KOR':['韩国','South Korea','Corea del Sur','Corée du Sud','Korea Selatan','Südkorea','대한민국','韓國','Южная Корея','Південна Корея','韓国','Corea del Sud','Korea Południowa','Coreia do Sul','Güney Kore','เกาหลีใต้'],
'KSA':['沙特','Saudi Arabia','Arabia Saudí','Arabie Saoudite','Arab Saudi','Saudi-Arabien','사우디아라비아','沙特阿拉伯','Саудовская Аравия','Саудівська Аравія','サウジアラビア','Arabia Saudita','Arabia Saudyjska','Arábia Saudita','Suudi Arabistan','ซาอุดีอาระเบีย'],
'MAR':['摩洛哥','Morocco','Marruecos','Maroc','Maroko','Marokko','모로코','摩洛哥','Марокко','Марокко','モロッコ','Marocco','Maroko','Marrocos','Fas','โมร็อกโก'],
'MEX':['墨西哥','Mexico','México','Mexique','Meksiko','Mexiko','멕시코','墨西哥','Мексика','Мексика','メキシコ','Messico','Meksyk','México','Meksika','เม็กซิโก'],
'NED':['荷兰','Netherlands','Países Bajos','Pays-Bas','Belanda','Niederlande','네덜란드','荷蘭','Нидерланды','Нідерланди','オランダ','Paesi Bassi','Holandia','Países Baixos','Hollanda','เนเธอร์แลนด์'],
'NOR':['挪威','Norway','Noruega','Norvège','Norwegia','Norwegen','노르웨이','挪威','Норвегия','Норвегія','ノルウェー','Norvegia','Norwegia','Noruega','Norveç','นอร์เวย์'],
'NZL':['新西兰','New Zealand','Nueva Zelanda','Nouvelle-Zélande','Selandia Baru','Neuseeland','뉴질랜드','紐西蘭','Новая Зеландия','Нова Зеландія','ニュージーランド','Nuova Zelanda','Nowa Zelandia','Nova Zelândia','Yeni Zelanda','นิวซีแลนด์'],
'PAN':['巴拿马','Panama','Panamá','Panama','Panama','Panama','파나마','巴拿馬','Панама','Панама','パナマ','Panama','Panama','Panamá','Panama','ปานามา'],
'PAR':['巴拉圭','Paraguay','Paraguay','Paraguay','Paraguay','Paraguay','파라과이','巴拉圭','Парагвай','Парагвай','パラグアイ','Paraguay','Paragwaj','Paraguai','Paraguay','ปารากวัย'],
'POR':['葡萄牙','Portugal','Portugal','Portugal','Portugal','Portugal','포르투갈','葡萄牙','Португалия','Португалія','ポルトガル','Portogallo','Portugalia','Portugal','Portekiz','โปรตุเกส'],
'QAT':['卡塔尔','Qatar','Catar','Qatar','Qatar','Katar','카타르','卡塔爾','Катар','Катар','カタール','Qatar','Katar','Catar','Katar','กาตาร์'],
'RSA':['南非','South Africa','Sudáfrica','Afrique du Sud','Afrika Selatan','Südafrika','남아프리카','南非','ЮАР','ПАР','南アフリカ','Sudafrica','RPA','África do Sul','Güney Afrika','แอฟริกาใต้'],
'SCO':['苏格兰','Scotland','Escocia','Écosse','Skotlandia','Schottland','스코틀랜드','蘇格蘭','Шотландия','Шотландія','スコットランド','Scozia','Szkocja','Escócia','İskoçya','สกอตแลนด์'],
'SEN':['塞内加尔','Senegal','Senegal','Sénégal','Senegal','Senegal','세네갈','塞內加爾','Сенегал','Сенегал','セネガル','Senegal','Senegal','Senegal','Senegal','เซเนกัล'],
'SUI':['瑞士','Switzerland','Suiza','Suisse','Swiss','Schweiz','스위스','瑞士','Швейцария','Швейцарія','スイス','Svizzera','Szwajcaria','Suíça','İsviçre','สวิตเซอร์แลนด์'],
'SWE':['瑞典','Sweden','Suecia','Suède','Swedia','Schweden','스웨덴','瑞典','Швеция','Швеція','スウェーデン','Svezia','Szwecja','Suécia','İsveç','สวีเดน'],
'TUN':['突尼斯','Tunisia','Túnez','Tunisie','Tunisia','Tunesien','튀니지','突尼西亞','Тунис','Туніс','チュニジア','Tunisia','Tunezja','Tunísia','Tunus','ตูนิเซีย'],
'TUR':['土耳其','Türkiye','Turquía','Turquie','Turki','Türkei','튀르키예','土耳其','Турция','Туреччина','トルコ','Turchia','Turcja','Turquia','Türkiye','ตุรกี'],
'URU':['乌拉圭','Uruguay','Uruguay','Uruguay','Uruguay','Uruguay','우루과이','烏拉圭','Уругвай','Уругвай','ウルグアイ','Uruguay','Urugwaj','Uruguai','Uruguay','อุรุกวัย'],
'USA':['美国','United States','Estados Unidos','États-Unis','Amerika Serikat','USA','미국','美國','США','США','アメリカ','Stati Uniti','USA','Estados Unidos','ABD','สหรัฐอเมริกา'],
'UZB':['乌兹别克斯坦','Uzbekistan','Uzbekistán','Ouzbékistan','Uzbekistan','Usbekistan','우즈베키스탄','烏茲別克','Узбекистан','Узбекистан','ウズベキスタン','Uzbekistan','Uzbekistan','Uzbequistão','Özbekistan','อุซเบกิสถาน'],
}

# 组合: 中文用 "世界杯·德国"(中点); 其他语言用 "World Cup Germany"(空格)
def combined(code):
    natn = C[code]
    out = []
    for i in range(16):
        if i in (0, 7):  # cn(0) 和 繁中zh(7) 用中点
            out.append(f'{WC[i]}·{natn[i]}')
        else:
            out.append(f'{WC[i]} {natn[i]}')
    return out  # 16项: cn+15语

# ===== 1. 改配置表 Name 列(col9) = 中文组合名 =====
shutil.copy(CFG, CFG + '.bak_rename')
clines = open(CFG, encoding='utf-8').read().split('\n')
n1 = 0
for i, l in enumerate(clines):
    c = l.split('\t')
    if c[0].isdigit() and int(c[0]) >= 10028:
        code = c[4].replace('DK_Img_Player_AvatarFrame_WC_', '')
        if code in C:
            c[9] = combined(code)[0]  # cn
            clines[i] = '\t'.join(c)
            n1 += 1
open(CFG, 'w', encoding='utf-8', newline='').write('\n'.join(clines))
print('配置表Name改', n1, '行 | 样例GER:', combined('GER')[0])

# ===== 2. 改 Text i18n 48行 全语言 =====
shutil.copy(TXT, TXT + '.bak_rename')
tlines = open(TXT, encoding='utf-8').read().split('\n')
# ID -> code 映射(从配置表)
id2code = {}
for l in clines:
    c = l.split('\t')
    if c[0].isdigit() and int(c[0]) >= 10028:
        id2code[c[0]] = c[4].replace('DK_Img_Player_AvatarFrame_WC_', '')
n2 = 0
for i, l in enumerate(tlines):
    c = l.split('\t')
    if c and c[0].startswith('TXT_PersonalizeAvatarFrameCfg_Name_'):
        tid = c[0].split('_')[-1].split('|')[0]
        if tid in id2code and int(tid) >= 10028:
            code = id2code[tid]
            vals = combined(code)  # 16: cn+15
            # col3=cn, col4-18=15语
            for j in range(16):
                c[3 + j] = vals[j]
            tlines[i] = '\t'.join(c)
            n2 += 1
open(TXT, 'w', encoding='utf-8', newline='').write('\n'.join(tlines))
print('Text i18n改', n2, '行 | 样例GER:', combined('GER')[:4])
