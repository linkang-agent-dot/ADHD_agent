import re

input_file = r"C:\Users\linkang\.cursor\projects\c-ADHD-agent\agent-tools\0b00bf78-8d2b-4b25-aec3-8013bd928e85.txt"
output_file = r"C:\ADHD_agent\output_2115_easter_reskin.txt"

rows = []
with open(input_file, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line.startswith("row "):
            continue
        content = re.sub(r'^row \d+: ', '', line)
        content = content.replace('"id":111110002,', '"id":111110305,')
        content = content.replace('"id":11119772,', '"id":11112500,')
        rows.append(content)

def fix_empty_strings(row):
    # 将行尾的 \t"" 替换为 \t'""
    row = re.sub(r'\t""$', '\t\'""', row)
    # 将中间的 \t""\t 替换为 \t'""\t
    row = re.sub(r'\t""\t', '\t\'""\t', row)
    return row

with open(output_file, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(fix_empty_strings(r) + "\n")

print(f"Done: {len(rows)} rows written")
old_ids = sum(1 for r in rows if '11119772' in r or '111110002' in r)
new_bp = sum(1 for r in rows if '11112500' in r)
new_card = sum(1 for r in rows if '111110305' in r)
print(f"残留旧ID行数: {old_ids} (应为0)")
print(f"含11112500(复活节BP箱): {new_bp} 行")
print(f"含111110305(复活节卡包): {new_card} 行")
