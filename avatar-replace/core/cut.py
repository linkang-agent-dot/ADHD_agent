"""切段规划 + 执行。

四原则：只向外吸附镜头切点、绝不截掉命中区、全片无缝覆盖、无零长段。
"""
from pathlib import Path

from core import media

_EPS = 1e-6


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
        spans.append([s, e, item["person_desc"]])
    spans.sort()

    # 2) 重叠/相接合并（desc 去重拼接）
    merged: list[list] = []
    for s, e, d in spans:
        if merged and s <= merged[-1][1] + _EPS:
            merged[-1][1] = max(merged[-1][1], e)
            if d not in merged[-1][2]:
                merged[-1][2] = merged[-1][2] + "；" + d
        else:
            merged.append([s, e, d])

    # 3) 铺全片：间隙补 keep，replace 超长 n 等分
    segs: list[dict] = []
    cursor = 0.0
    for s, e, d in merged:
        if s > cursor + _EPS:
            segs.append({"start": cursor, "end": s, "mode": "keep"})
        else:
            s = cursor  # 与上一段贴合，防负长/微缝
        n = 1
        while (e - s) / n > segment_max:
            n += 1
        step = (e - s) / n
        for i in range(n):
            # 末份终点直接取 e，避免 s+n*step 浮点漂移在 e 处留缝
            seg_end = e if i == n - 1 else s + (i + 1) * step
            segs.append({"start": s + i * step, "end": seg_end,
                         "mode": "replace", "desc": d})
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
