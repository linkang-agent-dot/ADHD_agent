# -*- coding: utf-8 -*-
"""猎杀时刻 简易BP → 3档真实效果图（真实像素重排，可拆组件）。
布局：免费(压) | 進度rail | 进阶(1格) | 至尊(2格)。進度条偏左、在免费与进阶之间。
裁真实奖励格重排，列头改 免费/进阶/至尊，顶部框架+底部栏保持原样。可复跑。
"""
from PIL import Image, ImageDraw, ImageFont
import os
D=r'C:\Users\linkang\Pictures\X3验收\BP新增档位'
OUT=os.path.join(D,'_mock')
os.makedirs(OUT,exist_ok=True)
SRC=os.path.join(D,'猎杀时刻.png')
FONT=r'C:\Windows\Fonts\msyhbd.ttc'

im=Image.open(SRC).convert('RGB'); W,H=im.size

# ---- 原图列/行边界(网格量) ----
HEAD=(0.423,0.467)      # 列头标签带(精确定位)
CELL=(0.467,0.876)      # 奖励格区
FREE_X=(0.035,0.285)    # 原 免費 列(1格)
RAIL_X=(0.292,0.438)    # 原 進度 轴
SUP_X =(0.445,0.978)    # 原 至尊 区(2格)
MID_X =(0.445,0.712)    # 原 至尊 左1格 → 复制做 进阶

def cr(x0,x1,y0,y1):
    return im.crop((int(W*x0),int(H*y0),int(W*x1),int(H*y1)))

# ---- 新布局 x(占444)·无缝相邻 ----
nFREE=(0.020,0.190)   # 免费 压窄(1格)
nRAIL=(0.190,0.315)   # 進度(宽度还原)
nMID =(0.315,0.545)   # 进阶 1格
nSUP =(0.545,0.985)   # 至尊 2格

canvas=im.copy()
hy0,hy1=int(H*HEAD[0]),int(H*HEAD[1])
cy0,cy1=int(H*CELL[0]),int(H*CELL[1])

def place(src_x, dst_x):
    c=cr(src_x[0],src_x[1],CELL[0],CELL[1])
    tw=int(W*dst_x[1])-int(W*dst_x[0])
    c=c.resize((tw, cy1-cy0), Image.LANCZOS)
    canvas.paste(c,(int(W*dst_x[0]),cy0))

# 1) 奖励格区(无缝相邻):免费(压)/rail/进阶(复制至尊1格=付费锁态)/至尊(2格)
place(FREE_X,nFREE)
place(RAIL_X,nRAIL)
place(MID_X ,nMID)
place(SUP_X ,nSUP)

# 2) 列头:画干净的真实风格米色标签(免费/进阶/至尊)+锁
dr=ImageDraw.Draw(canvas)
# 先用米色覆盖整条列头带
head_bg=im.getpixel((int(W*0.12),int((HEAD[0]+HEAD[1])/2*H)))
dr.rectangle((0,hy0,W,hy1),fill=head_bg)
fnt=ImageFont.truetype(FONT,15)
BEIGE=(232,214,170); BORD=(150,120,70); TXTC=(92,54,20)
# 真实锁图标(从原至尊列头裁)
lock=cr(0.452,0.492,HEAD[0]+0.004,HEAD[1]-0.004)
def label(dst,text,locked):
    x0,x1=int(W*dst[0])+3,int(W*dst[1])-3
    dr.rounded_rectangle((x0,hy0+5,x1,hy1-4),radius=6,fill=BEIGE,outline=BORD,width=1)
    cx=(x0+x1)//2; cy=(hy0+hy1)//2
    lw=0
    if locked:
        lk=lock.resize((14,14),Image.LANCZOS); canvas.paste(lk,(cx-30,cy-7)); lw=16
    tb=dr.textbbox((0,0),text,font=fnt); tw=tb[2]-tb[0]
    dr.text((cx-tw//2+lw//2,cy-9),text,font=fnt,fill=TXTC)
label(nFREE,'免费',False)
label(nMID ,'进阶',True)
label(nSUP ,'至尊',True)
# 進度 头(原样真实裁)
rh=cr(RAIL_X[0],RAIL_X[1],HEAD[0],HEAD[1]).resize((int(W*nRAIL[1])-int(W*nRAIL[0]),hy1-hy0),Image.LANCZOS)
canvas.paste(rh,(int(W*nRAIL[0]),hy0))

# 3) 折扣徽章(3600%)真实裁→挪到至尊列右上
badge=cr(0.84,0.998,0.418,0.470)
canvas.paste(badge,(int(W*0.86),hy0-8))

# 4) 放大2x输出
big=canvas.resize((W*2,H*2),Image.LANCZOS)
p=os.path.join(OUT,'猎杀时刻_3档效果图_v3.png')
big.save(p)
print('saved',p,big.size)
