#!/usr/bin/env python3
"""将 x2-media 的 Cursor 规则安装到目标项目的 .cursor/rules/。

初始配置或换项目时使用；可重复执行（覆盖同名文件）。

用法:
    python install_cursor_rule.py
    python install_cursor_rule.py --project E:/X2
    python install_cursor_rule.py --project . --dry-run
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy rules/x2-media.mdc → <project>/.cursor/rules/x2-media.mdc"
    )
    parser.add_argument(
        "--project",
        "-p",
        type=Path,
        default=Path("."),
        help="目标项目根目录（默认：当前工作目录）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印源路径与目标路径，不写入",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    skill_root = Path(__file__).resolve().parent.parent
    src = skill_root / "rules" / "x2-media.mdc"
    if not src.is_file():
        print(f"ERROR: 未找到规则模板: {src}", file=sys.stderr)
        return 1

    dst_dir = project / ".cursor" / "rules"
    dst = dst_dir / "x2-media.mdc"

    if args.dry_run:
        print(f"[dry-run] 将复制:\n  {src}\n  -> {dst}")
        return 0

    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"已安装 Cursor 规则: {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
