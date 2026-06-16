# -*- coding: utf-8 -*-
"""素材实体占画布比例规范化:实体等比缩到目标占比,放回原画布指定位置,可选加底部落地阴影。
用法: python rescale_to_canvas.py <in.png> <out.png> [ratio=0.76] [anchor] [bottom_margin] [shadow=0|1]
  anchor: center(居中) | bottom(底对齐,留原底边距) | margin(用 bottom_margin 指定底边距px,对齐参考素材位置)
  bottom_margin: anchor=margin 时生效,实体底距画布底的像素(对齐春节箱:闭箱~87 开箱~88)
  shadow: 1=在实体底部正中加半透明椭圆落地阴影(解决AI素材悬空,对齐春节箱有影);默认0
为什么:AI 生成的箱子/物件常无落地阴影→缩小居中后显得悬空。春节开箱箱(img_Activity_NewYear_box_1/2)
       底部自带椭圆投影有实感→给世界杯箱补同款椭圆阴影对齐。
"""
import sys
from PIL import Image, ImageDraw, ImageFilter

def rescale(inp, out, ratio=0.76, anchor="center", bottom_margin=None, shadow=False,
            shadow_w_ratio=0.82, shadow_h=None, shadow_alpha=105, shadow_blur=8):
    im = Image.open(inp).convert("RGBA"); W,H = im.size
    bbox = im.split()[3].getbbox()
    if not bbox: im.save(out); print("no content"); return
    l,t,r,b = bbox; cw,ch = r-l, b-t
    body = im.crop(bbox)
    scale = (max(W,H)*ratio)/max(cw,ch)
    nw,nh = max(1,int(cw*scale)), max(1,int(ch*scale))
    body = body.resize((nw,nh), Image.LANCZOS)
    x = (W-nw)//2
    if anchor=="bottom":
        y = H - (H-b) - nh
    elif anchor=="margin" and bottom_margin is not None:
        y = H - bottom_margin - nh
    else:
        y = (H-nh)//2
    y = max(0, y)
    canvas = Image.new("RGBA",(W,H),(0,0,0,0))
    if shadow:
        # 阴影=对称扁椭圆,按【箱体水平中心 x+nw//2】(不是画布中心W//2,否则箱体偏移时影子露左/右),贴箱底正下方
        sw=int(nw*shadow_w_ratio); sh=shadow_h if shadow_h else max(16,int(nw*0.13))
        scx=x+nw//2; scy=y+nh-sh//2+2
        sl=Image.new("RGBA",(W,H),(0,0,0,0))
        ImageDraw.Draw(sl).ellipse((scx-sw//2,scy-sh//2,scx+sw//2,scy+sh//2),fill=(0,0,0,shadow_alpha))
        canvas.alpha_composite(sl.filter(ImageFilter.GaussianBlur(shadow_blur)))
    canvas.alpha_composite(body,(x,y))
    canvas.save(out)
    print(f"{out}: body {cw}x{ch}->{nw}x{nh} scale={scale:.3f} ratio={ratio} anchor={anchor} y={y} 底边距={H-(y+nh)} shadow={shadow}")

if __name__=="__main__":
    inp,out=sys.argv[1],sys.argv[2]
    ratio=float(sys.argv[3]) if len(sys.argv)>3 else 0.76
    anchor=sys.argv[4] if len(sys.argv)>4 else "center"
    bm=int(sys.argv[5]) if len(sys.argv)>5 else None
    shadow=bool(int(sys.argv[6])) if len(sys.argv)>6 else False
    rescale(inp,out,ratio,anchor,bm,shadow)
