#!/usr/bin/env python3
"""生成技能图标构图参考图 template_256x256_circle.png。

256×256 圆形技能图标，**贴边设计**：透明底 + 圆边贴画布四边（半径 128）、内容贴满圆，
供生图时作为 reference_images 第一张传入，让模型产出贴边设计。
"""
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("需要 Pillow: pip install Pillow", file=sys.stderr)
    sys.exit(1)

OUTPUT_DIR = Path(__file__).resolve().parent
TARGET_SIZE = 256
CENTER = TARGET_SIZE // 2
# 贴边设计：外圆贴画布边，内容区贴满圆，无留白
OUTER_RADIUS = TARGET_SIZE // 2  # 128，圆边贴画布四边
INNER_RADIUS = OUTER_RADIUS - 2  # 内容区紧贴外圆内侧（仅 2px 线宽）
FILL_COLOR = (180, 180, 180, 70)  # 圆内填充（半透明灰），让模型看到「内容贴满圆边」
BOUNDARY_COLOR = (200, 200, 200, 200)  # 圆形边界线（浅灰）
SAFE_COLOR = (150, 150, 150, 120)  # 内圆线（内容贴此圆边）


def main():
    # 透明底
    img = Image.new("RGBA", (TARGET_SIZE, TARGET_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 外圆：实心填充贴边（半径 128 贴画布边），让模型明确看到「内容贴满边」
    bbox_outer = [
        CENTER - OUTER_RADIUS, CENTER - OUTER_RADIUS,
        CENTER + OUTER_RADIUS, CENTER + OUTER_RADIUS
    ]
    draw.ellipse(bbox_outer, fill=FILL_COLOR, outline=BOUNDARY_COLOR, width=2)
    
    # 内圆（内容贴此圆边，无留白）
    bbox_inner = [
        CENTER - INNER_RADIUS, CENTER - INNER_RADIUS,
        CENTER + INNER_RADIUS, CENTER + INNER_RADIUS
    ]
    draw.ellipse(bbox_inner, outline=SAFE_COLOR, width=1)
    
    out_path = OUTPUT_DIR / "template_256x256_circle.png"
    img.save(out_path)
    print(f"已生成: {out_path} ({TARGET_SIZE}×{TARGET_SIZE}, 贴边设计: 外圆半径 {OUTER_RADIUS}px 贴画布边)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
