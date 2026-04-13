import re, json

# Try reading the utf8 file
for enc in ['utf-8-sig', 'utf-8', 'utf-16']:
    try:
        with open(r'C:\ADHD_agent\_tmp_task_abc_utf8.json', 'r', encoding=enc) as f:
            first_bytes = f.read(100)
        print(f'{enc}: {repr(first_bytes[:80])}')
        break
    except Exception as e:
        print(f'{enc}: FAIL - {e}')
