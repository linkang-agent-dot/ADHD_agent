# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-活动美术需求"; GID=1651551353
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
def rgb(h): return {"red":int(h[0:2],16)/255,"green":int(h[2:4],16)/255,"blue":int(h[4:6],16)/255}
GREEN=rgb("8EE085");HDR=rgb("D9E6F2");LBLUE=rgb("CFE2FF")
rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1:H30"})])).get('values',[]); N=len(rows)
def cell(r,c0,c1,fmt,fields): return {"repeatCell":{"range":{"sheetId":GID,"startRowIndex":r,"endRowIndex":r+1,"startColumnIndex":c0,"endColumnIndex":c1},"cell":{"userEnteredFormat":fmt},"fields":fields}}
reqs=[{"repeatCell":{"range":{"sheetId":GID,"startRowIndex":0,"endRowIndex":N,"startColumnIndex":0,"endColumnIndex":8},"cell":{"userEnteredFormat":{"textFormat":{"fontSize":10,"bold":False},"backgroundColor":{"red":1,"green":1,"blue":1},"wrapStrategy":"WRAP","verticalAlignment":"TOP"}},"fields":"userEnteredFormat(textFormat,backgroundColor,wrapStrategy,verticalAlignment)"}}]
for col,w in [(0,110),(1,140),(2,360),(3,230),(4,200),(5,110)]:
    reqs.append({"updateDimensionProperties":{"range":{"sheetId":GID,"dimension":"COLUMNS","startIndex":col,"endIndex":col+1},"properties":{"pixelSize":w},"fields":"pixelSize"}})
for i,r in enumerate(rows):
    a=(r[0] if r else "").strip()
    if a.startswith("深海节 · 活动美术需求"): reqs.append(cell(i,0,8,{"backgroundColor":GREEN,"textFormat":{"fontSize":14,"bold":True}},"userEnteredFormat(backgroundColor,textFormat)"))
    elif a.startswith("【视觉调性】"): reqs.append(cell(i,0,8,{"backgroundColor":LBLUE,"textFormat":{"bold":True}},"userEnteredFormat(backgroundColor,textFormat)"))
    elif a=="模块": reqs.append(cell(i,0,6,{"backgroundColor":HDR,"textFormat":{"bold":True}},"userEnteredFormat(backgroundColor,textFormat)"))
    elif a and a[0] in "①②③④⑤⑥⑦⑧⑨": reqs.append(cell(i,0,1,{"textFormat":{"bold":True}},"userEnteredFormat.textFormat"))
    elif a.startswith("★"): reqs.append(cell(i,0,8,{"textFormat":{"bold":True}},"userEnteredFormat.textFormat"))
o=gws(['sheets','spreadsheets','batchUpdate','--params',json.dumps({"spreadsheetId":SID})],{"requests":reqs})
print("fmt:", 'OK' if 'replies' in o or 'spreadsheetId' in o else o[:100])
