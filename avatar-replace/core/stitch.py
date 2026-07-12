"""拼回：替换段时长漂移校正（retime）→ concat → 原片音轨整条铺回。"""
from pathlib import Path

from core import media


def stitch(segs: list[dict], original: Path, workdir: Path, drift_pct: float = 2.0) -> Path:
    fixed = []
    for i, s in enumerate(segs):
        expect = s["end"] - s["start"]
        actual = media.probe(s["path"]).duration
        if s["mode"] == "replace" and abs(actual - expect) / expect * 100 > drift_pct:
            adj = workdir / f"retime_{i:03d}.mp4"
            media.retime(s["path"], adj, factor=expect / actual)
            fixed.append(adj)
        else:
            fixed.append(Path(s["path"]))
    joined = workdir / "joined.mp4"
    media.concat(fixed, joined)
    final = workdir / "final.mp4"
    media.replace_audio(joined, original, final)
    return final
