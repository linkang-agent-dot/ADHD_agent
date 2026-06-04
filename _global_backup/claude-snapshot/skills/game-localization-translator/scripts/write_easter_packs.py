import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY'
STAGING_SHEET = 'AI翻译暂存'

# 12 rows: [目标页签, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROWS = [
    ['ITEM', 'easter_fest_pack_core_decipher_name', '矿洞寻宝卡包', 'Mine Treasure Hunt Card Pack', 'Pack de Cartes Chasse au Trésor Minier', 'Minenschatzsuche-Kartenpaket', 'Pacote de Cartas Caça ao Tesouro na Mina', '礦洞尋寶卡包', 'Paket Kartu Berburu Harta Karun Tambang', 'แพ็คการ์ดล่าสมบัติเหมือง', 'Paquete de Cartas Búsqueda del Tesoro Minero', 'Набор карт «Охота за сокровищами в шахте»', 'Maden Hazine Avı Kart Paketi', 'Gói Thẻ Săn Kho Báu Hầm Mỏ', 'Pacchetto Carte Caccia al Tesoro in Miniera', 'Paczka Kart Poszukiwanie Skarbów w Kopalni', 'حزمة بطاقات البحث عن الكنز في المنجم', '鉱山トレジャーハントカードパック', '광산 보물찾기 카드 팩', '矿洞寻宝卡包'],
    ['ITEM', 'easter_fest_pack_core_decipher_desc', '打开即可获得两张3星以上"矿洞寻宝"游戏卡片。', 'Open to receive 2 "Mine Treasure Hunt" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Chasse au Trésor Minier" de 3 étoiles ou plus.', 'Öffnen, um 2 "Minenschatzsuche"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas do jogo "Caça ao Tesouro na Mina" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「礦洞尋寶」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu permainan "Berburu Harta Karun Tambang" bintang 3 ke atas.', 'เปิดเพื่อรับการ์ดเกม "ล่าสมบัติเหมือง" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas del juego "Búsqueda del Tesoro Minero" de 3 estrellas o más.', 'Откройте, чтобы получить 2 игровые карты «Охота за сокровищами в шахте» от 3 звёзд и выше.', 'Açarak 3 yıldız ve üzeri 2 "Maden Hazine Avı" oyun kartı kazanın.', 'Mở để nhận 2 thẻ trò chơi "Săn Kho Báu Hầm Mỏ" từ 3 sao trở lên.', 'Apri per ricevere 2 carte gioco "Caccia al Tesoro in Miniera" da 3 stelle o superiori.', 'Otwórz, aby otrzymać 2 karty gry "Poszukiwanie Skarbów w Kopalni" o 3 gwiazdkach lub więcej.', 'افتح للحصول على بطاقتين من لعبة "البحث عن الكنز في المنجم" بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「鉱山トレジャーハント」ゲームカードを2枚獲得できます。', '열면 3성 이상의 "광산 보물찾기" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"矿洞寻宝"游戏卡片。'],
    ['ITEM', 'easter_fest_pack_underground_name', '极速飞车卡包', 'Speed Racing Card Pack', 'Pack de Cartes Course Rapide', 'Schnellrennen-Kartenpaket', 'Pacote de Cartas Corrida Veloz', '極速飛車卡包', 'Paket Kartu Balap Kecepatan', 'แพ็คการ์ดแข่งรถความเร็ว', 'Paquete de Cartas Carreras de Velocidad', 'Набор карт «Скоростные гонки»', 'Hız Yarışı Kart Paketi', 'Gói Thẻ Đua Xe Tốc Độ', 'Pacchetto Carte Corse Veloci', 'Paczka Kart Szybkie Wyścigi', 'حزمة بطاقات سباق السرعة', 'スピードレーシングカードパック', '스피드 레이싱 카드 팩', '极速飞车卡包'],
    ['ITEM', 'easter_fest_pack_underground_desc', '打开即可获得两张3星以上"极速飞车"游戏卡片。', 'Open to receive 2 "Speed Racing" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Course Rapide" de 3 étoiles ou plus.', 'Öffnen, um 2 "Schnellrennen"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas do jogo "Corrida Veloz" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「極速飛車」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu permainan "Balap Kecepatan" bintang 3 ke atas.', 'เปิดเพื่อรับการ์ดเกม "แข่งรถความเร็ว" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas del juego "Carreras de Velocidad" de 3 estrellas o más.', 'Откройте, чтобы получить 2 игровые карты «Скоростные гонки» от 3 звёзд и выше.', 'Açarak 3 yıldız ve üzeri 2 "Hız Yarışı" oyun kartı kazanın.', 'Mở để nhận 2 thẻ trò chơi "Đua Xe Tốc Độ" từ 3 sao trở lên.', 'Apri per ricevere 2 carte gioco "Corse Veloci" da 3 stelle o superiori.', 'Otwórz, aby otrzymać 2 karty gry "Szybkie Wyścigi" o 3 gwiazdkach lub więcej.', 'افتح للحصول على بطاقتين من لعبة "سباق السرعة" بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「スピードレーシング」ゲームカードを2枚獲得できます。', '열면 3성 이상의 "스피드 레이싱" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"极速飞车"游戏卡片。'],
    ['ITEM', 'easter_fest_pack_lucky_marble_name', '彩蛋大亨卡包', 'Easter Tycoon Card Pack', 'Pack de Cartes Magnat de Pâques', 'Oster-Tycoon-Kartenpaket', 'Pacote de Cartas Magnata da Páscoa', '彩蛋大亨卡包', 'Paket Kartu Taipan Paskah', 'แพ็คการ์ดเศรษฐีอีสเตอร์', 'Paquete de Cartas Magnate de Pascua', 'Набор карт «Пасхальный магнат»', 'Paskalya Kodamanı Kart Paketi', 'Gói Thẻ Đại Gia Phục Sinh', 'Pacchetto Carte Magnate di Pasqua', 'Paczka Kart Wielkanocny Potentat', 'حزمة بطاقات قطب عيد الفصح', 'イースタータイクーンカードパック', '이스터 타이쿤 카드 팩', '彩蛋大亨卡包'],
    ['ITEM', 'easter_fest_pack_lucky_marble_desc', '打开即可获得两张3星以上"彩蛋大亨"游戏卡片。', 'Open to receive 2 "Easter Tycoon" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Magnat de Pâques" de 3 étoiles ou plus.', 'Öffnen, um 2 "Oster-Tycoon"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas do jogo "Magnata da Páscoa" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「彩蛋大亨」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu permainan "Taipan Paskah" bintang 3 ke atas.', 'เปิดเพื่อรับการ์ดเกม "เศรษฐีอีสเตอร์" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas del juego "Magnate de Pascua" de 3 estrellas o más.', 'Откройте, чтобы получить 2 игровые карты «Пасхальный магнат» от 3 звёзд и выше.', 'Açarak 3 yıldız ve üzeri 2 "Paskalya Kodamanı" oyun kartı kazanın.', 'Mở để nhận 2 thẻ trò chơi "Đại Gia Phục Sinh" từ 3 sao trở lên.', 'Apri per ricevere 2 carte gioco "Magnate di Pasqua" da 3 stelle o superiori.', 'Otwórz, aby otrzymać 2 karty gry "Wielkanocny Potentat" o 3 gwiazdkach lub więcej.', 'افتح للحصول على بطاقتين من لعبة "قطب عيد الفصح" بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「イースタータイクーン」ゲームカードを2枚獲得できます。', '열면 3성 이상의 "이스터 타이쿤" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"彩蛋大亨"游戏卡片。'],
    ['ITEM', 'easter_fest_pack_coin_pusher_name', '异族探秘卡包', 'Alien Exploration Card Pack', 'Pack de Cartes Exploration Extraterrestre', 'Alien-Erkundungs-Kartenpaket', 'Pacote de Cartas Exploração Alienígena', '異族探秘卡包', 'Paket Kartu Eksplorasi Alien', 'แพ็คการ์ดสำรวจเอเลี่ยน', 'Paquete de Cartas Exploración Alienígena', 'Набор карт «Инопланетное исследование»', 'Uzaylı Keşfi Kart Paketi', 'Gói Thẻ Khám Phá Người Ngoài Hành Tinh', 'Pacchetto Carte Esplorazione Aliena', 'Paczka Kart Eksploracja Obcych', 'حزمة بطاقات استكشاف الفضائيين', 'エイリアン探検カードパック', '외계인 탐험 카드 팩', '异族探秘卡包'],
    ['ITEM', 'easter_fest_pack_coin_pusher_desc', '打开即可获得两张3星以上"异族探秘"游戏卡片。', 'Open to receive 2 "Alien Exploration" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Exploration Extraterrestre" de 3 étoiles ou plus.', 'Öffnen, um 2 "Alien-Erkundungs"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas do jogo "Exploração Alienígena" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「異族探秘」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu permainan "Eksplorasi Alien" bintang 3 ke atas.', 'เปิดเพื่อรับการ์ดเกม "สำรวจเอเลี่ยน" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas del juego "Exploración Alienígena" de 3 estrellas o más.', 'Откройте, чтобы получить 2 игровые карты «Инопланетное исследование» от 3 звёзд и выше.', 'Açarak 3 yıldız ve üzeri 2 "Uzaylı Keşfi" oyun kartı kazanın.', 'Mở để nhận 2 thẻ trò chơi "Khám Phá Người Ngoài Hành Tinh" từ 3 sao trở lên.', 'Apri per ricevere 2 carte gioco "Esplorazione Aliena" da 3 stelle o superiori.', 'Otwórz, aby otrzymać 2 karty gry "Eksploracja Obcych" o 3 gwiazdkach lub więcej.', 'افتح للحصول على بطاقتين من لعبة "استكشاف الفضائيين" بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「エイリアン探検」ゲームカードを2枚獲得できます。', '열면 3성 이상의 "외계인 탐험" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"异族探秘"游戏卡片。'],
    ['ITEM', 'easter_fest_pack_roaming_name', '趣味骰子卡包', 'Fun Dice Card Pack', 'Pack de Cartes Dés Amusants', 'Spaßwürfel-Kartenpaket', 'Pacote de Cartas Dados Divertidos', '趣味骰子卡包', 'Paket Kartu Dadu Seru', 'แพ็คการ์ดลูกเต๋าสนุก', 'Paquete de Cartas Dados Divertidos', 'Набор карт «Весёлые кости»', 'Eğlenceli Zar Kart Paketi', 'Gói Thẻ Xúc Xắc Vui Nhộn', 'Pacchetto Carte Dadi Divertenti', 'Paczka Kart Zabawne Kości', 'حزمة بطاقات النرد الممتع', 'ファン・サイコロカードパック', '재미 주사위 카드 팩', '趣味骰子卡包'],
    ['ITEM', 'easter_fest_pack_roaming_desc', '豪礼不断的游戏主题卡包，至少获得一张"趣味骰子"游戏卡片。', 'A reward-rich game-themed card pack. Guarantees at least one "Fun Dice" game card.', 'Un pack de cartes thématique riche en récompenses. Garantit au moins une carte de jeu "Dés Amusants".', 'Ein belohnungsreiches Spielthemen-Kartenpaket. Garantiert mindestens eine "Spaßwürfel"-Spielkarte.', 'Um pacote de cartas temático rico em recompensas. Garante pelo menos uma carta do jogo "Dados Divertidos".', '豪禮不斷的遊戲主題卡包，至少獲得一張「趣味骰子」遊戲卡片。', 'Paket kartu bertema permainan yang kaya hadiah. Dijamin mendapatkan setidaknya satu kartu permainan "Dadu Seru".', 'แพ็คการ์ดธีมเกมที่เต็มไปด้วยรางวัล รับประกันการ์ดเกม "ลูกเต๋าสนุก" อย่างน้อย 1 ใบ', 'Un paquete de cartas temático lleno de recompensas. Garantiza al menos una carta del juego "Dados Divertidos".', 'Тематический набор карт с богатыми наградами. Гарантирует как минимум одну игровую карту «Весёлые кости».', 'Ödül dolu oyun temalı kart paketi. En az bir "Eğlenceli Zar" oyun kartı garantili.', 'Gói thẻ chủ đề trò chơi giàu phần thưởng. Đảm bảo nhận được ít nhất một thẻ trò chơi "Xúc Xắc Vui Nhộn".', 'Un pacchetto carte a tema gioco ricco di ricompense. Garantisce almeno una carta gioco "Dadi Divertenti".', 'Bogaty w nagrody pakiet kart o tematyce gry. Gwarantuje co najmniej jedną kartę gry "Zabawne Kości".', 'حزمة بطاقات ذات طابع لعبة غنية بالمكافآت. تضمن بطاقة لعبة "النرد الممتع" واحدة على الأقل.', '報酬たっぷりのゲームテーマカードパック。「ファン・サイコロ」ゲームカードを少なくとも1枚獲得できます。', '보상이 풍부한 게임 테마 카드 팩. "재미 주사위" 게임 카드를 최소 1장 획득 보장.', '豪礼不断的游戏主题卡包，至少获得一张"趣味骰子"游戏卡片。'],
    ['ITEM', 'easter_fest_pack_lab_rampage_name', '天外来客卡包', 'Visitor from Beyond Card Pack', "Pack de Cartes Visiteur d'Outre-Monde", 'Besucher aus dem Jenseits Kartenpaket', 'Pacote de Cartas Visitante de Além', '天外來客卡包', 'Paket Kartu Pengunjung dari Luar', 'แพ็คการ์ดผู้มาเยือนจากต่างดาว', 'Paquete de Cartas Visitante del Más Allá', 'Набор карт «Гость из иного мира»', 'Ötelerden Gelen Ziyaretçi Kart Paketi', 'Gói Thẻ Khách Từ Cõi Khác', "Pacchetto Carte Visitatore dall'Oltre", 'Paczka Kart Gość z Zaświatów', 'حزمة بطاقات الزائر من العالم الآخر', '彼方からの来訪者カードパック', '저 너머에서 온 방문자 카드 팩', '天外来客卡包'],
    ['ITEM', 'easter_fest_pack_lab_rampage_desc', '别具一格的游戏主题卡包，至少获得一张"天外来客"游戏卡片。', 'A unique game-themed card pack. Guarantees at least one "Visitor from Beyond" game card.', "Un pack de cartes thématique unique. Garantit au moins une carte de jeu \"Visiteur d'Outre-Monde\".", 'Ein einzigartiges Spielthemen-Kartenpaket. Garantiert mindestens eine "Besucher aus dem Jenseits"-Spielkarte.', 'Um pacote de cartas temático único. Garante pelo menos uma carta do jogo "Visitante de Além".', '別具一格的遊戲主題卡包，至少獲得一張「天外來客」遊戲卡片。', 'Paket kartu bertema permainan yang unik. Dijamin mendapatkan setidaknya satu kartu permainan "Pengunjung dari Luar".', 'แพ็คการ์ดธีมเกมที่ไม่เหมือนใคร รับประกันการ์ดเกม "ผู้มาเยือนจากต่างดาว" อย่างน้อย 1 ใบ', 'Un paquete de cartas temático único. Garantiza al menos una carta del juego "Visitante del Más Allá".', 'Уникальный тематический набор карт. Гарантирует как минимум одну игровую карту «Гость из иного мира».', 'Benzersiz oyun temalı kart paketi. En az bir "Ötelerden Gelen Ziyaretçi" oyun kartı garantili.', 'Gói thẻ chủ đề trò chơi độc đáo. Đảm bảo nhận được ít nhất một thẻ trò chơi "Khách Từ Cõi Khác".', "Un pacchetto carte a tema gioco unico. Garantisce almeno una carta gioco \"Visitatore dall'Oltre\".", 'Unikalny pakiet kart o tematyce gry. Gwarantuje co najmniej jedną kartę gry "Gość z Zaświatów".', 'حزمة بطاقات ذات طابع لعبة فريدة. تضمن بطاقة لعبة "الزائر من العالم الآخر" واحدة على الأقل.', '個性的なゲームテーマカードパック。「彼方からの来訪者」ゲームカードを少なくとも1枚獲得できます。', '독특한 게임 테마 카드 팩. "저 너머에서 온 방문자" 게임 카드를 최소 1장 획득 보장.', '别具一格的游戏主题卡包，至少获得一张"天外来客"游戏卡片。'],
]

