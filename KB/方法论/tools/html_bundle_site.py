# -*- coding: utf-8 -*-
"""
把「一个入口 HTML + 若干被它链接的 HTML + 素材目录」打包成**一个自包含单文件 HTML**。

跟 `html_inline_assets.py` 的分工：
  - html_inline_assets.py → 单页：把这一页引用的图/视频内嵌，结构不变。
  - html_bundle_site.py（本脚本）→ 多页：把整个分享包（index + reports/*.html + assets/）
    合成一份，页面间跳转变成页内切换，仍然只发一个文件。

为什么用 iframe srcdoc 而不是把各页 body 拼进同一个 DOM：
  各报告页都自带 <style>（往往还有同名 :root 变量）和 <script>。
  - 直接拼 DOM → 样式互相污染，得逐个加 CSS 前缀，极易翻车；
  - Shadow DOM → 样式隔离到位，但 innerHTML 注入的 <script> **不会执行**，交互全废；
  - iframe srcdoc → 样式天然隔离 + script 正常跑。
  代价是高度要自己量（已处理）。

🔑**父子之间零通信**（实测踩坑后的定案，别再往回改）：
  srcdoc iframe 看着"同源"，实测 **contentDocument 取不到（TypeError）、postMessage 也不通**，
  http:// 和 file:// 都一样。所以父页既不读子页 DOM、也不收子页消息，改为在**打包期把问题消灭**：
    1. 跨页跳转 → 打包时把 `href="xxx.html#a"` 重写成 `href="#p/<key>@a"` + `target="_top"`，
       点击直接改顶层 hash → 父页 hashchange 切页。不需要运行时拦截。
    2. 高度 → 不量了，iframe 固定 `calc(100vh - 头高)`，内容在 iframe 内部滚动
       （header 常驻顶部，反而比外层长滚动更好用）。
    3. 进页后要跳锚点 → 父页把一小段 `scrollIntoView` 脚本**拼在 srcdoc 字符串末尾**，
       由子页自己执行，同样不跨文档。

用法：
  python html_bundle_site.py 分享包/index.html
  python html_bundle_site.py 分享包/index.html -o 单文件版.html --title "X3 下期节日优化清单"
  python html_bundle_site.py index.html --img-q 80        # 图片质量（默认 82）
  python html_bundle_site.py index.html --no-compress     # 原样内嵌不压缩

行为：
  从 entry 出发**递归**收集同目录树下被 <a href> 链到的 .html（外链 http/data/# 跳过），
  每个页面内的本地 img/video/css/js 一律内嵌（图片默认转 WebP、视频转 H.264）。
  产出外壳含：顶部页签导航 + hash 路由（#p/<页名>）+ 页内链接拦截 + iframe 高度自适应。
  入口页原有的锚点照常可用：`#某锚点`（不带 p/ 前缀）会被转发进入口 iframe。
"""
import argparse
import base64
import hashlib
import html as html_mod
import mimetypes
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

IMG_EXT = {".png", ".jpg", ".jpeg"}
VID_EXT = {".mp4", ".webm", ".mov"}
ASSET_RE = re.compile(r'(?:src|data-video|href)\s*=\s*"([^"]+)"')
LINK_RE = re.compile(r'href\s*=\s*"([^"]+\.html(?:#[^"]*)?)"', re.I)


def sh(cmd):
    return subprocess.run(cmd, capture_output=True).returncode == 0


def is_local(u: str) -> bool:
    return not (u.startswith(("http://", "https://", "data:", "#", "//", "mailto:", "javascript:")))


def conv_asset(src: Path, cache: Path, img_q: int, crf: int, compress: bool):
    ext = src.suffix.lower()
    mime = mimetypes.guess_type(src.name)[0] or "application/octet-stream"
    if not compress or ext not in (IMG_EXT | VID_EXT):
        return src.read_bytes(), mime
    st = src.stat()
    key = hashlib.md5(f"{src}|{st.st_size}|{int(st.st_mtime)}|{img_q}|{crf}".encode()).hexdigest()[:16]
    if ext in IMG_EXT:
        out = cache / f"{key}.webp"
        if not out.exists() and not sh(["ffmpeg", "-v", "error", "-i", str(src),
                                        "-q:v", str(img_q), str(out), "-y"]):
            return src.read_bytes(), mime
        return out.read_bytes(), "image/webp"
    out = cache / f"{key}.mp4"
    if not out.exists() and not sh(["ffmpeg", "-v", "error", "-i", str(src), "-c:v", "libx264",
                                    "-crf", str(crf), "-preset", "slow", "-an",
                                    "-movflags", "+faststart", str(out), "-y"]):
        return src.read_bytes(), "video/mp4"
    return out.read_bytes(), "video/mp4"


