# -*- coding: utf-8 -*-
"""瓦坎达永恒评述三期音频 -> faster-whisper 转写（复用 bili_transcribe 配置）"""
import os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
SP = os.path.dirname(os.path.abspath(__file__))
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8", local_files_only=True)

JOBS = [
    ("wkd_shangqi_audio.m4a", "瓦坎达_永恒评述_上期_transcript.txt", "上期18:07 章节:吉鲁/古蒂/菲尔米诺/马赫雷斯/萨内蒂?/马尔基尼奥斯/希勒/卡恩/里瓦尔多/法布雷加斯/萨内蒂/卡纳瓦罗/欧文/罗伊斯/伊涅斯塔/劳尔/范佩西"),
    ("wkd_zhongqi_audio.m4a", "瓦坎达_永恒评述_中期_transcript.txt", "中期21:53 第1章普斯卡什起"),
    ("wkd_xiaqi_audio.m4a", "瓦坎达_永恒评述_下期_transcript.txt", "下期20:30 第2章维埃拉/埃辛等"),
]
for src, dst, note in JOBS:
    m4a = os.path.join(SP, src)
    wav = m4a + ".wav"
    subprocess.run(["ffmpeg", "-y", "-i", m4a, "-vn", "-ar", "16000", "-ac", "1", wav], capture_output=True)
    segs, _ = model.transcribe(wav, language="zh", beam_size=5)
    lines = [f"# FConline瓦坎达 永恒评述直播切片 {note}", "# 抓取转写 2026-07-25", ""]
    for s in segs:
        lines.append(f"[{int(s.start)//60:02d}:{int(s.start)%60:02d}] {s.text.strip()}")
    out = os.path.join(SP, dst)
    tmp = out + ".tmp"
    open(tmp, "w", encoding="utf-8").write("\n".join(lines))
    os.replace(tmp, out)
    os.remove(wav)
    print("DONE", dst, len(lines))
print("ALL_DONE")
