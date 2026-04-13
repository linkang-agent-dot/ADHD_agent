"""Get spreadsheet metadata using gws sheets spreadsheets get."""
import subprocess
import json
import sys

def get_spreadsheet_meta(spreadsheet_id):
    """Get metadata for a spreadsheet including sheet names."""
    # Try using params with JSON
    result = subprocess.run(
        f'gws sheets spreadsheets get --params "{{\\"spreadsheetId\\":\\"{spreadsheet_id}\\"}}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    raw = result.stdout
    stderr = result.stderr.decode('utf-8', errors='replace')
    
    if not raw:
        print(f'No stdout. Stderr: {stderr[:200]}')
        return None
    
    try:
        text = raw.decode('utf-8')
        data = json.loads(text)
        return data
    except Exception as e:
        print(f'Parse error: {e}')
        print(f'Raw (first 300): {repr(raw[:300])}')
        return None

if __name__ == '__main__':
    spreadsheet_id = sys.argv[1]
    data = get_spreadsheet_meta(spreadsheet_id)
    
    if data:
        sheets = data.get('sheets', [])
        if sheets:
            print(f'Found {len(sheets)} sheets:')
            for s in sheets:
                props = s.get('properties', {})
                print(f'  ID: {props.get("sheetId")}, Title: {props.get("title")}, Index: {props.get("index")}')
        else:
            print('Keys in response:', list(data.keys()))
            if 'error' in data:
                print('Error:', data['error'])
