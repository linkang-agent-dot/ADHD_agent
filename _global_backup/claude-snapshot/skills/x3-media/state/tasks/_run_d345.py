import subprocess
import sys
import json
import os

params = {
    "model": "gpt",
    "prompt": "X3 game circular avatar frame, World Cup / soccer theme, Cape Verde. Use reference image 1 as the EXACT target paradigm (a detailed team-color ring with gradient, metallic sheen and engraved texture, plus a flag-textured soccer ball at bottom-center) and reference image 2 for the skeleton/ornaments (top gold crest with gem, side gold diamond clips, bottom gold wings). RING band = royal blue team color, but NOT flat: give it a smooth light-to-dark gradient, subtle metallic sheen and rim light, and fine engraved geometric texture so it reads as an ornate metal-and-enamel frame (match reference image 1 ring quality). Slim gold edge trim. Bottom-center soccer ball = CAPE VERDE flag: blue with white-red stripes and ring of yellow stars, simplified. Keep cel-shaded glossy highlight on top of the ball so it reads as a real ball, not a flat 2D disc. The flag-ball is the single identity focus; national identity must be instantly recognizable. Keep the EXACT same skeleton, layout, proportions and ornaments and clean cel-shaded X3 game-UI art style. Square 1:1, circular hollow center fully transparent for avatar, fully transparent background, NO text, NO national flag cloth draped over the frame, NO scene background, readable at 256x256. ONE SINGLE avatar frame, do NOT generate multiple frames or a grid.",
    "aspect_ratio": "1:1",
    "output_format": "png"
}

call_grfal = r"C:\Users\linkang\.claude\skills\grfal-api\scripts\call_grfal.py"
ref1 = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_国旗球_环纹理试点\Img_Player_AvatarFrame_WC_JPN.png"
ref2 = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_X3风格试点\Img_Player_AvatarFrame_WC_France_mid_v2_alt1.png"

cmd = [
    sys.executable, call_grfal,
    "--tool", "generate_image",
    "--params", json.dumps(params),
    "--file", f"reference_images={ref1}",
    "--file", f"reference_images={ref2}",
    "--url", "http://172.20.90.45:6018",
    "--public-url", "none",
    "--timeout", "1200",
]

result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr, file=sys.stderr)
sys.exit(result.returncode)
