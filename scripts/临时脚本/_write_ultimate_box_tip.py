import json, subprocess, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding="utf-8")

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

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

# [target_tab, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROW = [
    "EVENT",
    "coin_pusher_ultimate_box_received_tip",
    "已经获取的奖励在本轮将不再重复获取，直到下轮奖励重置。",
    "Acquired rewards will not drop again this round until rewards reset for the next round.",
    "Les récompenses déjà obtenues ne réapparaîtront plus ce tour-ci jusqu'à la réinitialisation des récompenses au tour suivant.",
    "Bereits erhaltene Belohnungen erscheinen in dieser Runde nicht erneut, bis die Belohnungen für die nächste Runde zurückgesetzt werden.",
    "Recompensas já obtidas não aparecerão novamente nesta rodada até que as recompensas sejam resetadas na próxima rodada.",
    "已經獲取的獎勵在本輪將不再重複獲取，直到下輪獎勵重置。",
    "Hadiah yang sudah diperoleh tidak akan muncul lagi di ronde ini hingga hadiah direset di ronde berikutnya.",
    "รางวัลที่ได้รับแล้วจะไม่ปรากฏอีกในรอบนี้ จนกว่ารางวัลจะถูกรีเซ็ตในรอบถัดไป",
    "Las recompensas ya obtenidas no volverán a aparecer en esta ronda hasta que se reinicien las recompensas para la siguiente ronda.",
    "Уже полученные награды не появятся снова в этом раунде, пока награды не сбросятся в следующем раунде.",
    "Bu turda alınmış ödüller, bir sonraki tur için ödüller sıfırlanana kadar tekrar düşmeyecek.",
    "Phần thưởng đã nhận sẽ không xuất hiện lại trong vòng này cho đến khi phần thưởng được đặt lại ở vòng tiếp theo.",
    "Le ricompense già ottenute non ricompariranno in questo round fino al reset delle ricompense per il round successivo.",
    "Już zdobyte nagrody nie pojawią się ponownie w tej rundzie, dopóki nagrody nie zostaną zresetowane w następnej rundzie.",
    "المكافآت المكتسبة بالفعل لن تظهر مرة أخرى في هذه الجولة حتى يتم إعادة تعيين المكافآت للجولة التالية.",
    "獲得済みの報酬は、次のラウンドで報酬がリセットされるまで、このラウンドでは再出現しません。",
    "이미 획득한 보상은 다음 라운드에서 보상이 재설정되기 전까지 이번 라운드에서 다시 나타나지 않습니다.",
    "已经获取的奖励在本轮将不再重复获取，直到下轮奖励重置。",
]

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

    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{next_row}",
        valueInputOption="RAW",
        body={"values": [ROW]},
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

    print(f"✅ Wrote staging row {next_row}: coin_pusher_ultimate_box_received_tip")

if __name__ == "__main__":
    main()
