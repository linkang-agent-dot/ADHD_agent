# -*- coding: utf-8 -*-
import subprocess, json, os
os.environ['GOOGLE_WORKSPACE_PROJECT_ID']='calm-repeater-489707-n1'
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'; TAB="深海节-各活动模块"
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
B=""
R=[]
def mod(title): R.append([title])
def L0(t): R.append([B,t])
def L1(t): R.append([B,B,t])
def blank(): R.append([B])

R.append(["深海节 · 各活动模块（除周卡/大富翁；9模块）"])
R.append([B,"骨架版：包装层/设计目的/玩法/复用改动 已填；规则说明/配置表/界面交互/本地化 为待补细节小节。逐模块确认后补全。"])
blank()

def skeleton(num,name,activity,period,zh_name,title,sub,visual,purpose,play,reuse):
    mod(f"▌{num}. {name}（{activity}） {period}")
    L0("〇、包装层")
    L1(f"活动名称：{zh_name}")
    L1(f"界面主标题：{title}")
    if sub: L1(f"副标/描述：{sub}")
    L1(f"视觉关键词：{visual}")
    L0("一、设计目的")
    L1(purpose)
    L0("二、玩法说明")
    L1(play)
    L0(f"·复用/改动点：{reuse}")
    L0("三、规则说明")
    L1("【待补细节】")
    L0("配置表（内嵌）")
    L1("【待补细节】")
    L0("界面交互")
    L1("【待补细节】")
    L0("本地化")
    L1("【待补细节】")
    blank()

skeleton("1","深海罗盘","开箱转盘+兑换+排行榜·英雄皮肤","D1–D14",
 "深海罗盘","转动深海罗盘，驶向宝藏","每一次转动，都让你离稀世皮肤更近一步","罗盘/宝箱/深海/航线",
 "第一周引流核心 + 英雄皮肤投放（海风旅者返场、赛米拉排行榜主投）",
 "消耗道具转动深海罗盘抽奖(奖池含英雄皮肤)+兑换商店兑换；排行榜 A+B 线消费冲榜",
 "复用夏日开箱框架；海风旅者返场(600刀节点充赠+重复返1万钻)、赛米拉排行榜主投、新增传说铭牌(3%战斗属性)、换深海背景文案")
skeleton("2","远航日志","通行证+史诗铭牌","D1–D14",
 "远航日志","记录你的远航，每一海里都有嘉奖","推进航海日志，逐级解锁深海珍宝","航海日志/罗盘/航徽",
 "BP 承载史诗铭牌权益，拉通行证升级率",
 "完成任务积分逐级解锁，免费+付费(9.99)双线",
 "复用 BP；9.99 + 史诗品质铭牌(头衔，无BUFF)；换深海皮")
skeleton("3","怦然心动·深海","每日礼包","D1–D14",
 "怦然心动·深海","深海每日来信，今日份的心动已送达","","深海/每日/信",
 "每日低价触达付费点",
 "每日登录可购买的限定礼包",
 "复用怦然心动礼包改深海节版本；需程序微量处理；出视频")
skeleton("4","深海印记","头像框礼包 9.99","D1–D14",
 "深海印记","深海限定头像框 + 节日珍藏","","深海头像框/印记",
 "新增可制作的节日投放付费点",
 "9.99 通用礼包，购买得深海头像框 + 节日道具",
 "需程序处理通用礼包模块；策划出图 + 跑头像框")
skeleton("5","深海馈赠","累充+行军皮肤","D1–D14",
 "深海馈赠","慷慨的远航者，深海以珍宝相报","累计远航补给，达档领丰厚奖励","累充/行军皮肤/宝藏",
 "累充新增外显，拉高档达成率、强化付费深度",
 "活动期累计充值达阶段目标领奖，顶端为行军皮肤",
 "累充档位新增行军皮肤奖励(档位等夏日复盘出来后定)；出背景图")
skeleton("6","深海居所","装饰礼包 19.99×3","D3–D14",
 "深海居所","把你的小岛，装点成深海的模样","限定装饰阶梯礼包，逐档解锁、性价比递增","深海装饰/居所",
 "19.99 阶梯已验证(夏日家具486%)，拉装饰复购深度",
 "深海装饰三件套改 19.99×3 阶梯礼包",
 "复用阶梯礼包形式 + 换美术；出图")
skeleton("7","海滨之约","拜访礼包·门头三件套 99.99","D7–D14",
 "海滨之约","为你的酒馆，挂上一道海滨的门楣","购置海滨门头，迎接远航归来的船长做客——被拜访越多，馈赠越丰","海滨门楣/酒馆/海风",
 "刺激门头装潢礼包售卖 + 提升社交(为超大R提供被拜访感)",
 "购买海滨门头礼包，按被拜访次数领阶段奖励；每日领邀请函拜访购包者获奖励",
 "复用拜访礼包(ActvType=56)；海滨门头三件套(Door_Skin08+Floor/Wallpaper_Summer)；换深海banner")
skeleton("8","许愿池","许愿池(名字不变)","D1–D14",
 "许愿池（名字不变）","(沿用原文案)","","深海背景(仅换背景图)",
 "$4.99 可重复抽，全服共建引流+复购抓手",
 "全服共同投入许愿池，达阶段奖池触发超级大奖",
 "复用；【仅换深海背景图】，名字与文案不变")
skeleton("9","最佳酒馆","最佳酒馆(名字不变)","D1–D14",
 "最佳酒馆（名字不变）","(沿用原文案)","","深海背景(仅换背景图)",
 "跨服酒馆赛事，拉中高R冲分",
 "完成节日任务赚积分，多阶段递进，阶段排名领世界级奖",
 "复用；【仅换深海背景图】，名字与文案不变")

gws(['sheets','spreadsheets','batchUpdate','--params',json.dumps({"spreadsheetId":SID})],{"requests":[{"addSheet":{"properties":{"title":TAB,"gridProperties":{"rowCount":400,"columnCount":12}}}}]})
out=gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{TAB}'!A1","valueInputOption":"RAW"})],{"values":R,"majorDimension":"ROWS"})
print("write:", 'OK' if 'updatedCells' in out else out[:140], "rows:",len(R))
# gid
d=json.loads(gws(['sheets','spreadsheets','get','--params',json.dumps({"spreadsheetId":SID,"fields":"sheets.properties(sheetId,title)"})]))
gid=next((s['properties']['sheetId'] for s in d['sheets'] if s['properties']['title']==TAB),None)
print("gid:",gid)
