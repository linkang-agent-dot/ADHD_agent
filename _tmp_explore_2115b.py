import re, sys, io, json

# Try different encodings
for enc in ['utf-8', 'gbk', 'gb2312', 'cp936', 'utf-8-sig']:
    try:
        with open(r'C:\ADHD_agent\_tmp_task_qa.json', 'r', encoding=enc) as f:
            first_line = f.readline()
        print(f'{enc}: OK - first line: {first_line[:50]}')
        break
    except Exception as e:
        print(f'{enc}: FAIL - {e}')
