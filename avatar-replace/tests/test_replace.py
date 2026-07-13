from core import media
from core.replace import build_prompt, replace_segment
from core.providers.base import FakeProvider

SB = {"scene": "浅色卧室", "shot": "中景", "start_pose": "面向镜头",
      "end_pose": "背对镜头", "action": "原地转身背对镜头", "camera": "缓慢推近",
      "others": ""}


def test_build_prompt_dual_anchor():
    p = build_prompt(SB, has_last=True)
    assert "尾帧" in p and "原地转身" in p and "镜头缓慢推近" in p


def test_build_prompt_first_only_and_defaults():
    p = build_prompt({}, has_last=False)
    assert "尾帧" not in p and "首帧" in p
    assert "站立" in p and "镜头固定" in p  # 分镜缺失兜底


def test_replace_segment_trims_to_expected(tmp_path):
    # i2v 固定产出约 5s（FakeProvider 同样出 5s 白场），目标 2s → 必须裁齐
    seg = tmp_path / "001_replace.mp4"; seg.write_bytes(b"v")
    kf = tmp_path / "kf_a.jpg"; kf.write_bytes(b"i")
    fake = FakeProvider()
    out = replace_segment(fake, seg, SB, kf, None, tmp_path / "out",
                          expect_dur=2.0)
    assert out.exists()
    assert out.name == "001_replaced.mp4"
    assert "原地转身" in fake.clip_calls[0]
    assert fake.edit_calls == []  # 绝不走真人视频输入路径
    assert abs(media.probe(out).duration - 2.0) < 0.2
