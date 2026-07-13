# -*- coding: utf-8 -*-
"""Step 1: per-video analysis (transcript + silence list). Resumable.

Usage: python analyze.py --base <产品根目录>
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

from common import parse_base, paths, run, load_model

SILENCE_DB = "-32dB"
SILENCE_MIN = 0.25


def detect_silences(ffmpeg, mp4):
    p = subprocess.run([str(ffmpeg), "-i", str(mp4), "-af",
                        f"silencedetect=noise={SILENCE_DB}:d={SILENCE_MIN}", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    out, start = [], None
    for line in p.stderr.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m:
            start = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", line)
        if m and start is not None:
            e, d = float(m.group(1)), float(m.group(2))
            out.append({"start": start, "end": e, "dur": d, "mid": round((start + e) / 2, 3)})
            start = None
    return out


def main():
    base, _ = parse_base(__doc__)
    P = paths(base)
    P["analysis"].mkdir(parents=True, exist_ok=True)
    model = load_model()
    videos = [v for v in sorted(P["src"].glob("*.mp4")) if "###" not in v.name]
    print(f"{len(videos)} videos")
    for mp4 in videos:
        if (P["analysis"] / f"{mp4.stem}.json").exists():
            continue
        print(f"== {mp4.name}")
        with tempfile.TemporaryDirectory() as td:
            wav = Path(td) / "a.wav"
            run([P["ffmpeg"], "-y", "-i", mp4, "-vn", "-ac", "1", "-ar", "16000",
                 "-c:a", "pcm_s16le", wav])
            segments, _info = model.transcribe(
                str(wav), language="zh", word_timestamps=True, vad_filter=False,
                initial_prompt="口播带货视频，简体中文。")
            segs = [{"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(),
                     "words": [{"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3)}
                               for w in (s.words or [])]} for s in segments]
        silences = detect_silences(P["ffmpeg"], mp4)
        (P["analysis"] / f"{mp4.stem}.json").write_text(
            json.dumps({"video": mp4.name, "segments": segs, "silences": silences},
                       ensure_ascii=False, indent=1), encoding="utf-8")
        lines = [(s["start"], f"[{s['start']:7.2f} - {s['end']:7.2f}] {s['text']}") for s in segs]
        lines += [(g["start"], f"[{g['start']:7.2f} - {g['end']:7.2f}] ~~~~ 静音 {g['dur']:.2f}s")
                  for g in silences]
        lines.sort(key=lambda x: x[0])
        (P["analysis"] / f"{mp4.stem}.txt").write_text(
            "\n".join(t for _, t in lines), encoding="utf-8")
        print(f"   {len(segs)} segments, {len(silences)} silences")
    print("done")


if __name__ == "__main__":
    main()
