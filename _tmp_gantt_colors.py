import subprocess, json

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

TARGET_SHEETS = {
    'X2前期节日循环': {'range': 'H1:P25', 'gantt_start_col': 8},   # 列H=数值/链接, I=第1周... (col index 0-based: 8=H)
    'X2-5月占星节':   {'range': 'G1:P30', 'gantt_start_col': 7},
    'X2-6月拓荒节':   {'range': 'G1:P42', 'gantt_start_col': 7},
    'X2-7月烟火庆典': {'range': 'G1:S35', 'gantt_start_col': 7},
}

# Use spreadsheets.get with includeGridData=true to get cell background colors
# But limit to specific ranges to avoid huge response

results = {}

for sheet_name, cfg in TARGET_SHEETS.items():
    params = json.dumps({
        'spreadsheetId': SPREADSHEET_ID,
        'ranges': f"{sheet_name}!{cfg['range']}",
        'includeGridData': True,
        'fields': 'sheets.data.rowData.values.userEnteredFormat.backgroundColor,sheets.data.rowData.values.formattedValue'
    })
    result = subprocess.run(
        [GWS_CMD, 'sheets', 'spreadsheets', 'get', '--params', params],
        capture_output=True, text=True, encoding='utf-8'
    )
    try:
        data = json.loads(result.stdout)
        results[sheet_name] = data
        print(f'{sheet_name}: OK')
    except Exception as e:
        print(f'{sheet_name}: ERROR - {e}')
        print(result.stdout[:200])
        print(result.stderr[:200])

with open(r'C:\ADHD_agent\_tmp_gantt_colors.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('保存完成')