AUTH_HINT = re.compile(r"demo-auth|/demo-auth/verify|returnUrl=", re.I)


def strip_auth_gate(text: str):
    """剥掉 html-deployer 注入的登录闸门 <script>。

    那段脚本会 fetch demo 站的 /demo-auth/verify，失败就 location.href 跳登录页。
    单文件版是发给人**本地双击**看的，fetch 必然失败 → 整页被顶去登录页（表现为一直 Loading）。
    所以打包时必须摘掉，否则产物在离线环境完全打不开。
    """
    out, n, pos = [], 0, 0
    for m in re.finditer(r"<script\b[^>]*>.*?</script>", text, re.S | re.I):
        if AUTH_HINT.search(m.group(0)):
            out.append(text[pos:m.start()])
            pos = m.end()
            n += 1
    out.append(text[pos:])
    return "".join(out), n


def page_title(text: str, fallback: str) -> str:
    m = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip() or fallback
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()[:40] or fallback
    return fallback


def main():
    ap = argparse.ArgumentParser(description="多页 HTML 分享包 → 单文件")
    ap.add_argument("entry", help="入口 HTML")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--img-q", type=int, default=82)
    ap.add_argument("--crf", type=int, default=28)
    ap.add_argument("--no-compress", action="store_true")
    ap.add_argument("--keep-auth", action="store_true",
                    help="保留 demo 站登录闸门脚本（默认剥掉，否则离线打开会被顶去登录页）")
    ap.add_argument("--exclude", action="append", default=[], metavar="页名",
                    help="不收进来的页面（文件名，可带或不带 .html，可多次）。"
                         "指向它的链接会降级成不可点，避免点出 404")
    a = ap.parse_args()
    excluded = {x.lower().removesuffix(".html") for x in a.exclude}

    entry = Path(a.entry).resolve()
    if not entry.exists():
        sys.exit(f"[错误] 入口不存在: {entry}")
    root = entry.parent
    out = Path(a.out).resolve() if a.out else root.parent / f"{root.name}_单文件版.html"
    cache = root / ".bundle_cache"
    cache.mkdir(exist_ok=True)
    compress = not a.no_compress
    if compress and not shutil.which("ffmpeg"):
        sys.exit("[错误] 缺 ffmpeg；不压缩可加 --no-compress")

    # ---- 递归收集页面 ----
    pages, order, queue = {}, [], [entry]
    while queue:
        p = queue.pop(0)
        if p in pages:
            continue
        if not p.exists():
            print(f"  ⚠ 链接指向的文件不存在，跳过: {p.name}")
            pages[p] = None
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        pages[p] = text
        order.append(p)
        for href in LINK_RE.findall(text):
            if not is_local(href):
                continue
            if Path(unquote(urlparse(href).path)).stem.lower() in excluded:
                continue
            tgt = (p.parent / unquote(urlparse(href).path)).resolve()
            if root in tgt.parents or tgt.parent == root or root in tgt.parents:
                queue.append(tgt)
            elif str(tgt).startswith(str(root)):
                queue.append(tgt)

    order = [p for p in order if pages.get(p)]
    keys = {}
    for p in order:
        k = "home" if p == entry else p.stem
        base, i = k, 2
        while k in keys.values():
            k = f"{base}{i}"; i += 1
        keys[p] = k

    # ---- 内嵌每页素材 ----
    total_src = total_out = 0
    built = {}
    stripped = 0
    for p in order:
        text = pages[p]
        if not a.keep_auth:
            text, n = strip_auth_gate(text)
            stripped += n
        for u in sorted(set(ASSET_RE.findall(text)), key=len, reverse=True):
            if not is_local(u) or u.lower().split("#")[0].endswith(".html"):
                continue
            f = (p.parent / unquote(urlparse(u).path)).resolve()
            if not f.exists() or f.is_dir():
                continue
            data, mime = conv_asset(f, cache, a.img_q, a.crf, compress)
            total_src += f.stat().st_size
            total_out += len(data)
            text = text.replace(f'"{u}"', f'"data:{mime};base64,{base64.b64encode(data).decode()}"')
            print(f"  [{keys[p]}] {u}  {f.stat().st_size/1024:.0f}KB -> {len(data)/1024:.0f}KB")
        built[p] = text

    # 页面名去掉站点后缀（"— tap4fun" 之类），页签才不会撑成两行
    def short(s: str) -> str:
        s = re.split(r"\s+[—\-|·]\s+tap4fun", s, flags=re.I)[0].strip()
        return s if len(s) <= 18 else s[:17] + "…"

    file2key = {p.name: keys[p] for p in order}
    title = a.title or page_title(pages[entry], root.name)
    tabs, blobs = [], []
    for p in order:
        k = keys[p]
        name = "总览" if p == entry else short(page_title(pages[p], p.stem))
        full = "总览" if p == entry else page_title(pages[p], p.stem)
        tabs.append(f'<button data-go="{k}" title="{html_mod.escape(full)}">{html_mod.escape(name)}</button>')

        # 跨页链接重写成顶层 hash 路由：href="reports/x.html#a" → href="#p/<key>@a" target="_top"
        def rw(m):
            raw = m.group(1)
            path, _, anchor = raw.partition("#")
            fname = unquote(urlparse(path).path).split("/")[-1]
            key = file2key.get(fname)
            if not key:
                # 被 --exclude 掉的页：链接降级成不可点，免得点出 404
                if Path(fname).stem.lower() in excluded:
                    return ('href="javascript:void(0)" style="cursor:default;opacity:.55" '
                            'title="该页未包含在本单文件版中"')
                return m.group(0)
            return f'href="#p/{key}' + (f"@{anchor}" if anchor else "") + '" target="_top"'

        body = LINK_RE.sub(rw, built[p])
        body = (body.replace("</body>", ANCHOR_FIX + "\n</body>", 1)
                if "</body>" in body else body + ANCHOR_FIX)
        b64 = base64.b64encode(body.encode("utf-8")).decode()
        blobs.append(f'<script type="text/plain" data-page="{k}" data-file="{p.name}">{b64}</script>')

    # 只有一页时不套外壳（没有可跳转的对象，多个空页签栏反而碍事）
    if len(order) == 1:
        only = order[0]
        body = LINK_RE.sub(lambda m: m.group(0), built[only])
        tmp = out.with_suffix(".tmp")
        tmp.write_text(body, encoding="utf-8", newline="")
        os.replace(tmp, out)
        if stripped:
            print(f"\n已剥离 {stripped} 段 demo 登录闸门脚本")
        print(f"\n单页模式（无外壳）：{only.name}")
        print(f"素材 {total_src/1024/1024:.1f}MB -> {total_out/1024/1024:.1f}MB")
        print(f"单文件产出：{out}  ({out.stat().st_size/1024/1024:.1f}MB)")
        return

    shell = SHELL.replace("__TITLE__", html_mod.escape(title))\
                 .replace("__TABS__", "\n  ".join(tabs))\
                 .replace("__BLOBS__", "\n".join(blobs))\
                 .replace("__MAP__", repr({p.name: keys[p] for p in order}).replace("'", '"'))
    tmp = out.with_suffix(".tmp")
    tmp.write_text(shell, encoding="utf-8", newline="")
    os.replace(tmp, out)

    mb = out.stat().st_size / 1024 / 1024
    if stripped:
        print(f"\n已剥离 {stripped} 段 demo 登录闸门脚本（离线打开才不会被顶去登录页）")
    print(f"\n页面 {len(order)} 个：{', '.join(keys[p] for p in order)}")
    print(f"素材 {total_src/1024/1024:.1f}MB -> {total_out/1024/1024:.1f}MB")
    print(f"单文件产出：{out}  ({mb:.1f}MB)")
    if mb > 15:
        print("⚠️ 超过 15MB，低配机开页会卡；建议调大 --crf / --img-q 压更狠")


