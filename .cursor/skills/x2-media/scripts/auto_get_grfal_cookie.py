#!/usr/bin/env python3
"""Auto-poll GRFal session cookie — no ENTER, background-friendly.

与 get_grfal_cookie.py 的区别：不靠 input() 等用户按回车，而是启动 Chrome 后
轮询 CDP，自动检测到有效的 grfal_session（已登录）就抓取、写 config.json、
并用 winreg 持久化到用户级环境变量 GRFAL_COOKIE（避开 setx 对 >1024 字符截断）。
可在 run_in_background 下跑：用户只需在弹出的 Chrome 里扫码登录。

Usage:
    python auto_get_grfal_cookie.py --url https://grfal.tap4fun.com
    python auto_get_grfal_cookie.py --config <path> --timeout 240
"""

import argparse
import os
import sys
import time

# 复用 get_grfal_cookie.py 的 Chrome/CDP 逻辑（同目录）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from get_grfal_cookie import (  # noqa: E402
    find_chrome, launch_chrome, get_cdp_pages, cdp_get_cookies,
    extract_grfal_cookie, load_config, save_config, DEBUG_PORT, DEFAULT_URL,
)


def find_session_cookie(cookies):
    """从原始 cookie 列表里找有效的 grfal_session（登录态的真正标志）。
    grfal_session 是会话级 cookie，登录后才会写入且值很长（~1000+）。
    返回该 cookie dict 或 None。"""
    for c in cookies:
        if c.get("name") == "grfal_session" and "grfal" in c.get("domain", ""):
            if len(c.get("value", "")) >= 200:
                return c
    return None


def persist_user_env(name, value):
    """用 winreg 写 HKCU\\Environment（避开 setx 的 1024 字符截断），并广播刷新。"""
    if sys.platform != "win32":
        return False
    try:
        import winreg
        import ctypes
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                            winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        # 通知系统环境变量已变（新开的进程才会读到）
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment",
            SMTO_ABORTIFHUNG, 5000, ctypes.byref(ctypes.c_ulong()))
        return True
    except Exception as e:
        print(f"  [warn] 持久化环境变量失败: {e}", flush=True)
        return False


def main():
    p = argparse.ArgumentParser(description="Auto-poll GRFal cookie (no ENTER)")
    p.add_argument("--config", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"))
    p.add_argument("--url", default=None)
    p.add_argument("--port", type=int, default=DEBUG_PORT)
    p.add_argument("--timeout", type=int, default=240, help="最长等待登录秒数")
    p.add_argument("--interval", type=int, default=3, help="轮询间隔秒")
    args = p.parse_args()

    config = load_config(args.config)
    grfal_url = args.url or config.get("grfal_url", DEFAULT_URL)

    print(f"GRFal URL: {grfal_url}")
    print(f"Config:    {args.config}")

    if not find_chrome():
        print("Chrome 未找到，无法自动模式。请手动跑 get_grfal_cookie.py。", flush=True)
        sys.exit(1)

    print(f"启动 Chrome（调试端口 {args.port}），请在弹出的窗口里钉钉扫码登录……", flush=True)
    proc = launch_chrome(grfal_url, args.port)
    if not proc:
        print("Chrome 启动失败。", flush=True)
        sys.exit(1)

    try:
        deadline = time.time() + args.timeout
        last_len = -1
        while time.time() < deadline:
            time.sleep(args.interval)
            pages = get_cdp_pages(args.port, retries=3)
            if not pages:
                continue
            ws_url = None
            for pg in pages:
                if pg.get("webSocketDebuggerUrl"):
                    ws_url = pg["webSocketDebuggerUrl"]
                    break
            if not ws_url:
                continue
            try:
                cookies = cdp_get_cookies(ws_url)
            except Exception:
                continue
            sess = find_session_cookie(cookies)
            sess_len = len(sess["value"]) if sess else 0
            if sess_len != last_len:
                print(f"  …grfal_session 长度 {sess_len}（需 >=200 视为已登录）", flush=True)
                last_len = sess_len
            if sess:
                cookie_str = extract_grfal_cookie(cookies, grfal_url)
                cur_len = len(cookie_str)
                config["grfal_cookie"] = cookie_str
                save_config(args.config, config)
                ok = persist_user_env("GRFAL_COOKIE", cookie_str)
                print("\n✅ 登录成功，已抓取 cookie！", flush=True)
                print(f"   长度: {cur_len}", flush=True)
                print(f"   已写入 config: {args.config}", flush=True)
                print(f"   用户级环境变量 GRFAL_COOKIE: {'已持久化' if ok else '未持久化(看上方warn)'}", flush=True)
                proc.terminate()
                return 0
        print(f"\n❌ {args.timeout}s 内未检测到有效登录态，已超时退出。重跑或确认是否扫码成功。", flush=True)
        proc.terminate()
        return 2
    except KeyboardInterrupt:
        proc.terminate()
        print("\n中断。", flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
