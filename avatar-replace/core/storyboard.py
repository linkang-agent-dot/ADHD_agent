"""分镜复刻（2026-07-13 用户反馈定版）：让生成段贴原片的叙事、背景与镜头，而不是数字人干站着。

链路：VLM 读该段连续帧出结构化分镜（读图合规）→ 用换装后数字人图 i2i 出
起始/结束两张场景关键帧（数字人摆进原片背景与构图）→ i2v 首尾帧双锚点生成。
全程生成接口只见 CG 图与中性文本。
"""
import json
import re
from pathlib import Path

from core.providers.base import Provider

SEG_PROMPT = """这是广告视频同一个镜头内按时间顺序的抽帧。之后会用一个CG数字人复刻同样的画面，请输出 JSON：
{"scene": "背景环境与光线，一句话（如浅色卧室白墙暖光），不含人物",
 "shot": "起始构图：景别与主要人物在画面中的位置，一句话（如中景、人物居中，腰部以上入画）",
 "start_pose": "第一帧主要人物的姿势与朝向",
 "end_pose": "最后一帧主要人物的姿势与朝向（含景别变化，如镜头已推近到上半身特写）",
 "action": "主要人物从头到尾按顺序做了什么动作",
 "camera": "镜头运动（固定/推近/拉远/跟拍/摇移）",
 "others": "画面中其他人物的位置与姿态概述，无则空串"}
每个字段都是对整段的单一描述，禁止「第一帧…第二帧…」式逐帧枚举。
只描述姿态、动作与画面构成；不要提及年龄、身份、身材与衣着细节，措辞中性。只输出 JSON。"""

_DEFAULTS = {"scene": "", "shot": "", "start_pose": "", "end_pose": "",
             "action": "", "camera": "固定", "others": ""}
MAX_FRAMES = 6

KF_TMPL = (
    "保持画面中人物的外观、服装、发型完全不变，做以下修改："
    "1) 背景更换为：{scene}；2) 人物姿势与朝向改为：{pose}；3) 构图：{shot}。"
    "{others_clause}输出单幅完整画面（禁止多宫格/分镜拼图），"
    "画风与原图完全一致：写实CG数字人质感，不要卡通风格，光影自然贴合场景。"
)
OTHERS_CLAUSE = "4) 画面中另有其他人物：{others}，同样为CG数字人质感。"


def _parse(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    sb = dict(_DEFAULTS)
    if m:
        try:
            d = json.loads(m.group())
            for k in sb:
                v = str(d.get(k, "")).strip()
                if v:
                    sb[k] = v
        except Exception:
            pass
    return sb


def describe_segment(provider: Provider, frames_dir: Path, start: float, end: float,
                     interval: float = 1.0) -> dict:
    frames = sorted(frames_dir.glob("f_*.jpg"))
    hits = [p for i, p in enumerate(frames)
            if start - 1e-6 <= i * interval <= end + 1e-6]
    if len(hits) > MAX_FRAMES:  # 均匀抽稀，首尾必保
        step = (len(hits) - 1) / (MAX_FRAMES - 1)
        hits = [hits[round(i * step)] for i in range(MAX_FRAMES)]
    if not hits:
        return dict(_DEFAULTS)
    return _parse(provider.chat_vision(SEG_PROMPT, hits))


def _kf_prompt(sb: dict, pose: str) -> str:
    others = OTHERS_CLAUSE.format(others=sb["others"]) if sb["others"] else ""
    return KF_TMPL.format(scene=sb["scene"] or "与原图一致",
                          pose=pose, shot=sb["shot"] or "与原图一致",
                          others_clause=others)


def build_keyframes(provider: Provider, base_img: Path, sb: dict,
                    kf_dir: Path, name: str) -> tuple[Path, Path | None]:
    """起始/结束两张场景关键帧（幂等）。end_pose 缺失或与起始相同则不出尾帧。"""
    kf_dir.mkdir(parents=True, exist_ok=True)
    kf_a = kf_dir / f"{name}_a.jpg"
    if not kf_a.exists():
        provider.edit_image(_kf_prompt(sb, sb["start_pose"] or "自然站立面向镜头"),
                            base_img, kf_a)
    if not sb["end_pose"] or sb["end_pose"] == sb["start_pose"]:
        return kf_a, None
    kf_b = kf_dir / f"{name}_b.jpg"
    if not kf_b.exists():
        # 从起始关键帧续改而非从形象图重出：人物/场景一致性优先
        provider.edit_image(_kf_prompt(sb, sb["end_pose"]), kf_a, kf_b)
    return kf_a, kf_b
