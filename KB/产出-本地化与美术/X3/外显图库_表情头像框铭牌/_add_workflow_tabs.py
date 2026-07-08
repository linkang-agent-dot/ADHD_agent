# -*- coding: utf-8 -*-
"""把 8 大模块全集 HTML 改造成美术版 demo：
顶部模块页签 + 每模块下「现有资源图库 / 制作流程」子页签 + 总览表。
不动原文件，产出 X3外显图库_美术制作流程_demo.html。
制作流程口径 = 2026-07-08 确认（英雄皮肤/主城皮肤→视频；家具/航迹→搬运P2/X2；
装饰三件套/行军皮肤/头像框→新做；纪念卡/表情→维持现行）。
"""
import io, os, sys

SRC = os.path.join(os.path.dirname(__file__), "X3节日外显图库_8大模块全集.html")
OUT = os.path.join(os.path.dirname(__file__), "X3外显图库_美术制作流程_demo.html")

EXTRA_CSS = """
/* ===== 美术版 demo：页签框架 ===== */
.topnav{position:sticky;top:0;z-index:50;background:#f4f5f7;padding:10px 0 12px;display:flex;flex-wrap:wrap;gap:8px;border-bottom:1px solid #e2e4ea;margin-bottom:6px}
.topnav button{border:1px solid #d5d8e0;background:#fff;color:#444;border-radius:18px;padding:7px 15px;font-size:13px;cursor:pointer;font-family:inherit}
.topnav button:hover{border-color:#4a6cf7;color:#4a6cf7}
.topnav button.on{background:#4a6cf7;border-color:#4a6cf7;color:#fff;font-weight:600}
.subtabs{display:flex;gap:2px;margin:14px 0 0;border-bottom:2px solid #e2e4ea}
.subtabs button{border:none;background:none;padding:9px 18px;font-size:14px;color:#666;cursor:pointer;border-bottom:3px solid transparent;margin-bottom:-2px;font-family:inherit}
.subtabs button.on{color:#4a6cf7;font-weight:700;border-bottom-color:#4a6cf7}
.pane[hidden]{display:none}
.module{display:none}.module.on{display:block}
/* ===== 制作流程面板 ===== */
.wf{max-width:1080px}
.wf-badge{display:inline-block;border-radius:6px;padding:3px 12px;font-size:13px;font-weight:700;color:#fff;margin:14px 0 4px}
.wf-badge.video{background:#8b5cf6}.wf-badge.reuse{background:#16a34a}.wf-badge.new{background:#ea580c}.wf-badge.keep{background:#0284c7}
.wf h4{font-size:15px;margin:20px 0 8px;color:#333;border-left:4px solid #c9d2f5;padding-left:8px}
.wf .box{background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.08);padding:14px 18px;font-size:13px;line-height:1.9;color:#444;margin-bottom:6px}
.wf ol{margin:4px 0;padding-left:22px}.wf ol li{margin:4px 0}
.wf ul{margin:4px 0;padding-left:20px}.wf ul li{margin:3px 0}
.wf .warn{background:#fff7ed;border:1px solid #fbd6a5;border-radius:8px;padding:10px 14px;color:#7c4a03;font-size:13px;line-height:1.8;margin:8px 0}
.wf code{background:#eef;border-radius:3px;padding:1px 5px;font-size:12px}
.wf table{border-collapse:collapse;width:100%;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08);font-size:13px}
.wf th{background:#4a6cf7;color:#fff;padding:9px 12px;text-align:left;font-size:13px;white-space:nowrap}
.wf td{padding:9px 12px;border-top:1px solid #eef0f5;line-height:1.7;vertical-align:top}
.wf tr:hover td{background:#f7f8fd}
.pill{display:inline-block;border-radius:5px;padding:1px 9px;font-size:12px;font-weight:700;color:#fff;white-space:nowrap}
.pill.video{background:#8b5cf6}.pill.reuse{background:#16a34a}.pill.new{background:#ea580c}.pill.keep{background:#0284c7}
"""

# ---------------- 制作流程内容（受众=美术同学） ----------------

