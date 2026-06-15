---
name: x3-cosmetic-resource-paths
description: X3 八大节日外显模块(英雄皮肤/岛屿皮肤/家具/装饰三件套/航迹/头像框/纪念卡/聊天表情)→客户端资源类型+实际文件路径总表，配活动/出美需/判断换皮工作量时查
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9e46b124-6441-4cf7-893a-41b8c4980d42
---

X3 节日白皮书的 **8 大外显模块**逐一对应到「客户端要哪些资源 + 实际路径」。白皮书本身(`C:\ADHD_agent\KB\产出-数据分析\X3\x3_festival_cosmetics_whitepaper.md`)是变现复盘，**没有资源路径**——下表是交叉 `C:\x3-project\client\Assets\` 实地核对补出来的。判断换皮工作量(3D/动画贵 vs 2D 便宜)、出美需、配活动时查。所有引用都走 DK→GUID 注册(`Res\Config\DisplayKey\Path_*.asset`，配置表写 `DK_` 名不写路径，见 [[reference_x3_client_resources]])。

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
- 建筑模型 prefab：`Res\Unit\City\Buildings\Building_<itemid>_Lock.prefab` / `_Unlock.prefab`
- 主城场景 3D 资产：`Res\Scene\City\EPIC_Fantasy_Town_Low_Poly_3D_Art\`(Meshes/Materials/Textures/Prefabs)

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
| 头像框 | `Personalize__PersonalizeAvatarFrameCfg.tsv`(定义框+Buff) **+** `Item__Item.tsv` 80xxx(包成道具) | **256×256** | 双表：定义表定框，Item_80xxx 参数=`框ID|时长` 包成可发道具，活动发 Item / 自选礼包 1080 |
| 铭牌=头衔 | `PlayerTitle__PlayerTitle.tsv`(Quality 0蓝1紫2橙3+站位Buff+Reimburse钻石补偿) | title板 **752×192**(ActvKvk/Activity `*_icon_title.png`)+小图标(ItemIcons) | 活动表直接挂(ActvKvk.PlayerTitleID/PlayerTitleID2)，KvK/世界征服头衔 |
- ⚠️ **X3 无独立"铭牌"系统**，铭牌就是 PlayerTitle(头衔)；白皮书8模块没单列铭牌。
- 🎯 **头像框标准尺寸限制(自产强制)**：256×256 透明PNG；头像透空内径标准 Ø165(容差150–180,必须真透空且<头像本体176让环压边)；单边环厚标准45(容差40–55,简洁取40华丽取50–64)；环外径~248留2~4px边；装饰顶满256不出血；左右对称。换尺寸=内径0.62–0.68×边长/环厚0.16–0.20×边长。明细+复测脚本见 KB 同目录图库。
- 🔑 **X3 表情共 5 套系统**（做"一波聊天表情"先认准走哪套，全集可视化见 KB 同目录 `表情全系统.html`）：
  1. 快捷回复 `ChatEmojyReply`(9个, `Chat/img_cm_emoji_*` 72×72, 内置不卖)
  2. ⭐**可售卖聊天表情 `Emoticons`**(22个,ID100-240, 主表`Emoticons__Emoticons.tsv`字段ID/Res/Pack/Name/ShowType/备注, 图`Spirits/Emoticons/Icon/icon_global_*.png`**256×256**, 气泡底ui_chat_memebg_*, Path_Emoticons.asset注册) — **节日通行证/礼包卖的就是这套**；解锁=Item **154xx表情包道具(ItemType24,"使用后获得聊天表情",param=Emoticons.ID)**进奖励 或 Emoticons.Pack绑包；用UIChatEmojiPanel发,SocialMeta.Emoji.cs管,ShowType=1买了才显示。**做可卖表情走这套**
  3. 自制内联表情 `custom_emoji1`(31个 EmojiFace黄脸, 图集`RichText/Emoji/custom_emoji1.png`1024×512, 单格~117×121) — 通用打字插文本(rich text)非主题
  4. 标准 EmojiOne `emoji_standard`(1638个,1024×2048)/TMP EmojiOne — 第三方开源**别动**
  5. 角色头顶 `CuteEmotes`(6656×2560图集+PopupEmote prefab驱动) — 世界内冒泡,非聊天文本
- ⚠️ **`HeroStickers`(英雄羁绊贴纸 icon_bond_* 512×512, 27个) 名字带Sticker但不是聊天表情**，是**英雄羁绊收集册**(养成+外显,"相册-羁绊"红点,关联DateMemory约会回忆)：
  - 投放=跟英雄绑定常驻系统(ShowConditionGroup: TimeCycle/活动时间内/拥有英雄 控制贴纸何时显示)，新英雄/CP上线配套出
  - 获取=**点亮**(非购买): LightConditionGroup(拥有英雄/皮肤/英雄星级)满足自动点亮→给积分+永久Buff(StickerBuff万分比)+道具；本质英雄/皮肤拥有度衍生奖励,间接绑gacha
  - 积分档位LightPointsLevel(25铜/50银/75金/100/150钻)领道具；使用=UIHeroStickers收集册看,点亮给永久数值Buff,可摆StickerBoard
  - 5表真源: `HeroStickers__{HeroStickers/LightConditionGroup/ShowConditionGroup/LightPointsLevel/StickerBuff}.tsv`；服务端`HeroStickerMeta.cs`；详见 KB `X3_外显生产链路…md` §1.4

## 关联
- DK→GUID 注册机制：[[reference_x3_client_resources]]
- 出美需颗粒度/尺寸规范：[[reference_x3_art_resource_spec]]
- 主城皮肤换皮链路(X2参照)：[[reference_x2_city_skin_chain]]
- 白皮书变现侧调整方案：见白皮书第四章
