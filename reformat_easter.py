import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
NEW_TAB = '复活节-整理版'

def gws_batch_update(requests_list):
    params = json.dumps({'spreadsheetId': SPREADSHEET_ID})
    body = json.dumps({'requests': requests_list}, ensure_ascii=False)
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'batchUpdate', '--params', params, '--json', body]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"ERROR batchUpdate: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"JSON parse error: {result.stdout[:500]}", file=sys.stderr)
        return None

def gws_values_update(range_name, values, value_input_option='RAW'):
    params = json.dumps({
        'spreadsheetId': SPREADSHEET_ID,
        'range': range_name,
        'valueInputOption': value_input_option,
    })
    body = json.dumps({'values': values}, ensure_ascii=False)
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'update', '--params', params, '--json', body]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"ERROR updating {range_name}: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"JSON parse error for {range_name}: {result.stdout[:300]}", file=sys.stderr)
        return None

# ── Step 1: Load previously dumped data ──
with open('easter_dump.json', 'r', encoding='utf-8') as f:
    rows = json.load(f)
print(f"Loaded {len(rows)} rows from easter_dump.json")

def safe(row, idx, default=''):
    if idx < len(row):
        return row[idx] if row[idx] else default
    return default

# ── Step 2: Extract 6 sections ──

# Section 1: Card List (R2-R82 = indices 1-81)
section1_data = []
for i in range(1, 82):
    r = rows[i]
    section1_data.append([
        safe(r, 0),   # 卡组主题
        safe(r, 2),   # 序号
        safe(r, 3),   # 卡片名称
        safe(r, 5),   # 资源ID
        safe(r, 6),   # 卡包名
    ])
print(f"Section 1 (Card List): {len(section1_data)} rows")

# Section 2: Pack Key Localization (R2-R25 = indices 1-24, cols J-L = idx 9-11)
section2_data = []
for i in range(1, 25):
    r = rows[i]
    key = safe(r, 9)
    cn = safe(r, 10)
    en = safe(r, 11)
    if key or cn or en:
        section2_data.append([key, cn, en])
print(f"Section 2 (Pack Key Loc): {len(section2_data)} rows")

# Section 3: Pack Description Localization (R28-R49 = indices 27-48, cols K-N = idx 10-13)
# R27 (idx 26) is a header row
section3_data = []
for i in range(27, 49):
    r = rows[i]
    col_k = safe(r, 10)
    col_l = safe(r, 11)
    col_m = safe(r, 12)
    col_n = safe(r, 13)
    if col_k or col_l or col_m or col_n:
        section3_data.append([col_k, col_l, col_m, col_n])
print(f"Section 3 (Pack Desc Loc): {len(section3_data)} rows")

# Section 4: Image Description Localization (R58-R63 = indices 57-62, cols K-M = idx 10-12)
section4_data = []
for i in range(57, 63):
    r = rows[i]
    col_k = safe(r, 10)
    col_l = safe(r, 11)
    col_m = safe(r, 12)
    if col_k or col_l or col_m:
        section4_data.append([col_k, col_l, col_m])
print(f"Section 4 (Image Desc Loc): {len(section4_data)} rows")

# Section 5: Card Group/Card Localization Detail (R98-R195 = indices 97-194, cols F-J = idx 5-9)
section5_data = []
for i in range(97, 195):
    r = rows[i]
    section5_data.append([
        safe(r, 5),   # 编号
        safe(r, 6),   # 中文名
        safe(r, 7),   # JSON Key
        safe(r, 8),   # 非JSON Key
        safe(r, 9),   # 英文翻译
    ])
print(f"Section 5 (Card/Group Detail): {len(section5_data)} rows")

# Section 6: Tycoon Image Text (R198-R206 = indices 197-205)
# Left side: idx 5(KEY_NAME), 6(中文), 7(LC_KEY), 9(EN)
# Right side: idx 12(序号), 13(中文), 14(JSON), 15(EN)
section6_data = []
for i in range(197, 206):
    r = rows[i]
    section6_data.append([
        safe(r, 12),  # 序号
        safe(r, 6),   # 中文
        safe(r, 5),   # 大写 Key Name
        safe(r, 7),   # LC_EVENT Key
        safe(r, 14),  # JSON Key
        safe(r, 9) or safe(r, 15),   # 英文翻译
    ])
print(f"Section 6 (Tycoon Image Text): {len(section6_data)} rows")

