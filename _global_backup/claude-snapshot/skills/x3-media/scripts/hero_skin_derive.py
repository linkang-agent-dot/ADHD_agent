"""
X3 英雄皮肤：从一张透明主稿派生游戏内三件规格图。

背景：X3 英雄皮肤落地需要 4 件资产（三张 2D + 一条展示视频）。这个脚本管三张 2D，
把 AI 出的主稿（通常 1152x2048 白底，先过 remove_background）切成客户端要的规格。

规格与构图基准（2026-07-27 实测现役资源反推，非拍脑袋）：
  立绘   Role_F_<hero>_Skin<n>.png    1024x1536  角色占高 89~95%（取 92%），水平居中，脚底锚定
  英雄卡 Role_C_<hero>_Skin<n>.png    308x420    半身（头顶~腰），四边出血撑满
  头像   Img_C_H_<hero>_Skin<n>.png   256x256    脸部特写，圆形柔边 + 肩线平切

★主稿构图要求（决定头像糊不糊，2026-07-27 实证）：
  生成主稿时让人物**尽量占满画幅、别留大片白边**。头像 256×256 是脸部裁切后放大的，
  脸在主稿里的原始像素直接决定清晰度——人物占画幅 ~95%（bbox 高 1947/2048）时脸够清晰、
  免超分；留白多的主稿（人物只占 ~85%）脸就在糊的临界点上，得额外补一步超分再裁。

★核心手法：头像/英雄卡的边缘形状**直接复用该英雄现役皮肤的 alpha 通道当遮罩**，
  而不是自己画圆——这样新皮肤与游戏里现有资源的边缘形状 100% 一致，不会出现
  "这张图边缘跟别的皮肤不一样"的违和感。没有现役皮肤可参照时用 --no-mask 退化为硬边。

用法：
  python hero_skin_derive.py --src <透明主稿.png> --out <输出目录> --hero 20 --skin 01
  # 指定遮罩参照（默认自动找该英雄的 skin02 → skin01 → Lv1）
  python hero_skin_derive.py ... --mask-ref skin02
  # 微调构图（出图目检后调，每次只动一个）
  python hero_skin_derive.py ... --head-ratio 0.17 --card-body-ratio 0.45

调参指引（目检后按症状调）：
  头像切到下巴/露太多脖子  → --head-ratio 调大/调小（默认 0.155）
  头像人物偏左右           → --head-x-shift ±0.02
  英雄卡露到大腿/只到脖子  → --card-body-ratio（默认 0.42，越大取越多身体）
  立绘顶头/悬空            → --full-height-ratio / --full-bottom-pad
"""
import argparse, os, sys, glob
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DEFAULT_ROLE_DIR = r'C:\x3-project\client\Assets\Res\UI\Spirits\Role'


def bbox_of(im):
    """取非透明区域 bbox。alpha>10 阈值滤掉抠图残留的极淡边缘。"""
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a > 10)
    if len(ys) == 0:
        raise SystemExit('!! 源图全透明，检查抠图是否把主体也抠掉了')
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def find_mask_ref(role_dir, hero, kind, prefer=None):
    """找该英雄现役资源当遮罩模板。kind: 'HeroCard' | 'Character Portraits'"""
    prefix = {'HeroCard': 'Role_C', 'Character Portraits': 'Img_C_H'}[kind]
    d = os.path.join(role_dir, kind)
    if not os.path.isdir(d):
        return None
    cands = glob.glob(os.path.join(d, f'{prefix}_{hero}_*.png'))
    if not cands:
        return None
    if prefer:
        for c in cands:
            if prefer.lower() in os.path.basename(c).lower():
                return c
    # 优先 skin（皮肤形状比本体更贴近皮肤用途），其次 Lv1
    skins = [c for c in cands if 'skin' in os.path.basename(c).lower()]
    return (skins or cands)[0]


