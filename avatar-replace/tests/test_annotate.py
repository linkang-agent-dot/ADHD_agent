import json

from core.annotate import annotate, merge_hits
from core.providers.base import FakeProvider


def test_merge_hits():
    # 帧时间 0..9，命中 2,3,4 和 8 → 两个时段
    spans = merge_hits([2.0, 3.0, 4.0, 8.0], interval=1.0)
    assert spans == [(2.0, 5.0), (8.0, 9.0)]  # 末端 +interval


def test_annotate_two_pass(sample_video, tmp_path):
    fake = FakeProvider(vision_responses=[
        json.dumps({"hits": [2, 3, 4]}),          # 粗扫批1 (帧0-7)
        json.dumps({"hits": []}),                  # 粗扫批2
        json.dumps({"hits": []}),                  # 粗扫批3
        "画面中央穿红色T恤的男孩，约8岁，在奔跑",     # 细化
    ])
    tl = annotate(sample_video, tmp_path, provider=fake, interval=1.0)
    assert len(tl) == 1
    assert tl[0]["start"] == 2.0 and tl[0]["end"] == 5.0
    assert "红色T恤" in tl[0]["person_desc"]
    assert tl[0]["sample_frame"]
    assert tl[0]["confirmed"] is False
    # 粗扫 prompt 必须要求 JSON 输出
    assert "JSON" in fake.vision_calls[0]
    # timeline.json 落盘
    saved = json.loads((tmp_path / "timeline.json").read_text(encoding="utf-8"))
    assert saved == tl
