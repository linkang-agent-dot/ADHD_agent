"""Use subprocess to call gws and capture UTF-8 output properly."""
import subprocess
import json
import sys

def gws_read(spreadsheet_id, range_name):
    result = subprocess.run(
        f'gws sheets +read --spreadsheet {spreadsheet_id} --range "{range_name}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    raw = result.stdout
    # gws outputs UTF-8
    text = raw.decode('utf-8', errors='replace')
    data = json.loads(text, strict=False)
    return data

if __name__ == '__main__':
    spreadsheet_id = sys.argv[1]
    range_name = sys.argv[2]
    max_rows = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    data = gws_read(spreadsheet_id, range_name)
    rows = data.get('values', [])
    sys.stdout.reconfigure(encoding='utf-8')
    print(f'Total rows: {len(rows)}')
    print(f'Sheet range: {data.get("range", "")}')
    for i, row in enumerate(rows[:max_rows]):
        print(f'Row {i+1}: {row}')
