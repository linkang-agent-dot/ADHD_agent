import subprocess, json

GWS_CMD = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SPREADSHEET_ID = '19cGUaviqgBBY5GgYG8OREAMpVrkEe6F5tP9T1vLHHBA'

# gid -> sheet name mapping (already known from previous read)
TARGET_SHEETS = {
    923559126: 'X2前期节日循环',
    166650109: 'X2-5月占星节',
    287098073: 'X2-6月拓荒节',
    1053666315: 'X2-7月烟火庆典',
}

all_data = {}

for gid, name in TARGET_SHEETS.items():
    params = json.dumps({
        'spreadsheetId': SPREADSHEET_ID,
        'range': f'{name}!A1:AM100'  # AM = ~40 columns to capture gantt
    })
    result = subprocess.run(
        [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
        capture_output=True, text=True, encoding='utf-8'
    )
    data = json.loads(result.stdout)
    values = data.get('values', [])
    all_data[name] = values
    print(f'{name}: {len(values)} 行')

with open(r'C:\ADHD_agent\_tmp_gantt_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print('已保存到 _tmp_gantt_data.json')
