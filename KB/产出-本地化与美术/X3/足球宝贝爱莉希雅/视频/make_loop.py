# -*- coding: utf-8 -*-
"""crossfade治循环接缝: 尾K帧交叉淡入头部→无缝循环。
原理: 输出长L=N-K, 头K帧用 尾帧(1-w)+头帧(w) 渐变混合, 使循环点落在原视频连续两帧之间(天然平滑)。"""
import cv2, numpy as np, io, sys, os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
D=r'C:\ADHD_agent\KB\产出-本地化与美术\X3\足球宝贝爱莉希雅\视频'
SRC=os.path.join(D,'足球宝贝_idle循环_v7_seedance_1.mp4')
TMP=os.path.join(D,'v7_loop_xfade.mp4')   # ASCII临时名(VideoWriter稳)
DST=os.path.join(D,'足球宝贝_v8_无缝循环_1.mp4')
K=18  # crossfade帧数(~0.75s@24fps)

cap=cv2.VideoCapture(SRC)
N=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
W=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frames=[]
while True:
    r,f=cap.read()
    if not r: break
    frames.append(f)
cap.release()
N=len(frames); L=N-K
print(f'源 {N}帧 {fps:.0f}fps {W}x{H} → 输出 {L}帧 (crossfade K={K})')

vw=cv2.VideoWriter(TMP,cv2.VideoWriter_fourcc(*'mp4v'),fps,(W,H))
for i in range(L):
    base=frames[i].astype(np.float32)
    if i<K:
        tail=frames[i+L].astype(np.float32)  # = frames[i+N-K]
        w=i/K
        out=(1-w)*tail + w*base
    else:
        out=base
    vw.write(np.clip(out,0,255).astype(np.uint8))
vw.release()
if os.path.exists(DST): os.remove(DST)
os.replace(TMP,DST)

# 验首尾差
cap=cv2.VideoCapture(DST); n2=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.set(cv2.CAP_PROP_POS_FRAMES,0);_,a=cap.read()
cap.set(cv2.CAP_PROP_POS_FRAMES,n2-1);_,b=cap.read()
cap.release()
print(f'输出 {DST}')
print(f'  {n2}帧 {n2/fps:.1f}s | 新首尾差={np.abs(a.astype(int)-b.astype(int)).mean():.2f} (原v7=1.79,越小越无缝)')
