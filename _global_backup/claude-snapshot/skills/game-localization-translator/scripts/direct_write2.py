import subprocess, json, os, tempfile

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY'
TARGET_SHEET = 'EVENT'

start_id = 1011089578

rows = [
    [start_id, 'easter_fest_pack_core_decipher_name', '矿洞寻宝卡包', 'Mine Treasure Hunt Card Pack', 'Pack de cartes Chasse au tresor minier', 'Minenschatzsuche-Kartenpaket', 'Pacote de Cartas Caca ao Tesouro na Mina', '礦洞尋寶卡包', 'Paket Kartu Berburu Harta Karun Tambang', 'แพ็คการ์ดล่าสมบัติเหมือง', 'Paquete de Cartas Busqueda del Tesoro Minero', 'Набор карт Охота за сокровищами в шахте', 'Maden Hazine Avi Kart Paketi', 'Goi The San Kho Bau Ham Mo', 'Pacchetto Carte Caccia al Tesoro Minerario', 'Paczka Kart Poszukiwanie Skarbow w Kopalni', 'حزمة بطاقات البحث عن الكنز في المنجم', '鉱山トレジャーハントカードパック', '광산 보물찾기 카드팩', '矿洞寻宝卡包'],
    [start_id+1, 'easter_fest_pack_core_decipher_desc', '打开即可获得两张3星以上"矿洞寻宝"游戏卡片。', 'Open to receive 2 "Mine Treasure Hunt" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Chasse au tresor minier" de 3 etoiles ou plus.', 'Offnen, um 2 "Minenschatzsuche"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas de jogo "Caca ao Tesouro na Mina" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「礦洞尋寶」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu game "Berburu Harta Karun Tambang" bintang 3 atau lebih.', 'เปิดเพื่อรับการ์ดเกม "ล่าสมบัติเหมือง" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas de juego "Busqueda del Tesoro Minero" de 3 estrellas o mas.', 'Откройте, чтобы получить 2 игровые карты Охота за сокровищами в шахте от 3 звёзд.', 'Acarak 3 yildiz ve uzeri 2 "Maden Hazine Avi" oyun karti alin.', 'Mo de nhan 2 the game "San Kho Bau Ham Mo" tu 3 sao tro len.', 'Apri per ricevere 2 carte gioco "Caccia al Tesoro Minerario" da 3 stelle o superiori.', 'Otworz, aby otrzymac 2 karty gry "Poszukiwanie Skarbow w Kopalni" o 3 gwiazdkachecej.', 'افتح للحصول على بطاقتين من لعبة البحث عن الكنز في المنجم بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「鉱山トレジャーハント」ゲームカードを2枚獲得できます。', '열면 3성 이상 "광산 보물찾기" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"矿洞寻宝"游戏卡片。'],
    [start_id+2, 'easter_fest_pack_underground_name', '极速飞车卡包', 'Speed Racing Card Pack', 'Pack de cartes Course de vitesse', 'Hochgeschwindigkeitsrennen-Kartenpaket', 'Pacote de Cartas Corrida Veloz', '極速飛車卡包', 'Paket Kartu Balap Kecepatan', 'แพ็คการ์ดแข่งรถความเร็ว', 'Paquete de Cartas Carrera de Velocidad', 'Набор карт Скоростные гонки', 'Hiz Yarisi Kart Paketi', 'Goi The Dua Xe Toc Do', 'Pacchetto Carte Corsa Veloce', 'Paczka Kart Wyscigi Predkosci', 'حزمة بطاقات سباق السرعة', 'スピードレーシングカードパック', '스피드 레이싱 카드팩', '极速飞车卡包'],
    [start_id+3, 'easter_fest_pack_underground_desc', '打开即可获得两张3星以上"极速飞车"游戏卡片。', 'Open to receive 2 "Speed Racing" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Course de vitesse" de 3 etoiles ou plus.', 'Offnen, um 2 "Hochgeschwindigkeitsrennen"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas de jogo "Corrida Veloz" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「極速飛車」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu game "Balap Kecepatan" bintang 3 atau lebih.', 'เปิดเพื่อรับการ์ดเกม "แข่งรถความเร็ว" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas de juego "Carrera de Velocidad" de 3 estrellas o mas.', 'Откройте, чтобы получить 2 игровые карты Скоростные гонки от 3 звёзд.', 'Acarak 3 yildiz ve uzeri 2 "Hiz Yarisi" oyun karti alin.', 'Mo de nhan 2 the game "Dua Xe Toc Do" tu 3 sao tro len.', 'Apri per ricevere 2 carte gioco "Corsa Veloce" da 3 stelle o superiori.', 'Otworz, aby otrzymac 2 karty gry "Wyscigi Predkosci" o 3 gwiazdkach lub wiecej.', 'افتح للحصول على بطاقتين من لعبة سباق السرعة بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「スピードレーシング」ゲームカードを2枚獲得できます。', '열면 3성 이상 "스피드 레이싱" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"极速飞车"游戏卡片。'],
    [start_id+4, 'easter_fest_pack_lucky_marble_name', '彩蛋大亨卡包', 'Easter Tycoon Card Pack', 'Pack de cartes Magnat de Paques', 'Oster-Tycoon-Kartenpaket', 'Pacote de Cartas Magnata da Pascoa', '彩蛋大亨卡包', 'Paket Kartu Taipan Paskah', 'แพ็คการ์ดเศรษฐีอีสเตอร์', 'Paquete de Cartas Magnate de Pascua', 'Набор карт Пасхальный магнат', 'Paskalya Kodamani Kart Paketi', 'Goi The Dai Gia Phuc Sinh', 'Pacchetto Carte Magnate di Pasqua', 'Paczka Kart Wielkanocny Potentat', 'حزمة بطاقات قطب عيد الفصح', 'イースタータイクーンカードパック', '이스터 타이쿤 카드팩', '彩蛋大亨卡包'],
    [start_id+5, 'easter_fest_pack_lucky_marble_desc', '打开即可获得两张3星以上"彩蛋大亨"游戏卡片。', 'Open to receive 2 "Easter Tycoon" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Magnat de Paques" de 3 etoiles ou plus.', 'Offnen, um 2 "Oster-Tycoon"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas de jogo "Magnata da Pascoa" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「彩蛋大亨」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu game "Taipan Paskah" bintang 3 atau lebih.', 'เปิดเพื่อรับการ์ดเกม "เศรษฐีอีสเตอร์" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas de juego "Magnate de Pascua" de 3 estrellas o mas.', 'Откройте, чтобы получить 2 игровые карты Пасхальный магнат от 3 звёзд.', 'Acarak 3 yildiz ve uzeri 2 "Paskalya Kodamani" oyun karti alin.', 'Mo de nhan 2 the game "Dai Gia Phuc Sinh" tu 3 sao tro len.', 'Apri per ricevere 2 carte gioco "Magnate di Pasqua" da 3 stelle o superiori.', 'Otworz, aby otrzymac 2 karty gry "Wielkanocny Potentat" o 3 gwiazdkach lub wiecej.', 'افتح للحصول على بطاقتين من لعبة قطب عيد الفصح بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「イースタータイクーン」ゲームカードを2枚獲得できます。', '열면 3성 이상 "이스터 타이쿤" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"彩蛋大亨"游戏卡片。'],
    [start_id+6, 'easter_fest_pack_coin_pusher_name', '异族探秘卡包', 'Alien Exploration Card Pack', 'Pack de cartes Exploration extraterrestre', 'Alien-Erkundungs-Kartenpaket', 'Pacote de Cartas Exploracao Alienigena', '異族探秘卡包', 'Paket Kartu Eksplorasi Alien', 'แพ็คการ์ดสำรวจเอเลี่ยน', 'Paquete de Cartas Exploracion Alienigena', 'Набор карт Исследование инопланетян', 'Uzayli Kesfi Kart Paketi', 'Goi The Kham Pha Nguoi Ngoai Hanh Tinh', 'Pacchetto Carte Esplorazione Aliena', 'Paczka Kart Eksploracja Obcych', 'حزمة بطاقات استكشاف الفضائيين', 'エイリアン探検カードパック', '외계인 탐험 카드팩', '异族探秘卡包'],
    [start_id+7, 'easter_fest_pack_coin_pusher_desc', '打开即可获得两张3星以上"异族探秘"游戏卡片。', 'Open to receive 2 "Alien Exploration" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Exploration extraterrestre" de 3 etoiles ou plus.', 'Offnen, um 2 "Alien-Erkundungs"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas de jogo "Exploracao Alienigena" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「異族探秘」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu game "Eksplorasi Alien" bintang 3 atau lebih.', 'เปิดเพื่อรับการ์ดเกม "สำรวจเอเลี่ยน" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas de juego "Exploracion Alienigena" de 3 estrellas o mas.', 'Откройте, чтобы получить 2 игровые карты Исследование инопланетян от 3 звёзд.', 'Acarak 3 yildiz ve uzeri 2 "Uzayli Kesfi" oyun karti alin.', 'Mo de nhan 2 the game "Kham Pha Nguoi Ngoai Hanh Tinh" tu 3 sao tro len.', 'Apri per ricevere 2 carte gioco "Esplorazione Aliena" da 3 stelle o superiori.', 'Otworz, aby otrzymac 2 karty gry "Eksploracja Obcych" o 3 gwiazdkach lub wiecej.', 'افتح للحصول على بطاقتين من لعبة استكشاف الفضائيين بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「エイリアン探検」ゲームカードを2枚獲得できます。', '열면 3성 이상 "외계인 탐험" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"异族探秘"游戏卡片。'],
]

# Write to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
    json.dump({'values': rows}, f, ensure_ascii=False)
    temp_file = f.name

append_params = json.dumps({
    'spreadsheetId': SPREADSHEET_ID,
    'range': f'{TARGET_SHEET}!A1',
    'valueInputOption': 'RAW',
    'insertDataOption': 'INSERT_ROWS',
})

with open(temp_file, 'r', encoding='utf-8') as f:
    body_json = f.read()

r = subprocess.run(
    [GWS, 'sheets', 'spreadsheets', 'values', 'append',
     '--params', append_params,
     '--json', body_json],
    capture_output=True, text=True, encoding='utf-8'
)
print('stdout:', r.stdout)
print('stderr:', r.stderr)
os.unlink(temp_file)
