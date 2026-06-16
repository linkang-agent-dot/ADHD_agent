# -*- coding: utf-8 -*-
"""世界杯48队应援表情 i18n: 生成96行(48 Emoticons名+48 Item名)x15语, 追加进 Text__Text.tsv。
列序: col1=key col2=状态AI col3=opt col4=cn col5-19=en/sp/fr/id/de/kr/zh/ru/ua/jp/it/pl/po/tr/th
名字模板 [{国}加油] / {国}加油（表情）。"""
import os,shutil,datetime

TEXT=r"C:\x3\gdconfig\tsv\i18n\Text__Text.tsv"

# code: cn, 15语国名(en sp fr id de kr zh ru ua jp it pl po tr th)
T={
"ALG":("阿尔及利亚","Algeria","Argelia","Algérie","Aljazair","Algerien","알제리","阿爾及利亞","Алжир","Алжир","アルジェリア","Algeria","Algieria","Argélia","Cezayir","แอลจีเรีย"),
"ARG":("阿根廷","Argentina","Argentina","Argentine","Argentina","Argentinien","아르헨티나","阿根廷","Аргентина","Аргентина","アルゼンチン","Argentina","Argentyna","Argentina","Arjantin","อาร์เจนตินา"),
"AUS":("澳大利亚","Australia","Australia","Australie","Australia","Australien","호주","澳大利亞","Австралия","Австралія","オーストラリア","Australia","Australia","Austrália","Avustralya","ออสเตรเลีย"),
"AUT":("奥地利","Austria","Austria","Autriche","Austria","Österreich","오스트리아","奧地利","Австрия","Австрія","オーストリア","Austria","Austria","Áustria","Avusturya","ออสเตรีย"),
"BEL":("比利时","Belgium","Bélgica","Belgique","Belgia","Belgien","벨기에","比利時","Бельгия","Бельгія","ベルギー","Belgio","Belgia","Bélgica","Belçika","เบลเยียม"),
"BIH":("波黑","Bosnia","Bosnia","Bosnie","Bosnia","Bosnien","보스니아","波赫","Босния","Боснія","ボスニア","Bosnia","Bośnia","Bósnia","Bosna","บอสเนีย"),
"BRA":("巴西","Brazil","Brasil","Brésil","Brasil","Brasilien","브라질","巴西","Бразилия","Бразилія","ブラジル","Brasile","Brazylia","Brasil","Brezilya","บราซิล"),
"CAN":("加拿大","Canada","Canadá","Canada","Kanada","Kanada","캐나다","加拿大","Канада","Канада","カナダ","Canada","Kanada","Canadá","Kanada","แคนาดา"),
"CIV":("科特迪瓦","Ivory Coast","Costa de Marfil","Côte d'Ivoire","Pantai Gading","Elfenbeinküste","코트디부아르","象牙海岸","Кот-д'Ивуар","Кот-д'Івуар","コートジボワール","Costa d'Avorio","Wybrzeże Kości Słoniowej","Costa do Marfim","Fildişi Sahili","ไอวอรีโคสต์"),
"COD":("刚果民主共和国","DR Congo","RD Congo","RD Congo","RD Kongo","DR Kongo","콩고민주공화국","剛果民主共和國","ДР Конго","ДР Конго","コンゴ民主共和国","RD Congo","DR Konga","RD Congo","DR Kongo","ดีอาร์คองโก"),
"COL":("哥伦比亚","Colombia","Colombia","Colombie","Kolombia","Kolumbien","콜롬비아","哥倫比亞","Колумбия","Колумбія","コロンビア","Colombia","Kolumbia","Colômbia","Kolombiya","โคลอมเบีย"),
"CPV":("佛得角","Cape Verde","Cabo Verde","Cap-Vert","Tanjung Verde","Kap Verde","카보베르데","維德角","Кабо-Верде","Кабо-Верде","カーボベルデ","Capo Verde","Republika Zielonego Przylądka","Cabo Verde","Cabo Verde","เคปเวิร์ด"),
"CRO":("克罗地亚","Croatia","Croacia","Croatie","Kroasia","Kroatien","크로아티아","克羅埃西亞","Хорватия","Хорватія","クロアチア","Croazia","Chorwacja","Croácia","Hırvatistan","โครเอเชีย"),
"CUW":("库拉索","Curaçao","Curazao","Curaçao","Curaçao","Curaçao","쿠라사오","庫拉索","Кюрасао","Кюрасао","キュラソー","Curaçao","Curaçao","Curaçao","Curaçao","กือราเซา"),
"CZE":("捷克","Czechia","Chequia","Tchéquie","Ceko","Tschechien","체코","捷克","Чехия","Чехія","チェコ","Cechia","Czechy","Tchéquia","Çekya","เช็กเกีย"),
"ECU":("厄瓜多尔","Ecuador","Ecuador","Équateur","Ekuador","Ecuador","에콰도르","厄瓜多","Эквадор","Еквадор","エクアドル","Ecuador","Ekwador","Equador","Ekvador","เอกวาดอร์"),
"EGY":("埃及","Egypt","Egipto","Égypte","Mesir","Ägypten","이집트","埃及","Египет","Єгипет","エジプト","Egitto","Egipt","Egito","Mısır","อียิปต์"),
"ENG":("英格兰","England","Inglaterra","Angleterre","Inggris","England","잉글랜드","英格蘭","Англия","Англія","イングランド","Inghilterra","Anglia","Inglaterra","İngiltere","อังกฤษ"),
"ESP":("西班牙","Spain","España","Espagne","Spanyol","Spanien","스페인","西班牙","Испания","Іспанія","スペイン","Spagna","Hiszpania","Espanha","İspanya","สเปน"),
"FRA":("法国","France","Francia","France","Prancis","Frankreich","프랑스","法國","Франция","Франція","フランス","Francia","Francja","França","Fransa","ฝรั่งเศส"),
"GER":("德国","Germany","Alemania","Allemagne","Jerman","Deutschland","독일","德國","Германия","Німеччина","ドイツ","Germania","Niemcy","Alemanha","Almanya","เยอรมนี"),
"GHA":("加纳","Ghana","Ghana","Ghana","Ghana","Ghana","가나","迦納","Гана","Гана","ガーナ","Ghana","Ghana","Gana","Gana","กานา"),
"HAI":("海地","Haiti","Haití","Haïti","Haiti","Haiti","아이티","海地","Гаити","Гаїті","ハイチ","Haiti","Haiti","Haiti","Haiti","เฮติ"),
"IRN":("伊朗","Iran","Irán","Iran","Iran","Iran","이란","伊朗","Иран","Іран","イラン","Iran","Iran","Irã","İran","อิหร่าน"),
"IRQ":("伊拉克","Iraq","Irak","Irak","Irak","Irak","이라크","伊拉克","Ирак","Ірак","イラク","Iraq","Irak","Iraque","Irak","อิรัก"),
"JOR":("约旦","Jordan","Jordania","Jordanie","Yordania","Jordanien","요르단","約旦","Иордания","Йорданія","ヨルダン","Giordania","Jordania","Jordânia","Ürdün","จอร์แดน"),
"JPN":("日本","Japan","Japón","Japon","Jepang","Japan","일본","日本","Япония","Японія","日本","Giappone","Japonia","Japão","Japonya","ญี่ปุ่น"),
"KOR":("韩国","South Korea","Corea del Sur","Corée du Sud","Korea Selatan","Südkorea","대한민국","韓國","Южная Корея","Південна Корея","韓国","Corea del Sud","Korea Płd.","Coreia do Sul","Güney Kore","เกาหลีใต้"),
"KSA":("沙特阿拉伯","Saudi Arabia","Arabia Saudí","Arabie saoudite","Arab Saudi","Saudi-Arabien","사우디아라비아","沙烏地阿拉伯","Саудовская Аравия","Саудівська Аравія","サウジアラビア","Arabia Saudita","Arabia Saudyjska","Arábia Saudita","Suudi Arabistan","ซาอุดีอาระเบีย"),
"MAR":("摩洛哥","Morocco","Marruecos","Maroc","Maroko","Marokko","모로코","摩洛哥","Марокко","Марокко","モロッコ","Marocco","Maroko","Marrocos","Fas","โมร็อกโก"),
"MEX":("墨西哥","Mexico","México","Mexique","Meksiko","Mexiko","멕시코","墨西哥","Мексика","Мексика","メキシコ","Messico","Meksyk","México","Meksika","เม็กซิโก"),
"NED":("荷兰","Netherlands","Países Bajos","Pays-Bas","Belanda","Niederlande","네덜란드","荷蘭","Нидерланды","Нідерланди","オランダ","Paesi Bassi","Holandia","Países Baixos","Hollanda","เนเธอร์แลนด์"),
"NOR":("挪威","Norway","Noruega","Norvège","Norwegia","Norwegen","노르웨이","挪威","Норвегия","Норвегія","ノルウェー","Norvegia","Norwegia","Noruega","Norveç","นอร์เวย์"),
"NZL":("新西兰","New Zealand","Nueva Zelanda","Nouvelle-Zélande","Selandia Baru","Neuseeland","뉴질랜드","紐西蘭","Новая Зеландия","Нова Зеландія","ニュージーランド","Nuova Zelanda","Nowa Zelandia","Nova Zelândia","Yeni Zelanda","นิวซีแลนด์"),
"PAN":("巴拿马","Panama","Panamá","Panama","Panama","Panama","파나마","巴拿馬","Панама","Панама","パナマ","Panama","Panama","Panamá","Panama","ปานามา"),
"PAR":("巴拉圭","Paraguay","Paraguay","Paraguay","Paraguay","Paraguay","파라과이","巴拉圭","Парагвай","Парагвай","パラグアイ","Paraguay","Paragwaj","Paraguai","Paraguay","ปารากวัย"),
"POR":("葡萄牙","Portugal","Portugal","Portugal","Portugal","Portugal","포르투갈","葡萄牙","Португалия","Португалія","ポルトガル","Portogallo","Portugalia","Portugal","Portekiz","โปรตุเกส"),
"QAT":("卡塔尔","Qatar","Catar","Qatar","Qatar","Katar","카타르","卡達","Катар","Катар","カタール","Qatar","Katar","Catar","Katar","กาตาร์"),
"RSA":("南非","South Africa","Sudáfrica","Afrique du Sud","Afrika Selatan","Südafrika","남아프리카공화국","南非","ЮАР","ПАР","南アフリカ","Sudafrica","RPA","África do Sul","Güney Afrika","แอฟริกาใต้"),
"SCO":("苏格兰","Scotland","Escocia","Écosse","Skotlandia","Schottland","스코틀랜드","蘇格蘭","Шотландия","Шотландія","スコットランド","Scozia","Szkocja","Escócia","İskoçya","สกอตแลนด์"),
"SEN":("塞内加尔","Senegal","Senegal","Sénégal","Senegal","Senegal","세네갈","塞內加爾","Сенегал","Сенегал","セネガル","Senegal","Senegal","Senegal","Senegal","เซเนกัล"),
"SUI":("瑞士","Switzerland","Suiza","Suisse","Swiss","Schweiz","스위스","瑞士","Швейцария","Швейцарія","スイス","Svizzera","Szwajcaria","Suíça","İsviçre","สวิตเซอร์แลนด์"),
"SWE":("瑞典","Sweden","Suecia","Suède","Swedia","Schweden","스웨덴","瑞典","Швеция","Швеція","スウェーデン","Svezia","Szwecja","Suécia","İsveç","สวีเดน"),
"TUN":("突尼斯","Tunisia","Túnez","Tunisie","Tunisia","Tunesien","튀니지","突尼西亞","Тунис","Туніс","チュニジア","Tunisia","Tunezja","Tunísia","Tunus","ตูนิเซีย"),
"TUR":("土耳其","Türkiye","Turquía","Turquie","Turki","Türkei","튀르키예","土耳其","Турция","Туреччина","トルコ","Turchia","Turcja","Turquia","Türkiye","ตุรกี"),
"URU":("乌拉圭","Uruguay","Uruguay","Uruguay","Uruguay","Uruguay","우루과이","烏拉圭","Уругвай","Уругвай","ウルグアイ","Uruguay","Urugwaj","Uruguai","Uruguay","อุรุกวัย"),
"USA":("美国","USA","EE. UU.","États-Unis","AS","USA","미국","美國","США","США","アメリカ","USA","USA","EUA","ABD","สหรัฐฯ"),
"UZB":("乌兹别克斯坦","Uzbekistan","Uzbekistán","Ouzbékistan","Uzbekistan","Usbekistan","우즈베키스탄","烏茲別克","Узбекистан","Узбекистан","ウズベキスタン","Uzbekistan","Uzbekistan","Uzbequistão","Özbekistan","อุซเบกิสถาน"),
}
# 应援词: (前,后) 15语+cn 顺序 = cn,en,sp,fr,id,de,kr,zh,ru,ua,jp,it,pl,po,tr,th
CH=[("","加油"),("Go ","!"),("¡Vamos ","!"),("Allez ","!"),("Ayo ","!"),("Los ","!"),(""," 파이팅!"),("","加油"),
    ("Вперёд, ","!"),("Вперед, ","!"),("がんばれ","！"),("Forza ","!"),("Naprzód ","!"),("Vai ","!"),("Haydi ","!"),("สู้ ๆ ","!")]
