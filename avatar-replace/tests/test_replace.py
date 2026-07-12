from pathlib import Path
from core.replace import build_prompt, replace_segment
from core.providers.base import FakeProvider


def test_build_prompt():
    p = build_prompt("画面左侧穿蓝裙的女孩，约6岁")
    assert "视频1" in p and "图片1" in p and "蓝裙" in p
    assert "运镜" in p  # 必须锁运镜


def test_replace_segment(tmp_path):
    seg = tmp_path / "001_replace.mp4"; seg.write_bytes(b"v")
    refs = [tmp_path / "front.png"]; refs[0].write_bytes(b"i")
    fake = FakeProvider()
    out = replace_segment(fake, seg, "红衣男孩", refs, tmp_path / "out")
    assert out.exists()
    assert out.name == "001_replaced.mp4"
    assert "红衣男孩" in fake.edit_calls[0]
