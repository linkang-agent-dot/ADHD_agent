# -*- coding: utf-8 -*-
"""Generate 2 X3 art requirement HTML docs (8月庆典主城皮肤 / 9月海盗船+三件套)."""
import os, base64, io
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = r"C:\ADHD_agent\KB\产出-本地化与美术"
CACHE = r"C:\Users\linkang\.claude\image-cache\42ce653e-2e7b-416e-a7f6-25cb4ac83e33"

def b64(path, maxw=460):
    img = Image.open(path)
    img = img.convert("RGBA") if img.mode != "RGB" else img
    if img.width > maxw:
        img = img.resize((maxw, int(img.height * maxw / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

IMGS = {
    "anniv_lv1": b64(r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew\anniversary2024\Common\Texture\AnniverSkinLv1.png", 300),
    "anniv_lv2": b64(r"E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew\anniversary2024\Common\Texture\AnniverSkinLv2.png", 300),
    "anniv_pose": b64(os.path.join(HERE, "renders", "AnnivLv2_f1.png"), 380),
    "pirate_low": b64(r"E:\P2\client\client\Assets\P2\Res\UI\Sprite\ItemIcon\151105559.png", 300),
    "pirate_high": b64(r"E:\P2\client\client\Assets\P2\Res\UI\Sprite\ItemIcon\151105560.png", 300),
    "trio_ref": b64(os.path.join(HERE, "trio_ref_x3.png"), 760),
}

CSS = """<style>
body{font-family:"Microsoft YaHei",sans-serif;background:#f4f5f7;margin:0;padding:26px;color:#222;max-width:1060px}
h1{font-size:22px;margin-bottom:4px}
h2{margin-top:34px;border-left:5px solid #4a6cf7;padding-left:10px;font-size:17px}
.d{color:#666;font-size:13px;line-height:1.7;margin:6px 0 14px}
.item{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.08);padding:16px 20px;margin:14px 0}
.item h3{margin:0 0 8px;font-size:15px}.item h3 .no{background:#4a6cf7;color:#fff;border-radius:5px;padding:1px 8px;font-size:12px;margin-right:8px}
table{border-collapse:collapse;font-size:13px;width:100%;margin:8px 0}
td,th{border:1px solid #e3e6ee;padding:6px 10px;text-align:left;vertical-align:top;line-height:1.65}
th{background:#f0f2f8;white-space:nowrap;width:92px}
.refs{display:flex;gap:14px;flex-wrap:wrap;margin-top:10px}
.ref{background:#fafbfe;border:1px solid #e7eaf3;border-radius:8px;padding:8px;text-align:center;font-size:12px;color:#666}
.ref img{display:block;margin:0 auto 6px;max-width:300px;border-radius:6px;background:repeating-conic-gradient(#eceef2 0 25%,#f7f8fa 0 50%) 50%/14px 14px}
.warn{background:#fff7e8;border:1px solid #f0d9a8;border-radius:6px;padding:8px 12px;font-size:12.5px;color:#7a5b00;line-height:1.7;margin-top:8px}
.tag{background:#e5f7e9;color:#2c8a43;border-radius:4px;padding:1px 7px;font-size:11px;margin-left:6px}
code{background:#eef;border-radius:3px;padding:1px 5px;font-size:12px}
.meta{color:#999;font-size:12px;margin-top:26px}
</style>"""

# ============ Doc 1: 8月庆典 ============
doc1 = f"""<!doctype html><meta charset="utf-8"><title>X3 8月庆典·主城皮肤美需（马戏团旋转木马）</title>{CSS}
<h1>X3 · 8月庆典 主城/岛屿皮肤美需 —— 马戏团旋转木马</h1>
<p class="d">来源：P2 周年庆2024「马戏团旋转木马」皮肤已由程序侧整套搬运到 X3（分支 <code>dev_festival</code> / 评审分支 <code>circus-homeland-port</code>，
prefab=<code>Assets/Res/Unit/WorldMap/Homeland/Homeland_Circus.prefab</code>，<b>Unity 里可直接打开预览，带旋转动画</b>）。
搬运稿可作为白模/坯子基础，本需求=美术产出<b>正式版</b>。排期目标：<b>8月庆典节日</b>。</p>

<div class="item"><h3><span class="no">①</span>岛屿皮肤本体（3D）<span class="tag">主件</span></h3>
<table>
<tr><th>需求</th><td>以马戏团旋转木马为主体的整岛皮肤，<b>出 1 档</b>（对齐 X3 现有 Homeland 单档惯例）。<b>P2 原模型只有建筑无岛座</b>——需按 X3 岛屿皮肤惯例补<b>岛体基座</b>（礁石/沙滩/草地托底，托住建筑底盘），建筑本体可直接沿用搬运的 FBX+贴图改（模型/UV/动画都是现成的），也可重构。<b>修缮清单</b>：①顶部飞碟转椅组与紫棚的衔接结构（当前有悬空）②底盘与岛座的过渡（帐篷群/彩旗/入口拱门可延伸到岛座上丰富层次）③<b>保留动画</b>：底层旋转木马转动 + 顶部火箭转椅旋转，如有余量可加彩旗飘动。</td></tr>
<tr><th>交付</th><td>按 X3 Homeland 目录规范：<code>Homeland_&lt;名&gt;/</code>（Fbx / Material / Texture）+ 顶层 prefab。整岛 <b>1 张烘焙漫反射贴图</b>（X3 惯例无法线/自发光；历套 512×512，本件建筑细节多，可用 1024~2048，与程序确认包体）+ 岸边水波 ripple 件（可复用现成）。</td></tr>
<tr><th>尺寸</th><td>体量对齐现有 17 套 Homeland（整岛约 4.6~6 世界单位，参考 <code>Homeland_Anniversary</code>）；搬运稿已按此调过缩放可直接量。</td></tr>
<tr><th>避坑</th><td>①顶部灰色飞碟必须<b>贴合紫色顶棚</b>（搬运稿当前有悬空 bug，正确姿态见下参考图）②Homeland 挂大地图相机，节点用 <b>Layer 0 (Default)</b>③岛在地图上以 55°X 倾角容器显示，直立建模即可（容器已处理）。</td></tr>
</table>
<div class="refs">
<div class="ref"><img src="data:image/png;base64,{IMGS['anniv_pose']}">正确组装姿态（渲染基准图：飞碟贴合紫棚）</div>
<div class="ref"><img src="data:image/png;base64,{IMGS['anniv_lv2']}">P2 官方展示图·高级档（目标观感）</div>
</div>
<div class="warn">源资产位置（美术可直接取）：X3 仓 <code>Homeland_Circus/Fbx/Anniversary2024.fbx</code>（含全部网格+动画）+ <code>Texture/Anniversary2024_Diffuse.png</code>（2048 漫反射）。P2 原仓另有 Light（夜灯发光）/Normal 贴图，如需夜景表现可找我取。</div>
</div>

<div class="item"><h3><span class="no">②</span>皮肤 2D 展示图标</h3>
<table>
<tr><th>需求</th><td>皮肤道具图标 + 皮肤列表展示图（同图两用）：马戏团建筑 3/4 视角渲染，透明底，主体饱满带节日彩带/星星点缀，风格与上方 P2 展示图一致但需<b>按 X3 图标规范重出</b>。</td></tr>
<tr><th>交付</th><td>透明 PNG，接 DK 注册（<code>DK_Head</code> + <code>Item.DK_Icon</code>）。</td></tr>
<tr><th>尺寸</th><td><b>256×256</b>（与现有岛屿皮肤道具 Item_81xxx 图标同尺寸），主体占比约 70~75%，四角真透明。</td></tr>
</table></div>

<div class="item"><h3><span class="no">③</span>皮肤获取活动展示图（2D）</h3>
<table>
<tr><th>需求</th><td>皮肤在获取活动（转盘/开箱大奖、活动页展示位）里用的<b>渲染宣传大图</b>：马戏团皮肤成品 3/4 视角高质量渲染 + 庆典氛围点缀（彩带/礼花/星光），突出「节日大奖」质感；构图给文案/按钮留出下方空间。</td></tr>
<tr><th>交付</th><td>透明底 PNG 一张（活动页/弹窗共用），DK 注册由数值侧处理。</td></tr>
<tr><th>尺寸</th><td>与深海节大奖展示位同尺寸（复用源=深海节潜艇皮肤展示图，美术直接量原资源；拿不到找我）。</td></tr>
</table></div>
<p class="meta">提出：林康 · 2026-07-10 · 工程搬运稿已在 dev_festival 可预览 · 配置接线（Skin__Skin/Item_81xxx）由数值侧负责，美术资源就位后替换 · 皮肤获得/预览展示视频走 AI 视频管线（我方产出），不占美术工时</p>
"""

# ============ Doc 2: 9月海盗 ============
doc2 = f"""<!doctype html><meta charset="utf-8"><title>X3 9月·海盗船主城皮肤+海盗三件套美需</title>{CSS}
<h1>X3 · 9月节日美需 —— 海盗船主城皮肤 + 海盗主题装饰三件套</h1>
<p class="d">主题锚：P2 深海节2026「海盗启航」海盗船（下方参考图）。9月节日两件事：①海盗船岛屿皮肤 ②海盗主题三件套（横梁/地板/墙纸）。</p>

<div class="item"><h3><span class="no">①</span>海盗船岛屿皮肤（3D）<span class="tag">主件</span></h3>
<table>
<tr><th>需求</th><td>海盗船主题整岛皮肤，<b>只出 1 档：黑金幽灵船</b>——黑帆+鎏金船身+紫色章鱼触手缠绕+绿色幽光（见参考图）。需补<b>岛座/海浪基座</b>（船体坐浪，参考展示图的浪座处理）。</td></tr>
<tr><th>交付</th><td>同 Homeland 规范：<code>Homeland_&lt;名&gt;/</code>（Fbx/Material/Texture）+ prefab；整岛 1 张烘焙漫反射 + 水波件。</td></tr>
<tr><th>尺寸</th><td>体量对齐现有 Homeland（整岛 4.6~6 世界单位）。</td></tr>
<tr><th>避坑</th><td>①节点 Layer 0 ②直立建模（55° 倾角由容器处理）③P2 全套源模型本机有（4 FBX/20 贴图），需要底模找我取，可省建模工时。</td></tr>
</table>
<div class="refs">
<div class="ref"><img src="data:image/png;base64,{IMGS['pirate_high']}">P2「海盗启航」黑金幽灵船（本件唯一目标档）</div>
</div></div>

<div class="item"><h3><span class="no">②</span>海盗主题装饰三件套（3D+图标）</h3>
<table>
<tr><th>需求</th><td>横梁(门+柱)／地板／墙纸 各 1 款，海盗主题。元素池：骷髅旗、船锚、舵轮、藏宝箱、金币、绳索缆绳、船木纹理、海图。建议：<b>横梁</b>=船首拱门（断桅+帆布+骷髅旗尖顶）；<b>地板</b>=甲板木纹+缆绳收边（角落金币/海星点缀）；<b>墙纸</b>=藏宝海图风（罗盘+航线虚线+一角骷髅印章）。</td></tr>
<tr><th>交付</th><td>沿用现行三件套规范——横梁：<code>Furniture_Door_Wall_Column_Skin&lt;n&gt;</code> 三模型(Door/Column/Wall FBX)+prefab；地板/墙纸：prefab+贴图（<code>Furniture/Prefabs/Floor|Wallpaper</code>）；三件各配 <b>256×256</b> 透明底图标。</td></tr>
<tr><th>尺寸</th><td>模型/贴图=与最近一期三件套（26春节「新春典藏」）对应资源同尺寸；图标 256×256。</td></tr>
<tr><th>避坑</th><td>属性/ID 由数值侧配（沿用 声望10000+水手攻击 横梁5%/地板1%/墙纸1%，ID 顺延 1001013/2001018/3001014），美术不用管；仅需三款风格成套、与海盗船皮肤同色系呼应。</td></tr>
</table>
<div class="refs">
<div class="ref"><img src="data:image/png;base64,{IMGS['trio_ref']}">X3 现行三件套图标样例（左=横梁·中=地板·右=墙纸，256×256 规格；完整历期图鉴见 KB 非节日外显投放图鉴）</div>
</div></div>
<p class="meta">提出：林康 · 2026-07-10 · 其他 9 月需求暂无，后续增补另开单</p>
"""

for fn, doc in [("X3_2026八月庆典_主城皮肤_美需.html", doc1),
                ("X3_2026九月海盗节_主城皮肤+三件套_美需.html", doc2)]:
    p = os.path.join(OUT_DIR, fn)
    open(p, "w", encoding="utf-8").write(doc)
    print("written", p, os.path.getsize(p) // 1024, "KB")
