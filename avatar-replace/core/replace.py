"""段替换（分镜复刻版，2026-07-13）：场景关键帧作首尾锚点 + 分镜动作描述 i2v。

不把原片段喂给模型——Seedance 公开 API 禁真人视频输入（video_edit 路径实测撞
InputVideoSensitiveContentDetected），原片只在打轴/分镜时被 VLM 读帧。
i2v 产出约 5s 且不受 duration 参数控制：超出目标时长只裁不拉，
不足 2% 内交给 stitch 变速兜底。
"""
import shutil
from pathlib import Path

from core import media
from core.providers.base import Provider

PROMPT_TMPL = (
    "{anchor}画面中的CG数字人{action}。镜头{camera}。"
    "人物外观、服装、发型与首帧保持一致，体态柔和自然，"
    "背景与首帧保持一致，动作自然连贯。"
)
ANCHOR_BOTH = "视频从首帧画面开始，到尾帧画面结束："
ANCHOR_FIRST = "以首帧画面为起点："
DEFAULT_ACTION = "自然站立展示，身体轻微自然晃动"
DEFAULT_CAMERA = "固定"


def build_prompt(sb: dict, has_last: bool) -> str:
    return PROMPT_TMPL.format(
        anchor=ANCHOR_BOTH if has_last else ANCHOR_FIRST,
        action=sb.get("action") or DEFAULT_ACTION,
        camera=sb.get("camera") or DEFAULT_CAMERA)


def replace_segment(provider: Provider, seg_path: Path, sb: dict,
                    kf_start: Path | None, kf_end: Path | None,
                    out_dir: Path, expect_dur: float) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / seg_path.name.replace("_replace", "_gen")
    out = out_dir / seg_path.name.replace("_replace", "_replaced")
    provider.generate_clip(build_prompt(sb, kf_end is not None),
                           kf_start, raw, last_frame=kf_end)
    actual = media.probe(raw).duration
    if expect_dur > 0 and actual > expect_dur * 1.02:
        media.trim(raw, out, expect_dur)
    else:
        shutil.copy(raw, out)
    return out
