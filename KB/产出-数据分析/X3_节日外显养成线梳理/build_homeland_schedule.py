from __future__ import annotations

import base64
import html
import io
import json
from pathlib import Path

from PIL import Image


ROOT = Path(r"C:\ADHD_agent\KB\产出-数据分析\X3_节日外显养成线梳理")
OUTPUT = ROOT / "X3主城皮肤内容排期_20260805.html"
DATA = ROOT / "x3_other_cosmetic_ownership.json"
ASSETS = {
    "sep_pirate": Path(r"C:\Users\linkang\Pictures\X3验收\X3-9月周年庆\美术需求\主城皮肤\主城皮肤.png"),
    "oct_basic": Path(r"C:\Users\linkang\Pictures\X3验收\X3-10月万圣节\主城皮肤基础主城.png"),
    "oct_set": Path(r"C:\Users\linkang\Pictures\X3验收\X3-10月万圣节\主城皮肤套装效果.png"),
    "nov_dj": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-dnh7uo.png"),
    "dec_a": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-zvnnog.png"),
    "dec_b": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-2FUTlB.png"),
    "dec_c": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-Ytwrfh.png"),
    "activity_pinball": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-DvnKtU.png"),
    "activity_treasure": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-RedFEe.png"),
}


def uri(path: Path, max_height: int = 760) -> str:
    with Image.open(path) as source:
        image = source.convert("RGB")
        if image.height > max_height:
            width = round(image.width * max_height / image.height)
            image = image.resize((width, max_height), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, "WEBP", quality=79, method=6)
    return "data:image/webp;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def main() -> None:
    image = {key: uri(path) for key, path in ASSETS.items()}
    months = [("9月", "周年庆"), ("10月", "万圣节"), ("11月", "感恩节"), ("12月", "圣诞节")]
    heads = "".join(f'<div class="month"><b>{m}</b><span>{f}</span></div>' for m, f in months)

    texture = [
        ("周年贴图主城", "具体基础模型与周年贴图方案待补。", []),
        ("万圣贴图主城", "具体基础模型与万圣贴图方案待补。", []),
        ("感恩节贴图主城", "秋收、麦穗、南瓜与暖棕配色。", []),
        ("圣诞贴图主城", "红绿金灯串、积雪与礼物；独立于3款搬运主城。", []),
    ]
    dynamic = [
        ("黑金海盗船", "高级黑金动态版；补船体、风帆、旗帜与航行动效。", [(image["sep_pirate"], "9月高级黑金海盗船方案卡")]),
        ("宇宙飞船主城套装", "基础/高级主城＋3个组件，集齐后触发终极套装效果。", [(image["oct_basic"], "10月宇宙飞船基础主城"), (image["oct_set"], "10月宇宙飞船套装效果")]),
        ("DJ全息舞台", "保留舞台结构，只把中央全息角色换成X3美女形象。", [(image["nov_dj"], "11月DJ全息舞台")]),
        ("圣诞主城3款组合", "圣诞雪人城堡 / 紫树冬夜城 / 绿树圣诞城，同时作为12月动态/套装内容。", [
            (image["dec_a"], "圣诞雪人城堡"),
            (image["dec_b"], "紫树冬夜城"),
            (image["dec_c"], "绿树圣诞城"),
        ]),
    ]

    def visual(images: list[tuple[str, str]], empty: bool) -> str:
        if len(images) == 1:
            src, alt = images[0]
            return f'<img class="cell-img" src="{src}" alt="{esc(alt)}">'
        if images:
            return '<div class="cell-gallery">' + "".join(
                f'<img src="{src}" alt="{esc(alt)}">' for src, alt in images
            ) + '</div>'
        return '' if empty else '<div class="no-img">贴图参考待补</div>'

    def row(label: str, sub: str, css: str, cells: list[tuple[str, str, list[tuple[str, str]]]]) -> str:
        price = {"texture": "$300", "dynamic": "$800 / $2,000"}.get(css, "")
        result = [f'<div class="lane {css}"><b>{esc(label)}</b><strong>{price}</strong><span>{esc(sub)}</span></div>']
        for title, note, images in cells:
            result.append(
                f'<div class="cell {css}-cell">{visual(images, title == "—")}<b>{esc(title)}</b><span>{esc(note)}</span></div>'
            )
        return "".join(result)

    activity = f'''<div class="lane activity"><b>投放活动</b><span>两套固定骨架</span></div>
    <div class="activity-cell">
      <article><img src="{image['activity_pinball']}" alt="庆典弹弹乐活动"><div><b>庆典弹弹乐</b><span>同一活动内承接跨服榜与每日榜主城奖励；9–12月按节日换包装。</span></div></article>
      <article><img src="{image['activity_treasure']}" alt="节日围寻宝活动"><div><b>节日围寻宝</b><span>承接永久主城大奖及榜单奖励；9–12月按节日换包装。</span></div></article>
    </div>'''

    gantt = (
        '<div class="gantt"><div class="corner">内容类型 / 月份</div>' + heads +
        row("贴图版", "低成本基础主城", "texture", texture) +
        row("动态 / 套装", "当月高规格内容", "dynamic", dynamic) + activity + '</div>'
    )

    raw = json.loads(DATA.read_text(encoding="utf-8"))
    cities = [x for x in raw["items"] if x["module"] == "主城皮肤"]
    rows = "".join(
        f'<tr><td>{esc(x["name"])}</td><td>{esc(x["id"])}</td><td>{x["owners"]:,}</td><td>{x["rate"]:.3f}%</td><td>{len(x["asset_ids"])}</td></tr>'
        for x in cities
    )

    page = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>X3主城皮肤内容排期｜9–12月</title><style>
