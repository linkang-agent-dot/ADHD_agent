"""List sheet names by trying common month names and checking which ones work."""
import subprocess
import json
import sys

def try_read_range(spreadsheet_id, range_name):
    """Try to read a range and return True if it has data."""
    result = subprocess.run(
        f'gws sheets +read --spreadsheet {spreadsheet_id} --range "{range_name}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    raw = result.stdout
    try:
        text = raw.decode('utf-8')
        data = json.loads(text)
        rows = data.get('values', [])
        if rows:
            return True, rows[:3]
        return True, []
    except Exception as e:
        return False, str(e)

def get_all_sheet_data(spreadsheet_id):
    """Get sheet metadata by using a special range request."""
    # Use a broad range to see which sheet is the default
    result = subprocess.run(
        f'gws sheets +read --spreadsheet {spreadsheet_id} --range "A1:A1"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    raw = result.stdout.decode('utf-8')
    data = json.loads(raw)
    # The range includes the sheet name
    sheet_range = data.get('range', '')
    print(f'Default sheet range: {sheet_range}')
    return sheet_range

if __name__ == '__main__':
    spreadsheet_id = sys.argv[1]
    
    # Get default sheet name
    default_range = get_all_sheet_data(spreadsheet_id)
    
    # Try potential sheet names
    candidate_names = [
        '4月排期', '4月', 'April', '科技节', '四月', 
        '排期总览', '活动排期', '4月活动',
        '科技节排期', '2026科技节',
        'Sheet1', '汇总', '总览',
        '活动清单', '4月活动清单',
    ]
    
    print('\nTrying candidate sheet names:')
    for name in candidate_names:
        ok, result = try_read_range(spreadsheet_id, f"'{name}'!A1:C5")
        if ok and result:
            print(f'  FOUND: {name} -> {result[:2]}')
        elif ok:
            print(f'  EMPTY: {name}')
