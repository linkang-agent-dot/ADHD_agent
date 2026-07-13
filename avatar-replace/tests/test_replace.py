from pathlib import Path

from core import media
from core.replace import build_prompt, pick_ref, replace_segment
from core.providers.base import FakeProvider


def test_build_prompt():
    p = build_prompt("向前走两步后转身，镜头固定")
    assert "首帧" in p and "向前走两步" in p
    assert "不出现其他人物" in p


def test_build_prompt_default_action():
    # 打轴没给出动作描述时用默认动作，不能生成空指令
    assert "站立" in build_prompt("")


def test_pick_ref_orientation(tmp_path):
    front = tmp_path / "front.jpg"; front.write_bytes(b"f")
    back = tmp_path / "back.jpg"; back.write_bytes(b"b")
    refs = [back, front]
    assert pick_ref(refs, "正面") == front
    assert pick_ref(refs, "背面") == back
    assert pick_ref([front], "背面") == front  # 缺背面图兜底
    assert pick_ref([], "正面") is None


def test_replace_segment_trims_to_expected(tmp_path):
    # i2v 固定产出约 5s（FakeProvider 同样出 5s 白场），目标 2s → 必须裁齐
    seg = tmp_path / "001_replace.mp4"; seg.write_bytes(b"v")
    refs = [tmp_path / "front.png"]; refs[0].write_bytes(b"i")
    fake = FakeProvider()
    out = replace_segment(fake, seg, "站立挥手，镜头固定", "正面",
                          refs, tmp_path / "out", expect_dur=2.0)
    assert out.exists()
    assert out.name == "001_replaced.mp4"
    assert "站立挥手" in fake.clip_calls[0]
    assert fake.edit_calls == []  # 绝不走真人视频输入路径
    assert abs(media.probe(out).duration - 2.0) < 0.2
