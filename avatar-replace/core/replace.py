"""段替换（i2v 架构，2026-07-13 定版）：数字人形象图作首帧 + 动作/运镜描述生成视频段。

不把原片段喂给模型——Seedance 公开 API 禁真人视频输入（video_edit 路径实测撞
InputVideoSensitiveContentDetected），原片只在打轴时被 VLM 读帧。生成段与原片的
画风断层已由业务验收（2026-07-13 demo 过审）。i2v 产出约 5s 且不受 duration 参数
控制：超出目标时长只裁不拉，不足部分交给 stitch 的变速兜底。
"""
import shutil
from pathlib import Path

from core import media
from core.providers.base import Provider

PROMPT_TMPL = (
    "以这张图为首帧生成视频：画面中的CG数字人{action}。"
    "人物外观、服装、发型与首帧完全一致，背景与首帧保持一致，"
    "动作自然连贯，画面中不出现其他人物。"
)
DEFAULT_ACTION = "自然站立展示，身体轻微自然晃动，镜头固定"


def build_prompt(action_desc: str) -> str:
    return PROMPT_TMPL.format(action=action_desc or DEFAULT_ACTION)


def pick_ref(avatar_refs: list[Path], orientation: str) -> Path | None:
    """按原片人物朝向选形象图：背面时段优先 back*，其余 front* 优先，兜底第一张。"""
    if not avatar_refs:
        return None
    want = "back" if "背" in (orientation or "") else "front"
    for p in avatar_refs:
        if p.stem.lower().startswith(want):
            return p
    return avatar_refs[0]


def replace_segment(provider: Provider, seg_path: Path, action_desc: str,
                    orientation: str, avatar_refs: list[Path], out_dir: Path,
                    expect_dur: float) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / seg_path.name.replace("_replace", "_gen")
    out = out_dir / seg_path.name.replace("_replace", "_replaced")
    provider.generate_clip(build_prompt(action_desc),
                           pick_ref(avatar_refs, orientation), raw)
    actual = media.probe(raw).duration
    if expect_dur > 0 and actual > expect_dur * 1.02:
        media.trim(raw, out, expect_dur)
    else:
        shutil.copy(raw, out)
    return out
