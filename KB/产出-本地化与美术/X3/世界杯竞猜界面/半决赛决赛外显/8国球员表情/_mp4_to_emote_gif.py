# -*- coding: utf-8 -*-
"""角色版动效 mp4 → 透明循环 GIF/.bytes(对齐现役Emoticons:160x160·~1.2s·透明底)。
每帧从边缘 flood 抠白(只去与边相连的白·保留角色内部白/球衣)→缩160→组透明GIF(铁律:transparency+disposal=2+loop)。
用法: python _mp4_to_emote_gif.py <mp4...>  ;  产出同目录 _GIF/<名>.gif + .bytes"""
import os, sys, io, glob, shutil
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SIZE = 160          # 成品边长(对齐Emoticons)
NFRAMES = 30        # 采样帧数(密采防卡顿·从原视频97帧里取)
DUR = 85            # 每帧ms(30×85≈2.55s·慢速且顺滑)
WHITE = 238         # 近白阈值(min(RGB)>=此=白底候选)

def cut_white(rgb):
    """rgb:HxWx3 uint8 → alpha:HxW uint8。去与边缘相连的近白,保留内部白。"""
    R,G,B = rgb[...,0].astype(int),rgb[...,1].astype(int),rgb[...,2].astype(int)
    nearwhite = (np.minimum(np.minimum(R,G),B) >= WHITE)
    lbl,n = ndimage.label(nearwhite)
    # 收集触边的label
    border = set(lbl[0,:]) | set(lbl[-1,:]) | set(lbl[:,0]) | set(lbl[:,-1])
    border.discard(0)
    bg = np.isin(lbl, list(border))
    alpha = np.where(bg, 0, 255).astype('uint8')
    # 羽化边缘1px(去锯齿)——对alpha做一次腐蚀避免白边残留
    alpha = ndimage.grey_erosion(alpha, size=(2,2))
    return alpha

def mp4_to_gif(mp4, outdir):
    cap = cv2.VideoCapture(mp4); N=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    idxs = [int(round(i*(N-1)/(NFRAMES-1))) for i in range(NFRAMES)]
    frames=[]
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES,i); ok,fr=cap.read()
        if not ok: continue
        rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        a = cut_white(rgb)
        rgba = np.dstack([rgb, a])
        im = Image.fromarray(rgba,"RGBA")
        # 裁到内容bbox再等比放进160(留8px边)——各帧统一用第一帧bbox避免抖动
        frames.append(im)
    cap.release()
    if not frames: print(mp4,"无帧"); return
    # 用所有帧的并集bbox(角色挥手会动)稳定构图
    union=None
    for im in frames:
        bb=im.split()[3].point(lambda p:255 if p>30 else 0).getbbox()
        if bb: union=bb if union is None else (min(union[0],bb[0]),min(union[1],bb[1]),max(union[2],bb[2]),max(union[3],bb[3]))
    out_frames=[]
    for im in frames:
        c=im.crop(union); cw,ch=c.size
        s=(SIZE-12)/max(cw,ch); c=c.resize((max(1,int(cw*s)),max(1,int(ch*s))),Image.LANCZOS)
        canvas=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0))
        canvas.alpha_composite(c,((SIZE-c.width)//2,(SIZE-c.height)//2))
        # 透明GIF帧(铁律:二值alpha→索引255透明·palette末位设白避免滤波黑边)
        a=canvas.split()[3]; mask=a.point(lambda p:255 if p>=128 else 0)
        p=canvas.convert("RGB").convert("P",palette=Image.ADAPTIVE,colors=255)
        p.paste(255, mask.point(lambda v:255-v).convert("1"))
        pal=p.getpalette(); pal[255*3:255*3+3]=[255,255,255]; p.putpalette(pal)  # 透明项=白
        out_frames.append(p)
    name=os.path.splitext(os.path.basename(mp4))[0].replace("_anim","")
    os.makedirs(outdir,exist_ok=True)
    gp=os.path.join(outdir,name+".gif")
    out_frames[0].save(gp,save_all=True,append_images=out_frames[1:],
                       duration=DUR,loop=0,transparency=255,disposal=2,background=255,optimize=False)
    shutil.copyfile(gp, os.path.join(outdir,name+".bytes"))
    print(f"{name}: {os.path.getsize(gp)//1024}KB {len(out_frames)}帧 -> {gp}")

if __name__=="__main__":
    for m in sys.argv[1:]:
        mp4_to_gif(m, os.path.join(os.path.dirname(m),"_GIF"))
