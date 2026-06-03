# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-各活动模块"
def gws(a):
    p=subprocess.run(['node',WRAPPER],input=json.dumps({"args":a},ensure_ascii=False),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1:C237"})])).get('values',[])
out=[]
for i,r in enumerate(rows):
    t=" | ".join(c for c in r if c)
    out.append(f"R{i+1}: {t}")
open("C:/ADHD_agent/_tmp_scripts/moddump.txt","w",encoding="utf-8").write("\n".join(out))
print("ok",len(rows))
