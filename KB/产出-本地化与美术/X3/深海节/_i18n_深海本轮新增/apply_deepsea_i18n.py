# -*- coding: utf-8 -*-
"""深海节本轮新增key 全16语言翻译·作用于备份表(解BUG后同步live)。
Text tsv列(0-idx): 0key 1状态 2cn备份 3cn 4en 5sp 6fr 7id 8de 9kr 10zh繁 11ru 12ua 13jp 14it 15pl 16po 17tr 18th
用法: python apply_deepsea_i18n.py <目标Text__Text.tsv>  (默认备份副本)"""
import csv, io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# cn -> [en,sp,fr,id,de,kr,zh繁,ru,ua,jp,it,pl,po,tr,th]  (15项·对col4..18)
CN2LANG = {
 "远航之歌": ["Song of the Voyage","Canto de la Travesía","Chant du Voyage","Lagu Pelayaran","Lied der Reise","항해의 노래","遠航之歌","Песнь странствия","Пісня мандрів","航海の歌","Canto del Viaggio","Pieśń Wyprawy","Canção da Viagem","Yolculuğun Şarkısı","บทเพลงแห่งการเดินเรือ"],
 "远航之歌（纪念卡）": ["Song of the Voyage (Commemorative Card)","Canto de la Travesía (Carta conmemorativa)","Chant du Voyage (Carte commémorative)","Lagu Pelayaran (Kartu Peringatan)","Lied der Reise (Gedenkkarte)","항해의 노래 (기념 카드)","遠航之歌（紀念卡）","Песнь странствия (памятная карта)","Пісня мандрів (пам'ятна картка)","航海の歌（記念カード）","Canto del Viaggio (Carta commemorativa)","Pieśń Wyprawy (Karta pamiątkowa)","Canção da Viagem (Carta comemorativa)","Yolculuğun Şarkısı (Anı Kartı)","บทเพลงแห่งการเดินเรือ (การ์ดที่ระลึก)"],
 "循着海风与星光，她驶过万顷深蓝——海渊尽头的珍藏，只属于无畏的远航者。": ["Following sea breeze and starlight, she sails the boundless blue - the treasure at the end of the abyss belongs only to the fearless voyager.","Siguiendo la brisa marina y la luz de las estrellas, surca el azul sin fin: el tesoro del fondo del abismo solo pertenece al viajero intrépido.","Suivant la brise marine et la lumière des étoiles, elle vogue sur le bleu infini : le trésor au fond de l'abîme n'appartient qu'au voyageur intrépide.","Mengikuti angin laut dan cahaya bintang, ia mengarungi biru tak berbatas - harta di dasar jurang hanya milik pelaut tak gentar.","Dem Meereswind und Sternenlicht folgend segelt sie ins grenzenlose Blau - der Schatz am Grund des Abgrunds gehört nur dem furchtlosen Reisenden.","바닷바람과 별빛을 따라 그녀는 끝없는 푸름을 항해한다 - 심연 끝의 보물은 두려움 없는 항해자만의 것이다.","循著海風與星光，她駛過萬頃深藍——海淵盡頭的珍藏，只屬於無畏的遠航者。","Следуя за морским бризом и светом звёзд, она плывёт сквозь бескрайнюю синь — сокровище на дне бездны принадлежит лишь бесстрашному страннику.","Слідуючи за морським бризом і сяйвом зірок, вона пливе крізь безмежну синь — скарб на дні безодні належить лише безстрашному мандрівнику.","潮風と星明かりを辿り、彼女は果てなき青を渡る——深淵の底の秘宝は、恐れを知らぬ航海者だけのもの。","Seguendo la brezza marina e la luce delle stelle, solca l'azzurro infinito: il tesoro in fondo all'abisso appartiene solo al viaggiatore impavido.","Podążając za morską bryzą i światłem gwiazd, żegluje przez bezkresny błękit - skarb na dnie otchłani należy tylko do nieustraszonego podróżnika.","Seguindo a brisa do mar e a luz das estrelas, ela navega pelo azul infinito - o tesouro no fundo do abismo pertence apenas ao viajante destemido.","Deniz meltemi ve yıldız ışığını izleyerek uçsuz bucaksız maviyi aşar - uçurumun dibindeki hazine yalnızca korkusuz yolcuya aittir.","ตามสายลมทะเลและแสงดาว นางแล่นผ่านท้องทะเลสีครามไร้ขอบเขต ขุมทรัพย์ ณ ก้นเหวลึกเป็นของนักเดินเรือผู้กล้าหาญเท่านั้น"],
 "深海节活动获取": ["Obtained from the Deep Sea Festival event.","Se obtiene en el evento del Festival de las Profundidades.","Obtenu lors de l'événement du Festival des Abysses.","Didapat dari event Festival Laut Dalam.","Erhältlich im Tiefsee-Fest-Event.","심해 축제 이벤트에서 획득.","深海節活動獲取。","Можно получить на событии «Фестиваль глубин».","Можна отримати на події «Фестиваль глибин».","深海フェス イベントで入手。","Ottenuto dall'evento Festival degli Abissi.","Zdobywane podczas wydarzenia Festiwal Głębin.","Obtido no evento Festival do Mar Profundo.","Derin Deniz Festivali etkinliğinden elde edilir.","รับได้จากกิจกรรมเทศกาลทะเลลึก"],
 "航者徽记（头衔）": ["Voyager's Crest (Title)","Emblema del Viajero (Título)","Emblème du Voyageur (Titre)","Lambang Pelaut (Gelar)","Wappen des Reisenden (Titel)","항해자의 문장 (칭호)","航者徽記（頭銜）","Герб странника (титул)","Герб мандрівника (титул)","航海者の紋章（称号）","Stemma del Viaggiatore (Titolo)","Herb Podróżnika (Tytuł)","Brasão do Viajante (Título)","Yolcunun Arması (Unvan)","ตราสัญลักษณ์นักเดินเรือ (ฉายา)"],
 "使用后可获得传说级头衔。深海罗盘排行榜顶端荣耀，航向深渊之巅。": ["Use to obtain a legendary title. The pinnacle glory of the Deep Sea Compass leaderboard - sail to the apex of the abyss.","Úsalo para obtener un título legendario. La gloria suprema de la clasificación de la Brújula Abisal: navega hacia la cima del abismo.","À utiliser pour obtenir un titre légendaire. La gloire suprême du classement de la Boussole des Abysses : voguez vers le sommet de l'abîme.","Gunakan untuk memperoleh gelar legendaris. Kejayaan puncak peringkat Kompas Laut Dalam - berlayarlah ke puncak jurang.","Verwenden, um einen legendären Titel zu erhalten. Der höchste Ruhm der Tiefsee-Kompass-Rangliste - segle zum Gipfel des Abgrunds.","사용 시 전설 등급 칭호를 획득합니다. 심해 나침반 순위표 정상의 영광, 심연의 정점을 향해 항해하라.","使用後可獲得傳說級頭銜。深海羅盤排行榜頂端榮耀，航向深淵之巔。","Используйте, чтобы получить легендарный титул. Высшая слава рейтинга «Компас глубин» — плывите к вершине бездны.","Використайте, щоб отримати легендарний титул. Найвища слава рейтингу «Компас глибин» — пливіть до вершини безодні.","使用すると伝説級の称号を獲得。深海コンパス ランキング頂点の栄光、深淵の頂へ。","Usa per ottenere un titolo leggendario. La gloria suprema della classifica Bussola degli Abissi: naviga verso l'apice dell'abisso.","Użyj, aby zdobyć legendarny tytuł. Najwyższa chwała rankingu Kompasu Głębin - żegluj ku szczytowi otchłani.","Use para obter um título lendário. A glória suprema do ranking da Bússola do Abismo - navegue ao ápice do abismo.","Efsanevi bir unvan elde etmek için kullan. Derin Deniz Pusulası sıralamasının zirve şanı - uçurumun zirvesine yelken aç.","ใช้เพื่อรับฉายาระดับตำนาน เกียรติยศสูงสุดของกระดานจัดอันดับเข็มทิศทะเลลึก จงแล่นสู่จุดสูงสุดของห้วงเหว"],
 "深海罗盘排行榜顶端获取": ["Obtained from the top of the Deep Sea Compass leaderboard.","Se obtiene en la cima de la clasificación de la Brújula Abisal.","Obtenu au sommet du classement de la Boussole des Abysses.","Didapat dari puncak peringkat Kompas Laut Dalam.","Erhältlich an der Spitze der Tiefsee-Kompass-Rangliste.","심해 나침반 순위표 정상에서 획득.","深海羅盤排行榜頂端獲取。","Можно получить на вершине рейтинга «Компас глубин».","Можна отримати на вершині рейтингу «Компас глибин».","深海コンパス ランキング頂点で入手。","Ottenuto in cima alla classifica Bussola degli Abissi.","Zdobywane na szczycie rankingu Kompasu Głębin.","Obtido no topo do ranking da Bússola do Abismo.","Derin Deniz Pusulası sıralamasının zirvesinden elde edilir.","รับได้จากอันดับสูงสุดของกระดานจัดอันดับเข็มทิศทะเลลึก"],
 "深海累充": ["Deep Sea Cumulative Recharge","Recarga Acumulada Abisal","Recharge Cumulée des Abysses","Isi Ulang Kumulatif Laut Dalam","Kumulative Tiefsee-Aufladung","심해 누적 충전","深海累充","Накопительное пополнение глубин","Накопичувальне поповнення глибин","深海累計チャージ","Ricarica Cumulativa Abissi","Skumulowane Doładowanie Głębin","Recarga Acumulada do Abismo","Derin Deniz Toplam Yükleme","เติมเงินสะสมทะเลลึก"],
 "累计充值领取深海珍稀奖励！": ["Recharge cumulatively to claim rare Deep Sea rewards!","¡Recarga acumulada para reclamar recompensas raras de las profundidades!","Rechargez de façon cumulée pour réclamer de rares récompenses des abysses !","Isi ulang secara kumulatif untuk klaim hadiah langka Laut Dalam!","Lade kumulativ auf und sichere dir seltene Tiefsee-Belohnungen!","누적 충전하여 희귀한 심해 보상을 받으세요!","累計充值領取深海珍稀獎勵！","Пополняйте накопительно и получайте редкие награды глубин!","Поповнюйте накопичувально й отримуйте рідкісні нагороди глибин!","累計チャージで深海の希少報酬を獲得！","Ricarica in modo cumulativo per ottenere rare ricompense degli abissi!","Doładowuj skumulowanie, by zdobyć rzadkie nagrody głębin!","Recarregue acumulando para resgatar recompensas raras do abismo!","Toplam yükleme yaparak nadir Derin Deniz ödüllerini al!","เติมเงินสะสมเพื่อรับรางวัลหายากแห่งทะเลลึก!"],
 "远航日志": ["Voyage Log","Diario de Travesía","Journal de Voyage","Catatan Pelayaran","Reisetagebuch","항해 일지","遠航日誌","Журнал странствий","Журнал мандрів","航海日誌","Diario di Viaggio","Dziennik Wyprawy","Diário de Viagem","Yolculuk Günlüğü","บันทึกการเดินเรือ"],
 "航行积分解锁深海远航日志奖励！": ["Earn voyage points to unlock Deep Sea Voyage Log rewards!","¡Gana puntos de travesía para desbloquear las recompensas del Diario de Travesía!","Gagnez des points de voyage pour débloquer les récompenses du Journal de Voyage des Abysses !","Kumpulkan poin pelayaran untuk membuka hadiah Catatan Pelayaran Laut Dalam!","Sammle Reisepunkte, um die Belohnungen des Tiefsee-Reisetagebuchs freizuschalten!","항해 점수를 모아 심해 항해 일지 보상을 잠금 해제하세요!","累積航行積分解鎖深海遠航日誌獎勵！","Зарабатывайте очки странствий, чтобы открыть награды журнала глубин!","Заробляйте очки мандрів, щоб відкрити нагороди журналу глибин!","航海ポイントを貯めて深海航海日誌の報酬を解放！","Guadagna punti viaggio per sbloccare le ricompense del Diario di Viaggio degli Abissi!","Zdobywaj punkty wyprawy, aby odblokować nagrody Dziennika Głębin!","Ganhe pontos de viagem para desbloquear recompensas do Diário de Viagem do Abismo!","Yolculuk puanı kazanarak Derin Deniz Yolculuk Günlüğü ödüllerini aç!","สะสมแต้มเดินเรือเพื่อปลดล็อกรางวัลบันทึกการเดินเรือทะเลลึก!"],
 "深海之冠": ["Crown of the Deep","Corona del Abismo","Couronne des Abysses","Mahkota Laut Dalam","Krone der Tiefsee","심해의 왕관","深海之冠","Корона глубин","Корона глибин","深海の冠","Corona degli Abissi","Korona Głębin","Coroa do Abismo","Derinliğin Tacı","มงกุฎแห่งทะเลลึก"],
 "深海之冠（头像框）": ["Crown of the Deep (Avatar Frame)","Corona del Abismo (Marco de avatar)","Couronne des Abysses (Cadre d'avatar)","Mahkota Laut Dalam (Bingkai Avatar)","Krone der Tiefsee (Avatar-Rahmen)","심해의 왕관 (아바타 프레임)","深海之冠（頭像框）","Корона глубин (рамка аватара)","Корона глибин (рамка аватара)","深海の冠（アバター枠）","Corona degli Abissi (Cornice avatar)","Korona Głębin (Ramka awatara)","Coroa do Abismo (Moldura de avatar)","Derinliğin Tacı (Avatar Çerçevesi)","มงกุฎแห่งทะเลลึก (กรอบอวาตาร์)"],
 "使用后获得深海之冠头像框，彰显远航者荣光。": ["Use to obtain the Crown of the Deep avatar frame and show the glory of a voyager.","Úsalo para obtener el marco de avatar Corona del Abismo y exhibir la gloria de un viajero.","À utiliser pour obtenir le cadre d'avatar Couronne des Abysses et afficher la gloire d'un voyageur.","Gunakan untuk memperoleh bingkai avatar Mahkota Laut Dalam dan tunjukkan kejayaan seorang pelaut.","Verwenden, um den Avatar-Rahmen Krone der Tiefsee zu erhalten und den Ruhm eines Reisenden zu zeigen.","사용하여 심해의 왕관 아바타 프레임을 획득하고 항해자의 영광을 드러내세요.","使用後獲得深海之冠頭像框，彰顯遠航者榮光。","Используйте, чтобы получить рамку аватара «Корона глубин» и показать славу странника.","Використайте, щоб отримати рамку аватара «Корона глибин» і показати славу мандрівника.","使用すると深海の冠アバター枠を獲得し、航海者の栄光を示せます。","Usa per ottenere la cornice avatar Corona degli Abissi e mostrare la gloria di un viaggiatore.","Użyj, aby zdobyć ramkę awatara Korona Głębin i ukazać chwałę podróżnika.","Use para obter a moldura de avatar Coroa do Abismo e exibir a glória de um viajante.","Derinliğin Tacı avatar çerçevesini elde etmek ve bir yolcunun şanını göstermek için kullan.","ใช้เพื่อรับกรอบอวาตาร์มงกุฎแห่งทะเลลึก และแสดงเกียรติของนักเดินเรือ"],
}

