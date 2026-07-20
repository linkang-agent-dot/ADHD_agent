"""t2v 批量出片 runner：吃一个 prompts json（{_meta:{prefix}, clips:[{id,prompt}]}），
逐条纯文字文生视频 → 下载。断点续跑（out 已存在则跳过）+ 小并发。

用法：
  python scripts/batch_t2v.py --json prompts/t2v_E222.json --out E:/222/t2v_成片 --workers 3
  python scripts/batch_t2v.py ... --only 03,07   # 只跑指定 id
"""
import argparse
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from core.config import load_config
from core.providers.volc import VolcProvider

_progress_lock = threading.Lock()


def verify_clip(path: Path) -> dict:
    """出片后就地验证，返回真实事实指纹（magic number + size + 流）。脚本自己验，不靠人目测。"""
    info = {}
    try:
        b = path.read_bytes()
        info["bytes"] = len(b)
        info["magic_ok"] = len(b) >= 8 and b[4:8] == b"ftyp"  # mp4 前12字节偏移4-7=ftyp
    except Exception as e:
        info["read_err"] = str(e)[:100]
        info["magic_ok"] = False
        return info
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "stream=codec_type,codec_name:format=duration", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30)
        d = json.loads(r.stdout or "{}")
        streams = d.get("streams", [])
        info["vcodec"] = next((s.get("codec_name") for s in streams if s.get("codec_type") == "video"), None)
        info["acodec"] = next((s.get("codec_name") for s in streams if s.get("codec_type") == "audio"), None)
        dur = d.get("format", {}).get("duration")
        info["dur"] = round(float(dur), 2) if dur else None
    except Exception as e:
        info["probe_err"] = str(e)[:100]
    return info


def append_progress(out_dir: Path, rec: dict) -> None:
    """进度台账：真实事实指纹逐行 append，脚本写、只读不改。汇报进度只认此文件（_progress.jsonl）。"""
    rec = {**rec, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    with _progress_lock:
        with open(out_dir / "_progress.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def gen_one(p: VolcProvider, model: str, prefix: str, suffix: str,
            ref_images: list, clip: dict, out_dir: Path,
            suffix_hidden: str = "", gen_audio: bool = False) -> tuple:
    cid = clip["id"]
    # garment_mode: hidden=内衣藏在正常外衣里(用 suffix_hidden、不挂内衣参考图，防 Seedance 把内衣当外衣穿)
    #               reveal/缺省=直接展示内衣(用 suffix + 内衣参考图)
    mode = clip.get("garment_mode", "reveal")
    use_suffix = suffix_hidden if mode == "hidden" else suffix
    use_refs = [] if mode == "hidden" else ref_images
    # clip.extra 拼在 suffix 之后（后置=覆盖前述冲突项，如内衣主体色 09/11/15 覆盖为粉底肤色）
    full_prompt = prefix + clip["prompt"] + use_suffix + clip.get("extra", "")
    # prompt 留档：每条实际喂给 API 的完整 text 存一份，成片↔prompt 一一对应（不管出不出片都记录）
    pdir = out_dir / "prompts"
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / f"t2v_{cid}.txt").write_text(full_prompt, encoding="utf-8")
    out = out_dir / f"t2v_{cid}.mp4"
    if out.exists() and out.stat().st_size > 0:
        v = verify_clip(out)
        append_progress(out_dir, {"id": cid, "status": "skip", **v})
        return cid, "skip", f"已存在 magic={v.get('magic_ok')} {v.get('bytes',0)/1024/1024:.1f}MB"
    content = [{"type": "text", "text": full_prompt}]
    # 产品参考图（内衣平铺图，无人物→不触发输入风控）：统一内衣造型，参考图1=正面/2=背面
    for img in use_refs:
        content.append({"type": "image_url",
                        "image_url": {"url": p._data_url(img)},
                        "role": "reference_image"})
    body = {
        "model": model,
        "content": content,
        "resolution": "720p",
        "ratio": "9:16",
        "generate_audio": gen_audio,   # 不走插入音轨方向→False(不配语音);字幕靠 prompt 让 Seedance 烧
        "watermark": False,
    }
    if clip.get("dur"):
        body["duration"] = clip["dur"]   # 按原片时长（clamp 4-15s）
    t0 = time.time()
    try:
        p._submit_and_poll(body, out)
        v = verify_clip(out)
        append_progress(out_dir, {"id": cid, "status": "ok", "secs": round(time.time() - t0),
                                  "dur_expect": clip.get("dur"), **v})
        return cid, "ok", (f"magic={v.get('magic_ok')} {v.get('bytes',0)/1024/1024:.1f}MB "
                           f"{v.get('vcodec')}/{v.get('acodec')} {v.get('dur')}s {time.time()-t0:.0f}s")
    except Exception as e:
        append_progress(out_dir, {"id": cid, "status": "fail", "err": f"{type(e).__name__}: {str(e)[:200]}"})
        return cid, "fail", f"{type(e).__name__}: {str(e)[:200]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    meta = data.get("_meta", {})
    prefix = meta.get("prefix", "")
    suffix = meta.get("suffix", "")
    suffix_hidden = meta.get("suffix_hidden", "")   # garment_mode=hidden 用（内衣藏外衣里）
    gen_audio = bool(meta.get("generate_audio", False))   # 不走音轨方向→默认 False
    # ref_image 支持单张(str)或多张(list)：正面+背面
    raw_refs = meta.get("ref_image") or []
    if isinstance(raw_refs, str):
        raw_refs = [raw_refs]
    ref_images = []
    for r in raw_refs:
        rp = (Path(args.json).parent.parent / r).resolve()
        if rp.exists():
            ref_images.append(rp)
        else:
            print(f"[batch] ⚠️ 参考图不存在: {rp}", flush=True)
    clips = data["clips"]
    if args.only:
        want = {x.strip() for x in args.only.split(",")}
        clips = [c for c in clips if c["id"] in want]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_config(ROOT / "config.yaml", require_key=True)
    p = VolcProvider(cfg.ark)
    model = cfg.ark.video_model
    print(f"[batch] {len(clips)} 条 → {out_dir}  model={model}  并发={args.workers}"
          f"  ref图={len(ref_images)}张  audio={'生成' if gen_audio else '关(不配音轨)'}"
          f"  hidden模式={'有' if suffix_hidden else '无'}  duration=按json", flush=True)

    results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(gen_one, p, model, prefix, suffix, ref_images, c, out_dir,
                          suffix_hidden, gen_audio): c["id"]
                for c in clips}
        for fut in as_completed(futs):
            cid, status, msg = fut.result()
            results[cid] = status
            print(f"[batch] {cid}: {status}  {msg}", flush=True)

    ok = sum(1 for v in results.values() if v == "ok")
    sk = sum(1 for v in results.values() if v == "skip")
    fl = [k for k, v in results.items() if v == "fail"]
    print(f"[batch] 完成：成功 {ok} / 跳过 {sk} / 失败 {len(fl)}"
          + (f"  失败id={fl}" if fl else ""), flush=True)


if __name__ == "__main__":
    main()
