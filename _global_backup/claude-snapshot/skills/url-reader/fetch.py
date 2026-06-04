#!/usr/bin/env python3
"""
url-reader wrapper — 修复 output 默认路径问题
原脚本 scripts/url_reader.py 默认 --output ./output，exec cwd 不固定导致落错目录。
本 wrapper 自动注入正确的 --output 路径。
"""
import sys
import os
import subprocess
from pathlib import Path

# 自动加载同目录下的 .env 文件
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

SCRIPT = Path(__file__).parent / "scripts" / "url_reader.py"
OUTPUT = Path(__file__).parent / "output"

# 如果调用方没有显式指定 --output，注入默认值
args = sys.argv[1:]
if "--output" not in args and "-o" not in args:
    args = args + ["--output", str(OUTPUT)]

result = subprocess.run([sys.executable, str(SCRIPT)] + args)
sys.exit(result.returncode)
