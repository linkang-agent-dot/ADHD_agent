import json

import pytest

from core.config import ArkCfg, Config, LimitsCfg, PipelineCfg
from core.pipeline import Job
from core.providers.base import FakeProvider


def _cfg():
    return Config(ark=ArkCfg(base_url="x", vlm_model="a", video_model="b"),
                  pipeline=PipelineCfg(), limits=LimitsCfg())


def _fake():
    return FakeProvider(vision_responses=[
        json.dumps({"hits": [6, 7]}), json.dumps({"hits": []}), json.dumps({"hits": []}),
        "红色T恤男孩",
    ])


def test_full_run_with_fake_provider(sample_video, tmp_path):
    job = Job.create(sample_video, jobs_root=tmp_path, cfg=_cfg())
    assert job.state == "created"
    job.annotate(_fake())
    assert job.state == "annotated" and len(job.timeline) == 1
    for item in job.timeline:
        item["confirmed"] = True
    job.confirm()
    assert job.state == "confirmed"
    job.run(_fake(), avatar_refs=[])          # cut → replace → stitch
    assert job.state == "done"
    assert (job.dir / "final.mp4").exists()


def test_confirm_requires_at_least_one(sample_video, tmp_path):
    job = Job.create(sample_video, jobs_root=tmp_path, cfg=_cfg())
    job.annotate(_fake())
    with pytest.raises(ValueError):
        job.confirm()   # 没人确认任何时段


def test_resume_skips_done_segments(sample_video, tmp_path):
    job = Job.create(sample_video, jobs_root=tmp_path, cfg=_cfg())
    job.annotate(_fake())
    for item in job.timeline:
        item["confirmed"] = True
    job.confirm()
    job.run(_fake(), avatar_refs=[])
    # 重新加载同一 job，再 run：不应产生新的 video_edit 调用
    fake2 = FakeProvider()
    job2 = Job.load(job.dir, cfg=_cfg())
    job2.run(fake2, avatar_refs=[])
    assert fake2.edit_calls == []
    assert job2.state == "done"


def test_create_rejects_overlong_video(sample_video, tmp_path):
    cfg = _cfg()
    cfg.limits.max_video_seconds = 10   # sample 是 20s
    with pytest.raises(ValueError):
        Job.create(sample_video, jobs_root=tmp_path, cfg=cfg)


def test_run_requires_confirmed_state(sample_video, tmp_path):
    # 未 confirm 直接 run 必须拒绝——否则会静默产出"零替换"成片
    job = Job.create(sample_video, jobs_root=tmp_path, cfg=_cfg())
    job.annotate(_fake())
    import pytest
    with pytest.raises(ValueError, match="不可 run"):
        job.run(FakeProvider(), avatar_refs=[])


def test_reconfirm_invalidates_segments(sample_video, tmp_path):
    # run 过后重新 confirm 不同选择 → 旧切段作废，再 run 会重切重替换
    job = Job.create(sample_video, jobs_root=tmp_path, cfg=_cfg())
    job.annotate(_fake())
    for item in job.timeline: item["confirmed"] = True
    job.confirm()
    job.run(_fake(), avatar_refs=[])
    job.confirm()  # 重新确认（同样全选）
    assert job._meta["segments"] == []
    fake2 = FakeProvider()
    job.run(fake2, avatar_refs=[])
    assert len(fake2.edit_calls) == 1  # 重切后重新替换
