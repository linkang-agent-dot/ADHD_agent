# -*- coding: utf-8 -*-
"""生成 X3 节日外显图库 HTML（白皮书 8 大模块全集 + 行军皮肤）。
数据源：x3_festival_cosmetics_whitepaper.md
       + Item__Item.tsv / Skin__Skin.tsv / Ship__ShipSkin.tsv
       + Hero__HeroSkin.tsv / FurnitureDecorate__FurnitureDecorate.tsv / FurnitureSkin__FurnitureSkin.tsv
资源：C:/x3-project/client/Assets/Res/UI/Spirits/  (DK_Icon → 实际 PNG)
排序对齐白皮书 §1~§8。
"""
import base64, os, csv, glob
from PIL import Image

ASSET = r"C:/x3-project/client/Assets"
SPIR = os.path.join(ASSET, "Res/UI/Spirits")
ICON = os.path.join(SPIR, "ItemIcons")
FURN_DIR = os.path.join(SPIR, "Furniture")
TSV = r"C:/x3/gdconfig/tsv"

def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def dim(path):
    try:
        with Image.open(path) as im:
            return f"{im.width}×{im.height}"
    except Exception:
        return "?"

def card(img_path, title, sub_lines, tag=None, big=False):
    if not img_path or not os.path.exists(img_path):
        thumb, d = '<div class="thumb miss">缺图</div>', "缺图"
    else:
        cls = "thumb big" if big else "thumb"
        thumb = f'<div class="{cls}"><img src="data:image/png;base64,{b64(img_path)}"></div>'
        d = dim(img_path)
    tagh = f'<span class="tag">{tag}</span>' if tag else ""
    subs = "".join(f'<div class="sub">{s}</div>' for s in sub_lines)
    w = "card big" if big else "card"
    return (f'<div class="{w}">{thumb}<div class="meta"><b>{title}</b> {tagh}'
            f'<div class="sub px">{d}</div>{subs}</div></div>')

# 递归解析（散落子目录）
_cache = {}
def rfind(root, name):
    key = (root, name)
    if key in _cache:
        return _cache[key]
    hits = glob.glob(os.path.join(root, "**", name + ".png"), recursive=True)
    _cache[key] = hits[0] if hits else ""
    return _cache[key]

def ipath(name):  # ItemIcons 直出
    return os.path.join(ICON, name + ".png") if name else ""

# ============================================================
# 数据
# ============================================================

# ---- ① 英雄皮肤（16 节日款）HeroCard 立绘 (Res/UI/Spirits/Role/HeroCard/Role_C_*) ----
HEROCARD = os.path.join(SPIR, "Role/HeroCard")
hero = [
    ("审判之光·维奥莱特", "修女", "礼包$49.99+常驻+排名Top5", "Role_C_28_Skin01"),
    ("守护誓约·阿什顿", "骑士荣光", "排名Top5", "Role_C_35_Skin01"),
    ("战斧女王·阿迪娜", "凛冬", "排名Top5", "Role_C_22_Skin01"),
    ("万圣魔女·哈妮", "万圣节", "排名Top5", "Role_C_36_Lv1"),
    ("糖杖小红帽·弗莱彻", "圣诞", "排名Top3", "Role_C_30_Lv1"),
    ("海风旅者·霍普金斯", "航海之路", "排名/活动", "Role_C_34_Skin03"),
    ("盛宴礼服·柳柳", "周年庆", "跨服排名Top3", "Role_C_14_Skin01"),
    ("热浪尤物·赛米拉", "海滨假日", "活动", "Role_C_17_Skin01"),
    ("月影华裳·霍普金斯", "中秋", "活动", "Role_C_34_Skin02"),
    ("星马赐福·卡蜜拉", "26元旦", "礼包$49.99+常驻", "Role_C_39_Skin01"),
    ("甜心咖啡师·海泽尔", "26情人节", "礼包$49.99", "Role_C_15_Skin01"),
    ("永恒誓约·赛米拉", "26情人节", "常驻$49.99+跨服Top20", "Role_C_17_Skin02"),
    ("尼罗王后·克利欧佩特拉", "26尼罗", "跨服排名Top20", "Role_C_23_Skin01"),
    ("猫女仆·莫妮卡", "26尼罗", "本服排名Top20", "Role_C_37_Skin01"),
    ("笑迎春·茉莉", "26春节", "本服排名Top20", "Role_C_6_Skin01"),
    ("红绸剑姬·阿米娜", "26春节", "跨服排名Top20", "Role_C_20_skin02"),
]

