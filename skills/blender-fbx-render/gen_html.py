# -*- coding: utf-8 -*-
"""Generate P2 city-skin resource-structure gallery HTML (style aligned with X3 外显图库)."""
import os, json, re, html

SCRATCH = os.path.dirname(os.path.abspath(__file__))
data = {d['name']: d for d in json.load(open(os.path.join(SCRATCH, 'p2_cityskins.json'), encoding='utf-8'))}
thumbs = json.load(open(os.path.join(SCRATCH, 'p2_thumbs.json'), encoding='utf-8'))
sources = json.load(open(os.path.join(SCRATCH, 'p2_thumb_sources.json'), encoding='utf-8'))

OUT_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术\P2\主城皮肤图库"
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "P2主城皮肤图库_资源结构全集.html")

# (folder, 中文名) grouped by theme
GROUPS = [
 ("g1", "冬季 / 圣诞", [
   ("CitySkinXmas", "圣诞主城(早期)"),
   ("ChristmasSkin2024", "圣诞 2024"),
   ("ChristmasSkin2025", "圣诞 2025"),
   ("IceTiger2025", "冰虎 2025"),
 ]),
 ("g2", "春节", [
   ("SpringFestivalSkin2023", "春节 2023"),
   ("SpringFestivalSkin2024", "春节 2024"),
   ("SpringFestivalSkin2025", "春节 2025"),
 ]),
 ("g3", "情人节", [
   ("ValentineDay", "情人节(早期)"),
   ("ValentineDaySkin", "情人节皮肤"),
   ("ValentineDaySkin2025", "情人节 2025"),
   ("Flame_Heart", "炽焰之心"),
 ]),
 ("g4", "春季 / 复活节", [
   ("EasterSkin", "复活节"),
   ("EasterSkin2025", "复活节 2025"),
   ("ColorfulSpringDay", "缤纷春日"),
   ("MarchCitySkin2026", "三月主城 2026"),
 ]),
 ("g5", "夏日 / 沙滩 / 水上", [
   ("SummerSkin", "夏日(早期)"),
   ("BeachFestival2024", "沙滩节 2024"),
   ("CityHallSwiming", "泳池主城(CityPool)"),
   ("Mayskin2026", "五月主城 2026"),
   ("JuneSkin2025", "六月主城 2025"),
   ("FishingSkin2025", "钓鱼 2025"),
 ]),
 ("g6", "万圣节", [
   ("HalloweenSkin", "万圣节(早期)"),
   ("PumpkinFortress", "南瓜堡垒"),
   ("HalloweenSkin2024", "万圣节 2024"),
   ("HalloweenSkin2025", "万圣节 2025"),
 ]),
 ("g7", "感恩节 / 丰收", [
   ("ThanksgivingSkin", "感恩节(早期)"),
   ("HarvestHouse", "丰收小屋"),
   ("ThanksGiveSkin2024", "感恩节 2024"),
 ]),
 ("g8", "中式节日 / 神话", [
   ("DragonBoatFestivalSkin", "端午(早期)"),
   ("DragonBoatFestivalSkin2024", "端午 2024"),
   ("MidAutumnSkin", "中秋"),
   ("MonkeyKingSkin", "猴王"),
 ]),
 ("g9", "拓荒节", [
   ("PioneeringFestivalBuildSkin", "拓荒节(早期)"),
   ("PioneeringFestival2024Skin", "拓荒节 2024"),
   ("PioneeringFestival2025Skin", "拓荒节 2025"),
 ]),
 ("g10", "科技 / 太空 / 机甲", [
   ("SciencesSkin", "科技节(早期)"),
   ("ScienceSkin2025", "科技节 2025"),
   ("TopTechnology", "顶尖科技"),
   ("CityHallMecha", "机甲主城"),
   ("LandingMoonFestivalSkin", "登月节(早期)"),
   ("LandingMoonFestivalSkin2024", "登月节 2024"),
   ("PlanetSkin2025", "星球 2025"),
 ]),
 ("g11", "周年庆 / 庆典", [
   ("anniversary2024", "周年庆 2024"),
   ("ColorfulCeremony", "缤纷庆典(UiAnniversaryCity)"),
   ("MusicFestivalSkin2025", "音乐节 2025"),
   ("BondsSkin2026", "羁绊 2026"),
 ]),
 ("g12", "玩法主题 / 专属", [
   ("MonopolySkin2026", "大富翁 2026"),
   ("CtiyCarSkin2025", "赛车主城 2025(UiRacecarCity)"),
   ("ChidrenMoneyBaseSkin_Lod", "儿童储蓄罐主题"),
   ("HandofCreation", "创世之手"),
   ("SvipCity", "SVIP 专属主城"),
   ("KvK5CitySkin", "KvK5 赛季皮肤"),
   ("Kvk3LegendOfTheBlueSea", "KvK3 蓝海传说"),
 ]),
]

