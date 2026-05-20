#!/usr/bin/env python3
import json, subprocess, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'

SID = '1YGVYGjiDxJ2Rx3MEUv4o-xIEzLuG6NL5wW06bisZSyg'
TAB = 'EVENT'

def run_gws(args, jb=None):
    cmd = [GWS] + args
    if jb: cmd.extend(['--json', json.dumps(jb, ensure_ascii=False)])
    r = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None

# 1. 修 BP基金 为通用名
r = run_gws(['sheets', 'spreadsheets', 'values', 'get',
    '--params', json.dumps({'spreadsheetId': SID, 'range': f"'{TAB}'!B:B"})])
for i, b in enumerate((r or {}).get('values', [])):
    if b and b[0].strip() == 'labor_2026_bp_title':
        row = i + 1
        run_gws(['sheets', 'spreadsheets', 'values', 'update',
            '--params', json.dumps({'spreadsheetId': SID, 'range': f"'{TAB}'!C{row}:D{row}", 'valueInputOption': 'RAW'})],
            jb={"values": [["BP集结奖励", "BP Rally Rewards"]]})
        run_gws(['sheets', 'spreadsheets', 'values', 'update',
            '--params', json.dumps({'spreadsheetId': SID, 'range': f"'{TAB}'!H{row}", 'valueInputOption': 'RAW'})],
            jb={"values": [["BP集結獎勵"]]})
        run_gws(['sheets', 'spreadsheets', 'values', 'update',
            '--params', json.dumps({'spreadsheetId': SID, 'range': f"'{TAB}'!T{row}", 'valueInputOption': 'RAW'})],
            jb={"values": [["BP集结奖励"]]})
        print("BP基金 → BP集结奖励 ✓")
        break

# 2. 道具 LC key 列表
item_lc = [
    ("labor_2026_bp_EVENT_title", "纪念钻头", "Memorial Drill"),
    ("labor_2026_bp_EVENT_title_desc", "使用后可提升拓荒节进度", "Use to boost Pioneer Festival progress."),
    ("labor_2026_avatar_title", "头像框", "Avatar Frame"),
    ("labor_2026_city_skin_title", "主城皮肤", "City Skin"),
    ("labor_2026_city_skin_desc", "解锁主城皮肤", "Unlock a unique city skin."),
    ("labor_2026_decoration_1", "装饰物", "Decoration"),
    ("labor_2026_decoration_1_desc", "一件独特的装饰物", "A unique decoration."),
    ("labor_2026_floor_1_title", "地板", "Floor"),
    ("labor_2026_floor_1_title_desc", "一款独特的地板", "A unique floor design."),
    ("labor_2026_gacha_EVENT_title", "抽奖道具", "Gacha Token"),
    ("labor_2026_gacha_EVENT_title_desc", "用于抽奖", "Used for gacha draws."),
    ("labor_2026_gacha_item_title_2", "内圈抽奖道具", "Inner Ring Token"),
    ("labor_2026_gacha_item_title_desc_2", "用于内圈抽奖", "Used for inner ring draws."),
    ("labor_2026_map_emoji_title", "行军表情", "March Emoji"),
    ("labor_2026_map_emoji_title_desc", "一个独特的行军表情", "A unique march emoji."),
    ("labor_2026_march_skin_title", "行军特效", "March Effect"),
    ("labor_2026_march_skin_title_desc", "一个独特的行军特效", "A unique march effect."),
    ("labor_2026_name_plate_title", "铭牌", "Nameplate"),
    ("labor_2026_name_plate_title_desc", "一个独特的铭牌", "A unique nameplate."),
    ("labor_2026_time_card_title_1", "自选周卡-高级", "Weekly Card - Premium"),
    ("labor_2026_time_card_title_2", "自选周卡-中级", "Weekly Card - Standard"),
    ("labor_2026_time_card_title_3", "自选周卡-初级", "Weekly Card - Basic"),
    ("labor_2026_wall_1_title", "墙纸", "Wallpaper"),
    ("labor_2026_wall_1_title_desc", "一款独特的墙纸", "A unique wallpaper."),
    ("labor_2026_wall_decoration_1", "装饰道具", "Wall Decoration"),
    ("labor_2026_wall_decoration_1_desc", "一件独特的墙饰", "A unique wall decoration."),
    ("labor_2026_wall_decoration_3", "墙饰", "Wall Ornament"),
    ("labor_2026_wall_decoration_3_desc", "一件独特的墙饰", "A unique wall ornament."),
    ("labor_2026_wall_decoration_4", "墙饰", "Wall Ornament"),
    ("labor_2026_wall_decoration_4_desc", "一件独特的墙饰", "A unique wall ornament."),
    ("labor_2026_wall_decoration_5", "墙饰", "Wall Ornament"),
    ("labor_2026_wall_decoration_5_desc", "一件独特的墙饰", "A unique wall ornament."),
    ("labor_2026_march_effect_used", "使用行军特效", "Use March Effect"),
    ("labor_2026_march_effect_used_1d", "使用行军特效（1天）", "Use March Effect (1 Day)"),
    ("labor_2026_march_effect_used_3d", "使用行军特效（3天）", "Use March Effect (3 Days)"),
    ("labor_2026_march_effect_used_7d", "使用行军特效（7天）", "Use March Effect (7 Days)"),
    ("labor_2026_march_effect_used_14d", "使用行军特效（14天）", "Use March Effect (14 Days)"),
    ("labor_2026_march_effect_used_30d", "使用行军特效（30天）", "Use March Effect (30 Days)"),
    ("labor_2026_march_skin_desc", "行军特效描述", "A unique march skin."),
]

