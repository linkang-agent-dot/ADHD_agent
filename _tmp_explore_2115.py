import re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\ADHD_agent\_tmp_task_qa.json', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-16', errors='replace')
lines = content.split('\n')

results = []
i = 0
current_row = []
in_row = False

while i < len(lines):
    line = lines[i].strip().rstrip('\r')
    if line == '[':
        if not in_row:
            in_row = True
            current_row = []
    elif line in ('],', ']') and in_row:
        in_row = False
        if len(current_row) >= 3:
            group_val = current_row[0].strip('"').strip(',').strip()
            id_val = current_row[1].strip('"').strip(',').strip()
            comment_val = current_row[2].strip('"').strip(',').strip()
            
            if id_val.startswith('2115') and id_val.isdigit():
                results.append({
                    'group': group_val,
                    'id': id_val,
                    'comment': comment_val,
                })
        current_row = []
    elif in_row:
        m = re.match(r'\s*"(.*?)(?<!\\)"[,]?\s*$', line)
        if m:
            current_row.append(m.group(1))
        elif line:
            current_row.append(line)
    i += 1

print(f'Total 2115 tasks: {len(results)}')

# Find any 加速 related mentions
speed_kw = re.compile(r'(加速|speed|acceler|\u5feb\u901f|\u5efa\u9020|\u5efa\u7b51|\u79d1\u7814|\u8bad\u7ec3|\u6cbb\u7597)', re.IGNORECASE)
speed_results = [r for r in results if speed_kw.search(r['comment'])]
print(f'Found 加速/建造/训练 etc: {len(speed_results)}')
for r in speed_results[:30]:
    print(f"  {r['id']}  {r['comment'][:80]}")

# Also search for 彩蛋 or egg
egg_kw = re.compile(r'(\u5f69\u86cb|egg|\u590d\u6d3b\u8282|easter)', re.IGNORECASE)
egg_results = [r for r in results if egg_kw.search(r['comment'])]
print(f'\n彩蛋/复活节 tasks: {len(egg_results)}')
for r in egg_results[:30]:
    print(f"  {r['id']}  {r['comment'][:80]}")

# Show unique comment prefixes to understand naming
print('\n=== Unique comment patterns (sample) ===')
seen = set()
for r in results:
    prefix = r['comment'][:10]
    if prefix not in seen:
        seen.add(prefix)
        print(f"  {r['id']}  {r['comment'][:60]}")
    if len(seen) >= 30:
        break