codes=sorted(T)
NF=len(open(TEXT,encoding="utf-8").readline().rstrip("\n").split("\t"))  # 列数

def cheer(idx,nm):
    p,s=CH[idx]; return f"{p}{nm}{s}"

rows=[]
for i,c in enumerate(codes):
    names=T[c]  # [cn, 15语...]
    eid=300+i; iid=15420+i
    # Emoticons 名 [国加油]
    f=[""]*NF
    f[0]=f"TXT_Emoticons_Name_{eid}"; f[1]="AI"
    f[3]=f"[{cheer(0,names[0])}]"
    for j in range(15): f[4+j]=f"[{cheer(j+1,names[j+1])}]"
    rows.append("\t".join(f))
    # Item 名 国加油（表情） / X (Emote)
    f=[""]*NF
    f[0]=f"TXT_Item_Name_{iid}"; f[1]="AI"
    f[3]=f"{cheer(0,names[0])}（表情）"
    for j in range(15):
        c2=cheer(j+1,names[j+1]); f[4+j]=f"{c2}（表情）" if (j+1)==7 else f"{c2} (Emote)"  # j+1==7 -> zh
    rows.append("\t".join(f))

# 备份+追加(LF行尾!)
shutil.copyfile(TEXT, TEXT+".bak_wc")
body=open(TEXT,encoding="utf-8").read().rstrip("\n")
open(TEXT,"w",encoding="utf-8",newline="\n").write(body+"\n"+"\n".join(rows)+"\n")
print(f"已追加 {len(rows)} 行(48 Emoticons名+48 Item名)x15语, 备份={os.path.basename(TEXT)}.bak_wc")
# 验证
import io
n=sum(1 for l in open(TEXT,encoding="utf-8") if l.startswith(("TXT_Emoticons_Name_30","TXT_Item_Name_154")))
print("Text表WC key行数:",n)
PY=open(TEXT,encoding="utf-8").read()
print("CRLF检查:", open(TEXT,'rb').read().count(b'\r\n'),"(应0)")
