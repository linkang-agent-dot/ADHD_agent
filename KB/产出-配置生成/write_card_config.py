import json, subprocess, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SHEET_1108 = '1yeFJwufv9QZBOHAIifHTfzyYhG0Fy9SQcfDoGLrzir0'
SHEET_1107 = '1w-hmQGDu86TxrHGirvhQoaoniUjJA11t1XxCPDE5ylA'
SHEET_1123 = '1Dlg3r30Q7q19NKWcTHP-orYs7UYXs2TmV_V0xHGexMc'
SHEET_1109 = '1zL0xNJwVQK95r71SDkIWEvZHp8ERFghkIsyyQ92HdZY'
SHEET_1111 = '1pm0nztHsjpHmFBEmx-bLtP7Zjf4GFC67wo-sUmqY7Fs'
GID_1108 = 65753380
GID_1107 = 887412445
GID_1123 = 593941196
GID_1109 = 0

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'

def gws(subcmds, params_dict, body_dict):
    params_str = json.dumps(params_dict, ensure_ascii=False)
    body_str = json.dumps(body_dict, ensure_ascii=False, separators=(',',':'))
    cmd = [GWS, 'sheets', 'spreadsheets'] + subcmds + ['--params', params_str, '--json', body_str]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        print(f'  ERR stderr={r.stderr[:300]}')
        return None
    try:
        return json.loads(r.stdout)
    except:
        return r.stdout[:200]

def backup(sheet_id, src_gid, name):
    print(f'  Backing up GID={src_gid} as "{name}"...')
    r = gws(['batchUpdate'], {'spreadsheetId': sheet_id},
        {'requests':[{'duplicateSheet':{'sourceSheetId':src_gid,'insertSheetIndex':99,'newSheetName':name}}]})
    if r and 'replies' in str(r):
        print(f'  ✅ Backup ok')
    else:
        print(f'  ✅ Backup done (response={str(r)[:100]})')

def insert_rows(sheet_id, gid, start_idx, count):
    print(f'  Inserting {count} rows at startIndex={start_idx}...')
    r = gws(['batchUpdate'], {'spreadsheetId': sheet_id},
        {'requests':[{'insertDimension':{'range':{'sheetId':gid,'dimension':'ROWS','startIndex':start_idx,'endIndex':start_idx+count},'inheritFromBefore':False}}]})
    print(f'  ✅ Insert done')
    return r

def write_values(sheet_id, tab, row_start, col_end, values):
    rng = f'{tab}!A{row_start}:{col_end}{row_start+len(values)-1}'
    print(f'  Writing {len(values)} rows to {rng}...')
    r = gws(['values', 'batchUpdate'],
        {'spreadsheetId': sheet_id, 'valueInputOption': 'RAW'},
        {'data':[{'range': rng, 'values': values}]})
    print(f'  ✅ Write done (resp={str(r)[:80]})')
    return r

def write_update(sheet_id, tab, row_start, col_end, values):
    """Update existing rows (no insert)"""
    rng = f'{tab}!A{row_start}:{col_end}{row_start+len(values)-1}'
    print(f'  Updating {len(values)} rows at {rng}...')
    r = gws(['values', 'batchUpdate'],
        {'spreadsheetId': sheet_id, 'valueInputOption': 'RAW'},
        {'data':[{'range': rng, 'values': values}]})
    print(f'  ✅ Update done')
    return r

# ─────────────────────────────────────────────
print('=== STEP 1: Backup all tabs ===')
backup(SHEET_1108, GID_1108, 'CardGallaryGroup_bak_0521')
backup(SHEET_1107, GID_1107, 'CardGallaryGroup_bak_0521')
backup(SHEET_1123, GID_1123, 'CardGallary_bak_0521')
backup(SHEET_1109, GID_1109, 'CardGallaryStore_bak_0521')

# ─────────────────────────────────────────────
print('\n=== STEP 2: 1109 CardGallaryStore — 3 rows ===')
rows_1109 = [
    ["","11090031","拓荒节1-2星活动卡包",'{"typ":"item","id":111111339,"val":1}','{"typ":"rss","id":11144013,"val":15}','{"limittype":"monthly", "limitcnt":20}',"1011","{}","{}"],
    ["","11090032","拓荒节1-3星活动卡包",'{"typ":"item","id":111111340,"val":1}','{"typ":"rss","id":11144013,"val":30}','{"limittype":"monthly", "limitcnt":15}',"1012","{}","{}"],
    ["","11090033","拓荒节2-3星活动卡包",'{"typ":"item","id":111111341,"val":1}','{"typ":"rss","id":11144013,"val":150}','{"limittype":"monthly", "limitcnt":10}',"1013","{}","{}"],
]
# RequirementPurchase uses actvend+actvopencnt for 21127381
req_purchase = '{"op":"and","args":[{"op":"ge","typ":"actvend","id":21127381,"val":1},{"op":"ge","typ":"actvopencnt","id":21127381,"val":1}]}'
for r in rows_1109:
    r[-1] = req_purchase
