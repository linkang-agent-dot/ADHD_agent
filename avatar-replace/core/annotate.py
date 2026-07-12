"""VLM 两遍打轴：粗扫定位含未成年人的帧 → 合并为时段 → 细化取样帧描述外观。"""
import json
import re
from pathlib import Path

from core import media
from core.providers.base import Provider

COARSE_PROMPT = """你在做广告素材合规审查。下面按顺序给出视频抽帧（第0张对应索引0）。
找出画面中出现疑似未成年人（看起来不满18岁的真人）的帧。
只输出 JSON：{"hits": [命中的帧索引数组]}，没有则 {"hits": []}。"""

DETAIL_PROMPT = """这是广告视频中出现未成年人的画面。用一句话描述这个未成年人，
供后续视频编辑指令定位使用，格式如「画面左侧穿蓝色连衣裙的女孩，约6岁，正在挥手」。
如有多个未成年人，逐个描述用分号隔开。只输出描述本身。"""

BATCH = 8


def merge_hits(hit_times: list[float], interval: float) -> list[tuple[float, float]]:
    """相邻命中（间隔 ≤2×interval）合并为时段，时段末端 +interval。入参需已升序。"""
    if not hit_times:
        return []
    spans, start, prev = [], hit_times[0], hit_times[0]
    for t in hit_times[1:]:
        if t - prev <= 2 * interval:
            prev = t
        else:
            spans.append((start, prev + interval))
            start = prev = t
    spans.append((start, prev + interval))
    return spans


def _parse_hits(text: str) -> list[int]:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return []
    try:
        return [int(i) for i in json.loads(m.group())["hits"]]
    except Exception:
        return []


def annotate(video: Path, workdir: Path, provider: Provider, interval: float = 1.0) -> list[dict]:
    frames = media.extract_frames(video, workdir / "frames", interval=interval)
    hit_times: list[float] = []
    for i in range(0, len(frames), BATCH):
        batch = frames[i:i + BATCH]
        resp = provider.chat_vision(COARSE_PROMPT, [f.path for f in batch])
        for idx in _parse_hits(resp):  # hits 是批内索引（每批 prompt 独立，索引从 0 起）
            if 0 <= idx < len(batch):
                hit_times.append(batch[idx].t)
    timeline = []
    for start, end in merge_hits(sorted(hit_times), interval):
        mid = min(frames, key=lambda f: abs(f.t - (start + end) / 2))
        desc = provider.chat_vision(DETAIL_PROMPT, [mid.path]).strip()
        timeline.append({"start": start, "end": end,
                         "person_desc": desc, "sample_frame": str(mid.path),
                         "confirmed": False})
    (workdir / "timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    return timeline
