# -*- coding: utf-8 -*-
"""
足球宝贝·爱莉希雅(104001) 2D三件套：从主稿FINAL直接加工（抠像+裁切），不重新生成。
格式锚=爱莉希雅本体: Img_C_H_40(256x256头胸) / Role_C_40(306x418半身) / Role_F_40(1024x1536全身)，全透明底。
产出: Img_C_H_40_Skin01.png / Role_C_40_Skin01.png / Role_F_40_Skin01.png + 棋盘格预览 + 透明差分验证
"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '足球宝贝爱莉希雅_主稿_FINAL.png')

# ---------- 1) 抠像（直接跑 u2net.onnx，绕开 rembg/pymatting——pymatting 的 numba 会死循环） ----------
cut_path = os.path.join(HERE, 'cut_full.png')
if not os.path.exists(cut_path):
    import onnxruntime as ort
    src = Image.open(SRC).convert('RGBA')
    print('主稿:', src.size)
    rgb = src.convert('RGB')
    inp = rgb.resize((320, 320), Image.LANCZOS)
    x = np.array(inp).astype(np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    sess = ort.InferenceSession(os.path.expanduser('~/.u2net/u2net.onnx'),
                                providers=['CPUExecutionProvider'])
    pred = sess.run(None, {sess.get_inputs()[0].name: x})[0][0, 0]
    pred = (pred - pred.min()) / (pred.max() - pred.min() + 1e-8)
    mask = Image.fromarray((pred * 255).astype(np.uint8)).resize(src.size, Image.LANCZOS)
    m = np.array(mask).astype(np.float32) / 255.0
    # 白底图增强：mask 软边外的近白像素压到 0，主体内拉满，中间过渡保留
    m = np.clip((m - 0.05) / 0.90, 0, 1)
    out_arr = np.array(src)
    out_arr[:, :, 3] = (m * 255).astype(np.uint8)
    out = Image.fromarray(out_arr)
    out.save(cut_path)
cut = Image.open(cut_path).convert('RGBA')
a = np.array(cut)[:, :, 3]
bbox = cut.getbbox()
print('cut:', cut.size, 'bbox:', bbox)
x0, y0, x1, y1 = bbox
pw, ph = x1 - x0, y1 - y0  # 人物实际宽高

# 脸部中心x：取头部区域(人物顶部12%)的alpha质心
head_band = a[y0:y0 + int(ph * 0.12), x0:x1]
cols = head_band.sum(axis=0)
face_cx = x0 + int(np.average(np.arange(len(cols)), weights=cols + 1))

# ---------- 2) 立绘 1024x1536 (人物占高97%,水平居中) ----------
W, H = 1024, 1536
target_h = int(H * 0.97)
scale = target_h / ph
person = cut.crop(bbox).resize((int(pw * scale), target_h), Image.LANCZOS)
canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
canvas.paste(person, ((W - person.width) // 2, (H - target_h) // 2), person)
canvas.save(os.path.join(HERE, 'Role_F_40_Skin01.png'))
print('立绘 OK', canvas.size)

# ---------- 3) 英雄卡 306x418 (头顶到腰胯,~45%人高,半身出血) ----------
CW, CH = 306, 418
crop_h = int(ph * 0.45)
crop_w = int(crop_h * CW / CH)
cx0 = face_cx - crop_w // 2
cy0 = y0 - int(ph * 0.015)  # 头顶留一点
card = cut.crop((cx0, cy0, cx0 + crop_w, cy0 + crop_h)).resize((CW, CH), Image.LANCZOS)
card.save(os.path.join(HERE, 'Role_C_40_Skin01.png'))
print('英雄卡 OK', card.size)

# ---------- 4) 头像 256x256 圆形徽章构图 ----------
# ★格式铁律(2026-06-12行军HUD穿帮实测): 头像不是方形满幅!
#   标准=圆形主体(直径~208px,圆心(128,132))+四边四角全透明(margin>=16px)，
#   HUD圆框直接渲染原图，满幅方图会画到圆框外穿帮。锚=Img_C_H_39_Skin01。
D = 208                      # 圆直径
CCX, CCY = 128, 132          # 圆心
hh = int(ph * 0.21)          # 取头到锁骨，脸部占比对齐34_Skin01锚
hx0 = face_cx - hh // 2
hy0 = y0 - int(ph * 0.01)
head_src = cut.crop((hx0, hy0, hx0 + hh, hy0 + hh)).resize((D + 24, D + 24), Image.LANCZOS)
canvas_h = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
canvas_h.paste(head_src, (CCX - head_src.width // 2, CCY - head_src.height // 2), head_src)
# 圆形遮罩(4x超采样抗锯齿)
from PIL import ImageDraw
mk = Image.new('L', (1024, 1024), 0)
ImageDraw.Draw(mk).ellipse((4*(CCX - D//2), 4*(CCY - D//2), 4*(CCX + D//2), 4*(CCY + D//2)), fill=255)
mk = mk.resize((256, 256), Image.LANCZOS)
arr_h = np.array(canvas_h)
arr_h[:, :, 3] = np.minimum(arr_h[:, :, 3], np.array(mk))
head = Image.fromarray(arr_h)
head.save(os.path.join(HERE, 'Img_C_H_40_Skin01.png'))
print('头像 OK(圆形)', head.size)

# ---------- 5) 透明差分验证 (feedback_transparent_asset_diff_check) ----------
def verify(p):
    im = Image.open(p).convert('RGBA')
    arr = np.array(im).astype(int)
    al = arr[:, :, 3]
    w = Image.new('RGBA', im.size, (255, 255, 255, 255)); w.paste(im, (0, 0), im)
    b = Image.new('RGBA', im.size, (0, 0, 0, 255)); b.paste(im, (0, 0), im)
    diff = np.abs(np.array(w).astype(int) - np.array(b).astype(int))[:, :, :3].mean()
    print('%s alpha[min%d max%d 全透%d%% 半透%d%%] 白黑差分%.1f %s' % (
        os.path.basename(p), al.min(), al.max(),
        (al == 0).mean() * 100, ((al > 0) & (al < 255)).mean() * 100, diff,
        'OK真透明' if diff > 1 else '!!疑似假透明'))

# ---------- 6) 棋盘格预览 ----------
def checker_preview(paths, out):
    imgs = [Image.open(p).convert('RGBA') for p in paths]
    th = 420
    tiles = []
    for im in imgs:
        s = th / im.height
        tiles.append(im.resize((int(im.width * s), th), Image.LANCZOS))
    gap = 20
    tw = sum(t.width for t in tiles) + gap * (len(tiles) + 1)
    cv = Image.new('RGBA', (tw, th + gap * 2), (255, 255, 255, 255))
    for yy in range(0, cv.height, 16):
        for xx in range(0, cv.width, 16):
            if (xx // 16 + yy // 16) % 2:
                cv.paste((204, 204, 204, 255), (xx, yy, min(xx + 16, cv.width), min(yy + 16, cv.height)))
    x = gap
    for t in tiles:
        cv.paste(t, (x, gap), t)
        x += t.width + gap
    cv.convert('RGB').save(out)
    print('预览:', out)

outs = [os.path.join(HERE, n) for n in
        ('Img_C_H_40_Skin01.png', 'Role_C_40_Skin01.png', 'Role_F_40_Skin01.png')]
for p in outs:
    verify(p)
checker_preview(outs, os.path.join(HERE, '_预览_棋盘格.png'))
print('DONE')
