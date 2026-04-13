import json
SHEET = "评分表（每月更新）"
params = {
    "spreadsheetId": "1ElKLw7zvz2-vjcgNkjpC54d6nW04lke_NWOPQs0Uq0Q",
    "range": f"'{SHEET}'!A34:P56",
    "valueInputOption": "USER_ENTERED"
}
# 用 ASCII-only (ensure_ascii=True) 避免编码问题
s = json.dumps(params, ensure_ascii=True)
with open(r'C:\ADHD_agent\_tmp_params_v4.json', 'w', encoding='ascii') as f:
    f.write(s)
print("Wrote:", s[:100])
