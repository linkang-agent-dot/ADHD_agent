# -*- coding: utf-8 -*-
"""世界杯 32 支 R32 球队队名 20 语言表 + 结果句式模板。供 _gen_发奖详情.py 注入每场邮件「对阵+最终结果」。
语言键对齐 multilang_mail.LANG_CODES / MAIL: en cn zh fr de ru jp kr sp id th ar ro nl tr po it vi fa pls
缺队/缺语言时调用方回退 FIFA 三字码。"""

LANGS = ["en","cn","zh","fr","de","ru","jp","kr","sp","id","th","ar","ro","nl","tr","po","it","vi","fa","pls"]

# 队名: code -> {lang: name}
TEAM = {
"RSA": {"en":"South Africa","cn":"南非","zh":"南非","fr":"Afrique du Sud","de":"Südafrika","ru":"ЮАР","jp":"南アフリカ","kr":"남아프리카공화국","sp":"Sudáfrica","id":"Afrika Selatan","th":"แอฟริกาใต้","ar":"جنوب أفريقيا","ro":"Africa de Sud","nl":"Zuid-Afrika","tr":"Güney Afrika","po":"África do Sul","it":"Sudafrica","vi":"Nam Phi","fa":"آفریقای جنوبی","pls":"RPA"},
"CAN": {"en":"Canada","cn":"加拿大","zh":"加拿大","fr":"Canada","de":"Kanada","ru":"Канада","jp":"カナダ","kr":"캐나다","sp":"Canadá","id":"Kanada","th":"แคนาดา","ar":"كندا","ro":"Canada","nl":"Canada","tr":"Kanada","po":"Canadá","it":"Canada","vi":"Canada","fa":"کانادا","pls":"Kanada"},
"BRA": {"en":"Brazil","cn":"巴西","zh":"巴西","fr":"Brésil","de":"Brasilien","ru":"Бразилия","jp":"ブラジル","kr":"브라질","sp":"Brasil","id":"Brasil","th":"บราซิล","ar":"البرازيل","ro":"Brazilia","nl":"Brazilië","tr":"Brezilya","po":"Brasil","it":"Brasile","vi":"Brazil","fa":"برزیل","pls":"Brazylia"},
"JPN": {"en":"Japan","cn":"日本","zh":"日本","fr":"Japon","de":"Japan","ru":"Япония","jp":"日本","kr":"일본","sp":"Japón","id":"Jepang","th":"ญี่ปุ่น","ar":"اليابان","ro":"Japonia","nl":"Japan","tr":"Japonya","po":"Japão","it":"Giappone","vi":"Nhật Bản","fa":"ژاپن","pls":"Japonia"},
"GER": {"en":"Germany","cn":"德国","zh":"德國","fr":"Allemagne","de":"Deutschland","ru":"Германия","jp":"ドイツ","kr":"독일","sp":"Alemania","id":"Jerman","th":"เยอรมนี","ar":"ألمانيا","ro":"Germania","nl":"Duitsland","tr":"Almanya","po":"Alemanha","it":"Germania","vi":"Đức","fa":"آلمان","pls":"Niemcy"},
"PAR": {"en":"Paraguay","cn":"巴拉圭","zh":"巴拉圭","fr":"Paraguay","de":"Paraguay","ru":"Парагвай","jp":"パラグアイ","kr":"파라과이","sp":"Paraguay","id":"Paraguay","th":"ปารากวัย","ar":"باراغواي","ro":"Paraguay","nl":"Paraguay","tr":"Paraguay","po":"Paraguai","it":"Paraguay","vi":"Paraguay","fa":"پاراگوئه","pls":"Paragwaj"},
"NED": {"en":"Netherlands","cn":"荷兰","zh":"荷蘭","fr":"Pays-Bas","de":"Niederlande","ru":"Нидерланды","jp":"オランダ","kr":"네덜란드","sp":"Países Bajos","id":"Belanda","th":"เนเธอร์แลนด์","ar":"هولندا","ro":"Țările de Jos","nl":"Nederland","tr":"Hollanda","po":"Países Baixos","it":"Paesi Bassi","vi":"Hà Lan","fa":"هلند","pls":"Holandia"},
"MAR": {"en":"Morocco","cn":"摩洛哥","zh":"摩洛哥","fr":"Maroc","de":"Marokko","ru":"Марокко","jp":"モロッコ","kr":"모로코","sp":"Marruecos","id":"Maroko","th":"โมร็อกโก","ar":"المغرب","ro":"Maroc","nl":"Marokko","tr":"Fas","po":"Marrocos","it":"Marocco","vi":"Maroc","fa":"مراکش","pls":"Maroko"},
"CIV": {"en":"Ivory Coast","cn":"科特迪瓦","zh":"科特迪瓦","fr":"Côte d'Ivoire","de":"Elfenbeinküste","ru":"Кот-д'Ивуар","jp":"コートジボワール","kr":"코트디부아르","sp":"Costa de Marfil","id":"Pantai Gading","th":"ไอวอรีโคสต์","ar":"ساحل العاج","ro":"Coasta de Fildeș","nl":"Ivoorkust","tr":"Fildişi Sahili","po":"Costa do Marfim","it":"Costa d'Avorio","vi":"Bờ Biển Ngà","fa":"ساحل عاج","pls":"Wybrzeże Kości Słoniowej"},
"NOR": {"en":"Norway","cn":"挪威","zh":"挪威","fr":"Norvège","de":"Norwegen","ru":"Норвегия","jp":"ノルウェー","kr":"노르웨이","sp":"Noruega","id":"Norwegia","th":"นอร์เวย์","ar":"النرويج","ro":"Norvegia","nl":"Noorwegen","tr":"Norveç","po":"Noruega","it":"Norvegia","vi":"Na Uy","fa":"نروژ","pls":"Norwegia"},
"FRA": {"en":"France","cn":"法国","zh":"法國","fr":"France","de":"Frankreich","ru":"Франция","jp":"フランス","kr":"프랑스","sp":"Francia","id":"Prancis","th":"ฝรั่งเศส","ar":"فرنسا","ro":"Franța","nl":"Frankrijk","tr":"Fransa","po":"França","it":"Francia","vi":"Pháp","fa":"فرانسه","pls":"Francja"},
"SWE": {"en":"Sweden","cn":"瑞典","zh":"瑞典","fr":"Suède","de":"Schweden","ru":"Швеция","jp":"スウェーデン","kr":"스웨덴","sp":"Suecia","id":"Swedia","th":"สวีเดน","ar":"السويد","ro":"Suedia","nl":"Zweden","tr":"İsveç","po":"Suécia","it":"Svezia","vi":"Thụy Điển","fa":"سوئد","pls":"Szwecja"},
"MEX": {"en":"Mexico","cn":"墨西哥","zh":"墨西哥","fr":"Mexique","de":"Mexiko","ru":"Мексика","jp":"メキシコ","kr":"멕시코","sp":"México","id":"Meksiko","th":"เม็กซิโก","ar":"المكسيك","ro":"Mexic","nl":"Mexico","tr":"Meksika","po":"México","it":"Messico","vi":"Mexico","fa":"مکزیک","pls":"Meksyk"},
"ECU": {"en":"Ecuador","cn":"厄瓜多尔","zh":"厄瓜多爾","fr":"Équateur","de":"Ecuador","ru":"Эквадор","jp":"エクアドル","kr":"에콰도르","sp":"Ecuador","id":"Ekuador","th":"เอกวาดอร์","ar":"الإكوادور","ro":"Ecuador","nl":"Ecuador","tr":"Ekvador","po":"Equador","it":"Ecuador","vi":"Ecuador","fa":"اکوادور","pls":"Ekwador"},
"ENG": {"en":"England","cn":"英格兰","zh":"英格蘭","fr":"Angleterre","de":"England","ru":"Англия","jp":"イングランド","kr":"잉글랜드","sp":"Inglaterra","id":"Inggris","th":"อังกฤษ","ar":"إنجلترا","ro":"Anglia","nl":"Engeland","tr":"İngiltere","po":"Inglaterra","it":"Inghilterra","vi":"Anh","fa":"انگلیس","pls":"Anglia"},
"COD": {"en":"DR Congo","cn":"刚果金","zh":"剛果金","fr":"RD Congo","de":"DR Kongo","ru":"ДР Конго","jp":"コンゴ民主共和国","kr":"콩고민주공화국","sp":"RD Congo","id":"Kongo","th":"คองโก","ar":"الكونغو الديمقراطية","ro":"RD Congo","nl":"DR Congo","tr":"Demokratik Kongo","po":"RD Congo","it":"RD Congo","vi":"CHDC Congo","fa":"کنگو","pls":"DR Konga"},
"BEL": {"en":"Belgium","cn":"比利时","zh":"比利時","fr":"Belgique","de":"Belgien","ru":"Бельгия","jp":"ベルギー","kr":"벨기에","sp":"Bélgica","id":"Belgia","th":"เบลเยียม","ar":"بلجيكا","ro":"Belgia","nl":"België","tr":"Belçika","po":"Bélgica","it":"Belgio","vi":"Bỉ","fa":"بلژیک","pls":"Belgia"},
"SEN": {"en":"Senegal","cn":"塞内加尔","zh":"塞內加爾","fr":"Sénégal","de":"Senegal","ru":"Сенегал","jp":"セネガル","kr":"세네갈","sp":"Senegal","id":"Senegal","th":"เซเนกัล","ar":"السنغال","ro":"Senegal","nl":"Senegal","tr":"Senegal","po":"Senegal","it":"Senegal","vi":"Senegal","fa":"سنگال","pls":"Senegal"},
"USA": {"en":"USA","cn":"美国","zh":"美國","fr":"États-Unis","de":"USA","ru":"США","jp":"アメリカ","kr":"미국","sp":"Estados Unidos","id":"Amerika Serikat","th":"สหรัฐอเมริกา","ar":"الولايات المتحدة","ro":"SUA","nl":"Verenigde Staten","tr":"ABD","po":"Estados Unidos","it":"Stati Uniti","vi":"Mỹ","fa":"آمریکا","pls":"USA"},
"BIH": {"en":"Bosnia","cn":"波黑","zh":"波赫","fr":"Bosnie","de":"Bosnien","ru":"Босния","jp":"ボスニア","kr":"보스니아","sp":"Bosnia","id":"Bosnia","th":"บอสเนีย","ar":"البوسنة","ro":"Bosnia","nl":"Bosnië","tr":"Bosna Hersek","po":"Bósnia","it":"Bosnia","vi":"Bosnia","fa":"بوسنی","pls":"Bośnia"},
"ESP": {"en":"Spain","cn":"西班牙","zh":"西班牙","fr":"Espagne","de":"Spanien","ru":"Испания","jp":"スペイン","kr":"스페인","sp":"España","id":"Spanyol","th":"สเปน","ar":"إسبانيا","ro":"Spania","nl":"Spanje","tr":"İspanya","po":"Espanha","it":"Spagna","vi":"Tây Ban Nha","fa":"اسپانیا","pls":"Hiszpania"},
"AUT": {"en":"Austria","cn":"奥地利","zh":"奧地利","fr":"Autriche","de":"Österreich","ru":"Австрия","jp":"オーストリア","kr":"오스트리아","sp":"Austria","id":"Austria","th":"ออสเตรีย","ar":"النمسا","ro":"Austria","nl":"Oostenrijk","tr":"Avusturya","po":"Áustria","it":"Austria","vi":"Áo","fa":"اتریش","pls":"Austria"},
"POR": {"en":"Portugal","cn":"葡萄牙","zh":"葡萄牙","fr":"Portugal","de":"Portugal","ru":"Португалия","jp":"ポルトガル","kr":"포르투갈","sp":"Portugal","id":"Portugal","th":"โปรตุเกส","ar":"البرتغال","ro":"Portugalia","nl":"Portugal","tr":"Portekiz","po":"Portugal","it":"Portogallo","vi":"Bồ Đào Nha","fa":"پرتغال","pls":"Portugalia"},
"CRO": {"en":"Croatia","cn":"克罗地亚","zh":"克羅地亞","fr":"Croatie","de":"Kroatien","ru":"Хорватия","jp":"クロアチア","kr":"크로아티아","sp":"Croacia","id":"Kroasia","th":"โครเอเชีย","ar":"كرواتيا","ro":"Croația","nl":"Kroatië","tr":"Hırvatistan","po":"Croácia","it":"Croazia","vi":"Croatia","fa":"کرواسی","pls":"Chorwacja"},
"SUI": {"en":"Switzerland","cn":"瑞士","zh":"瑞士","fr":"Suisse","de":"Schweiz","ru":"Швейцария","jp":"スイス","kr":"스위스","sp":"Suiza","id":"Swiss","th":"สวิตเซอร์แลนด์","ar":"سويسرا","ro":"Elveția","nl":"Zwitserland","tr":"İsviçre","po":"Suíça","it":"Svizzera","vi":"Thụy Sĩ","fa":"سوئیس","pls":"Szwajcaria"},
"ALG": {"en":"Algeria","cn":"阿尔及利亚","zh":"阿爾及利亞","fr":"Algérie","de":"Algerien","ru":"Алжир","jp":"アルジェリア","kr":"알제리","sp":"Argelia","id":"Aljazair","th":"แอลจีเรีย","ar":"الجزائر","ro":"Algeria","nl":"Algerije","tr":"Cezayir","po":"Argélia","it":"Algeria","vi":"Algeria","fa":"الجزایر","pls":"Algieria"},
"AUS": {"en":"Australia","cn":"澳大利亚","zh":"澳大利亞","fr":"Australie","de":"Australien","ru":"Австралия","jp":"オーストラリア","kr":"호주","sp":"Australia","id":"Australia","th":"ออสเตรเลีย","ar":"أستراليا","ro":"Australia","nl":"Australië","tr":"Avustralya","po":"Austrália","it":"Australia","vi":"Úc","fa":"استرالیا","pls":"Australia"},
"EGY": {"en":"Egypt","cn":"埃及","zh":"埃及","fr":"Égypte","de":"Ägypten","ru":"Египет","jp":"エジプト","kr":"이집트","sp":"Egipto","id":"Mesir","th":"อียิปต์","ar":"مصر","ro":"Egipt","nl":"Egypte","tr":"Mısır","po":"Egito","it":"Egitto","vi":"Ai Cập","fa":"مصر","pls":"Egipt"},
"ARG": {"en":"Argentina","cn":"阿根廷","zh":"阿根廷","fr":"Argentine","de":"Argentinien","ru":"Аргентина","jp":"アルゼンチン","kr":"아르헨티나","sp":"Argentina","id":"Argentina","th":"อาร์เจนตินา","ar":"الأرجنتين","ro":"Argentina","nl":"Argentinië","tr":"Arjantin","po":"Argentina","it":"Argentina","vi":"Argentina","fa":"آرژانتین","pls":"Argentyna"},
"CPV": {"en":"Cape Verde","cn":"佛得角","zh":"維德角","fr":"Cap-Vert","de":"Kap Verde","ru":"Кабо-Верде","jp":"カーボベルデ","kr":"카보베르데","sp":"Cabo Verde","id":"Tanjung Verde","th":"เคปเวิร์ด","ar":"الرأس الأخضر","ro":"Capul Verde","nl":"Kaapverdië","tr":"Cape Verde","po":"Cabo Verde","it":"Capo Verde","vi":"Cabo Verde","fa":"کیپ ورد","pls":"Republika Zielonego Przylądka"},
"COL": {"en":"Colombia","cn":"哥伦比亚","zh":"哥倫比亞","fr":"Colombie","de":"Kolumbien","ru":"Колумбия","jp":"コロンビア","kr":"콜롬비아","sp":"Colombia","id":"Kolombia","th":"โคลอมเบีย","ar":"كولومبيا","ro":"Columbia","nl":"Colombia","tr":"Kolombiya","po":"Colômbia","it":"Colombia","vi":"Colombia","fa":"کلمبیا","pls":"Kolumbia"},
"GHA": {"en":"Ghana","cn":"加纳","zh":"迦納","fr":"Ghana","de":"Ghana","ru":"Гана","jp":"ガーナ","kr":"가나","sp":"Ghana","id":"Ghana","th":"กานา","ar":"غانا","ro":"Ghana","nl":"Ghana","tr":"Gana","po":"Gana","it":"Ghana","vi":"Ghana","fa":"غنا","pls":"Ghana"},
}

