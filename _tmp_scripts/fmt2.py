# -*- coding: utf-8 -*-
import subprocess, json, re
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-各活动模块"; GID=1735716843
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
def rgb(h): return {"red":int(h[0:2],16)/255,"green":int(h[2:4],16)/255,"blue":int(h[4:6],16)/255}
GREEN=rgb("8EE085");MOD=rgb("D9EAD3");PEACH=rgb("FCEBCC");PINK=rgb("FF99FF")
rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1:L230"})])).get('values',[]); N=len(rows)
def cell(r,c0,c1,fmt,fields): return {"repeatCell":{"range":{"sheetId":GID,"startRowIndex":r,"endRowIndex":r+1,"startColumnIndex":c0,"endColumnIndex":c1},"cell":{"userEnteredFormat":fmt},"fields":fields}}
reqs=[{"repeatCell":{"range":{"sheetId":GID,"startRowIndex":0,"endRowIndex":N,"startColumnIndex":0,"endColumnIndex":12},"cell":{"userEnteredFormat":{"textFormat":{"fontSize":10,"bold":False},"backgroundColor":{"red":1,"green":1,"blue":1},"wrapStrategy":"WRAP","verticalAlignment":"TOP"}},"fields":"userEnteredFormat(textFormat,backgroundColor,wrapStrategy,verticalAlignment)"}}]
for col,w in [(0,150),(1,160),(2,640)]:
    reqs.append({"updateDimensionProperties":{"range":{"sheetId":GID,"dimension":"COLUMNS","startIndex":col,"endIndex":col+1},"properties":{"pixelSize":w},"fields":"pixelSize"}})
for i,r in enumerate(rows):
    a=(r[0] if len(r)>0 else "").strip(); b=(r[1] if len(r)>1 else "").strip()
    if a.startswith("深海节 · 各活动模块"):
        reqs.append(cell(i,0,12,{"backgroundColor":GREEN,"textFormat":{"fontSize":14,"bold":True}},"userEnteredFormat(backgroundColor,textFormat)"))
    elif a.startswith("▌"):
        reqs.append(cell(i,0,12,{"backgroundColor":MOD,"textFormat":{"fontSize":12,"bold":True}},"userEnteredFormat(backgroundColor,textFormat)"))
    elif re.match(r"^〇、|^[一二三]、",b) or b in ("配置表/复用源","界面交互","本地化") or b.startswith("·复用") or b.startswith("【美术需求】"):
        reqs.append(cell(i,1,12,{"textFormat":{"bold":True}},"userEnteredFormat.textFormat"))
        if b.startswith("〇、"): reqs.append(cell(i,1,2,{"backgroundColor":PEACH},"userEnteredFormat.backgroundColor"))
        if b.startswith("【美术需求】"): reqs.append(cell(i,1,2,{"backgroundColor":PINK},"userEnteredFormat.backgroundColor"))
for k in range(0,len(reqs),50):
    o=gws(['sheets','spreadsheets','batchUpdate','--params',json.dumps({"spreadsheetId":SID})],{"requests":reqs[k:k+50]})
    print(f"b{k}:", 'OK' if 'replies' in o or 'spreadsheetId' in o else o[:80])
print("reqs",len(reqs))
