# -*- coding: utf-8 -*-
# 审片：抽 首/中/尾 帧 + 首尾帧差(循环) + 帧间运动量
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import cv2
import numpy as np

ASSETS = r'C:\ADHD_agent\KB\产出-数值设计\X3_皮肤互动视频\demo\_assets'

def check(name):
    path = os.path.join(ASSETS, name)
    if not os.path.exists(path):
        print(name, 'MISSING'); return
    cap = cv2.VideoCapture(path)
    frames = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        frames.append(fr)
    cap.release()
    n = len(frames)
    if n == 0:
        print(name, 'NO FRAMES'); return
    first, mid, last = frames[0], frames[n//2], frames[-1]
    seam = float(np.mean(cv2.absdiff(first, last)))
    diffs = [float(np.mean(cv2.absdiff(frames[i], frames[i+1]))) for i in range(0, n-1, 4)]
    motion = float(np.mean(diffs))
    base = name.replace('.mp4', '')
    for tag, fr in (('first', first), ('mid', mid), ('last', last)):
        cv2.imencode('.jpg', fr, [cv2.IMWRITE_JPEG_QUALITY, 85])[1].tofile(os.path.join(ASSETS, f'_{base}_{tag}.jpg'))
    print(f'{name}: {n}帧 首尾差={seam:.2f}(循环<8可接受) 运动量={motion:.2f}(木头<3.5/正常4-7)')

for v in ('gen_idle.mp4', 'gen_reject.mp4', 'gen_greet.mp4', 'gen_touch_body_high.mp4'):
    check(v)
