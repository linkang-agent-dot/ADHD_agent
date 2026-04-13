"""
cursor_watchdog.py — 确保 cursor_daemon.py 永远在跑

逻辑：
  1. 读取 PID 文件，检查进程是否存活
  2. 不在 → 启动新的 daemon 进程
  3. 已在 → 什么都不做，退出

由 Windows 计划任务每 5 分钟调用一次。

强制重启（在本机 PowerShell/CMD/计划任务中执行，勿依赖 Cursor 内置终端沙箱）：
  python cursor_watchdog.py --force-restart
"""
import sys
import os
import json
import subprocess
import time
import argparse
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

PIDFILE   = r'C:\ADHD_agent\openclaw\workspace\daemon.pid'
DAEMON_PY = r'C:\ADHD_agent\.cursor\skills\async-notify\scripts\cursor_daemon.py'
LOG_FILE  = r'C:\ADHD_agent\openclaw\workspace\daemon_watchdog.log'
STOP_PS   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stop_cursor_daemon.ps1')


def log(msg: str):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line, flush=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def is_pid_alive(pid: int) -> bool:
    """检查 PID 是否还活着（Windows）

    注意：GetExitCodeProcess 要求句柄带 PROCESS_QUERY_LIMITED_INFORMATION（或
    PROCESS_QUERY_INFORMATION）。仅用 SYNCHRONIZE 时 API 行为不可靠，会误判「已退出」，
    导致 watchdog 每 5 分钟杀进程式地重复启动 daemon，任务队列与飞书通知全部乱套。
    """
    try:
        import ctypes
        import ctypes.wintypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        SYNCHRONIZE = 0x00100000
        access = PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE
        handle = ctypes.windll.kernel32.OpenProcess(access, False, pid)
        if handle == 0:
            return False
        exit_code = ctypes.wintypes.DWORD()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        ctypes.windll.kernel32.CloseHandle(handle)
        if not ok:
            return False
        STILL_ACTIVE = 259
        return exit_code.value == STILL_ACTIVE
    except Exception:
        return False


def read_pid() -> int | None:
    if not os.path.exists(PIDFILE):
        return None
    try:
        with open(PIDFILE, 'r') as f:
            data = json.load(f)
        return data.get('pid')
    except Exception:
        return None


def write_pid(pid: int):
    with open(PIDFILE, 'w', encoding='utf-8') as f:
        json.dump({'pid': pid, 'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, f)


def force_kill_via_powershell():
    """按命令行匹配结束所有 cursor_daemon.py（Windows）。失败则仅打日志。"""
    if not os.path.isfile(STOP_PS):
        log(f'⚠ 未找到 {STOP_PS}，跳过 PowerShell 强杀')
        return
    r = subprocess.run(
        [
            'powershell',
            '-NoProfile',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            STOP_PS,
        ],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    if r.stdout:
        for line in r.stdout.strip().splitlines():
            log(line)
    if r.returncode != 0 and r.stderr:
        log(f'⚠ stop_cursor_daemon.ps1 stderr: {r.stderr.strip()[:500]}')


def start_daemon(auto_execute: bool = True, default_model: str = None):
    """以独立进程启动 daemon，不阻塞本脚本。
    auto_execute=True 时加 --auto-execute，daemon 检测到任务后自动调用 Agent CLI 执行。
    default_model 可指定全局默认模型（可被任务 JSON 的 model 字段覆盖）。
    """
    cmd = [sys.executable, DAEMON_PY, '--timeout', '86400', '--stay-alive']
    if auto_execute:
        cmd.append('--auto-execute')
    if default_model:
        cmd += ['--default-model', default_model]
    proc = subprocess.Popen(
        cmd,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
        stdout=open(r'C:\ADHD_agent\openclaw\workspace\daemon_stdout.log', 'a', encoding='utf-8'),
        stderr=subprocess.STDOUT,
        close_fds=True,
    )
    write_pid(proc.pid)
    mode = 'auto-execute' if auto_execute else 'stay-alive'
    model_info = default_model or '(CLI默认)'
    log(f'✅ daemon 已启动 PID={proc.pid} 模式={mode} 默认模型={model_info}')
    return proc.pid


def main():
    parser = argparse.ArgumentParser(description='cursor_daemon 看门狗')
    parser.add_argument(
        '--force-restart',
        action='store_true',
        help='先按命令行强杀所有 cursor_daemon.py，再启动新 daemon（需在本机非沙箱环境执行）',
    )
    parser.add_argument(
        '--no-auto-execute',
        action='store_true',
        help='启动 daemon 时不加 --auto-execute（传统模式，仅打印任务等人来读）',
    )
    parser.add_argument(
        '--default-model',
        type=str, default=None,
        help='全局默认模型，透传给 daemon。例: claude-4.6-opus-high-thinking',
    )
    args = parser.parse_args()
    auto_exec = not args.no_auto_execute

    if args.force_restart:
        log('--- watchdog 强制重启（先杀后启）---')
        force_kill_via_powershell()
        time.sleep(1)
        new_pid = start_daemon(auto_execute=auto_exec, default_model=args.default_model)
        log(f'daemon 强制重启完成 PID={new_pid}')
        return

    log('--- watchdog 检查 ---')
    pid = read_pid()

    if pid and is_pid_alive(pid):
        log(f'✔ daemon 正常运行中 PID={pid}，无需重启')
        return

    if pid:
        log(f'⚠ daemon PID={pid} 已退出，准备重启')
    else:
        log('⚠ 未找到 daemon PID，首次启动')

    new_pid = start_daemon(auto_execute=auto_exec, default_model=args.default_model)
    log(f'daemon 重启完成 PID={new_pid}')


if __name__ == '__main__':
    main()
