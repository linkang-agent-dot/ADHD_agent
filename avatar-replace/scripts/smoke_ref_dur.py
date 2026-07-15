"""冒烟：验证 t2v + 内衣产品参考图(reference_image) + duration 三者能不能一起用。
测两个未知前提：① mini t2v 接不接受 duration 参数（i2v mini 不接受，t2v 待验）；
② 内衣平铺产品图作 reference_image 会不会触发输入风控 + 造型能否带上。
用 07 羽毛球（原片 12.7s）测 duration=13。"""
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from core.config import load_config
from core.providers.volc import VolcProvider

cfg = load_config(ROOT / "config.yaml", require_key=True)
p = VolcProvider(cfg.ark)
bra_front = ROOT / "refs" / "product_bra_front.png"   # 正面
bra_back = ROOT / "refs" / "product_bra_back.png"     # 后背

# 台词版 prompt：台词驱动语音+口型（generate_audio），画面不烧字幕（解决字幕重复）
prompt = (
    "这是一个数字人带货视频，竖屏 9:16，真人实拍质感、自然光，出镜均为女性。"
    "画面中不出现任何字幕、标题或贴片文字，人物自然开口说话、配同步中文语音。"
    "场景：室内羽毛球馆（蓝色场地、羽毛球网、后景多人打球）。"
    "人物：两个女生各持羽毛球拍，均梳麻花辫，右边配粉色发绳；"
    "左边白色运动背心配白色运动短裤，右边白色运动背心配粉色运动短裤。"
    "分镜与台词：开头右边女生转向镜头说「哎同学，你们现在都不穿内衣的吗」；"
    "两人并排对话，另一女生说「我们穿了呀，我们穿的是吊带也能穿的」；"
    "结尾镜头推近右边女生，她说「冰冰凉凉的可舒服了，还是粉底液的颜色，不用担心会有内衣痕迹哦」。"
    "内衣款式统一为参考图那款细肩带背心式无痕内衣（可调节细肩带带金属调节扣、V型压纹罩杯、透气网面、米白色）；"
    "参考图1为该内衣正面款式、参考图2为背面款式，正反造型都以参考图为准。"
)

def body(dur, with_ref):
    content = [{"type": "text", "text": prompt}]
    if with_ref:
        for img in (bra_front, bra_back):   # 参考图1=正面, 参考图2=背面
            content.append({"type": "image_url",
                            "image_url": {"url": p._data_url(img)},
                            "role": "reference_image"})
    b = {"model": cfg.ark.video_model, "content": content,
         "resolution": "720p", "ratio": "9:16",
         "generate_audio": True, "watermark": False}   # 方案B：Seedance 生成语音
    if dur:
        b["duration"] = dur
    return b

out = ROOT / "jobs" / "_smoke" / "smoke07_audio.mp4"
out.parent.mkdir(parents=True, exist_ok=True)
t0 = time.time()
print("[smoke] 测 t2v + 内衣参考图 + duration=13 ...")
try:
    p._submit_and_poll(body(13, True), out)
    print(f"[smoke] OK {out} {out.stat().st_size/1024/1024:.1f}MB {time.time()-t0:.0f}s")
except Exception as e:
    print(f"[smoke] FAIL(带duration+ref): {type(e).__name__}: {str(e)[:300]}")
    # 若 duration 被拒，退一步测「只加参考图、不传 duration」判断是哪个环节的问题
    print("[smoke] 回退测：只加参考图、不传 duration ...")
    try:
        p._submit_and_poll(body(None, True), out)
        print(f"[smoke] 参考图 OK（是 duration 被拒）{out} {out.stat().st_size/1024/1024:.1f}MB")
    except Exception as e2:
        print(f"[smoke] FAIL(仅ref): {type(e2).__name__}: {str(e2)[:300]}")