# 查已存在
r2 = run_gws(['sheets', 'spreadsheets', 'values', 'get',
    '--params', json.dumps({'spreadsheetId': SID, 'range': f"'{TAB}'!B:B"})])
existing = set(b[0].strip() for b in (r2 or {}).get('values', []) if b)

missing = [(k, cn, en) for k, cn, en in item_lc if k not in existing]
print(f"\n道具 LC: {len(missing)} 条需写入")

if not missing:
    print("全部已存在")
    sys.exit(0)

# 读 max ID_int
r3 = run_gws(['sheets', 'spreadsheets', 'values', 'get',
    '--params', json.dumps({'spreadsheetId': SID, 'range': f"'{TAB}'!A:A"})])
all_a = (r3 or {}).get('values', [])
max_int = max((int(a[0]) for a in all_a if a and a[0].strip().isdigit()), default=0)
next_int = max_int + 1
last_row = len(all_a)

# 获取 gid
r_meta = run_gws(['sheets', 'spreadsheets', 'get',
    '--params', json.dumps({'spreadsheetId': SID, 'fields': 'sheets.properties'})])
gid = None
for s in (r_meta or {}).get('sheets', []):
    if s.get('properties', {}).get('title') == TAB:
        gid = s['properties']['sheetId']

# insertDimension
run_gws(['sheets', 'spreadsheets', 'batchUpdate',
    '--params', json.dumps({'spreadsheetId': SID})],
    jb={"requests": [{"insertDimension": {"range": {
        "sheetId": gid, "dimension": "ROWS",
        "startIndex": last_row, "endIndex": last_row + len(missing)},
        "inheritFromBefore": True}}]})

ok = 0
for i, (key, cn, en) in enumerate(missing):
    row = [str(next_int), key, cn, en, en, en, en, cn, en, en, en, en, en, en, en, en, en, en, en, cn]
    next_int += 1
    rng = f"'{TAB}'!A{last_row+i+1}:T{last_row+i+1}"
    resp = run_gws(['sheets', 'spreadsheets', 'values', 'update',
        '--params', json.dumps({'spreadsheetId': SID, 'range': rng, 'valueInputOption': 'RAW'})],
        jb={"values": [row]})
    if resp is not None: ok += 1

print(f"写入 {ok}/{len(missing)}")
