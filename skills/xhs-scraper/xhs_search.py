# -*- coding: utf-8 -*-
"""小红书搜索+笔记正文抓取（需先跑 xhs_login.py 扫码登录一次）。

用法: python -X utf8 xhs_search.py "关键词" [笔记数上限,默认8]
输出: 当前目录 xhs_<关键词>.md （笔记标题/链接/点赞/正文）
"""
import sys, time, re, json, os
from playwright.sync_api import sync_playwright

PROFILE = r"C:\Users\linkang\.xhs-profile"
KW = sys.argv[1] if len(sys.argv) > 1 else "幻兽帕鲁"
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 8

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        PROFILE, headless=True, viewport={"width": 1280, "height": 900},
        args=["--disable-blink-features=AutomationControlled"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    from urllib.parse import quote
    page.goto(f"https://www.xiaohongshu.com/search_result?keyword={quote(KW)}&type=51", timeout=30000)
    page.wait_for_timeout(4000)
    for _ in range(3):
        page.mouse.wheel(0, 1200); page.wait_for_timeout(1500)

    cards = page.eval_on_selector_all(
        "section a[href*='/search_result/'], section a[href*='/explore/']",
        """els => els.map(e => ({href: e.href, text: (e.innerText||'').trim().slice(0,80)}))"""
    )
    # 去重 + 过滤空标题
    seen, notes = set(), []
    for c in cards:
        m = re.search(r"/(?:explore|search_result)/([0-9a-f]{24})", c["href"])
        if not m: continue
        nid = m.group(1)
        if nid in seen: continue
        seen.add(nid)
        notes.append({"id": nid, "href": c["href"], "title": c["text"]})
    print(f"found {len(notes)} notes for [{KW}]", flush=True)

    out = [f"# 小红书搜索: {KW}", ""]
    for n in notes[:LIMIT]:
        try:
            page.goto(n["href"], timeout=30000)
            page.wait_for_timeout(3000)
            title = page.title()
            # 正文
            body = ""
            for sel in ["#detail-desc", ".note-content", ".desc"]:
                el = page.query_selector(sel)
                if el:
                    body = el.inner_text().strip(); break
            if not body:
                md = page.query_selector("meta[name='description']")
                body = md.get_attribute("content") if md else ""
            likes = ""
            le = page.query_selector(".like-wrapper .count, .engage-bar .like-wrapper")
            if le: likes = le.inner_text().strip()
            out.append(f"## {title}\n- 链接: {n['href']}\n- 点赞: {likes}\n\n{body}\n")
            print("OK", n["id"], title[:40], flush=True)
        except Exception as e:
            print("ERR", n["id"], repr(e)[:80], flush=True)
        time.sleep(2)

    fn = os.path.join(os.getcwd(), f"xhs_{re.sub(r'[^\w]', '_', KW)}.md")
    open(fn, "w", encoding="utf-8").write("\n".join(out))
    print("saved:", fn, flush=True)
    ctx.close()