def drop_orphan_blobs(img, min_area_ratio=0.02):
    """
    清掉与主体不相连的孤立小碎块。

    为什么需要：半身/头部裁切会把举起的手臂、道具、飘带从主体上切断，
    框内只剩一小块 → 视觉上就是一坨莫名其妙的脏东西。
    （马戏节阿米娜 alt 版扶帽手臂就是这样在头像/英雄卡左上留了个黑碎块。）

    min_area_ratio: 面积小于「最大连通域 × 此比例」的独立域会被清掉。
    """
    try:
        import cv2
    except ImportError:
        print('  ! 无 cv2，跳过孤立碎块清理')
        return img, 0

    arr = np.array(img)
    binary = (arr[:, :, 3] > 10).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if n <= 2:
        return img, 0
    areas = stats[1:, cv2.CC_STAT_AREA]
    main_area = areas.max()
    dropped = 0
    for i, area in enumerate(areas, start=1):
        if area < main_area * min_area_ratio:
            arr[labels == i, 3] = 0
            dropped += 1
    return Image.fromarray(arr, 'RGBA'), dropped


def apply_mask(img, mask_path):
    if not mask_path or not os.path.exists(mask_path):
        return img, None
    mask = np.array(Image.open(mask_path).convert('RGBA'))[:, :, 3]
    if mask.shape[:2] != (img.height, img.width):
        mask = np.array(Image.fromarray(mask).resize((img.width, img.height), Image.LANCZOS))
    arr = np.array(img).astype(np.float32)
    arr[:, :, 3] = arr[:, :, 3] * (mask.astype(np.float32) / 255.0)
    return Image.fromarray(arr.astype(np.uint8), 'RGBA'), mask_path


def make_fulllength(src, a):
    W, H = 1024, 1536
    l, t, r, b = bbox_of(src)
    person = src.crop((l, t, r + 1, b + 1))
    pw, ph = person.size
    target_h = int(H * a.full_height_ratio)
    scale = target_h / ph
    person = person.resize((max(1, int(pw * scale)), target_h), Image.LANCZOS)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    x = (W - person.width) // 2
    y = H - int(H * a.full_bottom_pad) - person.height
    canvas.paste(person, (x, y), person)
    return canvas


def _crop_segment(src, y0, y1, cx, aspect):
    """按目标宽高比从源图裁一段，越界补透明。"""
    seg_h = y1 - y0
    crop_w = max(1, int(seg_h * aspect))
    x0 = int(cx - crop_w / 2)
    seg = Image.new('RGBA', (crop_w, seg_h), (0, 0, 0, 0))
    sx0, sx1 = max(0, x0), min(src.width, x0 + crop_w)
    sy0, sy1 = max(0, y0), min(src.height, y1)
    if sx1 > sx0 and sy1 > sy0:
        seg.paste(src.crop((sx0, sy0, sx1, sy1)), (sx0 - x0, sy0 - y0))
    return seg


def make_herocard(src, a, mask_path):
    W, H = 308, 420
    l, t, r, b = bbox_of(src)
    ph = b - t + 1
    y0, y1 = t, min(src.height, t + int(ph * a.card_body_ratio))
    cx = (l + r) / 2 + a.card_x_shift * (r - l)
    card = _crop_segment(src, y0, y1, cx, W / H).resize((W, H), Image.LANCZOS)
    card, used = apply_mask(card, mask_path)
    # ★碎块清理必须放在最后（最终分辨率 + 套完遮罩）：
    #   裁切后的原分辨率下，断肢常通过淡边缘像素还跟主体连着，缩放/套遮罩后才真正分离。
    if not a.keep_orphans:
        card, n = drop_orphan_blobs(card, a.orphan_ratio)
        if n:
            print(f'  英雄卡：清掉 {n} 个孤立碎块')
    return card, used


def make_portrait(src, a, mask_path):
    S = 256
    l, t, r, b = bbox_of(src)
    ph = b - t + 1
    head_h = int(ph * a.head_ratio)
    y0 = int(t - head_h * a.head_pad_top)
    y1 = int(t + head_h * (1 + a.head_pad_bottom))
    cx = (l + r) / 2 + a.head_x_shift * (r - l)
    port = _crop_segment(src, y0, y1, cx, 1.0).resize((S, S), Image.LANCZOS)
    port, used = apply_mask(port, mask_path)
    if not a.keep_orphans:
        port, n = drop_orphan_blobs(port, a.orphan_ratio)
        if n:
            print(f'  头像：清掉 {n} 个孤立碎块')
    return port, used


