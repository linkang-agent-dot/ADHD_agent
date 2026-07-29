# -*- coding: utf-8 -*-
"""UI循环视频动态强度/循环接缝/局部稳定性检测。
用法: python check_video_motion.py <video.mp4> [参照.mp4] [--region x,y,w,h]
标尺(X3实测): 深海参照 0.22 好 / 0.15 及格 / 0.067 偏静 / 0.02 静止图
"""
import cv2, numpy as np, sys

def analyze(path, region=None):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames, diffs, prev = [], [], None
    while True:
        ok, f = cap.read()
        if not ok: break
        frames.append(f)
        g = f
        if region:
            x, y, w, h = region
            g = f[y:y+h, x:x+w]
        g = cv2.cvtColor(cv2.resize(g, (200, 266)), cv2.COLOR_BGR2GRAY).astype(float)
        if prev is not None: diffs.append(np.abs(g - prev).mean())
        prev = g
    cap.release()
    seam = np.abs(frames[0].astype(float) - frames[-1].astype(float)).mean()
    return dict(n=len(frames), sec=len(frames)/fps, size=(frames[0].shape[1], frames[0].shape[0]),
                motion=float(np.mean(diffs)), seam=float(seam))

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    reg = None
    for a in sys.argv[1:]:
        if a.startswith('--region'):
            reg = tuple(int(x) for x in a.split('=')[1].split(','))
    for p in args:
        r = analyze(p, reg)
        print('%-46s %d帧/%.2fs %dx%d  动态=%.3f  首尾差=%.2f' %
              (p.split('/')[-1], r['n'], r['sec'], r['size'][0], r['size'][1], r['motion'], r['seam']))
