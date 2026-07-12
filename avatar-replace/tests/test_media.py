from core import media


def test_probe(sample_video):
    info = media.probe(sample_video)
    assert 19.5 < info.duration < 20.5
    assert info.width == 640 and info.has_audio


def test_extract_frames(sample_video, tmp_path):
    frames = media.extract_frames(sample_video, tmp_path, interval=2.0)
    assert 9 <= len(frames) <= 11
    assert all(f.path.exists() and f.t >= 0 for f in frames)


def test_scene_cuts(sample_video):
    cuts = media.scene_cuts(sample_video)
    assert any(abs(c - 5) < 0.5 for c in cuts)
    assert any(abs(c - 12) < 0.5 for c in cuts)


def test_cut_clip(sample_video, tmp_path):
    seg = tmp_path / "seg.mp4"
    media.cut_clip(sample_video, seg, 2.0, 6.0)
    assert abs(media.probe(seg).duration - 4.0) < 0.2
