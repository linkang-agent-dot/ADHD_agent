# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'
MOD="深海节-各活动模块"; MX="深海节-活动美术需求"
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
# 替换规则：海洋命名→深海；偏暗词→明亮
def fix(t):
    for a,b in [("海洋版","深海版"),("海洋每日来信","深海每日来信"),("海洋主题","深海主题"),
                ("海洋金边框","深海金边框"),("舷窗外海洋","舷窗外深海"),("海洋许愿池","深海许愿池"),
                ("阳光海域俯瞰","明亮浅海俯瞰"),("青绿幽蓝","明亮青绿(偏亮不阴暗)"),
                ("金黄×蓝","金黄×亮蓝"),("暗绿","亮绿")]:
        t=t.replace(a,b)
    return t
# 模块页签:读受影响的C列单元格,替换后写回
rows=[34,35,84,85,108,133,211,234]
data=[]
for r in rows:
    v=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{MOD}'!C{r}"})])).get('values',[[""]])[0][0]
    nv=fix(v)
    if nv!=v: data.append({"range":f"'{MOD}'!C{r}","values":[[nv]]})
if data:
    o=gws(['sheets','spreadsheets','values','batchUpdate','--params',json.dumps({"spreadsheetId":SID})],{"valueInputOption":"RAW","data":data})
    print("模块:", 'OK '+str(json.loads(o).get('totalUpdatedCells')) if 'totalUpdatedCells' in o else o[:120])
else: print("模块:无需改")
# checklist 视觉调性行 改成明亮基调
newtone="主色海蓝/浅蓝/青绿+金黄(宝藏)+珍珠白(贝壳)+暖橘(阳光)；明亮潜水海洋风(非深渊·偏亮不阴暗·潜水与泳装/海滨不冲突)；卡通奇幻；表现水波/气泡/光斑/鱼群/航线/珊瑚；避坑:不阴暗·不克苏鲁·与航海之路区分"
rows2=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{MX}'!A1:B8"})])).get('values',[])
ti=next((i for i,rr in enumerate(rows2) if rr and rr[0].startswith("【视觉调性】")),None)
if ti is not None:
    o2=gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{MX}'!B{ti+1}","valueInputOption":"RAW"})],{"values":[[newtone]]})
    print("checklist视觉调性:", 'OK' if 'updatedCells' in o2 else o2[:100])