# ---- ② 主城皮肤（岛屿皮肤）Item_81xxx ----
city = [
    ("81001", "南瓜灯岬", "万圣节", "5万 / 攻+500", "节日兑换 / 排名", "icon_island_halloween"),
    ("81041", "雪舞奇缘", "圣诞节", "5万 / 攻+500", "节日活动兑换", "icon_island_christmas"),
    ("81051", "柔情海湾", "情人节", "10万 / 攻+1000", "累充 / 活动", "icon_island_ValentinesDay"),
    ("81081", "狂欢剧场", "愚人节", "5万 / 攻+500", "节日活动", "icon_island_AFD"),
    ("81091", "夏日甜筒小屋", "儿童节", "5万 / 攻+500", "节日活动", "icon_island_cd"),
    ("81101", "月心珍珠", "航海之路", "10万 / 攻+1000", "节日活动", "icon_island_navigation"),
    ("81111", "周年庆典", "周年庆", "10万 / 攻+500+采集", "节日活动", "icon_island_anniversary"),
    ("81121", "深海花园", "人鱼之歌", "5万 / 攻+500", "节日活动", "icon_island_mermaid"),
    ("81151", "金字塔之城", "26尼罗之辉", "5万 / 攻+500", "礼包 210617 $99.99", "icon_island_Egypt"),
]
city_other = [
    ("81011", "度假酒馆", "常驻", "5万", "酒馆升级解锁", "icon_island_common_2"),
    ("81021", "鲸骨沙滩", "常驻", "5万", "酒馆升级解锁", "icon_island_common_3"),
    ("81031", "繁荣岛屿", "常驻", "1万", "酒馆升级解锁", "icon_island_common_4"),
    ("81032", "强盛岛屿", "常驻", "2万", "酒馆升级解锁", "icon_island_common_5"),
    ("81033", "霸主岛屿", "常驻", "5万", "酒馆升级解锁", "icon_island_common_6"),
    ("81061", "女神神殿", "KvK", "—", "KvK 奖励", "icon_island_kvk"),
    ("81071", "风暴守卫", "KvK", "—", "KvK 奖励", "icon_island_kvk2"),
    ("81131", "回声魔山", "亡灵祭/回声", "5万", "节日活动", "icon_island_echo"),
    ("81141", "梦幻王蝶巢穴", "梦幻王蝶", "5万", "节日活动", "icon_island_Butterfly"),
]

# ---- ③ 家具：从 tsv 直读分组 ----
NON_FEST = ["摊位", "开拓航道商店", "酒馆狂欢礼包", "秋季酿酒大赛", "金币鸡仔", "远征商店", "累计充值"]
furn_fest, furn_other = {}, []
with open(os.path.join(TSV, "FurnitureDecorate__FurnitureDecorate.tsv"), encoding="utf-8") as f:
    frows = list(csv.reader(f, delimiter="\t"))
for r in frows[29:]:
    if len(r) < 29 or not r[0].isdigit():
        continue
    iid, name, icon, src = r[0], r[1], r[6], r[28]
    if not ("jiaju" in icon or "Halloween" in icon):
        continue
    (furn_other.append((iid, name, icon, src or "—"))
     if (any(k in src for k in NON_FEST) or not src)
     else furn_fest.setdefault(src, []).append((iid, name, icon)))

# ---- ④ 装饰三件套 ----
DECO = os.path.join(SPIR, "Furniture/Actv")
deco_beam = [("1001006","樱花浮雕","樱花·春风品酒节","icon_jiaju_spring_4"),("1001008","灵潮之殿","人鱼之歌·魂归之潮","icon_jiaju_DOTD_4"),
             ("1001009","海滨假日","25海滨假日","icon_jiaju_summer_4"),("1001010","团圆之夜","25中秋","icon_jiaju_MF_4"),
             ("1001011","圣诞庆典","25圣诞","icon_jiaju_Christmas01"),("1001012","新春典藏","26春节","icon_jiaju_cny_3")]
