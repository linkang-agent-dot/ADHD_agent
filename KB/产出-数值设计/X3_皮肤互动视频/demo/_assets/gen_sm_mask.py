# -*- coding: utf-8 -*-
# 皮肤专属时刻 demo 热区遮罩 v2：按场景首帧图(sm_104001_scene.png 1152x2048)实际人物站位描区
# 颜色约定同 HeroClub：红=头 绿=身 蓝=手 黑=忽略；采样按归一化坐标，遮罩分辨率跟图一致即可
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from PIL import Image, ImageDraw
import os

W, H = 1152, 2048
img = Image.new('RGB', (W, H), (0, 0, 0))
d = ImageDraw.Draw(img)

# 身体（躯干：胸口→裙摆，含腰腹）
d.ellipse([420, 360, 810, 1010], fill=(0, 255, 0))
# 头（脸+刘海，含发顶）
d.ellipse([530, 70, 770, 380], fill=(255, 0, 0))
# 手：左手（持彩球）/ 右手（扶球），后画盖过绿区边缘
d.ellipse([290, 820, 510, 1080], fill=(0, 0, 255))
d.ellipse([700, 650, 900, 890], fill=(0, 0, 255))

# ★必须输出到 Club/images/mask/ 白名单目录：贴图后处理器只对该目录保留 isReadable，别的目录会被强制改 0（点击采样失效）
out = r'C:\x3-project\client\Assets\Res\UI\Spirits\Club\images\mask\SM_104001_mask.png'
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out)
print('mask v2 saved:', out, '(meta 不动，沿用已生成的 guid)')

