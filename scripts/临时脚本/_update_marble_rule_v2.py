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
    '1.玩家消耗抽奖道具，发射弹珠抽奖即可获取弹珠阶段奖励和弹珠兑换奖励\\n2.弹珠可以碰撞阶段奖励进度，每次碰撞均可填充奖励进度，阶段奖励进度被填满后，即可获取阶段奖励。单个弹珠最多累计5次阶段奖励进度（两侧总计）\\n3.弹珠落入对应的兑换道具格中，即可获取对应数量的兑换道具\\n4.玩家可以使用兑换道具在普通商店中兑换各种奖励\\n5.弹珠掉入指定随机的奖励洞口中达到一定次数，即可激活高级福利弹珠关卡\\n6.高级福利弹珠关卡中弹珠落入洞口可获得高级兑换券，可在高级商店中兑换珍稀奖励\\n7.累计激活高级福利弹珠关卡达到指定次数时，可开启弹珠大师宝箱获得额外奖励\\n8.活动结束后，未使用的抽奖、兑换道具将会回收为15分钟训练加速、1分钟训练加速',
    # en
    '1.Spend a Draw Token to launch a Marble and earn stage rewards plus Exchange Tokens.\\n2.Each time your Marble hits a stage-reward node, the progress bar fills\u2014max it out to claim the prize. A single Marble can accumulate up to 5 stage reward progress (total for both sides).\\n3.When the Marble drops into an exchange slot, you receive the corresponding Exchange Tokens.\\n4.Trade Exchange Tokens for rewards in the Normal Shop.\\n5.When Marbles drop into the designated random reward slot a certain number of times, the Premium Bonus Marble Round is activated.\\n6.In the Premium Bonus Marble Round, Marbles that land in slots award Premium Exchange Tickets, redeemable in the Advanced Shop for rare rewards.\\n7.Activating the Premium Bonus Marble Round a set number of times unlocks the Marble Master Chest for extra rewards.\\n8.When the event ends, unused Draw and Exchange items convert into 15-minute Training Speedup and 1-minute Training Speedup.',
    # fr
    "1.D\u00e9pensez des Jetons de Tirage pour lancer des Billes et gagner des r\u00e9compenses d'\u00e9tape et des jetons d'\u00e9change.\\n2.Chaque fois qu'une Bille touche un n\u0153ud de r\u00e9compense, la barre de progression se remplit. Remplissez-la pour obtenir le prix. Une seule Bille peut accumuler jusqu'\u00e0 5 progressions (des deux c\u00f4t\u00e9s).\\n3.Lorsqu'une Bille tombe dans une case d'\u00e9change, vous recevez les Jetons correspondants.\\n4.Utilisez les Jetons d'\u00e9change pour \u00e9changer des r\u00e9compenses dans la Boutique Normale.\\n5.Lorsque les Billes tombent un certain nombre de fois dans la case de r\u00e9compense al\u00e9atoire d\u00e9sign\u00e9e, le Tour Bonus Premium des Billes est activ\u00e9.\\n6.Pendant le Tour Bonus Premium des Billes, les Billes qui atterrissent dans les cases rapportent des Tickets d'\u00c9change Premium, \u00e9changeables en Boutique Avanc\u00e9e contre des r\u00e9compenses rares.\\n7.Activer le Tour Bonus Premium des Billes un certain nombre de fois d\u00e9bloque le Coffre Ma\u00eetre des Billes avec des r\u00e9compenses suppl\u00e9mentaires.\\n8.\u00c0 la fin de l'\u00e9v\u00e9nement, les objets de tirage et d'\u00e9change inutilis\u00e9s sont convertis en Acc\u00e9l\u00e9rations d'Entra\u00eenement de 15 min et 1 min.",
    # de
    '1.Setze Zieh-Marken ein, um Murmeln zu starten und Stufen-Belohnungen sowie Tausch-Marken zu erhalten.\\n2.Jedes Mal, wenn eine Murmel einen Belohnungsknoten trifft, f\u00fcllt sich der Fortschrittsbalken. F\u00fclle ihn, um den Preis zu erhalten. Eine einzelne Murmel kann bis zu 5 Stufen-Fortschritte sammeln (beide Seiten zusammen).\\n3.Wenn eine Murmel in einen Tauschplatz f\u00e4llt, erh\u00e4ltst du die entsprechenden Tausch-Marken.\\n4.Verwende Tausch-Marken, um Belohnungen im Normalen Shop einzul\u00f6sen.\\n5.Wenn Murmeln eine bestimmte Anzahl von Malen in den festgelegten zuf\u00e4lligen Belohnungsschlitz fallen, wird die Premium-Bonus-Murmelrunde aktiviert.\\n6.In der Premium-Bonus-Murmelrunde landen Murmeln in Schlitzen f\u00fcr Premium-Tauschtickets, einl\u00f6sbar im Fortgeschrittenen Shop f\u00fcr seltene Belohnungen.\\n7.Das Aktivieren der Premium-Bonus-Murmelrunde eine bestimmte Anzahl von Malen schaltet die Murmel-Meister-Truhe mit Extra-Belohnungen frei.\\n8.Nach dem Event werden unbenutzte Zieh- und Tausch-Gegenst\u00e4nde in 15-Min- und 1-Min-Trainings-Beschleunigungen umgewandelt.',
    # po
    '1.Gaste Fichas de Sorteio para lan\u00e7ar Bolas e ganhar recompensas de etapa e fichas de troca.\\n2.Cada vez que uma Bola atinge um n\u00f3 de recompensa, a barra de progresso \u00e9 preenchida. Complete-a para reivindicar o pr\u00eamio. Uma \u00fanica Bola pode acumular at\u00e9 5 progressos (ambos os lados).\\n3.Quando uma Bola cai em um slot de troca, voc\u00ea recebe as Fichas correspondentes.\\n4.Use Fichas de Troca para resgatar recompensas na Loja Normal.\\n5.Quando as Bolas ca\u00edrem no slot de recompensa aleat\u00f3rio designado um certo n\u00famero de vezes, a Rodada B\u00f4nus Premium de Bolas \u00e9 ativada.\\n6.Na Rodada B\u00f4nus Premium de Bolas, Bolas que caem em slots concedem Bilhetes de Troca Premium, resgat\u00e1veis na Loja Avan\u00e7ada por recompensas raras.\\n7.Ativar a Rodada B\u00f4nus Premium de Bolas um n\u00famero definido de vezes desbloqueia o Ba\u00fa Mestre de Bolas com recompensas extras.\\n8.Quando o evento terminar, itens de sorteio e troca n\u00e3o utilizados ser\u00e3o convertidos em Acelera\u00e7\u00f5es de Treino de 15 min e 1 min.',
    # zh (繁體)
    '1.玩家消耗抽獎道具，發射彈珠抽獎即可獲取彈珠階段獎勵和彈珠兌換獎勵\\n2.彈珠可以碰撞階段獎勵進度，每次碰撞均可填充獎勵進度，階段獎勵進度被填滿後，即可獲取階段獎勵。單個彈珠最多累計5次階段獎勵進度（兩側總計）\\n3.彈珠落入對應的兌換道具格中，即可獲取對應數量的兌換道具\\n4.玩家可以使用兌換道具在普通商店中兌換各種獎勵\\n5.彈珠掉入指定隨機的獎勵洞口中達到一定次數，即可激活高級福利彈珠關卡\\n6.高級福利彈珠關卡中彈珠落入洞口可獲得高級兌換券，可在高級商店中兌換珍稀獎勵\\n7.累計激活高級福利彈珠關卡達到指定次數時，可開啟彈珠大師寶箱獲得額外獎勵\\n8.活動結束後，未使用的抽獎、兌換道具將會回收為15分鐘訓練加速、1分鐘訓練加速',
    # id
    '1.Gunakan Token Undian untuk meluncurkan Kelereng dan dapatkan hadiah tahap serta token penukaran.\\n2.Setiap kali Kelereng mengenai node hadiah, bar progres terisi. Isi penuh untuk mengklaim hadiah. Satu Kelereng dapat mengumpulkan hingga 5 progres (kedua sisi).\\n3.Saat Kelereng jatuh ke slot penukaran, Anda menerima Token Penukaran yang sesuai.\\n4.Gunakan Token Penukaran untuk menukarkan hadiah di Toko Normal.\\n5.Ketika Kelereng jatuh ke slot hadiah acak yang ditentukan sejumlah kali tertentu, Ronde Bonus Premium Kelereng diaktifkan.\\n6.Di Ronde Bonus Premium Kelereng, Kelereng yang mendarat di slot memberikan Tiket Penukaran Premium, dapat ditukar di Toko Lanjutan untuk hadiah langka.\\n7.Mengaktifkan Ronde Bonus Premium Kelereng sejumlah kali yang ditentukan membuka Peti Master Kelereng dengan hadiah ekstra.\\n8.Saat event berakhir, item undian dan penukaran yang tidak digunakan dikonversi menjadi Percepatan Latihan 15 menit dan 1 menit.',
    # th
    '1.ใช้โทเค็นจับฉลากเพื่อยิงลูกแก้วและรับรางวัลตามขั้นตอนพร้อมโทเค็นแลกเปลี่ยน\\n2.ทุกครั้งที่ลูกแก้วชนโหนดรางวัล แถบความคืบหน้าจะเติมเต็ม เติมเต็มเพื่อรับรางวัล ลูกแก้วหนึ่งลูกสะสมได้สูงสุด 5 ความคืบหน้า (ทั้งสองด้านรวมกัน)\\n3.เมื่อลูกแก้วตกลงในช่องแลกเปลี่ยน คุณจะได้รับโทเค็นแลกเปลี่ยนที่สอดคล้อง\\n4.ใช้โทเค็นแลกเปลี่ยนเพื่อแลกรางวัลในร้านค้าปกติ\\n5.เมื่อลูกแก้วตกในช่องรางวัลสุ่มที่กำหนดจำนวนครั้งหนึ่ง รอบโบนัสพรีเมียมลูกแก้วจะถูกเปิดใช้งาน\\n6.ในรอบโบนัสพรีเมียมลูกแก้ว ลูกแก้วที่ตกในช่องจะให้ตั๋วแลกเปลี่ยนพรีเมียม แลกได้ในร้านค้าขั้นสูงเพื่อรับรางวัลหายาก\\n7.การเปิดใช้งานรอบโบนัสพรีเมียมลูกแก้วตามจำนวนครั้งที่กำหนดจะปลดล็อคกล่องสมบัติปรมาจารย์ลูกแก้วพร้อมรางวัลพิเศษ\\n8.เมื่อกิจกรรมสิ้นสุด ไอเทมจับฉลากและแลกเปลี่ยนที่ไม่ได้ใช้จะถูกแปลงเป็นเร่งการฝึก 15 นาทีและ 1 นาที',
    # sp
    '1.Gasta Fichas de Sorteo para lanzar Canicas y ganar recompensas de etapa y fichas de intercambio.\\n2.Cada vez que una Canica golpea un nodo de recompensa, la barra de progreso se llena. Compl\u00e9tala para reclamar el premio. Una sola Canica puede acumular hasta 5 progresos (ambos lados).\\n3.Cuando una Canica cae en una ranura de intercambio, recibes las Fichas correspondientes.\\n4.Usa las Fichas de Intercambio para canjear recompensas en la Tienda Normal.\\n5.Cuando las Canicas caen en la ranura de recompensa aleatoria designada un cierto n\u00famero de veces, se activa la Ronda Bonus Premium de Canicas.\\n6.En la Ronda Bonus Premium de Canicas, las Canicas que caen en ranuras otorgan Tickets de Intercambio Premium, canjeables en la Tienda Avanzada por recompensas raras.\\n7.Activar la Ronda Bonus Premium de Canicas un n\u00famero determinado de veces desbloquea el Cofre Maestro de Canicas con recompensas adicionales.\\n8.Al finalizar el evento, los objetos de sorteo e intercambio no utilizados se convierten en Aceleraciones de Entrenamiento de 15 min y 1 min.',
    # ru
    '1.Тратьте жетоны розыгрыша, чтобы запустить шарики и получить награды этапов и жетоны обмена.\\n2.Каждый раз, когда шарик попадает в узел награды, полоса прогресса заполняется. Заполните её, чтобы получить приз. Один шарик может накопить до 5 прогрессов (с обеих сторон).\\n3.Когда шарик попадает в ячейку обмена, вы получаете соответствующие жетоны обмена.\\n4.Используйте жетоны обмена для получения наград в обычном магазине.\\n5.Когда шарики попадают в указанную случайную лунку наград определённое количество раз, активируется премиум-бонусный раунд шариков.\\n6.В премиум-бонусном раунде шарики, попавшие в лунки, приносят премиум-билеты обмена, обмениваемые в продвинутом магазине на редкие награды.\\n7.Активация премиум-бонусного раунда определённое количество раз открывает сундук мастера шариков с дополнительными наградами.\\n8.По окончании события неиспользованные предметы розыгрыша и обмена конвертируются в 15-мин и 1-мин ускорения тренировки.',
    # tr
    "1.Çekiliş Jetonları harcayarak Bilye fırlatın, aşama ödülleri ve takas jetonları kazanın.\\n2.Bilye her ödül düğümüne çarptığında ilerleme çubuğu dolar. Ödülü almak için doldurun. Tek bir Bilye en fazla 5 ilerleme biriktirebilir (iki taraf toplamı).\\n3.Bilye bir takas yuvasına düştüğünde ilgili Takas Jetonlarını alırsınız.\\n4.Takas Jetonlarını Normal Mağaza'da ödüller için kullanın.\\n5.Bilyeler belirlenen rastgele ödül yuvasına belirli bir sayıda düştüğünde, Premium Bonus Bilye Turu etkinleştirilir.\\n6.Premium Bonus Bilye Turunda yuvalara düşen Bilyeler Premium Takas Biletleri verir, Gelişmiş Mağaza'da nadir ödüller için takas edilebilir.\\n7.Premium Bonus Bilye Turunu belirli sayıda etkinleştirmek, ekstra ödüller için Bilye Ustası Sandığını açar.\\n8.Etkinlik sona erdiğinde kullanılmayan çekiliş ve takas eşyaları 15 dk ve 1 dk Eğitim Hızlandırıcılarına dönüştürülür.",
    # vi
    '1.Sử dụng Vé Quay để bắn Bi và nhận phần thưởng giai đoạn cùng token đổi thưởng.\\n2.Mỗi lần Bi chạm vào nút thưởng, thanh tiến trình sẽ được lấp đầy. Lấp đầy để nhận giải. Một viên Bi có thể tích lũy tối đa 5 tiến trình (cả hai bên).\\n3.Khi Bi rơi vào ô đổi, bạn nhận được Token Đổi Thưởng tương ứng.\\n4.Dùng Token Đổi Thưởng để đổi phần thưởng tại Cửa Hàng Thường.\\n5.Khi Bi rơi vào ô thưởng ngẫu nhiên được chỉ định đủ số lần nhất định, Vòng Thưởng Bi Cao Cấp sẽ được kích hoạt.\\n6.Trong Vòng Thưởng Bi Cao Cấp, Bi rơi vào ô sẽ nhận Vé Đổi Cao Cấp, có thể đổi tại Cửa Hàng Cao Cấp lấy phần thưởng quý hiếm.\\n7.Kích hoạt Vòng Thưởng Bi Cao Cấp đủ số lần nhất định sẽ mở Rương Bậc Thầy Bi với phần thưởng bổ sung.\\n8.Khi sự kiện kết thúc, vật phẩm quay và đổi chưa dùng sẽ được chuyển thành Tăng Tốc Huấn Luyện 15 phút và 1 phút.',
    # it
    "1.Spendi Gettoni Estrazione per lanciare Biglie e ottenere ricompense di tappa e gettoni scambio.\\n2.Ogni volta che una Biglia colpisce un nodo ricompensa, la barra progresso si riempie. Completala per ottenere il premio. Una singola Biglia può accumulare fino a 5 progressi (entrambi i lati).\\n3.Quando una Biglia cade in uno slot di scambio, ricevi i Gettoni Scambio corrispondenti.\\n4.Usa i Gettoni Scambio per riscattare ricompense nel Negozio Normale.\\n5.Quando le Biglie cadono un certo numero di volte nello slot di ricompensa casuale designato, si attiva il Round Bonus Premium delle Biglie.\\n6.Nel Round Bonus Premium delle Biglie, le Biglie che atterrano negli slot assegnano Biglietti Scambio Premium, riscattabili nel Negozio Avanzato per ricompense rare.\\n7.Attivare il Round Bonus Premium delle Biglie un certo numero di volte sblocca lo Scrigno Maestro delle Biglie con ricompense extra.\\n8.Al termine dell'evento, gli oggetti di estrazione e scambio non utilizzati vengono convertiti in Accelerazioni Addestramento da 15 min e 1 min.",
    # pl
    '1.Wydaj Żetony Losowania, aby wystrzelić Kulki i zdobyć nagrody etapowe oraz żetony wymiany.\\n2.Za każdym razem, gdy Kulka trafi w węzeł nagrody, pasek postępu się zapełnia. Zapełnij go, aby odebrać nagrodę. Jedna Kulka może zgromadzić do 5 postępów (obie strony łącznie).\\n3.Gdy Kulka wpada do slotu wymiany, otrzymujesz odpowiednie Żetony Wymiany.\\n4.Użyj Żetonów Wymiany, aby wymieniać nagrody w Sklepie Zwykłym.\\n5.Gdy Kulki wpadną do wyznaczonego losowego slotu nagrody określoną liczbę razy, aktywowana zostaje Premium Runda Bonusowa Kulek.\\n6.W Premium Rundzie Bonusowej Kulek, Kulki lądujące w slotach dają Bilety Wymiany Premium, wymienialne w Sklepie Zaawansowanym na rzadkie nagrody.\\n7.Aktywowanie Premium Rundy Bonusowej Kulek określoną liczbę razy odblokowuje Skrzynię Mistrza Kulek z dodatkowymi nagrodami.\\n8.Po zakończeniu wydarzenia niewykorzystane przedmioty losowania i wymiany zostaną zamienione na Przyspieszenia Treningu 15 min i 1 min.',
    # ar
    '1.أنفق رموز السحب لإطلاق الكرات والحصول على مكافآت المراحل ورموز التبادل.\\n2.في كل مرة تصطدم فيها كرة بعقدة مكافأة، يمتلئ شريط التقدم. أكمله للحصول على الجائزة. يمكن لكرة واحدة تجميع حتى 5 تقدمات (كلا الجانبين).\\n3.عندما تسقط كرة في فتحة تبادل، تحصل على رموز التبادل المقابلة.\\n4.استخدم رموز التبادل لاستبدال المكافآت في المتجر العادي.\\n5.عندما تسقط الكرات في فتحة المكافأة العشوائية المحددة عدداً معيناً من المرات، يتم تفعيل جولة الكرات البونص الممتازة.\\n6.في جولة الكرات البونص الممتازة، الكرات التي تهبط في الفتحات تمنح تذاكر تبادل ممتازة، قابلة للاستبدال في المتجر المتقدم بمكافآت نادرة.\\n7.تفعيل جولة الكرات البونص الممتازة عدداً محدداً من المرات يفتح صندوق سيد الكرات بمكافآت إضافية.\\n8.عند انتهاء الحدث، يتم تحويل عناصر السحب والتبادل غير المستخدمة إلى تسريعات تدريب 15 دقيقة و1 دقيقة.',
    # jp
    '1.抽選トークンを使ってマーブルを発射し、ステージ報酬と交換トークンを獲得します。\\n2.マーブルが報酬ノードに当たるたびにプログレスバーが溜まります。満タンにすると報酬を獲得できます。1つのマーブルで最大5回分のステージ報酬進捗を蓄積できます（両側合計）。\\n3.マーブルが交換スロットに落ちると、対応する交換トークンを受け取ります。\\n4.交換トークンを使って通常ショップで報酬と交換できます。\\n5.マーブルが指定されたランダムな報酬スロットに一定回数落ちると、プレミアムボーナスマーブルラウンドが発動します。\\n6.プレミアムボーナスマーブルラウンドでスロットに落ちたマーブルはプレミアム交換チケットを獲得でき、上級ショップで希少報酬と交換可能です。\\n7.プレミアムボーナスマーブルラウンドを規定回数発動すると、マーブルマスターチェストが開放され、追加報酬を獲得できます。\\n8.イベント終了後、未使用の抽選・交換アイテムは15分訓練加速と1分訓練加速に変換されます。',
    # kr
    '1.뽑기 토큰을 사용하여 구슬을 발사하고 단계 보상과 교환 토큰을 획득하세요.\\n2.구슬이 보상 노드에 맞을 때마다 진행 바가 채워집니다. 가득 채우면 보상을 받을 수 있습니다. 구슬 하나당 최대 5회 단계 보상 진행도를 누적할 수 있습니다 (양쪽 합산).\\n3.구슬이 교환 슬롯에 떨어지면 해당 교환 토큰을 받습니다.\\n4.교환 토큰을 사용하여 일반 상점에서 보상을 교환하세요.\\n5.구슬이 지정된 랜덤 보상 슬롯에 일정 횟수 떨어지면, 프리미엄 보너스 구슬 라운드가 활성화됩니다.\\n6.프리미엄 보너스 구슬 라운드에서 슬롯에 떨어진 구슬은 프리미엄 교환 티켓을 획득하며, 고급 상점에서 희귀 보상으로 교환할 수 있습니다.\\n7.프리미엄 보너스 구슬 라운드를 지정된 횟수만큼 활성화하면 추가 보상이 담긴 구슬 마스터 상자가 열립니다.\\n8.이벤트 종료 시 미사용 뽑기 및 교환 아이템은 15분 훈련 가속과 1분 훈련 가속으로 전환됩니다.',
    # cns = cn
    '1.玩家消耗抽奖道具，发射弹珠抽奖即可获取弹珠阶段奖励和弹珠兑换奖励\\n2.弹珠可以碰撞阶段奖励进度，每次碰撞均可填充奖励进度，阶段奖励进度被填满后，即可获取阶段奖励。单个弹珠最多累计5次阶段奖励进度（两侧总计）\\n3.弹珠落入对应的兑换道具格中，即可获取对应数量的兑换道具\\n4.玩家可以使用兑换道具在普通商店中兑换各种奖励\\n5.弹珠掉入指定随机的奖励洞口中达到一定次数，即可激活高级福利弹珠关卡\\n6.高级福利弹珠关卡中弹珠落入洞口可获得高级兑换券，可在高级商店中兑换珍稀奖励\\n7.累计激活高级福利弹珠关卡达到指定次数时，可开启弹珠大师宝箱获得额外奖励\\n8.活动结束后，未使用的抽奖、兑换道具将会回收为15分钟训练加速、1分钟训练加速',
]

def main():
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="'EVENT'!C7380:T7380",
        valueInputOption="RAW",
        body={"values": [translations]},
    ).execute()

    print("✅ 2025anni_marble_gacha_rule updated: EVENT row 7380")

    r = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'EVENT'!B7380:D7380"
    ).execute()
    row = r.get("values", [[]])[0]
    print(f"   Key: {row[0]}")
    print(f"   cn (first 100): {row[1][:100]}...")

if __name__ == "__main__":
    main()