# 我的key -> cn (定位用)
KEY2CN = {
 "TXT_MemorialCard_Name_80":"远航之歌",
 "TXT_MemorialCard_Desc_80":"循着海风与星光，她驶过万顷深蓝——海渊尽头的珍藏，只属于无畏的远航者。",
 "TXT_MemorialCard_GetTips_80":"深海节活动获取","TXT_MemorialCard_GetMoreTips_80":"深海节活动获取",
 "TXT_Item_Name_180080":"远航之歌（纪念卡）",
 "TXT_Item_Desc_180080":"循着海风与星光，她驶过万顷深蓝——海渊尽头的珍藏，只属于无畏的远航者。",
 "TXT_Item_ObtainTips_180080":"深海节活动获取",
 "TXT_Item_Name_82005":"航者徽记（头衔）",
 "TXT_Item_Desc_82005":"使用后可获得传说级头衔。深海罗盘排行榜顶端荣耀，航向深渊之巅。",
 "TXT_Item_ObtainTips_82005":"深海罗盘排行榜顶端获取",
 "TXT_ActvOnline_ActvName_100598":"深海累充","TXT_ActvOnline_ActvDesc_100598":"累计充值领取深海珍稀奖励！",
 "TXT_ActvOnline_ActvName_102244":"远航日志","TXT_ActvOnline_ActvDesc_102244":"航行积分解锁深海远航日志奖励！",
 "TXT_PersonalizeAvatarFrameCfg_Name_10080":"深海之冠","TXT_PersonalizeAvatarFrameCfg_SourceDesc_10080":"深海节活动获取",
 "TXT_Item_Name_80100":"深海之冠（头像框）",
 "TXT_Item_Desc_80100":"使用后获得深海之冠头像框，彰显远航者荣光。",
 "TXT_Item_ObtainTips_80100":"深海节活动获取",
 "TXT_Pack_Name_211019":"深海之冠（头像框）",  # Pack名 暂用框名(可改"深海头像框礼包")
 "TXT_Pack_Desc_211019":"集齐深海之冠头像框，彰显远航者的荣光。",
}
# Pack名/描述 单独译(跟框名略不同)
CN2LANG["集齐深海之冠头像框，彰显远航者的荣光。"]=CN2LANG["使用后获得深海之冠头像框，彰显远航者荣光。"]

