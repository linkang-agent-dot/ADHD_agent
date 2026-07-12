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
