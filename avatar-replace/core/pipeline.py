"""任务状态机 + 断点续跑。

状态流转：created → annotated → confirmed → cut → done。
状态与段级进度全部落盘 job.json；replace 段带 status(pending/done)，
续跑时跳过 status=done 的 replace 段（keep 段无状态语义）。
stitch 每次 run 都重跑一遍（幂等，覆盖 final.mp4），保证中断后终态一致。
"""
import json
import os
import shutil
import time
import uuid
from pathlib import Path

from core import annotate as ann
from core import cut as cutmod
from core import media
from core import replace as repmod
from core import stitch as stitchmod
from core import storyboard as sbmod
from core import subtitles as submod
from core import wardrobe as warmod
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
        # 原子写：半途崩不能留下损坏的 job.json（断点续跑全靠它）
        tmp = self.dir / "job.json.tmp"
        tmp.write_text(
            json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.dir / "job.json")

    @classmethod
    def create(cls, video: Path, jobs_root: Path, cfg: Config) -> "Job":
        info = media.probe(video)
        if info.duration > cfg.limits.max_video_seconds:
            raise ValueError(
                f"视频 {info.duration:.0f}s 超上限 {cfg.limits.max_video_seconds}s")
        size_mb = Path(video).stat().st_size / 1024 / 1024
        if size_mb > cfg.limits.max_video_mb:
            raise ValueError(
                f"视频 {size_mb:.0f}MB 超上限 {cfg.limits.max_video_mb}MB")
        jid = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        jdir = Path(jobs_root) / jid
        jdir.mkdir(parents=True)
        shutil.copy(video, jdir / "source.mp4")
        (jdir / "job.json").write_text(json.dumps({
            "id": jid, "state": "created", "duration": info.duration,
            "timeline": [], "segments": []}, ensure_ascii=False, indent=2),
            encoding="utf-8")
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
        # 重新确认使已有切段作废——否则改动会被"segments 非空则不重切"静默吞掉
        self._meta["segments"] = []
        # 关键帧按段名幂等缓存，段界变了必须一并作废，否则复用错段的旧帧
        if (self.dir / "kf").exists():
            shutil.rmtree(self.dir / "kf")
        self._meta["state"] = "confirmed"
        self._save()

    def run(self, provider: Provider, avatar_refs: list[Path]) -> None:
        # 状态机不变量：未经人工确认不得进入替换——否则会静默产出
        # "未替换任何人但标记完成"的成片，是本业务最坏的失败形态
        if self.state not in ("confirmed", "cut", "done"):
            raise ValueError(f"job 状态 {self.state} 不可 run，先 annotate+confirm")
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
        # 换装：数字人穿上与原片一致的服装+弱化肌肉感（2026-07-13 用户反馈）。
        # job 级形象图落在 jobs/<id>/avatar/，幂等续跑不重复生成。
        pending = [s for s in self._meta["segments"]
                   if s["mode"] == "replace" and s["status"] != "done"]
        if pending and avatar_refs:
            if not self._meta.get("garment"):
                sample = next((t["sample_frame"] for t in self._meta["timeline"]
                               if t.get("confirmed")), None)
                if sample:
                    self._meta["garment"] = warmod.describe_garment(
                        provider, Path(sample))
                    self._save()
            if self._meta.get("garment"):
                avatar_refs = warmod.dress_avatar(
                    provider, avatar_refs, self._meta["garment"],
                    self.dir / "avatar")
        for s in self._meta["segments"]:
            if s["mode"] != "replace" or s["status"] == "done":
                continue
            # 分镜复刻：每段先读原片帧出分镜（缓存进 job.json），
            # 再用换装数字人图出首尾场景关键帧，i2v 双锚点生成
            if not s.get("storyboard"):
                s["storyboard"] = sbmod.describe_segment(
                    provider, self.dir / "frames", s["start"], s["end"],
                    interval=self.cfg.pipeline.frame_interval)
                self._save()
            kf_a = kf_b = None
            if avatar_refs:
                base = next((r for r in avatar_refs
                             if r.stem.lower().startswith("front")),
                            avatar_refs[0])
                kf_a, kf_b = sbmod.build_keyframes(
                    provider, base, s["storyboard"], self.dir / "kf",
                    Path(s["path"]).stem)
            out = repmod.replace_segment(
                provider, Path(s["path"]), s["storyboard"], kf_a, kf_b,
                self.dir / "out", expect_dur=s["end"] - s["start"])
            s["path"] = str(out)
            s["status"] = "done"
            self._save()  # 段级落盘：每替换完一段立即持久化，中断后从下一段续
        final = stitchmod.stitch(
            [{**s, "path": Path(s["path"])} for s in self._meta["segments"]],
            original=src, workdir=self.dir, drift_pct=p.duration_drift_pct)
        final = self._burn_subtitles(provider, final)
        self._meta["state"] = "done"
        self._meta["final"] = str(final)
        self._save()

    def _burn_subtitles(self, provider: Provider, final: Path) -> Path:
        """替换段丢失的原片硬字幕重烧回去。OCR 结果缓存 captions.json（续跑不重复花钱）；
        相邻 replace 段合并成整时段处理（超长命中区被 segment_max 切开只是生成粒度）。"""
        spans: list[list[float]] = []
        for s in self._meta["segments"]:
            if s["mode"] != "replace":
                continue
            if spans and abs(s["start"] - spans[-1][1]) < 0.02:
                spans[-1][1] = s["end"]
            else:
                spans.append([s["start"], s["end"]])
        if not spans:
            return final
        spans_t = [(a, b) for a, b in spans]
        cache = self.dir / "captions.json"
        if cache.exists():
            ocr = json.loads(cache.read_text(encoding="utf-8"))
            ocr["captions"] = [tuple(c) for c in ocr.get("captions", [])]
        else:
            ocr = submod.ocr_spans(provider, self.dir / "frames", spans_t,
                                   interval=self.cfg.pipeline.frame_interval)
            cache.write_text(json.dumps(
                {"captions": [list(c) for c in ocr["captions"]],
                 "bottom": ocr["bottom"]}, ensure_ascii=False, indent=2),
                encoding="utf-8")
        if not ocr["captions"] and not ocr.get("bottom"):
            return final
        out = self.dir / "final_sub.mp4"
        submod.burn(final, out, ocr, spans_t, self.dir / "sub")
        return out