WF_OVERVIEW = """
<div class="wf">
<h4>各模块制作方式一览（口径 2026-07-08 确认）</h4>
<table>
<tr><th>模块</th><th>资源形态</th><th>确认制作方式</th><th>一句话说明</th></tr>
<tr><td><b>① 英雄皮肤</b></td><td>展示视频（替代 Spine）</td><td><span class="pill video">🎬 直接做视频</span></td><td>新皮肤不再绑 Spine 骨骼动画，AI 视频管线直出 1080×1920 循环展示片，已落地首例=世界杯足球宝贝</td></tr>
<tr><td><b>② 主城皮肤</b></td><td>整岛低模+烘焙贴图（+展示视频）</td><td><span class="pill new">🆕 除 Spine 外全可自产</span></td><td>整岛=1 低模 FBX+1 张 512 烘焙贴图+水波件，全部可自产（Spine 动画岛除外）；展示视频复用英雄皮肤管线</td></tr>
<tr><td><b>③ 家具</b></td><td>3D 模型 + 2D 图标</td><td><span class="pill reuse">♻️ 搬运 P2/X2 模型</span></td><td>不新建模，FBX+贴图+prefab 从 P2/X2 现成家具直接迁移</td></tr>
<tr><td><b>④ 装饰三件套</b></td><td>横梁/地板/墙纸 3D+贴图</td><td><span class="pill new">🆕 新做</span></td><td>流程参考 X2 室内场景做法；地板/墙纸是平面贴图件、横梁要建模</td></tr>
<tr><td><b>⑤ 航迹</b></td><td>拖尾粒子特效 prefab</td><td><span class="pill reuse">♻️ 直接用 X2/P2 资源</span></td><td>现成航迹特效迁移调整，不新做</td></tr>
<tr><td><b>⑤ 行军皮肤</b></td><td>船体 3D 模型 + 状态特效</td><td><span class="pill new">🆕 新做模型需求</span></td><td>走美需→建模；FxID 绑一条航迹，节日船+节日航迹成套出</td></tr>
<tr><td><b>⑥ 头像框</b></td><td>2D PNG 256×256</td><td><span class="pill new">🆕 新做</span></td><td>按尺寸规范直出，AI 可端到端产出</td></tr>
<tr><td><b>⑦ 纪念卡</b></td><td>2D 卡面 + 图标</td><td><span class="pill keep">🔵 维持现行</span></td><td>2D 直出，AI 可端到端产出</td></tr>
<tr><td><b>⑧ 聊天表情</b></td><td>GIF 动图 + 静态面板图</td><td><span class="pill keep">🔵 维持现行</span></td><td>动+静两份产出；GIF 透明有硬性存图规则（见模块页）</td></tr>
</table>
<div class="box" style="margin-top:14px">💡 使用说明：点上方模块页签进入各模块，「现有资源图库」子页签=实物图+资源路径（实地导出自 <code>C:\\x3-project\\client\\Assets</code>）；「制作流程」子页签=该模块确认的制作方式、产出清单、规格与落地路径。所有资源进游戏统一走 DK 注册（配置表写 <code>DK_</code> 名，不写路径）。</div>
</div>
"""

