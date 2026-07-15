# -*- coding: utf-8 -*-
"""马戏节美术总评审页生成器：扫四个产出目录,按 NOTES 标注 FINAL/候选/废弃,重跑即最新。
终选后把选定项的 note 改成 FINAL、落选改废弃,重跑本脚本。"""
import os, html, io
ROOT = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\马戏节"
SECS = [
    ("皮肤主稿（大奖·阿米娜猛兽驯服者）", "皮肤主稿", {"Amina_BeastTamer_master_v1.png": "主稿 v1 · 待终审→三件套+视频"}),
    ("道具定稿（✅用户已过审=FINAL）", "道具定稿", {"circus_box_close.png": "福箱·关 FINAL", "circus_box_open.png": "福箱·开 FINAL", "circus_ticket_icon.png": "门票1209 FINAL", "circus_medal_icon.png": "勋章1210 FINAL"}),
    ("地块与图标（wave1+2·待终选）", "地块与图标", None),
    ("活动背景（v1 QA过筛+v2 道具锚重做·待终选）", "活动背景", None),
]
NOTES = {
    "img_Activity_circus_island_start.png": "大富翁地块·巡游大门（起点格）",
    "img_Activity_circus_island_lucky.png": "大富翁地块·彩球摊（幸运格）",
    "img_Activity_circus_island_mystery.png": "大富翁地块·小丑迷阵（神秘格）",
    "img_Activity_circus_island_treasure.png": "大富翁地块·魔术宝箱（宝藏格）",
    "img_Activity_circus_island_diamond.png": "大富翁地块·钻石格",
    "img_Activity_circus_hud_icon.png": "主hub入口图标（142马戏节）",
    "img_Activity_icon_Monopoly_circus.png": "第二hub入口图标（143马戏巡游）",
    "img_Activity_circus_box_icon.png": "福箱活动HUD图标",
    "img_Activity_circus_fund_icon.png": "累充活动HUD图标",
    "img_Activity_circus_bp_icon.png": "BP活动HUD图标（双BP共用）",
    "img_Activity_circus_schedule_icon.png": "每日礼包活动HUD图标",
    "img_Activity_circus_visit_icon.png": "拜访活动HUD图标",
    "img_Activity_circus_wishpool_icon.png": "许愿池活动HUD图标",
    "img_Activity_circus_puzzle.png": "拼图封面·小丑的梦境（切5x5）",
    "img_Activity_circus_icon_decor.png": "装饰礼包页签图标",
    "icon_island_Circus.png": "主城皮肤·梦幻旋转木马 2D头像图标",
    "img_Activity_circus_visit_bg.png": "拜访活动bg·主图",
    "img_Activity_circus_weekcard_bg.png": "周卡活动bg",
    "img_Activity_circus_tavern_bg_1.png": "酒馆活动bg·候选1（QA视觉推荐）",
    "img_Activity_circus_exchange_bg.png": "兑换商店bg（两集市共用）",
    "img_Activity_circus_monopoly_bg_alt.png": "大富翁地图bg·alt（QA推荐）",
    "img_Activity_circus_bp_bg_v2.png": "BP活动bg·v2（通行证+勋章中心物件）",
    "img_Activity_circus_schedule_bg_v2.png": "每日礼包bg·v2（门票礼盒中心物件）",
    "img_Activity_circus_box_bg.png": "福箱活动bg（替代原转盘bg）",
    "img_Activity_circus_wishpool_bg.png": "许愿池活动bg（喷泉件另出）",
    "img_Activity_circus_wishpool_fountain.png": "许愿池喷泉件·主图（⚠️贝壳纹）",
    "img_Activity_circus_wishpool_fountain_alt.png": "许愿池喷泉件·alt（QA推荐）",
    "img_Activity_circus_fund_bg.png": "累充活动bg·主图",
    "img_Activity_circus_fund_bg_alt.png": "累充活动bg·alt（下方留白大）",
    "img_Activity_circus_tavern_bg.png": "酒馆活动bg·主图（压字多选这张）",
    "img_Activity_circus_monopoly_bg.png": "大富翁地图bg·主图（⚠️疑似潜艇→建议alt）",
    "img_Activity_circus_visit_bg_cand1.png": "拜访活动bg·候选1",
    "img_Activity_circus_visit_bg_cand2.png": "拜访活动bg·候选2（QA推荐）",
    "img_card_image_81.png": "纪念卡卡面·欢乐颂歌(补漏)",
    "icon_global_circustitle.png": "头衔道具图标(补漏)",
    "circus_icon_title.png": "铭牌大图(补漏)",
    "Img_Player_AvatarFrame_circus.png": "头像框·欢庆之环(补漏·配置已修BP残留)",
    "img_Activity_circus_tavern_icon.png": "酒馆HUD图标(反查补)",
    "img_Activity_circus_exchange_icon.png": "兑换HUD图标(反查补)",
    "icon_global_circus_invitation.png": "邀请函道具图标(反查补)",
    "img_Activity_circus_wishpool_bg.png": "许愿池活动bg(反查补)",
    "img_Activity_circus_schedule_bg.png": "v1 ❌藏宝图残留→已被 v2 替代", "img_Activity_circus_schedule_bg_v2.png": "v2 道具锚重做 ✔候选",
    "img_Activity_circus_bp_bg.png": "v1 ❌罗盘残留→已被 v2 替代", "img_Activity_circus_bp_bg_cand1.png": "v1备选 ❌罗盘",
    "img_Activity_circus_bp_bg_v2.png": "v2 道具锚重做 ✔候选",
    "img_Activity_circus_turntable_bg.png": "❌转盘已废(玩法改开箱)→box_bg 替代", "img_Activity_circus_turntable_bg_alt2.png": "❌同左",
    "img_Activity_circus_box_bg.png": "开箱活动bg ✔候选(替代转盘)",
    "img_Activity_circus_monopoly_bg.png": "v1 ⚠️疑似潜艇→建议用alt", "img_Activity_circus_monopoly_bg_alt.png": "QA推荐 ✔",
    "img_Activity_circus_visit_bg_cand1.png": "可用", "img_Activity_circus_visit_bg_cand2.png": "QA推荐 ✔",
    "img_Activity_circus_wishpool_fountain.png": "⚠️贝壳纹", "img_Activity_circus_wishpool_fountain_alt.png": "QA推荐 ✔",
    "img_Activity_circus_wishpool_fountain_raw.png": "raw留底不上",
    "img_Activity_circus_tavern_bg.png": "压字多选这张", "img_Activity_circus_tavern_bg_1.png": "QA视觉推荐 ✔",
    "img_Activity_circus_fund_bg.png": "主图", "img_Activity_circus_fund_bg_alt.png": "列表高选alt",
}
parts, total = [], 0
for title, sub, fixed in SECS:
    d = os.path.join(ROOT, sub)
    files = sorted(f for f in os.listdir(d) if f.endswith(".png") and "_raw_0" not in f)
    cells = []
    for f in files:
        note = (fixed or {}).get(f) or NOTES.get(f, "")
        note = note or "（未标注·按文件名对照美术清单）"
        cells.append('<figure><img src="%s/%s" loading="lazy"><figcaption>%s<br><small>%s</small></figcaption></figure>' % (sub, f, html.escape(note), html.escape(f)))
        total += 1
    parts.append('<h2>%s <small>%d 张</small></h2><div class="grid">%s</div>' % (html.escape(title), len(files), "".join(cells)))
page = ('<!doctype html><meta charset="utf-8"><title>马戏节美术总评审</title><style>'
 'body{font-family:system-ui;background:#1a1a20;color:#eee;margin:24px}h1{font-size:20px}h2{font-size:15px;border-left:4px solid #e0a13a;padding-left:8px;margin-top:24px}small{color:#999;font-weight:normal}'
 '.grid{display:flex;gap:14px;flex-wrap:wrap}figure{margin:0;text-align:center;max-width:260px}'
 'img{max-height:300px;max-width:250px;border-radius:8px;background:repeating-conic-gradient(#33333c 0 25%,#26262e 0 50%) 0 0/20px 20px}'
 'figcaption{font-size:12px;margin-top:4px}</style>'
 '<h1>X3 马戏节 · 美术总评审（全资产 ' + str(total) + ' 张）</h1>'
 '<p>标注：FINAL=已定稿 ｜ ✔候选/推荐=待终选 ｜ ❌=废弃 ｜ ⚠️=有瑕疵可选 alt。</p>' + "".join(parts))
out = os.path.join(ROOT, "_美术总评审.html")
io.open(out, "w", encoding="utf-8").write(page)
print(out, total)
