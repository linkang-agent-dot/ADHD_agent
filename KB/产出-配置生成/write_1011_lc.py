import json, subprocess, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_1011 = '1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg'
EVENT_GID = 550403607
TAB = 'EVENT'

def gws_run(args, body=None):
    cmd = [GWS] + args
    if body:
        cmd += ['--json', json.dumps(body, ensure_ascii=False, separators=(',', ':'))]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(f'  FAIL rc={r.returncode}\n  stderr={r.stderr[:500]}')
        return None
    return json.loads(r.stdout) if r.stdout.strip() else {}

# ── Step 0: Backup ───────────────────────────────────────────────────────────
print('Step 0: Backing up EVENT tab...')
backup_body = {'requests': [{'duplicateSheet': {
    'sourceSheetId': EVENT_GID,
    'insertSheetIndex': 99,
    'newSheetName': 'EVENT_backup_labor_lc'
}}]}
resp = gws_run(['sheets', 'spreadsheets', 'batchUpdate',
                '--params', json.dumps({'spreadsheetId': SHEET_1011})], backup_body)
if resp is None:
    print('Backup FAILED — aborting')
    sys.exit(1)
print('  ✅ Backup created: EVENT_backup_labor_lc')

# ── All 70 LC rows ────────────────────────────────────────────────────────────
# Format: [ID_int, key, cn, en, fr, de]
rows = [
    # ── Book (1) ─────────────────────────────────────────────────────────────
    ['1011087586', 'item_card_book_title_4',
     '拓荒传奇', "Pioneer's Legend",
     'Légende des pionniers', 'Pionierslegende'],
    # ── Groups (9): item_card_collection_title_35–43 ─────────────────────────
    ['1011087587', 'item_card_collection_title_35',
     '启程准备', 'Departure Preparations',
     'Préparatifs de départ', 'Aufbruchsvorbereitungen'],
    ['1011087588', 'item_card_collection_title_36',
     '荒野行军', 'Wilderness March',
     'Marche en pleine nature', 'Wildnismarsch'],
    ['1011087589', 'item_card_collection_title_37',
     '扎营落脚', 'Setting Up Camp',
     'Installation du camp', 'Lageraufbau'],
    ['1011087590', 'item_card_collection_title_38',
     '矿脉勘探', 'Mineral Prospecting',
     'Prospection minière', 'Mineraliensuche'],
    ['1011087591', 'item_card_collection_title_39',
     '河谷淘金', 'Valley Gold Panning',
     "Orpaillage en vallée", 'Goldwaschen im Tal'],
    ['1011087592', 'item_card_collection_title_40',
     '前哨筑城', 'Outpost Construction',
     "Construction de l'avant-poste", 'Außenpostenbau'],
    ['1011087593', 'item_card_collection_title_41',
     '荒原猎踪', 'Prairie Tracking',
     'Pistage dans la prairie', 'Prärieverfolgung'],
    ['1011087594', 'item_card_collection_title_42',
     '地底秘境', 'Underground Secrets',
     'Secrets souterrains', 'Unterirdische Geheimnisse'],
    ['1011087595', 'item_card_collection_title_43',
     '拓荒盛典', 'Pioneer Celebration',
     'Célébration des pionniers', 'Pioniersfeier'],
    # ── G1 启程准备: item_card_name_309–314 ──────────────────────────────────
    ['1011087596', 'item_card_name_309',
     '整理行囊', 'Packing Up',
     'Ranger ses affaires', 'Gepäck ordnen'],
    ['1011087597', 'item_card_name_310',
     '晨起伸懒腰', 'Morning Stretch',
     'Étirement matinal', 'Morgenstreckung'],
    ['1011087598', 'item_card_name_311',
     '打扫工坊', 'Cleaning the Workshop',
     "Nettoyer l'atelier", 'Die Werkstatt säubern'],
    ['1011087599', 'item_card_name_312',
     '调校日晷', 'Calibrating the Sundial',
     'Réglage du cadran solaire', 'Sonnenuhr kalibrieren'],
    ['1011087600', 'item_card_name_313',
     '仰望星河', 'Gazing at the Stars',
     'Contempler les étoiles', 'Zu den Sternen schauen'],
    ['1011087601', 'item_card_name_314',
     '指点星图', 'Reading the Star Map',
     'Lire la carte des étoiles', 'Sternenkarte lesen'],
    # ── G2 荒野行军: item_card_name_315–320 ──────────────────────────────────
    ['1011087602', 'item_card_name_315',
     '攀岩探路', 'Rock Climbing Scout',
     'Escalade exploratoire', 'Kletterkundschaft'],
    ['1011087603', 'item_card_name_316',
     '涉水渡河', 'Wading Across',
     'Traverser à gué', 'Durch das Wasser waten'],
    ['1011087604', 'item_card_name_317',
     '树下小憩', 'Resting Under a Tree',
     'Se reposer sous un arbre', 'Unter einem Baum rasten'],
    ['1011087605', 'item_card_name_318',
     '雨中赶路', 'Marching in the Rain',
     'Marcher sous la pluie', 'Im Regen marschieren'],
    ['1011087606', 'item_card_name_319',
     '发现脚印', 'Discovering Footprints',
     'Découvrir des empreintes', 'Fußspuren entdecken'],
    ['1011087607', 'item_card_name_320',
     '悬崖远眺', 'Cliff Overlook',
     'Vue depuis la falaise', 'Klippen-Ausblick'],
    # ── G3 扎营落脚: item_card_name_321–326 ──────────────────────────────────
    ['1011087608', 'item_card_name_321',
     '选址插旗', 'Choosing a Campsite',
     'Choisir un emplacement de camp', 'Lagerplatz wählen'],
    ['1011087609', 'item_card_name_322',
     '搭建帐篷', 'Pitching the Tent',
     'Monter la tente', 'Zelt aufschlagen'],
    ['1011087610', 'item_card_name_323',
     '挖井取水', 'Digging for Water',
     'Creuser un puits', 'Nach Wasser graben'],
    ['1011087611', 'item_card_name_324',
     '砍伐木材', 'Chopping Wood',
     'Couper du bois', 'Holz hacken'],
    ['1011087612', 'item_card_name_325',
     '升起篝火', 'Lighting the Campfire',
     'Allumer le feu de camp', 'Lagerfeuer entzünden'],
    ['1011087613', 'item_card_name_326',
     '第一顿饭', 'The First Meal',
     'Le premier repas', 'Das erste Mahl'],
    # ── G4 矿脉勘探: item_card_name_327–332 ──────────────────────────────────
    ['1011087614', 'item_card_name_327',
     '采集矿样', 'Collecting Ore Samples',
     'Collecter des échantillons de minerai', 'Erzproben sammeln'],
    ['1011087615', 'item_card_name_328',
     '洞口初探', 'Cave Entrance Exploration',
     "Explorer l'entrée de la grotte", 'Höhleneingang erkunden'],
    ['1011087616', 'item_card_name_329',
     '矿壁采集', 'Mining the Walls',
     'Extraire du minerai des parois', 'Erzwände abbauen'],
    ['1011087617', 'item_card_name_330',
     '矿车推运', 'Pushing the Mine Cart',
     'Pousser le wagonnet minier', 'Minenkarren schieben'],
    ['1011087618', 'item_card_name_331',
     '矿脉闪光', "Vein's Gleam",
     'Éclat de la veine', 'Aderglanz'],
    ['1011087619', 'item_card_name_332',
     '标记矿脉', 'Marking the Vein',
     'Marquer la veine', 'Ader markieren'],
    # ── G5 河谷淘金: item_card_name_333–338 ──────────────────────────────────
    ['1011087620', 'item_card_name_333',
     '河边淘洗', 'Panning by the River',
     "Chercher de l'or en rivière", 'Am Fluss waschen'],
    ['1011087621', 'item_card_name_334',
     '筛选矿砂', 'Sifting Ore',
     'Tamiser le minerai', 'Erz sieben'],
    ['1011087622', 'item_card_name_335',
     '发现金粒', 'Finding Gold Nuggets',
     "Trouver des pépites d'or", 'Goldnuggets finden'],
    ['1011087623', 'item_card_name_336',
     '搭建水渠', 'Building a Channel',
     'Construire un canal', 'Kanal bauen'],
    ['1011087624', 'item_card_name_337',
     '称量收获', 'Weighing the Haul',
     'Peser la récolte', 'Ausbeute abwiegen'],
    ['1011087625', 'item_card_name_338',
     '满载而归', 'Returning Laden',
     'Rentrer chargé', 'Beladen zurückkehren'],
    # ── G6 前哨筑城: item_card_name_339–344 ──────────────────────────────────
    ['1011087626', 'item_card_name_339',
     '绘制蓝图', 'Drawing the Blueprint',
     'Tracer le plan', 'Bauplan zeichnen'],
    ['1011087627', 'item_card_name_340',
     '夯实地基', 'Laying the Foundation',
     'Consolider les fondations', 'Fundament legen'],
    ['1011087628', 'item_card_name_341',
     '竖起围墙', 'Raising the Walls',
     'Ériger les murs', 'Mauern errichten'],
    ['1011087629', 'item_card_name_342',
     '瞭望塔成', 'Watchtower Complete',
     'Tour de guet achevée', 'Wachturm fertig'],
    ['1011087630', 'item_card_name_343',
     '铁匠开炉', 'The Smithy Opens',
     'La forge ouvre', 'Die Schmiede öffnet'],
    ['1011087631', 'item_card_name_344',
     '升旗时刻', 'Flag Raising Ceremony',
     'Cérémonie du lever du drapeau', 'Flaggenhissung'],
    # ── G7 荒原猎踪: item_card_name_345–350 ──────────────────────────────────
    ['1011087632', 'item_card_name_345',
     '追踪足迹', 'Tracking Footprints',
     'Suivre les empreintes', 'Fußspuren verfolgen'],
    ['1011087633', 'item_card_name_346',
     '布置陷阱', 'Setting Traps',
     'Poser des pièges', 'Fallen aufstellen'],
    ['1011087634', 'item_card_name_347',
     '正面对峙', 'Face to Face',
     'Confrontation frontale', 'Direkte Konfrontation'],
    ['1011087635', 'item_card_name_348',
     '驯服坐骑', 'Taming a Mount',
     'Dompter une monture', 'Ein Reittier zähmen'],
    ['1011087636', 'item_card_name_349',
     '荒原伙伴', 'Prairie Companion',
     'Compagnon de la prairie', 'Präriebegleiter'],
    ['1011087637', 'item_card_name_350',
     '原野奔驰', 'Racing the Plains',
     'Galoper dans les plaines', 'Über die Ebenen galoppieren'],
    # ── G8 地底秘境: item_card_name_351–356 ──────────────────────────────────
    ['1011087638', 'item_card_name_351',
     '深渊入口', 'Abyss Entrance',
     "Entrée de l'abîme", 'Abgrund-Eingang'],
    ['1011087639', 'item_card_name_352',
     '水晶密林', 'Crystal Forest',
     'Forêt de cristaux', 'Kristallwald'],
    ['1011087640', 'item_card_name_353',
     '地底暗河', 'Underground River',
     'Rivière souterraine', 'Unterirdischer Fluss'],
    ['1011087641', 'item_card_name_354',
     '远古化石', 'Ancient Fossil',
     'Fossile antique', 'Urzeitliches Fossil'],
    ['1011087642', 'item_card_name_355',
     '熔岩之心', 'Heart of Magma',
     'Cœur de magma', 'Herz der Magma'],
    ['1011087643', 'item_card_name_356',
     '上古宝藏', 'Ancient Treasure',
     'Trésor antique', 'Urzeit-Schatz'],
    # ── G9 拓荒盛典: item_card_name_357–362 ──────────────────────────────────
    ['1011087644', 'item_card_name_357',
     '丰收集市', 'Harvest Market',
     'Marché de la récolte', 'Erntemarkt'],
    ['1011087645', 'item_card_name_358',
     '凯旋巡游', 'Triumphal Parade',
     'Défilé triomphal', 'Triumphparade'],
    ['1011087646', 'item_card_name_359',
     '丰饶之宴', 'Feast of Plenty',
     "Festin de l'abondance", 'Fest der Fülle'],
    ['1011087647', 'item_card_name_360',
     '授勋仪式', 'Award Ceremony',
     'Cérémonie de remise des distinctions', 'Auszeichnungszeremonie'],
    ['1011087648', 'item_card_name_361',
     '烟火之夜', 'Night of Fireworks',
     "Nuit de feux d'artifice", 'Feuerwerknacht'],
    ['1011087649', 'item_card_name_362',
     '新世界黎明', 'Dawn of the New World',
     'Aube du nouveau monde', 'Morgenröte der neuen Welt'],
    # ── Pack names (3) ────────────────────────────────────────────────────────
    ['1011087650', 'item_card_pack_name_15',
     '卓越-活动史诗卡包（拓荒）', 'Excellent - Event Epic Card Pack (Pioneer)',
     "Excellent - Pack de cartes épiques d'événement (Pionnier)",
     'Ausgezeichnet – Epische Ereigniskartenpackung (Pionier)'],
    ['1011087651', 'item_card_pack_name_16',
     '卓越-活动传说卡包（拓荒）', 'Excellent - Event Legendary Card Pack (Pioneer)',
     "Excellent - Pack de cartes légendaires d'événement (Pionnier)",
     'Ausgezeichnet – Legendäres Ereignis-Kartenpaket (Pionier)'],
    ['1011087652', 'item_card_pack_name_17',
     '史诗-活动传说卡包（拓荒）', 'Epic - Event Legendary Card Pack (Pioneer)',
     'Épique - Pack de cartes légendaires post-action (Pionnier)',
     'Episch – Legendäres Kartenpaket nach der Aktion (Pionier)'],
    # ── Pack descs (3) ────────────────────────────────────────────────────────
    # desc_15: 3★/4★  (same tier as 占星 desc_12)
    ['1011087653', 'item_card_pack_desc_15',
     '随机获得<color=#59B7FF>卓越</color>到<color=#CF68FF>史诗</color>品质的卡片',
     'Randomly obtain cards of <color=#59B7FF>Excellent</color> to <color=#CF68FF>Epic</color> rarity',
     'Obtenez aléatoirement des cartes de rareté <color=#59B7FF>Excellente</color> à <color=#CF68FF>Épique</color>',
     'Erhalte zufällig Karten der Seltenheit <color=#59B7FF>Hervorragend</color> bis <color=#CF68FF>Episch</color>'],
    # desc_16: 3★/4★/5★  (same tier as 占星 desc_13)
    ['1011087654', 'item_card_pack_desc_16',
     '随机获得<color=#59B7FF>卓越</color>到<color=#FF9B26>传说</color>品质的卡片',
     'Randomly obtain cards of <color=#59B7FF>Excellent</color> to <color=#FF9B26>Legendary</color> rarity',
     'Obtenez aléatoirement des cartes de rareté <color=#59B7FF>Excellente</color> à <color=#FF9B26>Légendaire</color>',
     'Erhalte zufällig Karten mit <color=#59B7FF>Hervorragender</color> bis <color=#FF9B26>Legendärer</color> Seltenheit'],
    # desc_17: 4★/5★  (same tier as 占星 desc_14)
    ['1011087655', 'item_card_pack_desc_17',
     '随机获得<color=#CF68FF>史诗</color>到<color=#FF9B26>传说</color>品质的卡片',
     'Randomly obtain cards of <color=#CF68FF>Epic</color> to <color=#FF9B26>Legendary</color> rarity',
     'Obtenez aléatoirement des cartes de rareté <color=#CF68FF>Épique</color> à <color=#FF9B26>Légendaire</color>',
     'Erhalte zufällig Karten der Seltenheit von <color=#CF68FF>Episch</color> bis <color=#FF9B26>Legendär</color>'],
]

