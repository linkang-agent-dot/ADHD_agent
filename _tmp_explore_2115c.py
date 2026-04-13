import re, json

with open(r'C:\ADHD_agent\_tmp_task_qa.json', 'rb') as f:
    raw = f.read()

# Decode as utf-16 (with BOM)
content = raw.decode('utf-16')

# Now try to fix the JSON and parse it
# The problem is there are embedded control characters in string values
# Let's replace them carefully
cleaned = re.sub(r'(?<=": ")(.*?)(?="[,\n])', 
                 lambda m: m.group(0).replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'),
                 content, flags=re.DOTALL)

try:
    data = json.loads(cleaned)
    rows = data.get('values', [])
    print(f'Parsed OK! Total rows: {len(rows)-1}')
except Exception as e:
    # Manual row extraction
    pass

# Manual extraction
lines = content.split('\n')
results = []
i = 0
current_row = []
in_row = False

while i < len(lines):
    line = lines[i].rstrip('\r')
    stripped = line.strip()
    if stripped == '[':
        if not in_row:
            in_row = True
            current_row = []
    elif (stripped in ('],', ']')) and in_row:
        in_row = False
        if len(current_row) >= 3:
            id_val = current_row[1]
            comment_val = current_row[2]
            
            if id_val.startswith('2115') and id_val.isdigit():
                results.append((id_val, comment_val))
        current_row = []
    elif in_row:
        # Extract quoted string value
        m = re.match(r'\s*"((?:[^"\\]|\\.)*)"\s*,?\s*$', line)
        if m:
            current_row.append(m.group(1))
        elif stripped:
            current_row.append(stripped)
    i += 1

print(f'Total 2115 tasks: {len(results)}')

# Write to output file with utf-8
with open(r'C:\ADHD_agent\_tmp_2115_tasks.txt', 'w', encoding='utf-8') as out:
    out.write(f'Total 2115 tasks: {len(results)}\n\n')
    
    # Find Easter/加速 related
    easter_kw = re.compile(r'(复活节|彩蛋|加速|easter|egg|兑换|exchange)', re.IGNORECASE)
    accel_kw = re.compile(r'(加速)', re.IGNORECASE)
    
    easter_results = [(id_val, comment) for id_val, comment in results if easter_kw.search(comment)]
    accel_results = [(id_val, comment) for id_val, comment in results if accel_kw.search(comment)]
    
    out.write(f'=== 含 复活节/彩蛋/加速/兑换 关键词的2115任务: {len(easter_results)} ===\n')
    for id_val, comment in easter_results:
        out.write(f'  {id_val}  {comment[:100]}\n')
    
    out.write(f'\n=== 含 加速 的2115任务: {len(accel_results)} ===\n')
    for id_val, comment in accel_results:
        out.write(f'  {id_val}  {comment[:100]}\n')
    
    # Sample of all
    out.write('\n=== 前100条2115任务 ===\n')
    for id_val, comment in results[:100]:
        out.write(f'  {id_val}  {comment[:80]}\n')

print('Done! Check _tmp_2115_tasks.txt')
