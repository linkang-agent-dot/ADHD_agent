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

- **WndMgr 命名空间=`UI`**（文件在 TFWCore 但不是 TFW.UI）；`WndMgr.Show<T>` 按 Type 直连，UITypeAutoRegisterGen 静态字典只服务按 ID 跳转，新窗口不进注册表也能 Show（2026-07-10 皮肤专属时刻 demo 实证）
- **新增 .cs 离线编译检查（不打扰开着的 Editor）**：Unity 自带 Roslyn `Data\NetCoreRuntime\dotnet.exe Data\DotNetSdkRoslyn\csc.dll @rsp`，引用集=ScriptAssemblies\*.dll + Managed\UnityEngine\*.dll + UnityReferenceAssemblies\unity-4.8-api\*.dll+Facades；⚠️别加 netstandard/UnityEditor 伞形 dll（假错 CS0012/CS0433）。细节见 [[project-x3-skin-moment-interactive]]
- **Play Mode 中 Unity 挂起脚本重编译**：新脚本 .meta 生成了但菜单/类不出现 → 退 Play + Ctrl+R
- **★窗口 prefab 根必须带 Canvas（+框架组件），从零拼根节点必炸**：WndMgr.Show 实例化后要取根 Canvas 调层级，裸 RectTransform 根报 MissingComponent"add a Canvas"。程序化拼新窗口的正确姿势=**整体 Object.Instantiate 一个现有窗口 prefab（根组件全保留）→ 不要的模块 SetActive(false)（别删，根上动画/Feedbacks 可能引用）→ SaveAsPrefabAsset**（2026-07-10 皮肤专属时刻 demo 实证）
- **★编辑器工具/MenuItem 必须放 `Assets\GameMainLogicEditor\`**（GameMainLogic.Editor 程序集，引用了 GameMainLogic 热更程序集）；放裸 `Assets\Editor\` 引用 UI.* 必 CS0234（HybridCLR 热更程序集非自动引用）。编译错误诊断=grep `%LOCALAPPDATA%\Unity\Editor\Editor.log`

- **★遮罩颜色采样做点击热区（无碰撞体，配置驱动，2026-07 皮肤互动 demo 验证）**：想让一张图上不同区域触发不同逻辑又不想摆一堆碰撞体 → 用一张**颜色编码遮罩图**(红/绿/蓝各代表一个区)覆盖，加载后设 `alpha=0` 但保 `raycastTarget=true`(不可见只接点击)，点击时屏幕坐标→`RectTransformUtility.ScreenPointToLocalPointInRectangle`→归一化→`mMaskTex.GetPixel(x,y)` 判颜色定区域。骨架=女仆俱乐部 `UIHeroClub.Interact.cs SampleMaskPart`。⚠️**遮罩图必须放贴图后处理器白名单目录**(如 `Res/UI/Spirits/Club/images/mask/`,`CustomizeAssetPostprocessor.Texture.cs` 的 `MaskImageDir` 只对它保 `isReadable:1`)——其他 UI 目录导入时强制 `isReadable:0`(手写 meta 也被覆盖)→`GetPixel` 失效=点击没反应。要新目录得改后处理器加白名单
- **★运行时代码创建 UI 糊，给美术 prefab 规格更好（2026-07 皮肤互动 demo 实证）**：想快速验证逻辑可运行时 `new GameObject`+`Image` 拼 UI(不依赖 prefab/Auto 绑定,编译即用),但**效果糙**(圆形靠 Knob mask 出来是方卡片、位置乱)。正解=**逻辑代码写成「驱动 prefab 里拼好的模板」**：Auto 绑定容器+模板节点,代码 `Instantiate` 模板 N 份填数据/绑点击,美术在 Unity 里拼样式。给美术**明确的节点路径+命名规格+现成素材清单**(项目 `Res/UI/Spirits/Common` 有 Round_frame 金圆环/Round_di 圆底/Round_mask 裁圆遮罩/Round_light 高亮/common_lock_1 锁等,别 AI 生成风格不统一)。分工=逻辑我接、样式美术拼
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
