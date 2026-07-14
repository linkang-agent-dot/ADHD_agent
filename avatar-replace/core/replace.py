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

# 多参考图模式（2026-07-14 定版主路径）：参考图按 content 顺序以"图1/图2..."指代。
# 用户明确要求强调三不变：服装不变、镜头不变、分镜内容不变（不得增删改编）
REFS_TMPL = (
    "生成一段竖版视频，严格按以下分镜复刻，不得增删情节或自行改编："
    "{shot_clause}画面中的CG数字人{action}。"
    "镜头{camera}，全程严格保持这一镜头运动方式，不要额外运镜。"
    "人物形象、发型严格以{avatar_clause}的数字人为准；"
    "服装必须与参考图上的完全一致，不得更换款式、颜色，不得增减衣物；体态柔和自然。"
    "场景、光线以{scene_clause}为准并全程保持不变。{others_clause}"
    "写实CG质感，动作自然连贯。"
)


def build_prompt(sb: dict, has_last: bool) -> str:
    return PROMPT_TMPL.format(
        anchor=ANCHOR_BOTH if has_last else ANCHOR_FIRST,
        action=sb.get("action") or DEFAULT_ACTION,
        camera=sb.get("camera") or DEFAULT_CAMERA)


def build_refs_prompt(sb: dict, n_avatar: int, has_scene: bool) -> str:
    avatar = "图1" if n_avatar == 1 else "图1（正面）与图2（背面）"
    scene = f"图{n_avatar + 1}" if has_scene else "分镜描述"
    shot = f"构图为{sb['shot']}，" if sb.get("shot") else ""
    others = (f"画面中另有其他人物：{sb['others']}，同样为CG数字人质感。"
              if sb.get("others") else "")
    return REFS_TMPL.format(shot_clause=shot,
                            action=sb.get("action") or DEFAULT_ACTION,
                            camera=sb.get("camera") or DEFAULT_CAMERA,
                            avatar_clause=avatar, scene_clause=scene,
                            others_clause=others)


def replace_segment_refs(provider: Provider, seg_path: Path, sb: dict,
                         avatar_refs: list[Path], scene_ref: Path | None,
                         out_dir: Path, expect_dur: float,
                         ratio: str | None = None) -> Path:
    """多参考图模式：人物形象图+空镜头场景图+脚本，Seedance 自主成镜。

    ratio 必须传源片档位——此模式 adaptive 不跟随参考图（实测出 1:1，
    拼回被拉伸变形）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / seg_path.name.replace("_replace", "_gen")
    out = out_dir / seg_path.name.replace("_replace", "_replaced")
    # prompt 以"图1=正面/图2=背面"指代，参考图顺序必须正面在前
    # （换装产物按文件名字母序是 back 在前，直接切片会张冠李戴）
    fronts = [p for p in avatar_refs if p.stem.lower().startswith("front")]
    backs = [p for p in avatar_refs if p.stem.lower().startswith("back")]
    avatars = (fronts[:1] + backs[:1]) or list(avatar_refs[:2])
    refs = avatars + ([scene_ref] if scene_ref else [])
    provider.generate_ref_clip(
        build_refs_prompt(sb, len(avatars), scene_ref is not None), refs, raw,
        ratio=ratio)
    return _fit_duration(raw, out, expect_dur)


def _fit_duration(raw: Path, out: Path, expect_dur: float) -> Path:
    actual = media.probe(raw).duration
    if expect_dur > 0 and actual > expect_dur * 1.02:
        media.trim(raw, out, expect_dur)
    else:
        shutil.copy(raw, out)
    return out


def replace_segment(provider: Provider, seg_path: Path, sb: dict,
                    kf_start: Path | None, kf_end: Path | None,
                    out_dir: Path, expect_dur: float) -> Path:
    """首尾帧锚点模式（备选，gen_mode=keyframes 时启用）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / seg_path.name.replace("_replace", "_gen")
    out = out_dir / seg_path.name.replace("_replace", "_replaced")
    provider.generate_clip(build_prompt(sb, kf_end is not None),
                           kf_start, raw, last_frame=kf_end)
    return _fit_duration(raw, out, expect_dur)
