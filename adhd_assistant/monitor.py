"""
Real-time bot monitor — tail the monitor.log with color-coded output.

Usage: python monitor.py
"""

import time
import sys
import os
from pathlib import Path

LOG_FILE = Path(__file__).parent / "logs" / "monitor.log"

COLORS = {
    "[USER]":     "\033[96m",   # cyan
    "[AI]":       "\033[93m",   # yellow
    "[BOT]":      "\033[92m",   # green
    "[BUTTON]":   "\033[95m",   # magenta
    "[SCHEDULE]": "\033[94m",   # blue
    "[ERROR]":    "\033[91m",   # red
}
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


def colorize(line: str) -> str:
    for tag, color in COLORS.items():
        if tag in line:
            ts, _, rest = line.partition(" ")
            return f"{DIM}{ts}{RESET} {color}{BOLD}{rest}{RESET}"
    return line


def main():
    os.system("")  # enable ANSI on Windows

    print(f"{BOLD}{'=' * 60}")
    print(f"  ADHD Bot Monitor — real-time interaction log")
    print(f"  Log file: {LOG_FILE}")
    print(f"  Ctrl+C to quit")
    print(f"{'=' * 60}{RESET}\n")

    LOG_FILE.parent.mkdir(exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.touch()

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        f.seek(0, 2)  # jump to end
        while True:
            line = f.readline()
            if line:
                line = line.rstrip()
                if line:
                    print(colorize(line))
            else:
                time.sleep(0.3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{DIM}Monitor stopped.{RESET}")
        sys.exit(0)
