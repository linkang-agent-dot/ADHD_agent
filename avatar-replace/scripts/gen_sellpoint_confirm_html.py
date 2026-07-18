"""卖点确认页生成器（出片流程 v2 第 0 步的交付物）。

读 prompts json 里每条的 `卖点` 字段 + 原片抽帧，生成一张给需求方看的确认 HTML：
原片关键帧图 + 卖点注意点 + 每张卡一个可直接打字的反馈框（contenteditable），
右上角「复制全部反馈」一键汇总。需求方逐条回「确认/改XX」后才写 prompt 开跑。

用法:
  python scripts/gen_sellpoint_confirm_html.py --ids 03,05,15 \
      --src-dir "E:/222/开头" --out "E:/222/卖点确认_03_05_15.html"
原片文件名默认 = int(id).mp4（3.mp4）；帧抽 4 张（首/1/3、2/3/尾）内嵌 base64。
"""
import argparse, base64, json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def probe_dur(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True)
    return float(out.stdout.strip())


def grab_frames(video: Path, n=4, width=260) -> list:
    dur = probe_dur(video)
    ts = [dur * f for f in (0.02, 0.33, 0.66, 0.96)][:n]
    imgs = []
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate(ts):
            fp = Path(td) / f"f{i}.jpg"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video),
                            "-frames:v", "1", "-vf", f"scale={width}:-1", str(fp)], check=True)
            b64 = base64.b64encode(fp.read_bytes()).decode()
            imgs.append(f"data:image/jpeg;base64,{b64}")
    return imgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(ROOT / "prompts" / "t2v_E222.json"))
    ap.add_argument("--ids", required=True, help="逗号分隔，如 03,05,15")
    ap.add_argument("--src-dir", required=True, help="原片目录，文件名=int(id).mp4")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    data = json.loads(Path(a.json).read_text(encoding="utf-8"))
    ids = [i.strip() for i in a.ids.split(",") if i.strip()]
    clips = {c["id"]: c for c in data["clips"]}
    cards = []
    for cid in ids:
        c = clips[cid]
        sp = c.get("卖点", {})
        video = Path(a.src_dir) / f"{int(cid)}.mp4"
        frames = grab_frames(video) if video.exists() else []
        frames_html = "".join(f'<img src="{u}">' for u in frames)
        rows = "".join(
            f'<div class="row"><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div></div>'
            for k, v in sp.items())
        cards.append(f'''
  <div class="card" data-cid="{cid}">
    <div class="head"><span class="cid">{cid}</span><span class="dur">{c.get("dur","")}s</span>
      <span class="hint">原片关键帧（首→尾）</span></div>
    <div class="frames">{frames_html}</div>
    {rows}
    <div class="row fb"><div class="k">📝 你的反馈</div>
      <div class="v edit" contenteditable="true" data-ph="没问题就写「确认」；要改直接在这里打字…"></div></div>
  </div>''')

    html = f'''<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>卖点确认页 · {esc(a.ids)}</title><style>
body{{font-family:"Microsoft YaHei",sans-serif;background:#f5f6f8;margin:0;padding:24px;color:#222}}
h1{{font-size:20px}} .tip{{color:#666;font-size:13px;margin-bottom:16px}}
.card{{background:#fff;border-radius:12px;padding:16px 18px;margin-bottom:18px;box-shadow:0 1px 4px rgba(0,0,0,.08);max-width:1100px}}
.head{{display:flex;gap:10px;align-items:center;margin-bottom:8px}}
.cid{{background:#2456d6;color:#fff;border-radius:6px;padding:2px 10px;font-weight:700}}
.dur{{color:#888;font-size:13px}} .hint{{color:#aaa;font-size:12px}}
.frames{{display:flex;gap:6px;overflow-x:auto;margin-bottom:10px}}
.frames img{{border-radius:6px;max-height:300px}}
.row{{display:flex;border-top:1px dashed #eee;padding:7px 0;font-size:14px;line-height:1.7}}
.k{{flex:0 0 110px;color:#2456d6;font-weight:600}} .v{{flex:1}}
.fb .k{{color:#c1417a}}
.edit{{min-height:34px;border:1.5px solid #f0c2d4;border-radius:8px;padding:6px 10px;background:#fffafc;outline:none}}
.edit:empty:before{{content:attr(data-ph);color:#bbb}}
#copybtn{{position:fixed;top:18px;right:24px;background:#2456d6;color:#fff;border:none;border-radius:8px;padding:10px 16px;font-size:14px;cursor:pointer}}
</style></head><body>
<h1>🎯 卖点确认页（出片前门禁）</h1>
<div class="tip">看每条的原片帧和卖点注意点 → 没问题在反馈框写「确认」，要改直接打字（写完 Ctrl+S 存回这个文件发我，或点右上角复制全部反馈粘给我）。确认前不开跑，不烧钱。</div>
<button id="copybtn" onclick="copyFb()">复制全部反馈</button>
{''.join(cards)}
<script>
function copyFb(){{
  let out=[];
  document.querySelectorAll('.card').forEach(c=>{{
    let t=c.querySelector('.edit').innerText.trim();
    out.push(c.dataset.cid+': '+(t||'（未填）'));
  }});
  navigator.clipboard.writeText(out.join('\\n')).then(()=>{{document.getElementById('copybtn').innerText='已复制 ✓';}});
}}
</script></body></html>'''
    Path(a.out).write_text(html, encoding="utf-8")
    print(f"OK -> {a.out}")


if __name__ == "__main__":
    main()
