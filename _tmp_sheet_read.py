import subprocess, json, sys

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'
TARGET_GID = 923559126

# Step 1: Get all sheet names
params_meta = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'fields': 'sheets.properties'})
result = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'get', '--params', params_meta],
    capture_output=True, text=True, encoding='utf-8'
)
meta = json.loads(result.stdout)

target_name = None
all_sheets = []
for sheet in meta.get('sheets', []):
    p = sheet['properties']
    gid = p.get('sheetId', -1)
    title = p.get('title', '')
    all_sheets.append((gid, title))
    if gid == TARGET_GID:
        target_name = title

# Step 2: Read ALL sheets (to analyze full schedule)
output = {'target_sheet': target_name, 'all_sheets': [], 'schedule_data': {}}
for gid, title in all_sheets:
    output['all_sheets'].append({'gid': gid, 'title': title})

# Read target sheet with wider range
params_read = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': f'{target_name}!A1:Z100'})
result2 = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params_read],
    capture_output=True, text=True, encoding='utf-8'
)
data = json.loads(result2.stdout)
output['schedule_data'][target_name] = data.get('values', [])

# Also read the main overview sheet
main_sheet = all_sheets[0][1]  # X2整体节日规划
params_main = json.dumps({'spreadsheetId': SPREADSHEET_ID, 'range': f'{main_sheet}!A1:Z100'})
result3 = subprocess.run(
    [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params_main],
    capture_output=True, text=True, encoding='utf-8'
)
data3 = json.loads(result3.stdout)
output['schedule_data'][main_sheet] = data3.get('values', [])

# Save to file for analysis
with open(r'C:\ADHD_agent\_tmp_schedule_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f'目标页签: {target_name}')
print(f'所有页签: {[t for _, t in all_sheets]}')
print(f'目标页签行数: {len(output["schedule_data"][target_name])}')
print(f'主页签行数: {len(output["schedule_data"][main_sheet])}')
print('数据已保存到 _tmp_schedule_data.json')