WF_M1 = """
<div class="wf">
<span class="wf-badge video">🎬 确认方案：直接做视频（不再做 Spine）</span>
<div class="box">新英雄皮肤不再绑 Spine 骨骼动画，直接产出<b>展示视频</b>，客户端循环播放。已落地首例：世界杯「足球宝贝·爱莉希雅」。</div>
<h4>产出规格</h4>
<div class="box"><ul>
<li>统一 <b>1080×1920（9:16）原生直出</b>，不做后期裁切（客户端显示框已按此比例定）。</li>
<li>透明角色视频 = <b>SBS 格式</b>（左半彩色画面 + 右半白模 alpha 并排），格式参照 <code>Res/Video/VideoRes/AllianceCard_icon_1_a.mp4</code>。</li>
<li>时长 4~8s；<b>一条片 = 入场表演段 + 落定 + 静态 idle 循环段</b>，整条循环播，<b>禁止拼接</b>（拼接缝光影漂移肉眼可见）。</li>
<li>角色框定参照官方全身立绘 <code>Res/UI/Spirits/Role/FullLength/Role_F_&lt;id&gt;.png</code>：占高约 95%、居中、脚底锚定。</li>
</ul></div>
<h4>流程步骤</h4>
<div class="box"><ol>
<li><b>出主稿立绘</b>：白底、按展示框站位、有张力的姿态+眼神（撩不撩的根在起点图，主稿端正视频就端正）。</li>
<li><b>AI 生成视频</b>：seedance 首选（2D 立绘脸稳、动得足）；kling 备选（首尾帧锁定最紧，适合纯 idle 循环）。</li>
<li><b>逐帧抠像</b>（video_remove_background）→ 透明 webm。</li>
<li><b>打包 SBS</b>（export_sbs_video，quality=12 甜点档，肉眼无损）。</li>
<li><b>最终压缩</b>统一走 GRFal <code>compress_video</code>（后端参数已调优，效果优于本地 ffmpeg 手调）；本地 ffmpeg 只做几何操作（裁切/缩放/去音轨）。</li>
<li><b>落地</b>：<code>Res/Video/VideoRes/</code> + DK 注册（<code>HeroSkin.DKVideo → EffectDisplay.VideoDisplayKey</code>）。</li>
</ol></div>
<h4>idle 段演出验收口径（沿用 Spine 精髓）</h4>
<div class="box"><ul>
<li>胸部呼吸起伏是主角（克制不浮夸）；头微侧倾 + 眨眼给「活气」；<b>嘴锁形状</b>（可随头平移、不张不变形）。</li>
<li>动作幅度带 0.4~0.9（帧间平均像素差）——压太狠变木头，推太猛破循环。</li>
<li>首尾帧一致 = 无缝循环（像素差 &lt;3 达标）。</li>
</ul></div>
<div class="warn">⚠️ 配套仍需 2D 产出：HeroCard 立绘 <code>Role/HeroCard/Role_C_*_Skin*.png</code>、头图 <code>Role/Character Portraits/Img_C_H_*</code>（图库页签展示的就是 HeroCard 立绘）。</div>
</div>
"""

WF_M2 = """
<div class="wf">
<span class="wf-badge new">🆕 确认（2026-07-08）：除 Spine 外全部组件可自产</span>
<div class="box">实地扒完历套岛屿皮肤（<code>Res/Unit/WorldMap/Homeland/</code>，17 套），一套主城皮肤的资源构成比想象轻——<b>整岛就是一个低模 + 一张烘焙贴图</b>。除情人节那种 Spine 动画岛，其余全部组件都能自产。</div>
<h4>一套岛屿皮肤的完整资源清单（历套标准范式）</h4>
<div class="box"><ul>
<li><b>整岛主体</b>：1 个 FBX（整岛一体低模）+ 1 张 <b>512×512 烘焙漫反射贴图</b>（整岛就这一张图，无法线/自发光）+ 材质 .mat。</li>
<li><b>岸边水波 ripple</b>：1 个 ripple FBX + 1 张 256×128 贴图 + 材质（历套标配）。</li>
<li><b>顶层 prefab</b>：<code>Homeland_&lt;名&gt;.prefab</code>；个别带 idle 动画（如愚人节 <code>Anim/Homeland_Joker_idle.anim</code>，挂 Animation 组件）。</li>
<li><b>道具图标</b>：<code>ItemIcons/icon_island_*.png</code> 一张。</li>
<li><b>落地路径</b>：<code>Res/Unit/WorldMap/Homeland/Homeland_&lt;名&gt;/</code>（Fbx / Texture / Material 子目录）。</li>
<li><b>接线</b>：DK 注册 <code>Path_Model.asset</code>（<code>DK_Homeland_*</code>）→ 配置 <code>Skin__Skin</code>（SkinType=1，DK_Prefab 本体 + DK_Head 图标）+ <code>Item_81xxx</code> 道具行。</li>
</ul></div>
<div class="warn">⚠️ 唯一例外做不了：<b>Spine 动画岛</b>——情人节「柔情海湾」主体是 Spine 骨骼动画（<code>Homeland_Spine_Valentine/daochu/lover.skel.bytes + atlas</code>，1213×1213）。新皮肤不走这种形态。</div>
<div class="warn">⚠️ 路径纠错：旧资料写的 <code>Res/Unit/City/Buildings/Building_*_Lock.prefab</code> 是<b>功能建筑</b>（酒馆/巢穴等 14xxxxx），不是岛屿皮肤——皮肤本体在 <code>WorldMap/Homeland/</code>。</div>
<h4>制作流程（3D 本体自产）</h4>
<div class="box"><ol>
<li>节日主题概念图（AI 出图定视觉，俯视 45° 对齐现有岛屿构图）。</li>
<li>整岛低模建模（一体网格）+ 512×512 烘焙贴图（AI 可辅助出贴图参考）。</li>
<li>ripple 水波件（可从历套皮肤复用改色）。</li>
<li>组 prefab（可选 idle 动画）→ DK 注册 → 配 <code>Skin__Skin</code> + <code>Item_81xxx</code>。</li>
<li>道具图标一张。</li>
</ol></div>
<span class="wf-badge video">🎬 展示视频（此前拍板方向，与 3D 自产并行不冲突）</span>
<div class="box">展示/售卖侧视频复用英雄皮肤管线：格式锚 <code>Res/Video/VideoRes/egypt_sphinx.mp4</code>（9:16 / h264 / yuv420p / 24fps），分辨率按实际展示框比例、保原生比例别硬缩；氛围动效为主（光影/粒子/旗帜），首尾帧像素差 &lt;3 无缝循环；去音轨；最终压缩走 GRFal <code>compress_video</code>（crf28 移动端标准）。</div>
</div>
"""

