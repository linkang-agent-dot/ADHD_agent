# -*- coding: utf-8 -*-
r"""英雄皮肤三件规格图落库 + DK 注册（立绘/英雄卡/头像）。

每个 DK 要三处齐全，缺一不可：
  ① 图片 + .meta（Unity 靠 meta guid 认资源，新文件必须给新 guid）
  ② Display_Role.asset  —— DK 定义（key 不带 DK_ 前缀 / type=Role / guid / exportCode=0）
  ③ Path_Role.asset     —— **两处**：顶部 key 清单 + 下方 key→objPath 映射
  ④ tableResInfo.txt    —— 通常已由机器人随 gdconfig 提交自动补（配置引用了该 DK 就会补），
                            但机器人**只补清单不补 Display/Path**，所以「tableResInfo 有」≠「资源能用」。
                            本脚本会检查，缺了才补。

用法: python deploy_skin_specs.py <立绘png> <英雄卡png> <头像png> <英雄序号>
例:   python deploy_skin_specs.py Role_F_9_Skin01.png Role_C_9_Skin01.png Img_C_H_9_Skin01.png 9
     （英雄序号不带前导零：琥珀 1009 → 9，阿米娜 1020 → 20）
"""
import io, os, re, shutil, sys, uuid

WT = r'C:\x3-project\wt_circus_card\client'
DISPLAY = os.path.join(WT, r'Assets\Editor\Config\DisplayKey\Display_Role.asset')
PATH = os.path.join(WT, r'Assets\Res\Config\DisplayKey\Path_Role.asset')
RESINFO = os.path.join(WT, r'Assets\Editor\Config\tableResInfo.txt')

# (DK 后缀模板, 落库子目录, 期望尺寸)
SPECS = [
    ('Role_F_{n}_Skin01',    r'Assets/Res/UI/Spirits/Role/FullLength',            (1024, 1536)),
    ('Role_C_{n}_Skin01',    r'Assets/Res/UI/Spirits/Role/HeroCard',              (308, 420)),
    ('Img_C_H_{n}_Skin01',   r'Assets/Res/UI/Spirits/Role/Character Portraits',   (256, 256)),
]
# 锚点：插在阿米娜同类条目前，保持字母序附近即可（该表非严格排序，靠近同族便于人工查阅）
ANCHORS = ['Role_F_20_Skin01', 'Role_C_20_Skin01', 'Img_C_H_20_Skin01']


def read(p):
    with io.open(p, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write(p, t):
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(t)


def main(src_full, src_card, src_port, n):
    from PIL import Image
    srcs = [src_full, src_card, src_port]
    done = []
    for (tpl, subdir, size), src, anchor in zip(SPECS, srcs, ANCHORS):
        key = tpl.format(n=n)
        dk = 'DK_' + key
        fname = key + '.png'
        dst_dir = os.path.join(WT, subdir.replace('/', os.sep))
        dst = os.path.join(dst_dir, fname)

        im = Image.open(src)
        if im.size != size:
            raise SystemExit(f'!! {src} 尺寸 {im.size} != 期望 {size}')
        if im.mode != 'RGBA':
            raise SystemExit(f'!! {src} 不是 RGBA（规格图必须带透明）')

        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)

        # meta：照同目录锚点文件的 meta 改 guid
        anchor_meta = os.path.join(dst_dir, anchor + '.png.meta')
        guid = uuid.uuid4().hex
        if os.path.exists(anchor_meta):
            meta = re.sub(r'guid: [0-9a-f]{32}', f'guid: {guid}', read(anchor_meta), count=1)
        else:
            raise SystemExit(f'!! 找不到锚点 meta 模板: {anchor_meta}')
        write(dst + '.meta', meta)
        print(f'① {fname:<22} {im.size} RGBA  guid={guid[:12]}…')

        # ② Display_Role
        t = read(DISPLAY)
        if re.search(rf'^\s*- key: {re.escape(key)}\s*$', t, re.M):
            print(f'   ② Display 已存在 {key}，跳过')
        else:
            a = f'  - key: {anchor}'
            if a not in t:
                raise SystemExit(f'!! Display_Role 找不到锚点 {anchor}')
            entry = f'  - key: {key}\n    type: Role\n    desc: \n    guid: {guid}\n    exportCode: 0\n'
            write(DISPLAY, t.replace(a, entry + a, 1))
            print(f'   ② Display_Role  + {key}')

        # ③ Path_Role（清单 + 映射两处）
        t = read(PATH)
        if f'- {dk}\n' in t:
            print(f'   ③ Path 已存在 {dk}，跳过')
        else:
            a1 = f'    - DK_{anchor}'
            a2 = f'    - key: DK_{anchor}'
            for a in (a1, a2):
                if a not in t:
                    raise SystemExit(f'!! Path_Role 找不到锚点 {a}')
            t = t.replace(a1, f'    - {dk}\n{a1}', 1)
            t = t.replace(a2, f'    - key: {dk}\n      objPath: {subdir}/{fname}\n{a2}', 1)
            write(PATH, t)
            print(f'   ③ Path_Role     + {dk}（清单 + objPath 两处）')

        # ④ tableResInfo
        t = read(RESINFO)
        lines = t.split('\n')
        if dk in [x.strip() for x in lines]:
            print('   ④ tableResInfo 已有（机器人随配置自动补的），跳过')
        else:
            ai = next((i for i, x in enumerate(lines) if x.strip() == f'DK_{anchor}'), None)
            if ai is None:
                raise SystemExit('!! tableResInfo 找不到锚点')
            lines.insert(ai, dk)
            write(RESINFO, '\n'.join(lines))
            print(f'   ④ tableResInfo  + {dk}')
        done.append(dk)

    print('\n✅ 三件规格图落库 + DK 四处注册完成')
    print('   ' + ' / '.join(done))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main(*sys.argv[1:5])
