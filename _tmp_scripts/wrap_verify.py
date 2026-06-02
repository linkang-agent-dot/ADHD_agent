# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-各活动模块"; GID=1735716843
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
# wrap+top valign on column C for all art rows
rows=[34,35,36,37,61,62,84,85,108,109,133,134,158,159,187,188,189,211,234]
reqs=[{"repeatCell":{"range":{"sheetId":GID,"startRowIndex":r-1,"endRowIndex":r,"startColumnIndex":2,"endColumnIndex":3},"cell":{"userEnteredFormat":{"wrapStrategy":"WRAP","verticalAlignment":"TOP"}},"fields":"userEnteredFormat(wrapStrategy,verticalAlignment)"}} for r in rows]
o=gws(['sheets','spreadsheets','batchUpdate','--params',json.dumps({"spreadsheetId":SID})],{"requests":reqs})
print("wrap:", 'OK' if ('replies' in o or 'spreadsheetId' in o) else o[:100])
# verify R85 video cell
v=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!C85"})])).get('values',[[""]])[0][0]
print("--- R85 视频格 ---"); print(v[:400])
