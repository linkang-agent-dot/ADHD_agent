import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

# 1. Update task desc (row 130) - change from "累计进入{0}次高级关" to "累计获取{0}个高级弹珠"
# 2. Add rule localization

NEW_TASK_ROW = ["EVENT", "marble_gacha_advanced_stage_task",
    "累计获取{0}个高级弹珠",
    "Collect {0} Advanced Marbles in total",
    "Collecter {0} billes avanc\u00e9es au total",
    "Insgesamt {0} Fortgeschrittene Murmeln sammeln",
    "Coletar {0} Bolinhas Avan\u00e7adas no total",
    "累計獲取{0}個高級彈珠",
    "Kumpulkan {0} Kelereng Tingkat Lanjut",
    "\u0e2a\u0e30\u0e2a\u0e21\u0e25\u0e39\u0e01\u0e41\u0e01\u0e49\u0e27\u0e02\u0e31\u0e49\u0e19\u0e2a\u0e39\u0e07\u0e23\u0e27\u0e21 {0} \u0e25\u0e39\u0e01",
    "Recolectar {0} Canicas Avanzadas en total",
    "\u0421\u043e\u0431\u0440\u0430\u0442\u044c {0} \u041f\u0440\u043e\u0434\u0432\u0438\u043d\u0443\u0442\u044b\u0445 \u0448\u0430\u0440\u0438\u043a\u043e\u0432",
    "Toplam {0} Geli\u015fmi\u015f Misket toplay\u0131n",
    "Thu th\u1eadp {0} Bi Cao c\u1ea5p",
    "Colleziona {0} Biglie Avanzate in totale",
    "Zbierz \u0142\u0105cznie {0} Zaawansowanych Kulek",
    "\u0627\u062c\u0645\u0639 {0} \u0643\u0631\u0627\u062a \u0645\u062a\u0642\u062f\u0645\u0629",
    "\u4e0a\u7d1a\u30d3\u30fc\u7389\u3092\u5408\u8a08{0}\u500b\u7372\u5f97",
    "\uace0\uae09 \uad6c\uc2ac {0}\uac1c \ud68d\ub4dd",
    "累计获取{0}个高级弹珠"]

RULE_ROW = ["EVENT", "marble_gacha_advanced_rule",
    "累计获取高级弹珠，即可获取宝箱奖励",
    "Collect Advanced Marbles to get chest rewards",
    "Collectez des billes avanc\u00e9es pour obtenir des r\u00e9compenses de coffre",
    "Sammle Fortgeschrittene Murmeln, um Truhenbelohnungen zu erhalten",
    "Colete Bolinhas Avan\u00e7adas para obter recompensas de ba\u00fa",
    "累計獲取高級彈珠，即可獲取寶箱獎勵",
    "Kumpulkan Kelereng Tingkat Lanjut untuk mendapatkan hadiah peti",
    "\u0e2a\u0e30\u0e2a\u0e21\u0e25\u0e39\u0e01\u0e41\u0e01\u0e49\u0e27\u0e02\u0e31\u0e49\u0e19\u0e2a\u0e39\u0e07\u0e40\u0e1e\u0e37\u0e48\u0e2d\u0e23\u0e31\u0e1a\u0e23\u0e32\u0e07\u0e27\u0e31\u0e25\u0e01\u0e25\u0e48\u0e2d\u0e07\u0e2a\u0e21\u0e1a\u0e31\u0e15\u0e34",
    "Recolecta Canicas Avanzadas para obtener recompensas de cofre",
    "\u0421\u043e\u0431\u0438\u0440\u0430\u0439\u0442\u0435 \u041f\u0440\u043e\u0434\u0432\u0438\u043d\u0443\u0442\u044b\u0435 \u0448\u0430\u0440\u0438\u043a\u0438, \u0447\u0442\u043e\u0431\u044b \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u044c \u043d\u0430\u0433\u0440\u0430\u0434\u044b \u0438\u0437 \u0441\u0443\u043d\u0434\u0443\u043a\u0430",
    "Geli\u015fmi\u015f Misketler toplayarak sand\u0131k \u00f6d\u00fclleri kazan\u0131n",
    "Thu th\u1eadp Bi Cao c\u1ea5p \u0111\u1ec3 nh\u1eadn ph\u1ea7n th\u01b0\u1edfng r\u01b0\u01a1ng",
    "Colleziona Biglie Avanzate per ottenere ricompense dello scrigno",
    "Zbieraj Zaawansowane Kulki, aby zdoby\u0107 nagrody ze skrzyni",
    "\u0627\u062c\u0645\u0639 \u0627\u0644\u0643\u0631\u0627\u062a \u0627\u0644\u0645\u062a\u0642\u062f\u0645\u0629 \u0644\u0644\u062d\u0635\u0648\u0644 \u0639\u0644\u0649 \u0645\u0643\u0627\u0641\u0622\u062a \u0627\u0644\u0635\u0646\u062f\u0648\u0642",
    "\u4e0a\u7d1a\u30d3\u30fc\u7389\u3092\u96c6\u3081\u3066\u5b9d\u7bb1\u5831\u916c\u3092\u7372\u5f97",
    "\uace0\uae09 \uad6c\uc2ac\uc744 \ubaa8\uc544 \uc0c1\uc790 \ubcf4\uc0c1\uc744 \ud68d\ub4dd\ud558\uc138\uc694",
    "累计获取高级弹珠，即可获取宝箱奖励"]

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

    # Overwrite row 130 (task desc) with updated text
    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B130:U130",
        valueInputOption="RAW",
        body={"values": [NEW_TASK_ROW]},
    ).execute()
    print("Updated row 130: task desc -> 累计获取{0}个高级弹珠")

    # Append rule row
    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
    ).execute()
    existing = result.get("values", [])
    next_row = max(len(existing) + 1, 2)

    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{next_row}",
        valueInputOption="RAW",
        body={"values": [RULE_ROW]},
    ).execute()

    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": staging_sheet_id,
                    "startRowIndex": next_row - 1,
                    "endRowIndex": next_row,
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
    print(f"Added rule row at row {next_row}")

if __name__ == "__main__":
    main()
