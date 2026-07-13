# -*- coding: utf-8 -*-
"""Shared helpers for the koubo-remix pipeline scripts."""
import argparse
import os
import re
import subprocess
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")

DEFAULT_BASE = r"C:\新建文件夹\000 源片"

T2S = str.maketrans("後腦認準萬這現見藥經絡壓縮頸", "后脑认准万这现见药经络压缩颈")


def norm(s):
    """Normalize ASR text for matching: traditional->simplified, CJK only."""
    return re.sub(r"[^一-鿿]", "", s.translate(T2S))


def parse_base(desc):
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("args", nargs="*")
    ap.add_argument("--base", default=DEFAULT_BASE, help="产品根目录")
    ns = ap.parse_args()
    return Path(ns.base), ns.args


def find_ffmpeg(base: Path):
    for p in base.glob("**/ffmpeg/ffmpeg.exe"):
        return p
    return Path("ffmpeg")  # fall back to PATH


def paths(base: Path):
    ff = find_ffmpeg(base)
    return {
        "src": base / "000 源片",
        "pipeline": base / "pipeline",
        "analysis": base / "pipeline" / "analysis",
        "lib": base / "切片库",
        "out": base / "输出池",
        "ffmpeg": ff,
        "ffprobe": ff.parent / "ffprobe.exe" if ff.name.endswith(".exe") else Path("ffprobe"),
    }


def run(cmd):
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-800:])
    return p


def load_model():
    """small on this box: medium routinely fails mkl_malloc (commit limit)."""
    from faster_whisper import WhisperModel
    try:
        return WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=4)
    except RuntimeError:
        return WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
