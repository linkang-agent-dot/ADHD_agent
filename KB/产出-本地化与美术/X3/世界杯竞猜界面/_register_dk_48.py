# -*- coding: utf-8 -*-
import os, glob, re, shutil, uuid
from PIL import Image

SRC = r'C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_48_FINAL'
DST = r'C:\x3-project\client\Assets\Res\UI\Spirits\Personalise\AvatarFrame'
META_TMPL = os.path.join(DST, 'Img_Player_AvatarFrame_kvk.png.meta')
PATH_ASSET = r'C:\x3-project\client\Assets\Res\Config\DisplayKey\Path_Personalise.asset'

# 1. 收集48规范名图
codes = sorted(set(re.search(r'WC_([A-Z]{3})\.png$', os.path.basename(f)).group(1)
                   for f in glob.glob(os.path.join(SRC, 'Img_Player_AvatarFrame_WC_*.png'))
                   if re.search(r'WC_[A-Z]{3}\.png$', os.path.basename(f))))
print('队数', len(codes))

# 2. 降256 + 拷贝
for c in codes:
    src = os.path.join(SRC, f'Img_Player_AvatarFrame_WC_{c}.png')
    dst = os.path.join(DST, f'Img_Player_AvatarFrame_WC_{c}.png')
    im = Image.open(src).convert('RGBA')
    if im.size != (256, 256):
        im = im.resize((256, 256), Image.LANCZOS)
    im.save(dst)
print('已降256+拷贝', len(codes), '张 ->', DST)

# 3. 生成meta (抄kvk模板,换guid+spriteID)
tmpl = open(META_TMPL, encoding='utf-8').read()
for c in codes:
    g = uuid.uuid4().hex
    sid = uuid.uuid4().hex
    m = re.sub(r'guid: [0-9a-f]{32}', f'guid: {g}', tmpl, count=1)
    m = re.sub(r'spriteID: [0-9a-f]{32}', f'spriteID: {sid}', m, count=1)
    open(os.path.join(DST, f'Img_Player_AvatarFrame_WC_{c}.png.meta'), 'w', encoding='utf-8').write(m)
print('已生成meta', len(codes))

# 4. 注册Path_Personalise.asset
shutil.copy(PATH_ASSET, PATH_ASSET + '.bak_wc48')
lines = open(PATH_ASSET, encoding='utf-8').read().split('\n')
vi = next(i for i, l in enumerate(lines) if l.strip() == 'values:')

new_keys = [f'    - DK_Img_Player_AvatarFrame_WC_{c}' for c in codes]
new_vals = []
for c in codes:
    new_vals.append(f'    - key: DK_Img_Player_AvatarFrame_WC_{c}')
    new_vals.append(f'      objPath: Assets/Res/UI/Spirits/Personalise/AvatarFrame/Img_Player_AvatarFrame_WC_{c}.png')

# keys段: 在 values: 行前插; values段: EOF前接
out = lines[:vi] + new_keys + lines[vi:]
while out and out[-1].strip() == '':
    out.pop()
out.extend(new_vals)
open(PATH_ASSET, 'w', encoding='utf-8', newline='').write('\n'.join(out) + '\n')

# 5. 校验 keys==values key 平行一致
chk = open(PATH_ASSET, encoding='utf-8').read().split('\n')
vi2 = next(i for i, l in enumerate(chk) if l.strip() == 'values:')
keys_list = [l.strip()[2:] for l in chk[:vi2] if l.strip().startswith('- DK_')]
vkeys = [l.strip()[len('- key: '):] for l in chk[vi2:] if l.strip().startswith('- key:')]
wc_keys = [k for k in keys_list if 'WC_' in k]
wc_vkeys = [k for k in vkeys if 'WC_' in k]
print('注册WC keys', len(wc_keys), '| WC values', len(wc_vkeys), '| 全表平行一致:', keys_list == vkeys)
