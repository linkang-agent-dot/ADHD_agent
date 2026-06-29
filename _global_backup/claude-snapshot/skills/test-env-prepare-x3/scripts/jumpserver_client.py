#!/usr/bin/env python3
"""经 JumpServer SSH 到 QC 物理机执行 date 命令。"""

from __future__ import annotations

import asyncio
import re

import asyncssh

JUMP_HOST = "j.tap4fun.com"
MARKER = "__DATE_CMD_END__"


async def _read_until(reader, patterns: list, timeout: float) -> str:
    buf = ""
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            return buf
        try:
            chunk = await asyncio.wait_for(reader.read(4096), timeout=min(remaining, 2.0))
            if not chunk:
                return buf
            buf += chunk.decode("utf-8", errors="replace") if isinstance(chunk, bytes) else chunk
            for pattern in patterns:
                if pattern in buf or re.search(pattern, buf):
                    return buf
        except asyncio.TimeoutError:
            return buf


def _clean(text: str) -> str:
    text = re.sub(r"\x1b\[[0-9;]*[mGKHJF]", "", text)
    return re.sub(r"\r\n", "\n", text)


async def run_on_host(hostname: str, cmd: str) -> str:
    short_name = hostname.split(".")[0]
    async with asyncssh.connect(JUMP_HOST, known_hosts=None, request_pty=True) as conn:
        proc = await conn.create_process("", term_type="xterm", term_size=(220, 50), request_pty=True)
        await _read_until(proc.stdout, ["Opt>"], timeout=15)
        proc.stdin.write(short_name + "\r")
        response = await _read_until(proc.stdout, [r"\$\s", r"#\s", "$ ", "# "], timeout=35)
        if re.search(r"\b1[\)\.\s]", response) and not re.search(r"[\$#]\s", response):
            proc.stdin.write("1\r")
            response = await _read_until(proc.stdout, [r"\$\s", r"#\s", "$ ", "# "], timeout=20)
        if not re.search(r"[\$#]", response):
            raise RuntimeError(f"未能登录 {hostname}:\n{_clean(response)[:800]}")
        proc.stdin.write("stty -echo\r")
        await asyncio.sleep(0.5)
        proc.stdin.write(
            f"echo '===BEFORE==='; date; {cmd}; echo '===AFTER==='; date; echo '{MARKER}'\r"
        )
        output = await _read_until(proc.stdout, [MARKER], timeout=60)
        proc.stdin.write("exit\r")
        return _clean(output)


async def shift_days(hostname: str, days: int) -> str:
    cmd = f'sudo date -s "$(date -d \'+{days} days\' \'+%Y-%m-%d %H:%M:%S\')"'
    return await run_on_host(hostname, cmd)


async def set_absolute_time(hostname: str, when: str) -> str:
    cmd = f'sudo date -s "{when}"'
    return await run_on_host(hostname, cmd)


def shift_days_sync(hostname: str, days: int) -> str:
    return asyncio.run(shift_days(hostname, days))


def set_absolute_time_sync(hostname: str, when: str) -> str:
    return asyncio.run(set_absolute_time(hostname, when))


def run_on_host_sync(hostname: str, cmd: str) -> str:
    return asyncio.run(run_on_host(hostname, cmd))


async def disable_ntp(hostname: str) -> str:
    return await run_on_host(hostname, "sudo timedatectl set-ntp false 2>/dev/null; timedatectl status 2>/dev/null | head -5")


def disable_ntp_sync(hostname: str) -> str:
    return asyncio.run(disable_ntp(hostname))


def check_time_sync(hostname: str) -> str:
    """检查物理机当前时间"""
    return asyncio.run(run_on_host(hostname, "date"))


def reset_time_to_now_sync(hostname: str, now: str) -> str:
    """重置物理机时间。now 格式: '2026-06-11 10:00:00'"""
    return asyncio.run(set_absolute_time(hostname, now))
