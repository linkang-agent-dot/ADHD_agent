# -*- coding: utf-8 -*-
import subprocess, json, os, io, re
os.environ['GOOGLE_WORKSPACE_PROJECT_ID']='calm-repeater-489707-n1'
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'
def gws(a):
    p=subprocess.run(['node',WRAPPER],input=json.dumps({"args":a},ensure_ascii=False),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60);return p.stdout
out=io.open(r"C:\ADHD_agent\_tmp_scripts\cmp.txt",'w',encoding='utf-8')
for tab in ["深海节策划案","深海节-各活动模块"]:
    rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{tab}'!A1:B300"})])).get('values',[])
    out.write(f"\n===== [{tab}] 章节/模块标题 =====\n")
    for i,r in enumerate(rows,1):
        a=(r[0] if len(r)>0 else "").strip()
        if a.startswith("▌") or re.match(r"^[〇一二三四五六七八九十]、",a) or a.startswith("X3 深海") or a.startswith("深海节 ·"):
            out.write(f"R{i}: {a}\n")
out.close(); print("done")
