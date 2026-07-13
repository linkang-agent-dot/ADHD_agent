"""字幕保留：原片硬字幕在替换段上会随画面一起被换掉，重烧回去（2026-07-13 demo 链路固化）。

- 文本与时序来源：打轴已抽的 1fps 帧，VLM 逐帧 OCR 原文（帧时刻=秒级时序，够用；
  硬字幕抠不出来——它背后就是被替换的人）。
- 烧录：ffmpeg drawtext，样式取自 demo 定稿（雅黑粗体白字黑边口播行 + 底部半透明声明行）。
- 三个工程坑规避：字体拷进工作目录用相对名（盘符冒号是 filtergraph 分隔符）、
  文案走 utf-8 textfile 不内联、subprocess cwd=工作目录。
"""
import json
import re
import shutil
from pathlib import Path

from core import media
from core.providers.base import Provider

OCR_PROMPT = """下面按时间顺序给出竖版广告视频的抽帧（批内索引从0起）。逐帧读出画面上烧录的字幕文字，只输出 JSON：
{"frames": [{"i": 0, "caption": "画面中下部的主字幕/口播字幕原文，无则空串", "bottom": "画面最底部的固定小字声明原文，无则空串"}]}
要求逐字保留原文（含标点），不要翻译、不要概括、不要把商品图案上的文字当字幕。"""

BATCH = 8
FONT_SRC = Path("C:/Windows/Fonts/msyhbd.ttc")

# demo 定稿样式（1080x1920 竖版）
CAP_STYLE = dict(fontsize=56, y=1380, border=7)
BOT_STYLE = dict(fontsize=38, border=2)
BOT_Y = (1788, 1852)


def _parse_ocr(text: str) -> list[dict]:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return []
    try:
        frames = json.loads(m.group()).get("frames", [])
        return [f for f in frames if isinstance(f, dict)]
    except Exception:
        return []


def ocr_spans(provider: Provider, frames_dir: Path, spans: list[tuple[float, float]],
              interval: float = 1.0) -> dict:
    """对落在替换时段内的帧跑 OCR，返回 {"captions": [[t0,t1,text]], "bottom": str}。"""
    frames = sorted(frames_dir.glob("f_*.jpg"))
    hits = [(i * interval, p) for i, p in enumerate(frames)
            if any(a - 1e-6 <= i * interval <= b + 1e-6 for a, b in spans)]
    per_frame: list[tuple[float, str, str]] = []  # (t, caption, bottom)
    for k in range(0, len(hits), BATCH):
        batch = hits[k:k + BATCH]
        parsed = _parse_ocr(provider.chat_vision(OCR_PROMPT, [p for _, p in batch]))
        got = {int(f.get("i", -1)): f for f in parsed}
        for j, (t, _) in enumerate(batch):
            f = got.get(j, {})
            per_frame.append((t, str(f.get("caption", "")).strip(),
                              str(f.get("bottom", "")).strip()))
    # 相邻同文合并为区间；区间终点=下一变化帧时刻（末帧+interval，并夹回所属 span 内）
    captions: list[list] = []
    for t, cap, _ in per_frame:
        if not cap:
            continue
        if captions and captions[-1][2] == cap and t - captions[-1][1] <= interval + 1e-6:
            captions[-1][1] = t + interval
        else:
            captions.append([t, t + interval, cap])
    for c in captions:
        for a, b in spans:
            if a - 1e-6 <= c[0] <= b + 1e-6:
                c[1] = min(c[1], b)
                break
    bottoms = [b for _, _, b in per_frame if b]
    bottom = max(set(bottoms), key=bottoms.count) if bottoms else ""
    return {"captions": [tuple(c) for c in captions], "bottom": bottom}


def _wrap(text: str, width: int = 15) -> str:
    """长口播句换行：fontsize 56 × 15字 ≈ 840px，1080 宽内留边。OCR 可能把同屏多行并成一句。"""
    return "\n".join(text[i:i + width] for i in range(0, len(text), width))


def _drawtext(textfile: str, fontsize: int, y, border: int, alpha: str,
              start: float, end: float) -> str:
    color = f"white@{alpha}" if alpha else "white"
    # between 两端闭区间：相邻字幕在整秒边界会同帧叠印，尾端退一帧变半开
    return (f"drawtext=fontfile=font.ttc:textfile={textfile}:fontsize={fontsize}:"
            f"fontcolor={color}:borderw={border}:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:enable='between(t,{start:.3f},{end - 0.04:.3f})'")


def burn(video: Path, out: Path, ocr: dict, spans: list[tuple[float, float]],
         workdir: Path) -> Path:
    """把 OCR 结果烧回替换段：口播行按区间变、底部声明整段常显。keep 段自带原字幕不动。"""
    workdir.mkdir(parents=True, exist_ok=True)
    if not FONT_SRC.exists():
        raise RuntimeError(f"缺少字体 {FONT_SRC}")
    shutil.copy(FONT_SRC, workdir / "font.ttc")
    filters = []
    for k, (t0, t1, text) in enumerate(ocr.get("captions", [])):
        (workdir / f"cap{k}.txt").write_text(_wrap(text), encoding="utf-8")
        filters.append(_drawtext(f"cap{k}.txt", CAP_STYLE["fontsize"], CAP_STYLE["y"],
                                 CAP_STYLE["border"], "", t0, t1))
    bottom = ocr.get("bottom", "")
    if bottom:
        lines = [ln.strip() for ln in re.split(r"[/\n]", bottom) if ln.strip()][:2]
        for k, ln in enumerate(lines):
            (workdir / f"bot{k}.txt").write_text(ln, encoding="utf-8")
            for a, b in spans:
                filters.append(_drawtext(f"bot{k}.txt", BOT_STYLE["fontsize"], BOT_Y[k],
                                         BOT_STYLE["border"], "0.75", a, b))
    if not filters:
        shutil.copy(video, out)
        return out
    media._run(["ffmpeg", "-y", "-i", str(Path(video).resolve()),
                "-vf", ",".join(filters), "-c:v", "libx264", "-crf", "18",
                "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy",
                str(Path(out).resolve())], cwd=workdir)
    return out
