# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-活动美术需求"
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
R=[]
R.append(["深海节 · 活动美术需求（复用换皮清单）"])
R.append(["复用参考图：KB\产出-数值设计\X3_深海节\复用参考图\夏日\；主题：深蓝/浅蓝/青绿 + 金黄(宝藏)/珍珠白(贝壳)；保留原界面布局，仅换主题美术。"])
R.append([""])
R.append(["模块","美术类型","深海版要求","复用参考图","状态"])
def row(m,t,req,ref,st): R.append([m,t,req,ref,st])
# 1 深海罗盘
row("①深海罗盘","🔧转盘换包装(玩法UI)","开箱UI→转盘/罗盘UI：罗盘外观/中心数字盘(1-6)/指针/格子岛图——需先定转盘换包装方案","01_致她的信_开箱_101514.png","🔧待策划转盘方案")
row("","活动主界面背景","换深海(深蓝/海面/航线)","01_致她的信_开箱_101514.png","待制作")
row("","兑换商店背景/banner","换深海集市风","06_绽放之礼_兑换_101337.png","待制作")
row("","活动入口icon(HUD)","深海罗盘icon","-","待制作")
row("","传说铭牌图","深海传说·航者徽记(传说品质)","-","待制作")
# 2 远航日志
row("②远航日志(BP)","BP主界面背景/banner","换深海(航海日志风)","02_为誓言而战_BP_102236.png","待制作")
row("","史诗铭牌图","深海远征·航徽(史诗品质)","-","待制作")
# 3 怦然心动
row("③怦然心动·深海","每日礼包背景/弹窗","换深海主题","怦然心动.png","待制作")
row("","礼包展示视频","深海版每日礼包视频","录制_2026_05_27...mp4(夏日参考)","待制作")
# 4 深海印记
row("④深海印记(头像框)","通用礼包banner","深海主题(9.99礼包)","-(新增通用礼包模块)","待制作")
row("","深海头像框图","新增深海头像框(80xxx)","-","待制作")
# 5 深海馈赠
row("⑤深海馈赠(累充)","累充活动背景","换深海(宝藏/馈赠风)","07_花瓣与恩典_累充_100595.png","待制作")
row("","行军皮肤图","深海行军皮肤(顶档外显,夏日为航迹)","-","🔧待夏日复盘定ID")
# 6 深海居所
row("⑥深海居所(装饰)","礼包banner","换深海(居所风)","08_夏日装饰礼包_装饰阶梯_106101.png","待制作")
row("","深海装饰三件套图","若复用人鱼之歌(灵潮之殿1001008/海灵归途2001012/灵魂之径3001009)则无需新出；否则新出深海三件套","-","待定(复用or新出)")
# 7 海滨之约
row("⑦海滨之约(拜访)","拜访活动背景","换深海(海滨酒馆风)","03_夏日柔情海湾_拜访礼包_105603.png / 门头拜访礼包.png","待制作")
row("","门头三件套图","复用海滨假日门头(横梁1001009/地板2001013/墙纸3001010)——已有，无需新出","门头拜访礼包.png","✅复用现有")
row("","礼包图/icon","海滨门头礼包$99.99","门头拜访礼包.png","待制作")
# 8 许愿池
row("⑧许愿池","仅换背景图","名字/文案/玩法不变，仅替换活动背景为深海","-(许愿池界面)","待制作(只背景)")
# 9 最佳酒馆
row("⑨最佳酒馆","仅换背景图","名字/文案/玩法不变，仅替换活动背景为深海","05_为爱干杯_最佳酒馆_10071702.png","待制作(只背景)")
R.append([""])
R.append(["★ 待策划提供：①转盘换包装方案(决定深海罗盘能否落地) ⑤行军皮肤ID(夏日复盘) ⑥深海装饰是否复用人鱼之歌"])

gws(['sheets','spreadsheets','batchUpdate','--params',json.dumps({"spreadsheetId":SID})],{"requests":[{"addSheet":{"properties":{"title":TAB,"gridProperties":{"rowCount":60,"columnCount":8}}}}]})
out=gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1","valueInputOption":"RAW"})],{"values":R,"majorDimension":"ROWS"})
print("write:", 'OK' if 'updatedCells' in out else out[:140], "rows:",len(R))
d=json.loads(gws(['sheets','spreadsheets','get','--params',json.dumps({"spreadsheetId":SID,"fields":"sheets.properties(sheetId,title)"})]))
print("gid:", next((s['properties']['sheetId'] for s in d['sheets'] if s['properties']['title']==TAB),None))
