"""Parse gws output properly using subprocess to avoid encoding issues."""
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
    # gws outputs proper UTF-8
    text = raw.decode('utf-8')
    data = json.loads(text)
    return data

if __name__ == '__main__':
    spreadsheet_id = sys.argv[1]
    range_name = sys.argv[2]
    max_rows = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    out_file = sys.argv[4] if len(sys.argv) > 4 else None
    
    data = gws_read(spreadsheet_id, range_name)
    rows = data.get('values', [])
    
    lines = []
    lines.append(f'Total rows: {len(rows)}')
    lines.append(f'Sheet range: {data.get("range", "")}')
    for i, row in enumerate(rows[:max_rows]):
        lines.append(f'Row {i+1}: {row}')
    
    output = '\n'.join(lines)
    
    if out_file:
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Written to {out_file}')
    else:
        sys.stdout.buffer.write(output.encode('utf-8'))
        sys.stdout.buffer.write(b'\n')
