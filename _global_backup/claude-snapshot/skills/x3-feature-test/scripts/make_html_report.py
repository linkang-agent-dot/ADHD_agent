#!/usr/bin/env python3
"""
可复用的「功能验证 HTML 报告」生成器（x3-feature-test 专用）。

为什么要它：用桥 ScreenCapture 截的图是本地 PNG，Artifact/分享场景需要把图**嵌进 HTML**
（Artifact 的 CSP 禁止外链图片/字体），手写 base64 内联又长又易错。本脚本把这套固化下来：
读一份 JSON spec → 把截图 base64 内联成 data URI → 输出一份配色考究、CSP 安全、自带验收横幅
和数据表的单文件 HTML。下次验任何功能要出报告，写个小 JSON 跑一下即可，别再现写。

用法：
    python make_html_report.py <spec.json> [out.html]
    # out 省略时默认写到 spec 同目录的 report_<ticket>.html

spec.json 结构（字段都可选，给了就渲染）：
{
  "title":  "X3NEW-592 验证报告 · 限时招募池断档修复",   # 浏览器标题
  "ticket": "X3NEW-592",
  "headline": "英雄限时招募池 174 天+ 断档修复",
  "subtitle": "异国美酒(7002)限时招募池排程止于开服 173 天 …",
  "status": "pass",                # pass | partial | fail  → 🟢/🟡/🔴 + 配色
  "banner": "<b>通过</b><br>纯配置改动 …",   # 横幅里的 HTML（允许 <b><code><br> 等）
  "screenshots": [                 # 截图：本地 PNG 路径 + caption(HTML)
    {"path": "C:/…/recruit_FINAL.png", "caption": "<b>核心证据 · 175 天</b><br>…"}
  ],
  "sections": [                    # 任意小节：标题 + 正文 HTML（表格自己写 <table>）
    {"h2": "运行时实测", "html": "<div class='scroll'><table>…</table></div>"}
  ],
  "footer_left": "验收：核心标准通过 → 🟢",
  "footer_right": "2026-06-24"
}

注意：sections/banner/caption 里的 HTML 原样输出（你自己保证可信），用本脚手架自带的
class（scroll/table/pill yes|no/note/grid2/k/mono/hero…）即可拿到统一样式，见下方 CSS。
"""
import base64
import json
import pathlib
import sys

STATUS = {
    "pass":    {"dot": "\U0001f7e2", "fg": "#2f7d4c", "bg": "#e7f2ea", "bd": "#bfe0cb"},
    "partial": {"dot": "\U0001f7e1", "fg": "#9a6a16", "bg": "#f7efdc", "bd": "#e6d3a6"},
    "fail":    {"dot": "\U0001f534", "fg": "#a33227", "bg": "#f6e7e4", "bd": "#e7c4bd"},
}


def data_uri(png_path: str) -> str:
    raw = pathlib.Path(png_path).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode()