deco_floor = [("2001010","樱花地板","樱花·春风品酒节","icon_jiaju_spring_1"),("2001012","海灵归途","人鱼之歌·魂归之潮","icon_jiaju_DOTD_1"),
              ("2001013","海滨假日","25海滨假日","icon_jiaju_summer_2"),("2001015","团圆之夜","25中秋","icon_jiaju_MF_1"),
              ("2001016","圣诞庆典","25圣诞","icon_jiaju_Christmas02"),("2001017","新春典藏","26春节","icon_jiaju_cny_1")]
deco_wall = [("3001007","樱花墙纸","樱花·春风品酒节","icon_jiaju_spring_2"),("3001009","灵魂之径","人鱼之歌·魂归之潮","icon_jiaju_DOTD_2"),
             ("3001010","海滨假日","25海滨假日","icon_jiaju_summer_1"),("3001011","团圆之夜","25中秋","icon_jiaju_MF_2"),
             ("3001012","圣诞庆典","25圣诞","icon_jiaju_Christmas03"),("3001013","新春典藏","26春节","icon_jiaju_cny_2")]

# ---- ⑤ 航迹（Skin type2）+ 行军皮肤（Ship__ShipSkin） ----
trail = [("3002 / 15029","极光航迹","圣诞","icon_global_shipeffects_2"),("3006 / 15069","蒸猎航迹","蒸汽纪元","icon_global_shipeffects_6"),
         ("3007 / 15079","鸭力航迹","愚人节","icon_global_shipeffects_7"),("3008 / 15089","缤纷航迹","儿童节","icon_global_shipeffects_8"),
         ("3009 / 15093","庆典航迹","周年庆","icon_global_shipeffects_9"),("3010 / 15113","鲸灵航迹","望帆节","icon_global_shipeffects_10"),
         ("3012 / 15136","炎龙航迹","炎龙苏醒","icon_global_shipeffects_11")]
ship_fest = [("9","感恩之翼","感恩节","3001 普通航迹","icon_global_TGDship_skin_8"),("10","极光驯鹿号","圣诞","3002 极光航迹","icon_global_ship_skin_christmas"),
             ("11","菌伞幽航","蘑菇/梦伞","3003 梦伞航迹","icon_global_ship_skin_mushroom"),("12","熊猫之旅","瑞竹/春节","3004 瑞竹航迹","icon_global_ship_skin_8"),
             ("13","风暴王座","KvK","3005 风暴航迹","icon_global_ship_skin_kvk"),("14","深海猎手","蒸汽纪元","3006 蒸猎航迹","icon_global_ship_skin_submarine"),
             ("15","Duck You!","愚人节","3007 鸭力航迹","icon_global_ship_skin_duck"),("16","冰淇淋大冒险号","儿童节","3008 缤纷航迹","icon_global_ship_skin_children'sday"),
             ("17","天际彩飨","周年庆","3009 庆典航迹","icon_global_ship_skin_anniversary"),("18","守护鲸灵","望帆节","3010 鲸灵航迹","icon_global_ship_skin_whale"),
             ("19","回声圣鳐","回声/亡灵祭","3011 圣鳐航迹","icon_global_ship_skin_echo"),("20","炽焰龙舟","炎龙苏醒","3012 炎龙航迹","icon_global_ship_skin_dragon"),
             ("21","梦幻王蝶","梦幻王蝶","3013 梦幻王蝶航迹","icon_global_ship_skin_newseason"),("22","天马启航号","26元旦","3014 天马航迹","icon_global_ship_skin_newyear")]
ship_basic = [("2","阳光黄","基础色","3001","icon_global_ship_skin_5"),("3","翡翠绿","基础色","3001","icon_global_ship_skin_3"),
              ("4","星辰紫","基础色","3001","icon_global_ship_skin_2"),("5","烈焰红","基础色","3001","icon_global_ship_skin_1"),
              ("6","银河灰","基础色","3001","icon_global_ship_skin_4"),("7","小克拉肯","特殊","3001",None),
              ("8","深海猎食者","特殊","3001","icon_global_ship_skin_7")]

