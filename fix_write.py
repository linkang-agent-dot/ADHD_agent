import subprocess
import json
import os
import sys

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '1d7AXDs3Jc4cq0XhyKpsWicqJjHcGa6mZQAr7oH12lsw'
NEW_TAB = '复活节-整理版'

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
        print(f"ERROR updating {range_name}: rc={result.returncode}")
        print(f"  stderr: {result.stderr[:300]}")
        print(f"  stdout: {result.stdout[:300]}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"JSON parse error for {range_name}")
        print(f"  stdout: {result.stdout[:300]}")
        return None

# Reload the same all_rows data
with open('easter_dump.json', 'r', encoding='utf-8') as f:
    rows = json.load(f)

def safe(row, idx, default=''):
    if idx < len(row):
        return row[idx] if row[idx] else default
    return default

# Rebuild all_rows exactly as before
all_rows = []
title_row_indices = []
header_row_indices = []

def add_section(title, headers, data):
    if all_rows:
        all_rows.append([])
    title_row_indices.append(len(all_rows))
    all_rows.append([title])
    header_row_indices.append(len(all_rows))
    all_rows.append(headers)
    all_rows.extend(data)

# Section 1
s1 = []
for i in range(1, 82):
    r = rows[i]
    s1.append([safe(r,0), safe(r,2), safe(r,3), safe(r,5), safe(r,6)])
add_section('【卡片清单】81 张卡片', ['卡组主题','序号','卡片名称','资源ID','卡包名'], s1)

# Section 2
s2 = []
for i in range(1, 25):
    r = rows[i]
    key, cn, en = safe(r,9), safe(r,10), safe(r,11)
    if key or cn or en:
        s2.append([key, cn, en])
add_section('【卡包本地化】12 种卡包 × name/desc', ['Key','中文名/描述','英文名/描述'], s2)

# Section 3
s3 = []
for i in range(27, 49):
    r = rows[i]
    a, b, c, d = safe(r,10), safe(r,11), safe(r,12), safe(r,13)
    if a or b or c or d:
        s3.append([a, b, c, d])
add_section('【卡包描述（修改版）】22 行', ['原文 (中文)','修改后中文','JSON Key','英文翻译'], s3)

# Section 4
s4 = []
for i in range(57, 63):
    r = rows[i]
    a, b, c = safe(r,10), safe(r,11), safe(r,12)
    if a or b or c:
        s4.append([a, b, c])
add_section('【图片描述本地化】6 行', ['图片中文原文','JSON Key','英文翻译'], s4)

# Section 5
s5 = []
for i in range(97, 195):
    r = rows[i]
    s5.append([safe(r,5), safe(r,6), safe(r,7), safe(r,8), safe(r,9)])
add_section('【卡组/卡片本地化详表】9 组 × 10 行', ['编号','简体中文名','JSON 格式 Key','非JSON Key','英文翻译'], s5)

# Section 6
s6 = []
for i in range(197, 206):
    r = rows[i]
    s6.append([safe(r,12), safe(r,6), safe(r,5), safe(r,7), safe(r,14), safe(r,9) or safe(r,15)])
add_section('【大富翁图像文字翻译】9 行', ['序号','中文名称','Key Name','LC_EVENT Key','JSON Key','英文翻译'], s6)

print(f"Total rows: {len(all_rows)}")

# Retry failed ranges in small batches of 10
for start in range(150, min(250, len(all_rows)), 10):
    end = min(start + 10, len(all_rows))
    batch_data = all_rows[start:end]
    range_name = f"'{NEW_TAB}'!A{start+1}"
    resp = gws_values_update(range_name, batch_data)
    if resp:
        print(f"  Wrote rows {start+1}-{end}: OK ({resp.get('updatedRows', '?')} rows)")
    else:
        print(f"  FAILED rows {start+1}-{end}")
        for j, row in enumerate(batch_data):
            single_range = f"'{NEW_TAB}'!A{start+j+1}"
            resp2 = gws_values_update(single_range, [row])
            status = "OK" if resp2 else "FAIL"
            print(f"    Row {start+j+1}: {status} -> {str(row)[:80]}")

print("\nRetry complete!")