WF_M3 = """
<div class="wf">
<span class="wf-badge reuse">♻️ 确认方案：直接搬运 P2/X2 模型资源</span>
<div class="box">不新建模——P2/X2 积累了大量节日家具模型，<b>FBX + 贴图 + prefab 直接迁移</b>到 X3。</div>
<h4>源资产在哪（以 X2 为例）</h4>
<div class="box"><ul>
<li>X2 室内家具根目录：<code>x2client/client/Assets/x2/Res/Shop/Indoor/</code>，按类型三大目录：<b>Building/</b>（柱/地板/墙/窗/壁灯）、<b>Decoration/</b>（吊饰/墙面挂件）、<b>Shelf/</b>（柜台整组陈设）。</li>
<li>资产构成 = <b>FBX + TGA 贴图 + mat + prefab</b>；贴图后缀 <code>_D</code>=漫反射（看花色用这个）/ <code>_N</code>=法线 / <code>_L</code>=自发光。</li>
<li>没有 2D 预览图——选品时把 <code>_D.tga</code> 转 PNG 看花色（平面件贴图≈肉眼所见，立体件是 UV 展开图）。</li>
</ul></div>
<h4>X3 落地路径</h4>
<div class="box"><ul>
<li>模型 FBX → <code>Res/Furniture/Model/&lt;子目录&gt;/Fbx/</code></li>
<li>prefab → <code>Res/Furniture/Prefabs/</code></li>
<li>2D 图标 → <code>Res/UI/Spirits/Furniture/Actv/icon_jiaju_*.png</code>（AI 可端到端产出，参考同目录往期图标构图）</li>
</ul></div>
<div class="warn">⚠️ 搬运 ≠ 拷完就完：命名要对齐 X3 现有规范；材质/Shader 需按 X3 工程适配；最后走 DK 注册 + <code>FurnitureDecorate</code> 配置接线才进游戏。</div>
</div>
"""

WF_M4 = """
<div class="wf">
<span class="wf-badge new">🆕 确认方案：新做（流程参考 X2 室内场景）</span>
<div class="box">每套固定 3 件：<b>横梁（门+柱）/ 地板 / 墙纸</b>，凑齐一套才有完整视觉，按套出。</div>
<h4>X3 落地路径（每件的家）</h4>
<div class="box"><ul>
<li><b>横梁</b>：模型 <code>Res/Furniture/Model/Furniture_Door_Wall_Column_Skin&lt;n&gt;/</code>（Door/Column/Wall 三个 FBX）→ prefab <code>Res/Furniture/Prefabs/Door/Skin&lt;n&gt;/</code>（现有 Skin01~11，新套顺延）。</li>
<li><b>地板</b>：prefab <code>Res/Furniture/Prefabs/Floor/FurnitureFloor_Actv_&lt;节日&gt;.prefab</code> + 贴图 <code>…/Floor/Textures/</code>。</li>
<li><b>墙纸</b>：prefab <code>Res/Furniture/Prefabs/Wallpaper/Wallpaper_&lt;节日&gt;.prefab</code> + 贴图 <code>…/Wallpaper/Textures/</code>。</li>
<li><b>图标</b>：<code>icon_jiaju_*.png</code> ×3（图库页签里同列即同套，可当构图参考）。</li>
</ul></div>
<h4>参考流程（X2 室内场景成熟做法）</h4>
<div class="box"><ol>
<li>定套装主题视觉（对齐节日主 KV 配色/元素）。</li>
<li><b>地板/墙纸 = 平面贴图件</b>：贴图≈玩家肉眼所见，可先 AI 出贴图小样定稿再上模，成本最低。</li>
<li><b>横梁 = 立体件</b>：需建模（门+柱结构），产出 FBX + <code>_D/_N/_L</code> 贴图 + mat + prefab。</li>
<li>X2 惯例还配套 <code>_Show</code> 摆拍 prefab 供商店 3D 展示位转着看——X3 若有对应展示位同步出。</li>
<li>DK 注册 + <code>FurnitureSkin</code> 配置接线。</li>
</ol></div>
</div>
"""

