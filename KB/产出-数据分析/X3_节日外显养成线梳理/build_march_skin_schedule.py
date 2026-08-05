from __future__ import annotations

import base64
import io
import json
from pathlib import Path

from PIL import Image


ROOT = Path(r"C:\ADHD_agent\KB\产出-数据分析\X3_节日外显养成线梳理")
SOURCE_HTML = ROOT / "X3节日外显养成线全景_模块页签版_20260804.html"
OUT = ROOT / "X3行军皮肤内容排期_20260805.html"
VOYAGE_SCREEN = Path(r"C:\Users\linkang\Pictures\X3验收\航海大富翁复用\Snipaste_2026-06-02_15-43-39.png")


def read_march_catalog() -> dict[str, dict]:
    source = SOURCE_HTML.read_text(encoding="utf-8")
    marker = "const moduleCatalogs="
    start = source.index(marker) + len(marker)
    catalogs, _ = json.JSONDecoder().raw_decode(source[start:])
    items = catalogs["行军皮肤"]["groups"][0]["items"]
    return {item["name"]: item for item in items}


def image_uri(path: Path) -> str:
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((900, 1200), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=84, method=6)
    return "data:image/webp;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def main() -> None:
    catalog = read_march_catalog()
    schedule = [
        {
            "month": "9月", "festival": "周年庆", "title": "天际船",
            "source_name": "现有资产：天际彩飨", "src": catalog["天际彩飨"]["src"],
            "state": "存量复用", "note": "周年主题船皮，进入9月航海之路兑换。",
        },
        {
            "month": "10月", "festival": "万圣节", "title": "新万圣节行军皮肤",
            "source_name": "方向参考：回声圣鳐（非最终资产）", "src": catalog["回声圣鳐"]["src"],
            "state": "全新制作", "note": "参考亡灵氛围与悬浮轮廓，新做万圣主题船体和动态表现。",
        },
        {
            "month": "11月", "festival": "感恩节", "title": "感恩之翼",
            "source_name": "现有资产 · ShipSkin 9", "src": catalog["感恩之翼"]["src"],
            "state": "存量复用", "note": "感恩节主题船皮，配套普通航迹不纳入本页排期。",
        },
        {
            "month": "12月", "festival": "圣诞节", "title": "极光驯鹿",
            "source_name": "现有资产：极光驯鹿号 · ShipSkin 10", "src": catalog["极光驯鹿号"]["src"],
            "state": "存量复用", "note": "圣诞主题船皮，进入12月航海之路兑换。",
        },
    ]

    heads = "".join(f'<div class="month"><b>{x["month"]}</b><span>{x["festival"]}</span></div>' for x in schedule)
    cells = "".join(f'''<article class="cell"><img src="{x["src"]}" alt="{x["title"]}参考图"><em>{x["state"]}</em><b>{x["title"]}</b><small>{x["source_name"]}</small><p>{x["note"]}</p></article>''' for x in schedule)
    voyage_src = image_uri(VOYAGE_SCREEN)

    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>X3行军皮肤内容排期｜9–12月</title><style>
