"""t2v 纯文字冒烟：验证 Seedance API 纯文本文生视频通不通 + 中性化文案过不过文本风控。
走用户流程（打轴叙述 + 成年人设锁 + 带货尾句 + 竖屏 9:16），不给任何参考图。
一次性脚本，成本=1 次 t2v 调用。"""
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# CLI 不自动读 .env，这里手动灌
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from core.config import load_config
from core.providers.volc import VolcProvider

cfg = load_config(ROOT / "config.yaml", require_key=True)
p = VolcProvider(cfg.ark)

# 16 号打轴叙述 → t2v prompt（成年锁 + 带货尾句），中性化：内衣不细化、明确成年
prompt = (
    "这是一个数字人带货视频，竖屏。"
    "场景：室内排球训练馆，蓝色场地、白色球网，后景有多人在训练打球。"
    "人物：两个梳麻花辫的成年女生，右边高个穿白色运动背心配粉色短裙，"
    "左边矮个穿白色运动背心配粉色运动短裤。"
    "分镜：开头两人背对镜头站在球网前看场内；随后右边高个女生转身面向镜头说"
    "「你那个肩带都露出来了」；中段她面对镜头说「我穿内衣都穿习惯了」，"
    "接着两人边走边聊，她指着旁边矮个女生说「她不穿内衣我可不习惯」；"
    "结尾镜头转到矮个女生，她面向镜头说「我穿的是吊带也能穿的」并拉了拉背心肩带位置，"
    "画面打出产品名「隐形内衣」。真人实拍质感，自然光，写实。"
)

body = {
    "model": cfg.ark.video_model,
    "content": [{"type": "text", "text": prompt}],   # 纯文本，无任何图
    "resolution": "720p",
    "ratio": "9:16",                                  # 显式竖屏（纯 t2v 无输入可跟随）
    "generate_audio": False,
    "watermark": False,
}

out = ROOT / "jobs" / "_smoke" / "smoke16_t2v.mp4"
out.parent.mkdir(parents=True, exist_ok=True)
t0 = time.time()
print(f"[smoke] 提交 t2v 纯文本任务 model={cfg.ark.video_model} ratio=9:16 720p ...")
try:
    p._submit_and_poll(body, out)
    print(f"[smoke] OK 出片 {out}  size={out.stat().st_size/1024/1024:.1f}MB  用时 {time.time()-t0:.0f}s")
except Exception as e:
    print(f"[smoke] FAIL: {type(e).__name__}: {e}")
    sys.exit(1)
