# -*- coding: utf-8 -*-
r"""英雄皮肤 SBS 视频落库 + 四处注册（一条命令做完，别手改）。

四处缺一不可：
  ① 视频文件 + .meta（Unity 靠 meta 里的 guid 认资源，新文件必须给新 guid）
  ② Display_Video.asset      —— DK 定义（key/type/desc/guid/exportCode）
  ③ Path_Video.asset         —— **两处**：顶部 key 清单 + 下方 key→objPath 映射
  ④ tableResInfo.txt         —— ⚠️最容易漏。漏登=图/视频在仓里但**不进包**，
                                 游戏里显示"没有资源"（马戏节头衔大图栽过）。
                                 换图沿用同名 DK 不受影响，**新增 DK 必登**。

用法: python deploy_skin_video.py <源mp4> <落库文件名.mp4> <DK名> <中文描述>
例:   python deploy_skin_video.py amber_skin01_sbs.mp4 amber_skin01_sbs.mp4 DK_video_amber_skin01_sbs "马戏节琥珀魔术师皮肤展示视频"
"""
import io, os, re, shutil, sys, uuid

WT = r'C:\x3-project\wt_circus_card\client'
VIDEO_DIR = os.path.join(WT, r'Assets\Res\Video\VideoRes\HeroSkin')
DISPLAY = os.path.join(WT, r'Assets\Editor\Config\DisplayKey\Display_Video.asset')
PATH = os.path.join(WT, r'Assets\Res\Config\DisplayKey\Path_Video.asset')
RESINFO = os.path.join(WT, r'Assets\Editor\Config\tableResInfo.txt')
OBJ_PREFIX = 'Assets/Res/Video/VideoRes/HeroSkin/'


def read(p):
    with io.open(p, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write(p, t):
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)


def cn_escape(s):
    """Unity .asset 的 desc 用 \\uXXXX 转义中文（照现役条目的写法）。"""
    return ''.join(c if ord(c) < 128 else '\\u%04X' % ord(c) for c in s)


def main(src, fname, dk, desc):
    key = dk[3:] if dk.startswith('DK_') else dk        # Display_Video 里的 key 不带 DK_ 前缀
    guid = uuid.uuid4().hex
    dst = os.path.join(VIDEO_DIR, fname)

    # ① 视频 + meta
    shutil.copy2(src, dst)
    meta_tpl = read(os.path.join(VIDEO_DIR, 'amina_skin01_sbs.mp4.meta'))
    meta = re.sub(r'guid: [0-9a-f]{32}', f'guid: {guid}', meta_tpl, count=1)
    write(dst + '.meta', meta)
    print(f'① 视频 {fname} ({os.path.getsize(dst)} bytes) + meta guid={guid}')

    # ② Display_Video.asset —— 插在锚点条目之前，保持字母序
    t = read(DISPLAY)
    anchor = '  - key: video_amina_skin01_sbs'
    if f'key: {key}\n' in t:
        raise SystemExit(f'!! Display_Video 已存在 key: {key}')
    entry = (f'  - key: {key}\n    type: Video\n'
             f'    desc: "{cn_escape(desc)}"\n    guid: {guid}\n    exportCode: 1\n')
    if anchor not in t:
        raise SystemExit('!! Display_Video 找不到锚点条目')
    write(DISPLAY, t.replace(anchor, entry + anchor, 1))
    print(f'② Display_Video 已加 key: {key}')

    # ③ Path_Video.asset —— 两处都要
    t = read(PATH)
    if f'- {dk}\n' in t or f'key: {dk}\n' in t:
        raise SystemExit(f'!! Path_Video 已存在 {dk}')
    a1 = '    - DK_video_amina_skin01_sbs'
    a2 = '    - key: DK_video_amina_skin01_sbs'
    for a in (a1, a2):
        if a not in t:
            raise SystemExit(f'!! Path_Video 找不到锚点: {a}')
    t = t.replace(a1, f'    - {dk}\n{a1}', 1)
    t = t.replace(a2, f'    - key: {dk}\n      objPath: {OBJ_PREFIX}{fname}\n{a2}', 1)
    write(PATH, t)
    print(f'③ Path_Video 已加 {dk}（清单 + objPath 映射两处）')

    # ④ tableResInfo.txt —— 漏这步 = 不进包
    t = read(RESINFO)
    lines = t.split('\n')
    if dk in [l.strip() for l in lines]:
        raise SystemExit(f'!! tableResInfo 已存在 {dk}')
    anchor_i = next((i for i, l in enumerate(lines)
                     if l.strip() == 'DK_video_amina_skin01_sbs'), None)
    if anchor_i is None:
        raise SystemExit('!! tableResInfo 找不到锚点')
    lines.insert(anchor_i, dk)          # amber < amina，插在它前面保持字母序
    write(RESINFO, '\n'.join(lines))
    print(f'④ tableResInfo 已加 {dk}（第 {anchor_i+1} 行，字母序）')

    print('\n✅ 四处注册完成')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main(*sys.argv[1:5])
