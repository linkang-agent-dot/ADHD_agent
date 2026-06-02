# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-各活动模块"
def gws(a):
    p=subprocess.run(['node',WRAPPER],input=json.dumps({"args":a},ensure_ascii=False),capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1:C260"})])).get('values',[])
# blocks: (mxHDRrow, nextMODrow)
hdrs=[33,60,83,107,132,157,186,210,233]; mods=[39,64,87,111,136,161,191,213,238]
import io,sys
buf=[]
for h,m in zip(hdrs,mods):
    buf.append(f"### 美需块 HDR R{h} → next R{m}")
    for i in range(h-1, m-1):
        r=rows[i] if i<len(rows) else []
        buf.append(f"R{i+1}: {' | '.join(r)}")
open("C:/ADHD_agent/_tmp_scripts/mxblocks.txt","w",encoding="utf-8").write("\n".join(buf))
print("written", len(buf),"lines")
