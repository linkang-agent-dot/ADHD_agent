import re

with open(r'C:\ADHD_agent\_tmp_task_qa.json', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-16', errors='replace')

lines = content.split('\n')
id_pat = re.compile(r'^\s*"(2115\d+)"')
found_ids = []
for line in lines:
    m = id_pat.match(line)
    if m:
        found_ids.append(m.group(1))

print('2115 IDs found:')
for id_val in sorted(set(found_ids)):
    print(id_val)
print(f'Total unique: {len(set(found_ids))}')