# ---- ⑥ 头像框（Item_80xxx, 256×256） ----
FRAME = os.path.join(SPIR, "Personalise/AvatarFrame")
frame = [("80010","捣蛋小鬼","万圣节","节日累充","Img_Player_AvatarFrame_08"),("80031","冰雪欢歌","圣诞节","节日累充","Img_Player_AvatarFrame_Christmas_1"),
         ("80051","瑞蛇迎春","25春节","节日累充","Img_Player_AvatarFrame_SpringFestival"),("80061","爱意缠绕","25情人节","节日累充","Img_Player_AvatarFrame_ValentinesDay"),
         ("80091","滑稽舞台","25愚人节","节日累充","Img_Player_AvatarFrame_AFD"),("80101","彩虹甜圈圈","25儿童节","活动进度","Img_Player_AvatarFrame_cd"),
         ("80103","1周年彩环","周年庆","活动进度","Img_Player_AvatarFrame_anniversary"),("80104","灵魂之环","亡灵祭","活动进度","Img_Player_AvatarFrame_DOTD"),
         ("80105","人鱼之歌","人鱼之歌","活动进度","Img_Player_AvatarFrame_mermaid"),("80106","玉兔逐月","中秋","活动进度","Img_Player_AvatarFrame_MF"),
         ("80110","双羽冠辉","26尼罗","排名奖励","Img_Player_AvatarFrame_Egypt"),("80112","龙焰誓约","26尼罗","排名奖励","Img_Player_AvatarFrame_SpringFestival02")]

# ---- ⑦ 纪念卡（Item_1800xx） ----
card_mem = [("180074","礼物堆里的小精灵","25圣诞","icon_card_image_74"),("180075","天马的守护","26元旦","icon_card_image_75"),
            ("180076","尼罗回响","26尼罗之辉","icon_card_image_76"),("180077","我对你的誓言","26情人节","icon_card_image_77"),
            ("180078","新春特辑","26春节","icon_card_image_78")]

# ---- ⑧ 聊天表情（Item_154xx, Emoticons 静态面板图 256×256） ----
EMO = os.path.join(SPIR, "Emoticons/Icon")
emoji = [("15415","送礼","25圣诞","icon_global_Musket01"),("15416","烟花","26元旦","icon_global_2026"),
         ("15417","猫神之舞","26尼罗之辉","icon_global_cat"),("15418","嫁给我！","26情人节","icon_global_Marry01"),
         ("15419","祝福","26春节","icon_global_molly01")]

# ============================================================
# 组装 HTML
# ============================================================
H = ['<!doctype html><meta charset="utf-8"><title>X3 节日外显图库 · 8 大模块全集</title><style>',
'body{font-family:"Microsoft YaHei",sans-serif;background:#f4f5f7;margin:0;padding:24px;color:#222}',
'h1{font-size:23px}h2{margin-top:38px;border-left:5px solid #4a6cf7;padding-left:10px;font-size:18px}',
'h3{margin-top:22px;color:#555;font-size:14px;font-weight:600}',
'.d{color:#666;font-size:13px;margin:6px 0 14px;line-height:1.6}',
'.grid{display:flex;flex-wrap:wrap;gap:14px}',
'.card{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.1);width:138px;overflow:hidden}',
'.card.big{width:190px}',
'.thumb{display:flex;align-items:center;justify-content:center;height:138px;background:repeating-conic-gradient(#e6e8ec 0 25%,#f2f3f6 0 50%) 50%/16px 16px}',
'.thumb.big{height:240px}',
'.thumb img{max-width:128px;max-height:128px}.thumb.big img{max-width:184px;max-height:232px}',
'.thumb.miss{color:#bbb;font-size:12px}',
'.meta{padding:7px 9px;font-size:11px;line-height:1.5}.meta b{font-size:13px}',
'.sub{color:#888}.sub.px{color:#bbb;font-size:10px}',
'.tag{background:#4a6cf7;color:#fff;border-radius:4px;padding:1px 7px;font-size:10px;white-space:nowrap}',
'.toc{background:#fff;border-radius:8px;padding:12px 18px;margin:10px 0 6px;font-size:13px;line-height:2}',
'.toc a{color:#4a6cf7;text-decoration:none;margin-right:16px}',
'.path{background:#fffbe6;border:1px solid #f0e0a0;border-radius:6px;padding:8px 12px;margin:0 0 14px;font-size:12px;line-height:1.8;color:#5a4a00}',
'.path b{color:#7a5d00}.path code{background:#fff3cf;color:#6b5200}',
'code{background:#eef;border-radius:3px;padding:1px 4px;font-size:12px}',
'</style>']

