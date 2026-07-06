---
name: reference-x3-schedulepack-heart-display
description: "X3 type-29 进度礼包(UIActvSchedulePack)中间那颗心的显示机制——EffectDisplay 由 ActvPrefab[0] 驱动(spine/视频)，按活动配置隔离，空则黑心"
metadata: 
  node_type: memory
  type: reference
  originSessionId: caf4f547-bcdb-4b6b-9d2b-1134233608fe
---

# X3 type-29 进度礼包「心形展示位」机制（2026-06-30 砰然心动 102993 黑心排查）

**界面** = `UIActvSchedulePack`（ActvType=29 进度礼包；DK/资源用 `schedule` 前缀，如 `DK_img_Activity_deepsea_schedule_bg`）。prefab=`client/Assets/Res/UI/Prefab/Activity/UIActvSchedulePack.prefab`，业务类 `Scripts/UI/Actv/UIActvSchedulePack.cs`，路由 `ActivityProgressPackCondition`。

## 中间那颗心 = 三层叠（节点 `Root/Animation/Content/Reward/Item/`）
- `BtnHeart`（底图 sprite `ededb874…`）：金色心框 + **深色空心底**——没配东西时看到的"黑心"就是它，点击=看最终大奖 tips（`OnBtnHeartTrigger`→`ShowEndowItemTips(FinalReward)`）。
- `Img`（`mImageHeart`，sprite `cd9f44…`，Type=Filled 垂直）：心形**进度填充**，运行时 `fillAmount = boughtCount/PackList.Count`（`DOFillAmount` 动画）；买 0 天=全透明。
- `Mask`(心形遮罩,alpha≈0.004只裁形状)/`Role`（`mEffectDisplayRole`，**EffectDisplay**）：设计上在心里露出 **英雄 Spine 或视频**。空 → 露底 = 黑。

## 心里放什么 = 按活动配置 `ActvOnline.ActvPrefab`（col24，1-indexed；脚本 0-idx[23]），天然每活动隔离
驱动逻辑 `UIHelper.Activity.cs::ApplyActivityRoleDisplay(cfg, effectDisplay)`：
- `ActvPrefab[0]` 非空且**不以 `DK_video` 开头** → 当 Spine：`effectDisplay.DisplayKey = key`（走 `Path_Spine.asset`）。
- `ActvPrefab[0]` 以 **`DK_video` 开头** → legacy 视频分支：`effectDisplay.VideoDisplayKey = key`（走 `Path_Video.asset`）。
- 都空 → DisplayKey/VideoDisplayKey 均置空 → **黑心**。

实例：同名「砰然心动」两条——`102901` 填 `DK_Role_Spine_34_Skin01`(英雄 Spine，心里有人)；`102993` ActvPrefab 空 → 黑心。

## 关键坑：EffectDisplay 不渲染静态图；视频要 prefab 里有 VideoRoot
- `EffectDisplay.DisplayKey` → `EffectManager.CreateEffect`(实例化**特效/Spine prefab**)；`VideoDisplayKey` → `RVideoPlayer.PlayEmbedVideo`(透明视频)。**没有静态 sprite 分支**——"心里塞张静态图"纯配置做不到。
- 视频路径要求 Role 节点下有名为 `VideoRoot` 的子节点：`ResolveVideoRoot()` 只 `transform.Find("VideoRoot")`，**不自动创建**；`UIActvSchedulePack` 默认 Role 下**没有** VideoRoot → 光配视频 DK 不播。现成件 `Assets/Res/Video/Prefab/VideoRoot.prefab`、深海视频 `DK_video_deepsea_decoration`(→`Video/VideoRes/deepsea_decoration.mp4`) 都在。

## 想让某条活动的心「非 spine 又不破坏共用 prefab」的办法（共用 prefab/底图被 type-29 所有活动复用，不能改外观）
1. **配视频(推荐)**：给共用 prefab 的 Role 加一个 `VideoRoot` 子节点（实例化 VideoRoot.prefab，默认 inactive）= **纯增量、对配了 spine 的活动无感**（视频仅在 VideoDisplayKey 被配时 SetActive）；再把该活动行 `ActvPrefab` 填 `DK_video_xxx`。区分 100% 配置级。
2. **静态图当 effect(零改共用 prefab，偏 hack)**：做个只含 Image 的小 prefab→注册 effect DK→该活动 ActvPrefab 指过去，CreateEffect 实例化。借特效系统放静态图，有生命周期/尺寸假设风险。
3. 配 Spine = 纯配置 1 行最省事，但若不要英雄站位则排除。

## 现状（2026-06-30）
102993 决定**先保留黑心**（不影响功能，仅略丑），后续交程序处理。未改任何配置/prefab。

相关：[[reference_x3_client_new_ui_workflow]]（4件套+EffectDisplay主题位）· [[reference_x3_client_resources]]（DK/Path_*.asset）· [[reference_x3_actvtype_enum]]
