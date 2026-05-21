"""
X2 通用节庆 Banner 生成脚本
用法: python generate_banner.py --name 掉落活动 --width 1640 --height 1240 --prompt "额外描述"
"""
import argparse, json, urllib.request, ssl, os, sys
from datetime import datetime

CONFIG_PATH = r"C:\ADHD_agent\.cursor\skills\x2-media\config.json"
OUTPUT_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\X2\Banner"
API_URL = "https://grfal.tap4fun.com/api/call"

# 预设 prompt 模板，按用途区分
PRESETS = {
    "每日礼包": "town square party celebration, crowd silhouettes dancing, colorful bunting flags and paper lanterns floating upward, confetti and sparkle particles",
    "抢购礼包": "bustling night market party, treasure chests and gift crates on display, dramatic warm spotlight beams, colorful banner flags and streamers, crowd silhouettes shopping",
    "强消耗": "overhead view of town plaza party, central fountain surrounded by celebrating crowd silhouettes, sky lanterns rising, symmetric composition",
    "7日活动": "wide panoramic town celebration, fireworks bursting above skyline, colorful streamers and ribbons flying, confetti particles floating",
    "掉落活动": "elevated view of town courtyard celebration, central stage or decorative centerpiece glowing warmly, crowd gathered around, festive lights and banners, slightly overhead angle",
    "累充": "heroic character silhouette centered, dramatic warm backlight glow, festive sparkles and particles around",
    "BP基金": "grand hall entrance with warm light spilling out, festive decorations on pillars, inviting atmosphere",
    "Gacha": "magical carnival machine or wheel glowing at center, festive booth decorations around, exciting atmosphere",
}

BASE_PROMPT = (
    "Steampunk fantasy game art, warm golden hour sunset sky with orange pink purple gradient, "
    "festive joyful party atmosphere, stylized 3D rendered, soft dreamy lighting, atmospheric haze, "
    "no text no words no signs no letters, game UI banner background, "
)

def generate(name, width, height, extra_prompt="", model="gemini"):
    config = json.load(open(CONFIG_PATH, encoding="utf-8"))
    cookie = config["grfal_cookie"]

    # 组装 prompt
    preset = PRESETS.get(name, "festive celebration scene, warm joyful atmosphere")
    prompt = BASE_PROMPT + preset
    if extra_prompt:
        prompt += ", " + extra_prompt

    # 根据比例补充构图指令
    ratio = height / width
    if ratio > 1.5:
        prompt += ", upper 60 percent is clean gradient sky for UI overlay, scene at bottom"
    elif ratio > 1.0:
        prompt += ", upper portion has clean sky area for UI overlay"
    else:
        prompt += ", upper half is clean sky area for UI overlay, scene at bottom half"

    params = {
        "tool": "generate_image",
        "params": {"prompt": prompt, "model": model, "width": width, "height": height}
    }

    print(f"[生成] {name} ({width}x{height}) model={model}")
    print(f"[Prompt] {prompt[:120]}...")

    ctx = ssl.create_default_context()
    payload = json.dumps(params).encode()
    req = urllib.request.Request(
        API_URL, data=payload,
        headers={"Content-Type": "application/json", "Cookie": cookie},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
        result = json.loads(resp.read())

    if not result.get("success"):
        print(f"[失败] {result}")
        sys.exit(1)

    urls = result["result"]
    print(f"[成功] 返回 {len(urls)} 张候选")

    # 下载第一张
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"v3_{name}_{width}x{height}.png"
    save_path = os.path.join(OUTPUT_DIR, fname)

    dl_url = API_URL.rsplit("/api/call", 1)[0] + urls[0]
    req = urllib.request.Request(dl_url, headers={"Cookie": cookie})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        data = r.read()
    with open(save_path, "wb") as f:
        f.write(data)

    print(f"[保存] {save_path} ({len(data)//1024}KB)")
    return save_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="X2 通用节庆 Banner 生成")
    parser.add_argument("--name", required=True, help="Banner 用途名（每日礼包/抢购礼包/强消耗/掉落活动/...）")
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--prompt", default="", help="额外 prompt 补充")
    parser.add_argument("--model", default="gemini")
    args = parser.parse_args()
    generate(args.name, args.width, args.height, args.prompt, args.model)