insert_rows(SHEET_1109, GID_1109, 16, 3)
time.sleep(1)
write_values(SHEET_1109, 'CardGallaryStore', 17, 'I', rows_1109)

# ─────────────────────────────────────────────
print('\n=== STEP 3: 1108 CardGallaryBook — 1 row ===')
open_req_1108 = '{"op":"or","args":[{"op":"eq","typ":"actvstart","id":21127381,"val":1}]}'
row_1108 = [["",
    "11081004","拓荒传奇",
    "[11074001,11074002,11074003,11074004,11074005,11074006,11074007,11074008,11074009]",
    "1511094005","1511094009","1511094003","1511094004","1511020681",
    '{"typ":"lc","txt":"LC_EVENT_item_card_book_title_4"}',
    '{"typ":"lc","txt":"LC_ASSET_card_gallary_desc"}',
    "99999999",
    "[111111339,111111340,111111341]",
    '[{"typ":"item","id":111111327,"val":1},{"typ":"item","id":11111082,"val":10},{"typ":"item","id":11111083,"val":20}]',
    "[-1,-1]",
    open_req_1108
]]
insert_rows(SHEET_1108, GID_1108, 9, 1)
time.sleep(1)
write_values(SHEET_1108, 'CardGallaryGroup', 10, 'P', row_1108)

# ─────────────────────────────────────────────
print('\n=== STEP 4: 1107 CardGallaryGroup — 9 rows ===')
rf = '[{"typ":"item","id":11116402,"val":5},{"typ":"rss","id":11144003,"val":30000}]'
rows_1107 = [
    ["","11074001","启程准备","[11235001,11235002,11235003,11235004,11235005,11235006]","1511094010","1511094019","1511094020",'{"typ":"lc","txt":"LC_EVENT_item_card_collection_title_35"}',""  ,"11071035",'[{"typ":"item","id":11117024,"val":5},{"typ":"item","id":11116402,"val":5}]',rf],
    ["","11074002","荒野行军","[11235011,11235012,11235013,11235014,11235015,11235016]","1511094011","1511094019","1511094020",'{"typ":"lc","txt":"LC_EVENT_item_card_collection_title_36"}',""  ,"11071036",'[{"typ":"item","id":11117024,"val":5},{"typ":"item","id":11116402,"val":5}]',rf],
    ["","11074003","扎营落脚","[11235021,11235022,11235023,11235024,11235025,11235026]","1511094012","1511094019","1511094020",'{"typ":"lc","txt":"LC_EVENT_item_card_collection_title_37"}',""  ,"11071037",'[{"typ":"item","id":11117024,"val":5},{"typ":"item","id":11116402,"val":5}]',rf],
    ["","11074004","矿脉勘探","[11235031,11235032,11235033,11235034,11235035,11235036]","1511094013","1511094019","1511094020",'{"typ":"lc","txt":"LC_EVENT_item_card_collection_title_38"}',""  ,"11071038",'[{"typ":"item","id":11111083,"val":2},{"typ":"item","id":11116304,"val":2}]',rf],
    ["","11074005","河谷淘金","[11235041,11235042,11235043,11235044,11235045,11235046]","1511094014","1511094019","1511094020",'{"typ":"lc","txt":"LC_EVENT_item_card_collection_title_39"}',""  ,"11071039",'[{"typ":"item","id":11111083,"val":2},{"typ":"item","id":11116304,"val":2}]',rf],
    ["","11074006","前哨筑城","[11235051,11235052,11235053,11235054,11235055,11235056]","1511094015","1511094019","1511094020",'{"typ":"lc","txt":"LC_EVENT_item_card_collection_title_40"}',""  ,"11071040",'[{"typ":"item","id":11111083,"val":2},{"typ":"item","id":11116304,"val":2}]',rf],
    ["","11074007","荒原猎踪","[11235061,11235062,11235063,11235064,11235065,11235066]","1511094016","1511094019","1511094020",'{"typ":"lc","txt":"LC_EVENT_item_card_collection_title_41"}',""  ,"11071041",'[{"typ":"item","id":11111083,"val":3},{"typ":"item","id":11116304,"val":3}]',rf],
    ["","11074008","地底秘境","[11235071,11235072,11235073,11235074,11235075,11235076]","1511094017","1511094019","1511094020",'{"typ":"lc","txt":"LC_EVENT_item_card_collection_title_42"}',""  ,"11071042",'[{"typ":"item","id":11111083,"val":3},{"typ":"item","id":11116304,"val":3}]',rf],
    ["","11074009","拓荒盛典","[11235081,11235082,11235083,11235084,11235085,11235086]","1511094018","1511094019","1511094020",'{"typ":"lc","txt":"LC_EVENT_item_card_collection_title_43"}',""  ,"11071043",'[{"typ":"item","id":11116304,"val":3},{"typ":"item","id":111111327,"val":1}]',rf],
]
insert_rows(SHEET_1107, GID_1107, 40, 9)
time.sleep(1)
write_values(SHEET_1107, 'CardGallaryGroup', 41, 'L', rows_1107)

