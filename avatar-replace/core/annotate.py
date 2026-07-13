"""VLM 两遍打轴：粗扫定位含未成年人的帧 → 合并为时段 → 细化取样帧描述外观。"""
import json
import re
from pathlib import Path

from core import media
from core.providers.base import Provider

COARSE_PROMPT = """你在做广告素材合规审查。下面按顺序给出视频抽帧（第0张对应索引0）。
找出画面中出现疑似未成年人（看起来不满18岁的真人）的帧。
只输出 JSON：{"hits": [命中的帧索引数组]}，没有则 {"hits": []}。"""

DETAIL_PROMPT = """这是广告视频某时段按时间顺序的抽帧。只输出 JSON，字段：
{"person": "一句话描述画面中疑似未成年人的外观与位置（多人用分号隔开），如「画面左侧穿蓝色连衣裙的女孩，约6岁」",
 "action": "一句话描述主要人物这段时间的动作/姿态变化与镜头运动（固定/推近/跟拍等），供后续用数字人形象重新生成该段画面。只写动作姿态与运镜，不要提及年龄、身份、身材或衣着",
 "orientation": "主要人物朝向，取 正面/背面/侧面 之一"}"""

BATCH = 8
DETAIL_FRAMES = 3  # 细化遍取样帧数（时段首/中/尾），单帧看不出动作变化


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


def _parse_detail(text: str) -> dict:
    """细化遍 JSON 解析；模型不守格式时整段文本兜底当 person 描述。"""
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            d = json.loads(m.group())
            return {"person": str(d.get("person", "")).strip(),
                    "action": str(d.get("action", "")).strip(),
                    "orientation": str(d.get("orientation", "正面")).strip() or "正面"}
        except Exception:
            pass
    return {"person": text.strip(), "action": "", "orientation": "正面"}


def _parse_hits(text: str) -> list[int]:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return []
    try:
        hits = json.loads(m.group())["hits"]
        if not isinstance(hits, list):  # 防 "hits":"12" 被逐字符迭代成 [1,2]
            return []
        return [int(i) for i in hits]
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
        # 首/中/尾各取最近帧（去重保序），让 VLM 看得出动作与运镜变化
        picks: list = []
        for t in (start, (start + end) / 2, end):
            f = min(frames, key=lambda fr: abs(fr.t - t))
            if f not in picks:
                picks.append(f)
        picks = picks[:DETAIL_FRAMES]
        detail = _parse_detail(
            provider.chat_vision(DETAIL_PROMPT, [f.path for f in picks]))
        mid = picks[len(picks) // 2]
        timeline.append({"start": start, "end": end,
                         "person_desc": detail["person"],
                         "action_desc": detail["action"],
                         "orientation": detail["orientation"],
                         "sample_frame": str(mid.path),
                         "confirmed": False})
    (workdir / "timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    return timeline
