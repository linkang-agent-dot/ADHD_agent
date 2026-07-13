import json

from core.storyboard import build_keyframes, describe_segment, SEG_PROMPT
from core.providers.base import FakeProvider


def _mk_frames(d, n):
    d.mkdir(parents=True, exist_ok=True)
    for i in range(1, n + 1):
        (d / f"f_{i:05d}.jpg").write_bytes(b"\xff\xd8x")


SB = {"scene": "浅色卧室白墙暖光", "shot": "中景人物居中",
      "start_pose": "面向镜头站立", "end_pose": "背对镜头站立，镜头推近到上半身",
      "action": "先面向镜头，随后原地转身背对镜头", "camera": "推近", "others": ""}


def test_describe_segment_parses_and_thins_frames(tmp_path):
    _mk_frames(tmp_path / "frames", 20)  # t=0..19，段(0,12)命中13帧>6→抽稀
    fake = FakeProvider(vision_responses=[json.dumps(SB)])
    sb = describe_segment(fake, tmp_path / "frames", 0.0, 12.0, interval=1.0)
    assert sb["action"].startswith("先面向镜头")
    assert sb["camera"] == "推近"
    assert "措辞中性" in SEG_PROMPT  # 分镜描述会进生成 prompt，必须避风控


def test_describe_segment_fallback_defaults(tmp_path):
    _mk_frames(tmp_path / "frames", 5)
    fake = FakeProvider()  # 默认回 "[]"，解析失败走默认值
    sb = describe_segment(fake, tmp_path / "frames", 0.0, 4.0, interval=1.0)
    assert sb["camera"] == "固定" and sb["action"] == ""


def test_build_keyframes_dual_anchor_idempotent(tmp_path):
    base = tmp_path / "front.jpg"; base.write_bytes(b"f")
    fake = FakeProvider()
    kf_a, kf_b = build_keyframes(fake, base, SB, tmp_path / "kf", "001_replace")
    assert kf_a.exists() and kf_b is not None and kf_b.exists()
    assert len(fake.image_calls) == 2
    assert "浅色卧室" in fake.image_calls[0] and "面向镜头站立" in fake.image_calls[0]
    assert "背对镜头" in fake.image_calls[1]
    # 幂等：已有关键帧不重复生成
    build_keyframes(fake, base, SB, tmp_path / "kf", "001_replace")
    assert len(fake.image_calls) == 2


def test_build_keyframes_skips_last_when_pose_same(tmp_path):
    base = tmp_path / "front.jpg"; base.write_bytes(b"f")
    sb = dict(SB, end_pose=SB["start_pose"])
    fake = FakeProvider()
    kf_a, kf_b = build_keyframes(fake, base, sb, tmp_path / "kf", "002_replace")
    assert kf_a.exists() and kf_b is None
    assert len(fake.image_calls) == 1
