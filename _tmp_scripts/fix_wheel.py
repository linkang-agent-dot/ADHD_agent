# -*- coding: utf-8 -*-
import subprocess, json
WRAPPER='C:/ADHD_agent/scripts/gws_stdin.js'; SID='1mC0yssLkuae_vPc0UvbwzNzXCJiv6m0M-6Ir_AyFxVI'
def gws(a,b=None):
    pl=json.dumps({"args":a,"json":b} if b else {"args":a},ensure_ascii=False)
    p=subprocess.run(['node',WRAPPER],input=pl,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90);return p.stdout
def setcell(tab,cell,val):
    gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{tab}'!{cell}","valueInputOption":"RAW"})],{"values":[[val]],"majorDimension":"ROWS"})

MT="深海节-各活动模块"
setcell(MT,"C15","复用【大转盘】(尼罗黄金卷轴)换深海皮——转盘UI参考 大转盘.png，换深海转盘美术即可落地（不再卡设计）")
setcell(MT,"C17","·基础设定：大转盘=ActvType10(复用尼罗黄金卷轴 ContentID1023/ActvOnline101023，自带排行榜+额外奖励进度)；兑换商店=ActvType13(1339/101339)；D1-D14；入口左HUD")
setcell(MT,"C18","·抽奖：消耗抽奖券，单抽/10连；奖池=ActvLuckyWheelReward；额外奖励进度条=ActvLuckyWheelOtherReward(x50~x3000阶段)；奖池含英雄皮肤/养成料/代币")
setcell(MT,"C22","大转盘=ActvLuckyWheel(ActvType10,复用尼罗黄金卷轴 ContentID1023/ActvOnline101023) + ActvLuckyWheelReward(奖池) + ActvLuckyWheelOtherReward(额外奖励) + RankCfg(海域排名)；转盘背景=DK_Turntable；兑换ActvType13(1339)；铭牌=Title表；海风旅者=Item_5303401")
setcell(MT,"C25","复用大转盘UI(参考 大转盘.png：8格轮盘/中心指针/额外奖励进度条x50-x3000/抽奖1次·10次/海域排名)；排行榜加传说铭牌奖励位 + 『距离上榜还差{0}分』提示")
setcell(MT,"C29","转盘换皮(可落地)：复用大转盘UI(参考 大转盘.png)，换 DK_Turntable转盘背景图(深海)/8格奖励图/中心罗盘指针/背景角色(克利奥佩特拉→深海角色)；活动主背景；传说铭牌图；活动icon")
print("模块tab 深海罗盘 6格 已更新")

# 美需tab: 找转盘换包装行
AT="深海节-活动美术需求"
rows=json.loads(gws(['sheets','spreadsheets','values','get','--params',json.dumps({"spreadsheetId":SID,"range":f"'{AT}'!A1:E15"})])).get('values',[])
target=None
for i,r in enumerate(rows,1):
    if len(r)>1 and "转盘换包装" in str(r[1]): target=i; break
if target:
    # 改 B列类型/C列要求/D列参考/E列状态
    gws(['sheets','spreadsheets','values','update','--params',json.dumps({"spreadsheetId":SID,"range":f"'{AT}'!B{target}:E{target}","valueInputOption":"RAW"})],
        {"values":[["转盘换皮(可落地)","复用大转盘UI；换 DK_Turntable转盘背景(深海)/8格奖励图/中心罗盘指针/背景角色(克利奥佩特拉→深海)","大转盘.png (尼罗黄金卷轴)","待制作"]],"majorDimension":"ROWS"})
    print(f"美需tab 转盘行 R{target} 已更新")
else:
    print("美需tab 未找到转盘行")
