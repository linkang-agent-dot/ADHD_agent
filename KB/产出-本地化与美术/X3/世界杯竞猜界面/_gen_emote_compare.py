# -*- coding: utf-8 -*-
"""现有Emoticons(22) vs 世界杯支持表情试点(4) 对比页。"""
import os, base64
EXIST = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\支持表情48_试点\_现有Emoticons对比"
PILOT = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\世界杯竞猜界面\支持表情48_试点"
OUT   = os.path.join(PILOT, "对比_现有vs世界杯.html")

# 现有表情 资源名→中文名
NAMES = {
 "Bella01":"欢庆·贝拉","Bella02":"害羞·贝拉","Bella03":"点赞·贝拉","Bella04":"震惊·贝拉","Bella05":"疑惑·贝拉",
 "Harper01":"举杯·哈珀","nurse01":"打针·护士","Pirate01":"吃月饼·海盗","Pirate02":"上!·海盗","Amina01":"下劈·阿米娜",
 "molly01":"祝福·茉莉","Rabbit01":"兔子!","Dancer01":"跳舞·舞者","Grace01":"开心·格蕾丝","Grace02":"大哭·格蕾丝",
 "squirrel01":"吓!·松鼠","Ashton":"战斗!·阿什顿","Violet01":"祈祷·紫罗兰","Musket01":"送礼","2026":"烟花(文字)",
 "cat":"猫神之舞","Marry01":"嫁给我!",
}
def b64(p): return base64.b64encode(open(p,"rb").read()).decode()
def card(p, label, sub=""):
    return (f'<div class="c"><div class="t"><img src="data:image/png;base64,{b64(p)}"></div>'
            f'<div class="m"><b>{label}</b><br><span>{sub}</span></div></div>')

exist_cards=[]
for fn in sorted(os.listdir(EXIST)):
    if fn.endswith(".png"):
        key = fn.replace("icon_global_","").replace(".png","")
        exist_cards.append(card(os.path.join(EXIST,fn), NAMES.get(key, key), key))

pilot_cards=[]
for code in ["GER","JPN","FRA","ENG"]:
    p=os.path.join(PILOT,f"WC_Emote_{code}.png")
    if os.path.exists(p): pilot_cards.append(card(p, code, "世界杯试点"))

html=f'''<!doctype html><html lang=zh><meta charset=utf-8><title>表情对比</title><style>
body{{font-family:"Microsoft YaHei";background:#f4f5f7;margin:0;padding:24px}}
h1{{font-size:21px}}h2{{margin-top:28px;border-left:5px solid #4a6cf7;padding-left:10px}}
.d{{color:#666;font-size:13px;margin:6px 0 14px;max-width:900px;line-height:1.6}}
.g{{display:flex;flex-wrap:wrap;gap:12px}}
.c{{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.1);width:130px;overflow:hidden}}
.t{{height:130px;display:flex;align-items:center;justify-content:center;background:repeating-conic-gradient(#e6e8ec 0 25%,#f2f3f6 0 50%) 50%/16px 16px}}
.t img{{max-width:92%;max-height:92%}}
.m{{padding:6px 8px;font-size:12px}}.m b{{font-size:13px}}.m span{{color:#999;font-size:10px}}
.warn{{background:#fff6e0;border-left:4px solid #f0a500;padding:10px 14px;border-radius:6px;font-size:13px;max-width:900px;line-height:1.6}}
</style>
<h1>X3 聊天表情对比 · 现有 vs 世界杯支持表情试点</h1>
<div class="warn"><b>画风差异（对比重点）：</b>现有 22 个表情是 <b>Q版角色半身立绘</b>（英雄做表情动作）+ 少量纯文字；世界杯试点是 <b>队徽+彩带氛围</b>（盾徽主体）。两者风格不同——世界杯要"应援本队"，盾徽路线队伍识别强、可复用已做好的48队徽、零角色绘制成本；若要贴合现有画风则需为48队各画Q版角色/吉祥物（成本极高）。</div>
<h2>① 现有可售卖表情 Emoticons（22个，256×256，节日/英雄主题）</h2>
<p class="d">走 154xx 表情包道具售卖。画风=Q版角色半身（贝拉/猫神/舞者…）或纯文字（HAPPY NEW YEAR）。</p>
<div class="g">{''.join(exist_cards)}</div>
<h2>② 世界杯支持表情 试点（4个，队徽+加油元素）</h2>
<p class="d">队色放射光晕+彩带+闪光，队徽缩80%当主体。可批量套版到48队、复用现成队徽。</p>
<div class="g">{''.join(pilot_cards)}</div>
</html>'''
open(OUT,"w",encoding="utf-8").write(html)
print("OUT:",OUT,"| 现有",len(exist_cards),"试点",len(pilot_cards))
