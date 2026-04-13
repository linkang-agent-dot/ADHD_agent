import json
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"
TARGET_TAB = "minigame"

# [目标页签, ID, cn, en, fr, de, po, zh(繁), id(印尼), th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROWS = [
    [TARGET_TAB, "trigger_adv_chest_monster",
     "触发高级宝箱怪", "TRIGGER ADVANCED CHEST MONSTER",
     "Déclencher le Monstre Coffre Avancé", "Fortgeschrittenes Truhenmonster Auslösen",
     "Ativar Monstro de Baú Avançado", "觸發高級寶箱怪",
     "Aktifkan Monster Peti Canggih", "เปิดใช้งานมอนสเตอร์กล่องขั้นสูง",
     "Activar Monstruo de Cofre Avanzado", "Активировать улучшенного монстра сундука",
     "Gelişmiş Sandık Canavarını Etkinleştir", "Kích Hoạt Quái Vật Rương Cấp Cao",
     "Attiva il Mostro Forziere Avanzato", "Aktywuj Potwora Zaawansowanej Skrzyni",
     "تفعيل وحش الصندوق المتقدم", "上級宝箱モンスターを発動する",
     "고급 보물상자 몬스터 발동", "触发高级宝箱怪"],

    [TARGET_TAB, "server_progress",
     "全服进度", "SERVER-WIDE PROGRESS",
     "Progression du Serveur", "Serverweiter Fortschritt",
     "Progresso do Servidor", "全服進度",
     "Progres Server", "ความคืบหน้าทั้งเซิร์ฟเวอร์",
     "Progreso del Servidor", "Прогресс сервера",
     "Sunucu Genelinde İlerleme", "Tiến Độ Toàn Server",
     "Progresso del Server", "Postęp Serwera",
     "تقدم السيرفر", "サーバー全体の進捗",
     "서버 전체 진행도", "全服进度"],

    [TARGET_TAB, "server_adv_chest_monster",
     "全服高级宝箱怪", "SERVER ADVANCED CHEST MONSTER",
     "Monstre Coffre Avancé du Serveur", "Server-Fortgeschrittenes-Truhenmonster",
     "Monstro de Baú Avançado do Servidor", "全服高級寶箱怪",
     "Monster Peti Canggih Server", "มอนสเตอร์กล่องขั้นสูงทั้งเซิร์ฟเวอร์",
     "Monstruo de Cofre Avanzado del Servidor", "Улучшенный монстр сундука всего сервера",
     "Sunucu Gelişmiş Sandık Canavarı", "Quái Vật Rương Cấp Cao Toàn Server",
     "Mostro Forziere Avanzato del Server", "Potwór Zaawansowanej Skrzyni Serwera",
     "وحش الصندوق المتقدم للسيرفر", "サーバー上級宝箱モンスター",
     "서버 고급 보물상자 몬스터", "全服高级宝箱怪"],

    [TARGET_TAB, "clown_adv_treasure_chest",
     "小丑高级宝箱", "CLOWN ADVANCED TREASURE CHEST",
     "Coffre Avancé du Clown", "Clown Fortgeschrittene Schatztruhe",
     "Baú do Tesouro Avançado do Palhaço", "小丑高級寶箱",
     "Peti Harta Canggih Badut", "หีบสมบัติขั้นสูงของตัวตลก",
     "Cofre del Tesoro Avanzado del Payaso", "Продвинутый сундук сокровищ клоуна",
     "Palyaço Gelişmiş Hazine Sandığı", "Rương Báu Cấp Cao Của Hề",
     "Forziere Avanzato del Clown", "Zaawansowana Skrzynia Skarbów Klauna",
     "صندوق كنز متقدم للمهرج", "ピエロ上級宝箱",
     "광대 고급 보물상자", "小丑高级宝箱"],

    [TARGET_TAB, "server_attacking",
     "全服进攻中！", "SERVER UNDER ATTACK!",
     "Serveur Sous Attaque !", "Server Im Angriff!",
     "Servidor Sob Ataque!", "全服進攻中！",
     "Server Diserang!", "ทั้งเซิร์ฟเวอร์กำลังถูกโจมตี!",
     "¡Servidor Bajo Ataque!", "Весь сервер атакуется!",
     "Sunucu Saldırı Altında!", "Toàn Server Đang Bị Tấn Công!",
     "Server Sotto Attacco!", "Serwer Pod Atakiem!",
     "السيرفر تحت الهجوم!", "サーバー全体攻撃中！",
     "서버 전체 공격 중!", "全服进攻中！"],

    [TARGET_TAB, "adv_monster_points_needed",
     "离高级宝箱怪出现还差{0}分", "{0} points needed for Advanced Chest Monster",
     "Il faut encore {0} points pour l'apparition du Monstre Coffre Avancé",
     "Noch {0} Punkte bis zum Erscheinen des Fortgeschrittenen Truhenmonsters",
     "Faltam {0} pontos para o Monstro de Baú Avançado aparecer",
     "離高級寶箱怪出現還差{0}分",
     "Masih kurang {0} poin untuk Monster Peti Canggih muncul",
     "ต้องการอีก {0} แต้มเพื่อให้มอนสเตอร์กล่องขั้นสูงปรากฏตัว",
     "Faltan {0} puntos para que aparezca el Monstruo de Cofre Avanzado",
     "Ещё {0} очков до появления улучшенного монстра сундука",
     "Gelişmiş Sandık Canavarı için {0} puan daha gerekiyor",
     "Cần thêm {0} điểm để Quái Vật Rương Cấp Cao xuất hiện",
     "Mancano {0} punti per l'apparizione del Mostro Forziere Avanzato",
     "Brakuje {0} punktów do pojawienia się Potwora Zaawansowanej Skrzyni",
     "تحتاج إلى {0} نقطة أخرى لظهور وحش الصندوق المتقدم",
     "上級宝箱モンスター出現まであと{0}ポイント",
     "고급 보물상자 몬스터 출현까지 {0}점 부족", "离高级宝箱怪出现还差{0}分"],

    [TARGET_TAB, "kill_reward",
     "击杀奖励", "KILL REWARDS",
     "Récompenses de Victoire", "Abschuss-Belohnungen",
     "Recompensas por Abate", "擊殺獎勵",
     "Hadiah Pembunuhan", "รางวัลการสังหาร",
     "Recompensas por Eliminación", "Награда за убийство",
     "Öldürme Ödülleri", "Phần Thưởng Tiêu Diệt",
     "Ricompense per Eliminazione", "Nagrody za Eliminację",
     "مكافآت القتل", "撃破報酬",
     "처치 보상", "击杀奖励"],

    [TARGET_TAB, "killed_by_player",
     "击杀玩家：{0}", "Defeated by: {0}",
     "Éliminé par : {0}", "Besiegt von: {0}",
     "Derrotado por: {0}", "擊殺玩家：{0}",
     "Dikalahkan oleh: {0}", "ถูกกำจัดโดย: {0}",
     "Derrotado por: {0}", "Побеждён игроком: {0}",
     "Öldüren Oyuncu: {0}", "Bị Tiêu Diệt Bởi: {0}",
     "Sconfitto da: {0}", "Pokonany przez: {0}",
     "تم القضاء عليه بواسطة: {0}", "撃破プレイヤー：{0}",
     "처치 플레이어: {0}", "击杀玩家：{0}"],

    [TARGET_TAB, "already_killed",
     "已击杀", "DEFEATED",
     "Vaincu", "Besiegt",
     "Derrotado", "已擊殺",
     "Dikalahkan", "ถูกสังหารแล้ว",
     "Derrotado", "Побеждён",
     "Yenildi", "Đã Bị Tiêu Diệt",
     "Sconfitto", "Pokonany",
     "مهزوم", "撃破済み",
     "처치됨", "已击杀"],

    [TARGET_TAB, "congrats_supreme_chest",
     "恭喜获得至尊宝箱", "YOU GOT THE SUPREME CHEST!",
     "Vous Avez Obtenu le Coffre Suprême !", "Du hast die Erhabene Schatztruhe erhalten!",
     "Você Obteve o Baú Supremo!", "恭喜獲得至尊寶箱",
     "Selamat! Kamu Mendapatkan Peti Agung!", "ยินดีด้วย! คุณได้รับหีบสูงสุดแล้ว!",
     "¡Felicidades! ¡Obtuviste el Cofre Supremo!", "Поздравляем! Вы получили Верховный сундук!",
     "Tebrikler! Yüce Sandığı Kazandın!", "Chúc Mừng! Bạn Nhận Được Rương Tối Thượng!",
     "Congratulazioni! Hai Ottenuto il Forziere Supremo!", "Gratulacje! Otrzymałeś Najwyższą Skrzynię!",
     "تهانينا! حصلت على الصندوق الأعلى!", "至尊宝箱を獲得しました！",
     "최고 보물상자를 획득했습니다!", "恭喜获得至尊宝箱"],

    [TARGET_TAB, "supreme_prize_pool",
     "至尊奖池", "SUPREME PRIZE POOL",
     "Réserve de Prix Suprême", "Erhabener Preispool",
     "Pool de Prêmios Supremo", "至尊獎池",
     "Kolam Hadiah Agung", "สระรางวัลสูงสุด",
     "Fondo de Premios Supremo", "Верховный призовой фонд",
     "Yüce Ödül Havuzu", "Bể Phần Thưởng Tối Thượng",
     "Pool Premi Supremo", "Najwyższa Pula Nagród",
     "مجموعة الجوائز العليا", "至尊賞品プール",
     "최고 상품 풀", "至尊奖池"],

    [TARGET_TAB, "congrats_obtained",
     "恭喜获得！", "YOU GOT IT!",
     "Vous l'Avez Obtenu !", "Du hast es!",
     "Você Conseguiu!", "恭喜獲得！",
     "Selamat Mendapatkan!", "ยินดีด้วย ได้รับแล้ว!",
     "¡Lo Conseguiste!", "Поздравляем! Получено!",
     "Tebrikler!", "Chúc Mừng! Đã Nhận!",
     "Ce l'Hai Fatta!", "Gratulacje! Zdobyłeś!",
     "تهانينا! حصلت عليه!", "おめでとうございます！",
     "획득했습니다!", "恭喜获得！"],

    [TARGET_TAB, "avg_score_per_player",
     "人均分：{0}", "Avg. Score: {0}",
     "Score Moyen : {0}", "Durchschnittspunkte: {0}",
     "Pontuação Média: {0}", "人均分：{0}",
     "Skor Rata-Rata: {0}", "คะแนนเฉลี่ย: {0}",
     "Puntuación Media: {0}", "Средний счёт: {0}",
     "Ortalama Puan: {0}", "Điểm Trung Bình: {0}",
     "Punteggio Medio: {0}", "Średni wynik: {0}",
     "متوسط النقاط: {0}", "平均スコア：{0}",
     "평균 점수: {0}", "人均分：{0}"],

    [TARGET_TAB, "normal_reward",
     "普通奖励", "NORMAL REWARDS",
     "Récompenses Normales", "Normale Belohnungen",
     "Recompensas Normais", "普通獎勵",
     "Hadiah Biasa", "รางวัลปกติ",
     "Recompensas Normales", "Обычные награды",
     "Normal Ödüller", "Phần Thưởng Thông Thường",
     "Ricompense Normali", "Zwykłe Nagrody",
     "مكافآت عادية", "通常報酬",
     "일반 보상", "普通奖励"],

    [TARGET_TAB, "already_escape",
     "已逃跑", "ESCAPED",
     "Échappé", "Entkommen",
     "Escapou", "已逃跑",
     "Melarikan Diri", "หนีไปแล้ว",
     "Escapado", "Сбежал",
     "Kaçtı", "Đã Bỏ Trốn",
     "Fuggito", "Uciekł",
     "هرب", "逃走済み",
     "도망감", "已逃跑"],
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

    if staging_sheet_id is None:
        print(f"ERROR: 找不到页签 '{STAGING_SHEET}'")
        return

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

    print(f"✅ 写入完成！共 {len(ROWS)} 条，写入行 {next_row}-{end_row}")
    print(f"请前往「AI翻译暂存」页签勾选后，菜单「本地化工具 > 提交选中行」提交到 {TARGET_TAB}")


if __name__ == "__main__":
    main()
