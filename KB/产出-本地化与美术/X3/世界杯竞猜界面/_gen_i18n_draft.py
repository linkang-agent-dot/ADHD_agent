# -*- coding: utf-8 -*-
"""世界杯48队应援表情 i18n 翻译稿(10语)。
名字模板 {国}加油。翻译备好待 gdconfig 重灌配表后写入 Text.xlsx。
列序对齐 Text.xlsx: key|状态|opt|cn|en|sp|fr|id|de|kr|zh(繁)|ru|ua|jp
"""
import csv, os

# 国名各语种标准译名 + Emoticons ID(300+i) + Item ID(15420+i), 字母序
# 每项: code, cn, en, sp, fr, id, de, kr, zh_tw, ru, ua, jp
T = [
("ALG","阿尔及利亚","Algeria","Argelia","Algérie","Aljazair","Algerien","알제리","阿爾及利亞","Алжир","Алжир","アルジェリア"),
("ARG","阿根廷","Argentina","Argentina","Argentine","Argentina","Argentinien","아르헨티나","阿根廷","Аргентина","Аргентина","アルゼンチン"),
("AUS","澳大利亚","Australia","Australia","Australie","Australia","Australien","호주","澳大利亞","Австралия","Австралія","オーストラリア"),
("AUT","奥地利","Austria","Austria","Autriche","Austria","Österreich","오스트리아","奧地利","Австрия","Австрія","オーストリア"),
("BEL","比利时","Belgium","Bélgica","Belgique","Belgia","Belgien","벨기에","比利時","Бельгия","Бельгія","ベルギー"),
("BIH","波黑","Bosnia","Bosnia","Bosnie","Bosnia","Bosnien","보스니아","波赫","Босния","Боснія","ボスニア"),
("BRA","巴西","Brazil","Brasil","Brésil","Brasil","Brasilien","브라질","巴西","Бразилия","Бразилія","ブラジル"),
("CAN","加拿大","Canada","Canadá","Canada","Kanada","Kanada","캐나다","加拿大","Канада","Канада","カナダ"),
("CIV","科特迪瓦","Ivory Coast","Costa de Marfil","Côte d'Ivoire","Pantai Gading","Elfenbeinküste","코트디부아르","象牙海岸","Кот-д'Ивуар","Кот-д'Івуар","コートジボワール"),
("COD","刚果民主共和国","DR Congo","RD Congo","RD Congo","RD Kongo","DR Kongo","콩고민주공화국","剛果民主共和國","ДР Конго","ДР Конго","コンゴ民主共和国"),
("COL","哥伦比亚","Colombia","Colombia","Colombie","Kolombia","Kolumbien","콜롬비아","哥倫比亞","Колумбия","Колумбія","コロンビア"),
("CPV","佛得角","Cape Verde","Cabo Verde","Cap-Vert","Tanjung Verde","Kap Verde","카보베르데","維德角","Кабо-Верде","Кабо-Верде","カーボベルデ"),
("CRO","克罗地亚","Croatia","Croacia","Croatie","Kroasia","Kroatien","크로아티아","克羅埃西亞","Хорватия","Хорватія","クロアチア"),
("CUW","库拉索","Curaçao","Curazao","Curaçao","Curaçao","Curaçao","쿠라사오","庫拉索","Кюрасао","Кюрасао","キュラソー"),
("CZE","捷克","Czechia","Chequia","Tchéquie","Ceko","Tschechien","체코","捷克","Чехия","Чехія","チェコ"),
("ECU","厄瓜多尔","Ecuador","Ecuador","Équateur","Ekuador","Ecuador","에콰도르","厄瓜多","Эквадор","Еквадор","エクアドル"),
("EGY","埃及","Egypt","Egipto","Égypte","Mesir","Ägypten","이집트","埃及","Египет","Єгипет","エジプト"),
("ENG","英格兰","England","Inglaterra","Angleterre","Inggris","England","잉글랜드","英格蘭","Англия","Англія","イングランド"),
("ESP","西班牙","Spain","España","Espagne","Spanyol","Spanien","스페인","西班牙","Испания","Іспанія","スペイン"),
("FRA","法国","France","Francia","France","Prancis","Frankreich","프랑스","法國","Франция","Франція","フランス"),
("GER","德国","Germany","Alemania","Allemagne","Jerman","Deutschland","독일","德國","Германия","Німеччина","ドイツ"),
("GHA","加纳","Ghana","Ghana","Ghana","Ghana","Ghana","가나","迦納","Гана","Гана","ガーナ"),
("HAI","海地","Haiti","Haití","Haïti","Haiti","Haiti","아이티","海地","Гаити","Гаїті","ハイチ"),
("IRN","伊朗","Iran","Irán","Iran","Iran","Iran","이란","伊朗","Иран","Іран","イラン"),
("IRQ","伊拉克","Iraq","Irak","Irak","Irak","Irak","이라크","伊拉克","Ирак","Ірак","イラク"),
("JOR","约旦","Jordan","Jordania","Jordanie","Yordania","Jordanien","요르단","約旦","Иордания","Йорданія","ヨルダン"),
("JPN","日本","Japan","Japón","Japon","Jepang","Japan","일본","日本","Япония","Японія","日本"),
("KOR","韩国","South Korea","Corea del Sur","Corée du Sud","Korea Selatan","Südkorea","대한민국","韓國","Южная Корея","Південна Корея","韓国"),
("KSA","沙特阿拉伯","Saudi Arabia","Arabia Saudí","Arabie saoudite","Arab Saudi","Saudi-Arabien","사우디아라비아","沙烏地阿拉伯","Саудовская Аравия","Саудівська Аравія","サウジアラビア"),
("MAR","摩洛哥","Morocco","Marruecos","Maroc","Maroko","Marokko","모로코","摩洛哥","Марокко","Марокко","モロッコ"),
("MEX","墨西哥","Mexico","México","Mexique","Meksiko","Mexiko","멕시코","墨西哥","Мексика","Мексика","メキシコ"),
("NED","荷兰","Netherlands","Países Bajos","Pays-Bas","Belanda","Niederlande","네덜란드","荷蘭","Нидерланды","Нідерланди","オランダ"),
("NOR","挪威","Norway","Noruega","Norvège","Norwegia","Norwegen","노르웨이","挪威","Норвегия","Норвегія","ノルウェー"),
("NZL","新西兰","New Zealand","Nueva Zelanda","Nouvelle-Zélande","Selandia Baru","Neuseeland","뉴질랜드","紐西蘭","Новая Зеландия","Нова Зеландія","ニュージーランド"),
("PAN","巴拿马","Panama","Panamá","Panama","Panama","Panama","파나마","巴拿馬","Панама","Панама","パナマ"),
("PAR","巴拉圭","Paraguay","Paraguay","Paraguay","Paraguay","Paraguay","파라과이","巴拉圭","Парагвай","Парагвай","パラグアイ"),
("POR","葡萄牙","Portugal","Portugal","Portugal","Portugal","Portugal","포르투갈","葡萄牙","Португалия","Португалія","ポルトガル"),
("QAT","卡塔尔","Qatar","Catar","Qatar","Qatar","Katar","카타르","卡達","Катар","Катар","カタール"),
("RSA","南非","South Africa","Sudáfrica","Afrique du Sud","Afrika Selatan","Südafrika","남아프리카공화국","南非","ЮАР","ПАР","南アフリカ"),
("SCO","苏格兰","Scotland","Escocia","Écosse","Skotlandia","Schottland","스코틀랜드","蘇格蘭","Шотландия","Шотландія","スコットランド"),
("SEN","塞内加尔","Senegal","Senegal","Sénégal","Senegal","Senegal","세네갈","塞內加爾","Сенегал","Сенегал","セネガル"),
("SUI","瑞士","Switzerland","Suiza","Suisse","Swiss","Schweiz","스위스","瑞士","Швейцария","Швейцарія","スイス"),
("SWE","瑞典","Sweden","Suecia","Suède","Swedia","Schweden","스웨덴","瑞典","Швеция","Швеція","スウェーデン"),
("TUN","突尼斯","Tunisia","Túnez","Tunisie","Tunisia","Tunesien","튀니지","突尼西亞","Тунис","Туніс","チュニジア"),
("TUR","土耳其","Türkiye","Turquía","Turquie","Turki","Türkei","튀르키예","土耳其","Турция","Туреччина","トルコ"),
("URU","乌拉圭","Uruguay","Uruguay","Uruguay","Uruguay","Uruguay","우루과이","烏拉圭","Уругвай","Уругвай","ウルグアイ"),
("USA","美国","USA","EE. UU.","États-Unis","AS","USA","미국","美國","США","США","アメリカ"),
("UZB","乌兹别克斯坦","Uzbekistan","Uzbekistán","Ouzbékistan","Uzbekistan","Usbekistan","우즈베키스탄","烏茲別克","Узбекистан","Узбекистан","ウズベキスタン"),
]
# "加油"应援语各语种 (置于国名后/前按习惯, 这里统一 "Go {国}!" 式 / {国}+应援词)
CHEER = {  # lang: (前缀, 后缀)  用 {n}=国名
 "cn":("","加油"),"en":("Go ","!"),"sp":("¡Vamos ","!"),"fr":("Allez ","!"),
 "id":("Ayo ","!"),"de":("Los ","!"),"kr":(""," 파이팅!"),"zh":("","加油"),
 "ru":("Вперёд, ","!"),"ua":("Вперед, ","!"),"jp":("がんばれ","！"),
}
LANGS=["en","sp","fr","id","de","kr","zh","ru","ua","jp"]
NAMEIDX={"en":2,"sp":3,"fr":4,"id":5,"de":6,"kr":7,"zh":8,"ru":9,"ua":10,"jp":11}

