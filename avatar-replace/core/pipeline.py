"""任务状态机 + 断点续跑。

状态流转：created → annotated → confirmed → cut → done。
状态与段级进度全部落盘 job.json；replace 段带 status(pending/done)，
续跑时跳过 status=done 的 replace 段（keep 段无状态语义）。
stitch 每次 run 都重跑一遍（幂等，覆盖 final.mp4），保证中断后终态一致。
"""
import json
import shutil
import time
import uuid
from pathlib import Path

from core import annotate as ann
from core import cut as cutmod
from core import media
from core import replace as repmod
from core import stitch as stitchmod
from core.config import Config
from core.providers.base import Provider


class Job:
    def __init__(self, jdir: Path, cfg: Config):
        self.dir, self.cfg = Path(jdir), cfg
        self._meta = json.loads((self.dir / "job.json").read_text(encoding="utf-8"))

    @property
    def state(self) -> str:
        return self._meta["state"]

    @property
    def timeline(self) -> list[dict]:
        # 返回内存引用：外部改 confirmed 后由 confirm() 统一 _save() 持久化
        return self._meta["timeline"]

    def _save(self) -> None:
        (self.dir / "job.json").write_text(
            json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def create(cls, video: Path, jobs_root: Path, cfg: Config) -> "Job":
        info = media.probe(video)
        if info.duration > cfg.limits.max_video_seconds:
            raise ValueError(
                f"视频 {info.duration:.0f}s 超上限 {cfg.limits.max_video_seconds}s")
        jid = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        jdir = Path(jobs_root) / jid
        jdir.mkdir(parents=True)
        shutil.copy(video, jdir / "source.mp4")
        (jdir / "job.json").write_text(json.dumps({
            "id": jid, "state": "created", "duration": info.duration,
            "timeline": [], "segments": []}, ensure_ascii=False), encoding="utf-8")
        return cls(jdir, cfg)

    @classmethod
    def load(cls, jdir: Path, cfg: Config) -> "Job":
        return cls(jdir, cfg)

    def annotate(self, provider: Provider) -> None:
        self._meta["timeline"] = ann.annotate(
            self.dir / "source.mp4", self.dir, provider,
            interval=self.cfg.pipeline.frame_interval)
        self._meta["state"] = "annotated"
        self._save()

    def confirm(self) -> None:
        if not any(t.get("confirmed") for t in self._meta["timeline"]):
            raise ValueError("没有已确认的时段")
        self._meta["state"] = "confirmed"
        self._save()

    def run(self, provider: Provider, avatar_refs: list[Path]) -> None:
        p = self.cfg.pipeline
        src = self.dir / "source.mp4"
        # 切段只做一次：segments 非空说明已切过（续跑直接复用）
        if not self._meta["segments"]:
            segs = cutmod.plan_segments(
                self._meta["timeline"], self._meta["duration"],
                media.scene_cuts(src), p.buffer, p.scene_align_tolerance, p.segment_max)
            cut_out = cutmod.execute_cut(src, segs, self.dir)
            self._meta["segments"] = [
                {**{k: v for k, v in s.items() if k != "path"},
                 "path": str(s["path"]), "status": "pending"} for s in cut_out]
            self._meta["state"] = "cut"
            self._save()
        for s in self._meta["segments"]:
            if s["mode"] != "replace" or s["status"] == "done":
                continue
            out = repmod.replace_segment(
                provider, Path(s["path"]), s.get("desc", ""), avatar_refs,
                self.dir / "out")
            s["path"] = str(out)
            s["status"] = "done"
            self._save()  # 段级落盘：每替换完一段立即持久化，中断后从下一段续
        final = stitchmod.stitch(
            [{**s, "path": Path(s["path"])} for s in self._meta["segments"]],
            original=src, workdir=self.dir, drift_pct=p.duration_drift_pct)
        self._meta["state"] = "done"
        self._meta["final"] = str(final)
        self._save()