def css() -> str:
    # 主题：暖纸 ground + 酒馆/酒 暖琥珀+酒红 accent，语义绿/黄/红独立于 accent。
    return """
<style>
  :root{--paper:#f6f1e7;--card:#fffdf7;--ink:#2b2318;--ink-soft:#5a4f3d;--muted:#8c8069;
    --line:#e3dac9;--line-soft:#efe8da;--amber:#a9701b;--wine:#7c2f25;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);line-height:1.65;-webkit-font-smoothing:antialiased;
    font-family:ui-sans-serif,-apple-system,"Segoe UI",system-ui,sans-serif}
  .wrap{max-width:880px;margin:0 auto;padding:48px 24px 96px}
  .serif{font-family:ui-serif,Georgia,"Songti SC","Noto Serif CJK SC",serif}
  .mono{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}
  .eyebrow{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--amber);font-weight:600;margin:0 0 10px}
  h1{font-family:ui-serif,Georgia,"Songti SC",serif;font-size:34px;line-height:1.2;margin:0 0 6px;text-wrap:balance;letter-spacing:-.01em}
  h2{font-family:ui-serif,Georgia,"Songti SC",serif;font-size:21px;margin:0 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)}
  .sub{color:var(--ink-soft);font-size:15px;margin:0}
  header{margin-bottom:34px}
  .ticket{display:inline-block;font-size:12.5px;letter-spacing:.04em;color:var(--wine);background:#f4e6e3;
    border:1px solid #e7cdc8;border-radius:5px;padding:2px 9px;margin-bottom:18px}
  .banner{display:flex;align-items:center;gap:16px;border-radius:10px;padding:18px 22px;margin:26px 0 6px}
  .banner .dot{font-size:30px;line-height:1}
  .banner p{margin:3px 0 0;font-size:14px;color:var(--ink-soft)}
  .banner b{font-size:18px}
  section{margin-top:40px}
  table{width:100%;border-collapse:collapse;font-size:14px}
  .scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}
  th,td{text-align:left;padding:11px 14px;border-bottom:1px solid var(--line-soft)}
  th{font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);background:#f0e9da;font-weight:600;white-space:nowrap}
  tr:last-child td{border-bottom:none}
  td.k{color:var(--ink-soft);white-space:nowrap}
  .pill{display:inline-block;font-size:12px;font-weight:600;padding:1px 8px;border-radius:20px}
  .pill.yes{color:#2f7d4c;background:#e7f2ea}
  .pill.no{color:var(--muted);background:#efe9dc}
  .hero{color:var(--wine);font-weight:600}
  figure{margin:0}
  .shotgrid{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
  @media(max-width:620px){.shotgrid{grid-template-columns:1fr}}
  .shot{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px;box-shadow:0 1px 2px rgba(60,45,20,.05)}
  .shot img{display:block;width:100%;max-width:100%;border-radius:7px;border:1px solid var(--line-soft)}
  figcaption{font-size:13px;color:var(--ink-soft);margin-top:10px}
  figcaption b{color:var(--ink)}
  ul{margin:0;padding-left:20px}
  li{margin:7px 0;font-size:14.5px}
  code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;background:#efe8da;padding:1px 5px;border-radius:4px;color:var(--wine)}
  .note{background:#f7efdc;border:1px solid #e6d3a6;border-left:4px solid #9a6a16;border-radius:9px;padding:14px 18px;font-size:14px;color:#5e4a18}
  .note b{color:#9a6a16}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  @media(max-width:620px){.grid2{grid-template-columns:1fr}}
  .lead{font-size:15.5px;color:var(--ink-soft)}
  .meta{font-size:13px;color:var(--muted);margin-top:54px;padding-top:18px;border-top:1px solid var(--line);
    display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
</style>
"""


def build(spec: dict) -> str:
    st = STATUS.get(spec.get("status", "pass"), STATUS["pass"])
    parts = [f"<title>{spec.get('title', 'Verification Report')}</title>", css(), '<div class="wrap">']

    parts.append('<header>')
    if spec.get("ticket"):
        parts.append(f'<span class="ticket mono">{spec["ticket"]}</span>')
    parts.append('<p class="eyebrow">运行时验证报告 · QA</p>')
    if spec.get("headline"):
        parts.append(f'<h1 class="serif">{spec["headline"]}</h1>')
    if spec.get("subtitle"):
        parts.append(f'<p class="sub">{spec["subtitle"]}</p>')
    if spec.get("banner"):
        parts.append(
            f'<div class="banner" style="background:{st["bg"]};border:1px solid {st["bd"]};border-left:5px solid {st["fg"]}">'
            f'<span class="dot">{st["dot"]}</span><div style="color:{st["fg"]}">{spec["banner"]}</div></div>'
        )
    parts.append('</header>')

    shots = spec.get("screenshots") or []
    if shots:
        parts.append('<section><h2 class="serif">截图证据</h2><div class="shotgrid">')
        for s in shots:
            parts.append(
                f'<figure class="shot"><img src="{data_uri(s["path"])}" alt="screenshot">'
                f'<figcaption>{s.get("caption", "")}</figcaption></figure>'
            )
        parts.append('</div></section>')

    for sec in spec.get("sections") or []:
        parts.append('<section>')
        if sec.get("h2"):
            parts.append(f'<h2 class="serif">{sec["h2"]}</h2>')
        parts.append(sec.get("html", ""))
        parts.append('</section>')

    if spec.get("footer_left") or spec.get("footer_right"):
        parts.append(
            f'<div class="meta mono"><span>{spec.get("footer_left", "")}</span>'
            f'<span>{spec.get("footer_right", "")}</span></div>'
        )
    parts.append('</div>')
    return "\n".join(parts)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    spec_path = pathlib.Path(sys.argv[1])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    # 截图路径相对 spec 文件解析（便于 sample 可移植）
    for s in spec.get("screenshots") or []:
        p = pathlib.Path(s["path"])
        if not p.is_absolute():
            s["path"] = str((spec_path.parent / p).resolve())
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else \
        spec_path.with_name(f"report_{spec.get('ticket', 'feature')}.html")
    out.write_text(build(spec), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes, {len(spec.get('screenshots') or [])} screenshots embedded)")


if __name__ == "__main__":
    main()
