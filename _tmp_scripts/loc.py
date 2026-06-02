import subprocess, json, io
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'
def gws(a):
    p=subprocess.run(['node',WRAPPER],input=json.dumps({"args":a},ensure_ascii=False),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60);return p.stdout
rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":"'深海节-各活动模块'!A1:C30"})])).get('values',[])
with io.open(r"C:\ADHD_agent\_tmp_scripts\loc.txt",'w',encoding='utf-8') as f:
    for i,r in enumerate(rows,1): f.write(f"R{i}: "+" | ".join(str(c) for c in r)+"\n")
print("ok")
