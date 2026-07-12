from pathlib import Path
from core.config import load_config

def test_load_config_merges_env_key(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "ark:\n  base_url: 'http://x'\n  vlm_model: m1\n  video_model: m2\n"
        "pipeline:\n  frame_interval: 1.0\n  segment_max: 15.0\n  buffer: 0.5\n"
        "  scene_align_tolerance: 2.0\n  duration_drift_pct: 2.0\n"
        "limits:\n  max_video_seconds: 60\n  max_video_mb: 200\n",
        encoding="utf-8")
    monkeypatch.setenv("ARK_API_KEY", "sk-test")
    cfg = load_config(cfg_file)
    assert cfg.ark.api_key == "sk-test"
    assert cfg.pipeline.segment_max == 15.0

def test_missing_key_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("ARK_API_KEY", raising=False)
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("ark: {base_url: x, vlm_model: a, video_model: b}", encoding="utf-8")
    import pytest
    with pytest.raises(RuntimeError, match="ARK_API_KEY"):
        load_config(cfg_file, require_key=True)
