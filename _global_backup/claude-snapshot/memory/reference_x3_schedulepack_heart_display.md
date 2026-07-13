---
name: reference-x3-schedulepack-heart-display
description: "X3 type-29 进度礼包(UIActvSchedulePack)中间那颗心的显示机制+FinalReward手动领取机制——EffectDisplay 由 ActvPrefab[0] 驱动(spine/视频)空则黑心；最终奖励必须点心形手动领、无活动结束兜底补发（X3NEW-1829客诉根源）"
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

## FinalReward（买齐5档最终大奖）= 手动点心形领取，无任何兜底（2026-07-07 X3NEW-1829 客诉查实）
- **发放唯一路径**：玩家点 `BtnHeart` → 客户端 `OnBtnHeartTrigger`（UIActvSchedulePack.cs）先本地判 `GetFinalRewardStatus==UnLock`（不满足只弹 tips 不发请求）→ `ReceiveActivityProgressPackFinalRewardReq` → 服务端 `ActivityMeta.Pack.cs::ReceiveFinalReward` 逐档验 Bought 后 `EndowReward(aPackCfg.FinalReward)`。
- **没有**：买齐自动发 ❌ / 活动结束结算补发 ❌（全仓 grep `finalRewardReceived` 仅此一处写入）。活动过期没点 = 奖励直接丢，只能人工邮件补发。
- **解锁计算**（客户端服务端同款）：`dayItems.day = PackList 下标 i（0-based 0~4）`，`passDay=(nowUTC-活动开始UTC).Days`，`day > passDay` 即 Lock（先判日锁再判已购）。第5档在开始+4天整点(UTC)解锁。
- **客诉画像**（深海每日礼包102993·玩家764881/服1510）：买齐5档（末档解锁当口 08:28 北京买入）→ 以为自动发 100 藏宝图 → 没点黑心 → 投诉"没到账"。**黑心（ActvPrefab空）+ 需手动点 = 玩家极易漏领**，Type29 客诉先查 `finalRewardReceived` 标志 + 是否收到过 Req。
- 配置链速查：`ActvOnline.ContentID → ActvPack(c0=cid, c2=五档PackList, c3=FinalReward的Reward组)`；深海 102993→ActvPack 3002→800005~800009→Reward组40600=藏宝图1200×100。⚠️ContentID 3002 同时被 300201「魔海回声」(Type30)引用，查表别串。
- **活动结束无自动补发（三层查实，2026-07-07）**：①代码层无专属兜底——`RemoveActivity` 对 `progressPackData` 零处理；②通用未领奖邮件兜底 `ProcessActivityUnclaimedRewards` 只遍历任务型 `finishSubItems`，读不到 FinalReward，且全仓无任何 trigger override 它；③兜底前提 `ActvOnline.MailID(c17 MailTemplate)>0`，而 **102993 该列为空**（违反 [[feedback_x3_actv_mailid_check]] 必填规矩——Type29 克隆自查点+1）。→ 活动过期没点心形 = 奖励丢，只能人工邮件补发。
- **数仓查证口径**：领取流水 = `ods_user_asset` `reason_id='item_op_activity_progress_pack_final_reward'`（SysOpReason 枚举小写化）；买齐五档 = `reason_id='buy_gift' AND reason_sub_id IN (五档礼包号) GROUP BY user_id,server_id HAVING count(distinct reason_sub_id)=5`；影响名单 = 前者 LEFT JOIN 后者取 NOT_claimed。

## 现状（2026-06-30）
102993 决定**先保留黑心**（不影响功能，仅略丑），后续交程序处理。未改任何配置/prefab。

相关：[[reference_x3_client_new_ui_workflow]]（4件套+EffectDisplay主题位）· [[reference_x3_client_resources]]（DK/Path_*.asset）· [[reference_x3_actvtype_enum]]
