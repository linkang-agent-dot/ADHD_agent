from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image


ROOT = Path(r"C:\ADHD_agent\KB\产出-数据分析\X3_节日外显养成线梳理")
HTML = ROOT / "X3节日外显养成线全景_模块页签版_20260804.html"
IMAGES = {
    "free": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-ddquCm.png"),
    "ladder": Path(r"C:\Users\linkang\AppData\Local\Temp\codex-clipboard-FhnlKR.png"),
    "rank": Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_挖孔搬运\05_界面重做静态图\08_排行榜_v3弹窗.png"),
}


def data_uri(path: Path, max_height: int = 980) -> str:
    with Image.open(path) as source:
        image = source.convert("RGB")
        if image.height > max_height:
            width = round(image.width * max_height / image.height)
            image = image.resize((width, max_height), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, format="WEBP", quality=79, method=6)
    return "data:image/webp;base64," + base64.b64encode(output.getvalue()).decode("ascii")


CSS = r'''
/* HERO_MONTHLY_SCHEDULE_CSS_START */
.month-plan{margin-top:24px;padding:24px;border:1px solid var(--line);border-radius:20px;background:#fffdf8}.month-plan-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.month-plan h3{font:700 29px Georgia,"Noto Serif SC",serif;margin:0 0 7px;color:#173f38}.month-plan-head p{font-size:16px;line-height:1.65;color:var(--muted);margin:0;max-width:850px}.plan-version{flex:0 0 auto;padding:8px 12px;border-radius:999px;background:#173f38;color:#fff;font-size:14px;font-weight:900}.schedule-note{margin:16px 0;padding:14px 16px;border-left:5px solid var(--orange);border-radius:10px;background:#fff0dd;font-size:15px;line-height:1.65}.month-grid{display:grid;gap:14px}.month-card{border:1px solid var(--line);border-radius:18px;overflow:hidden;background:#fff}.month-bar{display:flex;align-items:center;gap:14px;padding:16px 18px;background:#173f38;color:#fff}.month-bar strong{font-size:25px}.month-bar span{font-size:16px;color:#d9e4dd}.tier-row{display:grid;grid-template-columns:118px minmax(190px,.75fr) minmax(260px,1.25fr) minmax(210px,1fr);gap:0;border-top:1px solid #e8dfcf}.tier-row>div{padding:16px;border-left:1px solid #e8dfcf;font-size:15px;line-height:1.55}.tier-row>div:first-child{border-left:0}.tier-name{font-weight:900}.tier-name.free{color:#17746a}.tier-name.paid{color:#b85b1c}.tier-name.rank{color:#8c6811}.hero-choice b{display:block;font-size:18px;color:#222}.hero-choice span,.design-base span{display:block;color:var(--muted);font-size:14px;margin-top:4px}.design-base b{display:block;font-size:16px;color:#173f38}.deliver-form{color:#413d36}.schedule-legend{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:17px 0 0}.schedule-legend div{padding:13px;border-radius:12px;background:#edf3ee;font-size:14px;line-height:1.55}.schedule-legend b{display:block;font-size:16px;color:#173f38;margin-bottom:3px}.shot-section{margin-top:24px}.shot-section h4{font-size:21px;margin:0 0 5px}.shot-section>p{font-size:15px;color:var(--muted);margin:0 0 14px}.shot-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.shot-card{margin:0;padding:13px;border-radius:15px;background:#f3eee3;border:1px solid #e4d8c5}.shot-card img{display:block;width:100%;height:430px;object-fit:contain;border-radius:10px;background:#17120f}.shot-card figcaption{padding:12px 4px 2px;font-size:15px;line-height:1.55}.shot-card figcaption b{display:block;font-size:17px;color:#173f38}.shot-card figcaption span{color:var(--muted);font-size:14px}.missing-shot{margin-top:13px;padding:13px 15px;border:1px dashed #b85b1c;border-radius:12px;color:#7f431f;background:#fff8ee;font-size:15px}.month-check{margin-top:15px;padding:14px 16px;border-radius:12px;background:#173f38;color:#eef5f1;font-size:15px;line-height:1.65}.month-check b{color:#c7e83f}@media(max-width:1050px){.tier-row{grid-template-columns:100px 1fr}.tier-row>div:nth-child(3),.tier-row>div:nth-child(4){grid-column:2}.shot-grid{grid-template-columns:1fr}.shot-card img{height:auto;max-height:760px}.schedule-legend{grid-template-columns:1fr}}@media(max-width:680px){.month-plan{padding:16px}.month-plan-head{display:block}.plan-version{display:inline-block;margin-top:10px}.tier-row{grid-template-columns:1fr}.tier-row>div,.tier-row>div:nth-child(3),.tier-row>div:nth-child(4){grid-column:auto;border-left:0;border-top:1px solid #eee5d6}.tier-row>div:first-child{border-top:0}.month-bar{align-items:flex-start;flex-direction:column;gap:3px}}
/* HERO_MONTHLY_SCHEDULE_CSS_END */
'''


