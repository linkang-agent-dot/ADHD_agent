"""ffmpeg/ffprobe 底层封装：探测、抽帧、切点检测、剪切、拼接、换音轨、变速。"""
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MediaInfo:
    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool


@dataclass
class Frame:
    t: float
    path: Path


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r


def probe(path: Path | str) -> MediaInfo:
    r = _run(["ffprobe", "-v", "quiet", "-print_format", "json",
              "-show_format", "-show_streams", str(path)])
    d = json.loads(r.stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = (v.get("avg_frame_rate") or "25/1").split("/")
    return MediaInfo(
        duration=float(d["format"]["duration"]),
        width=int(v["width"]), height=int(v["height"]),
        fps=float(num) / float(den or 1),
        has_audio=any(s["codec_type"] == "audio" for s in d["streams"]))


def extract_frames(path: Path | str, out_dir: Path, interval: float = 1.0) -> list[Frame]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("f_*.jpg"):  # 续跑复用目录时残留旧帧会污染帧列表
        stale.unlink()
    _run(["ffmpeg", "-y", "-i", str(path), "-vf", f"fps=1/{interval}",
          "-q:v", "3", str(out_dir / "f_%05d.jpg")])
    frames = sorted(out_dir.glob("f_*.jpg"))
    return [Frame(t=i * interval, path=p) for i, p in enumerate(frames)]


def scene_cuts(path: Path | str, threshold: float = 0.3) -> list[float]:
    r = subprocess.run(
        ["ffmpeg", "-i", str(path), "-vf", f"select='gt(scene,{threshold})',showinfo",
         "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    cuts = [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    if r.returncode != 0 and not cuts:  # 无切点是正常结果，但坏输入不能静默当"无切点"
        raise RuntimeError(f"scene_cuts failed on {path}\n{r.stderr[-1000:]}")
    return cuts


def cut_clip(src: Path | str, dst: Path, start: float, end: float) -> None:
    # 重编码保帧精确；统一编码参数便于后续 concat
    _run(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(src),
          "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
          "-c:a", "aac", str(dst)])


def concat(parts: list[Path], dst: Path) -> None:
    lst = dst.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dst)])


def replace_audio(video: Path, audio_src: Path, dst: Path) -> None:
    """视频轨用 video，音轨整条用 audio_src 的（原片），时长以视频为准"""
    _run(["ffmpeg", "-y", "-i", str(video), "-i", str(audio_src),
          "-map", "0:v", "-map", "1:a?", "-c:v", "copy", "-c:a", "aac",
          "-shortest", str(dst)])


def retime(src: Path, dst: Path, factor: float) -> None:
    """factor>1 拉长。仅动视频 PTS 后重编码（无音轨段用）"""
    _run(["ffmpeg", "-y", "-i", str(src), "-vf", f"setpts={factor}*PTS", "-an",
          "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", str(dst)])
