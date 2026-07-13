from core.wardrobe import describe_garment, dress_avatar, GARMENT_PROMPT
from core.providers.base import FakeProvider


def test_garment_prompt_neutral_wording():
    # 服装描述会进 Seedream prompt，措辞必须避文本风控（实锤敏感词见 memory）
    assert "中性" in GARMENT_PROMPT and "内衣" in GARMENT_PROMPT  # 明令禁用该词


def test_describe_garment(tmp_path):
    frame = tmp_path / "f.jpg"; frame.write_bytes(b"\xff\xd8x")
    fake = FakeProvider(vision_responses=["米白色蕾丝吊带背心与同色短裤套装"])
    assert describe_garment(fake, frame) == "米白色蕾丝吊带背心与同色短裤套装"


def test_dress_avatar_idempotent(tmp_path):
    front = tmp_path / "front.jpg"; front.write_bytes(b"f")
    back = tmp_path / "back.jpg"; back.write_bytes(b"b")
    fake = FakeProvider()
    out_dir = tmp_path / "job_avatar"
    outs = dress_avatar(fake, [back, front], "米色吊带背心", out_dir)
    assert [p.name for p in outs] == ["back.jpg", "front.jpg"]
    assert all(p.exists() for p in outs)
    assert len(fake.image_calls) == 2
    assert "米色吊带背心" in fake.image_calls[0]
    assert "肌肉" in fake.image_calls[0]  # 弱化肌肉感必须在换装指令里
    # 幂等：已有产物不重复生成（续跑不重复花钱）
    dress_avatar(fake, [back, front], "米色吊带背心", out_dir)
    assert len(fake.image_calls) == 2
