# tests/conftest.py
import subprocess

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def sample_video(tmp_path_factory) -> Path:
    """20s 彩条+正弦音，带 5s/12s 两个画面突变（当镜头切点用）"""
    out = tmp_path_factory.mktemp("media") / "sample.mp4"
    parts = []
    d = tmp_path_factory.mktemp("media_parts")
    for i, (color, dur) in enumerate([("red", 5), ("blue", 7), ("green", 8)]):
        p = d / f"p{i}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=640x360:r=25:d={dur}",
            "-f", "lavfi", "-i", f"sine=frequency={220*(i+1)}:duration={dur}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(p)],
            check=True, capture_output=True)
        parts.append(p)
    lst = d / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(out)], check=True, capture_output=True)
    return out
