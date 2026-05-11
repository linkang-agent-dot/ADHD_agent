"""
DK 图片预处理工具
用法:
  python image_utils.py check <src_path> [target_w] [target_h]
  python image_utils.py resize <src_path> <dst_path> [size] [padding_ratio]
  python image_utils.py remove_bg <src_path> <dst_path> [size] [padding_ratio]

padding_ratio 按 DK 类型参考值:
  Icon(活动/道具) = 0.05  |  Icon(礼包/商店) = 0.03
  Head/Avatar = 0.07      |  IconBg = 0.04
  Portrait = 0.02         |  IconFront/IconMask = 0.02
  MinigameIcon/Guide = 0.05
"""
import sys
import os
import base64
import json
import urllib.request
import ssl
import io

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


def check_image(src_path, target_size=(256, 256)):
    img = Image.open(src_path)
    issues = []
    if img.mode != 'RGBA':
        issues.append(f"mode={img.mode}，无 alpha 通道")
    else:
        corners = [img.getpixel(p) for p in [
            (0, 0), (img.width-1, 0), (0, img.height-1), (img.width-1, img.height-1)
        ]]
        if all(c[3] == 255 for c in corners):
            issues.append("边角像素 alpha=255，可能是假透明（棋盘格截图）")
    if img.size != target_size:
        issues.append(f"尺寸 {img.size} 不符合要求 {target_size}")
    return issues


def resize_image(src_path, dst_path, size=(256, 256), padding_ratio=0.05):
    img = Image.open(src_path).convert('RGBA')
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    canvas_w, canvas_h = size
    pad = int(min(canvas_w, canvas_h) * padding_ratio)
    max_w = canvas_w - pad * 2
    max_h = canvas_h - pad * 2
    scale = min(max_w / img.width, max_h / img.height)
    new_w, new_h = int(img.width * scale), int(img.height * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    result = Image.new('RGBA', size, (0, 0, 0, 0))
    x = (canvas_w - new_w) // 2
    y = (canvas_h - new_h) // 2
    result.paste(resized, (x, y), resized)
    result.save(dst_path, 'PNG')
    print(f"✅ resize 完成: {dst_path}  size={result.size}")


def remove_bg_and_resize(src_path, dst_path, size=(256, 256), padding_ratio=0.05):
    config_path = r'c:\ADHD_agent\.cursor\skills\x2-media\config.json'
    config = json.load(open(config_path))
    cookie = config['grfal_cookie']

    with open(src_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(src_path)[1].lower().lstrip('.')
    data_uri = f"data:image/{ext};base64,{b64}"

    payload = json.dumps({
        "tool": "remove_background",
        "params": {"image_paths": [data_uri]}
    }).encode()
    req = urllib.request.Request(
        "https://grfal.tap4fun.com/api/mcp/call",
        data=payload,
        headers={"Content-Type": "application/json", "Cookie": cookie},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as resp:
        result = json.loads(resp.read())

    raw = result['result']
    url = raw[0][0] if isinstance(raw[0], list) else raw[0]
    dl_url = url.replace(url.split('/app/')[0], "http://172.20.90.45:6018") if '/app/' in url else url
    dl_req = urllib.request.Request(dl_url, headers={"Cookie": cookie})
    with urllib.request.urlopen(dl_req, timeout=30) as r:
        img_data = r.read()

    tmp_path = dst_path + ".bg_removed.png"
    with open(tmp_path, 'wb') as f:
        f.write(img_data)
    resize_image(tmp_path, dst_path, size, padding_ratio)
    os.remove(tmp_path)
    print(f"✅ 抠图+resize 完成: {dst_path}")


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    src = sys.argv[2] if len(sys.argv) > 2 else None
    dst = sys.argv[3] if len(sys.argv) > 3 else None

    if cmd == 'check':
        w = int(sys.argv[3]) if len(sys.argv) > 3 else 256
        h = int(sys.argv[4]) if len(sys.argv) > 4 else 256
        issues = check_image(src, (w, h))
        if issues:
            print("⚠️ 问题:", "; ".join(issues))
        else:
            print("✅ 图片检查通过")
    elif cmd == 'resize':
        size = int(sys.argv[4]) if len(sys.argv) > 4 else 256
        ratio = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
        resize_image(src, dst, (size, size), ratio)
    elif cmd == 'remove_bg':
        size = int(sys.argv[4]) if len(sys.argv) > 4 else 256
        ratio = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
        remove_bg_and_resize(src, dst, (size, size), ratio)
    else:
        print(__doc__)