def pathbox(rows):
    inner = "".join(f'<div>{r}</div>' for r in rows)
    return (f'<div class="path">📁 <b>Unity 资源路径</b>（均在 <code>C:\\x3-project\\client\\Assets\\</code> 下）{inner}</div>')

H.append('<h1>X3 节日外显图库 · 8 大模块全集</h1>')
H.append('<p class="d">配套 <b>X3 节日外显投放白皮书</b>（<code>x3_festival_cosmetics_whitepaper.md</code>），模块顺序对齐白皮书 §1~§8。'
         '资源实地导出自 <code>C:\\x3-project\\client\\Assets\\Res\\UI\\Spirits</code>（2026-06-17），用配置表 <code>DK_Icon</code> 解析。'
         '<br>① 英雄皮肤展示的是 <b>HeroCard 立绘</b>；② 主城皮肤本体是 3D 建筑、⑤ 航迹/行军是粒子特效，用<b>道具图标</b>作可视代表；⑥⑦⑧ 本身就是 2D 成品图。</p>')
H.append('<div class="toc"><b>目录：</b>'
         '<a href="#m1">① 英雄皮肤</a><a href="#m2">② 主城皮肤</a><a href="#m3">③ 家具</a><a href="#m4">④ 装饰三件套</a>'
         '<a href="#m5">⑤ 航迹 + 行军皮肤</a><a href="#m6">⑥ 头像框</a><a href="#m7">⑦ 纪念卡</a><a href="#m8">⑧ 聊天表情</a></div>')

# ① 英雄皮肤
H.append('<h2 id="m1">① 英雄晋升皮肤 · 16 节日款 <span class="tag">最重·Spine立绘</span></h2>')
H.append('<p class="d">Spine 骨骼动画立绘（重绑动画，最贵的一档外显）。直购 $49.99 一口价无升级坑；排名皮肤是收入主力（A+B线消费冲榜）。下图为 <b>HeroCard 立绘</b>。</p>')
H.append(pathbox([
    '本图用图(HeroCard 立绘)：<code>Res/UI/Spirits/Role/HeroCard/Role_C_&lt;英雄id&gt;_Skin&lt;n&gt;.png</code>',
    'Spine 立绘动画(本体)：prefab <code>Res/Spine/Prefabs_Download/Role_Spine_&lt;id&gt;_Skin&lt;n&gt;.prefab</code> ＋ 数据目录 <code>Res/Spine/Role_Spine_&lt;id&gt;_skin&lt;n&gt;/</code>',
    '头图/全身：<code>Res/UI/Spirits/Role/Character Portraits/Img_C_H_*</code> · <code>Res/UI/Spirits/Role/FullLength/Role_F_*</code>',
]))
H.append('<div class="grid">')
for name, fest, get, dk in hero:
    H.append(card(rfind(HEROCARD, dk), name, [f"获取：{get}"], tag=fest, big=True))
H.append('</div>')

# ② 主城皮肤
H.append('<h2 id="m2">② 主城皮肤（岛屿皮肤）· 9 节日款 <span class="tag">带战力Buff·Item_81xxx</span></h2>')
H.append('<p class="d">3D 建筑模型皮肤，8 大外显里<b>唯一带属性（战力 5万~10万 / 攻 +500~+1000）</b>。直购仅 1 款（金字塔之城 $99.99），其余走兑换/累充/活动。</p>')
H.append(pathbox([
    '本图用图(道具图标)：<code>Res/UI/Spirits/ItemIcons/icon_island_*.png</code>',
    '建筑模型(本体)：<code>Res/Unit/City/Buildings/Building_&lt;itemid&gt;_Lock.prefab</code> / <code>_Unlock.prefab</code>',
    '主城场景 3D 资产：<code>Res/Scene/City/EPIC_Fantasy_Town_Low_Poly_3D_Art/</code>',
]))
H.append('<div class="grid">')
for iid, name, fest, power, get, icon in city:
    H.append(card(ipath(icon), name, [f"ID {iid}", f"战力 {power}", f"获取：{get}"], tag=fest))
H.append('</div><h3>常驻 / KvK 主城皮肤（非节日，补充）</h3><div class="grid">')
for iid, name, fest, power, get, icon in city_other:
    H.append(card(ipath(icon), name, [f"ID {iid}", f"战力 {power}", f"获取：{get}"], tag=fest))
H.append('</div>')

