from __future__ import annotations

import base64
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "X3节日外显内容排期_合并页签版_20260805.html"

PAGES = [
    {
        "key": "hero",
        "label": "英雄皮肤",
        "eyebrow": "HERO · FIRST",
        "description": "免费 / $19.99 / 排行榜三档，含 9–12 月完整内容排期",
        "file": "X3英雄皮肤三档排期_20260805.html",
    },
    {
        "key": "city",
        "label": "主城皮肤",
        "eyebrow": "CITY",
        "description": "主城外观内容分层、组合与节日投放规划",
        "file": "X3主城皮肤内容排期_20260805.html",
    },
    {
        "key": "march",
        "label": "行军皮肤",
        "eyebrow": "MARCH",
        "description": "行军外显的月度主题、投放方式与内容排期",
        "file": "X3行军皮肤内容排期_20260805.html",
    },
    {
        "key": "trail",
        "label": "航迹皮肤",
        "eyebrow": "TRAIL",
        "description": "航迹外显的主题组合、投放结构与内容排期",
        "file": "X3航迹皮肤内容排期_20260805.html",
    },
]


def audit_source(source: str, filename: str) -> tuple[int, int]:
    image_sources = re.findall(
        r'<img\b[^>]*?\bsrc=["\']([^"\']+)', source, flags=re.I | re.S
    )
    external_images = [src for src in image_sources if not src.startswith("data:image/")]
    if external_images:
        raise ValueError(f"{filename} contains external images: {external_images[:3]}")

    linked_assets = re.findall(
        r'<(?:script|link)\b[^>]*?(?:src|href)=["\']([^"\']+)',
        source,
        flags=re.I | re.S,
    )
    external_assets = [
        src for src in linked_assets if not src.startswith(("data:", "#"))
    ]
    if external_assets:
        raise ValueError(f"{filename} contains external assets: {external_assets[:3]}")
    return len(image_sources), len(source.encode("utf-8"))