def main(path):
    raw=open(path,encoding='utf-8').read(); trail=raw.endswith('\n')
    rows=list(csv.reader(io.StringIO(raw),delimiter='\t'))
    while rows and rows[-1]==['']: rows.pop()
    idx={r[0]:i for i,r in enumerate(rows) if r}
    filled=0; miss=[]
    for key,cn in KEY2CN.items():
        if key not in idx: miss.append(key); continue
        if cn not in CN2LANG: miss.append('NO_TRANS:'+key); continue
        r=rows[idx[key]]
        while len(r)<27: r.append('')
        r[3]=cn                       # cn母版
        for off,val in enumerate(CN2LANG[cn]):  # col4..18 = en..th
            r[4+off]=val
        r[1]='AI'                     # 状态
        rows[idx[key]]=r; filled+=1
    buf=io.StringIO(); csv.writer(buf,delimiter='\t',lineterminator='\n').writerows(rows)
    out=buf.getvalue()
    if not trail and out.endswith('\n'): out=out[:-1]
    open(path,'w',encoding='utf-8',newline='').write(out)
    print('填了%d个key'%filled)
    if miss: print('缺/无译:',miss)
    # 审计: 我的key有无空/cn泄漏(en列==cn)
    bad=[]
    for key in KEY2CN:
        if key in idx:
            r=rows[idx[key]]
            for c in range(4,19):
                if c<len(r) and (r[c]=='' or (r[c]==r[3] and c not in(10,))): bad.append('%s col%d'%(key,c))
    print('审计 空/泄漏:', bad if bad else '无 ✓(zh繁col10=cn属正常·简繁这里按繁译已填)')

if __name__=='__main__':
    p=sys.argv[1] if len(sys.argv)>1 else r"C:\Users\linkang\AppData\Local\Temp\claude\C--Users-linkang\f62aaf0b-2522-4962-afda-ba39e6e04fd1\scratchpad\Text__Text.BACKUP.tsv"
    main(p)
