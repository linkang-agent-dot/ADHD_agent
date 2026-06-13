# -*- coding: utf-8 -*-
"""视频四边超框检测(可复用): 每帧四边3px条带扫非背景暗像素(<215灰度,>1%即判贴边)。
用法: python check_video_edges.py <video.mp4> [基线video.mp4]
判读: right 前几帧=入场合法 / bottom=地面阴影多半合法 / top与left大量命中=动作甩出框,要治。"""
import io, sys, cv2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
def profile(path):
    cap = cv2.VideoCapture(path)
    hits = {'top': [], 'bottom': [], 'left': [], 'right': []}
    idx = 0
    while True:
        ok, fr = cap.read()
        if not ok: break
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        for name, strip in (('top', g[:3, :]), ('bottom', g[-3:, :]),
                            ('left', g[:, :3]), ('right', g[:, -3:])):
            if (strip < 215).mean() > 0.01:
                hits[name].append(idx)
        idx += 1
    cap.release()
    return hits, idx
for p in sys.argv[1:]:
    h, n = profile(p)
    print(p, '总帧', n)
    for k, v in h.items():
        print('  %s: %d帧' % (k, len(v)), ('首尾示例 ' + str(v[:5] + (['...'] if len(v) > 10 else []) + v[-3:])) if v else '')
