---
name: p2-city-skin-assets
description: P2 主城皮肤美术资源结构（CityBuildingNew 路径/标准目录/2D展示图位置/皮肤vs功能建筑分类/图库HTML），P2 主城皮肤找资源先读
metadata: 
  node_type: memory
  type: reference
  originSessionId: 42ce653e-2e7b-416e-a7f6-25cb4ac83e33
---

P2 主城皮肤 3D 资源全在本机 E 盘 P2 仓：`E:\P2\client\client\Assets\P2\Res\Map\CityBuildingNew\`（⚠️ 路径里嵌两层 client）。2026-07-09 实地扫描（bugfix 分支）：72 个文件夹 = **61 款主城皮肤 + 11 个非皮肤**（功能建筑/基底）。

## ⚠️ 分支真源（先确认再扫）
**P2 client 活跃美术真源 = `bugfix` 分支**（每日更新）；`dev` 分支 2026-05-13 起停更（GitLab default_branch 仍标 dev，是死的）；`master` 美术比 dev 还旧。找不到新资源先 `git log -1` 看快照日期 + 切 bugfix。远程 GitLab API 可用 `$env:GITLAB_TAP4FUN_TOKEN`（项目 `p2%2Fclient`，仓内路径前缀 `client/`）；美术文件走 **Git LFS**（API raw 只给 130B 指针，要发 `info/lfs/objects/batch` 换下载 URL，Basic auth=oauth2:token）。

## 标准结构（新式皮肤，约 2024 起）
```
CityBuildingNew/{SkinName}/
├─ Common/        Fbx + 共用贴图(Normal等) + 2D展示图PNG(见下)
├─ High/          {SkinName}Lv1~Lv3.prefab ×2~5档(含Lv1.5/2.5半档) + Material/Texture(_High)
├─ Low/           同名 prefab + _Low 贴图
└─ Ui{SkinName}LvX.prefab   UI 3D展示prefab(部分用DK数字命名如 Ui151104627)
```
- 贴图命名 `P2_{SkinName}{编号}_Diffuse/_Light/_Normal(_High/_Low).tga`，全 TGA，单皮肤 80~640MB
- **老式皮肤（约2023前）单模型无等级分档**（High/Low 各 1 个 prefab）
- ⚠️ **克隆残留命名坑**：prefab 名可能是克隆源节日残留（实锤：ChristmasSkin2024 文件夹里 prefab 全叫 ThanksGiveSkin2024Lv*.prefab）——找资源认文件夹名，别信 prefab 名

## 2D 道具图标（皮肤选择/详情界面用图）——查图标的权威姿势
**不是 RenderTexture 实时渲染**，每款皮肤有官方道具 ICON，走 DK 系统。**权威反查法**（别在文件夹里瞎搜）：
1. `Assets\P2\Res\DisplayKey\Path_Prefab.asset`（`- key: N` + `objPath:` 纯文本）按 objPath 含 `CityBuildingNew/<皮肤>` 拿到该皮肤全部 DK key；
2. 同目录 `Path_Icon.asset` 用同 key 查图标路径。**主模型 Prefab 型 DK 没注册时别急着判"无图标"**：皮肤文件夹根下的 `Ui<数字>.prefab` 文件名就是 DK key，拿它去 Path_Icon 查往往已有图标（拓荒2026/JuneSkin2026 都是这样找到的）。图标散落三类位置：皮肤自己目录 `Common/Texture/`、`UI/Sprite/ItemIcon/<key>.png`、**各 Gacha 活动 UI 目录**（老皮肤，如 `UI/Sprite/Activity/SandGacha/`、`OctAct/`、`ValentineGacha/`）。
3. `Editor\DisplayKey\Display_Prefab.asset` 的 desc 是中文官方名（unicode-escape 编码，`txt.encode('latin-1').decode('unicode_escape')` 解），例：151105384/386=「2026深海节（6月）主城皮肤」=PirateSkin2026 海盗启航。
脚本已固化：`C:\ADHD_agent\skills\blender-fbx-render\map_dk_icons.py`。61 款中 57 款有图标；DK 未注册的待上线款用 Blender 渲模型兜底（坑已修全：alpha CHANNEL_PACKED / Cycles CPU / ASCII FBX 走 FBX2glTF / 跳过 @aim 动画 fbx 和 *Shadow.fbx*）。

## 非皮肤文件夹（勿当皮肤处理）
MaincitySkin(默认主城本体 CityShuttleHall lv1/6/12/18/30，皮肤替换的基底)、CityHallLV6、DrillGround、ResourceStation、SurvivorCamp、TreasureChest、SecurityBox(Map)、MonkeyNest(大地图资源点)、WonderCity、Animation。判据：主城皮肤有 Lv 档 prefab 或 CityHall 变体命名。

## 文件夹名↔官方名对号表（⚠️文件夹名一半是克隆残留，以 Display_Prefab desc 为准）
- 深海节2025=`JuneSkin2025`(鲸鱼船拼装套装) · 深海节2026=`PirateSkin2026`(海盗启航,低级木船/高级黑金,icon=ItemIcon/151105558&560)
- 春节2026=`IceTiger2025` · 登月节2025=`MidAutumnSkin`(不是中秋!) · 登月节2026(7月)=`PioneeringFestival2026Skin`(低/高级)+`MachCitySkin2026`(不是拓荒/机甲!)
- 音乐节2026(9月)=`SeptemberSkin2026` · 复活节2026大富翁=`MonopolySkin2026` · 钓鱼2026=`FishingSkin2025`
- 拼装套装外显族(初级/高级/拼装完成三态)：坦克=`MarchCitySkin2026`、巨龙=`Mayskin2026`、爆裂鼓手=`AugustSkin2026`、周年悟空=`MonkeyKingSkin`、科技节=`ScienceSkin2025`、星球25.10=`PlanetSkin2025`
- **非主城皮肤别收**：`HandofCreation`(创世之手=装饰)、`JuneSkin2026`(深海节2026装饰Ui容器,沙堡/章鱼海盗装饰本体在 `Decorations/BeachDeco2026(SandCastle*)`、`OctopusDeco2026`)

## 产出
59 款皮肤图库（15 主题分组·DK官方名校正 + 道具ICON统一表现 + prefab/贴图/体量明细）：`C:\ADHD_agent\KB\产出-本地化与美术\P2\主城皮肤图库\P2主城皮肤图库_资源结构全集.html`（生成脚本在 skills\blender-fbx-render\）

关联 [[x2-city-skin]]（X2 是另一套 X2_T_Shop 结构，勿混）
