# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-活动美术需求"; GID=1651551353
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
def rgb(h): return {"red":int(h[0:2],16)/255,"green":int(h[2:4],16)/255,"blue":int(h[4:6],16)/255}
GREEN=rgb("8EE085");HDR=rgb("D9E6F2");LBLUE=rgb("CFE2FF");GREY=rgb("EFEFEF");YEL=rgb("FFF2CC")
rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1:H32"})])).get('values',[]); N=len(rows)
def cell(r,c0,c1,fmt,fields): return {"repeatCell":{"range":{"sheetId":GID,"startRowIndex":r,"endRowIndex":r+1,"startColumnIndex":c0,"endColumnIndex":c1},"cell":{"userEnteredFormat":fmt},"fields":fields}}
reqs=[{"repeatCell":{"range":{"sheetId":GID,"startRowIndex":0,"endRowIndex":N,"startColumnIndex":0,"endColumnIndex":8},"cell":{"userEnteredFormat":{"textFormat":{"fontSize":10,"bold":False},"backgroundColor":{"red":1,"green":1,"blue":1},"wrapStrategy":"WRAP","verticalAlignment":"TOP"}},"fields":"userEnteredFormat(textFormat,backgroundColor,wrapStrategy,verticalAlignment)"}}]
for col,w in [(0,30),(1,110),(2,140),(3,300),(4,180),(5,330),(6,100),(7,60)]:
    reqs.append({"updateDimensionProperties":{"range":{"sheetId":GID,"dimension":"COLUMNS","startIndex":col,"endIndex":col+1},"properties":{"pixelSize":w},"fields":"pixelSize"}})
for i,r in enumerate(rows):
    a=(r[0] if r else "").strip()
    st=(r[6] if len(r)>6 else "")
    if a.startswith("深海节 · 活动美术需求 CHECKLIST"): reqs.append(cell(i,0,8,{"backgroundColor":GREEN,"textFormat":{"fontSize":14,"bold":True}},"userEnteredFormat(backgroundColor,textFormat)"))
    elif a.startswith("【视觉调性】"): reqs.append(cell(i,0,8,{"backgroundColor":LBLUE,"textFormat":{"bold":True}},"userEnteredFormat(backgroundColor,textFormat)"))
    elif a=="#": reqs.append(cell(i,0,8,{"backgroundColor":HDR,"textFormat":{"bold":True}},"userEnteredFormat(backgroundColor,textFormat)"))
    elif a.startswith("合计") or a.startswith("★"): reqs.append(cell(i,0,8,{"textFormat":{"bold":True},"backgroundColor":GREY},"userEnteredFormat(textFormat,backgroundColor)"))
    elif a.isdigit():
        reqs.append(cell(i,1,2,{"textFormat":{"bold":True}},"userEnteredFormat.textFormat"))
        if "复用现成" in st: reqs.append(cell(i,6,7,{"backgroundColor":GREY},"userEnteredFormat.backgroundColor"))
        elif "待策划" in st: reqs.append(cell(i,6,7,{"backgroundColor":YEL},"userEnteredFormat.backgroundColor"))
o=gws(['sheets','spreadsheets','batchUpdate','--params',json.dumps({"spreadsheetId":SID})],{"requests":reqs})
print("fmt:", 'OK' if ('replies' in o or 'spreadsheetId' in o) else o[:120])
