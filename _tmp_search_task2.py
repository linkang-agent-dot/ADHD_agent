import re, json

with open(r'C:\ADHD_agent\_tmp_task_abc_utf8.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Fix embedded control chars (newlines in strings)
content_fixed = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', content)

try:
    data = json.loads(content_fixed)
    rows = data.get('values', [])
    print(f'Parsed OK! Total rows: {len(rows)-1}')
    print('Header:', rows[0] if rows else [])
    print()
    
    # Show first 5 rows
    for row in rows[1:6]:
        print(row)
    
    # Search for Easter/加速
    easter_kw = re.compile(r'(复活节|彩蛋|加速|easter|egg|兑换)', re.IGNORECASE)
    
    results_2115 = []
    for row in rows[1:]:
        if not row or len(row) < 2:
            continue
        id_val = str(row[1]) if len(row) > 1 else str(row[0])
        comment = row[2] if len(row) > 2 else ''
        
        if id_val.startswith('2115') and id_val.isdigit():
            if easter_kw.search(comment):
                results_2115.append(row)
    
    print(f'\n=== Easter/加速 tasks with 2115 ID: {len(results_2115)} ===')
    for r in results_2115:
        print(r)
    
    # Also search across all IDs for Easter/加速
    print(f'\n=== Any 加速 tasks ===')
    accel = [(row[1], row[2]) for row in rows[1:] if len(row) >= 3 and '加速' in str(row[2])]
    print(f'Total 加速 tasks: {len(accel)}')
    for id_val, comment in accel[:20]:
        print(f'  {id_val}: {comment[:80]}')
        
except json.JSONDecodeError as e:
    print(f'JSON error: {e}')
    # Show context
    start = max(0, e.pos - 50)
    end = min(len(content_fixed), e.pos + 50)
    print(f'Context: {repr(content_fixed[start:end])}')