# ─────────────────────────────────────────────
print('\n=== STEP 5: 1123 CardGallary — 54 rows ===')
fd = '[{"typ":"vm","id":11151001,"val":5}]'
ld = '{"typ":"lc","txt":"LC_ASSET_card_gallary_desc"}'

cards_data = [
    # G1 启程准备 all ★3
    ("11235001","启程准备","整理行囊","3","1511094021","309"),
    ("11235002","启程准备","晨起伸懒腰","3","1511094022","310"),
    ("11235003","启程准备","打扫工坊","3","1511094023","311"),
    ("11235004","启程准备","调校日晷","3","1511094024","312"),
    ("11235005","启程准备","仰望星河","3","1511094025","313"),
    ("11235006","启程准备","指点星图","3","1511094026","314"),
    # G2 荒野行军 5×3★ + 1×4★
    ("11235011","荒野行军","攀岩探路","3","1511094027","315"),
    ("11235012","荒野行军","涉水渡河","3","1511094028","316"),
    ("11235013","荒野行军","树下小憩","3","1511094029","317"),
    ("11235014","荒野行军","雨中赶路","3","1511094030","318"),
    ("11235015","荒野行军","发现脚印","3","1511094031","319"),
    ("11235016","荒野行军","悬崖远眺","4","1511094032","320"),
    # G3 扎营落脚 4×3★ + 2×4★
    ("11235021","扎营落脚","选址插旗","3","1511094033","321"),
    ("11235022","扎营落脚","搭建帐篷","3","1511094034","322"),
    ("11235023","扎营落脚","挖井取水","3","1511094035","323"),
    ("11235024","扎营落脚","砍伐木材","3","1511094036","324"),
    ("11235025","扎营落脚","升起篝火","4","1511094037","325"),
    ("11235026","扎营落脚","第一顿饭","4","1511094038","326"),
    # G4 矿脉勘探 3×3★ + 3×4★
    ("11235031","矿脉勘探","采集矿样","3","1511094039","327"),
    ("11235032","矿脉勘探","洞口初探","3","1511094040","328"),
    ("11235033","矿脉勘探","矿壁采集","3","1511094041","329"),
    ("11235034","矿脉勘探","矿车推运","4","1511094042","330"),
    ("11235035","矿脉勘探","矿脉闪光","4","1511094043","331"),
    ("11235036","矿脉勘探","标记矿脉","4","1511094044","332"),
    # G5 河谷淘金 2×3★ + 3×4★ + 1×5★
    ("11235041","河谷淘金","河边淘洗","3","1511094045","333"),
    ("11235042","河谷淘金","筛选矿砂","3","1511094046","334"),
    ("11235043","河谷淘金","发现金粒","4","1511094047","335"),
    ("11235044","河谷淘金","搭建水渠","4","1511094048","336"),
    ("11235045","河谷淘金","称量收获","4","1511094049","337"),
    ("11235046","河谷淘金","满载而归","5","1511094050","338"),
    # G6 前哨筑城 1×3★ + 4×4★ + 1×5★
    ("11235051","前哨筑城","绘制蓝图","3","1511094051","339"),
    ("11235052","前哨筑城","夯实地基","4","1511094052","340"),
    ("11235053","前哨筑城","竖起围墙","4","1511094053","341"),
    ("11235054","前哨筑城","瞭望塔成","4","1511094054","342"),
    ("11235055","前哨筑城","铁匠开炉","4","1511094055","343"),
    ("11235056","前哨筑城","升旗时刻","5","1511094056","344"),
    # G7 荒原猎踪 1×3★ + 3×4★ + 2×5★
    ("11235061","荒原猎踪","追踪足迹","3","1511094057","345"),
    ("11235062","荒原猎踪","布置陷阱","4","1511094058","346"),
    ("11235063","荒原猎踪","正面对峙","4","1511094059","347"),
    ("11235064","荒原猎踪","驯服坐骑","4","1511094060","348"),
    ("11235065","荒原猎踪","荒原伙伴","5","1511094061","349"),
    ("11235066","荒原猎踪","原野奔驰","5","1511094062","350"),
    # G8 地底秘境 3×4★ + 3×5★
    ("11235071","地底秘境","深渊入口","4","1511094063","351"),
    ("11235072","地底秘境","水晶密林","4","1511094064","352"),
    ("11235073","地底秘境","地底暗河","4","1511094065","353"),
    ("11235074","地底秘境","远古化石","5","1511094066","354"),
    ("11235075","地底秘境","熔岩之心","5","1511094067","355"),
    ("11235076","地底秘境","上古宝藏","5","1511094068","356"),
    # G9 拓荒盛典 3×4★ + 3×5★
    ("11235081","拓荒盛典","丰收集市","4","1511094069","357"),
    ("11235082","拓荒盛典","凯旋巡游","4","1511094070","358"),
    ("11235083","拓荒盛典","丰饶之宴","4","1511094071","359"),
    ("11235084","拓荒盛典","授勋仪式","5","1511094072","360"),
    ("11235085","拓荒盛典","烟火之夜","5","1511094073","361"),
    ("11235086","拓荒盛典","新世界黎明","5","1511094074","362"),
]