# ── Step 3: Create new tab ──
print(f"\nCreating new tab: {NEW_TAB}")
add_sheet_req = {
    'addSheet': {
        'properties': {
            'title': NEW_TAB,
            'gridProperties': {
                'rowCount': 300,
                'columnCount': 20
            }
        }
    }
}
resp = gws_batch_update([add_sheet_req])
if resp is None:
    print("Failed to create new tab!")
    sys.exit(1)

new_sheet_id = resp['replies'][0]['addSheet']['properties']['sheetId']
print(f"New tab created, sheetId = {new_sheet_id}")

# ── Step 4: Build all rows for the new tab ──
all_rows = []
title_row_indices = []
header_row_indices = []

def add_section(title, headers, data):
    if all_rows:
        all_rows.append([])  # blank separator row
    title_row_indices.append(len(all_rows))
    all_rows.append([title])
    header_row_indices.append(len(all_rows))
    all_rows.append(headers)
    all_rows.extend(data)

add_section(
    '【卡片清单】81 张卡片',
    ['卡组主题', '序号', '卡片名称', '资源ID', '卡包名'],
    section1_data
)

add_section(
    '【卡包本地化】12 种卡包 × name/desc',
    ['Key', '中文名/描述', '英文名/描述'],
    section2_data
)

add_section(
    '【卡包描述（修改版）】22 行',
    ['原文 (中文)', '修改后中文', 'JSON Key', '英文翻译'],
    section3_data
)

add_section(
    '【图片描述本地化】6 行',
    ['图片中文原文', 'JSON Key', '英文翻译'],
    section4_data
)

add_section(
    '【卡组/卡片本地化详表】9 组 × 10 行',
    ['编号', '简体中文名', 'JSON 格式 Key', '非JSON Key', '英文翻译'],
    section5_data
)

add_section(
    '【大富翁图像文字翻译】9 行',
    ['序号', '中文名称', 'Key Name', 'LC_EVENT Key', 'JSON Key', '英文翻译'],
    section6_data
)

print(f"\nTotal rows to write: {len(all_rows)}")
print(f"Title rows at: {title_row_indices}")
print(f"Header rows at: {header_row_indices}")

# ── Step 5: Write data in batches ──
BATCH = 50
for start in range(0, len(all_rows), BATCH):
    end = min(start + BATCH, len(all_rows))
    batch_data = all_rows[start:end]
    range_name = f"'{NEW_TAB}'!A{start+1}"
    resp = gws_values_update(range_name, batch_data)
    if resp:
        print(f"  Wrote rows {start+1}-{end}: OK ({resp.get('updatedRows', '?')} rows)")
    else:
        print(f"  ERROR writing rows {start+1}-{end}")

print("\nData write complete!")

# ── Step 6: Format title rows and header rows ──
format_requests = []

for idx in title_row_indices:
    format_requests.append({
        'repeatCell': {
            'range': {
                'sheetId': new_sheet_id,
                'startRowIndex': idx,
                'endRowIndex': idx + 1,
                'startColumnIndex': 0,
                'endColumnIndex': 10
            },
            'cell': {
                'userEnteredFormat': {
                    'textFormat': {'bold': True, 'fontSize': 12},
                    'backgroundColor': {
                        'red': 0.85, 'green': 0.92, 'blue': 1.0
                    }
                }
            },
            'fields': 'userEnteredFormat(textFormat,backgroundColor)'
        }
    })

for idx in header_row_indices:
    format_requests.append({
        'repeatCell': {
            'range': {
                'sheetId': new_sheet_id,
                'startRowIndex': idx,
                'endRowIndex': idx + 1,
                'startColumnIndex': 0,
                'endColumnIndex': 10
            },
            'cell': {
                'userEnteredFormat': {
                    'textFormat': {'bold': True},
                    'backgroundColor': {
                        'red': 0.95, 'green': 0.95, 'blue': 0.95
                    }
                }
            },
            'fields': 'userEnteredFormat(textFormat,backgroundColor)'
        }
    })

# Freeze row 1 (title)
format_requests.append({
    'updateSheetProperties': {
        'properties': {
            'sheetId': new_sheet_id,
            'gridProperties': {
                'frozenRowCount': 0
            }
        },
        'fields': 'gridProperties.frozenRowCount'
    }
})

# Auto-resize columns
format_requests.append({
    'autoResizeDimensions': {
        'dimensions': {
            'sheetId': new_sheet_id,
            'dimension': 'COLUMNS',
            'startIndex': 0,
            'endIndex': 10
        }
    }
})

print("\nApplying formatting...")
resp = gws_batch_update(format_requests)
if resp:
    print("Formatting applied successfully!")
else:
    print("ERROR applying formatting!")

print("\nDone! New tab '复活节-整理版' created and formatted.")