def cheer(lang, nm):
    p,s=CHEER[lang]; return f"{p}{nm}{s}"

rows_emo=[]; rows_item=[]
for i,row in enumerate(T):
    code=row[0]; cn=row[1]
    eid=300+i; iid=15420+i
    # Emoticons.Name key
    emo_key=f"TXT_Emoticons_Name_{eid}"
    emo_cn=f"[{cheer('cn',cn)}]"
    emo_tr=[f"[{cheer(l, row[NAMEIDX[l]])}]" for l in LANGS]
    rows_emo.append([emo_key,"AI","",emo_cn]+emo_tr)
    # Item.Name key (道具名 "{国}加油（表情）")
    item_key=f"TXT_Item_Name_{iid}"
    item_cn=f"{cheer('cn',cn)}（表情）"
    item_tr=[]
    for l in LANGS:
        c=cheer(l,row[NAMEIDX[l]])
        item_tr.append(f"{c}（表情）" if l=="zh" else f"{c} (Emote)")
    rows_item.append([item_key,"AI","",item_cn]+item_tr)

OUT=r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\应援表情48_落地素材"
hdr=["key","状态","opt","cn"]+LANGS
with open(os.path.join(OUT,"_i18n翻译稿.tsv"),"w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f,delimiter="\t"); w.writerow(hdr)
    for r in rows_emo: w.writerow(r)
    for r in rows_item: w.writerow(r)
print(f"翻译稿生成: Emoticons {len(rows_emo)} + Item {len(rows_item)} = {len(rows_emo)+len(rows_item)} 行")
print("样本Emo:",rows_emo[6][:6])
print("样本Item:",rows_item[6][:6])
