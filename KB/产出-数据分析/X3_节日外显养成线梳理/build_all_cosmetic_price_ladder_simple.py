from __future__ import annotations

import html
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "X3全部外显价格梯度一图_20260805.html"
HERO_PAGE = ROOT / "X3英雄皮肤三档排期_20260805.html"
CITY_PAGE = ROOT / "X3主城皮肤内容排期_20260805.html"
sys.path.insert(0, str(ROOT))

from enrich_other_cosmetic_catalogs import build as build_catalogs  # noqa: E402


def page_images(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    return {
        alt: src
        for src, alt in re.findall(
            r'<img[^>]*src="(data:[^"]+)"[^>]*alt="([^"]*)"', source
        )
    }


def catalog_items(catalogs: dict, module: str) -> list[dict]:
    return [item for group in catalogs[module]["groups"] for item in group["items"]]


def first(catalogs: dict, module: str, *, meta: str | None = None, index: int = 0) -> dict:
    items = catalog_items(catalogs, module)
    if meta:
        items = [item for item in items if item.get("meta") == meta]
    return items[index]


def image_tag(src: str, alt: str) -> str:
    return f'<img src="{src}" alt="{html.escape(alt)}" loading="eager">'


def row(index: int, tone: str, price: str, lines: str, pictures: list[tuple[str, str]], badge: str = "") -> str:
    gallery = "".join(image_tag(src, alt) for src, alt in pictures)
    badge_html = f'<span class="badge">{badge}</span>' if badge else ""
    return f'''<article class="tier {tone}">
      <div class="order">{index:02d}</div>
      <div class="gallery">{gallery}</div>
      <div class="price-block"><div class="price">{price}</div>{badge_html}</div>
      <div class="lines">{lines}</div>
    </article>'''


def build() -> None:
    catalogs = build_catalogs()
    heroes = page_images(HERO_PAGE)
    city_refs = page_images(CITY_PAGE)

    old_skin_alt = next(name for name in heroes if name.endswith("道具ICON"))
    card = first(catalogs, "纪念卡")
    furniture = first(catalogs, "家具")
    frame = first(catalogs, "头像框")
    emoji = first(catalogs, "聊天表情")
    door = first(catalogs, "装饰三件套", meta="横梁")
    march = first(catalogs, "行军皮肤")
    trail = first(catalogs, "航迹")
    cities = catalog_items(catalogs, "主城皮肤")
    title = first(catalogs, "称号 / 铭牌")

    rows = [
        row(1, "free", "FREE", "纪念卡获取 · 稀有/史诗老皮肤自选", [
            (card["src"], card["name"]), (heroes[old_skin_alt], old_skin_alt)
        ]),
        row(2, "light", "$19.99", "英雄节日装扮 · 家具 · 头像框 · 聊天表情", [
            (heroes["$19.99档｜三阶礼包"], "$19.99英雄节日装扮"),
            (furniture["src"], furniture["name"]),
            (frame["src"], frame["name"]),
            (emoji["src"], emoji["name"]),
        ]),
        row(3, "mid", "$100", "门头（装饰三件套） · 行军皮肤", [
            (door["src"], door["name"]), (march["src"], march["name"])
        ]),
        row(4, "mid", "$300", "贴图版主城", [(cities[0]["src"], cities[0]["name"])]),
        row(5, "gate", "$600", "排行榜英雄皮肤 · 动态版主城 · 航迹", [
            (heroes["排行榜档｜皮肤大奖"], "排行榜英雄皮肤"),
            (cities[1]["src"], cities[1]["name"]),
            (trail["src"], trail["name"]),
        ], "上榜"),
        row(6, "top", "$2,000", "完整主城套装", [
            (city_refs["10月宇宙飞船套装效果"], "宇宙飞船完整主城套装参考")
        ]),
        row(7, "rank", "TOP N", "称号 / 铭牌", [(title["src"], title["name"])], "无固定价"),
    ]

    document = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>X3 全部外显价格梯度一图</title>
<style>
:root{{--ink:#172224;--paper:#f3efe5;--cream:#fffaf0;--deep:#143f42;--orange:#dc6038;--gold:#d4a13e;--line:#c9bfad;--red:#762f2c}}
*{{box-sizing:border-box}}html,body{{margin:0;min-height:100%;background:#d9d2c6;color:var(--ink)}}
body{{font-family:"Microsoft YaHei UI","PingFang SC","Noto Sans CJK SC",sans-serif;padding:18px}}
.sheet{{width:min(1740px,calc(100vw - 36px));margin:auto;padding:34px 42px 42px;background:var(--paper);border:1px solid #b9ae9c;box-shadow:0 24px 80px rgba(24,41,42,.17)}}
header{{display:flex;align-items:end;justify-content:space-between;gap:24px;padding-bottom:18px;border-bottom:3px solid var(--deep)}}
.eyebrow{{color:var(--orange);font:800 13px/1.2 Georgia,serif;letter-spacing:.19em}}h1{{margin:7px 0 0;font:700 38px/1.1 Georgia,"STSong",serif;letter-spacing:-.03em}}
.stamp{{color:#69726f;font-size:14px;white-space:nowrap}}.ladder{{display:flex;flex-direction:column;gap:9px;margin-top:18px}}
.tier{{min-height:126px;display:grid;grid-template-columns:54px 350px 250px 1fr;align-items:center;gap:22px;padding:12px 30px 12px 18px;background:rgba(255,250,240,.88);border:1px solid var(--line);border-left:8px solid #50766c;position:relative;overflow:hidden}}
.order{{font:700 18px/1 Georgia,serif;color:#89908a;text-align:center}}.gallery{{height:100px;display:flex;align-items:center;gap:10px;overflow:hidden}}
.gallery img{{width:100px;height:100px;object-fit:cover;background:#e8e1d5;border:1px solid #b9ad9a;box-shadow:0 6px 14px rgba(23,34,36,.13)}}
.gallery img:first-child:nth-last-child(1){{width:150px}}.price-block{{display:flex;align-items:center;gap:12px}}.price{{font:700 38px/1 Georgia,serif;letter-spacing:-.04em;white-space:nowrap}}
.badge{{display:inline-flex;padding:5px 9px;border:1px solid currentColor;border-radius:999px;color:#a6412e;font-size:14px;font-weight:900;white-space:nowrap}}
.lines{{font-size:24px;font-weight:900;line-height:1.35;letter-spacing:.01em}}.light{{border-left-color:#bb6b3f}}.mid{{border-left-color:#28585b}}
.gate{{background:#fff0e6;border-color:#da7b5c;border-left-color:var(--orange)}}.top{{color:#fff8e9;background:var(--deep);border-color:var(--deep);border-left-color:var(--gold)}}
.top .order{{color:#adc0ba}}.rank{{color:#fff8e9;background:var(--red);border-color:var(--red);border-left-color:#ffb86d}}.rank .order{{color:#ddb3a7}}.rank .badge{{color:#ffd09a}}
@media(max-width:1050px){{.tier{{grid-template-columns:42px 260px 190px 1fr;gap:14px}}.gallery{{height:82px}}.gallery img{{width:82px;height:82px}}.lines{{font-size:19px}}.price{{font-size:31px}}}}
@media(max-width:720px){{body{{padding:6px}}.sheet{{width:100%;padding:22px 14px}}header{{display:block}}.stamp{{margin-top:8px}}h1{{font-size:30px}}.tier{{grid-template-columns:34px 1fr;padding:12px;border-left-width:6px}}.gallery{{grid-column:2;height:auto;overflow:visible;flex-wrap:wrap}}.gallery img{{width:64px;height:64px}}.price-block,.lines{{grid-column:2}}.lines{{font-size:18px}}}}
@media print{{html,body{{background:#fff}}body{{padding:0}}.sheet{{width:100%;border:0;box-shadow:none}}}}
</style></head>
<body><main class="sheet"><header><div><div class="eyebrow">X3 · FESTIVAL COSMETICS</div><h1>全部外显价格梯度</h1></div><div class="stamp">由小到大 · 当前规划口径 · USD</div></header><section class="ladder">{"".join(rows)}</section></main></body></html>'''
    OUTPUT.write_text(document, encoding="utf-8", newline="\n")
    print(f"output={OUTPUT}")
    print(f"tiers={len(rows)} size={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    build()
