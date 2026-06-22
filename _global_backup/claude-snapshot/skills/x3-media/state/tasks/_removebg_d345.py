import subprocess
import sys
import json
import urllib.request
import os

call_grfal = r"C:\Users\linkang\.claude\skills\grfal-api\scripts\call_grfal.py"
grfal_url = "http://172.20.90.45:6018"
output_dir = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\头像框_48_FINAL"
input_file = os.path.join(output_dir, "Img_Player_AvatarFrame_WC_CPV.png")

cmd = [
    sys.executable, call_grfal,
    "--tool", "remove_background",
    "--file", f"image_paths={input_file}",
    "--url", grfal_url,
    "--public-url", "none",
    "--timeout", "180",
]
result = subprocess.run(cmd, capture_output=True)
stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""

with open("_removebg_d345.log", "w", encoding="utf-8") as f:
    f.write(f"rc={result.returncode}\n")
    f.write(stdout + "\n")
    if stderr:
        f.write("STDERR: " + stderr + "\n")

try:
    data = json.loads(stdout)
    if data.get("success") is True and data.get("result"):
        results = data["result"]
        if isinstance(results, list):
            url_path = results[0]
        else:
            url_path = results
        url = grfal_url + url_path if url_path.startswith("/") else url_path
        out_path = os.path.join(output_dir, "Img_Player_AvatarFrame_WC_CPV_nobg.png")
        urllib.request.urlretrieve(url, out_path)
        with open("_removebg_d345.log", "a", encoding="utf-8") as f:
            f.write(f"Saved: {out_path}\n")
    else:
        with open("_removebg_d345.log", "a", encoding="utf-8") as f:
            f.write("remove_background failed or no result\n")
except Exception as e:
    with open("_removebg_d345.log", "a", encoding="utf-8") as f:
        f.write(f"Error: {e}\n")
