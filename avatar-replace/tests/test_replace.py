from core import media
from core.replace import (build_prompt, build_refs_prompt, replace_segment,
                          replace_segment_refs)
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


def test_build_refs_prompt_indexes_images():
    p = build_refs_prompt(SB, n_avatar=2, has_scene=True)
    assert "图1（正面）与图2（背面）" in p and "图3" in p
    assert "原地转身" in p and "构图为中景" in p


def test_build_refs_prompt_single_avatar_no_scene():
    p = build_refs_prompt({}, n_avatar=1, has_scene=False)
    assert "图1" in p and "图2" not in p and "分镜描述" in p


def test_replace_segment_refs_orders_front_first(tmp_path):
    seg = tmp_path / "001_replace.mp4"; seg.write_bytes(b"v")
    back = tmp_path / "back.jpg"; back.write_bytes(b"b")
    front = tmp_path / "front.jpg"; front.write_bytes(b"f")
    scene = tmp_path / "scene.jpg"; scene.write_bytes(b"s")
    fake = FakeProvider()
    out = replace_segment_refs(fake, seg, SB, [back, front], scene,
                               tmp_path / "out", expect_dur=2.0)
    assert out.exists()
    assert fake.ref_counts == [3]  # 正面+背面+场景
    assert "图1（正面）" in fake.clip_calls[0]
    assert abs(media.probe(out).duration - 2.0) < 0.2


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