# ③ 家具
H.append('<h2 id="m3">③ 家具（城内家具）· 节日/主题款 <span class="tag">FurnitureDecorate·按节日分</span></h2>')
H.append('<p class="d">城内可摆放家具（3D 模型 + 2D 图标）。白皮书框定"38 节日款覆盖 14 节日"，当前配置已扩到更多节日。按配置 <code>来源描述</code> 分组。'
         '$19.99 家具礼包是最优价格带（大R付费率 25%~35%）；情人节提价 $99.99 致付费率暴跌至 4%。</p>')
H.append(pathbox([
    '本图用图(图标)：<code>Res/UI/Spirits/Furniture/Actv/icon_jiaju_*.png</code>',
    '模型/prefab(本体)：FBX <code>Res/Furniture/Model/&lt;子目录&gt;/Fbx/</code> · prefab <code>Res/Furniture/Prefabs/</code>',
]))
for src in sorted(furn_fest, key=lambda s: -len(furn_fest[s])):
    items = furn_fest[src]
    H.append(f'<h3>{src} · {len(items)} 款</h3><div class="grid">')
    for iid, name, icon in items:
        H.append(card(rfind(FURN_DIR, icon[3:] if icon.startswith("DK_") else icon), name, [f"ID {iid}"]))
    H.append('</div>')
H.append(f'<h3>常驻 / 商店 / 排行家具（非节日，补充）· {len(furn_other)} 款</h3><div class="grid">')
for iid, name, icon, src in furn_other:
    H.append(card(rfind(FURN_DIR, icon[3:] if icon.startswith("DK_") else icon), name, [f"ID {iid}", src]))
H.append('</div>')

# ④ 装饰三件套
H.append('<h2 id="m4">④ 装饰三件套（城内装饰）· 6 套 × 3 件 = 18 节日款 <span class="tag">FurnitureSkin·按类型分</span></h2>')
H.append('<p class="d">城内装饰换肤，每套 3 件：<b>横梁</b>（门+柱，type3，<code>1001xxx</code>）/ <b>地板</b>（type1，<code>2001xxx</code>）/ <b>墙纸</b>（type2，<code>3001xxx</code>）。'
         '凑齐一套才有完整视觉，无集套奖励。直购仅 2 套（圣诞/新春 $99.99），其余走活动/累充。下方按类型分组，<b>同列即同套</b>。</p>')
H.append(pathbox([
    '本图用图(图标)：<code>Res/UI/Spirits/Furniture/Actv/icon_jiaju_*.png</code>',
    '横梁(模型)：<code>Res/Furniture/Model/Furniture_Door_Wall_Column_Skin&lt;n&gt;/</code> → prefab <code>Res/Furniture/Prefabs/Door/Skin&lt;n&gt;/</code>',
    '地板(本体)：prefab <code>Res/Furniture/Prefabs/Floor/</code> ＋ 贴图 <code>…/Floor/Textures/</code>',
    '墙纸(本体)：prefab <code>Res/Furniture/Prefabs/Wallpaper/</code> ＋ 贴图 <code>…/Wallpaper/Textures/</code>',
]))
for label, arr in [("横梁（门 + 柱）", deco_beam), ("地板", deco_floor), ("墙纸", deco_wall)]:
    H.append(f'<h3>{label} · 6 款</h3><div class="grid">')
    for iid, name, fest, icon in arr:
        H.append(card(os.path.join(DECO, icon + ".png"), name, [f"ID {iid}"], tag=fest))
    H.append('</div>')

# ⑤ 航迹 + 行军皮肤
H.append('<h2 id="m5">⑤ 航迹（拖尾）+ 行军皮肤（船体）<span class="tag">FxID 成套绑定</span></h2>')
H.append('<p class="d"><b>航迹</b>=船航行拖尾粒子（<code>Skin</code> type2，零属性，白皮书诊断超R/大R持有率均 0%）；'
         '<b>行军皮肤</b>=船体造型（<code>Ship__ShipSkin</code>），其 <code>FxID</code> 绑定一条航迹——节日船与节日航迹成套出。</p>')
