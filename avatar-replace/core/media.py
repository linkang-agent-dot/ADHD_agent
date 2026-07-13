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
    # concat demuxer 相对路径是相对 list 文件目录解析的——list 与被拼文件不同目录时
    # 会拼错路径（2026-07-13 demo 实锤），一律转绝对路径
    lst = dst.with_suffix(".txt")
    lst.write_text("".join(f"file '{Path(p).resolve().as_posix()}'\n" for p in parts),
                   encoding="utf-8")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dst)])


def trim(src: Path, dst: Path, duration: float) -> None:
    """截取开头 duration 秒（重编码保精确；-an：音轨最终整条铺回原片）"""
    _run(["ffmpeg", "-y", "-i", str(src), "-t", f"{duration:.3f}", "-an",
          "-c:v", "libx264", "-crf", "18", "-preset", "fast",
          "-pix_fmt", "yuv420p", str(dst)])


def replace_audio(video: Path, audio_src: Path, dst: Path) -> None:
    """视频轨用 video，音轨整条用 audio_src 的（原片），时长以视频为准"""
    _run(["ffmpeg", "-y", "-i", str(video), "-i", str(audio_src),
          "-map", "0:v", "-map", "1:a?", "-c:v", "copy", "-c:a", "aac",
          "-shortest", str(dst)])


def normalize(src: Path, dst: Path, width: int, height: int, fps: float,
              retime_factor: float = 1.0) -> None:
    """把外来段（模型产出）重编码为与本地切段一致的参数。

    concat -c copy 要求各段编码参数完全一致；Seedance 产出段的分辨率/fps/
    编码参数与 cut_clip 不同，直接拼会花屏/时间戳错乱。统一 -an 去音轨
    （最终 replace_audio 会整条铺回原片音轨）。retime_factor≠1 时顺带变速对齐时长。
    ratio=adaptive 下模型输出应保持源画幅，scale 到源宽高不会形变；若真形变属模型问题。
    """
    vf = f"scale={width}:{height},fps={fps}"
    if abs(retime_factor - 1.0) > 1e-9:
        vf = f"setpts={retime_factor}*PTS," + vf
    _run(["ffmpeg", "-y", "-i", str(src), "-vf", vf, "-an",
          "-c:v", "libx264", "-crf", "18", "-preset", "fast",
          "-pix_fmt", "yuv420p", str(dst)])


def retime(src: Path, dst: Path, factor: float) -> None:
    """factor>1 拉长。仅动视频 PTS 后重编码（无音轨段用）"""
    _run(["ffmpeg", "-y", "-i", str(src), "-vf", f"setpts={factor}*PTS", "-an",
          "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p", str(dst)])
