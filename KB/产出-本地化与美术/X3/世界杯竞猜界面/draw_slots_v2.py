# -*- coding: utf-8 -*-
"""竞猜界面槽位示意图 v2：独立线框图(不叠效果图)。左=界面槽位线框,右=产出清单表。"""
from PIL import Image, ImageDraw, ImageFont
import io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')

W,H=2000,2080
im=Image.new('RGB',(W,H),(245,245,242))
d=ImageDraw.Draw(im)
F   =ImageFont.truetype(r'C:\Windows\Fonts\msyhbd.ttc',40)
F2  =ImageFont.truetype(r'C:\Windows\Fonts\msyhbd.ttc',30)
F3  =ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',26)
F4  =ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',24)

# 配色: F固定=蓝 T队伍=红 B背景=绿 TXT文本=橙黄
CF=(66,133,244); CT=(219,68,55); CB=(15,157,88); CX=(244,160,0)
def fill(c,a=38): return tuple(int(255-(255-x)*a/100) for x in c)

# ---- 左侧:界面线框 (phone 740x1660 @ x=60,y=160) ----
PX,PY,PW,PH=60,170,760,1700
d.text((PX,40),'竞猜二选一界面 · 槽位拆解示意',font=F,fill=(30,30,30))
d.text((PX,100),'(线框示意,观感见 竞猜界面_方向定稿_FINAL.png)',font=F3,fill=(120,120,120))
# 背景B1=手机框整体
d.rounded_rectangle([PX,PY,PX+PW,PY+PH],radius=28,fill=fill(CB,22),outline=CB,width=6)
d.text((PX+12,PY+PH-54),'B1 背景·整张(按阶段3张:32强日场/8强夜场/决赛庆典)',font=F4,fill=CB)

def slot(x0,y0,x1,y1,c,tag,line2=None,top=False):
    d.rounded_rectangle([PX+x0,PY+y0,PX+x1,PY+y1],radius=14,fill=fill(c),outline=c,width=5)
    cx=(x0+x1)/2+PX
    if top:
        d.text((cx,PY+y0+22),tag,font=F2,fill=c,anchor='mm')
        if line2: d.text((cx,PY+y0+58),line2,font=F4,fill=(70,70,70),anchor='mm')
    elif line2:
        d.text((cx,PY+(y0+y1)/2-34),tag,font=F2,fill=c,anchor='mm')
        d.text((cx,PY+(y0+y1)/2+10),line2,font=F4,fill=(70,70,70),anchor='mm')
    else:
        d.text((cx,PY+(y0+y1)/2-12),tag,font=F2,fill=c,anchor='mm')

slot( 40,  30, 720, 120, CF,'F1 标题横幅','固定·无文字(标题=TextKey)')
slot(200, 140, 560, 210, CF,'F2 倒计时章','固定')
# VS区(T1标签置顶防被子槽盖住,子槽下移)
slot( 40, 240, 340, 620, CT,'T1L 队伍横幅·左','渐变烧图·按队32张',top=True)
slot(420, 240, 720, 620, CT,'T1R 队伍横幅·右','同一张图水平翻转',top=True)
slot(312, 380, 448, 500, CF,'F3 VS','固定')
slot( 90, 330, 290, 480, CT,'T2L 队徽','icon·32张')
slot(470, 330, 670, 480, CT,'T2R 队徽','icon·32张')
slot( 70, 520, 310, 595, CX,'TXT 队名','TextKey·不烧图')
slot(450, 520, 690, 595, CX,'TXT 队名','32队×10语言')
# 礼包柱
slot( 40, 660, 365,1340, CF,'F4L 礼包柱面板','固定(内容=道具icon+TextKey)',top=True)
slot(395, 660, 720,1340, CF,'F4R 礼包柱面板','固定·与左同构',top=True)
slot( 80,1220, 325,1310, CF,'F5 价格按钮','固定(价格=TextKey)')
slot(435,1220, 680,1310, CF,'F5 价格按钮','固定')
slot( 40,1390, 720,1470, CF,'F6 锁定提示条','固定(文案=TextKey)')

