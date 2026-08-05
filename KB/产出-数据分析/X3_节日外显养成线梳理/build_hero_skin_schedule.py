from __future__ import annotations

import base64
import html
import io
import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(r"C:\ADHD_agent\KB\产出-数据分析\X3_节日外显养成线梳理")
SOURCE = ROOT / "X3节日外显养成线全景_模块页签版_20260804.html"
OUTPUT = ROOT / "X3英雄皮肤三档排期_20260805.html"
SHOTS = {
    "免费档｜七日活跃终奖": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-ddquCm.png"),
    "$19.99档｜三阶礼包": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-FhnlKR.png"),
    "排行榜档｜皮肤大奖": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-fWhuCu.png"),
}


def image_uri(path: Path, max_height: int = 940, quality: int = 80) -> str:
    with Image.open(path) as source:
        image = source.convert("RGB")
        if image.height > max_height:
            width = round(image.width * max_height / image.height)
            image = image.resize((width, max_height), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, "WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def extract_json(text: str, prefix: str, suffix: str) -> dict:
    start = text.index(prefix) + len(prefix)
    end = text.index(suffix, start)
    return json.loads(text[start:end])


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    hero_data = extract_json(source, "const earlyHeroData=", ";\n/* EARLY_HERO_DATA_END */")
    item_icons = extract_json(source, "const heroItemIcons=", ";\n/* HERO_ITEM_ICONS_END */")
    heroes = hero_data["heroes"]
    hero_map = {x["name"]: x for x in heroes}
    free_pool = hero_data["free_pool"]
    skin_map = {x["name"]: x for x in free_pool}

    months = [
        {
            "month": "9月", "festival": "周年庆",
            "free": ["仙蒂公主·格蕾丝", "微醺·哈珀"],
            "paid": "柳柳", "paid_base": "周年盛宴·轻礼服",
            "rank": "赛米拉", "rank_base": "全新周年主题｜星光盛典主理人",
        },
        {
            "month": "10月", "festival": "万圣节",
            "free": ["战神·艾丽丝", "传奇舞者·奥黛丽"],
            "paid": "弗莱彻", "paid_base": "南瓜小红帽·轻换装",
            "rank": "夜玫瑰", "rank_base": "全新万圣主题｜暗夜血宴",
        },
        {
            "month": "11月", "festival": "黑色星期五",
            "free": ["海上女王·阿米娜", "甜心咖啡师·海泽尔"],
            "paid": "霍普金斯", "paid_base": "黑金契约·轻装",
            "rank": "琥珀", "rank_base": "全新黑五主题｜黑金拍卖夜",
        },
        {
            "month": "12月", "festival": "圣诞节",
            "free": ["白雪公主·格蕾丝", "史诗舞者·奥黛丽"],
            "paid": "凌霜", "paid_base": "雪夜礼装·轻换装",
            "rank": "柳柳", "rank_base": "全新圣诞主题｜冬日奇境",
        },
    ]

    shot_html = "".join(
        f'<figure><img src="{image_uri(path)}" alt="{esc(label)}"><figcaption><b>{esc(label)}</b><span>结构复用，节日美术与奖励内容按当月替换</span></figcaption></figure>'
        for label, path in SHOTS.items()
    )

    header_cells = "".join(f'<div class="month-head"><b>{x["month"]}</b><span>{x["festival"]}</span></div>' for x in months)

    def free_cell(month: dict) -> str:
        skins = [skin_map[x] for x in month["free"]]
        chips = "".join(
            f'<div class="skin-line"><img src="{item_icons[s["name"]]["src"]}" alt="{esc(s["name"])}道具ICON"><div><b>{esc(s["name"])}</b><span>{esc(s["hero_quality_name"])}英雄 · 获取率{s["rate"]:.2f}% · {esc(s["buff"])}</span></div></div>'
            for s in skins
        )
        return f'<div class="g-cell free-cell">{chips}<em>七日活跃终奖 · 2选1</em></div>'

    def hero_cell(month: dict, kind: str) -> str:
        name = month[kind]
        hero = hero_map[name]
        base = month[f"{kind}_base"]
        if kind == "paid":
            spec = "第1阶皮肤 / 第2阶头像框 / 第3阶表情 · 均$19.99"
            css = "paid-cell"
        else:
            spec = "排行榜现有视频/最高BUFF规格 · 唯一新增：技能可主动激活"
            css = "rank-cell"
        return (
            f'<div class="g-cell {css}"><div class="hero-line"><img src="{hero["icon"]}" alt="{esc(name)}头像">'
            f'<div><b>{esc(name)}</b><span>{hero["hero_owners"]:,}人解锁 · 传奇</span></div></div>'
            f'<strong>{esc(base)}</strong><em>{esc(spec)}</em></div>'
        )

    gantt = (
        '<div class="gantt">'
        '<div class="corner">档位 / 月份</div>' + header_cells +
        '<div class="lane-label free-label"><b>FREE</b><span>免费旧皮</span></div>' + ''.join(free_cell(x) for x in months) +
        '<div class="lane-label paid-label"><b>$19.99</b><span>付费破冰</span></div>' + ''.join(hero_cell(x, "paid") for x in months) +
        '<div class="lane-label rank-label"><b>TOP N</b><span>排行榜旗舰</span></div>' + ''.join(hero_cell(x, "rank") for x in months) +
        '</div>'
    )

    free_cards = "".join(
        f'<article class="pool-card"><img src="{item_icons[x["name"]]["src"]}" alt="{esc(x["name"])}道具ICON"><div><b>{esc(x["name"])}</b><span>{esc(x["hero_quality_name"])}英雄 · {esc(x["hero_name"])}</span><span>获取率 {x["rate"]:.3f}% · {esc(x["buff"])}</span></div></article>'
        for x in free_pool
    )

    hero_cards = "".join(
        f'<article class="hero-card"><img src="{x["icon"]}" alt="{esc(x["name"])}头像"><div><b>{esc(x["name"])}</b><span>{esc(x["quality_name"])}英雄 · {esc(x["display"])}</span><span>{"未纳入专项查询" if x["hero_owners"] is None else f"{x["hero_owners"]:,}人解锁"} · {len(x["skins"])}款皮肤</span></div></article>'
        for x in heroes
    )

    skin_rows = "".join(
        f'<tr><td>{esc(hero["name"])}</td><td>{esc(hero["quality_name"])}</td><td>{esc(skin["name"])}</td><td>{esc(skin["tag"])}</td><td>{skin["owners"]:,}</td><td>{"—" if skin["rate"] is None else f"{skin["rate"]:.3f}%"}</td><td>{esc(skin["buff"])}</td></tr>'
        for hero in heroes for skin in hero["skins"]
    )

    template = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>X3英雄皮肤三档排期｜9–12月</title><style>
:root{--ink:#23231f;--muted:#68675f;--paper:#f4f0e6;--card:#fffdf8;--green:#173f38;--lime:#c7e83f;--orange:#c96427;--gold:#b48a22;--line:#ded4c2}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 "Microsoft YaHei","Noto Sans SC",sans-serif}.page{width:min(1540px,calc(100% - 40px));margin:28px auto 70px}.hero{padding:26px 30px;border-radius:22px;background:var(--green);color:#fff}.hero small{display:block;color:var(--lime);font-weight:900;letter-spacing:.08em}.hero h1{font:700 39px/1.2 Georgia,"Noto Serif SC",serif;margin:7px 0}.hero p{margin:0;color:#dce8e2}.thesis{margin:18px 0;padding:19px 22px;border-left:6px solid var(--lime);border-radius:13px;background:#fff;font-size:21px;font-weight:900;box-shadow:0 8px 24px #243c3420}.thesis em{font-style:normal;color:var(--orange)}.shots{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0 22px}.shots figure{margin:0;padding:14px;border:1px solid var(--line);border-radius:17px;background:var(--card)}.shots img{display:block;width:100%;height:450px;object-fit:contain;border-radius:11px;background:#17120f}.shots figcaption{padding:12px 3px 2px}.shots figcaption b{display:block;font-size:18px}.shots figcaption span{display:block;font-size:14px;color:var(--muted);margin-top:3px}.section-title{display:flex;justify-content:space-between;align-items:end;margin:20px 0 10px}.section-title h2{font:700 29px Georgia,"Noto Serif SC",serif;margin:0;color:var(--green)}.section-title span{font-size:14px;color:var(--muted)}.gantt{display:grid;grid-template-columns:125px repeat(4,minmax(250px,1fr));border:1px solid var(--line);border-radius:18px;overflow:auto;background:#fff;box-shadow:0 10px 26px #453a2a12}.gantt>*{min-width:0;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.gantt>*:nth-child(5n){border-right:0}.corner,.month-head{padding:15px;background:#2b2d29;color:#fff}.corner{font-size:14px;color:#cdd2cd}.month-head b{display:block;font-size:24px}.month-head span{color:#d5ddd8}.lane-label{padding:18px 12px;display:flex;flex-direction:column;justify-content:center}.lane-label b{font-size:20px}.lane-label span{font-size:14px}.free-label{background:#dceee8;color:#12695f}.paid-label{background:#ffeadc;color:#9a4718}.rank-label{background:#f7e9b5;color:#7d5d0e}.g-cell{padding:15px;min-height:174px;background:#fff}.free-cell{background:#f7fcfa}.paid-cell{background:#fffaf6}.rank-cell{background:#fffcf1}.skin-line,.hero-line{display:flex;align-items:center;gap:9px;margin-bottom:9px}.skin-line img{width:48px;height:48px;object-fit:contain}.hero-line img{width:52px;height:52px;border-radius:50%;object-fit:cover;background:#ddd}.skin-line b,.hero-line b{display:block;font-size:16px}.skin-line span,.hero-line span{display:block;font-size:14px;color:var(--muted)}.g-cell>strong{display:block;color:var(--green);font-size:16px;margin:10px 0}.g-cell>em{display:block;font-style:normal;font-size:14px;color:var(--muted);border-top:1px dashed #d9cfbc;padding-top:8px}.decision-note{margin-top:13px;padding:14px 17px;border-radius:12px;background:#173f38;color:#eef5f1;font-size:15px}.decision-note b{color:var(--lime)}.secondary{margin-top:24px;border:1px solid var(--line);border-radius:17px;background:#fff;overflow:hidden}.secondary>summary{cursor:pointer;padding:18px 21px;font-size:19px;font-weight:900;color:var(--green);background:#faf6ed}.secondary-body{padding:20px}.secondary h3{font-size:21px;margin:23px 0 10px}.secondary h3:first-child{margin-top:0}.proof-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.proof{padding:13px;border-radius:11px;background:#eef4ef}.proof b{display:block;font-size:18px}.proof span{display:block;font-size:14px;color:var(--muted)}.pool-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.pool-card,.hero-card{display:flex;align-items:center;gap:10px;padding:11px;border:1px solid var(--line);border-radius:11px}.pool-card img{width:58px;height:58px;object-fit:contain}.pool-card b,.hero-card b{display:block}.pool-card span,.hero-card span{display:block;font-size:14px;color:var(--muted)}.nested{margin-top:16px;border:1px solid var(--line);border-radius:12px}.nested summary{cursor:pointer;padding:14px 16px;font-weight:900}.hero-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;padding:0 14px 14px}.hero-card img{width:52px;height:52px;border-radius:50%;object-fit:cover}.table-wrap{overflow:auto;padding:0 14px 14px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:9px 10px;border-bottom:1px solid #e7dfd2;text-align:left;white-space:nowrap}th{background:#edf3ee;color:#173f38;position:sticky;top:0}.foot{margin-top:17px;color:var(--muted);font-size:14px}@media(max-width:1050px){.page{width:min(100% - 20px,1540px)}.shots{grid-template-columns:1fr}.shots img{height:auto;max-height:760px}.gantt{grid-template-columns:110px repeat(4,270px)}.proof-grid,.pool-grid,.hero-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:620px){body{font-size:16px}.hero{padding:21px}.hero h1{font-size:31px}.thesis{font-size:18px}.proof-grid,.pool-grid,.hero-grid{grid-template-columns:1fr}}
</style></head><body><main class="page"><header class="hero"><small>X3 · 节日外显模块养成线</small><h1>英雄皮肤三档排期｜9–12月</h1><p>决策页 v2 · 2026-08-05</p></header><div class="thesis">一句话分档：<em>免费档</em>用低获取弱BUFF旧皮肤拉七日活跃，<em>$19.99档</em>用高拥有英雄轻换装做节日付费破冰，<em>排行榜档</em>做全新节日主题，沿用视频与最高BUFF规格，本轮只新增“技能可主动激活”。</div><section class="shots">__SHOTS__</section><div class="section-title"><h2>9–12月三档内容甘特图</h2><span>横轴=节日月份 · 纵轴=投放档位</span></div>__GANTT__<div class="decision-note"><b>当前取舍：</b>8款免费旧皮拆成4期、每月2选1，四个月不重复；若坚持9月一次8选1，则10–12月必须另补免费候选池。每月三档英雄互不重复；12月排行榜柳柳与9月$19.99档间隔3个月。</div><details class="secondary"><summary>二级界面｜查看数据依据、免费池与D35前完整资产</summary><div class="secondary-body"><h3>为什么$19.99先用这4位</h3><div class="proof-grid">__PROOFS__</div><p>霍普金斯、弗莱彻、凌霜属于当前高覆盖传奇候选；柳柳用于承接9月周年轻换装，赛米拉则上调为周年排行榜旗舰。英雄解锁数只能证明覆盖规模，排行榜“人气”仍需英雄出战率、偏好/投票或内容互动数据复核。</p><h3>免费档首批8款</h3><div class="pool-grid">__FREE_POOL__</div><details class="nested"><summary>D35前42位英雄池</summary><div class="hero-grid">__HEROES__</div></details><details class="nested"><summary>现有48款皮肤明细</summary><div class="table-wrap"><table><thead><tr><th>英雄</th><th>英雄品质</th><th>皮肤</th><th>皮肤标签</th><th>获取人数</th><th>获取率</th><th>BUFF</th></tr></thead><tbody>__SKIN_ROWS__</tbody></table></div></details><div class="foot">数据口径：D35前严格按D0–D34；英雄解锁人数与皮肤获取率沿用2026-07-29成熟服专项快照。获取率=曾获得皮肤人数÷对应英雄解锁人数。英雄品质与皮肤品质是两条独立轴。</div></div></details></main></body></html>'''

    paid_proofs = "".join(
        f'<div class="proof"><b>{esc(name)}</b><span>{hero_map[name]["hero_owners"]:,}人解锁 · 传奇英雄</span></div>'
        for name in ["柳柳", "霍普金斯", "弗莱彻", "凌霜"]
    )
    page = (template.replace("__SHOTS__", shot_html).replace("__GANTT__", gantt)
            .replace("__PROOFS__", paid_proofs).replace("__FREE_POOL__", free_cards)
            .replace("__HEROES__", hero_cards).replace("__SKIN_ROWS__", skin_rows))
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"output={OUTPUT}")
    print(f"heroes={len(heroes)} skins={sum(len(x['skins']) for x in heroes)} free_pool={len(free_pool)} size={OUTPUT.stat().st_size:,}")


if __name__ == "__main__":
    main()
