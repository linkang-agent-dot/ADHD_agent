# -*- coding: utf-8 -*-
"""入场片拼装(可复用): SegA + [缝1: 4帧交叉淡化] + SegB + [缝2: 10帧渐变到循环首帧] + 循环首帧本体。
终帧=循环视频首帧逐像素 → 客户端入场片播完切循环零跳变。
缝处理原则: 同姿势缝才能crossfade(高运动缝禁用,见知识库§四); 缝2用"渐变到目标真像素"根治交棒。
用法: python assemble_intro.py <segA.mp4> <segB.mp4> <loop.mp4> <out_intro.mp4> [out_preview.mp4]"""
import io, sys, cv2, numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
segA, segB, loop_p, out_p = sys.argv[1:5]
prev_p = sys.argv[5] if len(sys.argv) > 5 else None
def frames(p):
    cap = cv2.VideoCapture(p); o = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        o.append(fr)
    cap.release(); return o
A, B, LOOP = frames(segA), frames(segB), frames(loop_p)
H, W = A[0].shape[:2]
out = []
XF1 = 4
out += A[:-XF1]
for i in range(XF1):
    t = (i + 1) / (XF1 + 1)
    out.append(cv2.addWeighted(A[len(A)-XF1+i], 1-t, B[0], t, 0))
out += B[:-2]
for i in range(10):
    t = (i + 1) / 10
    out.append(cv2.addWeighted(B[-2], 1-t, LOOP[0], t, 0))
out.append(LOOP[0].copy())
def write(path, frs):
    vw = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), 24, (W, H))
    for fr in frs: vw.write(fr)
    vw.release()
write(out_p, out)
if prev_p: write(prev_p, out + LOOP + LOOP)
print('intro %.1fs 终缝diff %.2f' % (len(out)/24, np.abs(out[-1].astype(int)-LOOP[0].astype(int)).mean()))
