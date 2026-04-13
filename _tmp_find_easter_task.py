import re, json

with open(r'C:\ADHD_agent\_tmp_task_qa.json', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-16', errors='replace')

# Try to parse as JSON with relaxed handling
# Replace problematic chars in string values only
# Strategy: replace control chars that break JSON parsing
cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', content)

try:
    data = json.loads(cleaned)
    rows = data.get('values', [])
    header = rows[0] if rows else []
    print('Header:', header[:10])
    print('Total rows:', len(rows)-1)
    
    # Search for Easter/加速 tasks with 2115 ID
    keywords = ['复活节', '彩蛋', '加速', 'easter', 'egg', 'accelerat']
    results = []
    for row in rows[1:]:
        if not row:
            continue
        id_val = str(row[0]) if row else ''
        if not id_val.startswith('2115'):
            continue
        row_str = ' '.join(str(c) for c in row).lower()
        if any(kw.lower() in row_str for kw in keywords):
            results.append(row)
    
    print(f'\nEaster/加速 tasks with 2115 ID: {len(results)}')
    for r in results:
        print(r[:8])

except json.JSONDecodeError as e:
    print(f'JSON error: {e}')
    # Fallback: search line by line
    lines = content.split('\n')
    print(f'Total lines: {len(lines)}')
    
    # Look for array structure - find rows containing 2115 IDs with nearby text
    # The gws output format has each row as an array
    # Let's find 2115 IDs and look at surrounding context
    id_pat = re.compile(r'"(2115\d{5,})"')
    easter_kw = re.compile(r'(复活节|彩蛋|加速|easter|egg)', re.IGNORECASE)
    
    i = 0
    while i < len(lines):
        line = lines[i]
        m = id_pat.search(line)
        if m:
            id_val = m.group(1)
            # Check context (±5 lines)
            ctx_start = max(0, i-2)
            ctx_end = min(len(lines), i+10)
            context = '\n'.join(lines[ctx_start:ctx_end])
            if easter_kw.search(context):
                print(f'--- ID {id_val} (line {i}) ---')
                print(context[:300])
                print()
        i += 1