# 🔴 必须注入：srcdoc iframe 的 base URL **继承父文档**，所以子页里的页内锚点
# `href="#sec"` 会被解析成「父文档URL#sec」→ 浏览器把**外壳文件自己**加载进 iframe，
# 于是页面套娃（header 出现两层）。这里把纯锚点点击改成 scrollIntoView，不动 URL。
# 注意放行 target="_top" 的 `#p/xxx`（那是我们重写的跨页路由，要让它冒泡到顶层）。
ANCHOR_FIX = """
<script>/* --- bundle anchor-fix（打包注入，勿手改） --- */
document.addEventListener("click", function(e){
  var a = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
  if (!a) return;
  if (a.target === "_top") return;                  // 跨页路由，交给顶层
  var h = a.getAttribute("href") || "";
  if (h.indexOf("#p/") === 0 || h === "#") return;
  var id = h.slice(1);
  var t = document.getElementById(id) || document.getElementsByName(id)[0];
  if (!t) return;
  e.preventDefault();
  t.scrollIntoView({block:"start"});   // 与原生 hash 跳转一致；smooth 会让"点了半天不动"
}, true);
</script>"""

SHELL = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
  :root{--bg:#0e131a;--bar:#141c26;--line:#25313f;--fg:#e8f0f8;--dim:#8fa3b8;--acc:#5ad1ff}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);
       font-family:"Microsoft YaHei","PingFang SC",sans-serif}
  header{position:sticky;top:0;z-index:10;background:var(--bar);
         border-bottom:1px solid var(--line);padding:8px 14px;
         display:flex;align-items:center;gap:10px;flex-wrap:wrap;
         box-shadow:0 2px 14px rgba(0,0,0,.4)}
  header .t{font-size:14px;font-weight:700;margin-right:6px;white-space:nowrap}
  header .t small{color:var(--dim);font-weight:400;margin-left:8px;font-size:11.5px}
  nav{display:flex;gap:6px;flex-wrap:wrap}
  nav button{background:transparent;color:var(--dim);border:1px solid var(--line);
             border-radius:4px;padding:4px 11px;font-size:12.5px;cursor:pointer;
             font-family:inherit;transition:.18s}
  nav button:hover{color:var(--fg);border-color:var(--acc)}
  nav button.on{background:var(--acc);border-color:var(--acc);color:#05202b;font-weight:700}
  nav button[title]{max-width:230px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  #wrap{position:relative}
  /* 高度不做运行时测量：iframe 占满视口余下高度，内容在其内部滚动 */
  iframe{width:100%;border:0;display:block;background:#fff;height:calc(100vh - var(--hh,46px))}
</style></head><body>

<header id="hd">
  <div class="t">__TITLE__ <small>单文件版 · 全部内容已内嵌</small></div>
  <nav>__TABS__</nav>
</header>
<div id="wrap"><iframe id="fr" title="内容"></iframe></div>

__BLOBS__

<script>
const FILE2KEY = __MAP__;
const store = {};
document.querySelectorAll('script[type="text/plain"][data-page]').forEach(s=>{
  store[s.dataset.page] = s.textContent.trim();
});
const fr = document.getElementById('fr');
const btns = [...document.querySelectorAll('nav button')];

function decode(b64){
  const bin = atob(b64), u8 = new Uint8Array(bin.length);
  for (let i=0;i<bin.length;i++) u8[i] = bin.charCodeAt(i);
  return new TextDecoder('utf-8').decode(u8);   // 必须走 TextDecoder，否则中文乱码
}
let cur = null;

function headH(){
  const h = document.getElementById('hd').offsetHeight;
  document.documentElement.style.setProperty('--hh', h + 'px');
}

// 进页后要滚到某锚点：把脚本拼在 srcdoc 末尾，由子页自己跑（不跨文档）
function anchorScript(anchor){
  if (!anchor) return '';
  return '<script>(function(){function g(){var t=document.getElementById(' +
         JSON.stringify(anchor) + ')||document.getElementsByName(' + JSON.stringify(anchor) +
         ')[0];if(t)t.scrollIntoView();}addEventListener("load",g);setTimeout(g,200);setTimeout(g,800);})();<\\/script>';
}

function go(key, anchor, push=true){
  if (!store[key]) key = 'home';
  const same = (cur === key);
  cur = key;
  btns.forEach(b=>b.classList.toggle('on', b.dataset.go === key));
  // 同页只换锚点也要重载 srcdoc（子页无法从外部驱动滚动）
  fr.srcdoc = decode(store[key]) + anchorScript(anchor);
  if (push){
    const h = (key === 'home' ? (anchor ? '#'+anchor : '') : '#p/'+key + (anchor?'@'+anchor:''));
    history.replaceState(null, '', h || location.pathname);
  }
}
function fromHash(){
  const h = decodeURIComponent(location.hash.slice(1));
  if (h.startsWith('p/')){
    const [k, an] = h.slice(2).split('@');
    go(k, an, false);
  } else {
    go('home', h || null, false);   // 兼容入口页原有锚点，如 #monopoly
  }
}
btns.forEach(b=>b.addEventListener('click', ()=>go(b.dataset.go)));
window.addEventListener('hashchange', fromHash);   // 子页链接 target=_top 改 hash 后由此接管
window.addEventListener('resize', headH);
headH();
fromHash();
</script>
</body></html>
"""

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
