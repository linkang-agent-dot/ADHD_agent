"""按「已知时间轴」烧字幕（post_subtitle.py 的无音频版）。

post_subtitle.py 走 whisper 词级对齐，前提是成片有音轨。
本脚本用于 generate_audio=false 的纯画面成片：时间轴由打轴卡直接给出，
不做任何 ASR，确定性 100%。

时间轴 json 格式：
  {"style": {...可选覆盖...},
   "lines": [{"s": 0.0, "e": 1.3, "t": "身体好看的人"}, ...]}

用法：
  python scripts/burn_ass_timeline.py --video in.mp4 --timeline t.json --out out.mp4

Windows 坑（沿用 post_subtitle.py 的解法）：
  - ffmpeg 的 subtitles filter 里盘符冒号会被当分隔符 → 用相对文件名 + cwd 切到该目录
  - 中文长句 libass 不自动折行 → _wrap_cjk 按字数硬折
"""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

DEFAULT_STYLE = {
    "font": "Microsoft YaHei",
    "size": 54,
    "bold": 1,
    "primary": "&H00FFFFFF",   # 白字
    "outline_col": "&H00000000",  # 黑边
    "outline": 3,
    "shadow": 0,
    "margin_v": 120,           # 距底部像素
    "wrap_chars": 13,          # 每行最多字数（CJK）
}


def _ts(sec: float) -> str:
    """秒 → ASS 时间戳 h:mm:ss.cc"""
    if sec < 0:
        sec = 0.0
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _wrap_cjk(text: str, n: int) -> str:
    """中文按 n 字/行硬折，优先在标点后断行（libass 不会自己折 CJK）。"""
    if len(text) <= n:
        return text
    puncts = "，。、；：？！,.;:?!"
    out, line = [], ""
    for ch in text:
        line += ch
        if len(line) >= n:
            cut = len(line)
            for i in range(len(line) - 1, max(len(line) - 4, 0), -1):
                if line[i - 1] in puncts:
                    cut = i
                    break
            out.append(line[:cut])
            line = line[cut:]
    if line:
        out.append(line)
    return r"\N".join(out)


def build_ass(lines: list, style: dict, path: Path) -> None:
    st = {**DEFAULT_STYLE, **(style or {})}
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Def,{st['font']},{st['size']},{st['primary']},{st['outline_col']},&H00000000,{st['bold']},0,1,{st['outline']},{st['shadow']},2,40,40,{st['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    body = []
    for ln in lines:
        txt = _wrap_cjk(str(ln["t"]).strip(), st["wrap_chars"])
        # 相邻整秒边界同帧叠印 → 尾端退 0.04s（post_subtitle.py 同款修正）
        body.append(f"Dialogue: 0,{_ts(float(ln['s']))},{_ts(float(ln['e']) - 0.04)},Def,,0,0,0,,{txt}")
    path.write_text(head + "\n".join(body) + "\n", encoding="utf-8")


def burn(video: Path, ass: Path, out: Path) -> None:
    """ffmpeg 烧录。ass 用相对名 + cwd=工作目录，规避 Windows 盘符冒号地狱。"""
    work = ass.parent
    tmp_out = work / "_burned.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video.resolve()),
           "-vf", f"subtitles={ass.name}",
           "-c:v", "libx264", "-crf", "18", "-preset", "medium",
           "-pix_fmt", "yuv420p"]
    # 有音轨就原样复制，没有就不加音频流
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                            "-show_entries", "stream=codec_type", "-of", "csv=p=0",
                            str(video.resolve())], capture_output=True, text=True)
    cmd += ["-c:a", "copy"] if probe.stdout.strip() else ["-an"]
    cmd += [str(tmp_out)]
    subprocess.run(cmd, cwd=str(work), check=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp_out), str(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--keep-ass", default="")
    args = ap.parse_args()

    data = json.loads(Path(args.timeline).read_text(encoding="utf-8"))
    lines = data["lines"]
    with tempfile.TemporaryDirectory() as td:
        ass = Path(td) / "sub.ass"
        build_ass(lines, data.get("style"), ass)
        if args.keep_ass:
            shutil.copy(str(ass), args.keep_ass)
        burn(Path(args.video), ass, Path(args.out))
    print(f"[burn] {len(lines)} 条字幕 → {args.out}")


if __name__ == "__main__":
    main()