WF_M5 = """
<div class="wf">
<span class="wf-badge reuse">♻️ 航迹：直接用 X2/P2 美术资源</span>
<div class="box"><ul>
<li>航迹 = 船航行拖尾<b>粒子特效 prefab</b>，从 X2/P2 现成航迹特效<b>迁移调整</b>，不新做。</li>
<li>X3 落地：<code>Res/Effect/Prefabs/Ship/&lt;节日&gt;_ship/Fx_*_Trail.prefab</code>。</li>
<li>图标：<code>ItemIcons/icon_global_shipeffects_*.png</code>。</li>
<li>注意粒子贴图/Shader 按 X3 工程适配，性能口径对齐现有航迹。</li>
</ul></div>
<span class="wf-badge new">🆕 行军皮肤：新做模型需求</span>
<div class="box"><ul>
<li>行军皮肤 = 船体造型，<b>要新做 3D 模型</b>：走美需 → 建模 → prefab。</li>
<li>状态特效同目录成套：Idle / Fly / Hit / Fire 等（见 <code>Res/Effect/Prefabs/Ship/&lt;节日&gt;_ship/</code> 现有节日船结构）。</li>
<li>图标：<code>ItemIcons/icon_global_ship_skin_*.png</code>。</li>
</ul></div>
<div class="warn">⚠️ 成套铁律：<code>ShipSkin.FxID</code> 绑定一条航迹——<b>节日船 + 节日航迹成套出</b>，排期要绑在一起。</div>
</div>
"""

WF_M6 = """
<div class="wf">
<span class="wf-badge new">🆕 确认方案：新做（2D 直出，AI 可端到端）</span>
<h4>尺寸规范（自产强制标准）</h4>
<div class="box"><ul>
<li>成品 <b>256×256 透明 PNG</b>。</li>
<li>头像透空内径标准 <b>Ø165</b>（容差 150–180），<b>必须真透空</b>，且小于头像本体 176 让环压边。</li>
<li>单边环厚标准 <b>45</b>（容差 40–55；简洁款取 40、华丽款取 50–64）。</li>
<li>环外径 ~248，四周留 2~4px 边；顶部装饰可顶满 256 但不出血；左右对称。</li>
</ul></div>
<h4>流程步骤</h4>
<div class="box"><ol>
<li>AI 生图（参考图库页签往期框的构图/体量，换节日元素）。</li>
<li>抠透明 + 内径/环厚校验（有复测脚本，见 KB 同目录）。</li>
<li>落地 <code>Res/UI/Spirits/Personalise/AvatarFrame/Img_Player_AvatarFrame_*.png</code>。</li>
<li>配置双表：框定义 <code>PersonalizeAvatarFrameCfg</code>（框 ID 10xxx）+ <code>Item</code> 80xxx 包成可发道具。</li>
</ol></div>
</div>
"""

WF_M7 = """
<div class="wf">
<span class="wf-badge keep">🔵 维持现行：2D 卡面直出（AI 可端到端）</span>
<h4>产出清单</h4>
<div class="box"><ul>
<li>小图标：<code>Res/UI/Spirits/ItemIcons/icon_card_image_*.png</code>。</li>
<li>卡面大图：<code>Res/UI/Spirits/MemorialCard/</code>（V1）或新集卡 <code>Res/UI/Spirits/CardCollectionV2/</code>（V2）。</li>
</ul></div>
<h4>流程步骤</h4>
<div class="box"><ol>
<li>AI 出卡面插画（节日主题场景/角色，对齐往期卡面画风）。</li>
<li>裁切出小图标版本。</li>
<li>DK 注册 + <code>MemorialCard</code> 配表。</li>
</ol></div>
</div>
"""

