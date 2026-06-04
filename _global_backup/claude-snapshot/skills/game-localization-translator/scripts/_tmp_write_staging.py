import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

ROWS = [
    ["EVENT", "marble_gacha_advanced_chest_name",
     "弹珠高级宝箱",
     "Advanced Marble Chest",
     "Coffre de billes avanc\u00e9",
     "Fortgeschrittene Murmeltruhe",
     "Ba\u00fa de Bolinhas Avan\u00e7ado",
     "彈珠高級寶箱",
     "Peti Kelereng Tingkat Lanjut",
     "\u0e01\u0e25\u0e48\u0e2d\u0e07\u0e2a\u0e21\u0e1a\u0e31\u0e15\u0e34\u0e25\u0e39\u0e01\u0e41\u0e01\u0e49\u0e27\u0e02\u0e31\u0e49\u0e19\u0e2a\u0e39\u0e07",
     "Cofre de Canicas Avanzado",
     "\u041f\u0440\u043e\u0434\u0432\u0438\u043d\u0443\u0442\u044b\u0439 \u0441\u0443\u043d\u0434\u0443\u043a \u0441 \u0448\u0430\u0440\u0438\u043a\u0430\u043c\u0438",
     "Geli\u015fmi\u015f Misket Sand\u0131\u011f\u0131",
     "R\u01b0\u01a1ng Bi Cao C\u1ea5p",
     "Cassa Biglie Avanzata",
     "Zaawansowana Skrzynia z Kulkami",
     "\u0635\u0646\u062f\u0648\u0642 \u0627\u0644\u0643\u0631\u0627\u062a \u0627\u0644\u0645\u062a\u0642\u062f\u0645",
     "\u4e0a\u7d1a\u30d3\u30fc\u7389\u30c1\u30a7\u30b9\u30c8",
     "\uace0\uae09 \uad6c\uc2ac \uc0c1\uc790",
     "弹珠高级宝箱"],
    ["EVENT", "marble_gacha_advanced_chest_desc",
     "完成高级关挑战后获得的里程碑奖励，有机会获得珍稀皮肤和高级兑换券",
     "Milestone rewards earned from Advanced Stage challenges. Chance to obtain rare skins and Advanced Exchange Tickets.",
     "R\u00e9compenses de jalon obtenues lors des d\u00e9fis du Stage Avanc\u00e9. Chance d\u2019obtenir des skins rares et des Tickets d\u2019\u00c9change Avanc\u00e9s.",
     "Meilenstein-Belohnungen aus Herausforderungen der Fortgeschrittenen Stufe. Chance auf seltene Skins und Fortgeschrittene Tausch-Tickets.",
     "Recompensas de marco obtidas nos desafios do Est\u00e1gio Avan\u00e7ado. Chance de obter skins raras e Tickets de Troca Avan\u00e7ados.",
     "完成高級關挑戰後獲得的里程碑獎勵，有機會獲得珍稀皮膚和高級兌換券",
     "Hadiah tonggak pencapaian dari tantangan Tahap Lanjutan. Kesempatan mendapatkan skin langka dan Tiket Penukaran Lanjutan.",
     "\u0e23\u0e32\u0e07\u0e27\u0e31\u0e25\u0e40\u0e1b\u0e49\u0e32\u0e2b\u0e21\u0e32\u0e22\u0e08\u0e32\u0e01\u0e01\u0e32\u0e23\u0e17\u0e49\u0e32\u0e17\u0e32\u0e22\u0e14\u0e48\u0e32\u0e19\u0e02\u0e31\u0e49\u0e19\u0e2a\u0e39\u0e07 \u0e21\u0e35\u0e42\u0e2d\u0e01\u0e32\u0e2a\u0e44\u0e14\u0e49\u0e23\u0e31\u0e1a\u0e2a\u0e01\u0e34\u0e19\u0e2b\u0e32\u0e22\u0e32\u0e01\u0e41\u0e25\u0e30\u0e15\u0e31\u0e4b\u0e27\u0e41\u0e25\u0e01\u0e40\u0e1b\u0e25\u0e35\u0e48\u0e22\u0e19\u0e02\u0e31\u0e49\u0e19\u0e2a\u0e39\u0e07",
     "Recompensas de hito obtenidas en los desaf\u00edos del Escenario Avanzado. Posibilidad de obtener skins raros y Tickets de Intercambio Avanzados.",
     "\u041d\u0430\u0433\u0440\u0430\u0434\u044b \u0437\u0430 \u0434\u043e\u0441\u0442\u0438\u0436\u0435\u043d\u0438\u0435 \u044d\u0442\u0430\u043f\u043e\u0432 \u0432 \u0438\u0441\u043f\u044b\u0442\u0430\u043d\u0438\u044f\u0445 \u041f\u0440\u043e\u0434\u0432\u0438\u043d\u0443\u0442\u043e\u0433\u043e \u044d\u0442\u0430\u043f\u0430. \u0428\u0430\u043d\u0441 \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c \u0440\u0435\u0434\u043a\u0438\u0435 \u0441\u043a\u0438\u043d\u044b \u0438 \u041f\u0440\u043e\u0434\u0432\u0438\u043d\u0443\u0442\u044b\u0435 \u043e\u0431\u043c\u0435\u043d\u043d\u044b\u0435 \u0431\u0438\u043b\u0435\u0442\u044b.",
     "Geli\u015fmi\u015f A\u015fama meydan okumalar\u0131ndan kazan\u0131lan kilometre ta\u015f\u0131 \u00f6d\u00fclleri. Nadir kost\u00fcmler ve Geli\u015fmi\u015f Takas Biletleri kazanma \u015fans\u0131.",
     "Ph\u1ea7n th\u01b0\u1edfng c\u1ed9t m\u1ed1c t\u1eeb th\u1eed th\u00e1ch Giai \u0111o\u1ea1n Cao c\u1ea5p. C\u01a1 h\u1ed9i nh\u1eadn \u0111\u01b0\u1ee3c trang ph\u1ee5c hi\u1ebfm v\u00e0 V\u00e9 \u0110\u1ed5i Cao c\u1ea5p.",
     "Ricompense traguardo ottenute dalle sfide dello Stadio Avanzato. Possibilit\u00e0 di ottenere skin rare e Biglietti di Scambio Avanzati.",
     "Nagrody za kamienie milowe zdobyte w wyzwaniach Zaawansowanego Etapu. Szansa na zdobycie rzadkich skin\u00f3w i Zaawansowanych Bilet\u00f3w Wymiany.",
     "\u0645\u0643\u0627\u0641\u0622\u062a \u0627\u0644\u0645\u0631\u0627\u062d\u0644 \u0627\u0644\u0645\u0643\u062a\u0633\u0628\u0629 \u0645\u0646 \u062a\u062d\u062f\u064a\u0627\u062a \u0627\u0644\u0645\u0631\u062d\u0644\u0629 \u0627\u0644\u0645\u062a\u0642\u062f\u0645\u0629. \u0641\u0631\u0635\u0629 \u0644\u0644\u062d\u0635\u0648\u0644 \u0639\u0644\u0649 \u0623\u0634\u0643\u0627\u0644 \u0646\u0627\u062f\u0631\u0629 \u0648\u062a\u0630\u0627\u0643\u0631 \u0627\u0633\u062a\u0628\u062f\u0627\u0644 \u0645\u062a\u0642\u062f\u0645\u0629.",
     "\u4e0a\u7d1a\u30b9\u30c6\u30fc\u30b8\u30c1\u30e3\u30ec\u30f3\u30b8\u3067\u7372\u5f97\u3059\u308b\u30de\u30a4\u30eb\u30b9\u30c8\u30fc\u30f3\u5831\u916c\u3002\u30ec\u30a2\u30b9\u30ad\u30f3\u3084\u4e0a\u7d1a\u4ea4\u63db\u30c1\u30b1\u30c3\u30c8\u3092\u7372\u5f97\u3059\u308b\u30c1\u30e3\u30f3\u30b9\u304c\u3042\u308a\u307e\u3059\u3002",
     "\uace0\uae09 \uc2a4\ud14c\uc774\uc9c0 \ub3c4\uc804\uc5d0\uc11c \ud68d\ub4dd\ud55c \ub9c8\uc77c\uc2a4\ud1a4 \ubcf4\uc0c1. \ud76c\uadc0 \uc2a4\ud0a8\uacfc \uace0\uae09 \uad50\ud658 \ud2f0\ucf13\uc744 \ud68d\ub4dd\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
     "完成高级关挑战后获得的里程碑奖励，有机会获得珍稀皮肤和高级兑换券"],
    ["EVENT", "marble_gacha_advanced_stage_task",
     "累计进入{0}次高级关",
     "Enter Advanced Stage {0} times in total",
     "Entrer dans le Stage Avanc\u00e9 {0} fois au total",
     "Insgesamt {0} Mal die Fortgeschrittene Stufe betreten",
     "Entrar no Est\u00e1gio Avan\u00e7ado {0} vezes no total",
     "累計進入{0}次高級關",
     "Masuk Tahap Lanjutan sebanyak {0} kali",
     "\u0e40\u0e02\u0e49\u0e32\u0e14\u0e48\u0e32\u0e19\u0e02\u0e31\u0e49\u0e19\u0e2a\u0e39\u0e07\u0e23\u0e27\u0e21 {0} \u0e04\u0e23\u0e31\u0e49\u0e07",
     "Entrar al Escenario Avanzado {0} veces en total",
     "\u0412\u043e\u0439\u0442\u0438 \u0432 \u041f\u0440\u043e\u0434\u0432\u0438\u043d\u0443\u0442\u044b\u0439 \u044d\u0442\u0430\u043f {0} \u0440\u0430\u0437",
     "Geli\u015fmi\u015f A\u015famaya toplam {0} kez girin",
     "V\u00e0o Giai \u0111o\u1ea1n Cao c\u1ea5p t\u1ed5ng c\u1ed9ng {0} l\u1ea7n",
     "Entrare nello Stadio Avanzato {0} volte in totale",
     "Wejd\u017a do Zaawansowanego Etapu \u0142\u0105cznie {0} razy",
     "\u0627\u062f\u062e\u0644 \u0627\u0644\u0645\u0631\u062d\u0644\u0629 \u0627\u0644\u0645\u062a\u0642\u062f\u0645\u0629 {0} \u0645\u0631\u0627\u062a \u0625\u062c\u0645\u0627\u0644\u0627\u064b",
     "\u4e0a\u7d1a\u30b9\u30c6\u30fc\u30b8\u306b\u5408\u8a08{0}\u56de\u5165\u308b",
     "\uace0\uae09 \uc2a4\ud14c\uc774\uc9c0\uc5d0 \ucd1d {0}\ud68c \uc785\uc7a5",
     "累计进入{0}次高级关"],
]

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

def main():
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    staging_sheet_id = None
    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == STAGING_SHEET:
            staging_sheet_id = s["properties"]["sheetId"]
            break

    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
    ).execute()
    existing = result.get("values", [])
    next_row = max(len(existing) + 1, 2)
    end_row = next_row + len(ROWS) - 1

    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{end_row}",
        valueInputOption="RAW",
        body={"values": ROWS},
    ).execute()

    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": staging_sheet_id,
                    "startRowIndex": next_row - 1,
                    "endRowIndex": end_row,
                    "startColumnIndex": 0, "endColumnIndex": 1,
                },
                "cell": {
                    "dataValidation": {"condition": {"type": "BOOLEAN"}, "strict": True},
                    "userEnteredValue": {"boolValue": False},
                },
                "fields": "dataValidation,userEnteredValue",
            }
        }]},
    ).execute()
    print(f"Done! Wrote {len(ROWS)} rows (row {next_row}-{end_row})")

if __name__ == "__main__":
    main()
