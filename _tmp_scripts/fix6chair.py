# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
def setc(tab,cell,val):
    gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{tab}'!{cell}","valueInputOption":"RAW"})],{"values":[[val]],"majorDimension":"ROWS"})
def setrow(tab,rng,vals):
    gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{tab}'!{rng}","valueInputOption":"RAW"})],{"values":[vals],"majorDimension":"ROWS"})
MT="深海节-各活动模块"; AT="深海节-活动美术需求"
setc(MT,"C134","装饰礼包=椰风遮阳椅(151043)单道具，19.99×3 阶梯礼包，每个礼包卖 1 个（一个道具×3包）")
setc(MT,"C136","复用阶梯礼包结构(夏日210917-919)；装饰物=椰风遮阳椅(海滨假日151043,现成家具摆件)，无需新美术")
setc(MT,"C138","·复用阶梯/链式礼包；3个礼包(各19.99)，每包奖励=椰风遮阳椅×1；D3-D14")
setc(MT,"C139","·装饰物=椰风遮阳椅(家具摆件 Item151043，海滨假日，现成，图标DK_icon_jiaju_summer_3，带角色坐下动画)")
setc(MT,"C141","Pack×3(各19.99,复用210917-919结构)，每包奖励=椰风遮阳椅 Item151043 ×1；ChainPack链式")
setc(MT,"C147","椰风遮阳椅(151043)复用现成(DK_icon_jiaju_summer_3)，无需新出；礼包banner(深海/海滨风)")
print("模块tab ⑥ 已更新")
setrow(AT,"B19:E19",["深海装饰(家具摆件)","椰风遮阳椅(海滨假日 Item151043，现成，DK_icon_jiaju_summer_3)，19.99×3阶梯每包1个","(现成)","✅复用现有"])
print("美需tab ⑥ 已更新")
