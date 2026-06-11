# -*- coding: utf-8 -*-
"""世界杯核心循环图(PIL程序化,贴总览「一、核心循环」图位)。横版1720x880。"""
from PIL import Image, ImageDraw, ImageFont
import io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')

W,H=1720,880
im=Image.new('RGB',(W,H),(250,250,247))
d=ImageDraw.Draw(im)
FT =ImageFont.truetype(r'C:\Windows\Fonts\msyhbd.ttc',40)
FB =ImageFont.truetype(r'C:\Windows\Fonts\msyhbd.ttc',30)
FS =ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',23)
FXS=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',20)

BLUE=(66,133,244); GOLD=(218,165,32); ORANGE=(230,126,34); PURPLE=(142,68,173); GREEN=(15,157,88); GRAY=(120,120,120)
def light(c,a=18): return tuple(int(255-(255-x)*a/100) for x in c)

def box(x,y,w,h,c,title,lines,tf=FB):
    d.rounded_rectangle([x,y,x+w,y+h],radius=16,fill=light(c),outline=c,width=5)
    d.text((x+w/2,y+26),title,font=tf,fill=c,anchor='mm')
    for i,ln in enumerate(lines):
        d.text((x+w/2,y+62+i*30),ln,font=FS,fill=(60,60,60),anchor='mm')

def arrow(x0,y0,x1,y1,c=(90,90,90),w=5,label=None,loff=(0,-18)):
    d.line([x0,y0,x1,y1],fill=c,width=w)
    import math
    ang=math.atan2(y1-y0,x1-x0); L=16
    for da in (2.6,-2.6):
        d.line([x1,y1,x1-L*math.cos(ang+da),y1-L*math.sin(ang+da)],fill=c,width=w)
    if label:
        d.text(((x0+x1)/2+loff[0],(y0+y1)/2+loff[1]),label,font=FXS,fill=c,anchor='mm')

d.text((40,28),'世界杯活动 · 核心循环',font=FT,fill=(30,30,30))
d.text((46,86),'唯一闭环货币 = 世界杯抽奖券（$0.25/张）；全部付费/免费入口产券 → 开箱 → 顶端外显',font=FS,fill=GRAY)

# 左列产出源(5个)
SX,SW,SH,GAP=40,360,108,18
srcs=[
 ('比赛竞猜(模块2)',['买助威礼包=竞猜 · 猜对+75%','焦点战爆冷再加成(押弱方)'],BLUE),
 ('签到(模块4)',['每日登录领券 · 可补签'],BLUE),
 ('BP通行证(模块3)',['三轨奖励含券','积分=活跃砍半+竞猜加分'],BLUE),
 ('传统礼包(连锁A线/锚点B线)',['A线:券+宝石+VIP(主投放)','B线:纯券=直购(ROI低)'],BLUE),
 ('累充(模块6)',['券按档位差值×2($0.50/张)','航迹/头像框进档位'],BLUE),
]
y=150
src_mid=[]
for t,ls,c in srcs:
    box(SX,y,SW,SH,c,t,ls)
    src_mid.append(y+SH/2)
    y+=SH+GAP

# 中央: 抽奖券
TX,TY,TW,TH_=560,330,300,180
box(TX,TY,TW,TH_,GOLD,'世界杯抽奖券',['唯一闭环货币','面价 $0.25/张','可单卖但ROI低(软引导竞猜)'],FB)
for ym in src_mid:
    arrow(SX+SW,ym,TX-8,TY+TH_/2,GOLD,4)

# 开箱
OX,OY,OW,OH=1000,300,330,240
box(OX,OY,OW,OH,ORANGE,'世界杯开箱(模块1)',['冠军福箱 · 10券=$2.5/次','累计阶梯 5/20/40/70/100','保底100次必得大奖(坑深$250)'],FB)
arrow(TX+TW,TY+TH_/2,OX-8,OY+OH/2,ORANGE,6,label='消耗')

# 大奖
PX,PY,PW,PH=1430,210,260,200
box(PX,PY,PW,PH,PURPLE,'★顶端大奖',['足球宝贝皮肤','(爱莉希雅·限定)','+ 限定英雄'],FB)
arrow(OX+OW,OY+OH/2-40,PX-8,PY+PH/2,PURPLE,6,label='超级大奖/保底')

# 兑换商店分支
EX,EY,EW,EH=1430,480,260,170
box(EX,EY,EW,EH,GREEN,'兑换商店(模块5)',['开箱副产出:纪念币($0.01)','兑换历史皮肤/养成'],FB)
arrow(OX+OW,OY+OH/2+50,EX-8,EY+EH/2,GREEN,5,label='副产出·纪念币')

# 底部券效率梯度条
y0=H-120
d.rounded_rectangle([40,y0,W-40,y0+86],radius=14,fill=(240,240,236),outline=(200,200,196),width=3)
d.text((60,y0+12),'券效率梯度(单券成本,越低越香):',font=FS,fill=(60,60,60))
d.text((60,y0+48),'爆冷$0.111 ＞ 猜对$0.143(≈$0.15) ＞ 竞猜EV$0.18 ＞ 连锁A线$0.20(+宝石VIP,综合ROI第一) ＞ B线/猜错$0.25 ＞ 累充附赠$0.50   →  激励指向:参与竞猜、敢押弱队',font=FS,fill=(110,80,20))

im.save('核心循环图.png',quality=95)
print('SAVED 核心循环图.png')
