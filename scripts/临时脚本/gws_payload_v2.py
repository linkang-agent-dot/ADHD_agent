import subprocess
import json
import sys

# notice_2 的值（从行 2746 读取到的结果）
notice2_values = [
    "在限定时间内派1支护卫队攻击毁灭劫匪团伙。造成的伤害越高，获得的积分越多。",
    "Send 1 troop to attack the Doom Giganto before the time is up. The more damage you deal, the higher the points earned.",
    "Envoyez 1 troupe pour attaquer le Giganto de Doom avant la fin du temps. Plus vous infligez de dégâts, plus vous gagnez de points.",
    "Entsende 1 Truppe, um den Doom Giganto anzugreifen, bevor die Zeit abläuft. Je mehr Schaden du verursachst, desto mehr Punkte erhältst du.",
    "Envie 1 tropa para atacar o Giganto da Perdição antes que o tempo acabe. Quanto mais dano você causar, mais pontos irá ganhar.",
    "在限定時間內派1支護衛隊攻擊毀滅劫匪團伙。造成的傷害越高，獲得的積分越多。",
    "Dalam waktu terbatas, kirim satu tim pengawal untuk menyerang dan menghancurkan kelompok Perampok. Semakin besar kerusakan yang ditimbulkan, semakin banyak poin yang didapatkan.",
    "ส่งกองกำลัง 1 หน่วยเพื่อโจมตีกิกันโตแห่งหายนะก่อนหมดเวลา ยิ่งสร้างความเสียหายได้มาก คะแนนที่ได้รับก็จะยิ่งสูงขึ้น",
    "Envía 1 tropa para atacar al Doom Giganto antes de que se acabe el tiempo. Cuanto más daño causes, más puntos ganarás.",
    "Отправьте 1 отряд для атаки Гиганто Судного дня до окончания времени. Чем больше урона вы нанесете, тем больше очков заработаете.",
    "Süre dolmadan önce Doom Giganto'ya saldırmak için 1 birlik gönderin. Ne kadar çok hasar verirseniz, o kadar fazla puan kazanırsınız.",
    "Điều động 1 quân để tấn công Doom Giganto trước khi hết thời gian. Gây càng nhiều sát thương, điểm nhận được càng cao.",
    "Invia 1 truppa ad attaccare il Giganto del Destino prima che il tempo scada. Più danni infliggi, più punti ottieni.",
    "Wyślij 1 oddział, aby zaatakować Giganto Zagłady przed upływem czasu. Im więcej obrażeń zadasz, tym więcej punktów zdobędziesz.",
    "أرسل وحدة واحدة لمهاجمة جيغانتو دوم قبل انتهاء الوقت. كلما سببت ضرراً أكبر، زادت النقاط التي تكسبها.",
    "時間内にドゥーム・ギガントを攻撃するために部隊を1つ派遣しましょう。与えるダメージが多いほど、獲得できるポイントも高くなります。",
    "시간이 끝나기 전에 부대 1개를 보내 둠 기가노토를 공격하세요. 더 많은 피해를 입힐수록 더 많은 포인트를 획득할 수 있습니다。",
    "在限定时间内派1支护卫队攻击毁灭劫匪团伙。造成的伤害越高，获得的积分越多。"
]

params = {
    "spreadsheetId": "1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg",
    "range": "EVENT!C2745:T2745",
    "valueInputOption": "RAW"
}

body = {
    "majorDimension": "ROWS",
    "values": [notice2_values]
}

params_str = json.dumps(params, ensure_ascii=False)
body_str = json.dumps(body, ensure_ascii=False)

# 写入文件
with open("C:/Users/linkang/gws_params.json", "w", encoding="utf-8") as f:
    f.write(params_str)
with open("C:/Users/linkang/gws_body.json", "w", encoding="utf-8") as f:
    f.write(body_str)

print("params:", params_str[:100])
print("body len:", len(body_str))