# 结果句式: {a}=A队 {b}=B队 {score}=比分(可含点球后缀) {w}=胜方
TMPL = {
"en":"{a} {score} {b} — {w} won","cn":"{a} {score} {b}，{w}胜","zh":"{a} {score} {b}，{w}勝",
"fr":"{a} {score} {b} — {w} a gagné","de":"{a} {score} {b} — {w} hat gewonnen","ru":"{a} {score} {b} — победа: {w}",
"jp":"{a} {score} {b}、{w}の勝利","kr":"{a} {score} {b}, {w} 승리","sp":"{a} {score} {b} — ganó {w}",
"id":"{a} {score} {b} — {w} menang","th":"{a} {score} {b} — {w} ชนะ","ar":"{a} {score} {b} — فاز {w}",
"ro":"{a} {score} {b} — {w} a câștigat","nl":"{a} {score} {b} — {w} won","tr":"{a} {score} {b} — {w} kazandı",
"po":"{a} {score} {b} — {w} venceu","it":"{a} {score} {b} — ha vinto {w}","vi":"{a} {score} {b} — {w} thắng",
"fa":"{a} {score} {b} — {w} برنده شد","pls":"{a} {score} {b} — wygrała {w}",
}

# 点球后缀词(出现点球时拼成 "1-1 (点球 4-3)")
PEN = {
"en":"pens","cn":"点球","zh":"點球","fr":"t.a.b.","de":"i.E.","ru":"пен.","jp":"PK","kr":"승부차기","sp":"pen.",
"id":"adu penalti","th":"จุดโทษ","ar":"ركلات الترجيح","ro":"pen.","nl":"strafschoppen","tr":"pen.","po":"pênaltis",
"it":"rig.","vi":"luân lưu","fa":"پنالتی","pls":"karne",
}

def team_name(code, lang):
    return TEAM.get(code, {}).get(lang, code)

def result_line(a, b, win, score, pens, lang):
    """返回该语言的「A 比分 B，W 胜」单行文本(含点球后缀)。"""
    ta = team_name(a, lang); tb = team_name(b, lang); tw = team_name(win, lang)
    sd = score if not pens else f"{score} ({PEN.get(lang,'pens')} {pens})"
    return TMPL.get(lang, "{a} {score} {b} — {w} won").format(a=ta, b=tb, w=tw, score=sd)
