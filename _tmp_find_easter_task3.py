import re

with open(r'C:\ADHD_agent\_tmp_task_qa.json', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-16', errors='replace')
lines = content.split('\n')

# Structure: each row is a [ ... ] block with fields:
# line 0: group
# line 1: id
# line 2: comment/name
# etc.
# We parse by finding row boundaries

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
        # Process current_row
        if len(current_row) >= 3:
            group_val = current_row[0].strip('"').strip(',').strip()
            id_val = current_row[1].strip('"').strip(',').strip()
            comment_val = current_row[2].strip('"').strip(',').strip()
            
            if id_val.startswith('2115') and id_val.isdigit():
                # Check if comment contains Easter/加速 keywords
                kw_match = re.search(r'(复活节|彩蛋|加速|easter|egg)', comment_val, re.IGNORECASE)
                if kw_match:
                    # Also get fincond if available
                    fincond = current_row[4].strip('"').strip(',') if len(current_row) > 4 else ''
                    results.append({
                        'group': group_val,
                        'id': id_val,
                        'comment': comment_val,
                        'fincond': fincond[:100]
                    })
        current_row = []
    elif in_row:
        # Extract string value
        m = re.match(r'\s*"(.*?)(?<!\\)"[,]?\s*$', line)
        if m:
            current_row.append(m.group(1))
        elif line:
            current_row.append(line)
    i += 1

print(f'Found {len(results)} Easter/加速 tasks with 2115 ID:')
print()
for r in results:
    print(f"ID: {r['id']}")
    print(f"  Group: {r['group']}")
    print(f"  Comment: {r['comment']}")
    print(f"  Fincond: {r['fincond']}")
    print()
