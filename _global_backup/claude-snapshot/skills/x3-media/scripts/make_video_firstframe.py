"""
把角色主稿重排进目标画幅，做成视频首帧。

## 为什么需要这一步（两个都是踩过的坑）

**① 画幅不匹配 → AI 自行裁切，构图失控**
主稿常是 4:3 或别的比例，视频要 9:16。直接把 4:3 图当首帧喂进去，
模型会自己决定怎么裁/补边，人物位置和大小全不可控。

**② 人物顶满画幅 → 大动作甩出框**
足球宝贝 v6/v8 实测：ref 图人物占满画幅时，AI 一做举手/张臂就把道具或手甩出画外，
而且**缩小角色救不了**——因为是动作幅度够到了框外，不是人物太大。
治本＝喂图时就让出安全边距，模型会全片继承这个构图尺度。
默认占高 0.86 是留够余量的经验值；纯 idle 无大动作的可以放到 0.92。

**③ 底色用白不用透明**
透明区域会被模型当成黑色或噪声。视频生成一律喂不透明底，
需要透明成片的走后续 remove_background → export_sbs_video 链路。

## 用法

    python make_video_firstframe.py --src <透明主稿.png> --out <首帧.png>
    # 自定义画幅与占比
    python make_video_firstframe.py --src a.png --out b.png --width 810 --height 1080 --height-ratio 0.92

透明主稿从哪来：原始主稿走 x3-media remove_background 抠白底后的 RGBA 图。
"""
import argparse
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def main():
    p = argparse.ArgumentParser(description='角色主稿 → 视频首帧（重排画幅+留动作边距）')
    p.add_argument('--src', required=True, help='透明主稿 PNG（RGBA，已抠底）')
    p.add_argument('--out', required=True, help='输出首帧 PNG')
    p.add_argument('--width', type=int, default=1080, help='目标宽，默认 1080')
    p.add_argument('--height', type=int, default=1920, help='目标高，默认 1920（9:16）')
    p.add_argument('--height-ratio', type=float, default=0.86,
                   help='人物占画幅高度比例，默认 0.86（留动作余量）；纯 idle 可放到 0.92')
    p.add_argument('--bottom-pad', type=float, default=0.05, help='脚底距底边比例，默认 0.05')
    p.add_argument('--bg', default='255,255,255', help='背景色 R,G,B，默认白底')
    a = p.parse_args()

    src = Image.open(a.src).convert('RGBA')
    alpha = np.array(src)[:, :, 3]
    ys, xs = np.where(alpha > 10)
    if len(ys) == 0:
        raise SystemExit('!! 源图全透明，检查抠图是否把主体也抠掉了')

    l, t, r, b = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
    person = src.crop((l, t, r + 1, b + 1))

    target_h = int(a.height * a.height_ratio)
    scale = target_h / person.height
    person = person.resize((max(1, int(person.width * scale)), target_h), Image.LANCZOS)

    bg = tuple(int(v) for v in a.bg.split(','))
    canvas = Image.new('RGB', (a.width, a.height), bg)
    x = (a.width - person.width) // 2
    y = a.height - int(a.height * a.bottom_pad) - person.height
    canvas.paste(person, (x, y), person)
    canvas.save(a.out)

    print(f'首帧已生成 {canvas.size}')
    print(f'  人物 {person.width}x{person.height}  占高 {person.height/a.height*100:.1f}%  占宽 {person.width/a.width*100:.1f}%')
    print(f'  左右余量各 {x}px  顶部 {y}px  底部 {a.height-y-person.height}px')
    if x < 60:
        print('  ⚠️ 左右余量偏小，大动作可能超框——考虑调低 --height-ratio')
    print(f'  → {a.out}')


if __name__ == '__main__':
    main()
