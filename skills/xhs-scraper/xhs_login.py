# -*- coding: utf-8 -*-
"""小红书扫码登录：开一个带界面的浏览器窗口，用户手机扫码。
登录态保存在持久化 profile（C:\\Users\\linkang\\.xhs-profile），
之后爬取脚本用同一 profile 无头复用，无需再登录。

用法: python -X utf8 xhs_login.py
判定登录成功: cookie 出现 web_session 即视为已登录，窗口自动关闭。
"""
import time, sys
from playwright.sync_api import sync_playwright

PROFILE = r"C:\Users\linkang\.xhs-profile"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        PROFILE,
        headless=False,
        viewport={"width": 1280, "height": 860},
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto("https://www.xiaohongshu.com", wait_until="domcontentloaded")
    print("browser opened, waiting for QR login (max 5 min)...", flush=True)

    # 若已有登录态直接通过
    def logged_in():
        return any(c["name"] == "web_session" and c["value"] for c in ctx.cookies("https://www.xiaohongshu.com"))

    if logged_in():
        print("ALREADY LOGGED IN", flush=True)
    else:
        # 尝试主动唤起登录弹窗（未登录时页面通常自动弹）
        deadline = time.time() + 300
        while time.time() < deadline:
            if logged_in():
                print("LOGIN OK", flush=True)
                break
            time.sleep(2)
        else:
            print("TIMEOUT: no login detected in 5 min", flush=True)
            ctx.close()
            sys.exit(1)

    # 落一份 cookie 快照备用（首选还是 persistent profile）
    import json
    cookies = ctx.cookies()
    with open(r"C:\ADHD_agent\skills\xhs-scraper\xhs_cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=1)
    print("cookies saved:", len(cookies), flush=True)
    time.sleep(2)
    ctx.close()
