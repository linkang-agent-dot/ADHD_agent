"""切段规划 + 执行。

四原则：只向外吸附镜头切点、绝不截掉命中区、全片无缝覆盖、无零长段。
"""
from pathlib import Path

from core import media

_EPS = 1e-6
# 段间合并容差：ffmpeg 切割用毫秒精度（%.3f），亚 10ms 的间隙切不出有意义的 keep 段
_MERGE_EPS = 0.01


def _snap_out(t: float, cuts: list[float], tolerance: float, direction: int) -> float:
    """只向外吸附镜头切点（direction=-1 起点向前 / +1 终点向后）。

    向内吸会截掉命中区，故起点只在 [t-tolerance, t] 找、终点只在 [t, t+tolerance] 找；
    多个候选取离原点最远的（min/max），尽量整镜头包住。
    """
    if direction < 0:
        cand = [c for c in cuts if t - tolerance <= c <= t]
        return min(cand) if cand else t
    cand = [c for c in cuts if t <= c <= t + tolerance]
    return max(cand) if cand else t


def plan_segments(timeline: list[dict], duration: float, scene_cuts: list[float],
                  buffer: float, tolerance: float, segment_max: float) -> list[dict]:
    """把 confirmed 命中时段变成覆盖全片、首尾相接的分段计划。

    返回 [{start, end, mode: keep|replace, desc(仅 replace)}]。
    """
    # 1) 取 confirmed 时段：外扩 buffer → clamp → 只向外吸附切点
    spans = []
    for item in timeline:
        if not item.get("confirmed"):
            continue
        s = _snap_out(max(0.0, item["start"] - buffer), scene_cuts, tolerance, -1)
        e = _snap_out(min(duration, item["end"] + buffer), scene_cuts, tolerance, +1)
        s = max(s, 0.0)
        e = min(e, duration)
        if e - s <= _EPS:  # 退化时段（零长/负长）不产生零长 replace 段
            continue
        spans.append([s, e, item["person_desc"],
                      item.get("action_desc", ""), item.get("orientation", "")])
    spans.sort()

    # 2) 重叠/相接合并（desc/action 去重拼接，orientation 取先出现的）
    merged: list[list] = []
    for s, e, d, a, o in spans:
        if merged and s <= merged[-1][1] + _MERGE_EPS:
            merged[-1][1] = max(merged[-1][1], e)
            # 按分号切分后判等去重：子串包含判定会把"男孩"误吞进"红衣男孩"
            if d not in merged[-1][2].split("；"):
                merged[-1][2] = merged[-1][2] + "；" + d
            if a and a not in merged[-1][3].split("；"):
                merged[-1][3] = (merged[-1][3] + "；" + a) if merged[-1][3] else a
        else:
            merged.append([s, e, d, a, o])

    # 3) 铺全片：间隙补 keep，replace 超长 n 等分
    segs: list[dict] = []
    cursor = 0.0
    _INNER_MARGIN = 0.75  # 离边太近的切点不切，避免产出碎段
    for s, e, d, a, o in merged:
        if s > cursor + _EPS:
            segs.append({"start": cursor, "end": s, "mode": "keep"})
        else:
            s = cursor  # 与上一段贴合，防负长/微缝
        # 替换区内部先按镜头切点分割——一段混两个镜头会让分镜/生成画面穿帮
        # （2026-07-13 实锤：跨切点段被 Seedream 画成多宫格）
        inner = sorted(c for c in scene_cuts if s + _INNER_MARGIN < c < e - _INNER_MARGIN)
        bounds = [s] + inner + [e]
        for shot_s, shot_e in zip(bounds, bounds[1:]):
            n = 1
            while (shot_e - shot_s) / n > segment_max:
                n += 1
            step = (shot_e - shot_s) / n
            for i in range(n):
                # 末份终点直接取 shot_e，避免浮点漂移留缝
                seg_end = shot_e if i == n - 1 else shot_s + (i + 1) * step
                segs.append({"start": shot_s + i * step, "end": seg_end,
                             "mode": "replace", "desc": d,
                             "action": a, "orient": o})
        cursor = e

    # 4) 收尾：补片尾 keep；已到片尾则把浮点残差归到最后一段。显式防空列表。
    if duration - cursor > _EPS:
        segs.append({"start": cursor, "end": duration, "mode": "keep"})
    elif segs:
        segs[-1]["end"] = duration
    return segs


def execute_cut(video: Path, segs: list[dict], workdir: Path) -> list[dict]:
    """按计划逐段切割到 workdir/segs/{i:03d}_{mode}.mp4，返回带 path 的段列表。"""
    seg_dir = Path(workdir) / "segs"
    seg_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for i, s in enumerate(segs):
        p = seg_dir / f"{i:03d}_{s['mode']}.mp4"
        media.cut_clip(video, p, s["start"], s["end"])
        out.append({**s, "path": p})
    return out
