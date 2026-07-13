---
name: x3-cosmetic-resource-paths
description: X3 八大节日外显模块(英雄皮肤/岛屿皮肤/家具/装饰三件套/航迹/头像框/纪念卡/聊天表情)→客户端资源类型+实际文件路径总表，配活动/出美需/判断换皮工作量时查
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9e46b124-6441-4cf7-893a-41b8c4980d42
---

X3 节日白皮书的 **8 大外显模块**逐一对应到「客户端要哪些资源 + 实际路径」。白皮书本身(`C:\ADHD_agent\KB\产出-数据分析\X3\x3_festival_cosmetics_whitepaper.md`)是变现复盘，**没有资源路径**——下表是交叉 `C:\x3-project\client\Assets\` 实地核对补出来的。判断换皮工作量(3D/动画贵 vs 2D 便宜)、出美需、配活动时查。所有引用都走 DK→GUID 注册(`Res\Config\DisplayKey\Path_*.asset`，配置表写 `DK_` 名不写路径，见 [[reference_x3_client_resources]])。

## ★各模块确认制作方针（2026-07-08 用户拍板）+ 美术版 demo
给美术的可视 demo（图库+制作流程双子页签，已接内网登录）：**https://demo.tap4fun.com/x3_cosmetics_art_demo_fbcc/** ；本地文件 `KB\产出-本地化与美术\X3\外显图库_表情头像框铭牌\X3外显图库_美术制作流程_demo.html`（生成=同目录 `_add_workflow_tabs.py`，基于 8 大模块全集 HTML 注入页签+流程，源图库重跑后再跑它即刷新；登录闸门带 `file:` 豁免，本地双击不受影响）。
| 模块 | 确认方式 |
|------|---------|
| ①英雄皮肤 | 🎬 直接做视频（不再做 Spine，管线见 [[reference-x3-hero-skin-video-production]]） |
| ②主城皮肤 | 🆕 除 Spine 动画岛外全可自产（整岛=低模+512烘焙贴图+水波件，见下②纠错段）；展示视频复用英雄皮肤管线 |
| ③家具 | ♻️ 直接搬运 P2/X2 模型资源（FBX+贴图+prefab 迁移） |
| ④装饰三件套 | 🆕 新做，流程参考 X2 室内场景（[[reference-x2-indoor-furniture-assets]]） |
| ⑤航迹 | ♻️ 直接用 X2/P2 美术资源 |
| ⑤行军皮肤 | 🆕 新做模型需求（FxID 绑航迹成套出） |
| ⑥头像框 | 🆕 新做（2D 规范直出） |
| ⑦纪念卡/⑧表情 | 维持现行 2D 流程 |

## 资源重量速判
前 5 个模块要美术出 **3D/Spine动画/特效**(贵、周期长)，后 3 个只要 **2D PNG**(轻)。

| 模块 | 资源类型 | 重量 |
|------|---------|------|
| ①英雄皮肤 | Spine 骨骼动画立绘 + 头图 | 🔴最重(重绑动画) |
| ②岛屿/主城皮肤 | 3D 建筑模型(FBX+prefab)+场景资产 | 🔴重 |
| ③家具 | 3D 模型(FBX+prefab)+2D icon | 🟡中 |
| ④装饰三件套 | 3D 模型/贴图(横梁/地板/墙纸) | 🟡中 |
| ⑤航迹皮肤 | 拖尾粒子特效 prefab | 🟡中 |
| ⑥头像框 | 2D PNG 256×256 | 🟢轻 |
| ⑦纪念卡 | 2D PNG 卡面 | 🟢轻 |
| ⑧聊天表情 | 2D PNG(图集) | 🟢轻 |

## 逐模块路径(均在 `C:\x3-project\client\Assets\` 下，已实地验证)

### ①英雄晋升皮肤 (Hero Skin, 53xxx) — 最重
- Spine 立绘 prefab：`Res\Spine\Prefabs_Download\Role_Spine_<英雄id>_Skin<n>.prefab`(如 `Role_Spine_17_Skin01.prefab`)
- Spine 动画数据：`Res\Spine\Role_Spine_<id>_Skin<n>\` → `.skel.bytes`(骨骼)+`.png`(图集)+`_SkeletonData.asset`+`_Material.mat`
- 角色头图：`Res\UI\Spirits\Role\Character Portraits\Img_C_H_<英雄id>_Skin<n>.png`
- ⚠️皮肤=重绑骨骼动画不是换图；配置字段 `DK_Role_Spine_xx_Skinxx`

### ②岛屿/主城皮肤 (Island/City Skin, Item_81xxx) — 带战力buff
- ⚠️**纠错(2026-07-08 实地核对)**：早前写的 `Res\Unit\City\Buildings\Building_<itemid>_Lock.prefab` 是**功能建筑**(酒馆/巢穴等 14xxxxx)，不是岛屿皮肤本体，别再抄。
- **真路径**：`Res\Unit\WorldMap\Homeland\Homeland_<名>.prefab` + 资源目录 `Homeland_<名>\`(Fbx/Texture/Material)，共 17 套。
- **一套的完整构成（历套标准范式，比想象轻）**：整岛 1 个一体低模 FBX + 1 张 **512×512 烘焙漫反射贴图**(整岛就一张图，无法线/自发光) + 岸边水波 ripple FBX + 256×128 贴图 + 材质 + 顶层 prefab；个别带 idle 动画(愚人节 `Anim/Homeland_Joker_idle.anim`)。
- **Spine 特例**：情人节「柔情海湾」主体=Spine 动画岛(`Homeland_Spine_Valentine\daochu\lover.skel.bytes`+atlas 1213×1213)，全 17 套里唯一一个——**除它这种形态外全部组件可自产**(2026-07-08 用户确认)。
- **接线**：DK 注册在 `Path_Model.asset`(`DK_Homeland_*`) → `Skin__Skin`(SkinType=1) 的 DK_Prefab(本体)+DK_Head(图标) + `Item_81xxx` 道具行。

### ③家具 (Furniture)
- 模型 FBX：`Res\Furniture\Model\<子目录>\Fbx\`
- prefab：`Res\Furniture\Prefabs\`
- 图标：`Res\UI\Spirits\Furniture\Actv\icon_jiaju_*.png`(如 `icon_jiaju_Egypt01.png`)

### ④装饰三件套 (横梁/地板/墙纸, FurnitureSkin)
- 地板 Floor：prefab `Res\Furniture\Prefabs\Floor\FurnitureFloor_Actv_<节日>.prefab` + 贴图 `…\Floor\Textures\Furniture_Floor_<节日>.png`
- 墙纸 Wallpaper：prefab `Res\Furniture\Prefabs\Wallpaper\Wallpaper_<节日>.prefab` + 贴图 `…\Wallpaper\Textures\`
- 横梁 Door/Column：模型 `Res\Furniture\Model\Furniture_Door_Wall_Column_Skin<n>\` → `Furniture_Door_Skin01.fbx`/`_Column_`/`_Wall_`；prefab `Res\Furniture\Prefabs\Door\Skin<n>\`(现有 Skin01~11)

### ⑤航迹皮肤 (Trail/Route, Skin 30xx) — 纯特效无属性
- 船拖尾特效：`Res\Effect\Prefabs\Ship\Fx_At_<节日>_ship_Trail.prefab`
- Route UI 图：`Res\UI\Spirits\Route\img_route_*.png`

### ⑥头像框 (Avatar Frame, 80xxx)
- `Res\UI\Spirits\Personalise\AvatarFrame\Img_Player_AvatarFrame_<id>.png`(256×256，如 `_Egypt.png`)

### ⑦纪念卡 (Memorial Card, 1800xx)
- V1：`Res\UI\Spirits\MemorialCard\img_card_image_<n>.png`
- V2 新集卡：`Res\UI\Spirits\CardCollectionV2\img_card_v2_<系列>_<n>.png`

### ⑧聊天表情 (Chat Emoji, 154xx)
- `Res\UI\Spirits\Chat\img_cm_emoji_*.png`(图集 `AtlasChat.spriteatlas`)
- 富文本库：`Res\UI\RichText\Emoji\emoji_standard.png`+`.asset`

## x3-media / GRFal 对各模块的可落地度（2026-06 逐工具核实）
判断"某外显能不能让 AI 跑图省美术"时查。x3-media/GRFal 只能产**静态2D图 / 视频 / 3D mesh模型 / 序列帧 / 音频**，**产不了 Spine 2D骨骼动画、也产不了可直接进游戏的特效prefab**。

| 模块 | AI 可落地度 | 说明 |
|------|-----------|------|
| ⑥头像框 / ⑦纪念卡 / ⑧聊天表情 | ✅ **端到端**(纯2D PNG) | 一个 worker 出成品 PNG + DK注册即进游戏 |
| 活动图标/banner/家具icon等2D图 | ✅ 端到端 | 同上 |
| ①英雄皮肤(Spine) | ❌ **只能做上游** | 见下「GRFal ✗ Spine」 |
| ②岛屿/主城皮肤 ③家具 ④装饰三件套(3D模型) | 🟡 只能做上游 | generate_3d 出 FBX mesh 是**毛坯**，游戏要的带绑点/LOD/规范命名的 prefab 仍靠美术；只能当参考/快速概念 |
| ⑤航迹(特效prefab) | ❌ 只能做上游 | 粒子特效 prefab 是引擎里搭的，AI 出不了 |

### 🔴 GRFal ✗ Spine（53工具核实，0 命中）
英雄皮肤核心=Spine骨骼动画(`.skel.bytes`+atlas+SkeletonData+绑骨/蒙皮/K帧)，**GRFal 无任何工具产出**。
- 三个"沾边但顶替不了"的：`creative_workflow/sprite_sheet`=**逐帧序列帧**(和Spine骨骼动画两套不兼容体系，导不进Role_Spine prefab)；`generate_motion`=**3D**人形动作(非2D Spine)；`generate_video`=MP4视频(非可换肤循环立绘)。
- GRFal **能帮的只有上游两步**：`generate_image`(出静态全身原画，注入英雄现有立绘锚形象) + `image_layered`(AI自动分层，辅助Spine拆件)。
- **搭骨骼+蒙皮+K动作+导出.skel/atlas/prefab 这步绕不过去**，仍是美术在 Spine 软件做。
- 落地分工流程见对话(原画→美术Spine→Unity prefab+DK→生头图→配表)。
- ⚠️ 但白皮书第七章：**夏日恋歌英雄皮肤=复用情人节赛米拉+海泽尔现成皮肤**，零美术零生成、只配置引用 DK——换皮场景优先「找现成」(见 [[reference_x3_art_resource_spec]] 维度D)，不是生成。

## 三个轻量2D外显的配置表 + 发放机制（2026-06-14 实地核实）
做「聊天表情/头像框/铭牌」一波时直接用，完整生产链路见 KB `产出-本地化与美术\X3\X3_外显生产链路_聊天表情+头像框+铭牌.md`。
| 模块 | tsv 真源 | 尺寸 | 发放方式 |
|------|----------|------|----------|
| 聊天表情(快捷回复) | `ChatEmojyReply__ChatEmojyReply.tsv`(仅9个 ID/Name/DK_icon) | **72×72** | 全员内置不售卖 |
| ⚠️聊天表情其实5套 | 见下「表情5系统」 | — | 做新表情别只盯9个快捷回复 |
| 头像框 | `Personalize__PersonalizeAvatarFrameCfg.tsv`(定义框+Buff) **+** `Item__Item.tsv` 80xxx(包成道具) | **256×256** | 双表：定义表定框，Item_80xxx 参数=`框ID|时长` 包成可发道具，活动发 Item / 自选礼包 1080。⚠️**框定义表 ID=10xxx**(如mermaid10019/Egypt10026,2026-06 max10075)，**80xxx 是 Item 道具 ID 不是框 ID**(2026-06 max80347)；新头像框礼包抄 Egypt 框10026+道具80110模板，9.99礼包价格档=PackPrice **107**，DK_Background 用 `DK_Bg_CM_Item4`。实例:深海印记礼包(框10076/道具80348/Pack211019) |
| 铭牌=头衔 | `PlayerTitle__PlayerTitle.tsv`(Quality 0蓝1紫2橙3+站位Buff+Reimburse钻石补偿) | title板 **752×192**(ActvKvk/Activity `*_icon_title.png`)+小图标(ItemIcons) | 活动表直接挂(ActvKvk.PlayerTitleID/PlayerTitleID2)，KvK/世界征服头衔 |
- ⚠️ **X3 无独立"铭牌"系统**，铭牌就是 PlayerTitle(头衔)；白皮书8模块没单列铭牌。
- 🎯 **头像框标准尺寸限制(自产强制)**：256×256 透明PNG；头像透空内径标准 Ø165(容差150–180,必须真透空且<头像本体176让环压边)；单边环厚标准45(容差40–55,简洁取40华丽取50–64)；环外径~248留2~4px边；装饰顶满256不出血；左右对称。换尺寸=内径0.62–0.68×边长/环厚0.16–0.20×边长。明细+复测脚本见 KB 同目录图库。
- 🔑 **X3 表情共 5 套系统**（做"一波聊天表情"先认准走哪套，全集可视化见 KB 同目录 `表情全系统.html`）：
  1. 快捷回复 `ChatEmojyReply`(9个, `Chat/img_cm_emoji_*` 72×72, 内置不卖)
  2. ⭐**可售卖聊天表情 `Emoticons`**(22个,ID100-240, 主表`Emoticons__Emoticons.tsv`字段ID/Res/Pack/Name/ShowType/备注) — **节日通行证/礼包卖的就是这套**；解锁=Item **154xx表情包道具(ItemType24,"使用后获得聊天表情",param=Emoticons.ID)**进奖励 或 Emoticons.Pack绑包；UIChatEmojiPanel发,SocialMeta.Emoji.cs管,ShowType=1买了才显示。**做可卖表情走这套**
     - ⚠️**双DK结构(2026-06-15实测,现有22个清一色动图零静态)**:① `Res`字段=`DK_{名}`→**动图** `Res/UI/Gif/{名}.bytes`(+`.gif`源,~100-270KB)=**发到聊天里会动的GIF** ② `DK_icon_global_{名}`→静态PNG `Spirits/Emoticons/Icon/icon_global_*.png`**256×256**=**仅表情面板缩略图**。气泡底`Spirits/Emoticons/ui_chat_memebg_*`。Path_Emoticons.asset注册两套DK。→**做新表情要出动图GIF(Res)+静态icon(面板)两份**;只有静态会是这套里唯一不动的(快捷回复ChatEmojyReply那9个才是纯静态72×72,另一套)。
     - ⚠️**GIF .bytes 透明铁律(2026-06-17 世界杯48表情聊天里显灰底/白框踩坑)**:游戏端 `UniGifDecoder.cs` 解码第0帧时 disposal 被强制为2→**整张贴图先用 `bgColor` 填满,之后透明像素不再覆盖**;`bgColor` 是否透明只看 line126 `背景色索引==透明色索引`。**所以 GIF 的 LSD 背景色索引必须==GCE 透明色索引**,否则透明区被填成不透明 `palette[bgIndex]`(默认 palette[0]=白)→角色背后一块实底(被聊天面板叠色显灰)。**文件用 PIL/Read 看是透明的也会中招**(PIL 认 alpha,这个解码器走索引填充,光看文件透明会误判)。正例 Bella01/2026:bgIndex==transIndex==127→白透明。修复=存 GIF 时 `background=transparency`(并把透明调色板项设白,对齐现役表情避免双线性过滤黑边渗色);48张就地批改范式:`Image.open→getpalette改t项=白→putpalette→save(format=GIF,transparency=t,background=t,disposal=2)`。`_gen_emote_gif.py`(动效版)同样缺 `background=`,改它要补。.bytes 是运行时加载资源→**改完必须重建 client 资源包/AssetBundle 并更新 dev 服才生效**(同 march-emoji/[[project-x3-worldcup-activity]] line238 "DK配置在但运行时not found":dev跑的是旧包)。
  3. 自制内联表情 `custom_emoji1`(31个 EmojiFace黄脸, 图集`RichText/Emoji/custom_emoji1.png`1024×512, 单格~117×121) — 通用打字插文本(rich text)非主题
  4. 标准 EmojiOne `emoji_standard`(1638个,1024×2048)/TMP EmojiOne — 第三方开源**别动**
  5. 角色头顶 `CuteEmotes`(6656×2560图集+PopupEmote prefab驱动) — 世界内冒泡,非聊天文本
- ⚠️ **`HeroStickers`(英雄羁绊贴纸 icon_bond_* 512×512, 27个) 名字带Sticker但不是聊天表情**，是**英雄羁绊收集册**(养成+外显,"相册-羁绊"红点,关联DateMemory约会回忆)：
  - 投放=跟英雄绑定常驻系统(ShowConditionGroup: TimeCycle/活动时间内/拥有英雄 控制贴纸何时显示)，新英雄/CP上线配套出
  - 获取=**点亮**(非购买): LightConditionGroup(拥有英雄/皮肤/英雄星级)满足自动点亮→给积分+永久Buff(StickerBuff万分比)+道具；本质英雄/皮肤拥有度衍生奖励,间接绑gacha
  - 积分档位LightPointsLevel(25铜/50银/75金/100/150钻)领道具；使用=UIHeroStickers收集册看,点亮给永久数值Buff,可摆StickerBoard
  - 5表真源: `HeroStickers__{HeroStickers/LightConditionGroup/ShowConditionGroup/LightPointsLevel/StickerBuff}.tsv`；服务端`HeroStickerMeta.cs`；详见 KB `X3_外显生产链路…md` §1.4

## 📷 8 模块实物图库（已建，2026-06-17）
白皮书 8 大模块每件外显的实际美术资源，已做成可视 HTML（162 件，按白皮书 §1~§8 排序），并从白皮书顶部「配套图库」块索引进去：
- 图库：`KB\产出-本地化与美术\X3\外显图库_表情头像框铭牌\X3节日外显图库_8大模块全集.html`
- 生成脚本：同目录 `_gen_festival_cosmetics.py`（配置/资源更新后重跑刷新）
- 白皮书入口：`KB\产出-数据分析\X3\x3_festival_cosmetics_whitepaper.md` 顶部 "📷 配套图库" + #m1~#m8 锚点
- **DK_Icon→PNG 解析配方**（脚本已固化，复用查图标用）：各模块道具的 2D 图标 = `Item__Item.tsv` col21 `DK_Icon`（去 `DK_` 前缀→同名 `.png`）；英雄皮肤立绘=`Hero__HeroSkin.tsv` col10 `DK_HeroCard`→`Role/HeroCard/Role_C_*`；家具按 `FurnitureDecorate__FurnitureDecorate.tsv` col7 Icon + col29 来源描述自动分组；行军船=`Ship__ShipSkin.tsv` `DK_Icon`+FxID 绑航迹。图标散落 `Res/UI/Spirits/{ItemIcons,Furniture,Personalise/AvatarFrame,Emoticons/Icon,Role/HeroCard}`，递归 glob 找。⚠️文件名大小写可能与 DK 不一致（如 `Role_C_20_skin02` 小写），Windows 不敏感但 `find -name` 敏感。

## 📄 非节日外显投放梳理（已建，2026-06-18）
白皮书只展开了节日外显110件，把非节日外显187件只列了分类。这份补集HTML逐模块梳理「内容/属性/投放来源活动」（全来自当前tsv实地核对）：
- **图鉴版(主用)**：`KB\产出-数据分析\X3\X3非节日外显投放图鉴.html`（生成脚本 `_gen_nonfestival_cosmetics.py`，~78MB图内嵌）——253件每件贴实物图(DK→PNG)+具体礼包/活动来源(橙字)+**投放D天/解锁条件(绿字,如"D8起·获得斯隆后2天")**；顶部分类页签筛模块 + **双时间轴切换(绝对时间=版本2024→2026 / 服务器时间=玩家生命周期D0→D60+)**，全部外显都落轴。
  - 🔑**投放时间权威源=GSheet `16Halv5vTyyL3E60Uyc2ZON_2GOnFjXpxa0rMT45rFts`（X3前期计划/排期）多页签**，已全部存档进KB同目录tsv：
    - 「英雄投放节奏」gid=2047950082 → `_hero_deploy_days.tsv`：英雄/皮肤首投day1-56 + 解锁条件(如艾丽丝海域开放16天=D16/克里斯塔尔D12/自由柳柳D13)
    - 「活动排期」gid=1842549936 → `_actv_schedule.tsv`：**系统活动服务器D天**(俘获芳心D1/舞娘助力D2/知识进修D5/伟大航道D8/异域盛典D15/永恒之岛D18/永恒之主D23)
    - 「运营日历」gid=1943216471 → `_op_calendar.tsv`：**节庆活动绝对真实日历**(万圣2024-10→春节2026-02)，每节庆产哪些外显(家具/船/英雄皮肤/头像框/表情/纪念卡列)
    - 「跨服战」gid=120652022：KvK首次D天(公会争霸D7循环/世界入侵~D35/风暴逐鹿~D42/魔海回声~D49)
    - 「建筑等级」gid=1055752070：建筑等级↔D天曲线(酒馆lv15≈D13)
  - 🕐**时间填充原则(用户确认)**：系统活动→活动排期服务器D天；节庆活动→运营日历真实月份(服务器D天因开服而异=SF「随节庆」桶)；建筑解锁→随建筑升级；**查不到排期的才标"不确定"(SX)，不臆测D天**。技能皮肤具体出处=跨表追530xxx道具(Pack18xxx道具礼包$29-49.99为主力)。
- 文字版：`KB\产出-数据分析\X3\x3_nonfestival_cosmetics_whitepaper.html`（不带图速览版，与节日白皮书同目录）
- **核心结论**：非节日外显≠付费视觉，而是**养成/PvP引擎**——几乎全带数值Buff（纪念卡10组战斗buff/头像框攻防/头衔站位buff/船皮肤声望buff/羁绊贴纸永久+1.5%/技能皮肤解锁技能），靠数值驱动收集；付费点只有3处且浅（家具内购礼包$2.99-49.99×10、表情礼包$4.99×3、战役终结礼包仅1款技能皮肤）。
- **实测件数（修白皮书估计口径）**：技能皮肤22款(非25,许愿池不直接发英雄皮肤)/纪念卡79张(MemorialCard ID1-79,180074-78属另一系统)/基础家具99条(纯装修~70)/基础装饰13件(白皮书24把横梁三件套重复计)/基础表情25(快捷回复9+Emoticons16)/头衔4件(非7,白皮书把头衔+同名头像框混算)/非节日头像框15/船皮肤8套+航迹7/羁绊贴纸27枚。

## 关联
- DK→GUID 注册机制：[[reference_x3_client_resources]]
- 出美需颗粒度/尺寸规范：[[reference_x3_art_resource_spec]]
- 主城皮肤换皮链路(X2参照)：[[reference_x2_city_skin_chain]]
- 白皮书变现侧调整方案：见白皮书第四章
