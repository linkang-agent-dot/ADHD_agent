import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY'
STAGING_SHEET = 'AI翻译暂存'

# 每行格式: [目标页签, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROWS = [
    ['EVENT', 'easter_fest_pack_core_decipher_name', '矿洞寻宝卡包', 'Mine Treasure Hunt Card Pack', 'Pack de cartes Chasse au trésor minier', 'Minenschatzsuche-Kartenpaket', 'Pacote de Cartas Caça ao Tesouro na Mina', '礦洞尋寶卡包', 'Paket Kartu Berburu Harta Karun Tambang', 'แพ็คการ์ดล่าสมบัติเหมือง', 'Paquete de Cartas Búsqueda del Tesoro Minero', 'Набор карт «Охота за сокровищами в шахте»', 'Maden Hazine Avı Kart Paketi', 'Gói Thẻ Săn Kho Báu Hầm Mỏ', 'Pacchetto Carte Caccia al Tesoro Minerario', 'Paczka Kart Poszukiwanie Skarbów w Kopalni', 'حزمة بطاقات البحث عن الكنز في المنجم', '鉱山トレジャーハントカードパック', '광산 보물찾기 카드팩', '矿洞寻宝卡包'],
    ['EVENT', 'easter_fest_pack_core_decipher_desc', '打开即可获得两张3星以上"矿洞寻宝"游戏卡片。', 'Open to receive 2 "Mine Treasure Hunt" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Chasse au trésor minier" de 3 étoiles ou plus.', 'Öffnen, um 2 "Minenschatzsuche"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas de jogo "Caça ao Tesouro na Mina" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「礦洞尋寶」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu game "Berburu Harta Karun Tambang" bintang 3 atau lebih.', 'เปิดเพื่อรับการ์ดเกม "ล่าสมบัติเหมือง" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas de juego "Búsqueda del Tesoro Minero" de 3 estrellas o más.', 'Откройте, чтобы получить 2 игровые карты «Охота за сокровищами в шахте» от 3 звёзд.', 'Açarak 3 yıldız ve üzeri 2 "Maden Hazine Avı" oyun kartı alın.', 'Mở để nhận 2 thẻ game "Săn Kho Báu Hầm Mỏ" từ 3 sao trở lên.', 'Apri per ricevere 2 carte gioco "Caccia al Tesoro Minerario" da 3 stelle o superiori.', 'Otwórz, aby otrzymać 2 karty gry "Poszukiwanie Skarbów w Kopalni" o 3 gwiazdkach lub więcej.', 'افتح للحصول على بطاقتين من لعبة "البحث عن الكنز في المنجم" بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「鉱山トレジャーハント」ゲームカードを2枚獲得できます。', '열면 3성 이상 "광산 보물찾기" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"矿洞寻宝"游戏卡片。'],
    ['EVENT', 'easter_fest_pack_underground_name', '极速飞车卡包', 'Speed Racing Card Pack', 'Pack de cartes Course de vitesse', 'Hochgeschwindigkeitsrennen-Kartenpaket', 'Pacote de Cartas Corrida Veloz', '極速飛車卡包', 'Paket Kartu Balap Kecepatan', 'แพ็คการ์ดแข่งรถความเร็ว', 'Paquete de Cartas Carrera de Velocidad', 'Набор карт «Скоростные гонки»', 'Hız Yarışı Kart Paketi', 'Gói Thẻ Đua Xe Tốc Độ', 'Pacchetto Carte Corsa Veloce', 'Paczka Kart Wyścigi Prędkości', 'حزمة بطاقات سباق السرعة', 'スピードレーシングカードパック', '스피드 레이싱 카드팩', '极速飞车卡包'],
    ['EVENT', 'easter_fest_pack_underground_desc', '打开即可获得两张3星以上"极速飞车"游戏卡片。', 'Open to receive 2 "Speed Racing" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Course de vitesse" de 3 étoiles ou plus.', 'Öffnen, um 2 "Hochgeschwindigkeitsrennen"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas de jogo "Corrida Veloz" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「極速飛車」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu game "Balap Kecepatan" bintang 3 atau lebih.', 'เปิดเพื่อรับการ์ดเกม "แข่งรถความเร็ว" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas de juego "Carrera de Velocidad" de 3 estrellas o más.', 'Откройте, чтобы получить 2 игровые карты «Скоростные гонки» от 3 звёзд.', 'Açarak 3 yıldız ve üzeri 2 "Hız Yarışı" oyun kartı alın.', 'Mở để nhận 2 thẻ game "Đua Xe Tốc Độ" từ 3 sao trở lên.', 'Apri per ricevere 2 carte gioco "Corsa Veloce" da 3 stelle o superiori.', 'Otwórz, aby otrzymać 2 karty gry "Wyścigi Prędkości" o 3 gwiazdkach lub więcej.', 'افتح للحصول على بطاقتين من لعبة "سباق السرعة" بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「スピードレーシング」ゲームカードを2枚獲得できます。', '열면 3성 이상 "스피드 레이싱" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"极速飞车"游戏卡片。'],
    ['EVENT', 'easter_fest_pack_lucky_marble_name', '彩蛋大亨卡包', 'Easter Tycoon Card Pack', 'Pack de cartes Magnat de Pâques', 'Oster-Tycoon-Kartenpaket', 'Pacote de Cartas Magnata da Páscoa', '彩蛋大亨卡包', 'Paket Kartu Taipan Paskah', 'แพ็คการ์ดเศรษฐีอีสเตอร์', 'Paquete de Cartas Magnate de Pascua', 'Набор карт «Пасхальный магнат»', 'Paskalya Kodamanı Kart Paketi', 'Gói Thẻ Đại Gia Phục Sinh', 'Pacchetto Carte Magnate di Pasqua', 'Paczka Kart Wielkanocny Potentat', 'حزمة بطاقات قطب عيد الفصح', 'イースタータイクーンカードパック', '이스터 타이쿤 카드팩', '彩蛋大亨卡包'],
    ['EVENT', 'easter_fest_pack_lucky_marble_desc', '打开即可获得两张3星以上"彩蛋大亨"游戏卡片。', 'Open to receive 2 "Easter Tycoon" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Magnat de Pâques" de 3 étoiles ou plus.', 'Öffnen, um 2 "Oster-Tycoon"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas de jogo "Magnata da Páscoa" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「彩蛋大亨」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu game "Taipan Paskah" bintang 3 atau lebih.', 'เปิดเพื่อรับการ์ดเกม "เศรษฐีอีสเตอร์" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas de juego "Magnate de Pascua" de 3 estrellas o más.', 'Откройте, чтобы получить 2 игровые карты «Пасхальный магнат» от 3 звёзд.', 'Açarak 3 yıldız ve üzeri 2 "Paskalya Kodamanı" oyun kartı alın.', 'Mở để nhận 2 thẻ game "Đại Gia Phục Sinh" từ 3 sao trở lên.', 'Apri per ricevere 2 carte gioco "Magnate di Pasqua" da 3 stelle o superiori.', 'Otwórz, aby otrzymać 2 karty gry "Wielkanocny Potentat" o 3 gwiazdkach lub więcej.', 'افتح للحصول على بطاقتين من لعبة "قطب عيد الفصح" بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「イースタータイクーン」ゲームカードを2枚獲得できます。', '열면 3성 이상 "이스터 타이쿤" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"彩蛋大亨"游戏卡片。'],
    ['EVENT', 'easter_fest_pack_coin_pusher_name', '异族探秘卡包', 'Alien Exploration Card Pack', 'Pack de cartes Exploration extraterrestre', 'Alien-Erkundungs-Kartenpaket', 'Pacote de Cartas Exploração Alienígena', '異族探秘卡包', 'Paket Kartu Eksplorasi Alien', 'แพ็คการ์ดสำรวจเอเลี่ยน', 'Paquete de Cartas Exploración Alienígena', 'Набор карт «Исследование инопланетян»', 'Uzaylı Keşfi Kart Paketi', 'Gói Thẻ Khám Phá Người Ngoài Hành Tinh', 'Pacchetto Carte Esplorazione Aliena', 'Paczka Kart Eksploracja Obcych', 'حزمة بطاقات استكشاف الفضائيين', 'エイリアン探検カードパック', '외계인 탐험 카드팩', '异族探秘卡包'],
    ['EVENT', 'easter_fest_pack_coin_pusher_desc', '打开即可获得两张3星以上"异族探秘"游戏卡片。', 'Open to receive 2 "Alien Exploration" game cards of 3 stars or above.', 'Ouvrez pour recevoir 2 cartes de jeu "Exploration extraterrestre" de 3 étoiles ou plus.', 'Öffnen, um 2 "Alien-Erkundungs"-Spielkarten mit 3 Sternen oder mehr zu erhalten.', 'Abra para receber 2 cartas de jogo "Exploração Alienígena" de 3 estrelas ou mais.', '打開即可獲得兩張3星以上「異族探秘」遊戲卡片。', 'Buka untuk mendapatkan 2 kartu game "Eksplorasi Alien" bintang 3 atau lebih.', 'เปิดเพื่อรับการ์ดเกม "สำรวจเอเลี่ยน" 3 ดาวขึ้นไป 2 ใบ', 'Abre para recibir 2 cartas de juego "Exploración Alienígena" de 3 estrellas o más.', 'Откройте, чтобы получить 2 игровые карты «Исследование инопланетян» от 3 звёзд.', 'Açarak 3 yıldız ve üzeri 2 "Uzaylı Keşfi" oyun kartı alın.', 'Mở để nhận 2 thẻ game "Khám Phá Người Ngoài Hành Tinh" từ 3 sao trở lên.', 'Apri per ricevere 2 carte gioco "Esplorazione Aliena" da 3 stelle o superiori.', 'Otwórz, aby otrzymać 2 karty gry "Eksploracja Obcych" o 3 gwiazdkach lub więcej.', 'افتح للحصول على بطاقتين من لعبة "استكشاف الفضائيين" بـ 3 نجوم أو أكثر.', '開封すると3つ星以上の「エイリアン探検」ゲームカードを2枚獲得できます。', '열면 3성 이상 "외계인 탐험" 게임 카드 2장을 획득합니다.', '打开即可获得两张3星以上"异族探秘"游戏卡片。'],
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

    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID, fields='sheets.properties'
    ).execute()
    staging_sheet_id = None
    for s in spreadsheet['sheets']:
        if s['properties']['title'] == STAGING_SHEET:
            staging_sheet_id = s['properties']['sheetId']
            break

    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
    ).execute()
    existing = result.get('values', [])
    next_row = max(len(existing) + 1, 2)
    end_row = next_row + len(ROWS) - 1

    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{end_row}",
        valueInputOption='RAW',
        body={'values': ROWS},
    ).execute()

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

if __name__ == '__main__':
    main()