def js_block(images: dict[str, str]) -> str:
    return r'''/* HERO_MONTHLY_SCHEDULE_START */
const heroDeliveryShots={free:"__FREE__",ladder:"__LADDER__",rank:"__RANK__"};
function heroMonthlySchedule(){const rows=[
{month:'9月',festival:'周年庆',free:'仙蒂公主·格蕾丝 / 微醺·哈珀',freeNote:'首批旧皮肤自选箱的周年主推展示位',paid:'赛米拉',paidNote:'96,796人解锁 · 当前D35前传奇覆盖Top1',paidBase:'周年酒会·轻礼服',paidDesign:'复用赛米拉酒馆/宴会角色认知与基础站姿，只换周年礼服、胸针和庆典配色；不做专属视频与技能。',rank:'柳柳',rankNote:'17,027人解锁 · 高覆盖传奇候选',rankBase:'“盛宴礼服·柳柳”周年基底升级',rankDesign:'沿用已有周年宴会轮廓，升级为二周年庆典主礼服；增加入场视频、周年技能演出和本档最高BUFF。'},
{month:'10月',festival:'万圣节',free:'战神·艾丽丝 / 传奇舞者·奥黛丽',freeNote:'旧皮肤自选箱的暗色系主推展示位',paid:'弗莱彻',paidNote:'28,711人解锁 · 当前D35前传奇覆盖Top3',paidBase:'南瓜小红帽·轻换装',paidDesign:'以现有小红帽轮廓为骨，替换南瓜灯、糖果篮、橙黑面料；保持静态换装规格。',rank:'夜玫瑰',rankNote:'13,982人解锁 · 主题适配度最高的传奇候选',rankBase:'暗夜血宴 / 哥特吸血鬼',rankDesign:'以夜玫瑰原生暗黑气质为骨，做血月宴会、蝙蝠入场视频与可激活诅咒技能。'},
{month:'11月',festival:'黑色星期五',free:'海上女王·阿米娜 / 甜心咖啡师·海泽尔',freeNote:'旧皮肤自选箱的经营/交易氛围展示位',paid:'霍普金斯',paidNote:'31,211人解锁 · 当前D35前传奇覆盖Top2',paidBase:'黑金契约·轻装',paidDesign:'优先核验并复用现有“黑金契约”概念资产，以黑金西装、价签和交易筹码完成轻换装。',rank:'琥珀',rankNote:'10,706人解锁 · 高覆盖传奇候选',rankBase:'“魅影魔术师·琥珀”黑金升级',rankDesign:'复用现有0持有的限定魔术师基底与视频资产，改造成黑金拍卖夜旗舰，并补独立技能与最高BUFF。'},
{month:'12月',festival:'圣诞节',free:'白雪公主·格蕾丝 / 史诗舞者·奥黛丽',freeNote:'旧皮肤自选箱的冬日/舞会展示位',paid:'凌霜',paidNote:'21,704人解锁 · 当前D35前传奇覆盖Top4',paidBase:'雪夜礼装·轻换装',paidDesign:'以凌霜原生冷色与基础姿态为骨，加绒领、雪花胸针和红白金节庆配色；不做视频与技能。',rank:'赛米拉',rankNote:'与9月付费档间隔3个月 · 12月当月不重复',rankBase:'冬夜宴会 / “永恒誓约”礼服轮廓',rankDesign:'复用高礼服轮廓与宴会角色认知，升级雪夜入场视频、可激活节庆技能及全年最高BUFF档。'}
];const tier=(kind,name,hero,note,base,design,form)=>`<div class="tier-row"><div class="tier-name ${kind}">${name}</div><div class="hero-choice"><b>${hero}</b><span>${note}</span></div><div class="design-base"><b>${base}</b><span>${design}</span></div><div class="deliver-form">${form}</div></div>`;return `<section class="month-plan"><div class="month-plan-head"><div><h3>9–12月英雄皮肤内容排期</h3><p>按“这批节日每月投谁”规划，而不是单期14D玩家时间轴。每月三档英雄互不重复；$19.99档四个月依次覆盖赛米拉、弗莱彻、霍普金斯、凌霜。</p></div><span class="plan-version">排期建议 v1</span></div><div class="schedule-note"><b>免费池处理建议：</b>当前8款低获取、弱/无BUFF旧皮肤，若一次全塞进同一个箱，后3个月会缺少新的免费档内容。因此排期先按“每月2选1、四个月消化8款”呈现；如果坚持“一次8选1”，建议只在9月首发，10–12月需另补新候选池。</div><div class="month-grid">${rows.map(r=>`<article class="month-card"><div class="month-bar"><strong>${r.month} · ${r.festival}</strong><span>当月三档：免费旧皮复用 / $19.99轻换装 / 排行榜旗舰</span></div>${tier('free','FREE 免费档',r.free,r.freeNote,'已有旧皮肤资产，不新画旗舰规格','仅调整自选箱展示排序与活动包装。','七日活跃累计终奖 · 2选1自选箱')}${tier('paid','$19.99 破冰档',r.paid,r.paidNote,r.paidBase,r.paidDesign,'阶梯礼包第1阶皮肤 $19.99；第2阶头像框 $19.99；第3阶聊天表情 $19.99')}${tier('rank','TOP N 排行榜档',r.rank,r.rankNote,r.rankBase,r.rankDesign,'排行榜大奖 · 专属视频 + 可激活技能 + 最高BUFF')}</article>`).join('')}</div><div class="schedule-legend"><div><b>不重复规则</b>同月免费、19.99、排行榜英雄不重复；跨月优先留冷却期。</div><div><b>选人依据</b>19.99先看英雄解锁覆盖；排行榜还需补出战率/偏好数据验证“人气”。</div><div><b>美术成本控制</b>19.99复用骨架与站姿；排行榜优先升级已有概念/视频资产。</div></div><div class="shot-section"><h4>三档投放形式 · 结构参考</h4><p>截图只说明交互与售卖结构，具体节日美术、奖励内容和文案按当月主题替换。</p><div class="shot-grid"><figure class="shot-card"><img src="${heroDeliveryShots.free}" alt="七日活跃任务投放截图"><figcaption><b>免费档｜七日活跃终奖</b><span>每日开放任务、累计进度、阶段奖励、终点皮肤箱。</span></figcaption></figure><figure class="shot-card"><img src="${heroDeliveryShots.ladder}" alt="19.99三阶礼包投放截图"><figcaption><b>$19.99档｜三阶礼包</b><span>直接复用你给的三柱阶梯结构，三阶均$19.99。</span></figcaption></figure><figure class="shot-card"><img src="${heroDeliveryShots.rank}" alt="排行榜投放结构截图"><figcaption><b>排行榜档｜积分排名大奖</b><span>当前知识库图能说明排行结构，但没有清楚展示英雄皮肤大奖本体。</span></figcaption></figure></div><div class="missing-shot"><b>还需要你补1张：</b>能同时看清“排行榜入口/名次档位 + 英雄皮肤大奖预览”的实机截图。拿到后我会替换右图，并把视频、技能、BUFF入口在图上对应标出来。</div></div><div class="month-check"><b>本版已校验：</b>4个月内每月三档英雄均不重复；$19.99四位高拥有英雄各用一次；排行榜优先选主题匹配且可复用已有皮肤基底的传奇英雄。12月赛米拉与9月赛米拉跨档复用，间隔3个月，如要“四个月所有英雄全局也不重复”，可改为爱莉希雅。</div></section>`}
/* HERO_MONTHLY_SCHEDULE_END */'''.replace("__FREE__", images["free"]).replace("__LADDER__", images["ladder"]).replace("__RANK__", images["rank"])


