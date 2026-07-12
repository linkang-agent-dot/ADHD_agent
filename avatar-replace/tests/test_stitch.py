from core.stitch import stitch
from core import media


def _make_segs(sample_video, tmp_path):
    segs = []
    for i, (s, e) in enumerate([(0, 6), (6, 11), (11, 20)]):
        p = tmp_path / f"{i:03d}.mp4"
        media.cut_clip(sample_video, p, s, e)
        segs.append({"path": p, "start": float(s), "end": float(e),
                     "mode": "replace" if i == 1 else "keep"})
    return segs


def test_stitch_full_length(sample_video, tmp_path):
    segs = _make_segs(sample_video, tmp_path)
    final = stitch(segs, original=sample_video, workdir=tmp_path, drift_pct=2.0)
    info = media.probe(final)
    assert abs(info.duration - 20.0) < 0.5
    assert info.has_audio
    assert not list(tmp_path.glob("retime_*.mp4"))  # 漂移<2%不应触发retime


def test_stitch_retimes_drifted_segment(sample_video, tmp_path):
    # 中段替换结果被人为拉长 20% → 应触发 retime 回到 ~5s
    segs = _make_segs(sample_video, tmp_path)
    drift = tmp_path / "drift.mp4"
    media.retime(segs[1]["path"], drift, factor=1.2)
    segs[1]["path"] = drift
    final = stitch(segs, original=sample_video, workdir=tmp_path, drift_pct=2.0)
    assert abs(media.probe(final).duration - 20.0) < 0.5
