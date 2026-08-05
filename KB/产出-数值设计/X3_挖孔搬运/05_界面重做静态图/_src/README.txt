11 屏静态图的出图源（可重跑，不依赖 scratchpad）

跑法（在本目录）：
  1) python prepare_data_and_assets.py   # 从 demo v02 只读抽 D5.json + assets\（80+52 张图素）
  2) python gen.py                       # 生成 12 个 1080×1920 静态 HTML
  3) powershell -File shot.ps1           # headless Chrome 1:1 截图，覆盖写上一级的 PNG

注意：
- gen.py 读 ..\D5.json，assets 相对路径 = 本目录 assets\；shot.ps1 里 $out 指向上一级目录。
- 九宫格切片值来自 sprite 同名 .png.meta 的 spriteBorder{x左,y下,z右,w上} → CSS「上 右 下 左」。
- 全程只读 03_横转竖demo\，不写不改。
