"""Debug sheet name comparison."""
import subprocess
import json
import sys

GWS_PS1 = r'C:\Users\linkang\AppData\Roaming\npm\gws.ps1'
TEMPLATE_SPREADSHEET_ID = '1YYZioyzHx44J6yw5UiagnwZS4-cx0ozl74BJjlCQ9X8'

def run_ps1(script_content):
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8', newline='') as f:
        f.write(script_content)
        ps1_file = f.name
    try:
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-File', ps1_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.stdout, result.stderr
    finally:
        os.unlink(ps1_file)

# Get sheet names
script = f'& "{GWS_PS1}" sheets spreadsheets get --params \'{{"spreadsheetId":"{TEMPLATE_SPREADSHEET_ID}"}}\''
stdout, stderr = run_ps1(script)

stdout_text = stdout.decode('utf-8', errors='replace')
stderr_text = stderr.decode('utf-8', errors='replace')

if stdout_text.strip():
    data = json.loads(stdout_text, strict=False)
    sheets = data.get('sheets', [])
    
    with open('C:/ADHD_agent/tmp_sheet_names_debug.txt', 'w', encoding='utf-8') as f:
        f.write(f'Found {len(sheets)} sheets:\n')
        for s in sheets[:10]:
            title = s.get('properties', {}).get('title', '')
            sid = s.get('properties', {}).get('sheetId', '')
            f.write(f'  ID: {sid}, Title: {repr(title)}\n')
    print(f'Written to tmp_sheet_names_debug.txt')
else:
    print(f'No output. Stderr: {stderr_text[:300]}')
