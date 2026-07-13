# -*- coding: utf-8 -*-
# 生成圆选择器用的方形上半身缩略图（脸+胸,正方形,放进圆里好看）+ 落客户端 + meta
import io, sys, os, uuid
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from PIL import Image

A = r'C:\ADHD_agent\KB\产出-数值设计\X3_皮肤互动视频\demo\_assets'
DST = r'C:\x3-project\client\Assets\Res\UI\Spirits\SkinMoment'
os.makedirs(DST, exist_ok=True)

# 抄现成 preview meta 换 guid（普通 sprite）
tpl_meta = os.path.join(DST, 'SM_104001_lockerroom_preview.png.meta')
with open(tpl_meta, 'r', encoding='utf-8') as f:
    meta_tpl = f.read()

pairs = [
    ('sm_104001_scene.png',       'SM_104001_lockerroom_thumb.png'),
    ('sm_104001_field_scene.png', 'SM_104001_field_thumb.png'),
]
for src, dst in pairs:
    im = Image.open(os.path.join(A, src)).convert('RGBA')
    W, Hh = im.size  # 1152x2048
    # 脸+胸区域方形裁切：人物居中，脸约在高度 8%~，取 x 居中 620 宽、y 从 5% 起 620 高
    s = 640
    cx = W // 2
    x0 = cx - s // 2
    y0 = int(Hh * 0.05)
    crop = im.crop((x0, y0, x0 + s, y0 + s)).resize((256, 256), Image.LANCZOS)
    crop.save(os.path.join(DST, dst))
    old_guid = [l for l in meta_tpl.splitlines() if l.startswith('guid:')][0].split()[1]
    meta = meta_tpl.replace(old_guid, uuid.uuid4().hex)
    with open(os.path.join(DST, dst + '.meta'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(meta)
    print('thumb:', dst)
