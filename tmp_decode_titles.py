"""Decode the garbled sheet titles."""
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
    
    sheets = get_sheets(spreadsheet_id)
    
    sys.stdout.buffer.write(f'Found {len(sheets)} sheets:\n'.encode('utf-8'))
    for s in sheets:
        props = s.get('properties', {})
        sheet_id = props.get('sheetId')
        title = props.get('title', '')
        title_bytes = title.encode('utf-8')
        sys.stdout.buffer.write(f'  ID: {sheet_id}, Title: {title}\n'.encode('utf-8'))
