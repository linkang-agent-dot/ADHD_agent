"""Get sheet names and write directly to file to avoid PowerShell encoding issues."""
import subprocess
import json
import sys

def get_sheets(spreadsheet_id):
    result = subprocess.run(
        f'gws sheets spreadsheets get --params "{{\\"spreadsheetId\\":\\"{spreadsheet_id}\\"}}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    raw = result.stdout.decode('utf-8')
    data = json.loads(raw)
    return data.get('sheets', [])

if __name__ == '__main__':
    spreadsheet_id = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    sheets = get_sheets(spreadsheet_id)
    
    lines = [f'Found {len(sheets)} sheets:']
    for s in sheets:
        props = s.get('properties', {})
        sheet_id = props.get('sheetId')
        title = props.get('title', '')
        index = props.get('index')
        lines.append(f'  ID: {sheet_id}, Index: {index}, Title: {title}')
    
    output = '\n'.join(lines)
    
    if out_file:
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Written to {out_file}')
    else:
        print(output)
