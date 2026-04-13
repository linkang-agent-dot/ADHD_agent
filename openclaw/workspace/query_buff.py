import subprocess, json

gws_cmd = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
sid = '1qqn6vjWJ30-TW-kXzN3Aa9eS1fyoTFwPSWdXyNZbauc'
buff_ids = {'12117002', '12117020', '12117011', '12117010', '121140935'}
results = []

for start in range(1, 10001, 2000):
    end = start + 1999
    range_str = f'buff!A{start}:C{end}'
    r = subprocess.run([gws_cmd, 'sheets', '+read', '--spreadsheet', sid, '--range', range_str, '--format', 'json'],
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        continue
    data = json.loads(r.stdout)
    rows = data.get('values', [])
    for row in rows:
        if len(row) > 0 and str(row[0]).strip() in buff_ids:
            col1 = row[1] if len(row) > 1 else ''
            col2 = row[2] if len(row) > 2 else ''
            results.append(f'{row[0]}\t{col1}\t{col2}')
            buff_ids.discard(str(row[0]).strip())
    if not buff_ids:
        break

with open(r'c:\ADHD_agent\openclaw\workspace\buff_result.txt', 'w', encoding='utf-8') as f:
    for line in results:
        f.write(line + '\n')
    if buff_ids:
        f.write(f'MISSING: {buff_ids}\n')