H.append(pathbox([
    '本图用图(图标)：航迹 <code>Res/UI/Spirits/ItemIcons/icon_global_shipeffects_*.png</code> · 行军 <code>icon_global_ship_skin_*.png</code>',
    '特效本体(粒子 prefab)：<code>Res/Effect/Prefabs/Ship/&lt;节日&gt;_ship/</code>（航迹=<code>Fx_*_Trail.prefab</code>；船体=Idle/Fly/Hit/Fire 等）',
]))
H.append('<h3>航迹 · 7 节日款</h3><div class="grid">')
for sid, name, fest, icon in trail:
    H.append(card(ipath(icon), name, [f"Skin/Item {sid}"], tag=fest))
H.append('</div><h3>行军皮肤 · 节日/主题款（14）</h3><div class="grid">')
for sid, name, fest, fx, icon in ship_fest:
    H.append(card(ipath(icon), name, [f"ShipSkin {sid}", f"绑定航迹 {fx}"], tag=fest))
H.append('</div><h3>行军皮肤 · 基础色/特殊款（7）</h3><div class="grid">')
for sid, name, fest, fx, icon in ship_basic:
    p = os.path.join(ASSET, "Res/UI/Spirits/Role/Ship/Img_Ship_01.png") if name == "小克拉肯" else ipath(icon)
    H.append(card(p, name, [f"ShipSkin {sid}", f"航迹 {fx}"], tag=fest))
H.append('</div>')

# ⑥ 头像框
H.append('<h2 id="m6">⑥ 头像框 · 12 节日款 <span class="tag">256×256·零独立收入</span></h2>')
H.append('<p class="d">2D 头像框（<code>Item_80xxx</code>，256×256）。投放=节日累充(Reward源519)/活动进度/排名，无直购。白皮书：大R饱和度仅 5%，活动进度框触达率极低。</p>')
H.append(pathbox([
    '成品图(即本体，2D)：<code>Res/UI/Spirits/Personalise/AvatarFrame/Img_Player_AvatarFrame_*.png</code>（256×256）',
]))
H.append('<div class="grid">')
for iid, name, fest, get, dk in frame:
    H.append(card(rfind(FRAME, dk), name, [f"ID {iid}", f"获取：{get}"], tag=fest))
H.append('</div>')

# ⑦ 纪念卡
H.append('<h2 id="m7">⑦ 纪念卡 · 5 节日款 <span class="tag">纯收藏·零收入</span></h2>')
H.append('<p class="d">2D 卡面（<code>Item_1800xx</code>）。走节日活动进度/BP，无直购无兑换。白皮书：集卡系统有粘性（超R覆盖 57.7%）但变现潜力完全未挖掘。</p>')
H.append(pathbox([
    '本图用图(图标)：<code>Res/UI/Spirits/ItemIcons/icon_card_image_*.png</code>',
    '卡面大图(本体)：<code>Res/UI/Spirits/MemorialCard/</code> · 新集卡 <code>Res/UI/Spirits/CardCollectionV2/</code>',
]))
H.append('<div class="grid">')
for iid, name, fest, icon in card_mem:
    H.append(card(ipath(icon), name, [f"ID {iid}"], tag=fest, big=True))
H.append('</div>')

# ⑧ 聊天表情
H.append('<h2 id="m8">⑧ 聊天表情 · 5 节日款 <span class="tag">Emoticons·BP免费</span></h2>')
H.append('<p class="d">可售卖聊天表情系统（<code>Emoticons</code>，<code>Item_154xx</code>）。节日款走 BP 进度/活动免费发放。下图为<b>表情面板静态图标</b>（256×256）；发到聊天里是会动的 GIF。<b>全表情 5 套系统详见同目录 <code>表情全系统.html</code></b>。</p>')
H.append(pathbox([
    '本图用图(面板静态 icon)：<code>Res/UI/Spirits/Emoticons/Icon/icon_global_*.png</code>（256×256）',
    '动图 GIF(发到聊天)：<code>Res/UI/Gif/&lt;名&gt;.bytes</code>（＋ <code>.gif</code> 源）',
    '气泡底：<code>Res/UI/Spirits/Emoticons/ui_chat_memebg_*.png</code>',
]))
H.append('<div class="grid">')
for iid, name, fest, icon in emoji:
    H.append(card(os.path.join(EMO, icon + ".png"), name, [f"ID {iid}"], tag=fest))
H.append('</div>')

out = os.path.join(os.path.dirname(__file__), "X3节日外显图库_8大模块全集.html")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(H))
print("WROTE", out, os.path.getsize(out), "bytes")
