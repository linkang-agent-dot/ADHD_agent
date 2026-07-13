"""拼回：替换段归一化（统一编码参数+时长对齐）→ concat → 原片音轨整条铺回。

替换段来自 Seedance 下载（720p/自有fps/可能无音轨），与本地切段参数不同，
不归一化直接 concat -c copy 会产出坏片——所有 replace 段一律重编码到源片参数。
"""
from pathlib import Path

from core import media


def stitch(segs: list[dict], original: Path, workdir: Path, drift_pct: float = 2.0) -> Path:
    src_info = media.probe(original)
    fixed = []
    for i, s in enumerate(segs):
        expect = s["end"] - s["start"]
        if s["mode"] != "replace" or expect <= 0:  # keep 段本就同参；零长守卫防除零
            fixed.append(Path(s["path"]))
            continue
        actual = media.probe(s["path"]).duration
        factor = 1.0
        if abs(actual - expect) / expect * 100 > drift_pct:
            factor = expect / actual
        norm = Path(workdir) / f"norm_{i:03d}.mp4"
        media.normalize(s["path"], norm, src_info.width, src_info.height,
                        src_info.fps, retime_factor=factor)
        fixed.append(norm)
    joined = Path(workdir) / "joined.mp4"
    media.concat(fixed, joined)
    final = Path(workdir) / "final.mp4"
    media.replace_audio(joined, original, final)
    return final
