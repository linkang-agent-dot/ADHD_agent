import urllib.request
import os

grfal_url = "http://172.20.90.45:6018"
output_dir = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_48_FINAL"
output_filename = "Img_Player_AvatarFrame_WC_CPV.png"

results = [
    "/api/output/image_generation/2026-06-15/17815370190328_0_0.png",
    "/api/output/image_generation/2026-06-15/17815370058415_0_0.png"
]

os.makedirs(output_dir, exist_ok=True)

saved = []
for i, path in enumerate(results):
    url = grfal_url + path
    if i == 0:
        fname = output_filename
    else:
        base, ext = os.path.splitext(output_filename)
        fname = f"{base}_v{i+1}{ext}"
    out_path = os.path.join(output_dir, fname)
    urllib.request.urlretrieve(url, out_path)
    saved.append(out_path)
    with open("_download_d345.log", "a", encoding="utf-8") as f:
        f.write(f"Downloaded: {out_path}\n")

with open("_download_d345.log", "a", encoding="utf-8") as f:
    f.write("DONE\n")
