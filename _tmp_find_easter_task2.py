import re

with open(r'C:\ADHD_agent\_tmp_task_qa.json', 'rb') as f:
    raw = f.read()

content = raw.decode('utf-16', errors='replace')

# The gws output is structured as:
# { "values": [ [col1, col2, ...], [col1, col2, ...], ... ] }
# Each row is a JSON array.
# Let's extract rows by parsing line by line looking for array boundaries

# Strategy: find lines that start a row (contain a 2115 ID), 
# then read forward to find the name column

lines = content.split('\n')

easter_kw = re.compile(r'(复活节|彩蛋|加速|easter|egg)', re.IGNORECASE)
id_pat = re.compile(r'"(2115\d{5,})"')

# Check what columns look like by viewing first few rows
print('=== First 30 lines of content ===')
for i, line in enumerate(lines[:30]):
    print(f'{i:4d}: {repr(line[:120])}')
