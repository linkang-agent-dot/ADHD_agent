"""读 t2v_E222.json，生成一张审阅用 HTML：每条展示实际发给 API 的完整 prompt
（prefix+分镜+suffix+extra 分色标注），附 dur/主体色/是否待重出/成片状态。本地打开审阅用。
用法: python scripts/gen_prompt_review_html.py
"""
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "prompts" / "t2v_E222.json").read_text(encoding="utf-8"))
m = data["_meta"]
prefix = m.get("prefix", "")
suffix = m.get("suffix", "")

# 逐条主体色标签 + 是否待重出（对着原片扫定的权威色卡）
COLOR = {
    "01": ("keeper·仅第4秒肤色肩带", "keep"),
    "02": ("keeper·妈妈+产品空镜", "keep"),
    "03": ("粉底肤色（裸肤无痕）", "redo"),
    "04": ("keeper·长袖", "keep"),
    "05": ("粉底肤色（裸肤无痕）", "redo"),
    "06": ("内衣被裙盖·肤色肩带", "ok"),
    "07": ("白色运动背心（照原片）", "ok"),
    "08": ("内衣被裙盖·肤色肩带", "ok"),
    "09": ("粉底肤色", "ok"),
    "10": ("着装+手持粉色产品", "ok"),
    "11": ("粉底肤色", "ok"),
    "12": ("内衣被纱裙盖·肤色肩带", "ok"),
    "13": ("keeper·妈妈", "keep"),
    "14": ("米白（象牙白透薄款）·严禁绿色", "redo"),
    "15": ("粉底肤色+掀衣露出", "redo"),
    "16": ("米白（偏白隐形·suffix默认）", "ok"),
}
STATUS_LABEL = {"keep": "keeper·不重出", "ok": "上版已OK", "redo": "待重出"}
STATUS_COLOR = {"keep": "#8b95a1", "ok": "#2e9e5b", "redo": "#d9822b"}

def esc(s):
    return html.escape(s)

cards = []
for c in data["clips"]:
    cid = c["id"]
    dur = c.get("dur", "")
    extra = c.get("extra", "")
    ctag, cstat = COLOR.get(cid, ("", "ok"))
    full = prefix + c["prompt"] + suffix + extra
    seg = (
        f'<span class="seg pfx">{esc(prefix)}</span>'
        f'<span class="seg body">{esc(c["prompt"])}</span>'
        f'<span class="seg sfx">{esc(suffix)}</span>'
        + (f'<span class="seg extra">{esc(extra)}</span>' if extra else "")
    )
    cards.append(f'''
    <div class="card {cstat}">
      <div class="chead">
        <span class="cid">{cid}</span>
        <span class="dur">{dur}s</span>
        <span class="ctag">{esc(ctag)}</span>
        <span class="cstat" style="background:{STATUS_COLOR[cstat]}">{STATUS_LABEL[cstat]}</span>
        <span class="charlen">{len(full)}字</span>
      </div>
      <div class="prompt">{seg}</div>
    </div>''')

colormap = m.get("颜色映射(逐条对原片扫定,权威色卡·2026-07-15)", {})
colormap_rows = "".join(
    f"<tr><td>{esc(str(k))}</td><td>{esc(str(v))}</td></tr>"
    for k, v in colormap.items()
)

doc = f'''<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>E222 t2v Prompt 审阅</title>
<style>
:root{{--bg:#f6f7f9;--fg:#1c2127;--card:#fff;--line:#e3e6ea;--muted:#8b95a1;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.7 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif;padding:24px;max-width:1000px;margin:0 auto}}
h1{{font-size:22px;margin:0 0 4px}}
.sub{{color:var(--muted);font-size:13px;margin-bottom:20px}}
.meta{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:16px}}
.meta h2{{font-size:14px;margin:0 0 8px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.04em}}
.kv{{margin:6px 0}}.kv b{{color:var(--muted);font-weight:600;margin-right:6px}}
.legend{{display:flex;gap:14px;flex-wrap:wrap;font-size:12.5px;margin:10px 0 0}}
.legend span{{padding:2px 8px;border-radius:5px}}
.pfx-b{{background:#eef4ff;color:#3a63b8}}.body-b{{background:#eafaf0;color:#1f8a4c}}
.sfx-b{{background:#fff4e6;color:#b5701c}}.extra-b{{background:#fdeaf0;color:#c1417a}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}}
td{{border:1px solid var(--line);padding:6px 9px;vertical-align:top}}
td:first-child{{color:var(--muted);white-space:nowrap;font-weight:600}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:12px;border-left:4px solid var(--line)}}
.card.redo{{border-left-color:#d9822b}}.card.keep{{border-left-color:#8b95a1}}.card.ok{{border-left-color:#2e9e5b}}
.chead{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px}}
.cid{{font-size:20px;font-weight:800;background:#1c2127;color:#fff;width:34px;height:34px;border-radius:8px;display:flex;align-items:center;justify-content:center}}
.dur{{font-size:13px;color:var(--muted);font-weight:600}}
.ctag{{font-size:13px;font-weight:600}}
.cstat{{font-size:12px;color:#fff;padding:2px 9px;border-radius:20px;font-weight:600}}
.charlen{{margin-left:auto;font-size:12px;color:var(--muted)}}
.prompt{{font-size:14.5px;line-height:1.85}}
.seg{{border-radius:3px;padding:1px 2px}}
.seg.pfx{{background:#eef4ff}}.seg.body{{background:#eafaf0}}.seg.sfx{{background:#fff4e6}}.seg.extra{{background:#fdeaf0;font-weight:600}}
</style></head><body>
<h1>E222 t2v Prompt 审阅（16 条）</h1>
<div class="sub">生成时间 2026-07-15 · 来源 prompts/t2v_E222.json · 展示的是实际发给 Seedance 的完整 prompt（prefix+分镜+suffix+extra）</div>

<div class="meta">
  <h2>全局参数（每条都带）</h2>
  <div class="kv"><b>模型</b>doubao-seedance-2-0-mini · 720p · 9:16 · generate_audio 同步语音 · duration 按原片 clamp[4,15]</div>
  <div class="kv"><b>参考图</b>refs/product_bra_front.png（正）+ product_bra_back.png（背），role=reference_image</div>
  <div class="kv"><b>prefix</b><span class="pfx-b">{esc(prefix)}</span></div>
  <div class="kv"><b>suffix</b><span class="sfx-b">{esc(suffix)}</span></div>
  <div class="legend"><span class="pfx-b">prefix 全局前缀</span><span class="body-b">分镜台词（逐条）</span><span class="sfx-b">suffix 全局造型/肩带</span><span class="extra-b">extra 逐条覆盖（主体色）</span></div>
</div>

<div class="meta">
  <h2>颜色映射（对着原片扫定·权威色卡）</h2>
  <table>{colormap_rows}</table>
</div>

<div class="meta">
  <h2>图例</h2>
  <div class="kv"><b>待重出</b>主体色/肩带上版没对上，需重跑（橙）：03 / 05 / 14 / 15</div>
  <div class="kv"><b>上版已OK</b>抽帧验过匹配（绿）</div>
  <div class="kv"><b>keeper</b>无内衣本体展示，不受影响不重出（灰）</div>
</div>

{"".join(cards)}
</body></html>'''

out = ROOT / "docs" / "prompt审阅_E222_20260715.html"
out.write_text(doc, encoding="utf-8")
print(f"OK -> {out}  ({len(doc)} bytes)")
