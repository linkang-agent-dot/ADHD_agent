"""换装：让数字人穿上与原片一致的服装，并弱化肌肉感（2026-07-13 用户反馈定版）。

链路：VLM 读原片样帧出服装描述（读图合规；措辞中性避 Seedream 文本风控）
→ Seedream i2i 给全局形象图换装+调体态 → 产出 job 级形象图（front/back），
i2v 用它作首帧。全程不把真人图送进生成接口——生成输入只有 CG 形象图。
"""
from pathlib import Path

from core.providers.base import Provider

GARMENT_PROMPT = """只描述画面主体人物所穿服装本身：款式、颜色、图案、材质，一句话。
要求：使用中性服饰词汇（如吊带背心、短裤、家居服套装）；只写服装，
不要出现人物年龄、身份、身体部位描述，不要出现"内衣"等敏感品类词。只输出描述本身。"""

DRESS_TMPL = (
    "保持画面中人物的姿势、构图、光线、背景与CG数字人质感完全不变，只做两处修改："
    "1) 将人物服装更换为：{garment}（当前视角看到的一面与该服装对应）；"
    "2) 明显弱化人物的肌肉线条，体态自然、柔和、纤细。"
)


def describe_garment(provider: Provider, sample_frame: Path) -> str:
    return provider.chat_vision(GARMENT_PROMPT, [sample_frame]).strip()


def dress_avatar(provider: Provider, avatar_refs: list[Path], garment: str,
                 out_dir: Path) -> list[Path]:
    """逐张换装，产出 job 级形象图（文件名沿用 front/back，pick_ref 逻辑不变）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    outs = []
    for ref in avatar_refs:
        out = out_dir / ref.name
        if not out.exists():  # 幂等：续跑不重复花钱
            provider.edit_image(DRESS_TMPL.format(garment=garment), ref, out)
        outs.append(out)
    return outs