assert len(rows) == 70, f'Expected 70 rows, got {len(rows)}'
print(f'Total rows to write: {len(rows)}')

# ── Step 1: appendDimension ───────────────────────────────────────────────────
print('Step 1: appendDimension +70 rows...')
append_body = {'requests': [{'appendDimension': {
    'sheetId': EVENT_GID,
    'dimension': 'ROWS',
    'length': 70
}}]}
resp = gws_run(['sheets', 'spreadsheets', 'batchUpdate',
                '--params', json.dumps({'spreadsheetId': SHEET_1011})], append_body)
if resp is None:
    print('appendDimension FAILED — aborting')
    sys.exit(1)
print('  ✅ appendDimension OK')

# ── Step 2: Write in batches of 14 ───────────────────────────────────────────
print('Step 2: Writing values...')
BATCH_SIZE = 14
for i in range(0, 70, BATCH_SIZE):
    batch = rows[i:i+BATCH_SIZE]
    row_start = 7401 + i
    rng = f'{TAB}!A{row_start}:F{row_start + len(batch) - 1}'
    print(f'  Batch {i//BATCH_SIZE+1}: {rng} ({len(batch)} rows)...')
    body = {'data': [{'range': rng, 'values': batch}]}
    body_str = json.dumps(body, ensure_ascii=False, separators=(',', ':'))
    params_str = json.dumps({'spreadsheetId': SHEET_1011, 'valueInputOption': 'RAW'})
    cmd = [GWS, 'sheets', 'spreadsheets', 'values', 'batchUpdate',
           '--params', params_str, '--json', body_str]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(f'    FAIL rc={r.returncode} err={r.stderr[:300]}')
    else:
        print(f'    ✅ OK')
    time.sleep(0.5)

# ── Step 3: Verify ────────────────────────────────────────────────────────────
print('\nStep 3: Verifying...')
r = subprocess.run([GWS, 'sheets', 'spreadsheets', 'values', 'get',
    '--params', json.dumps({'spreadsheetId': SHEET_1011,
                            'range': f'{TAB}!A7399:B7471'})],
    capture_output=True, text=True, encoding='utf-8', errors='replace')
d = json.loads(r.stdout)
vals = d.get('values', [])
print(f'Rows 7399-7471: {len(vals)} rows returned')
print(f'  Last anchor (7399): {vals[1] if len(vals)>1 else "(empty)"}')
print(f'  First new (7401):   {vals[2] if len(vals)>2 else "(empty)"}')
print(f'  Last new  (7470):   {vals[-1] if vals else "(empty)"}')
