# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-各活动模块"
def gws(a):
    p=subprocess.run(['node',WRAPPER],input=json.dumps({"args":a},ensure_ascii=False),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
for r in [36,187]:
    v=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!C{r}"})])).get('values',[[""]])[0][0]
    open(f"C:/ADHD_agent/_tmp_scripts/cell{r}.txt","w",encoding="utf-8").write(v)
print("ok")
