---
name: x2-strong-consume-client
description: X2 节日强消耗活动客户端代号=JulyGacha，模块ID 21201326，主prefab与代码位置速查
metadata: 
  node_type: memory
  type: reference
  originSessionId: cdb29e8f-c97c-493b-814f-e402fa08e3ad
---

# X2 节日强消耗 客户端速查

- **内部代号 = JulyGacha**（历史七月活动复用），埋点前缀 `UIActivity_new_strong_consume_*`，玩法=消耗攒积分+奖池抽球（如拓荒节 in-game 名 Lucky Ball）
- **模块 ID = 21201326**，注册处 `Assets\P2\GameScript\Activity\ActivityRoot.cs`（`RegisterModule<UIActivityJulyGacha>(21201326)`）
- **主界面 prefab**（按模块 ID 命名）：
  - `D:\UGit\x2client\client\Assets\x2\Res\UI\Prefab\Activity\Module\21201326.prefab`（现役）
  - 同目录 `21201326_old.prefab`（旧版）、`JulyGachaTip.prefab`（气泡提示）、`UI1597ActivityConsumePop.prefab`（消耗弹窗）
- **界面代码**：`Assets\P2\GameScript\Activity\UIActivityJulyGacha\`（UIActivityJulyGacha.cs 主模块 / UIActivityJulyGachaOpen.cs 开奖窗）；逻辑 `Assets\P2\GameScript\GameLogic\Activity\Module\ActivityJulyGacha.cs`
- 规律：X2 活动模块 prefab 大多按**模块 ID 数字**命名放 `Assets\x2\Res\UI\Prefab\Activity\Module\`，按类名 glob 搜不到时改搜代码里的节点名（如 ContMachine）反查 prefab YAML
- 关联：[[x2-festival-monitor]]（强消耗抽奖券礼包口径 2013500177-179）

## 协议与配置完整规格（2026-07-08）
- **实现规格文档（proto 字段/tag 全表 + 配置表 schema + 2025 夏日/占星真实模板行）**：`C:\ADHD_agent\KB\方法论\活动程序开发\X2_强消耗扭蛋机_协议与配置规格.md` —— 新做/换皮该玩法先读这份
- 速记：模块数据=`cspb.JulyTomyGachaModule`(ActvModuleUnion tag145)；抽奖=`JulyGachaReq{actvID,gachaTyp,gachaCnt}`→`JulyGachaAck`；MultiGachaTyp 0=免费/2=付费；消息按**类型名字符串**注册路由无数字消息号。配置=2112 components 标准挂法 `drop×4+actv_show_rank+rank+task×14+package×6+retake×2`（模板行 211200075 夏日2025/211200205 占星2025，⚠️2023 那行是旧任务式别抄）；奖池 2124 `Type=gacha,Drop.typ=single_random,args[].wgt`，DisplayDrop=抽一次的消耗代币；免费上限 const 10137130 `event_strong_consume_free_limit`=1000。

## 换皮视角全链路（2026-07-08 探索沉淀）
- **弹窗 prefab 全集（旧记录 UI1597 是错的）**：主 `Module\21201326.prefab` + 气泡 `Module\JulyGachaTip.prefab` + `Activity\UI2101ActivityConsumePop`(消耗弹窗) / `UI2102ActivityConsumeAward`(开奖) / `UI2103ActivityConsumePop`(奖励预览) / `UI2104ActivityConsumePop`(二次确认) / `UI2105ActivityConsumePop`(概率描述)。另有两个锚点外代码：`UIJulyGachaConfirm.cs`、`UIJulyGachaRewardDesc.cs`（Activity 根目录）。
- **皮全在 prefab 静态引用**：机器A/B背景(`Activity_bg_GachaMachineA/B_2`,NewSprite 版是现役、无 `_2` 的 TextureNew 版是旧素材)、扭蛋球1/2、货币图(UiItemsGachaCoin×7处/QXHHD_Youxibi×2处)全静态；代码动态加载的只有奖励/道具 item 图标（DK 随配置自动变）。**无任何按活动期/主题切资源的代码分支**——换皮=改 prefab Sprite+配置表，代码零改动（往期 5月/8月/占星节全是同套代码复用，git log 无新主题提交）。
- **代码引用的 LC key 仅 4 个**：`new_strong_consume_gacha_task_desc` / `new_strong_consume_tip` / `strong_consume_free_limit_tip` / `new_strong_consume_gacha_desc`(带{0}占位)；其余全 prefab 静态绑定。⚠️ 策划案把循环任务数值写死在 task_desc 文案里（"1550000积分后每30000分奖5个扭蛋币"），改数值必须同步改这条 i18n。
- **🪤 唯一硬编码坑**：`UIActivityJulyGacha.cs:869` `OnRankClick` 传死 `CActivityConfig.EventThanksgivingdayGacha2023`（感恩节遗留常量），换皮若排行榜需按新活动走要改这行。
- **数据侧**：服务端下发 `cspb.JulyTomyGachaModule`（curGotFreeNum/showRank/questList/costs[MultiGachaTyp]/packages/showRewards/dropIDList）；奖池=`CActivityDrop.I(dropID)` 权重表（**dropID 服务端下发**，分阶段奖池即多 drop 切换）；免费抽上限=`CConstConfig.EventStrongConsumeFreeLimit`。
- **非贴图资产**：无 Spine、无内联粒子；动画=Unity Animation(ContMachine 晃动/ContCoin 投币/UI2102 开奖 clip)+嵌套特效 prefab；扭蛋球=Rigidbody2D 物理小球；**音效=Wwise 事件名写死代码里**（`Play_gacha_machine_shake/draw/ball`），换音效要改代码。
- 原始策划案：GSheet `13eHiIX48L7Y865XLGOBxJqWloXiirNC43djoK17i2II` 页签 `v66宝箱版本`(gid 92117869)；prefab 资产导出拷贝在 `D:\newX2\Copy\UIactvfesstrong\`（含 _manifest.txt 全资源清单 + localization_keys.tsv 15键18语言）。