def get_credentials():
    result = subprocess.run(
        ['gws', 'auth', 'export', '--unmasked'],
        capture_output=True, text=True, encoding='utf-8', shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    return Credentials(
        token=None,
        refresh_token=creds_data['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
    )

def main():
    credentials = get_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    sheets_api = service.spreadsheets()

    # 获取暂存页签 sheetId
    spreadsheet = sheets_api.get(spreadsheetId=SPREADSHEET_ID, fields='sheets.properties').execute()
    staging_sheet_id = None
    for s in spreadsheet['sheets']:
        if s['properties']['title'] == STAGING_SHEET:
            staging_sheet_id = s['properties']['sheetId']
            break

    # 定位追加起始行
    result = sheets_api.values().get(spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A").execute()
    existing = result.get('values', [])
    next_row = max(len(existing) + 1, 2)
    end_row = next_row + len(ROWS) - 1

    # 写入数据到 B~U 列
    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{end_row}",
        valueInputOption='RAW',
        body={'values': ROWS},
    ).execute()

    # 为 A 列设置 checkbox
    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'requests': [{
            'repeatCell': {
                'range': {
                    'sheetId': staging_sheet_id,
                    'startRowIndex': next_row - 1,
                    'endRowIndex': end_row,
                    'startColumnIndex': 0, 'endColumnIndex': 1,
                },
                'cell': {
                    'dataValidation': {'condition': {'type': 'BOOLEAN'}, 'strict': True},
                    'userEnteredValue': {'boolValue': False},
                },
                'fields': 'dataValidation,userEnteredValue',
            }
        }]},
    ).execute()
    print(f'Done! Wrote {len(ROWS)} rows (row {next_row}-{end_row})')

if __name__ == "__main__":
    main()
