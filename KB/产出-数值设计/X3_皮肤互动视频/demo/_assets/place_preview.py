# -*- coding: utf-8 -*-
import io, sys, os, shutil, uuid
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = r'C:\ADHD_agent\KB\产出-数值设计\X3_皮肤互动视频\demo\_assets'
DST = r'C:\x3-project\client\Assets\Res\UI\Spirits\SkinMoment'
os.makedirs(DST, exist_ok=True)

# 抄一个现成 sprite meta 换 guid（普通 sprite，不需 readable）
tpl = r'C:\x3-project\client\Assets\Res\UI\Spirits\Club\images\mask\SM_104001_mask.png.meta'
with open(tpl, 'r', encoding='utf-8') as f:
    meta_tpl = f.read()

pairs = [
    ('sm_104001_scene.png',       'SM_104001_lockerroom_preview.png'),
    ('sm_104001_field_scene.png', 'SM_104001_field_preview.png'),
]
for src, dst in pairs:
    shutil.copy(os.path.join(SRC, src), os.path.join(DST, dst))
    old_guid = [l for l in meta_tpl.splitlines() if l.startswith('guid:')][0].split()[1]
    meta = meta_tpl.replace(old_guid, uuid.uuid4().hex).replace('isReadable: 1', 'isReadable: 0')
    with open(os.path.join(DST, dst + '.meta'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(meta)
    print('placed', dst)
