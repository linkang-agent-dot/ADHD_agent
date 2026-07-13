# -*- coding: utf-8 -*-
"""Steps 4-5: anchored cut-point refinement + frame-accurate cutting.

Usage:
  python cut.py plan --base <产品根目录>   # 精调切点，人工核对"前词┃后词"后再 cut
  python cut.py cut  --base <产品根目录>   # 切割 + 边界预览 + 台账(保留旧 used_in)

Reads <base>/pipeline/boundaries.json (see SKILL.md for format).
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

from common import parse_base, paths, run, norm, load_model

FPS = 30
ENC_V = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p"]
ENC_A = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"]


def probe_dur(P, mp4):
    p = run([P["ffprobe"], "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", mp4])
    return float(p.stdout.strip())


def window_words(P, model, mp4, hint, half=6.0):
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "w.wav"
        t0 = max(0.0, hint - half)
        run([P["ffmpeg"], "-y", "-ss", f"{t0:.3f}", "-to", f"{hint + half:.3f}",
             "-i", mp4, "-vn", "-ac", "1", "-ar", "16000", wav])
        segs, _ = model.transcribe(str(wav), language="zh", word_timestamps=True,
                                   vad_filter=False, initial_prompt="口播带货视频，简体中文。")
        return [{"w": w.word, "s": round(w.start + t0, 3), "e": round(w.end + t0, 3)}
                for s in segs for w in (s.words or [])]


def acoustic_gap(P, mp4, t):
    """Real speech pause via cascaded silencedetect (whisper words are glued)."""
    for db in ("-25dB", "-30dB", "-35dB"):
        p = subprocess.run(
            [str(P["ffmpeg"]), "-ss", f"{max(0, t - 0.8):.3f}", "-to", f"{t + 0.8:.3f}",
             "-i", str(mp4), "-af", f"silencedetect=noise={db}:d=0.06", "-f", "null", "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        hits, start = [], None
        for line in p.stderr.splitlines():
            m = re.search(r"silence_start: ([\d.]+)", line)
            if m:
                start = float(m.group(1)) + max(0, t - 0.8)
            m = re.search(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", line)
            if m and start is not None:
                e = float(m.group(1)) + max(0, t - 0.8)
                hits.append((round((start + e) / 2, 3), round(e - start, 3)))
                start = None
        if start is not None:
            hits.append((round((start + t + 0.8) / 2, 3), round(t + 0.8 - start, 3)))
        if hits:
            return min(hits, key=lambda h: abs(h[0] - t))
    return None


def refine(P, model, mp4, hint, after):
    """Anchor the NEXT segment's opening words; never slide to other gaps —
    a cut belongs to its sentence boundary or it is LOW (standard v1.2)."""
    words = window_words(P, model, mp4, hint)
    idx = None
    for i in range(1, len(words)):
        if norm("".join(w["w"] for w in words[i:i + 3])).startswith(norm(after)):
            idx = i
            break
    if idx is None:  # ASR missed the zone (BGM) -> full-transcript hint + acoustic
        ac = acoustic_gap(P, mp4, hint)
        if ac and abs(ac[0] - hint) <= 0.45:
            return {"cut": round(round(ac[0] * FPS) / FPS, 3), "gap": ac[1],
                    "conf": "LOW-fallback-acoustic", "before": "?", "after": after}
        return {"cut": hint, "gap": 0.0, "conf": "LOW-anchor-not-found",
                "before": "?", "after": after,
                "ctx": norm("".join(w["w"] for w in words))}
    prev, nxt = words[idx - 1], words[idx]
    t_b = (prev["e"] + nxt["s"]) / 2
    ac = acoustic_gap(P, mp4, t_b)
    t_cut, gap = (ac if ac and abs(ac[0] - t_b) <= 0.45
                  else (t_b, round(nxt["s"] - prev["e"], 3)))
    conf = "HIGH" if gap >= 0.30 else ("MID" if gap >= 0.12 else "LOW-ear-check")
    return {"cut": round(round(t_cut * FPS) / FPS, 3), "gap": gap, "conf": conf,
            "before": prev["w"], "after": nxt["w"]}


def plan(P):
    sources = json.loads((P["pipeline"] / "boundaries.json").read_text(encoding="utf-8"))
    model = load_model()
    plans = []
    for s in sources:
        mp4 = P["src"] / s["file"]
        dur = probe_dur(P, mp4)
        rec = {"file": s["file"], "dur": dur, "hooks": s.get("hooks", 1)}
        for k in ("cut1", "cut2"):
            rec[k] = {**refine(P, model, mp4, s[k]["hint"], s[k]["after"]),
                      "note": s[k].get("note", "")}
        plans.append(rec)
        print(f"== {s['file']} ({dur:.2f}s)")
        for k in ("cut1", "cut2"):
            c = rec[k]
            print(f"  {k}: {c['cut']}s gap={c['gap']} [{c['conf']}] "
                  f"…{c['before']} ┃ {c['after']}…  ({c['note']})")
    (P["analysis"] / "cut_plan.json").write_text(
        json.dumps(plans, ensure_ascii=False, indent=1), encoding="utf-8")
    print("plan saved. 人工核对每行『前词┃后词』与预期句边界一致后再执行 cut。")


def cut_segment(P, mp4, start, end, dest):
    dur = round(end - start, 3)
    nframes = round(dur * FPS)  # exact frame count -> zero overlap
    af = f"afade=t=in:st=0:d=0.03,afade=t=out:st={max(0.0, dur - 0.03):.3f}:d=0.03"
    vf = "fps=30,scale=1080:1920:flags=lanczos,setsar=1"
    run([P["ffmpeg"], "-y", "-ss", f"{start:.3f}", "-i", mp4, "-t", f"{dur:.3f}",
         "-vf", vf, "-frames:v", str(nframes), "-af", af, *ENC_V, *ENC_A, dest])


def cut(P):
    plans = json.loads((P["analysis"] / "cut_plan.json").read_text(encoding="utf-8"))
    for d in ("A", "B", "C", "边界预览"):
        (P["lib"] / d).mkdir(parents=True, exist_ok=True)
    ledger_path = P["lib"] / "ledger.json"
    old_used = {}
    if ledger_path.exists():  # preserve remix history across recuts
        for e in json.loads(ledger_path.read_text(encoding="utf-8")):
            if e.get("used_in"):
                old_used[e["file"]] = e["used_in"]
    ledger = []
    for p in plans:
        mp4 = P["src"] / p["file"]
        stem = Path(p["file"]).stem
        c1, c2, dur = p["cut1"]["cut"], p["cut2"]["cut"], p["dur"]
        for seg, (t0, t1) in {"A": (0.0, c1), "B": (c1, c2), "C": (c2, dur)}.items():
            f0, f1 = round(t0 * FPS), round(t1 * FPS)
            dest = P["lib"] / seg / f"{stem}__{seg}__f{f0}-f{f1}.mp4"
            if not dest.exists():
                print(f"cut {seg} {t0}-{t1} -> {dest.name}")
                cut_segment(P, mp4, t0, t1, dest)
            ledger.append({
                "segment": seg, "source": p["file"], "start": t0, "end": t1,
                "frames": [f0, f1], "file": f"{seg}/{dest.name}",
                "hook_units": p["hooks"] if seg == "A" else None,
                "cut_confidence": {"A": p["cut1"]["conf"],
                                   "B": f"{p['cut1']['conf']}/{p['cut2']['conf']}",
                                   "C": p["cut2"]["conf"]}[seg],
                "review": "pending", "used_in": old_used.get(f"{seg}/{dest.name}", []),
            })
        for k, label in (("cut1", "切点1_A尾接B头"), ("cut2", "切点2_B尾接C头")):
            c = p[k]["cut"]
            prev = P["lib"] / "边界预览" / f"{stem}__{label}_{c}s.mp4"
            if not prev.exists():
                cut_segment(P, mp4, max(0, c - 1.5), min(dur, c + 1.5), prev)
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"done -> {P['lib']}  ({len(ledger)} segments in ledger)")


def main():
    base, args = parse_base(__doc__)
    P = paths(base)
    {"plan": plan, "cut": cut}[args[0]](P)


if __name__ == "__main__":
    main()