honor_map = {"3":"100","4":"200","5":"400"}
recycle_map = {"3":"1","4":"2","5":"10"}

rows_1123 = []
for card_id, group, card_name, star, dk, lc_num in cards_data:
    rows_1123.append([
        "", card_id, group, card_name,
        "11071001", star, dk, "1511094002",
        f'{{"typ":"lc","txt":"LC_EVENT_item_card_name_{lc_num}"}}',
        ld,
        card_id,
        honor_map[star], recycle_map[star],
        fd
    ])

print(f'  Total 1123 rows: {len(rows_1123)}')
insert_rows(SHEET_1123, GID_1123, 258, 54)
time.sleep(1)

# Write in batches of 18
for batch_start in range(0, 54, 18):
    batch = rows_1123[batch_start:batch_start+18]
    sheet_row = 259 + batch_start
    rng = f'CardGallary!A{sheet_row}:N{sheet_row+len(batch)-1}'
    print(f'  Batch {batch_start//18+1}: writing rows {sheet_row}-{sheet_row+len(batch)-1}...')
    r = gws(['values', 'batchUpdate'],
        {'spreadsheetId': SHEET_1123, 'valueInputOption': 'RAW'},
        {'data':[{'range': rng, 'values': batch}]})
    print(f'  ✅ Batch done')
    time.sleep(0.5)

# ─────────────────────────────────────────────
print('\n=== STEP 6: 1111 item — update 3 rows ===')
def make_1111_row(item_id, name, dk, quality_dk, lc_num, category_param, value_gold, bg_quality):
    return ["", item_id, name, "item_asset", "0", "0",
            dk, quality_dk, "{}",
            f'{{"typ":"lc","txt":"LC_EVENT_item_card_pack_name_{lc_num}"}}',
            f'{{"typ":"lc","txt":"LC_EVENT_item_card_pack_desc_{lc_num}"}}',
            "{}", value_gold, "999999", "99999", "99999",
            '["bag_other","card_pack"]', '["bag","card_pack"]',
            category_param, "-1", "0", "[]", "11740000", "0",
            bg_quality, "1511010003", "0", "0", "1"]

cat_339 = '{"drop":{"typ":"single_random","num":1,"args":[{"typ":"cardquality","id":3,"num":1,"random_add":11081004,"wgt":9000},{"typ":"cardquality","id":4,"num":1,"random_add":11081004,"wgt":1000}]}}'
cat_340 = '{"drop":{"typ":"single_random","num":1,"args":[{"typ":"cardquality","id":3,"num":1,"random_add":11081004,"wgt":8000},{"typ":"cardquality","id":4,"num":1,"random_add":11081004,"wgt":1300},{"typ":"cardquality","id":5,"num":1,"random_add":11081004,"wgt":200}]}}'
cat_341 = '{"drop":{"typ":"single_random","num":1,"args":[{"typ":"cardquality","id":4,"num":1,"random_add":11081004,"wgt":9500},{"typ":"cardquality","id":5,"num":1,"random_add":11081004,"wgt":500}]}}'

rows_1111 = [
    make_1111_row("111111339","拓荒节2026-1-2星卡包","1511094006","1511010121","15",cat_339,"16","3"),
    make_1111_row("111111340","拓荒节2026-1-3星卡包","1511094007","1511010121","16",cat_340,"19","3"),
    make_1111_row("111111341","拓荒节2026-2-3星卡包","1511094008","1511010122","17",cat_341,"36","4"),
]
write_update(SHEET_1111, 'item', 2222, 'AC', rows_1111)

print('\n=== ALL WRITES DONE ===')
print('请手动验证各表的写入结果')