def build() -> None:
    page_payloads: list[str] = []
    tab_buttons: list[str] = []
    total_images = 0

    for index, page in enumerate(PAGES):
        source_path = ROOT / page["file"]
        source = source_path.read_text(encoding="utf-8")
        image_count, byte_count = audit_source(source, page["file"])
        total_images += image_count
        encoded = base64.b64encode(source.encode("utf-8")).decode("ascii")
        page_payloads.append(
            f'<script type="application/octet-stream" id="payload-{page["key"]}">{encoded}</script>'
        )
        active = " is-active" if index == 0 else ""
        selected = "true" if index == 0 else "false"
        tab_buttons.append(
            f'''<button class="tab{active}" role="tab" aria-selected="{selected}" data-key="{page["key"]}">
                <span class="tab-index">{index + 1:02d}</span>
                <span class="tab-copy"><strong>{html.escape(page["label"])}</strong><small>{html.escape(page["eyebrow"])}</small></span>
                <span class="tab-arrow" aria-hidden="true">↗</span>
            </button>'''
        )

    page_meta = {
        page["key"]: {
            "label": page["label"],
            "eyebrow": page["eyebrow"],
            "description": page["description"],
        }
        for page in PAGES
    }

    page = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>X3 节日外显内容排期｜合并页签版</title>
  <style>
    :root {{
      --ink:#162024; --paper:#f5f1e8; --panel:#fffdf7; --line:#c8c0b1;
      --accent:#e14b32; --muted:#6d736f; --deep:#173a3d; --shadow:0 20px 55px rgba(23,58,61,.14);
    }}
    * {{ box-sizing:border-box; }}
    html,body {{ height:100%; margin:0; }}
    body {{
      color:var(--ink); background:var(--paper);
      font-family:"Microsoft YaHei UI","PingFang SC","Noto Sans CJK SC",sans-serif;
      overflow:hidden;
    }}
    body::before {{
      content:""; position:fixed; inset:0; pointer-events:none; opacity:.34;
      background-image:linear-gradient(rgba(23,58,61,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(23,58,61,.055) 1px,transparent 1px);
      background-size:24px 24px;
    }}
    .shell {{ position:relative; height:100%; display:grid; grid-template-columns:292px minmax(0,1fr); padding:18px; gap:18px; }}
    .rail {{
      min-height:0; display:flex; flex-direction:column; padding:24px 18px 18px;
      background:var(--deep); color:#f8f2e6; border-radius:8px 28px 8px 8px;
      box-shadow:var(--shadow); overflow:hidden;
    }}
    .brand {{ padding:0 8px 22px; border-bottom:1px solid rgba(255,255,255,.18); }}
    .kicker {{ color:#f3ad7e; letter-spacing:.18em; font:700 12px/1.2 Georgia,serif; }}
    h1 {{ margin:12px 0 9px; font:700 28px/1.16 Georgia,"STSong",serif; letter-spacing:-.04em; }}
    .brand p {{ margin:0; color:#c9d4cf; font-size:14px; line-height:1.65; }}
    .tabs {{ display:grid; gap:9px; padding:18px 0; }}
    .tab {{
      width:100%; display:grid; grid-template-columns:30px 1fr 22px; align-items:center; gap:10px;
      padding:13px 12px; color:#dce5df; background:transparent; border:1px solid transparent;
      border-radius:7px; cursor:pointer; text-align:left; transition:.22s ease;
    }}
    .tab:hover {{ background:rgba(255,255,255,.08); transform:translateX(3px); }}
    .tab.is-active {{ color:var(--ink); background:#f4c89f; border-color:#ffd9b4; box-shadow:0 8px 22px rgba(0,0,0,.18); }}
    .tab-index {{ font:700 12px/1 Georgia,serif; opacity:.68; }}
    .tab-copy {{ display:grid; gap:3px; }}
    .tab-copy strong {{ font-size:15px; }}
    .tab-copy small {{ font:700 10px/1.2 Georgia,serif; letter-spacing:.13em; opacity:.64; }}
    .tab-arrow {{ opacity:.55; transition:.22s ease; }}
    .tab.is-active .tab-arrow {{ transform:rotate(45deg); opacity:1; }}
    .rail-note {{ margin-top:auto; padding:15px 8px 2px; color:#adc0b9; font-size:12px; line-height:1.6; }}
    .rail-note b {{ color:#fff1e0; }}
    .workspace {{ min-width:0; min-height:0; display:grid; grid-template-rows:auto minmax(0,1fr); }}
    .workspace-head {{
      min-height:86px; display:flex; align-items:flex-end; justify-content:space-between; gap:20px;
      padding:5px 12px 15px;
    }}
    .context small {{ color:var(--accent); font:700 11px/1.2 Georgia,serif; letter-spacing:.18em; }}
    .context h2 {{ margin:6px 0 3px; font:700 24px/1.2 Georgia,"STSong",serif; }}
    .context p {{ margin:0; color:var(--muted); font-size:14px; }}
    .status {{ display:flex; align-items:center; gap:9px; color:var(--muted); font-size:12px; white-space:nowrap; }}
    .status::before {{ content:""; width:8px; height:8px; border-radius:50%; background:#55a672; box-shadow:0 0 0 5px rgba(85,166,114,.13); }}
    .stage {{
      min-height:0; position:relative; background:var(--panel); border:1px solid var(--line);
      border-radius:8px 8px 26px 8px; box-shadow:var(--shadow); overflow:hidden;
    }}
    iframe {{ width:100%; height:100%; border:0; background:#fff; display:block; }}
    .loading {{
      position:absolute; inset:0; display:grid; place-items:center; background:var(--panel); color:var(--muted);
      font:700 13px/1.4 Georgia,serif; letter-spacing:.12em; transition:opacity .25s ease;
    }}
    .loading::before {{ content:""; width:34px; height:34px; margin-right:12px; border:3px solid #d9d1c3; border-top-color:var(--accent); border-radius:50%; animation:spin .75s linear infinite; }}
    .loading-inner {{ display:flex; align-items:center; }}
    .loading.is-hidden {{ opacity:0; pointer-events:none; }}
    @keyframes spin {{ to {{ transform:rotate(360deg); }} }}
    @media (max-width:900px) {{
      body {{ overflow:auto; }}
      .shell {{ height:auto; min-height:100%; grid-template-columns:1fr; padding:10px; gap:10px; }}
      .rail {{ border-radius:8px 20px 8px 8px; padding:18px 14px 12px; }}
      .brand {{ padding-bottom:14px; }} h1 {{ font-size:23px; }}
      .tabs {{ grid-template-columns:repeat(2,minmax(0,1fr)); padding:12px 0 4px; }}
      .rail-note {{ display:none; }}
      .workspace {{ min-height:760px; }}
      .workspace-head {{ min-height:90px; align-items:center; }}
      .status {{ display:none; }}
    }}
    @media (max-width:520px) {{
      .tabs {{ grid-template-columns:1fr; }}
      .tab {{ padding:10px; }}
      .workspace {{ min-height:680px; }}
      .context h2 {{ font-size:20px; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <aside class="rail">
      <header class="brand">
        <div class="kicker">X3 · FESTIVAL COSMETICS</div>
        <h1>节日外显<br>内容排期总览</h1>
        <p>四条规划线汇于一个决策入口；英雄皮肤固定置于第一视图。</p>
      </header>
      <nav class="tabs" role="tablist" aria-label="外显内容规划页签">
        {''.join(tab_buttons)}
      </nav>
      <div class="rail-note"><b>离线单文件</b><br>共 {len(PAGES)} 份完整规划 · {total_images} 张内嵌图片<br>不引用外部图片、脚本或样式。</div>
    </aside>

    <section class="workspace">
      <header class="workspace-head">
        <div class="context">
          <small id="page-eyebrow">HERO · FIRST</small>
          <h2 id="page-title">英雄皮肤</h2>
          <p id="page-description">免费 / $19.99 / 排行榜三档，含 9–12 月完整内容排期</p>
        </div>
        <div class="status">全部内容已封装于本文件</div>
      </header>
      <div class="stage">
        <iframe id="content-frame" title="英雄皮肤规划" loading="eager"></iframe>
        <div class="loading" id="loading"><div class="loading-inner">LOADING PLAN</div></div>
      </div>
    </section>
  </main>

  {''.join(page_payloads)}
  <script>
    const PAGE_META = {page_meta!r};
    const frame = document.getElementById('content-frame');
    const loading = document.getElementById('loading');
    const cache = new Map();

    function decodePayload(key) {{
      if (cache.has(key)) return cache.get(key);
      const encoded = document.getElementById(`payload-${{key}}`).textContent.trim();
      const binary = atob(encoded);
      const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
      const source = new TextDecoder('utf-8').decode(bytes);
      cache.set(key, source);
      return source;
    }}

    function openPage(key, pushHash = true) {{
      const meta = PAGE_META[key] || PAGE_META.hero;
      loading.classList.remove('is-hidden');
      document.querySelectorAll('.tab').forEach(button => {{
        const active = button.dataset.key === key;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-selected', String(active));
      }});
      document.getElementById('page-eyebrow').textContent = meta.eyebrow;
      document.getElementById('page-title').textContent = meta.label;
      document.getElementById('page-description').textContent = meta.description;
      frame.title = `${{meta.label}}规划`;
      frame.srcdoc = decodePayload(key);
      if (pushHash) history.replaceState(null, '', `#${{key}}`);
    }}

    frame.addEventListener('load', () => loading.classList.add('is-hidden'));
    document.querySelectorAll('.tab').forEach(button => button.addEventListener('click', () => openPage(button.dataset.key)));
    document.addEventListener('keydown', event => {{
      if (!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(event.key)) return;
      const buttons = [...document.querySelectorAll('.tab')];
      const index = buttons.findIndex(button => button.classList.contains('is-active'));
      const delta = ['ArrowDown','ArrowRight'].includes(event.key) ? 1 : -1;
      const target = buttons[(index + delta + buttons.length) % buttons.length];
      target.focus(); target.click(); event.preventDefault();
    }});
    const initial = location.hash.slice(1);
    openPage(PAGE_META[initial] ? initial : 'hero', false);
  </script>
</body>
</html>'''

    # Python repr uses single-quoted strings and is valid JavaScript for this plain metadata.
    OUTPUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"WROTE {OUTPUT}")
    print(f"PAGES={len(PAGES)} IMAGES={total_images} BYTES={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    build()
