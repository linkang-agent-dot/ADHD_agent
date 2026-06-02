# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-各活动模块"
def gws(a):
    p=subprocess.run(['node',WRAPPER],input=json.dumps({"args":a},ensure_ascii=False),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1:C260"})])).get('values',[])
out=[]
for i,r in enumerate(rows):
    txt=" | ".join(r)
    if "美术需求" in txt: out.append(f"HDR R{i+1}: {txt[:60]}")
    elif ("▌" in txt): out.append(f"MOD R{i+1}: {txt[:50]}")
print("\n".join(out)); print("TOTAL_ROWS:",len(rows))