def replace_marked(text: str, start: str, end: str, replacement: str) -> str:
    if start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        return before + replacement + after
    return text


def main() -> None:
    text = HTML.read_text(encoding="utf-8")
    css_start = "/* HERO_MONTHLY_SCHEDULE_CSS_START */"
    css_end = "/* HERO_MONTHLY_SCHEDULE_CSS_END */"
    if css_start in text:
        text = replace_marked(text, css_start, css_end, CSS.strip())
    else:
        text = text.replace("</style>", CSS + "\n</style>", 1)

    images = {name: data_uri(path) for name, path in IMAGES.items()}
    js = js_block(images)
    js_start = "/* HERO_MONTHLY_SCHEDULE_START */"
    js_end = "/* HERO_MONTHLY_SCHEDULE_END */"
    if js_start in text:
        text = replace_marked(text, js_start, js_end, js)
    else:
        text = text.replace("/* HERO_ITEM_ICONS_START */", js + "\n/* HERO_ITEM_ICONS_START */", 1)

    old = "heroRateDetail()+earlyHeroCatalog()+heroSkinCatalog()"
    new = "heroRateDetail()+earlyHeroCatalog()+heroTierBlueprint()+heroMonthlySchedule()+heroSkinCatalog()"
    text = text.replace(old, new)
    HTML.write_text(text, encoding="utf-8")
    print(f"updated={HTML}")
    print("embedded=" + ",".join(f"{k}:{len(v):,}" for k, v in images.items()))
    print(f"html_size={HTML.stat().st_size:,}")


if __name__ == "__main__":
    main()
