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
# ⑤ 深海馈赠
setc(MT,"C112","复用累充换背景；顶档行军皮肤=深海猎手(现成·永久15065)；档位/数值待夏日复盘")
setc(MT,"C115","·顶档行军皮肤=深海猎手(永久 Item15065，现状'暂无获取'正好投放，复用现成)；具体档位/数值待夏日复盘")
setc(MT,"C117","累充=ActvType5(复用597)；ActvOnline.RechargePointPackWhitelist；累充Reward各档，顶档=深海猎手 Item15065(永久,现成)")
setc(MT,"C123","累充活动背景图(深海)；行军皮肤=深海猎手15065 现成，无需新出")
# ⑥ 深海居所
setc(MT,"C139","·深海装饰三件套=复用人鱼之歌【灵潮之殿套】：灵潮之殿(横梁1001008)/海灵归途(地板2001012)/灵魂之径(墙纸3001009)，现成无需新出")
setc(MT,"C141","Pack×3(各19.99,复用210917-919结构) + 装饰FurnitureSkin=灵潮之殿套(横梁1001008/地板2001012/墙纸3001009,现成) + ChainPack链式")
setc(MT,"C147","深海装饰三件套=复用灵潮之殿套(1001008/2001012/3001009)现成无需新出；礼包banner")
print("模块tab ⑤⑥ 已更新")
# 美需tab ⑤行军皮肤R17 / ⑥装饰R19
setrow(AT,"B17:E17",["行军皮肤(顶档外显)","深海猎手(永久 Item15065，现状'暂无获取'正好投)","(现成,无需新出)","✅复用现有"])
setrow(AT,"B19:E19",["深海装饰三件套","复用人鱼之歌【灵潮之殿套】:灵潮之殿1001008/海灵归途2001012/灵魂之径3001009","(现成)","✅复用现有"])
print("美需tab ⑤⑥行 已更新")
# 美需tab 底部★待办行 → 全解决
rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{AT}'!A20:A30"})])).get('values',[])
star=None
for i,r in enumerate(rows,20):
    if r and str(r[0]).startswith("★"): star=i; break
if star:
    setc(AT,f"A{star}","★ 待策划/待定：①转盘换包装✅(复用大转盘) ⑤行军皮肤✅(深海猎手15065) ⑥深海装饰✅(灵潮之殿套) 均已解决；剩 ⑤累充具体档位数值待夏日复盘")
    print(f"美需 ★待办行 R{star} 已更新(全解决)")
