import os
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class ArkCfg:
    base_url: str
    vlm_model: str
    video_model: str
    api_key: str = ""
    image_model: str = ""            # Seedream 图生图（换装/调体态），空=禁用 wardrobe
    # 视频生成 body 顶层参数（Seedance 2.0 契约，Task 11 核对）
    video_resolution: str = "720p"   # 480p/720p/1080p（1080p 仅标准版）
    video_ratio: str = "adaptive"    # adaptive=跟随输入比例
    video_duration: int = -1         # -1=模型自适应（4-15s）
    generate_audio: bool = False     # 拼回用原片音轨，生成音频会被丢弃，默认关省费
    watermark: bool = False

@dataclass
class PipelineCfg:
    frame_interval: float = 1.0
    segment_max: float = 5.0   # i2v 产出约 5s，段≤5s 只裁不拉伸
    gen_mode: str = "refs"     # refs=多参考图自主成镜(2026-07-14主路径) / keyframes=首尾帧锚点(备选)
    buffer: float = 0.5
    scene_align_tolerance: float = 2.0
    duration_drift_pct: float = 2.0

@dataclass
class LimitsCfg:
    max_video_seconds: int = 60
    max_video_mb: int = 200

@dataclass
class Config:
    ark: ArkCfg
    pipeline: PipelineCfg = field(default_factory=PipelineCfg)
    limits: LimitsCfg = field(default_factory=LimitsCfg)

def load_config(path: Path | str = "config.yaml", require_key: bool = False) -> Config:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    key = os.environ.get("ARK_API_KEY", "")
    if require_key and not key:
        raise RuntimeError(
            "缺少 ARK_API_KEY 环境变量（CLI 不自动读 .env，需先 set/export）")
    return Config(
        ark=ArkCfg(api_key=key, **raw["ark"]),
        pipeline=PipelineCfg(**raw.get("pipeline", {})),
        limits=LimitsCfg(**raw.get("limits", {})),
    )