WF_M8 = """
<div class="wf">
<span class="wf-badge keep">🔵 维持现行：动 + 静两份产出</span>
<div class="box">可售卖聊天表情（Emoticons 系统）每个表情要出<b>两份</b>：<ul>
<li>① <b>动图 GIF</b> → <code>Res/UI/Gif/&lt;名&gt;.bytes</code>（+ <code>.gif</code> 源，~100-270KB）= 发到聊天里会动的本体。</li>
<li>② <b>静态面板图</b> → <code>Res/UI/Spirits/Emoticons/Icon/icon_global_*.png</code>（256×256）= 表情面板缩略图。</li>
</ul>气泡底：<code>Res/UI/Spirits/Emoticons/ui_chat_memebg_*.png</code>。</div>
<div class="warn">⚠️ <b>GIF 透明硬规则</b>（踩过坑：游戏里角色背后一块灰底/白框）：GIF 的<b>背景色索引必须 == 透明色索引</b>——图看着透明也会中招（游戏解码器按索引填底）。存图时 <code>background=transparency</code>、<code>disposal=2</code>，透明调色板项设白（避免滤波黑边渗色）。</div>
<div class="warn">⚠️ <code>.bytes</code> 是运行时加载资源：改完必须重建客户端资源包并更新到服务器才生效，不是拷进工程就完。</div>
</div>
"""

PANELS = {
    "overview": WF_OVERVIEW, "m1": WF_M1, "m2": WF_M2, "m3": WF_M3,
    "m4": WF_M4, "m5": WF_M5, "m6": WF_M6, "m7": WF_M7, "m8": WF_M8,
}

JS = """
<script>
(function(){
  var MODS=[["m1","① 英雄皮肤"],["m2","② 主城皮肤"],["m3","③ 家具"],["m4","④ 装饰三件套"],["m5","⑤ 航迹+行军"],["m6","⑥ 头像框"],["m7","⑦ 纪念卡"],["m8","⑧ 聊天表情"]];
  var body=document.body;
  var toc=document.querySelector('.toc'); if(toc) toc.style.display='none';
  var firstH2=document.getElementById('m1');
  var wfPanels=document.getElementById('wf-panels');

  // 顶部模块页签
  var nav=document.createElement('div'); nav.className='topnav';
  var wrap=document.createElement('div'); wrap.id='modwrap';
  body.insertBefore(nav, firstH2); body.insertBefore(wrap, firstH2);

  function collect(startH2){
    var nodes=[], n=startH2;
    while(n){
      var next=n.nextSibling;
      nodes.push(n);
      n=next;
      if(n && n.nodeType===1 && (n.tagName==='H2' || n.id==='wf-panels' || n.id==='modwrap')) break;
      if(!n) break;
    }
    return nodes;
  }

  function makeModule(id,label,galleryNodes,wfHtml){
    var mod=document.createElement('div'); mod.className='module'; mod.id='mod-'+id;
    var g=null,w=null;
    if(galleryNodes){
      var st=document.createElement('div'); st.className='subtabs';
      var b1=document.createElement('button'); b1.textContent='📷 现有资源图库'; b1.className='on';
      var b2=document.createElement('button'); b2.textContent='🛠 制作流程';
      st.appendChild(b1); st.appendChild(b2); mod.appendChild(st);
      g=document.createElement('div'); g.className='pane';
      galleryNodes.forEach(function(n){g.appendChild(n);});
      w=document.createElement('div'); w.className='pane'; w.hidden=true; w.innerHTML=wfHtml;
      mod.appendChild(g); mod.appendChild(w);
      b1.onclick=function(){b1.className='on';b2.className='';g.hidden=false;w.hidden=true;};
      b2.onclick=function(){b2.className='on';b1.className='';g.hidden=true;w.hidden=false;};
    }else{
      var w2=document.createElement('div'); w2.className='pane'; w2.innerHTML=wfHtml; mod.appendChild(w2);
    }
    wrap.appendChild(mod);
    return mod;
  }

  function navBtn(label,modId){
    var b=document.createElement('button'); b.textContent=label;
    b.onclick=function(){
      nav.querySelectorAll('button').forEach(function(x){x.className='';});
      b.className='on';
      wrap.querySelectorAll('.module').forEach(function(m){m.className='module';});
      document.getElementById('mod-'+modId).className='module on';
      window.scrollTo(0,0);
    };
    nav.appendChild(b); return b;
  }

  // 总览
  makeModule('overview','总览',null,document.getElementById('wf-overview').innerHTML);
  var ob=navBtn('🗂 总览','overview');
  // 各模块（先收集所有节点再搬，避免边遍历边移动）
  var collected={};
  MODS.forEach(function(m){ collected[m[0]]=collect(document.getElementById(m[0])); });
  MODS.forEach(function(m){
    makeModule(m[0],m[1],collected[m[0]],document.getElementById('wf-'+m[0]).innerHTML);
    navBtn(m[1],m[0]);
  });
  wfPanels.remove();
  ob.className='on';
  document.getElementById('mod-overview').className='module on';
})();
</script>
"""

