"""段替换：构造替换 prompt，调 Provider.video_edit 生成替换段。"""
from pathlib import Path

from core.providers.base import Provider

PROMPT_TMPL = (
    "将视频1中的{desc}替换为图片1中的数字人形象，"
    "数字人的外观、服装、比例严格以参考图片为准。"
    "视频中其余人物、场景、光线、运镜、动作节奏完全保持不变，"
    "替换后人物的动作与原人物动作保持一致。"
)


def build_prompt(person_desc: str) -> str:
    return PROMPT_TMPL.format(desc=person_desc)


def replace_segment(provider: Provider, seg_path: Path, person_desc: str,
                    avatar_refs: list[Path], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / seg_path.name.replace("_replace", "_replaced")
    return provider.video_edit(build_prompt(person_desc), seg_path, avatar_refs, out)
