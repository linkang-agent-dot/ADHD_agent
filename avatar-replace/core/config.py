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

@dataclass
class PipelineCfg:
    frame_interval: float = 1.0
    segment_max: float = 15.0
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
        raise RuntimeError("缺少 ARK_API_KEY 环境变量（.env）")
    return Config(
        ark=ArkCfg(api_key=key, **raw["ark"]),
        pipeline=PipelineCfg(**raw.get("pipeline", {})),
        limits=LimitsCfg(**raw.get("limits", {})),
    )