:root{{--ink:#24241f;--muted:#6c6a61;--paper:#f4f0e7;--green:#173f38;--lime:#c7e83f;--line:#dfd4c1;--gold:#b86424}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 "Microsoft YaHei","Noto Sans SC",sans-serif}}.page{{width:min(1550px,calc(100% - 40px));margin:28px auto 70px}}.hero{{padding:27px 30px;border-radius:22px;background:linear-gradient(120deg,#173f38,#24584e);color:#fff}}.hero small{{display:block;color:var(--lime);font-weight:900;letter-spacing:.08em}}.hero h1{{font:700 39px/1.2 Georgia,"Noto Serif SC",serif;margin:7px 0}}.hero p{{margin:0;color:#dce8e2}}.thesis{{margin:18px 0;padding:19px 22px;border-left:6px solid var(--lime);border-radius:13px;background:#fff;font-size:21px;font-weight:900;box-shadow:0 8px 24px #243c3420}}.summary{{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin:14px 0}}.summary div{{padding:15px 17px;border:1px solid var(--line);border-radius:13px;background:#fff}}.summary b{{display:block;font-size:25px;color:var(--green)}}.summary span{{display:block;color:var(--muted);font-size:14px}}.section-title{{display:flex;justify-content:space-between;align-items:end;margin:21px 0 10px}}.section-title h2{{font:700 29px Georgia,"Noto Serif SC",serif;margin:0;color:var(--green)}}.section-title span{{font-size:14px;color:var(--muted)}}
.gantt{{display:grid;grid-template-columns:130px repeat(4,minmax(250px,1fr));border:1px solid var(--line);border-radius:18px;overflow:auto;background:#fff;box-shadow:0 10px 26px #453a2a12}}.gantt>*{{border-right:1px solid var(--line);border-bottom:1px solid var(--line)}}.gantt>*:nth-child(5n){{border-right:0}}.corner,.month{{padding:15px;background:#2b2d29;color:#fff}}.corner{{font-size:14px;color:#cdd2cd}}.month b{{display:block;font-size:24px}}.month span{{color:#d6ddd9}}.lane{{padding:18px 12px;display:flex;flex-direction:column;justify-content:center;background:#dfeee8;color:#16675e}}.lane b{{font-size:19px}}.lane strong{{font-size:17px;margin:3px 0}}.lane span{{font-size:14px}}.cell{{padding:13px;min-height:355px;background:#f7fcfa}}.cell img{{display:block;width:100%;height:180px;object-fit:contain;border-radius:9px;background:#253222;margin-bottom:11px}}.cell em{{display:inline-block;padding:3px 9px;border-radius:999px;background:#dfeee8;color:#16675e;font-size:14px;font-style:normal;font-weight:900}}.cell b{{display:block;font-size:18px;margin:7px 0 2px}}.cell small{{display:block;font-size:14px;color:var(--gold)}}.cell p{{margin:7px 0 0;color:var(--muted);font-size:14px}}.activity-lane{{background:#dfe8f7;color:#284c7d}}.activity-cell{{grid-column:span 4;display:grid;grid-template-columns:minmax(300px,.8fr) 1.2fr;gap:18px;align-items:center;padding:16px;background:#f5f8fd}}.activity-cell img{{display:block;width:100%;height:310px;object-fit:contain;border-radius:10px;background:#162237}}.activity-cell h3{{margin:0 0 7px;font-size:24px;color:#284c7d}}.activity-cell p{{margin:5px 0;color:var(--muted)}}.price{{display:inline-block;margin-top:9px;padding:8px 12px;border-radius:9px;background:#173f38;color:#fff;font-weight:900}}.price b{{color:var(--lime);font-size:21px}}.guard{{margin-top:13px;padding:14px 17px;border-radius:12px;background:#173f38;color:#eef5f1;font-size:15px}}.guard b{{color:var(--lime)}}.foot{{margin-top:13px;font-size:14px;color:var(--muted)}}@media(max-width:1100px){{.page{{width:min(100% - 20px,1550px)}}.gantt{{grid-template-columns:110px repeat(4,300px)}}.activity-cell{{grid-template-columns:1fr}}}}@media(max-width:650px){{body{{font-size:16px}}.hero h1{{font-size:31px}}.thesis{{font-size:18px}}.summary{{grid-template-columns:1fr}}}}
</style></head><body><main class="page"><header class="hero"><small>X3 · 节日外显模块养成线</small><h1>行军皮肤内容排期｜9–12月</h1><p>月度内容＋统一定价＋投放活动</p></header><div class="thesis">一句话：每月1款节日行军皮肤，统一在航海之路以$100兑换。</div><div class="summary"><div><b>4款</b><span>9–12月每月1款行军皮肤</span></div><div><b>$100</b><span>统一兑换价格</span></div><div><b>航海之路</b><span>唯一投放活动</span></div></div><div class="section-title"><h2>9–12月行军皮肤甘特图</h2><span>每月内容图与活动参考图均在甘特内部</span></div><section class="gantt"><div class="corner">内容类型 / 月份</div>{heads}<div class="lane"><b>行军皮肤</b><strong>$100兑换</strong><span>节日主题船皮</span></div>{cells}<div class="lane activity-lane"><b>投放活动</b><strong>航海之路</strong><span>统一兑换出口</span></div><article class="activity-cell"><img src="{voyage_src}" alt="航海之路活动实机截图"><div><h3>航海之路</h3><p>行军皮肤统一进入航海之路的兑换体系，随当月节日主题更新皮肤内容。</p><p>本页只确定内容、月份、价格与活动；具体兑换币数量及活动数值另案确定。</p><div class="price">行军皮肤统一 <b>$100</b> 兑换</div></div></article></section><div class="guard"><b>模块边界：</b>挖矿小游戏排行榜与$300上榜条件属于航迹／行军特效，不放入本行军皮肤页面。</div><div class="foot">正式ICON来源：X3节日外显养成线资源知识库；10月使用“回声圣鳐”作为亡灵氛围方向参考，非最终资产。</div></main></body></html>'''
    OUT.write_text(page, encoding="utf-8")
    print(f"output={OUT}")
    print(f"cards={len(schedule)} embedded_images={sum(bool(x['src']) for x in schedule)} size={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
