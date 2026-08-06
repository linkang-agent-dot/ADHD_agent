from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image


ROOT = Path(r"C:\ADHD_agent\KB\产出-数据分析\X3_节日外显养成线梳理")
SOURCE_DIR = Path(r"C:\Users\linkang\Pictures\X3验收\行军特效")
MINING_DEMO = ROOT / "_source_trail_mining_demo.png"
OUT = ROOT / "X3航迹皮肤内容排期_20260805.html"

SCHEDULE = [
    ("9月", "周年庆", "璀璨之星", SOURCE_DIR / "行军特效9月.png", "星光、彩虹与庆典轨迹"),
    ("10月", "万圣节", "南瓜恶作剧", SOURCE_DIR / "行军特效10月.png", "南瓜、蝙蝠与紫绿夜色"),
    ("11月", "感恩节", "随乐出征", SOURCE_DIR / "行军特效11月.png", "节拍、霓虹与音乐舞台轨迹"),
    ("12月", "圣诞节", "骇浪狂鲨", SOURCE_DIR / "行军特效12月.png", "巨浪、鲨鱼与深海冲刺"),
]


def image_uri(path: Path, size: tuple[int, int]) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail(size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=84, method=6)
    return "data:image/webp;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def main() -> None:
    heads = "".join(f'<div class="month"><b>{m}</b><span>{festival}</span></div>' for m, festival, *_ in SCHEDULE)
    cells = "".join(
        f'''<article class="cell"><img src="{image_uri(path, (1200, 760))}" alt="{month}{festival}{name}实机图"><em>排行榜航迹</em><b>{name}</b><small>{visual}</small><p>进入当月挖矿小游戏排行榜奖励池。</p></article>'''
        for month, festival, name, path, visual in SCHEDULE
    )
    mining_src = image_uri(MINING_DEMO, (900, 1200))
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>X3航迹皮肤内容排期｜9–12月</title><style>
:root{{--ink:#24241f;--muted:#6c6a61;--paper:#f4f0e7;--green:#173f38;--lime:#c7e83f;--line:#dfd4c1;--blue:#284c7d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 "Microsoft YaHei","Noto Sans SC",sans-serif}}.page{{width:min(1550px,calc(100% - 40px));margin:28px auto 70px}}.hero{{padding:27px 30px;border-radius:22px;background:linear-gradient(120deg,#173f38,#24584e);color:#fff}}.hero small{{display:block;color:var(--lime);font-weight:900;letter-spacing:.08em}}.hero h1{{font:700 39px/1.2 Georgia,"Noto Serif SC",serif;margin:7px 0}}.hero p{{margin:0;color:#dce8e2}}.thesis{{margin:18px 0;padding:19px 22px;border-left:6px solid var(--lime);border-radius:13px;background:#fff;font-size:21px;font-weight:900;box-shadow:0 8px 24px #243c3420}}.summary{{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin:14px 0}}.summary div{{padding:15px 17px;border:1px solid var(--line);border-radius:13px;background:#fff}}.summary b{{display:block;font-size:25px;color:var(--green)}}.summary span{{display:block;color:var(--muted);font-size:14px}}.section-title{{display:flex;justify-content:space-between;align-items:end;margin:21px 0 10px}}.section-title h2{{font:700 29px Georgia,"Noto Serif SC",serif;margin:0;color:var(--green)}}.section-title span{{font-size:14px;color:var(--muted)}}
.gantt{{display:grid;grid-template-columns:130px repeat(4,minmax(250px,1fr));border:1px solid var(--line);border-radius:18px;overflow:auto;background:#fff;box-shadow:0 10px 26px #453a2a12}}.gantt>*{{border-right:1px solid var(--line);border-bottom:1px solid var(--line)}}.gantt>*:nth-child(5n){{border-right:0}}.corner,.month{{padding:15px;background:#2b2d29;color:#fff}}.corner{{font-size:14px;color:#cdd2cd}}.month b{{display:block;font-size:24px}}.month span{{color:#d6ddd9}}.lane{{padding:18px 12px;display:flex;flex-direction:column;justify-content:center;background:#dfeee8;color:#16675e}}.lane b{{font-size:19px}}.lane strong{{font-size:17px;margin:3px 0}}.lane span{{font-size:14px}}.cell{{padding:13px;min-height:355px;background:#f7fcfa}}.cell img{{display:block;width:100%;height:190px;object-fit:cover;border-radius:9px;background:#253222;margin-bottom:11px}}.cell em{{display:inline-block;padding:3px 9px;border-radius:999px;background:#dfeee8;color:#16675e;font-size:14px;font-style:normal;font-weight:900}}.cell b{{display:block;font-size:18px;margin:7px 0 2px}}.cell small{{display:block;font-size:14px;color:#a54b18}}.cell p{{margin:7px 0 0;color:var(--muted);font-size:14px}}.activity-lane{{background:#dfe8f7;color:var(--blue)}}.activity-cell{{grid-column:span 4;display:grid;grid-template-columns:minmax(300px,.8fr) 1.2fr;gap:18px;align-items:center;padding:16px;background:#f5f8fd}}.activity-cell img{{display:block;width:100%;height:330px;object-fit:contain;border-radius:10px;background:#162237}}.activity-cell h3{{margin:0 0 7px;font-size:24px;color:var(--blue)}}.activity-cell p{{margin:5px 0;color:var(--muted)}}.price{{display:inline-block;margin-top:9px;padding:8px 12px;border-radius:9px;background:var(--green);color:#fff;font-weight:900}}.price b{{color:var(--lime);font-size:21px}}.guard{{margin-top:13px;padding:14px 17px;border-radius:12px;background:var(--green);color:#eef5f1;font-size:15px}}.guard b{{color:var(--lime)}}.foot{{margin-top:13px;font-size:14px;color:var(--muted)}}@media(max-width:1100px){{.page{{width:min(100% - 20px,1550px)}}.gantt{{grid-template-columns:110px repeat(4,300px)}}.activity-cell{{grid-template-columns:1fr}}}}@media(max-width:650px){{body{{font-size:16px}}.hero h1{{font-size:31px}}.thesis{{font-size:18px}}.summary{{grid-template-columns:1fr}}}}
</style></head><body><main class="page"><header class="hero"><small>X3 · 节日外显模块养成线</small><h1>航迹皮肤内容排期｜9–12月</h1><p>月度内容＋上榜门槛＋投放活动</p></header><div class="thesis">一句话：每月1款节日航迹皮肤，玩家累计$600获得挖矿排行榜上榜资格，并通过排名竞争获取。</div><div class="summary"><div><b>4款</b><span>9–12月每月1款节日航迹</span></div><div><b>$600</b><span>统一上榜资格门槛</span></div><div><b>挖矿排行榜</b><span>唯一投放方式</span></div></div><div class="section-title"><h2>9–12月航迹内容甘特图</h2><span>四款实机效果与挖矿Demo均在甘特内部</span></div><section class="gantt"><div class="corner">内容类型 / 月份</div>{heads}<div class="lane"><b>航迹皮肤</b><strong>$600上榜</strong><span>排行榜竞争奖励</span></div>{cells}<div class="lane activity-lane"><b>投放活动</b><strong>挖矿排行榜</strong><span>小游戏Demo</span></div><article class="activity-cell"><img src="{mining_src}" alt="挖矿小游戏排行榜Demo"><div><h3>挖矿小游戏排行榜</h3><p>玩家通过坚屏挖矿关卡推进与排行榜竞争获取当月航迹皮肤。</p><p>累计$600只负责解锁上榜资格；最终皮肤仍由排行榜名次决定。</p><div class="price">统一上榜条件 <b>$600</b></div></div></article></section><div class="guard"><b>模块边界：</b>航迹／行军特效走挖矿排行榜；行军皮肤本体走航海之路$100兑换，两者不混用。</div><div class="foot">内容图来源：X3验收 / 行军特效；活动图来源：用户提供的挖矿小游戏Demo。</div></main></body></html>'''
    page = page.replace("坚屏挖矿", "竖屏挖矿")
    OUT.write_text(page, encoding="utf-8")
    print(f"output={OUT}")
    print(f"images={len(SCHEDULE)+1} size={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