# ---- 右侧:产出清单表 ----
TX,TY=900,170
d.text((TX,40),'产出清单 & 复用规则',font=F,fill=(30,30,30))
rows=[
 ('层','槽位','产出','复用规则',(60,60,60)),
 ('F 固定层','F1-F6 框架/VS/礼包柱/按钮/提示条','美术 1 套切图(★无文字)','全场次永不换',CF),
 ('T 队伍层','T1 渐变横幅','每队1张·共32张(AI批量,对称设计一图翻转)','同队全赛程复用',CT),
 ('T 队伍层','T2 队徽','每队1张icon·共32张(可用国家队徽)','同队复用',CT),
 ('B 背景层','B1 整张背景','3张:32强日场/8强夜场/决赛庆典','按阶段换=换氛围',CB),
 ('TXT 文本','队名/标题/按钮/提示全部文字','TextKey(队名=TXT_WC_Team_{三字码},32队×10语言)','i18n一次翻完·不烧图',CX),
]
colw=[170,300,380,230]
y=TY
for i,(a,b,c,e,col) in enumerate(rows):
    rh=96 if i>0 else 64
    bg=(232,232,230) if i==0 else fill(col,16)
    d.rectangle([TX,y,TX+sum(colw),y+rh],fill=bg,outline=(190,190,190),width=2)
    x=TX
    for j,(txt,wd) in enumerate(zip([a,b,c,e],colw)):
        # 简单折行
        ft=F4; maxch=int(wd/24)
        lines=[txt[k:k+maxch] for k in range(0,len(txt),maxch)][:3]
        for li,ln in enumerate(lines):
            d.text((x+10,y+10+li*28),ln,font=ft,fill=col if i>0 else (40,40,40))
        x+=wd
    y+=rh

# 维表+运营操作
y+=50
d.text((TX,y),'队伍维表（32强一次配完）',font=F2,fill=(30,30,30)); y+=50
d.rectangle([TX,y,TX+sum(colw),y+70],fill=(250,247,235),outline=(190,180,140),width=2)
d.text((TX+12,y+18),'TeamID │ 队名TextKey │ 横幅DK(T1) │ 队徽DK(T2)',font=F3,fill=(110,90,30)); y+=110
d.text((TX,y),'每场运营操作（零美术增量）',font=F2,fill=(30,30,30)); y+=50
steps=['① 场次表填: 左TeamID / 右TeamID / 开赛时间 / 价格档','② 横幅·队徽·队名 由维表自动带出','③ 挂 2 个竞猜礼包(Pack) → 完成一场设计']
for st in steps:
    d.rectangle([TX,y,TX+sum(colw),y+62],fill=(238,243,250),outline=(170,190,220),width=2)
    d.text((TX+12,y+14),st,font=F3,fill=(40,70,120)); y+=74
y+=40
d.text((TX,y),'焦点战实例增量槽(独立活动,界面同构):',font=F2,fill=(30,30,30)); y+=44
for st in ['F7 焦点之战角标(固定1张·挂标题区)','T3 胜利加赠标签(固定1张·挂指定方横幅侧,数字TextKey)','B1+ 夜场氛围背景(高档实例,🔧专属或复用决赛庆典)']:
    d.rectangle([TX,y,TX+sum(colw),y+56],fill=(252,240,238),outline=(220,170,160),width=2)
    d.text((TX+12,y+12),st,font=F3,fill=(150,60,40)); y+=66
y+=20
d.text((TX,y),'交付三件套：本图(结构/产出) + 最终效果图_FINAL(普通场) + 焦点战效果图_FINAL',font=F3,fill=(120,60,60))

im.save('竞猜界面_槽位拆解示意图.png',quality=95)
print('SAVED 竞猜界面_槽位拆解示意图.png')