EXCLUDED = [
 ("MaincitySkin", "默认主城本体(CityShuttleHall lv1/6/12/18/30)"),
 ("CityHallLV6", "主城 LV6 基础模型"),
 ("DrillGround", "校场"), ("ResourceStation", "资源站"), ("SurvivorCamp", "幸存者营地"),
 ("TreasureChest", "宝箱"), ("SecurityBox", "保险箱"), ("SecurityBoxMap", "保险箱(大地图)"),
 ("MonkeyNest", "大地图资源点/遗迹(Food/Iron/Mine/Ruins)"), ("WonderCity", "奇观装饰(怪物/树)"),
 ("Animation", "公共动画(anim)"),
]

def lv_tokens(d):
    """Extract level tokens from High prefabs."""
    toks = []
    for p in d['prefabs_high']:
        m = re.search(r'[Ll][Vv]\s*(\d+(?:\.\d+)?)', p)
        m2 = re.search(r'L(\d)\.prefab$', p)
        if m:
            toks.append(m.group(1))
        elif m2:
            toks.append(m2.group(1))
    return sorted(set(toks), key=float)

def tex_sets(d):
    names = set()
    for t in d.get('textures_common', []):
        m = re.search(r'([^/]+?)_?(Diffuse|Light|Normal|Nromal)', t, re.I)
        if m:
            names.add(m.group(1))
    return len(names)

cards_total = 0
parts = []
parts.append("""<!doctype html><meta charset="utf-8"><title>P2 主城皮肤图库 · 资源结构全集</title><style>
body{font-family:"Microsoft YaHei",sans-serif;background:#f4f5f7;margin:0;padding:24px;color:#222}
h1{font-size:23px}h2{margin-top:38px;border-left:5px solid #4a6cf7;padding-left:10px;font-size:18px}
.d{color:#666;font-size:13px;margin:6px 0 14px;line-height:1.6}
.grid{display:flex;flex-wrap:wrap;gap:14px}
.card{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.1);width:236px;overflow:hidden}
.thumb{display:flex;align-items:center;justify-content:center;height:180px;background:repeating-conic-gradient(#e6e8ec 0 25%,#f2f3f6 0 50%) 50%/16px 16px}
.thumb img{max-width:220px;max-height:176px}
.thumb.miss{color:#bbb;font-size:12px}
.meta{padding:8px 10px;font-size:11px;line-height:1.55}.meta b{font-size:13px}
.sub{color:#888}.pf{color:#4a6cf7;font-family:Consolas,monospace;font-size:10px;word-break:break-all}
.tag{background:#4a6cf7;color:#fff;border-radius:4px;padding:1px 7px;font-size:10px;white-space:nowrap;margin-left:6px}
.tag.old{background:#999}
.src{float:right;font-size:10px;border-radius:4px;padding:0 5px}.src.i{background:#e5f7e9;color:#2c8a43}.src.r{background:#eef1ff;color:#5a6acf}
.toc{background:#fff;border-radius:8px;padding:12px 18px;margin:10px 0 6px;font-size:13px;line-height:2}
.toc a{color:#4a6cf7;text-decoration:none;margin-right:14px}
.path{background:#fffbe6;border:1px solid #f0e0a0;border-radius:6px;padding:10px 14px;margin:0 0 14px;font-size:12px;line-height:1.9;color:#5a4a00}
.path b{color:#7a5d00}.path code{background:#fff3cf;color:#6b5200}
code{background:#eef;border-radius:3px;padding:1px 4px;font-size:12px}
pre{background:#2b2f3a;color:#dce3f0;border-radius:8px;padding:12px 16px;font-size:12px;line-height:1.7;overflow-x:auto}
.excl{background:#fff;border-radius:8px;padding:10px 16px;font-size:12px;color:#777;line-height:1.9}
</style>
""")

n_skins = sum(len(items) for _, _, items in GROUPS)
parts.append(f"<h1>P2 主城皮肤图库 · 资源结构全集（{n_skins} 款）</h1>")
parts.append("""<p class="d">资源实地扫描自 <code>E:\\P2\\client\\client\\Assets\\P2\\Res\\Map\\CityBuildingNew</code>（2026-07-09），只收录<b>主城皮肤</b>（63 个文件夹中排除 11 个功能建筑/基底，见文末）。<br>
缩略图来源两种（卡片右上角有标注）：<b>游戏内美术图标</b>（34款，皮肤目录 Common/Texture 下的 Sprite PNG，即 DK Icon 用图）；无美术图的 19 款老皮肤用 <b>Blender 无头渲染 FBX 模型</b>直出（Diffuse 贴图 + Cycles，非游戏内实际光照）。</p>""")

