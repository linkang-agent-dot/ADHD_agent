import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

fname = sys.argv[1]
max_rows = int(sys.argv[2]) if len(sys.argv) > 2 else 30

with open(fname, 'rb') as f:
    content = f.read()

# Remove BOM
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]

text = content.decode('utf-8', errors='replace')
data = json.loads(text, strict=False)
rows = data.get('values', [])
print(f'Total rows: {len(rows)}')
print(f'Sheet range: {data.get("range", "")}')
for i, row in enumerate(rows[:max_rows]):
    print(f'Row {i+1}: {row}')
