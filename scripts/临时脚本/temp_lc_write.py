import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY'
STAGING_SHEET = 'AI翻译暂存'

# 修正后的翻译 [目标页签, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROWS = [
    ['EVENT', '2026pioneer_marble_gacha_title', '拓荒节弹珠GACHA', 'Pioneer Marble Gacha', 'Gacha Billes Pionnier', 'Pionier-Murmel-Gacha', 'Gacha de Bolas Pioneiro', '拓荒節彈珠GACHA', 'Gacha Kelereng Perintis', 'กาชาลูกแก้วไพโอเนียร์', 'Gacha Canicas Pionero', 'Гача Шарики Пионера', 'Öncü Bilye Gacha', 'Gacha Bi Tiên Phong', 'Gacha Biglie Pioniere', 'Gacha Kulki Pioniera', 'جاتشا كرات الرواد', 'パイオニアビー玉ガチャ', '개척자 구슬 가챠', '拓荒节弹珠GACHA'],
    ['EVENT', 'noumenon_gacha_welfare_title', '高级奖励关', 'PREMIUM BONUS', 'BONUS PREMIUM', 'PREMIUM-BONUS', 'BÔNUS PREMIUM', '高級獎勵關', 'BONUS PREMIUM', 'โบนัสพรีเมียม', 'BONIFICACIÓN PREMIUM', 'ПРЕМИУМ-БОНУС', 'PREMİUM BONUS', 'THƯỞNG CAO CẤP', 'BONUS PREMIUM', 'BONUS PREMIUM', 'مكافأة مميزة', 'プレミアムボーナス', '프리미엄 보너스', '高级奖励关'],
    ['EVENT', 'noumenon_gacha_welfare_desc', '恭喜触发高级奖励关！使用超级弹珠获取高级弹珠券', 'Congratulations! Use Super Marbles to earn Premium Marble Tokens', 'Félicitations ! Utilisez des Super Billes pour obtenir des Jetons Billes Premium', 'Herzlichen Glückwunsch! Verwende Super-Murmeln, um Premium-Murmel-Token zu erhalten', 'Parabéns! Use Super Bolas para ganhar Fichas de Bola Premium', '恭喜觸發高級獎勵關！使用超級彈珠獲取高級彈珠券', 'Selamat! Gunakan Kelereng Super untuk mendapatkan Token Kelereng Premium', 'ยินดีด้วย! ใช้ลูกแก้วซุปเปอร์เพื่อรับโทเค็นลูกแก้วพรีเมียม', '¡Felicidades! Usa Super Canicas para obtener Fichas de Canica Premium', 'Поздравляем! Используйте Супер-шарики для получения Премиум-жетонов шариков', 'Tebrikler! Premium Bilye Tokeni kazanmak için Süper Bilye kullanın', 'Chúc mừng! Dùng Bi Siêu Cấp để nhận Vé Bi Cao Cấp', 'Congratulazioni! Usa Super Biglie per ottenere Gettoni Biglia Premium', 'Gratulacje! Użyj Super Kulek, aby zdobyć Żetony Kulek Premium', 'تهانينا! استخدم الكرات الخارقة للحصول على رموز الكرات المميزة', 'おめでとう！スーパービー玉でプレミアムビー玉トークンを獲得', '축하합니다! 슈퍼 구슬로 프리미엄 구슬 토큰 획득', '恭喜触发高级奖励关！使用超级弹珠获取高级弹珠券'],
    ['EVENT', 'noumenon_gacha_high_exchange_title', '高级兑换', 'Premium Exchange', 'Échange Premium', 'Premium-Tausch', 'Troca Premium', '高級兌換', 'Tukar Premium', 'แลกพรีเมียม', 'Canje Premium', 'Премиум-обмен', 'Premium Takas', 'Đổi Cao Cấp', 'Scambio Premium', 'Wymiana Premium', 'التبادل المميز', 'プレミアム交換', '프리미엄 교환', '高级兑换'],
    ['EVENT', 'noumenon_gacha_high_exchange_desc', '使用高级弹珠券兑换奖励', 'Use Premium Marble Tokens to exchange for rewards', 'Utilisez des Jetons Billes Premium pour échanger des récompenses', 'Verwende Premium-Murmel-Token, um Belohnungen einzutauschen', 'Use Fichas de Bola Premium para trocar por recompensas', '使用高級彈珠券兌換獎勵', 'Gunakan Token Kelereng Premium untuk menukar hadiah', 'ใช้โทเค็นลูกแก้วพรีเมียมแลกรางวัล', 'Usa Fichas de Canica Premium para canjear recompensas', 'Используйте Премиум-жетоны шариков для обмена на награды', 'Ödüller için Premium Bilye Tokeni kullanın', 'Dùng Vé Bi Cao Cấp để đổi phần thưởng', 'Usa Gettoni Biglia Premium per scambiare premi', 'Użyj Żetonów Kulek Premium, aby wymienić na nagrody', 'استخدم رموز الكرات المميزة لاستبدال المكافآت', 'プレミアムビー玉トークンで報酬と交換', '프리미엄 구슬 토큰으로 보상 교환', '使用高级弹珠券兑换奖励'],
    ['EVENT', 'noumenon_gacha_normal_exchange_title', '普通兑换', 'Normal Exchange', 'Échange Normal', 'Normal-Tausch', 'Troca Normal', '普通兌換', 'Tukar Normal', 'แลกปกติ', 'Canje Normal', 'Обычный обмен', 'Normal Takas', 'Đổi Thường', 'Scambio Normale', 'Wymiana Normalna', 'التبادل العادي', '通常交換', '일반 교환', '普通兑换'],
    ['EVENT', 'noumenon_gacha_normal_exchange_desc', '使用普通弹珠券兑换奖励', 'Use Normal Marble Tokens to exchange for rewards', 'Utilisez des Jetons Billes Normaux pour échanger des récompenses', 'Verwende Normal-Murmel-Token, um Belohnungen einzutauschen', 'Use Fichas de Bola Normais para trocar por recompensas', '使用普通彈珠券兌換獎勵', 'Gunakan Token Kelereng Normal untuk menukar hadiah', 'ใช้โทเค็นลูกแก้วปกติแลกรางวัล', 'Usa Fichas de Canica Normales para canjear recompensas', 'Используйте Обычные жетоны шариков для обмена на награды', 'Ödüller için Normal Bilye Tokeni kullanın', 'Dùng Vé Bi Thường để đổi phần thưởng', 'Usa Gettoni Biglia Normali per scambiare premi', 'Użyj Żetonów Kulek Normalnych, aby wymienić na nagrody', 'استخدم رموز الكرات العادية لاستبدال المكافآت', '通常ビー玉トークンで報酬と交換', '일반 구슬 토큰으로 보상 교환', '使用普通弹珠券兑换奖励'],
    ['EVENT', '2026pioneer_marble_gacha_item_name_1', '高级弹珠券', 'Premium Marble Token', 'Jeton Bille Premium', 'Premium-Murmel-Token', 'Ficha de Bola Premium', '高級彈珠券', 'Token Kelereng Premium', 'โทเค็นลูกแก้วพรีเมียม', 'Ficha de Canica Premium', 'Премиум-жетон шарика', 'Premium Bilye Tokeni', 'Vé Bi Cao Cấp', 'Gettone Biglia Premium', 'Żeton Kulki Premium', 'رمز الكرة المميز', 'プレミアムビー玉トークン', '프리미엄 구슬 토큰', '高级弹珠券'],
    ['EVENT', '2026pioneer_marble_gacha_item_desc_1', '用于高级兑换', 'Used in Premium Exchange', "Utilisé dans l'Échange Premium", 'Wird im Premium-Tausch verwendet', 'Usado na Troca Premium', '用於高級兌換', 'Digunakan di Tukar Premium', 'ใช้ในแลกพรีเมียม', 'Usado en Canje Premium', 'Используется в Премиум-обмене', 'Premium Takasta kullanılır', 'Dùng tại Đổi Cao Cấp', 'Usato nello Scambio Premium', 'Używany w Wymianie Premium', 'يستخدم في التبادل المميز', 'プレミアム交換で使用', '프리미엄 교환에서 사용', '用于高级兑换'],
    ['EVENT', '2026pioneer_marble_gacha_item_name_2', '超级弹珠', 'Super Marble', 'Super Bille', 'Super-Murmel', 'Super Bola', '超級彈珠', 'Kelereng Super', 'ลูกแก้วซุปเปอร์', 'Super Canica', 'Супер-шарик', 'Süper Bilye', 'Bi Siêu Cấp', 'Super Biglia', 'Super Kulka', 'كرة خارقة', 'スーパービー玉', '슈퍼 구슬', '超级弹珠'],
    ['EVENT', '2026pioneer_marble_gacha_item_desc_2', '高级奖励关专用弹珠', 'Marble for Premium Bonus', 'Bille pour Bonus Premium', 'Murmel für Premium-Bonus', 'Bola para Bônus Premium', '高級獎勵關專用彈珠', 'Kelereng untuk Bonus Premium', 'ลูกแก้วสำหรับโบนัสพรีเมียม', 'Canica para Bonificación Premium', 'Шарик для Премиум-бонуса', 'Premium Bonus için bilye', 'Bi cho Thưởng Cao Cấp', 'Biglia per Bonus Premium', 'Kulka na Bonus Premium', 'كرة لمكافأة مميزة', 'プレミアムボーナス用ビー玉', '프리미엄 보너스용 구슬', '高级奖励关专用弹珠'],
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
    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID, fields='sheets.properties'
    ).execute()
    staging_sheet_id = None
    for s in spreadsheet['sheets']:
        if s['properties']['title'] == STAGING_SHEET:
            staging_sheet_id = s['properties']['sheetId']
            break

    # 先清理之前写入的数据（行101-120）
    sheets_api.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!A101:U120"
    ).execute()
    print('Cleared old data in rows 101-120')

    # 定位追加起始行
    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
    ).execute()
    existing = result.get('values', [])
    next_row = max(len(existing) + 1, 2)
    end_row = next_row + len(ROWS) - 1

    # 写入数据到 B~U 列（A 列留给 checkbox）
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

if __name__ == '__main__':
    main()
