import json, subprocess, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding="utf-8")

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"

def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    return Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

# 18 languages: cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns
translations = [
    # cn
    '1.活动中使用一定数量<color=#ffa200>惊喜锤</color>即可敲击金字塔当前层，不放回随机抽取当前层的奖励\\n2.每层最左侧道具为升层道具，抽中后下次可抽取上一层道具\\n3.每层最右侧道具为降层道具，抽中后下次将抽取下一层道具\\n4.已抽中的道具不再出现，升层和降层道具将自动顺延至剩余道具的最左侧和最右侧\\n5.集齐4个阶段奖励道具后，将自动获得阶段奖励\\n6.抽奖道具消耗随层数递增\\n7.活动结束后，未使用的惊喜锤将被回收为15分钟加速',
    # en
    '1.Spend <color=#ffa200>Lucky Hammers</color> to strike the current Pyramid tier and randomly draw a reward without replacement.\\n2.The leftmost item on each tier is a Tier-Up item. Drawing it lets you access the tier above next time.\\n3.The rightmost item on each tier is a Tier-Down item. Drawing it moves you to the tier below next time.\\n4.Drawn items will not appear again. Tier-Up and Tier-Down items automatically shift to the leftmost and rightmost remaining items.\\n5.Collect 4 Stage Reward items to automatically claim the Stage Reward.\\n6.Draw item cost increases with each tier.\\n7.When the event ends, unused Lucky Hammers convert into 15-minute Speedups.',
    # fr
    "1.D\u00e9pensez des <color=#ffa200>Marteaux Chanceux</color> pour frapper l'\u00e9tage actuel de la Pyramide et tirer al\u00e9atoirement une r\u00e9compense sans remise.\\n2.L'objet le plus \u00e0 gauche de chaque \u00e9tage est un objet de Mont\u00e9e. Le tirer vous permet d'acc\u00e9der \u00e0 l'\u00e9tage sup\u00e9rieur.\\n3.L'objet le plus \u00e0 droite de chaque \u00e9tage est un objet de Descente. Le tirer vous ram\u00e8ne \u00e0 l'\u00e9tage inf\u00e9rieur.\\n4.Les objets tir\u00e9s n'apparaissent plus. Les objets de Mont\u00e9e et Descente se d\u00e9calent automatiquement vers les extr\u00e9mit\u00e9s restantes.\\n5.Collectez 4 objets de R\u00e9compense d'\u00c9tape pour obtenir automatiquement la R\u00e9compense d'\u00c9tape.\\n6.Le co\u00fbt des objets de tirage augmente avec chaque \u00e9tage.\\n7.\u00c0 la fin de l'\u00e9v\u00e9nement, les Marteaux Chanceux inutilis\u00e9s sont convertis en Acc\u00e9l\u00e9rations de 15 min.",
    # de
    '1.Setze <color=#ffa200>Gl\u00fccksh\u00e4mmer</color> ein, um die aktuelle Pyramidenstufe zu schlagen und zuf\u00e4llig eine Belohnung ohne Zur\u00fccklegen zu ziehen.\\n2.Der Gegenstand ganz links auf jeder Stufe ist ein Aufstiegs-Gegenstand. Ihn zu ziehen erm\u00f6glicht den Zugang zur n\u00e4chsth\u00f6heren Stufe.\\n3.Der Gegenstand ganz rechts auf jeder Stufe ist ein Abstiegs-Gegenstand. Ihn zu ziehen f\u00fchrt zur n\u00e4chstniedrigeren Stufe.\\n4.Gezogene Gegenst\u00e4nde erscheinen nicht mehr. Aufstiegs- und Abstiegs-Gegenst\u00e4nde verschieben sich automatisch zu den \u00e4u\u00dfersten verbleibenden Positionen.\\n5.Sammle 4 Stufen-Belohnungs-Gegenst\u00e4nde, um die Stufen-Belohnung automatisch zu erhalten.\\n6.Die Kosten f\u00fcr Zieh-Gegenst\u00e4nde steigen mit jeder Stufe.\\n7.Nach dem Event werden unbenutzte Gl\u00fccksh\u00e4mmer in 15-Min-Beschleunigungen umgewandelt.',
    # po
    '1.Gaste <color=#ffa200>Martelos da Sorte</color> para golpear o andar atual da Pir\u00e2mide e sortear aleatoriamente uma recompensa sem reposi\u00e7\u00e3o.\\n2.O item mais \u00e0 esquerda de cada andar \u00e9 um item de Subida. Sort\u00e1-lo permite acessar o andar acima.\\n3.O item mais \u00e0 direita de cada andar \u00e9 um item de Descida. Sort\u00e1-lo leva ao andar abaixo.\\n4.Itens sorteados n\u00e3o aparecem novamente. Itens de Subida e Descida mudam automaticamente para as extremidades restantes.\\n5.Colete 4 itens de Recompensa de Etapa para receber automaticamente a Recompensa de Etapa.\\n6.O custo dos itens de sorteio aumenta a cada andar.\\n7.Quando o evento terminar, Martelos da Sorte n\u00e3o utilizados ser\u00e3o convertidos em Acelera\u00e7\u00f5es de 15 min.',
    # zh (繁體)
    '1.活動中使用一定數量<color=#ffa200>驚喜錘</color>即可敲擊金字塔當前層，不放回隨機抽取當前層的獎勵\\n2.每層最左側道具為升層道具，抽中後下次可抽取上一層道具\\n3.每層最右側道具為降層道具，抽中後下次將抽取下一層道具\\n4.已抽中的道具不再出現，升層和降層道具將自動順延至剩餘道具的最左側和最右側\\n5.集齊4個階段獎勵道具後，將自動獲得階段獎勵\\n6.抽獎道具消耗隨層數遞增\\n7.活動結束後，未使用的驚喜錘將被回收為15分鐘加速',
    # id
    '1.Gunakan <color=#ffa200>Palu Keberuntungan</color> untuk memukul tingkat Piramida saat ini dan secara acak menarik hadiah tanpa pengembalian.\\n2.Item paling kiri di setiap tingkat adalah item Naik Tingkat. Menariknya memungkinkan akses ke tingkat di atasnya.\\n3.Item paling kanan di setiap tingkat adalah item Turun Tingkat. Menariknya membawa Anda ke tingkat di bawahnya.\\n4.Item yang sudah ditarik tidak akan muncul lagi. Item Naik dan Turun Tingkat otomatis bergeser ke posisi terluar yang tersisa.\\n5.Kumpulkan 4 item Hadiah Tahap untuk otomatis mendapatkan Hadiah Tahap.\\n6.Biaya item undian meningkat seiring tingkat.\\n7.Saat event berakhir, Palu Keberuntungan yang tidak digunakan dikonversi menjadi Percepatan 15 menit.',
    # th
    '1.ใช้<color=#ffa200>ค้อนเซอร์ไพรส์</color>เพื่อตีชั้นปัจจุบันของพีระมิดและสุ่มจับรางวัลแบบไม่คืนกลับ\\n2.ไอเทมซ้ายสุดของแต่ละชั้นเป็นไอเทมเลื่อนชั้นขึ้น จับได้แล้วครั้งถัดไปจะจับจากชั้นบน\\n3.ไอเทมขวาสุดของแต่ละชั้นเป็นไอเทมเลื่อนชั้นลง จับได้แล้วครั้งถัดไปจะจับจากชั้นล่าง\\n4.ไอเทมที่จับแล้วจะไม่ปรากฏอีก ไอเทมเลื่อนขึ้นและลงจะเลื่อนไปยังตำแหน่งซ้ายสุดและขวาสุดที่เหลืออัตโนมัติ\\n5.สะสมไอเทมรางวัลขั้นตอนครบ 4 ชิ้นจะได้รับรางวัลขั้นตอนอัตโนมัติ\\n6.ต้นทุนไอเทมจับฉลากเพิ่มขึ้นตามชั้น\\n7.เมื่อกิจกรรมสิ้นสุด ค้อนเซอร์ไพรส์ที่ไม่ได้ใช้จะถูกแปลงเป็นเร่งความเร็ว 15 นาที',
    # sp
    '1.Gasta <color=#ffa200>Martillos de la Suerte</color> para golpear el piso actual de la Pir\u00e1mide y obtener aleatoriamente una recompensa sin reemplazo.\\n2.El objeto m\u00e1s a la izquierda de cada piso es un objeto de Ascenso. Obtenerlo permite acceder al piso superior.\\n3.El objeto m\u00e1s a la derecha de cada piso es un objeto de Descenso. Obtenerlo te lleva al piso inferior.\\n4.Los objetos obtenidos no vuelven a aparecer. Los objetos de Ascenso y Descenso se desplazan autom\u00e1ticamente a los extremos restantes.\\n5.Re\u00fane 4 objetos de Recompensa de Etapa para recibir autom\u00e1ticamente la Recompensa de Etapa.\\n6.El coste de los objetos de sorteo aumenta con cada piso.\\n7.Al finalizar el evento, los Martillos de la Suerte no utilizados se convierten en Aceleraciones de 15 min.',
    # ru
    '1.Тратьте <color=#ffa200>Молоты удачи</color>, чтобы ударить по текущему ярусу Пирамиды и случайно вытянуть награду без возврата.\\n2.Самый левый предмет на каждом ярусе — предмет повышения яруса. Вытянув его, вы получите доступ к ярусу выше.\\n3.Самый правый предмет — предмет понижения яруса. Вытянув его, вы перейдёте на ярус ниже.\\n4.Вытянутые предметы больше не появляются. Предметы повышения и понижения автоматически сдвигаются к крайним оставшимся позициям.\\n5.Соберите 4 предмета этапной награды, чтобы автоматически получить этапную награду.\\n6.Стоимость предметов розыгрыша увеличивается с каждым ярусом.\\n7.По окончании события неиспользованные Молоты удачи конвертируются в 15-мин ускорения.',
    # tr
    '1.<color=#ffa200>Şans Çekiçleri</color> harcayarak Piramidin mevcut katını vurun ve iade olmadan rastgele bir ödül çekin.\\n2.Her katın en solundaki eşya bir Kat Yükseltme eşyasıdır. Çekildiğinde bir üst kata erişim sağlar.\\n3.Her katın en sağındaki eşya bir Kat Düşürme eşyasıdır. Çekildiğinde bir alt kata inersiniz.\\n4.Çekilen eşyalar tekrar görünmez. Yükseltme ve Düşürme eşyaları otomatik olarak kalan en uç pozisyonlara kayar.\\n5.4 Aşama Ödülü eşyası toplayarak Aşama Ödülünü otomatik olarak alın.\\n6.Çekiliş eşyası maliyeti her katla artar.\\n7.Etkinlik sona erdiğinde kullanılmayan Şans Çekiçleri 15 dk Hızlandırıcılara dönüştürülür.',
    # vi
    '1.Sử dụng <color=#ffa200>Búa May Mắn</color> để đập tầng hiện tại của Kim Tự Tháp và rút ngẫu nhiên phần thưởng không hoàn lại.\\n2.Vật phẩm ngoài cùng bên trái mỗi tầng là vật phẩm Lên Tầng. Rút được sẽ cho phép truy cập tầng trên.\\n3.Vật phẩm ngoài cùng bên phải mỗi tầng là vật phẩm Xuống Tầng. Rút được sẽ đưa bạn xuống tầng dưới.\\n4.Vật phẩm đã rút sẽ không xuất hiện lại. Vật phẩm Lên và Xuống Tầng tự động dịch chuyển đến các vị trí ngoài cùng còn lại.\\n5.Thu thập đủ 4 vật phẩm Phần Thưởng Giai Đoạn để tự động nhận Phần Thưởng Giai Đoạn.\\n6.Chi phí vật phẩm rút tăng theo từng tầng.\\n7.Khi sự kiện kết thúc, Búa May Mắn chưa dùng sẽ được chuyển thành Tăng Tốc 15 phút.',
    # it
    "1.Spendi <color=#ffa200>Martelli Fortunati</color> per colpire il livello attuale della Piramide ed estrarre casualmente una ricompensa senza reinserimento.\\n2.L'oggetto più a sinistra di ogni livello è un oggetto Salita. Estrarlo permette di accedere al livello superiore.\\n3.L'oggetto più a destra di ogni livello è un oggetto Discesa. Estrarlo porta al livello inferiore.\\n4.Gli oggetti estratti non riappaiono. Gli oggetti Salita e Discesa si spostano automaticamente alle estremità rimanenti.\\n5.Raccogli 4 oggetti Ricompensa di Tappa per ottenere automaticamente la Ricompensa di Tappa.\\n6.Il costo degli oggetti di estrazione aumenta con ogni livello.\\n7.Al termine dell'evento, i Martelli Fortunati non utilizzati vengono convertiti in Accelerazioni da 15 min.",
    # pl
    '1.Wydaj <color=#ffa200>Szczęśliwe Młotki</color>, aby uderzyć w bieżące piętro Piramidy i losowo wyciągnąć nagrodę bez zwrotu.\\n2.Przedmiot najbardziej na lewo na każdym piętrze to przedmiot Awansu. Wyciągnięcie go umożliwia dostęp do wyższego piętra.\\n3.Przedmiot najbardziej na prawo to przedmiot Degradacji. Wyciągnięcie go przenosi na niższe piętro.\\n4.Wyciągnięte przedmioty nie pojawiają się ponownie. Przedmioty Awansu i Degradacji automatycznie przesuwają się na skrajne pozostałe pozycje.\\n5.Zbierz 4 przedmioty Nagrody Etapowej, aby automatycznie otrzymać Nagrodę Etapową.\\n6.Koszt przedmiotów losowania rośnie z każdym piętrem.\\n7.Po zakończeniu wydarzenia niewykorzystane Szczęśliwe Młotki zostaną zamienione na Przyspieszenia 15 min.',
    # ar
    '1.أنفق <color=#ffa200>مطارق الحظ</color> لضرب الطابق الحالي من الهرم وسحب مكافأة عشوائية بدون إعادة.\\n2.العنصر الأيسر في كل طابق هو عنصر صعود. سحبه يتيح الوصول إلى الطابق الأعلى.\\n3.العنصر الأيمن في كل طابق هو عنصر هبوط. سحبه ينقلك إلى الطابق الأدنى.\\n4.العناصر المسحوبة لا تظهر مجدداً. عناصر الصعود والهبوط تنتقل تلقائياً إلى أقصى المواقع المتبقية.\\n5.اجمع 4 عناصر مكافأة المرحلة للحصول تلقائياً على مكافأة المرحلة.\\n6.تكلفة عناصر السحب تزداد مع كل طابق.\\n7.عند انتهاء الحدث، يتم تحويل مطارق الحظ غير المستخدمة إلى تسريعات 15 دقيقة.',
    # jp
    '1.<color=#ffa200>ラッキーハンマー</color>を使ってピラミッドの現在の階層を叩き、補充なしでランダムに報酬を引きます。\\n2.各階層の最も左のアイテムは階層アップアイテムです。引くと次回は上の階層からアイテムを引けます。\\n3.各階層の最も右のアイテムは階層ダウンアイテムです。引くと次回は下の階層に移動します。\\n4.引いたアイテムは再出現しません。階層アップ・ダウンアイテムは残りのアイテムの最も左と右に自動的にシフトします。\\n5.ステージ報酬アイテムを4つ集めると、自動的にステージ報酬を獲得します。\\n6.抽選アイテムのコストは階層ごとに増加します。\\n7.イベント終了後、未使用のラッキーハンマーは15分加速に変換されます。',
    # kr
    '1.<color=#ffa200>행운의 망치</color>를 사용하여 피라미드의 현재 층을 치고 비복원 방식으로 무작위 보상을 뽑습니다.\\n2.각 층의 가장 왼쪽 아이템은 층 상승 아이템입니다. 뽑으면 다음에 윗층 아이템을 뽑을 수 있습니다.\\n3.각 층의 가장 오른쪽 아이템은 층 하강 아이템입니다. 뽑으면 다음에 아랫층으로 이동합니다.\\n4.뽑힌 아이템은 다시 나타나지 않습니다. 상승 및 하강 아이템은 남은 아이템의 양 끝으로 자동 이동합니다.\\n5.단계 보상 아이템 4개를 모으면 자동으로 단계 보상을 획득합니다.\\n6.뽑기 아이템 비용은 층이 올라갈수록 증가합니다.\\n7.이벤트 종료 시 미사용 행운의 망치는 15분 가속으로 전환됩니다.',
    # cns = cn
    '1.活动中使用一定数量<color=#ffa200>惊喜锤</color>即可敲击金字塔当前层，不放回随机抽取当前层的奖励\\n2.每层最左侧道具为升层道具，抽中后下次可抽取上一层道具\\n3.每层最右侧道具为降层道具，抽中后下次将抽取下一层道具\\n4.已抽中的道具不再出现，升层和降层道具将自动顺延至剩余道具的最左侧和最右侧\\n5.集齐4个阶段奖励道具后，将自动获得阶段奖励\\n6.抽奖道具消耗随层数递增\\n7.活动结束后，未使用的惊喜锤将被回收为15分钟加速',
]

def main():
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    # Direct update EVENT row 4996, columns C~T (18 languages)
    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="'EVENT'!C4996:T4996",
        valueInputOption="RAW",
        body={"values": [translations]},
    ).execute()

    print("✅ mecha_gacha_rule updated: EVENT row 4996")

    # Verify
    r = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'EVENT'!B4996:D4996"
    ).execute()
    row = r.get("values", [[]])[0]
    print(f"   Key: {row[0]}")
    print(f"   cn (first 60): {row[1][:60]}...")
    print(f"   en (first 60): {row[2][:60]}...")
    print("Done!")

if __name__ == "__main__":
    main()
