import json, subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

# 每行格式: [目标页签, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns]
ROWS = [
    ["ITEM", "easter_fest_pack_common_name", "节日普通卡包-复活节", "Easter Festival Common Card Pack", "Pack de cartes commun du festival de Pâques", "Oster-Festival Gewöhnliches Kartenpaket", "Pacote de Cartas Comum do Festival de Páscoa", "復活節普通卡包", "Paket Kartu Umum Festival Paskah", "แพ็คการ์ดธรรมดาเทศกาลอีสเตอร์", "Paquete de Cartas Común del Festival de Pascua", "Обычный набор карт Пасхального фестиваля", "Paskalya Festivali Normal Kart Paketi", "Gói Thẻ Thường Lễ Hội Phục Sinh", "Pacchetto Carte Comune del Festival di Pasqua", "Zwykła Paczka Kart Festiwalu Wielkanocnego", "حزمة بطاقات عادية لمهرجان عيد الفصح", "イースターフェスティバル通常カードパック", "부활절 축제 일반 카드 팩", "节日普通卡包-复活节"],
    ["ITEM", "easter_fest_pack_common_desc", "最为常见的节日限定卡包，至少获得一张普通以上品质卡片。", "The most common Easter Festival card pack. Contains at least one card of Common quality or higher.", "Le pack de cartes le plus courant du festival de Pâques. Contient au moins une carte de qualité Commune ou supérieure.", "Das häufigste Oster-Festival-Kartenpaket. Enthält mindestens eine Karte von gewöhnlicher Qualität oder höher.", "O pacote de cartas mais comum do Festival de Páscoa. Contém pelo menos uma carta de qualidade Comum ou superior.", "最常見的復活節限定卡包，至少獲得一張普通以上品質卡片。", "Paket kartu paling umum dari Festival Paskah. Berisi setidaknya satu kartu berkualitas Umum atau lebih tinggi.", "แพ็คการ์ดที่พบได้บ่อยที่สุดของเทศกาลอีสเตอร์ มีการ์ดคุณภาพธรรมดาขึ้นไปอย่างน้อยหนึ่งใบ", "El paquete de cartas más común del Festival de Pascua. Contiene al menos una carta de calidad Común o superior.", "Самый распространённый набор карт Пасхального фестиваля. Содержит как минимум одну карту обычного качества или выше.", "Paskalya Festivali'nin en yaygın kart paketi. En az bir Sıradan kalitede veya daha yüksek kart içerir.", "Gói thẻ phổ biến nhất của Lễ hội Phục Sinh. Chứa ít nhất một thẻ chất lượng Thường trở lên.", "Il pacchetto di carte più comune del Festival di Pasqua. Contiene almeno una carta di qualità Comune o superiore.", "Najpopularniejsza paczka kart Festiwalu Wielkanocnego. Zawiera co najmniej jedną kartę o jakości Zwykłej lub wyższej.", "أكثر حزم بطاقات مهرجان عيد الفصح شيوعًا. تحتوي على بطاقة واحدة على الأقل بجودة عادية أو أعلى.", "最も一般的なイースターフェスティバルカードパック。通常品質以上のカードが少なくとも1枚含まれています。", "가장 흔한 부활절 축제 카드 팩입니다. 일반 품질 이상의 카드가 최소 1장 포함되어 있습니다.", "最为常见的节日限定卡包，至少获得一张普通以上品质卡片。"],
    ["ITEM", "easter_fest_pack_excellent_name", "节日精良卡包-复活节", "Easter Festival Excellent Card Pack", "Pack de cartes excellent du festival de Pâques", "Oster-Festival Ausgezeichnetes Kartenpaket", "Pacote de Cartas Excelente do Festival de Páscoa", "復活節精良卡包", "Paket Kartu Bagus Festival Paskah", "แพ็คการ์ดยอดเยี่ยมเทศกาลอีสเตอร์", "Paquete de Cartas Excelente del Festival de Pascua", "Отличный набор карт Пасхального фестиваля", "Paskalya Festivali Mükemmel Kart Paketi", "Gói Thẻ Xuất Sắc Lễ Hội Phục Sinh", "Pacchetto Carte Eccellente del Festival di Pasqua", "Doskonała Paczka Kart Festiwalu Wielkanocnego", "حزمة بطاقات ممتازة لمهرجان عيد الفصح", "イースターフェスティバル精良カードパック", "부활절 축제 우수 카드 팩", "节日精良卡包-复活节"],
    ["ITEM", "easter_fest_pack_excellent_desc", "品质稍好的节日限定卡包，至少获得一张精良以上品质卡片。", "A decent-quality Easter Festival card pack. Contains at least one card of Excellent quality or higher.", "Un pack de cartes de bonne qualité du festival de Pâques. Contient au moins une carte de qualité Excellente ou supérieure.", "Ein Oster-Festival-Kartenpaket von guter Qualität. Enthält mindestens eine Karte von ausgezeichneter Qualität oder höher.", "Um pacote de cartas de boa qualidade do Festival de Páscoa. Contém pelo menos uma carta de qualidade Excelente ou superior.", "品質稍好的復活節限定卡包，至少獲得一張精良以上品質卡片。", "Paket kartu berkualitas baik dari Festival Paskah. Berisi setidaknya satu kartu berkualitas Bagus atau lebih tinggi.", "แพ็คการ์ดคุณภาพดีของเทศกาลอีสเตอร์ มีการ์ดคุณภาพยอดเยี่ยมขึ้นไปอย่างน้อยหนึ่งใบ", "Un paquete de cartas de buena calidad del Festival de Pascua. Contiene al menos una carta de calidad Excelente o superior.", "Набор карт Пасхального фестиваля хорошего качества. Содержит как минимум одну карту отличного качества или выше.", "Paskalya Festivali'nin iyi kaliteli kart paketi. En az bir Mükemmel kalitede veya daha yüksek kart içerir.", "Gói thẻ chất lượng tốt của Lễ hội Phục Sinh. Chứa ít nhất một thẻ chất lượng Xuất sắc trở lên.", "Un pacchetto di carte di buona qualità del Festival di Pasqua. Contiene almeno una carta di qualità Eccellente o superiore.", "Paczka kart dobrej jakości Festiwalu Wielkanocnego. Zawiera co najmniej jedną kartę o jakości Doskonałej lub wyższej.", "حزمة بطاقات ذات جودة جيدة لمهرجان عيد الفصح. تحتوي على بطاقة واحدة على الأقل بجودة ممتازة أو أعلى.", "品質の良いイースターフェスティバルカードパック。精良品質以上のカードが少なくとも1枚含まれています。", "품질이 좋은 부활절 축제 카드 팩입니다. 우수 품질 이상의 카드가 최소 1장 포함되어 있습니다.", "品质稍好的节日限定卡包，至少获得一张精良以上品质卡片。"],
    ["ITEM", "easter_fest_pack_rare_name", "节日稀有卡包-复活节", "Easter Festival Rare Card Pack", "Pack de cartes rare du festival de Pâques", "Oster-Festival Seltenes Kartenpaket", "Pacote de Cartas Raro do Festival de Páscoa", "復活節稀有卡包", "Paket Kartu Langka Festival Paskah", "แพ็คการ์ดหายากเทศกาลอีสเตอร์", "Paquete de Cartas Raro del Festival de Pascua", "Редкий набор карт Пасхального фестиваля", "Paskalya Festivali Nadir Kart Paketi", "Gói Thẻ Hiếm Lễ Hội Phục Sinh", "Pacchetto Carte Raro del Festival di Pasqua", "Rzadka Paczka Kart Festiwalu Wielkanocnego", "حزمة بطاقات نادرة لمهرجان عيد الفصح", "イースターフェスティバルレアカードパック", "부활절 축제 희귀 카드 팩", "节日稀有卡包-复活节"],
    ["ITEM", "easter_fest_pack_rare_desc", "较为罕见的节日限定卡包，至少获得一张稀有以上品质卡片。", "A rare Easter Festival card pack. Contains at least one card of Rare quality or higher.", "Un pack de cartes rare du festival de Pâques. Contient au moins une carte de qualité Rare ou supérieure.", "Ein seltenes Oster-Festival-Kartenpaket. Enthält mindestens eine Karte von seltener Qualität oder höher.", "Um pacote de cartas raro do Festival de Páscoa. Contém pelo menos uma carta de qualidade Rara ou superior.", "較為罕見的復活節限定卡包，至少獲得一張稀有以上品質卡片。", "Paket kartu langka dari Festival Paskah. Berisi setidaknya satu kartu berkualitas Langka atau lebih tinggi.", "แพ็คการ์ดหายากของเทศกาลอีสเตอร์ มีการ์ดคุณภาพหายากขึ้นไปอย่างน้อยหนึ่งใบ", "Un paquete de cartas raro del Festival de Pascua. Contiene al menos una carta de calidad Rara o superior.", "Редкий набор карт Пасхального фестиваля. Содержит как минимум одну карту редкого качества или выше.", "Paskalya Festivali'nin nadir kart paketi. En az bir Nadir kalitede veya daha yüksek kart içerir.", "Gói thẻ hiếm của Lễ hội Phục Sinh. Chứa ít nhất một thẻ chất lượng Hiếm trở lên.", "Un pacchetto di carte raro del Festival di Pasqua. Contiene almeno una carta di qualità Rara o superiore.", "Rzadka paczka kart Festiwalu Wielkanocnego. Zawiera co najmniej jedną kartę o jakości Rzadkiej lub wyższej.", "حزمة بطاقات نادرة لمهرجان عيد الفصح. تحتوي على بطاقة واحدة على الأقل بجودة نادرة أو أعلى.", "珍しいイースターフェスティバルカードパック。レア品質以上のカードが少なくとも1枚含まれています。", "희귀한 부활절 축제 카드 팩입니다. 희귀 품질 이상의 카드가 최소 1장 포함되어 있습니다.", "较为罕见的节日限定卡包，至少获得一张稀有以上品质卡片。"],
    ["ITEM", "easter_fest_pack_epic_name", "节日史诗卡包-复活节", "Easter Festival Epic Card Pack", "Pack de cartes épique du festival de Pâques", "Oster-Festival Episches Kartenpaket", "Pacote de Cartas Épico do Festival de Páscoa", "復活節史詩卡包", "Paket Kartu Epik Festival Paskah", "แพ็คการ์ดมหากาพย์เทศกาลอีสเตอร์", "Paquete de Cartas Épico del Festival de Pascua", "Эпический набор карт Пасхального фестиваля", "Paskalya Festivali Destansı Kart Paketi", "Gói Thẻ Sử Thi Lễ Hội Phục Sinh", "Pacchetto Carte Epico del Festival di Pasqua", "Epicka Paczka Kart Festiwalu Wielkanocnego", "حزمة بطاقات أسطورية لمهرجان عيد الفصح", "イースターフェスティバルエピックカードパック", "부활절 축제 에픽 카드 팩", "节日史诗卡包-复活节"],
    ["ITEM", "easter_fest_pack_epic_desc", "制作精美的节日限定卡包，至少获得一张史诗以上品质卡片。", "An exquisitely crafted Easter Festival card pack. Contains at least one card of Epic quality or higher.", "Un pack de cartes du festival de Pâques finement conçu. Contient au moins une carte de qualité Épique ou supérieure.", "Ein kunstvoll gefertigtes Oster-Festival-Kartenpaket. Enthält mindestens eine Karte von epischer Qualität oder höher.", "Um pacote de cartas requintadamente elaborado do Festival de Páscoa. Contém pelo menos uma carta de qualidade Épica ou superior.", "製作精美的復活節限定卡包，至少獲得一張史詩以上品質卡片。", "Paket kartu Festival Paskah yang dibuat dengan indah. Berisi setidaknya satu kartu berkualitas Epik atau lebih tinggi.", "แพ็คการ์ดเทศกาลอีสเตอร์ที่ประดิษฐ์อย่างประณีต มีการ์ดคุณภาพมหากาพย์ขึ้นไปอย่างน้อยหนึ่งใบ", "Un paquete de cartas del Festival de Pascua exquisitamente elaborado. Contiene al menos una carta de calidad Épica o superior.", "Изысканно изготовленный набор карт Пасхального фестиваля. Содержит как минимум одну карту эпического качества или выше.", "Paskalya Festivali'nin özenle hazırlanmış kart paketi. En az bir Destansı kalitede veya daha yüksek kart içerir.", "Gói thẻ Lễ hội Phục Sinh được chế tác tinh xảo. Chứa ít nhất một thẻ chất lượng Sử thi trở lên.", "Un pacchetto di carte del Festival di Pasqua finemente realizzato. Contiene almeno una carta di qualità Epica o superiore.", "Pięknie wykonana paczka kart Festiwalu Wielkanocnego. Zawiera co najmniej jedną kartę o jakości Epickiej lub wyższej.", "حزمة بطاقات مهرجان عيد الفصح المصنوعة بإتقان. تحتوي على بطاقة واحدة على الأقل بجودة أسطورية أو أعلى.", "精巧に作られたイースターフェスティバルカードパック。エピック品質以上のカードが少なくとも1枚含まれています。", "정교하게 제작된 부활절 축제 카드 팩입니다. 에픽 품질 이상의 카드가 최소 1장 포함되어 있습니다.", "制作精美的节日限定卡包，至少获得一张史诗以上品质卡片。"],
    ["ITEM", "easter_fest_pack_legendary_name", "节日传说卡包-复活节", "Easter Festival Legendary Card Pack", "Pack de cartes légendaire du festival de Pâques", "Oster-Festival Legendäres Kartenpaket", "Pacote de Cartas Lendário do Festival de Páscoa", "復活節傳說卡包", "Paket Kartu Legendaris Festival Paskah", "แพ็คการ์ดตำนานเทศกาลอีสเตอร์", "Paquete de Cartas Legendario del Festival de Pascua", "Легендарный набор карт Пасхального фестиваля", "Paskalya Festivali Efsanevi Kart Paketi", "Gói Thẻ Huyền Thoại Lễ Hội Phục Sinh", "Pacchetto Carte Leggendario del Festival di Pasqua", "Legendarna Paczka Kart Festiwalu Wielkanocnego", "حزمة بطاقات أسطورية لمهرجان عيد الفصح", "イースターフェスティバルレジェンダリーカードパック", "부활절 축제 전설 카드 팩", "节日传说卡包-复活节"],
    ["ITEM", "easter_fest_pack_legendary_desc", "工艺上乘的节日限定卡包，至少获得一张传说以上品质卡片。", "A masterfully crafted Easter Festival card pack. Contains at least one card of Legendary quality or higher.", "Un pack de cartes du festival de Pâques magistralement conçu. Contient au moins une carte de qualité Légendaire ou supérieure.", "Ein meisterhaft gefertigtes Oster-Festival-Kartenpaket. Enthält mindestens eine Karte von legendärer Qualität oder höher.", "Um pacote de cartas magistralmente elaborado do Festival de Páscoa. Contém pelo menos uma carta de qualidade Lendária ou superior.", "工藝上乘的復活節限定卡包，至少獲得一張傳說以上品質卡片。", "Paket kartu Festival Paskah yang dibuat dengan ahli. Berisi setidaknya satu kartu berkualitas Legendaris atau lebih tinggi.", "แพ็คการ์ดเทศกาลอีสเตอร์ที่ประดิษฐ์อย่างเชี่ยวชาญ มีการ์ดคุณภาพตำนานขึ้นไปอย่างน้อยหนึ่งใบ", "Un paquete de cartas del Festival de Pascua magistralmente elaborado. Contiene al menos una carta de calidad Legendaria o superior.", "Мастерски изготовленный набор карт Пасхального фестиваля. Содержит как минимум одну карту легендарного качества или выше.", "Paskalya Festivali'nin ustalıkla hazırlanmış kart paketi. En az bir Efsanevi kalitede veya daha yüksek kart içerir.", "Gói thẻ Lễ hội Phục Sinh được chế tác bậc thầy. Chứa ít nhất một thẻ chất lượng Huyền thoại trở lên.", "Un pacchetto di carte del Festival di Pasqua magistralmente realizzato. Contiene almeno una carta di qualità Leggendaria o superiore.", "Mistrzowsko wykonana paczka kart Festiwalu Wielkanocnego. Zawiera co najmniej jedną kartę o jakości Legendarnej lub wyższej.", "حزمة بطاقات مهرجان عيد الفصح المصنوعة ببراعة. تحتوي على بطاقة واحدة على الأقل بجودة أسطورية أو أعلى.", "熟練の職人が作ったイースターフェスティバルカードパック。レジェンダリー品質以上のカードが少なくとも1枚含まれています。", "장인이 제작한 부활절 축제 카드 팩입니다. 전설 품질 이상의 카드가 최소 1장 포함되어 있습니다.", "工艺上乘的节日限定卡包，至少获得一张传说以上品质卡片。"],
    ["ITEM", "easter_fest_pack_selection_name", "节日自选卡包-复活节", "Easter Festival Selection Card Pack", "Pack de cartes à sélection du festival de Pâques", "Oster-Festival Auswahl-Kartenpaket", "Pacote de Cartas de Seleção do Festival de Páscoa", "復活節自選卡包", "Paket Kartu Pilihan Festival Paskah", "แพ็คการ์ดเลือกได้เทศกาลอีสเตอร์", "Paquete de Cartas de Selección del Festival de Pascua", "Набор карт на выбор Пасхального фестиваля", "Paskalya Festivali Seçim Kart Paketi", "Gói Thẻ Tự Chọn Lễ Hội Phục Sinh", "Pacchetto Carte a Scelta del Festival di Pasqua", "Paczka Kart do Wyboru Festiwalu Wielkanocnego", "حزمة بطاقات اختيار مهرجان عيد الفصح", "イースターフェスティバル選択カードパック", "부활절 축제 선택 카드 팩", "节日自选卡包-复活节"],
    ["ITEM", "easter_fest_pack_selection_desc", "工艺上乘的节日自选卡包，可自选指定卡册中的传说、史诗品质卡片。", "A premium Easter Festival selection card pack. Choose any card of any quality from the designated collection.", "Un pack de cartes à sélection premium du festival de Pâques. Choisissez n'importe quelle carte de n'importe quelle qualité parmi la collection désignée.", "Ein Premium-Oster-Festival-Auswahl-Kartenpaket. Wähle eine beliebige Karte beliebiger Qualität aus der angegebenen Sammlung.", "Um pacote de cartas de seleção premium do Festival de Páscoa. Escolha qualquer carta de qualquer qualidade da coleção designada.", "工藝上乘的復活節自選卡包，可自選指定卡冊中的傳說、史詩品質卡片。", "Paket kartu pilihan premium Festival Paskah. Pilih kartu apa pun dengan kualitas apa pun dari koleksi yang ditentukan.", "แพ็คการ์ดเลือกได้พรีเมียมของเทศกาลอีสเตอร์ เลือกการ์ดใดก็ได้จากคอลเลกชันที่กำหนด", "Un paquete de cartas de selección premium del Festival de Pascua. Elige cualquier carta de cualquier calidad de la colección designada.", "Премиальный набор карт на выбор Пасхального фестиваля. Выберите любую карту любого качества из указанной коллекции.", "Paskalya Festivali'nin premium seçim kart paketi. Belirlenen koleksiyondan herhangi bir kalitede herhangi bir kart seçin.", "Gói thẻ tự chọn cao cấp của Lễ hội Phục Sinh. Chọn bất kỳ thẻ nào với bất kỳ chất lượng nào từ bộ sưu tập được chỉ định.", "Un pacchetto di carte a scelta premium del Festival di Pasqua. Scegli qualsiasi carta di qualsiasi qualità dalla collezione designata.", "Paczka kart premium do wyboru Festiwalu Wielkanocnego. Wybierz dowolną kartę o dowolnej jakości z wyznaczonej kolekcji.", "حزمة بطاقات اختيار مميزة لمهرجان عيد الفصح. اختر أي بطاقة بأي جودة من المجموعة المحددة.", "プレミアムイースターフェスティバル選択カードパック。指定されたコレクションから任意の品質のカードを選択できます。", "프리미엄 부활절 축제 선택 카드 팩입니다. 지정된 컬렉션에서 원하는 품질의 카드를 선택할 수 있습니다.", "工艺上乘的节日自选卡包，可自选指定卡册中的传说、史诗品质卡片。"],
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

    # 获取暂存页签 sheetId
    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID, fields="sheets.properties"
    ).execute()
    staging_sheet_id = None
    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == STAGING_SHEET:
            staging_sheet_id = s["properties"]["sheetId"]
            break

    # 定位追加起始行
    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID, range=f"'{STAGING_SHEET}'!A:A"
    ).execute()
    existing = result.get("values", [])
    next_row = max(len(existing) + 1, 2)
    end_row = next_row + len(ROWS) - 1

    # 写入数据到 B~U 列（A 列留给 checkbox）
    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B{next_row}:U{end_row}",
        valueInputOption="RAW",
        body={"values": ROWS},
    ).execute()

    # 为 A 列设置 checkbox
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