parts.append("""<div class="path">📁 <b>标准资源结构</b>（新式皮肤，2024 起）<pre>CityBuildingNew/{SkinName}/
├─ Common/                      Fbx 模型 + 共用贴图（Normal 等）
│   ├─ Fbx/  ├─ Texture/  └─ Material/(部分)
├─ High/                        高画质档
│   ├─ {SkinName}Lv1~Lv3.prefab   按主城等级分 2~5 档（部分含 Lv1.5/2.5 半档）
│   ├─ Material/  └─ Texture/     _High 贴图
├─ Low/                         低画质档（同名 prefab + _Low 贴图）
└─ Ui{SkinName}LvX.prefab       UI 3D 展示 prefab（皮肤预览/详情界面 RenderTexture 用；
                                部分用 DK 数字命名，如 Ui151104627.prefab）</pre>
<div>贴图命名：<code>P2_{SkinName}{编号}_Diffuse / _Light / _Normal（_High/_Low）.tga</code>，全部 TGA 源图</div>
<div>⚠️ 老式皮肤（约 2023 前）为<b>单模型无等级分档</b>：High/Low 各 1 个 prefab，卡片标灰色「单模型」；新式按主城等级 2~5 档，换皮时按此区分工作量</div>
<div>⚠️ <b>克隆残留命名坑</b>：部分皮肤 prefab 名是克隆源节日的残留（实锤例：<code>ChristmasSkin2024</code> 文件夹内 prefab 全叫 <code>ThanksGiveSkin2024Lv*.prefab</code>），找资源认<b>文件夹名</b>，别信 prefab 名</div></div>""")

toc = '<div class="toc"><b>目录：</b>'
for gid, gname, items in GROUPS:
    toc += f'<a href="#{gid}">{gname}({len(items)})</a>'
toc += '</div>'
parts.append(toc)

for gid, gname, items in GROUPS:
    parts.append(f'<h2 id="{gid}">{gname} · {len(items)} 款</h2>')
    parts.append('<div class="grid">')
    for folder, cn in items:
        d = data[folder]
        lvs = lv_tokens(d)
        if lvs:
            lv_label = f'<span class="tag">{len(d["prefabs_high"])}档 Lv{lvs[0]}~{lvs[-1]}</span>'
        elif folder == 'ScienceSkin2025':
            lv_label = '<span class="tag">3档 L1/L2/All</span>'
        else:
            lv_label = '<span class="tag old">单模型</span>'
        ui = d['prefabs_root']
        ui_label = f"Ui prefab ×{len(ui)}" if ui else "无 Ui prefab"
        ui_names = html.escape(', '.join(p.replace('.prefab', '') for p in ui[:5]))
        hi = [p.replace('.prefab', '') for p in d['prefabs_high']]
        hi_txt = html.escape(', '.join(hi[:6])) + ('…' if len(hi) > 6 else '')
        t = thumbs.get(folder)
        timg = f'<img src="data:image/png;base64,{t}">' if t else '无贴图'
        tcls = 'thumb' if t else 'thumb miss'
        sinfo = sources.get(folder, {})
        if sinfo.get('kind') == 'icon':
            srclabel, srccls = '游戏内美术图标', 'i'
        else:
            srclabel, srccls = 'Blender模型渲染', 'r'
        cards_total += 1
        parts.append(f'''<div class="card"><div class="{tcls}">{timg}</div><div class="meta">
<b>{folder}</b>{lv_label}<br><span class="sub">{cn}</span><span class="src {srccls}">{srclabel}</span><br>
<span class="pf">High: {hi_txt}</span><br>
<span class="sub">{ui_label}{("：" if ui else "")}</span><span class="pf">{ui_names}</span><br>
<span class="sub">贴图 {d["tex_count"]} 张{(" / " + str(tex_sets(d)) + " 套") if tex_sets(d) else ""} · FBX {d["fbx_count"]} · {d["size_mb"]:.0f} MB</span>
</div></div>''')
    parts.append('</div>')

parts.append('<h2 id="excl">附：已排除的 11 个非皮肤文件夹</h2><div class="excl">')
parts.append(' · '.join(f'<code>{n}</code> {cn}' for n, cn in EXCLUDED))
parts.append('<br>其中 <code>MaincitySkin</code>（CityShuttleHall，默认主城 5 档 lv1/6/12/18/30）是所有皮肤替换的基底本体。</div>')
parts.append(f'<p class="d" style="margin-top:24px">生成于 2026-07-09 · 共 {cards_total} 款皮肤 · 扫描脚本 scan_p2_cityskins.py</p>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(parts))
print('written', OUT, os.path.getsize(OUT) // 1024, 'KB, cards:', cards_total)
