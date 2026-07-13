from core.cut import plan_segments, execute_cut
from core import media


def test_plan_basic():
    tl = [{"start": 2.0, "end": 5.0, "person_desc": "红衣男孩", "confirmed": True}]
    segs = plan_segments(tl, duration=20.0, scene_cuts=[5.0, 12.0],
                         buffer=0.5, tolerance=2.0, segment_max=15.0)
    assert [s["mode"] for s in segs] == ["keep", "replace", "keep"]
    assert segs[0]["start"] == 0.0 and segs[-1]["end"] == 20.0
    r = segs[1]
    assert r["start"] <= 1.5 and r["end"] >= 5.5
    # 全片无缝covered
    for a, b in zip(segs, segs[1:]):
        assert a["end"] == b["start"]


def test_plan_split_over_15s():
    tl = [{"start": 0.0, "end": 18.0, "person_desc": "x", "confirmed": True}]
    segs = plan_segments(tl, duration=20.0, scene_cuts=[], buffer=0.0,
                         tolerance=0.0, segment_max=15.0)
    rep = [s for s in segs if s["mode"] == "replace"]
    assert len(rep) == 2 and all(s["end"] - s["start"] <= 15.0 for s in rep)


def test_plan_skips_unconfirmed():
    tl = [{"start": 2.0, "end": 5.0, "person_desc": "x", "confirmed": False}]
    segs = plan_segments(tl, duration=20.0, scene_cuts=[], buffer=0.5,
                         tolerance=2.0, segment_max=15.0)
    assert all(s["mode"] == "keep" for s in segs)


def test_plan_merges_overlapping():
    tl = [{"start": 2.0, "end": 5.0, "person_desc": "男孩", "confirmed": True},
          {"start": 5.5, "end": 8.0, "person_desc": "女孩", "confirmed": True}]
    # buffer=0.5 外扩后 [1.5,5.5] 和 [5.0,8.5] 重叠 → 合并为一段
    segs = plan_segments(tl, duration=20.0, scene_cuts=[], buffer=0.5,
                         tolerance=0.0, segment_max=15.0)
    rep = [s for s in segs if s["mode"] == "replace"]
    assert len(rep) == 1
    assert rep[0]["start"] == 1.5 and rep[0]["end"] == 8.5
    assert "男孩" in rep[0]["desc"] and "女孩" in rep[0]["desc"]


def test_plan_edge_clamp():
    # 命中区贴片头片尾：外扩不得越界，且不产生零长 keep 段
    tl = [{"start": 0.2, "end": 19.9, "person_desc": "x", "confirmed": True}]
    segs = plan_segments(tl, duration=20.0, scene_cuts=[], buffer=0.5,
                         tolerance=0.0, segment_max=15.0)
    assert segs[0]["start"] == 0.0 and segs[-1]["end"] == 20.0
    assert all(s["end"] > s["start"] for s in segs)


def test_execute_cut(sample_video, tmp_path):
    segs = [{"start": 0.0, "end": 6.0, "mode": "keep"},
            {"start": 6.0, "end": 11.0, "mode": "replace", "desc": "x"},
            {"start": 11.0, "end": 20.0, "mode": "keep"}]
    out = execute_cut(sample_video, segs, tmp_path)
    assert len(out) == 3
    assert abs(media.probe(out[1]["path"]).duration - 5.0) < 0.3
    assert out[0]["path"].name == "000_keep.mp4"


def test_plan_splits_at_inner_scene_cuts():
    # 替换区内部有镜头切点必须分段——一段混两个镜头会生成穿帮画面
    tl = [{"start": 0.0, "end": 6.0, "person_desc": "x", "confirmed": True}]
    segs = plan_segments(tl, duration=8.0, scene_cuts=[2.6], buffer=0.0,
                         tolerance=0.0, segment_max=5.0)
    rep = [s for s in segs if s["mode"] == "replace"]
    assert [(s["start"], s["end"]) for s in rep] == [(0.0, 2.6), (2.6, 6.0)]


def test_plan_inner_cut_near_edge_not_split():
    # 离段边 <0.75s 的切点不切，避免产出碎段
    tl = [{"start": 0.0, "end": 6.0, "person_desc": "x", "confirmed": True}]
    segs = plan_segments(tl, duration=8.0, scene_cuts=[5.6], buffer=0.0,
                         tolerance=0.0, segment_max=10.0)
    rep = [s for s in segs if s["mode"] == "replace"]
    assert len(rep) == 1


def test_plan_snaps_outward_only():
    # 起点向前吸到 1.0，终点向后吸到 6.0（向内吸绝不发生，命中区完整覆盖）；
    # 内部切点 3.0 按镜头分段但不缩小覆盖范围
    tl = [{"start": 2.0, "end": 5.0, "person_desc": "x", "confirmed": True}]
    segs = plan_segments(tl, duration=20.0, scene_cuts=[1.0, 3.0, 6.0],
                         buffer=0.0, tolerance=2.0, segment_max=15.0)
    rep = [s for s in segs if s["mode"] == "replace"]
    assert [(s["start"], s["end"]) for s in rep] == [(1.0, 3.0), (3.0, 6.0)]


def test_desc_dedup_no_substring_swallow():
    # "红衣男孩"与"男孩"是两个人，短描述不能被子串包含吞掉
    tl = [{"start": 2.0, "end": 4.0, "person_desc": "红衣男孩", "confirmed": True},
          {"start": 4.0, "end": 6.0, "person_desc": "男孩", "confirmed": True}]
    segs = plan_segments(tl, duration=20.0, scene_cuts=[], buffer=0.5,
                         tolerance=0.0, segment_max=15.0)
    rep = [s for s in segs if s["mode"] == "replace"][0]
    assert rep["desc"] == "红衣男孩；男孩"
