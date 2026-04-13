import json
import sys

fname = sys.argv[1]
max_rows = int(sys.argv[2]) if len(sys.argv) > 2 else 30

with open(fname, 'r', encoding='utf-8-sig') as f:
    raw = f.read()

data = json.loads(raw)
rows = data.get('values', [])
sheet_range = data.get('range', '')
print(f'Total rows: {len(rows)}')
print(f'Sheet range: {sheet_range}')
for i, row in enumerate(rows[:max_rows]):
    print(f'Row {i+1}: {row}')
