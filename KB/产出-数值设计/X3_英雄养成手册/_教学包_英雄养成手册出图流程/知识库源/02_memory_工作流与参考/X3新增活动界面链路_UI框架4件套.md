---
name: reference-x3-client-new-ui-workflow
description: X3 客户端新增一个活动界面的完整链路（UI框架4件套/手写Auto绑定/路由分流点/可复用组件清单），做新界面或换皮界面前先读
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1cc55f5e-84e0-4e4f-a468-e25e40422ad5
---

# X3 客户端新增活动界面链路（2026-06-11 世界杯竞猜案验证）

X3 = 纯 UGUI + prefab + 代码生成绑定（**无** UI Toolkit/UI Builder/FairyGUI；X2 探索过 UI Builder 没落地，别引入）。

## 一个界面 = 4 件套

| 件 | 路径 | 说明 |
|---|---|---|
| 业务类 | `Assets\Scripts\UI\Actv\UIActvXxx.cs` | partial，继承 `UIBase<UIActivityData>`，OnLoad 里先调 `OnAutoLoad()` |
| 绑定类 | `Assets\Scripts\UI\Gen\Auto_UIActvXxx.cs` | **可手写**（标准是编辑器工具生成）：`[GameCommon.Identifier(任意全局唯一int)]` + `[UIDescribe(assetPath, layer, label)]` + OnAutoLoad 里 `GameObject.FindByFullPath("Root/...")` 按路径绑字段。⚠️ Identifier 不是类名哈希，是工具保存时存的，唯一即可；工具重生成会覆盖手写版、ID 变了也无碍 |
| prefab | `Assets\Res\UI\Prefab\Activity\UIActvXxx.prefab` | 节点路径必须与绑定代码一字不差；要被代码填的图/字必须是 TFWImage/TFWText |
| 路由 | ActvType→UI 一对一：`CSSharedHotfix\...\ActivityTriggerConditions\` 的 Condition 类 `GetActivityUIType()` | **复用现有 ActvType 换 UI**：在 `ActivityMeta.GetActivityUIType()`（Entity\Player\Activity\ActivityMeta.cs ~1480 行）按 cfg.ContentID 段分流，客户端热更层搞定、服务端零改动 |

打开界面：`WndMgr.Show<T>(data)`；类型注册自动（UITypeAutoRegisterGen 编译期扫描）。

## 可复用组件（拼礼包类界面零新功能件）

- 价格购买按钮 `UIBtnPurchase`（`Scripts\UI\Gift\`）：本地化价格+拉支付+限购变灰全内置，`WidgetContainer.AddSingle` 挂上调 `Show(giftID)`；样式 prefab UIBtnPriceBlue/Green
- 道具格 `ItemUnitView`+`ItemSmall.prefab`（自带品质框）；整列表一行填充 `ItemUnitHelper.RefreshLoopReward(go, rewardID)`——go 内需 LoopScrollRect+ItemUnitView 模板
- 倒计时 `UIHelper.StartTiming` / 标题倒计时背景一条龙 `UIHelper.SetActivityBaseInfo`；通用美术=img_gift_bg_4+沙漏 img_gift_time（别新出）。**背景天然配置驱动**：传入的 bgImage 会被 `ActvOnline.ActvImg`(DK) 覆盖（UIHelper.Activity.cs:249）——prefab 里垫的背景图只是兜底，多套背景=每实例 ActvImg 填不同 DK，零代码
- **活动「主题展示位」=配置级可换的角色 Spine/视频**（2026-06-15 开箱案验证）：界面 prefab 放一个 `Root/Role` 节点挂 `EffectDisplay` 组件，`UIHelper.SetActivityBaseInfo(..., effectDisplay)` 会把 `ActvOnline.ActvPrefab[0]`（col23/0-idx[23]，proto 注释「DK_主题spine」）填进 `effectDisplay.DisplayKey`→走 `Path_Spine.asset` 注册表→`Res/Spine/Role_Spine_XX/`。开箱(ActvType15/天马福箱 101513)就是这么把卡蜜拉 Spine 配成背景角色的（[23]=DK_Role_Spine_39_Skin01；底图 ActvImg[22] 在后、Role Spine 在前两层叠）。⚠️**同一个 EffectDisplay 还有 `VideoDisplayKey` 分支(与 DisplayKey/Spine 互斥)**——视频化皮肤(DK_Spine空/DK_Video有值)走它。要让某界面背景放「活的角色」：加 Role/EffectDisplay 节点，Spine 皮肤填 ActvPrefab、视频皮肤走 VideoDisplayKey。竞猜界面(UIActvWorldCupGuess)现在只有静态 Bg 无 Role 节点，要加才能放爱莉希雅视频背景
- **可滑动+居中的列表（奖励/道具列表标准做法，2026-06-15 莫琪 GUI 做世界杯竞猜验证）**：别用 `localScale` 死缩硬塞（静态、多了挤、少了靠左）。三件套——
  ① **滑动**=节点挂原生 `ScrollRect`：`m_Horizontal:1 / m_Vertical:0`（只横滑锁竖滑）+ `m_MovementType:1`(Elastic 弹性，Elasticity 0.1/Inertia 1/Deceleration 0.135)，连 `m_Viewport`(可视窗，带 Mask/RectMask2D 裁溢出) + `m_Content`(排物品容器)。
  ② **居中**=Content 挂 `GridLayoutGroup`，命门 `m_ChildAlignment:4`(=MiddleCenter，物品少没填满时整体居中不靠左)；配 `m_CellSize`(如180×180)/`m_Spacing`/`m_Constraint`(1=FixedColumnCount)+`m_ConstraintCount` 控行列。
  ③ **内容自适应**=Content 同时挂 `ContentSizeFitter` `m_HorizontalFit:2`(PreferredSize)→内容宽度随物品数自动撑开，ScrollRect 才知道能滑多远（漏了=滑不动/滑过头）。
  左右两列(ColumnL/ColumnR)各独立一套此结构。一句话：**滑动容器+居中布局(MiddleCenter)+内容自适应，别用缩放硬塞**。
- DK 动态图 `UIHelper.SetImageWithDisplayKey(img, dk)`；会随配置变的图走 DK，固定装饰焊死 prefab
- 通用图库：`Res\UI\NewSprite\Common\`（frame/IconBox 品质框/ProgressBar）、`Spirits\CommonNew\`（按钮 img_cm_anniu 系列）

## 关键暗坑

- **X3 背景自适应用自研 `RectTransformScaler` 脚本**（不是 Unity 原生 AspectRatioFitter）：挂在全屏 Bg 节点上持续接管 localScale（Match Mode=Expand 按父级撑满，会把 Scale 压到 0.26 之类）。**复制 Bg 当装饰节点（徽章/面板）会把它带过去**→Scale 怎么改都被弹回；修法=装饰件上 Remove Component + Scale 归 1，仅 Bg 本体保留。另：模板 `Animation` 节点挂入场动画也会接管 Scale——UI 调大小一律改 Width/Height 不碰 Scale。"改了就还原"通用诊断：找接管该属性的组件（动画/Scaler/Layout），改它的参数而不是硬掰。
- **TFWText 默认勾 Best Fit（多语言自适应）**：勾着时 Font Size 字段失效，实际字号=框内能塞下的最大值、封顶 Max Size——调字大小=改 Max Size+拉大文本框，别取消勾（10语言长文案防爆框）；Min Size 默认 2 太极端建议设 20。
- **X3 标题金字=TFWText+BetterOutline(描边投影)+Gradient2(黄色Multiply渐变) 三件套**：复制 txt_title 出来的文字全带这俩组件——`Gradient2 不删则 Color 改了也不生效`（被渐变盖染成金）；正文要平色就把两组件 Remove（米色底删双件，深底白字留 Outline 删 Gradient2）。
- **★加新图节点别复制 Bg，复制已清理过的 Badge/VS**（2026-06-11 实测）：复制 Bg 带的 RectTransformScaler 在编辑器 ExecuteAlways 下会**把整块布局搞乱**（症状：所有 TFWImage 消失、TFWText 还在，背景变默认灰），Ctrl+Z 可恢复。根因=带毒 Scaler 哪怕只是临时存在也会触发。规避=复制一个本来就没 Scaler 的干净图节点（队徽/VS）做新图节点的源。

- **type 29 进度礼包的 day 锁是纯客户端表现**：服务端建包 `day=PackList序号` 但购买路径不校验 day → 复用 29 挂多个"平行可买"礼包成立（世界杯竞猜两包互斥就是这么做的，互斥也是纯客户端查 purchaseNum）
- **AI 柔光/发光件太虚的秒级修法**：不重生成——PIL 对 alpha 跑 smoothstep 收紧（lo=50/hi=130/封顶215）+ 与目标色 6:4 混合校色，雾团→紧致羽化光带；**原地覆盖客户端 png（meta/guid 不动）= prefab 引用不断、Unity 焦点重导即生效**（2026-06-12 世界杯加送光带实证）。
- 新切图落仓可**手写 .meta**（抄现有 sprite meta 改 guid：textureType:8 + spriteBorder 九宫格初值=短边/3），Unity 打开即正确导入，实例见 `Spirits\ActvWorldCup\`（commit a92064dd 附带批量落仓脚本写法）
- 提交规范：feature branch + MR，commit 前缀 `X3NEW-`/`X3-{n}`
- **写拼 prefab 操作指南/核对节点路径前，先解析真实 prefab 结构别凭印象猜**：`python C:\ADHD_agent\scripts\unity_prefab_tree.py <prefab路径> [深度]` 直接打印节点树（2026-06-11 教训：指南假设模板 Top 区有底板图+DailyGift，实际只有 txt_title/Time/txt_desc/Info 四节点，用户照做必卡）

相关：[[project_x3_worldcup_activity]]（首个落地案）· [[reference_x3_client_resources]] · [[reference_x3_art_resource_spec]]