def main():
    p = argparse.ArgumentParser(description='X3 英雄皮肤主稿 → 三件规格图')
    p.add_argument('--src', required=True, help='透明主稿 PNG（先过 remove_background）')
    p.add_argument('--out', required=True, help='输出目录')
    p.add_argument('--hero', required=True, help='英雄 id，如 20')
    p.add_argument('--skin', default='01', help='皮肤编号，默认 01')
    p.add_argument('--tag', default='', help='文件名后缀标签（出多版对比时用）')
    p.add_argument('--role-dir', default=DEFAULT_ROLE_DIR, help='客户端 Role 资源目录（找遮罩模板用）')
    p.add_argument('--mask-ref', default=None, help='遮罩参照关键词，如 skin02；默认自动挑')
    p.add_argument('--no-mask', action='store_true', help='不套遮罩，输出硬边')
    p.add_argument('--full-height-ratio', type=float, default=0.92)
    p.add_argument('--full-bottom-pad', type=float, default=0.03)
    p.add_argument('--card-body-ratio', type=float, default=0.42)
    p.add_argument('--card-x-shift', type=float, default=0.0)
    p.add_argument('--head-ratio', type=float, default=0.155)
    p.add_argument('--head-pad-top', type=float, default=0.02)
    p.add_argument('--head-pad-bottom', type=float, default=0.06)
    p.add_argument('--head-x-shift', type=float, default=0.0)
    p.add_argument('--keep-orphans', action='store_true',
                   help='保留孤立碎块（默认清理裁切造成的断肢/断道具碎片）')
    p.add_argument('--orphan-ratio', type=float, default=0.02,
                   help='小于主体面积此比例的独立域视为碎块，默认 0.02')
    a = p.parse_args()

    os.makedirs(a.out, exist_ok=True)
    src = Image.open(a.src).convert('RGBA')

    # ⛔ 输入闸门：源图必须是**已抠好的 RGBA 立绘**，不能是白底主稿。
    # 为什么：apply_mask 是 alpha 相乘（arr[:,:,3] *= mask/255，这一步本身是对的）。
    # 但白底主稿的 alpha 恒为 255，相乘后等于直接采用遮罩形状——遮罩内**没有人物**的地方
    # 露出来的就是白底 RGB → 白块从新轮廓的缝隙里透出。2026-07-29 三档规格图全废重跑就是这个。
    _a = np.array(src)[:, :, 3]
    _transparent_ratio = (_a < 16).mean()
    if _transparent_ratio < 0.02:
        raise SystemExit(
            f'!! 源图几乎没有透明区域（透明占比 {_transparent_ratio*100:.1f}%），'
            f'多半是白底主稿而非抠好的立绘。\n'
            f'   直接用会让白块从遮罩缝隙透出（历史事故：三档规格图全废重跑）。\n'
            f'   请先跑 remove_background 得到 RGBA 立绘再喂进来；\n'
            f'   确实要用硬边无遮罩输出请显式加 --no-mask。')

    print(f'源图 {src.size}  bbox={bbox_of(src)}  透明占比={_transparent_ratio*100:.1f}%')

    suffix = f'_{a.tag}' if a.tag else ''
    card_mask = None if a.no_mask else find_mask_ref(a.role_dir, a.hero, 'HeroCard', a.mask_ref)
    port_mask = None if a.no_mask else find_mask_ref(a.role_dir, a.hero, 'Character Portraits', a.mask_ref)

    results = []
    full = make_fulllength(src, a)
    fp = os.path.join(a.out, f'Role_F_{a.hero}_Skin{a.skin}{suffix}.png')
    full.save(fp); results.append((fp, None))

    card, cm = make_herocard(src, a, card_mask)
    fp = os.path.join(a.out, f'Role_C_{a.hero}_Skin{a.skin}{suffix}.png')
    card.save(fp); results.append((fp, cm))

    port, pm = make_portrait(src, a, port_mask)
    fp = os.path.join(a.out, f'Img_C_H_{a.hero}_Skin{a.skin}{suffix}.png')
    port.save(fp); results.append((fp, pm))

    print()
    for fp, mask in results:
        im = Image.open(fp)
        note = f'  [遮罩: {os.path.basename(mask)}]' if mask else ''
        print(f'  ✓ {os.path.basename(fp)}  {im.size}  {os.path.getsize(fp)//1024}KB{note}')
    print('\n⚠️ 出图后必须目检：头像有没有切到下巴/露太多脖子、英雄卡截断位置、立绘有没有顶头或悬空。')
    print('   按脚本头部「调参指引」调，每次只动一个参数。')


if __name__ == '__main__':
    main()
