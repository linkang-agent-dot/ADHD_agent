import re, json

with open(r'C:\ADHD_agent\_tmp_task_abc_utf8.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()

content_fixed = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', content)
data = json.loads(content_fixed)
rows = data.get('values', [])

# Search for Easter/加速
easter_kw = re.compile(r'(复活节|彩蛋|加速|easter|egg|兑换)', re.IGNORECASE)

# Print results to file with utf-8 BOM
with open(r'C:\ADHD_agent\_tmp_easter_accel_results.txt', 'w', encoding='utf-8-sig') as out:
    results_2115 = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        id_val = str(row[1]) if len(row) > 1 else str(row[0])
        comment = row[2] if len(row) > 2 else ''
        
        if id_val.startswith('2115') and id_val.isdigit():
            if easter_kw.search(comment):
                results_2115.append(row)
    
    out.write(f'复活节/彩蛋/加速 任务 (2115 IDs): 共 {len(results_2115)} 条\n\n')
    
    # Group by comment prefix to understand
    for row in results_2115:
        out.write(f"ID: {row[1]}  Group: {row[0]}  Comment: {row[2][:100] if len(row)>2 else ''}\n")
    
    # Also search specifically for "彩蛋" and "兑换" 
    out.write('\n\n=== 仅含 彩蛋 关键词 ===\n')
    egg_only = [(row[1], row[2] if len(row)>2 else '') for row in rows[1:] 
                if len(row)>=2 and str(row[1]).startswith('2115') and '彩蛋' in str(row[2] if len(row)>2 else '')]
    out.write(f'共 {len(egg_only)} 条\n')
    for id_val, comment in egg_only:
        out.write(f'  {id_val}: {comment[:100]}\n')
    
    # "兑换" keyword  
    out.write('\n=== 仅含 兑换 关键词 ===\n')
    exchange = [(row[1], row[2] if len(row)>2 else '') for row in rows[1:]
                if len(row)>=2 and str(row[1]).startswith('2115') and '兑换' in str(row[2] if len(row)>2 else '')]
    out.write(f'共 {len(exchange)} 条\n')
    for id_val, comment in exchange[:30]:
        out.write(f'  {id_val}: {comment[:100]}\n')

print('Results written to _tmp_easter_accel_results.txt')
