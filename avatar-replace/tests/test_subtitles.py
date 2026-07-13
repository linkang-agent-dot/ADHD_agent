import json
import subprocess

from core import media
from core.subtitles import burn, ocr_spans
from core.providers.base import FakeProvider


def _mk_frames(d, n):
    d.mkdir(parents=True, exist_ok=True)
    for i in range(1, n + 1):
        (d / f"f_{i:05d}.jpg").write_bytes(b"\xff\xd8x")


def test_ocr_spans_merges_and_clamps(tmp_path):
    _mk_frames(tmp_path / "frames", 10)  # 帧 t=0..9
    # span (2,6)：命中帧 2,3,4,5,6 → 一批
    fake = FakeProvider(vision_responses=[json.dumps({"frames": [
        {"i": 0, "caption": "超薄透气", "bottom": "仅供产品展示/无不良引导"},
        {"i": 1, "caption": "超薄透气", "bottom": "仅供产品展示/无不良引导"},
        {"i": 2, "caption": "舒适贴身", "bottom": "仅供产品展示/无不良引导"},
        {"i": 3, "caption": "舒适贴身", "bottom": ""},
        {"i": 4, "caption": "", "bottom": ""},
    ]})])
    ocr = ocr_spans(fake, tmp_path / "frames", [(2.0, 6.0)], interval=1.0)
    assert ocr["captions"] == [(2.0, 4.0, "超薄透气"), (4.0, 6.0, "舒适贴身")]
    assert ocr["bottom"] == "仅供产品展示/无不良引导"


def test_ocr_spans_empty_when_no_captions(tmp_path):
    _mk_frames(tmp_path / "frames", 5)
    fake = FakeProvider()  # 默认回 "[]"，解析不出 frames
    ocr = ocr_spans(fake, tmp_path / "frames", [(0.0, 4.0)], interval=1.0)
    assert ocr["captions"] == [] and ocr["bottom"] == ""


def test_burn_produces_video_with_captions(tmp_path):
    src = tmp_path / "in.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                    "color=c=black:s=320x240:r=24:d=4",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(src)],
                   check=True, capture_output=True)
    ocr = {"captions": [(0.0, 2.0, "测试字幕")], "bottom": "仅供展示/无不良引导"}
    out = burn(src, tmp_path / "out.mp4", ocr, [(0.0, 4.0)], tmp_path / "work")
    assert out.exists()
    assert abs(media.probe(out).duration - 4.0) < 0.2
    # 工程坑规避：字体以相对名进工作目录、文案走 textfile
    assert (tmp_path / "work" / "font.ttc").exists()
    assert (tmp_path / "work" / "cap0.txt").read_text(encoding="utf-8") == "测试字幕"


def test_burn_noop_without_content(tmp_path):
    src = tmp_path / "in.mp4"; src.write_bytes(b"v")
    out = burn(src, tmp_path / "out.mp4", {"captions": [], "bottom": ""},
               [(0.0, 1.0)], tmp_path / "work")
    assert out.read_bytes() == b"v"  # 无字幕原样拷贝，不跑 ffmpeg