LOGIN_GATE = """<script>
(function () {
  if (location.protocol === "file:") return; /* 本地打开不鉴权 */
  var VERIFY = "https://demo.tap4fun.com/demo-auth/verify";
  var LOGIN  = "https://demo.tap4fun.com/demo-auth/login";
  fetch(VERIFY, { credentials: "include" })
    .then(function (r) { return r.json(); })
    .then(function (info) {
      if (!info.loggedIn) {
        window.location.href = LOGIN + "?returnUrl=" + encodeURIComponent(window.location.href);
      }
    })
    .catch(function () {
      window.location.href = LOGIN + "?returnUrl=" + encodeURIComponent(window.location.href);
    });
})();
</script>"""

def main():
    with io.open(SRC, encoding="utf-8") as f:
        html = f.read()
    # -1) 图库侧 ② 主城皮肤路径纠错（2026-07-08 实地核对：本体在 WorldMap/Homeland，不是 City/Buildings）
    html = html.replace(
        '<div>建筑模型(本体)：<code>Res/Unit/City/Buildings/Building_&lt;itemid&gt;_Lock.prefab</code> / <code>_Unlock.prefab</code></div>'
        '<div>主城场景 3D 资产：<code>Res/Scene/City/EPIC_Fantasy_Town_Low_Poly_3D_Art/</code></div>',
        '<div>整岛模型(本体)：<code>Res/Unit/WorldMap/Homeland/Homeland_&lt;名&gt;.prefab</code> ＋ 资源目录 <code>Homeland_&lt;名&gt;/</code>(Fbx/Texture/Material)</div>'
        '<div>标准构成：主体FBX + 512×512烘焙贴图 · 水波 ripple FBX + 256×128贴图 · 个别带 idle .anim；情人节特例=Spine(<code>Homeland_Spine_Valentine/daochu/lover.*</code>)</div>'
        '<div>DK 注册：<code>Res/Config/DisplayKey/Path_Model.asset</code> 的 <code>DK_Homeland_*</code>（配置 <code>Skin__Skin.DK_Prefab</code>）</div>', 1)
    # 0) 登录验证闸门（demo 部署用；file:// 本地打开豁免）
    html = html.replace('<meta charset="utf-8">',
                        '<meta charset="utf-8">' + LOGIN_GATE, 1)
    # 1) 标题
    html = html.replace("<title>X3 节日外显图库 · 8 大模块全集</title>",
                        "<title>X3 节日外显图库 · 8 大模块 + 制作流程（美术版）</title>", 1)
    html = html.replace("<h1>X3 节日外显图库 · 8 大模块全集</h1>",
                        "<h1>X3 节日外显图库 · 8 大模块 + 制作流程（美术版）</h1>", 1)
    # 2) CSS 注入
    assert "</style>" in html[:6000]
    html = html.replace("</style>", EXTRA_CSS + "\n</style>", 1)
    # 3) 尾部：流程面板 + JS
    tail = ['<div id="wf-panels" hidden>']
    for k, v in PANELS.items():
        tail.append('<div id="wf-%s">%s</div>' % (k, v))
    tail.append("</div>")
    tail.append(JS)
    html = html + "\n" + "\n".join(tail)
    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("WROTE", OUT, os.path.getsize(OUT), "bytes")

if __name__ == "__main__":
    main()
