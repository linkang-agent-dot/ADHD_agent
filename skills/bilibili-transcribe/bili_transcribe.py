# -*- coding: utf-8 -*-
"""B站视频批量转写: BV -> metadata -> html5 playurl -> download -> ffmpeg wav -> faster-whisper transcript.

用法: python -X utf8 bili_transcribe.py BV1xxx BV2yyy ...
      转写文本输出到当前目录 transcript_<BV>.txt(已存在自动跳过, 失败可重跑续传)
依赖: ffmpeg 在 PATH; faster-whisper 已装且本地缓存 small 模型(本机HF不通,必须 local_files_only)
详见 memory: reference_bilibili_video_analysis.md
"""
import urllib.request, urllib.parse, json, subprocess, os, sys, datetime, traceback

BVIDS = sys.argv[1:]
if not BVIDS:
    print("usage: python -X utf8 bili_transcribe.py <BV> [BV...]"); sys.exit(1)

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
H = {"User-Agent": UA, "Referer": "https://www.bilibili.com/"}
OUT = os.getcwd()

def get(url):
    import time
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers=H)
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if i == 3: raise
            time.sleep(5 * (i + 1))

def dl(url, path):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk: break
            f.write(chunk)

from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True)

for bv in BVIDS:
    tpath = os.path.join(OUT, f"transcript_{bv}.txt")
    if os.path.exists(tpath):
        print(bv, "already done", flush=True); continue
    try:
        v = get(f"https://api.bilibili.com/x/web-interface/view?bvid={bv}")["data"]
        cid, title, dur = v["cid"], v["title"], v["duration"]
        desc = v.get("desc", "")
        pub = datetime.datetime.fromtimestamp(v["pubdate"]).strftime("%Y-%m-%d")
        stat = v["stat"]
        p = get(f"https://api.bilibili.com/x/player/playurl?bvid={bv}&cid={cid}&platform=html5&high_quality=1&qn=16")
        if p["code"] != 0:
            print(bv, "playurl fail", p.get("message"), flush=True); continue
        mp4 = os.path.join(OUT, f"{bv}.mp4"); wav = os.path.join(OUT, f"{bv}.wav")
        parts = p["data"]["durl"]
        if len(parts) == 1:
            dl(parts[0]["url"], mp4)
        else:  # 长视频可能分多段，全下再 concat
            names = []
            for i, seg in enumerate(parts):
                pn = os.path.join(OUT, f"{bv}_part{i}.mp4"); dl(seg["url"], pn); names.append(pn)
            lst = os.path.join(OUT, f"{bv}_list.txt")
            open(lst, "w").write("\n".join("file '%s'" % n.replace("\\", "/") for n in names))
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", mp4], capture_output=True)
            for n in names: os.remove(n)
            os.remove(lst)
        subprocess.run(["ffmpeg", "-y", "-i", mp4, "-vn", "-ar", "16000", "-ac", "1", wav],
                       capture_output=True)
        segs, _ = model.transcribe(wav, language="zh", beam_size=5)
        lines = [f"# {title}", f"# {bv} | {pub} | {dur}s | play={stat['view']} like={stat['like']} fav={stat['favorite']}",
                 f"# desc: {desc[:500]}", ""]
        for s in segs:
            lines.append(f"[{int(s.start)//60:02d}:{int(s.start)%60:02d}] {s.text.strip()}")
        with open(tpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        os.remove(mp4); os.remove(wav)
        print(bv, "OK", len(lines)-4, "segs |", title[:40], flush=True)
    except Exception:
        print(bv, "ERROR", flush=True)
        traceback.print_exc()
print("ALL DONE", flush=True)