:root{--ink:#24241f;--muted:#6c6a61;--paper:#f4f0e7;--green:#173f38;--lime:#c7e83f;--line:#dfd4c1}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 "Microsoft YaHei","Noto Sans SC",sans-serif}.page{width:min(1550px,calc(100% - 40px));margin:28px auto 70px}.hero{padding:27px 30px;border-radius:22px;background:linear-gradient(120deg,#173f38,#24584e);color:#fff}.hero small{display:block;color:var(--lime);font-weight:900;letter-spacing:.08em}.hero h1{font:700 39px/1.2 Georgia,"Noto Serif SC",serif;margin:7px 0}.hero p{margin:0;color:#dce8e2}.thesis{margin:18px 0;padding:19px 22px;border-left:6px solid var(--lime);border-radius:13px;background:#fff;font-size:21px;font-weight:900;box-shadow:0 8px 24px #243c3420}.kpis,.price-rules{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin:14px 0}.kpi,.price-rule{padding:15px 17px;border:1px solid var(--line);border-radius:13px;background:#fff}.kpi b{font-size:28px;color:var(--green)}.kpi span,.price-rule span{display:block;color:var(--muted);font-size:14px}.price-rule b{display:block;font-size:22px;color:#9a4719}.price-rule strong{display:block;font-size:16px;color:var(--green);margin:3px 0}.section-title{display:flex;justify-content:space-between;align-items:end;margin:21px 0 10px}.section-title h2{font:700 29px Georgia,"Noto Serif SC",serif;margin:0;color:var(--green)}.section-title span{font-size:14px;color:var(--muted)}.gantt{display:grid;grid-template-columns:130px repeat(4,minmax(260px,1fr));border:1px solid var(--line);border-radius:18px;overflow:auto;background:#fff;box-shadow:0 10px 26px #453a2a12}.gantt>*{border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.gantt>*:nth-child(5n){border-right:0}.corner,.month{padding:15px;background:#2b2d29;color:#fff}.corner{font-size:14px;color:#cdd2cd}.month b{display:block;font-size:24px}.month span{color:#d6ddd9}.lane{padding:18px 12px;display:flex;flex-direction:column;justify-content:center}.lane b{font-size:19px}.lane strong{font-size:16px;margin:3px 0}.lane span{font-size:14px}.texture{background:#dfeee8;color:#16675e}.dynamic{background:#ffeadc;color:#994719}.activity{background:#dfe8f7;color:#284c7d}.cell{padding:13px;min-height:180px}.cell-img{display:block;width:100%;height:180px;object-fit:contain;border-radius:9px;background:#253222;margin-bottom:11px}.cell-gallery{display:grid;grid-template-columns:repeat(3,1fr);gap:5px;margin-bottom:11px}.cell-gallery img{display:block;width:100%;height:180px;object-fit:cover;border-radius:8px;background:#253222}.dynamic-cell .cell-gallery:has(img:nth-child(2):last-child){grid-template-columns:repeat(2,1fr)}.no-img{display:flex;height:100px;align-items:center;justify-content:center;border:1px dashed #b7ad9c;border-radius:9px;color:#81796d;background:#f6f2ea;font-size:14px;margin-bottom:10px}.cell b{display:block;font-size:18px;margin-bottom:7px}.cell span{display:block;font-size:14px;color:var(--muted)}.texture-cell{background:#f7fcfa}.dynamic-cell{background:#fffaf6}.activity-cell{grid-column:span 4;display:grid;grid-template-columns:repeat(2,1fr);gap:12px;padding:14px;background:#f5f8fd}.activity-cell article{display:grid;grid-template-columns:minmax(260px,.9fr) 1fr;gap:14px;align-items:center;padding:12px;border:1px solid #cfdae9;border-radius:12px;background:#fff}.activity-cell img{display:block;width:100%;height:260px;object-fit:contain;border-radius:9px;background:#162237}.activity-cell b{display:block;font-size:19px;color:#284c7d}.activity-cell span{display:block;font-size:14px;color:var(--muted);margin-top:5px}.guard{margin-top:13px;padding:14px 17px;border-radius:12px;background:#173f38;color:#eef5f1;font-size:15px}.guard b{color:var(--lime)}.secondary{margin-top:24px;border:1px solid var(--line);border-radius:17px;background:#fff;overflow:hidden}.secondary>summary{cursor:pointer;padding:18px 21px;font-size:19px;font-weight:900;color:var(--green);background:#faf6ed}.secondary-body{padding:20px}.todo{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.todo div{padding:13px;border-radius:11px;background:#f2eee5}.todo b{display:block}.todo span{display:block;font-size:14px;color:var(--muted)}.table-wrap{overflow:auto;margin-top:18px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:9px 10px;border-bottom:1px solid #e7dfd2;text-align:left;white-space:nowrap}th{background:#edf3ee;color:#173f38}.foot{margin-top:14px;font-size:14px;color:var(--muted)}@media(max-width:1100px){.page{width:min(100% - 20px,1550px)}.gantt{grid-template-columns:110px repeat(4,300px)}.activity-cell article{grid-template-columns:1fr}.activity-cell img{height:220px}}@media(max-width:650px){body{font-size:16px}.hero h1{font-size:31px}.thesis{font-size:18px}.kpis,.price-rules,.todo{grid-template-columns:1fr}}
</style></head><body><main class="page"><header class="hero"><small>X3 · 节日外显模块养成线</small><h1>主城皮肤内容排期｜9–12月</h1><p>内容生产＋定价＋投放活动骨架</p></header><div class="thesis">一句话：每月各有1款$300基础贴图主城；动态版以累计$800作为上榜条件并进入排行榜竞争；完整套装保持$2,000。</div><div class="kpis"><div class="kpi"><b>4款</b><span>基础贴图主城 · 当前均待补方案</span></div><div class="kpi"><b>6款</b><span>动态主城 / 主城套装</span></div><div class="kpi"><b>2套</b><span>固定投放活动骨架</span></div></div><div class="price-rules"><div class="price-rule"><b>$300</b><strong>贴图版主城</strong><span>低成本基础主城固定价格。</span></div><div class="price-rule"><b>$800</b><strong>动态版上榜条件</strong><span>累计达到$800后进入排行榜竞争。</span></div><div class="price-rule"><b>$2,000</b><strong>完整主城套装</strong><span>高级主城$800＋组件$300×2＋主城特效$600，结构保持不变。</span></div></div><div class="section-title"><h2>9–12月主城内容甘特图</h2><span>内容图、价格与投放活动图均在甘特内部</span></div>__GANTT__<div class="guard"><b>11月动态主城改造边界：</b>保留DJ台、灯光、唱盘、全息投影和昼夜切换结构；只把中央全息角色替换为X3美女形象，具体英雄待定。</div><details class="secondary"><summary>二级界面｜查看待补素材与现有主城数据</summary><div class="secondary-body"><div class="todo"><div><b>9月周年 / 10月万圣贴图主城</b><span>现有海盗船和宇宙飞船图均属于动态/套装；两款基础贴图主城另行补图。</span></div><div><b>11月感恩 / 12月圣诞贴图主城</b><span>需确定沿用的基础主城模型与贴图稿。</span></div></div><div class="table-wrap"><table><thead><tr><th>名称</th><th>ID</th><th>获取人数</th><th>获取率</th><th>关联资产数</th></tr></thead><tbody>__ROWS__</tbody></table></div><div class="foot">存量口径：成熟服1000–1880，近30日活跃窗口2026-07-07~2026-08-05，分母16,969人。</div></div></details></main></body></html>'''
    page = page.replace("__GANTT__", gantt).replace("__ROWS__", rows)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"output={OUTPUT}")
    print(f"images={len(image)} cities={len(cities)} size={OUTPUT.stat().st_size:,}")


if __name__ == "__main__":
    main()
