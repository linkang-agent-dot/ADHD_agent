"""后期烧字幕：用准确台词(来自 t2v_E222.json 每条 prompt 的「」)+whisper词级时间轴 → 生成带货风格ASS → ffmpeg烧。
台词文本以 json 为准(100%准)，whisper 只提供时间轴；difflib 容错对齐修正 ASR 错字。

用法:
  python scripts/post_subtitle.py --video E:/222/t2v_成片_v2/t2v_06.mp4 --json prompts/t2v_E222.json --id 06 --out E:/222/t2v_成片_v2_字幕/t2v_06.mp4
  # 或直接给台词: --lines "句1;句2;句3"
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def lines_from_json(json_path: Path, cid: str) -> list:
    d = json.loads(json_path.read_text(encoding="utf-8"))
    clip = next(c for c in d["clips"] if c["id"] == cid)
    # 台词=prompt 里所有「」中的内容，按出现顺序
    return re.findall(r"「(.+?)」", clip["prompt"])


def whisper_words(wav: Path) -> list:
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True)
    segs, _ = m.transcribe(str(wav), language="zh", word_timestamps=True)
    words = []
    for s in segs:
        for w in (s.words or []):
            words.append((w.word.strip(), w.start, w.end))
    return words


def norm(s: str) -> str:
    # 去标点/空格，只留可对齐的字符
    return re.sub(r"[，。、！？「」,.!?…\s~]", "", s)


def align_lines(lines: list, words: list) -> list:
    """把每句台词对齐到 whisper 词流，返回 [(line, start, end)]。"""
    # 源字符流 S + 每个字符的时间
    S, char_t = [], []
    for w, st, en in words:
        wn = norm(w)
        for i, ch in enumerate(wn):
            S.append(ch)
            # 词内字符时间线性插值
            char_t.append(st + (en - st) * (i / max(1, len(wn))))
    S = "".join(S)
    # 目标字符流 T + 每字符属于哪句
    T, char_line = [], []
    for li, ln in enumerate(lines):
        for ch in norm(ln):
            T.append(ch); char_line.append(li)
    T = "".join(T)
    sm = difflib.SequenceMatcher(None, T, S, autojunk=False)
    # 每句台词在 S 中命中的时间点集合
    line_times = {i: [] for i in range(len(lines))}
    for a, b, size in sm.get_matching_blocks():
        for k in range(size):
            li = char_line[a + k]
            line_times[li].append(char_t[b + k])
    out = []
    prev_end = 0.0
    for i, ln in enumerate(lines):
        ts = line_times[i]
        if ts:
            start, end = min(ts), max(ts)
        else:  # 没对上→接在上一句后按字数估
            start = prev_end + 0.1
            end = start + 0.35 * len(norm(ln))
        out.append((ln, start, end))
        prev_end = end
    return out


def to_ass_time(t: float) -> str:
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(timed: list, out_ass: Path, w=720, h=1280):
    # 带货风格：微软雅黑粗体、白字、黑边、底部居中
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Def,Microsoft YaHei,54,&H00FFFFFF,&H00000000,&H00000000,1,1,3,0,2,40,40,90,134

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for ln, st, en in timed:
        if en <= st:
            en = st + 0.8
        lines.append(f"Dialogue: 0,{to_ass_time(st)},{to_ass_time(en)},Def,,0,0,0,,{_wrap_cjk(ln)}")
    out_ass.write_text("\n".join(lines), encoding="utf-8")


def _wrap_cjk(text: str, max_chars: int = 13) -> str:
    # libass 对无空格中文不自动换行，手动按 max_chars 折行（优先在标点后断），\N 硬换行
    if len(text) <= max_chars:
        return text
    puncts = "，。！？、；：,.!?;: "
    out, cur = [], ""
    for ch in text:
        cur += ch
        if len(cur) >= max_chars:
            # 回找最近标点断行（避免标点悬挂行首）
            cut = -1
            for i in range(len(cur) - 1, max(0, len(cur) - 7), -1):
                if cur[i] in puncts:
                    cut = i + 1
                    break
            if cut > 0 and cut < len(cur):
                out.append(cur[:cut])
                cur = cur[cut:]
            else:
                out.append(cur)
                cur = ""
    if cur:
        out.append(cur)
    return "\\N".join(s.strip() for s in out if s.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--json", default=str(ROOT / "prompts" / "t2v_E222.json"))
    ap.add_argument("--id", default="")
    ap.add_argument("--lines", default="", help="分号分隔台词，覆盖 --json/--id")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    video = Path(args.video)
    if args.lines:
        lines = [x for x in args.lines.split(";") if x.strip()]
    else:
        lines = lines_from_json(Path(args.json), args.id)
    print(f"[sub] {video.name} 台词{len(lines)}句: {lines}", flush=True)

    work = video.parent / f"_sub_{video.stem}"
    work.mkdir(exist_ok=True)
    wav = work / "audio.wav"
    subprocess.run(["ffmpeg", "-y", "-i", str(video), "-vn", "-ar", "16000",
                    "-acodec", "pcm_s16le", str(wav)], capture_output=True)
    words = whisper_words(wav)
    timed = align_lines(lines, words)
    for ln, st, en in timed:
        print(f"[sub]   [{st:.2f}-{en:.2f}] {ln}", flush=True)

    ass = work / "sub.ass"
    build_ass(timed, ass)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # ffmpeg 烧字幕（ass 路径含盘符冒号，用相对名+cwd 规避 filtergraph 冒号地狱）
    r = subprocess.run(["ffmpeg", "-y", "-i", str(video.resolve()),
                        "-vf", "subtitles=sub.ass", "-c:a", "copy", str(out.resolve())],
                       cwd=str(work), capture_output=True, text=True)
    if out.exists() and out.stat().st_size > 0:
        print(f"[sub] OK -> {out}", flush=True)
    else:
        print(f"[sub] FAIL: {r.stderr[-400:]}", flush=True)


if __name__ == "__main__":
    main()
