import json, subprocess, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding="utf-8")

X2_I18N = "1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg"
STAGING_TAB = "AI翻译页签"

def get_sheets_api():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    creds = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=creds).spreadsheets()

# [target_tab, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROW = [
    "EVENT",
    "wonder_event_remind_mes",
    "{0}活动开启了！快去开启毁灭劫匪团伙挑战，一起保卫帝国吧！",
    "Hey {0}, an event has started! Go challenge the Doom Giganto and protect the Empire together!",
    "Salut {0}, un événement a commencé ! Va défier le Giganto de la Fatalité et protégeons l'Empire ensemble !",
    "Hey {0}, ein Ereignis hat begonnen! Fordere den Unheil-Giganto heraus und beschütze gemeinsam das Imperium!",
    "Olá {0}, um evento começou! Vá desafiar o Doom Giganto e proteja o Império juntos!",
    "{0}活動開啟了！快去開啟毀滅劫匪團夥挑戰，一起保衛帝國吧！",
    "Hai {0}, sebuah event telah dimulai! Tantang Doom Giganto dan lindungi Kekaisaran bersama!",
    "เฮ้ {0} อีเวนต์เริ่มขึ้นแล้ว! ไปท้าทาย Doom Giganto และปกป้องจักรวรรดิด้วยกัน!",
    "¡Hola {0}, ha comenzado un evento! ¡Ve a desafiar al Doom Giganto y protejamos el Imperio juntos!",
    "Привет, {0}! Событие началось! Бросьте вызов Doom Giganto и вместе защитим Империю!",
    "Selam {0}, bir etkinlik başladı! Doom Giganto'ya meydan oku ve İmparatorluğu birlikte koruyalım!",
    "Chào {0}, một sự kiện đã bắt đầu! Hãy thách đấu Doom Giganto và cùng bảo vệ Đế Chế!",
    "Ehi {0}, è iniziato un evento! Vai a sfidare il Doom Giganto e proteggi l'Impero insieme!",
    "Hej {0}, rozpoczęło się wydarzenie! Wyzwij Doom Giganto i wspólnie chrońmy Imperium!",
    "مرحباً {0}، بدأ حدث! اذهب لتحدي Doom Giganto ولنحمي الإمبراطورية معاً!",
    "{0}さん、イベントが始まりました！ドゥームギガントに挑戦し、共に帝国を守りましょう！",
    "{0}님, 이벤트가 시작되었습니다! 둠 기간토에 도전하여 함께 제국을 지킵시다!",
    "{0}活动开启了！快去开启毁灭劫匪团伙挑战，一起保卫帝国吧！",
]

def main():
    sheets_api = get_sheets_api()

    # Append (staging may be near full)
    result = sheets_api.values().append(
        spreadsheetId=X2_I18N,
        range=f"'{STAGING_TAB}'!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [ROW]},
    ).execute()

    updated = result.get("updates", {})
    print(f"✅ Appended to {updated.get('updatedRange','?')}")
    print(f"   Key: wonder_event_remind_mes")
    print(f"   cn: {ROW[2]}")
    print(f"   en: {ROW[3]}")

if __name__ == "__main__":
    main()
