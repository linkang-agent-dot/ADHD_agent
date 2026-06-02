import subprocess, json, io
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'
def gws(a):
    p=subprocess.run(['node',WRAPPER],input=json.dumps({"args":a},ensure_ascii=False),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60);return p.stdout
out=io.open(r"C:\ADHD_agent\_tmp_scripts\loc56.txt",'w',encoding='utf-8')
for tab,rng in [("深海节-各活动模块","A75:C135"),("深海节-活动美术需求","A10:E24")]:
    rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{tab}'!{rng}"})])).get('values',[])
    base=int(rng.split(':')[0][1:])
    out.write(f"\n=== {tab} ({rng}) ===\n")
    for i,r in enumerate(rows,base):
        line=" | ".join(str(c) for c in r)
        if line.strip(): out.write(f"R{i}: "+line[:150]+"\n")
out.close(); print("ok")
