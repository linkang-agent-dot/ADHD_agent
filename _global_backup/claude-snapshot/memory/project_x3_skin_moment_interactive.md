---
name: project-x3-skin-moment-interactive
description: X3 新案子——皮肤专属时刻(Skin Moment)：皮肤互动视频功能(HUD入口+不透明满幅视频+点击部位触发对话/反应/音效)，骨架照抄女仆俱乐部(HeroClub)，含互动脚本首稿
metadata: 
  node_type: memory
  type: project
  originSessionId: 855ac3e3-eb49-49a3-8198-fa61c11eb474
---

X3 新案子（2026-07-10 立项，方案稿待过审）：**皮肤专属时刻（Skin Moment）**——给视频化皮肤加可互动的专属剧情视频。HUD 入口 → 不透明满幅场景视频（greet播一次→idle循环），点角色 头/手/身体 三热区触发 对话+反应视频+音效。**商业钩子=未拥有皮肤只能看挑逗版 reject 反应（带导购跳转），拥有全解锁。**

## 🚀 冷启动接管摘要（2026-07-13 最新·先读这段，下面段落是演进史）
**一句话**：足球宝贝104001 双场景互动 demo，代码全就绪编译过在 **`feature/skin-moment`**，只差用户手拼 prefab 圆选择器+实机验证。
- **分支/存档**：活跃分支 `feature/skin-moment`（切回马戏节=`git checkout circus-homeland-port`）；checkpoint `963e3e0`(旧结构)→`8105a32`(多场景重构+归位)；之后选择器/调试入口改动**未commit**(工作区)。视频走LFS，KB备份=`KB\产出-数值设计\X3_皮肤互动视频\demo\_assets\`
- **设计(定)**：双场景 `lockerroom`(免费默认解锁=钩子)/`field`(需拥有皮肤,未拥有看静态图预览+点角色弹ShowItemObtain获取弹窗)。一场景=一互动=一视频(点角色→act→回idle,砍了三部位/档位/greet/reject)。场景名「更衣室·耳语/球场·挑逗」
- **代码(编译过EXIT=0)**：`UI\SkinMoment\UISkinMoment.cs`(主逻辑:场景表Scenes[]/SwitchScene/OnMaskClick→PlayAct/ShowPreviewAsync/ShowUnlockObtain/对白/引导) + `UISkinMoment.Selector.cs`(圆选择器**驱动prefab模板**) + `Auto_UISkinMoment.cs`(绑定加 mGoSceneSelector/mGoSceneCircleTemplate) + `UISkinMomentEntry.cs`(两入口白名单) + `GameMainLogicEditor\SkinMomentDemo\SkinMomentDemoTool.cs`(菜单:1构建prefab/2打开正常态/3打开强制未拥有态验锁定)
- **素材已归位客户端**：视频 `Res\Video\SkinMomentVideo\SM_104001_{lockerroom|field}_{idle|act}.mp4`(4支<1MB) / 预览图 `Res\UI\Spirits\SkinMoment\SM_104001_{场景}_preview.png` / 遮罩 `Res\UI\Spirits\Club\images\mask\SM_104001_mask.png`(必须此白名单目录保isReadable)
- **⏳待用户**：拼prefab圆选择器(节点规格`Root/SceneSelector/SceneCircleTemplate/{Thumb,SelectFrame,Lock}`+组件包见下)→1构建→Play→菜单2/3验证。用户遗留问题「本地化位置不对」待其指具体文本
- **圆选择器组件切图包+效果图**(2026-07-13,项目现成真图别生成)：`demo\_assets\ui\components\`——★**圆框=`img_cm_bg_icon_touxiangkuang1.png`(CommonNew通用库圆形金边头像框,用户拍板走通用件,别用chat_frame_avatar)** / Common_WhiteImg_Circle.png(白圆=裁圆Mask或选中高亮染金) / lock_2.png(锁,用户认可)。UI效果图 `sm_ui_mockup.png` ✅已出(满屏视频+左上圆返回+右上对白气泡+底部中央一排2圆选择器[左更衣室金光环选中/右球场带锁]+金花纹底座;⚠️效果图圆偏大压腿,实拼往下贴底缩小)
- **★选择器节点规格(更新:加Label)**：`Root/SceneSelector/SceneCircleTemplate` 下挂 `Thumb`(圆Image+白圆Mask裁圆,填preview缩略)/`SelectFrame`(选中金光环)/`Lock`(lock_2锁,未解锁显)/**`Label`(TFWText场景名,圆下方,走本地化)**。圆框用通用件 img_cm_bg_icon_touxiangkuang1
- **★场景名走本地化(2026-07-13,用户要求"本地化缺了")**：`SceneDef.TxtKey` i18n键=`LC_skin_moment_scene_lockerroom`/`LC_skin_moment_scene_field`,`SceneDisplayName()` 用 `LocalizationMgr.Get(key)`(TFW.Localization命名空间)取,键缺失退回中文Name兜底(demo可读)。**正式版让本地化组补这2个LC键(18语言)**→自动多语言。选择器Label+调试标签都走 SceneDisplayName
- **后续正式化**：配置表HeroSkinMoment/多语言/StreamedAssets/弹窗队列屏蔽(打开期主城弹窗照弹)/iOS和谐闸门/走MR

### 🕳️ 关键坑（都已解决/已知，避免重踩）
- **别把没真跑的工具结果当真**(2026-07-13血泪)：我几轮把「Round_*圆素材」搜索、「🚀接管摘要」edit 当成功了实际没发生→关键事实(文件存在/路径/edit生效)必看真实 tool_result,凭印象=埋雷
- **PowerShell 嵌套`$_`冲突**：`$want|ForEach{...Where{$_.Name -eq "$_.png"}}` 内外`$_`撞车静默拷0个→外层用`foreach($n in $want)`命名变量
- **Read工具读client仓图报File does not exist(真图也报)**：拷到KB再Read；拷预览用ASCII目录名(中文子目录会坏)
- 编辑器工具必须放`Assets\GameMainLogicEditor\`(GameMainLogic.Editor程序集),裸Editor目录引用UI.*必CS0234
- 窗口prefab根必须带Canvas→整体克隆现有窗口再裁,别从零拼根
- 遮罩必须放Club/images/mask/白名单(后处理器只对它保isReadable),否则GetPixel失效点击没反应
- 离线编译检查:Unity自带Roslyn`Data\NetCoreRuntime\dotnet.exe Data\DotNetSdkRoslyn\csc.dll @rsp`(refs=ScriptAssemblies+Managed\UnityEngine+UnityReferenceAssemblies\unity-4.8-api\*+Facades;别加netstandard/UnityEditor伞形;rsp过滤.cs别用`UISkinMoment\.cs"$`会误伤Auto_)
- 视频生成假卡死(Gotcha15):worker等poller卡→SendMessage催它直接`call_grfal.py --check-task <id>`
- demo文件别裸奔untracked(切分支git stash -u会卷走);已commit保护

---
## 唯一入口（方案+互动脚本全文）
`C:\ADHD_agent\KB\产出-数值设计\X3_皮肤互动视频\X3_皮肤专属时刻_方案+互动脚本_20260710.html`
含：技术落地delta表 / 配置表 HeroSkinMoment 字段 / 足球宝贝「赛后加时」8支视频分镜+对白池+三层音效设计 / 待拍板4项。

## 🔑 女仆俱乐部(HeroClub)技术锚点（2026-07-10 实地核实 client 仓，别重挖）
- 内部代号 **HeroClub**，UI 在 `client\Assets\Scripts\UI\Club\`，服务端 `server\GameServer.Hotfix\PlayerMeta\HeroClub\`
- **最核心=`UIHeroClub.Interact.cs`**：①视频序列 greet(播一次)→onEnd→idle(循环)，token 代际防旧回调顶新视频 ②点击热区=**遮罩图颜色采样**（`SampleMaskPart` L142-185：红=头2/绿=身3/蓝=手1/黑=忽略），遮罩在 `Res/UI/Spirits/Club/images/mask/RoleF{英雄}_{皮肤}_mask.png`，加载后设全透明只留 raycastTarget ③对白=配置TID组`;`分隔随机取（PickTalk），延1s出气泡3s自关
- 视频播放：`RVideoPlayer.PlayEmbedVideo(root, VideoPlayerData)` → `UIVideoPlayer.cs`(AVPro双缓冲)。**透明判定=文件名 `EndsWith("sbs.mp4")`(UIVideoPlayer.cs:238)**；HeroClub 的 DoPlayEmbedVideo 写死 `m_IsTransparentVideo=true`+`m_PauseBgm=false`(idle循环别抢BGM)
- 视频目录 `Res\Video\HeroClubVideo\`，命名 `RoleF{英雄}_{皮肤}_{greet|idle|reject|touch_{hand|head|body}_{low|high}}_sbs.mp4`，**StreamedAssets+OnDemand 按需下载不占首包**
- 配置表 `HeroClubInteract`（proto 在 `Res\Config\Proto\`）：HeroCfgID+DressCfgID(0=原皮可回退) + 三部位×{UnlockLow/High, FavorLow/High, TalkLow/High} + TalkReject
- 音效=**全烧进视频音轨**，无独立 PlaySound；打击特效=`Win_FX_5_Maid.prefab` 粒子
- 入口链：UIMainBottomMenu(FunctionType.Character 解锁gate)→UIRole `mBtnBtnClub`(HeroGift红点)→`WndMgr.Show<UIHeroClub>`；服务端每日加好感上限 `InteractFavorDailyMax=3`

## 新功能 vs HeroClub 的三处 delta
1. **不透明视频**：文件名不带 `_sbs`、`m_IsTransparentVideo=false`，满幅 1080×1920（格式锚 egypt_sphinx.mp4）；省掉整条透明化流水，AI 直出
2. **HUD 入口**：推荐活动 HUD 走 ActvOnline 配置驱动（可上下线/分服）；界面=新窗口 UIHeroSkinMoment 标准4件套，prefab 抄 UIHeroClub 的 VideoRoot+Dialogue+Mask 三节点
3. **解锁轴=皮肤拥有**（非好感）：未拥有→reject 层（转化面做最勾人）+JumpID 跳礼包

## 脚本设计要点（尺度/风格定式）
- 尺度红线=**以已上线女仆俱乐部为上限**，全程双关+留白无露骨词；足球术语天然双关（加时赛/贴身盯防/犯规/金球制）
- 人设沿用皮肤视频已验证的"高冷带撩"（撩点=征服欲非谄媚）；音效三层=视频内嵌音轨(主)+UI点击音+高档心跳震动/vignette(P1)
- 过审保险：复用现成和谐视频闸门 `ResolveHarmonyVideo`（版本+创角时间双闸），iOS/新号屏蔽或换和谐版，成本≈0
- 热区不漂的前提=反应视频锁镜头锁站位（prompt 措辞抄 [[reference-x3-hero-skin-video-production]] §六）

## ✅Demo 已实跑验证（2026-07-11 Editor 实测：窗口打开/greet→idle/三热区采样/对白全通，真片 3/4 已换入）
- 遗留观察：demo 窗口打开期间**主城弹窗队列照常自弹**（海妖议价类定时弹窗，用户误以为点出来的）——正式版需在窗口打开期屏蔽弹窗队列（女仆俱乐部同款处理）；正式版待办还有：touch 头/手 6 支视频补生成、配置表化、HUD 入口、iOS 和谐闸门

## ⚠️2026-07-13 分支事故+恢复法（demo文件寄生在途分支的坑）
- **现象**：用户从 circus-homeland-port 切到 feature/circus-gacha，`git stash -u` 把 demo 全部 untracked 文件卷进 **stash@{0}**(`circus-homeland-port在途meta暂存_20260713`)，切后工作区 demo 文件全消失、两个改过的现有文件(UIActvCrafting.cs/UIHeroInfo.Skin.cs)回退成原始版
- **没丢**：demo 6代码+prefab+9视频+遮罩+2现有文件改动**完整在 stash@{0}**；视频/图 KB 另有备份(demo\_assets)
- **恢复法**：先 `git checkout circus-homeland-port`(stash 建在此分支，别在别的分支 pop 会污染) → `git stash pop 'stash@{0}'`。⚠️stash@{0} 混了一堆 mask meta/图集 Unity重导噪音，pop 回来会带上(无害但脏)
- **★根因**：demo 一直寄生马戏节分支 untracked=定时炸弹
- **✅已解决(2026-07-13)**：demo 已落独立分支 **`feature/skin-moment`**(从 circus-homeland-port HEAD 开)，stash pop 恢复无冲突，清掉 77 行 Unity meta 噪音(RoleF*_mask.png.meta+UIActvLaborGacha 图集，`git restore` 恢复仓库版)，做了 **checkpoint commit `963e3e0`**(本地未推远程，视频走 LFS)。demo 不再裸奔 untracked。**当前活跃分支=feature/skin-moment；切回马戏节=`git checkout circus-homeland-port`**

## 2026-07-13 视频归位完成（commit 8105a32，双场景素材就位）
- **4支干净场景视频**(每<1MB)：`SM_104001_{lockerroom|field}_{idle|act}.mp4`。更衣室=旧 idle+挑 touch_body_high 当 act(git mv 重命名)；球场=新生成 field idle/act(seadance,首尾差2.98无缝/act凑近飞吻很撩)
- **退役7支**(git rm)：greet/reject/touch_{head,hand}_{low,high}/touch_body_low(KB有备份)
- **2张preview静态图**落客户端 `Res/UI/Spirits/SkinMoment/SM_104001_{场景}_preview.png`(=各场景act首帧=场景首帧图 sm_104001_scene/field_scene，isReadable:0普通sprite)。固化脚本 place_preview.py 在 KB demo\_assets
- **两个checkpoint**：963e3e0(旧9视频结构) → 8105a32(多场景重构+归位)
- **只差**：①圆形场景选择器UI进 SkinMomentDemoTool 构建(视频下方一排圆,点切场景,未解锁显🔒)②重建prefab实机验证(两场景切换+球场锁定预览+点击弹解锁)

## 2026-07-13 多场景重构（代码，编译通过，feature/skin-moment）
UISkinMoment.cs 重构完成（编译 EXIT=0）：
- **场景表驱动**：`SceneDef[]{lockerroom(免费默认解锁,更衣室·耳语), field(需拥有皮肤,球场·挑逗)}`，每场景带 act 对白组。命名 `SM_{皮肤}_{场景}_{idle|act}.mp4`，preview=`SM_{皮肤}_{场景}_preview.png`
- **一场景一互动**：砍三部位×档位/reject/greet。`OnMaskClick`→点角色任意非黑热区(`IsHitRole`不再分部位)→`PlayAct`(播act+对白)→回idle。进界面直接 idle 无 greet
- **场景解锁+静态图预览**：`SwitchScene(i)`解锁→播idle+`mViewLocked=false`；未解锁→停视频+`ShowPreviewAsync`(运行时建 ScenePreview Image全屏+Dim 35%暗化层,raycastTarget=false 让下层遮罩接点击)+锁定对白+`mViewLocked=true`。锁定场景点角色→`ShowUnlockObtain`=`UIHelper.ShowItemObtain(skinCfg.ObtainItemID, KEEP_OPEN_PANEL_NEED_COUNT, buySuccessAction:刷新)`
- **切场景**：调试按钮`OnBtnTierTrigger`复用为循环切场景；圆形选择器 UI 待加。预览层运行时创建(不改prefab/Auto绑定)保证编译稳
- **待做**(视频回来一次做)：①球场idle/act审压归位 SM_104001_field_{idle|act} ②更衣室现有视频归位 SM_104001_lockerroom_{idle|act}(留idle+挑body_high当act) ③2张preview归位(=act首帧,已有场景图 sm_104001_scene/field_scene) ④圆形选择器进prefab ⑤实机验证
- 球场首帧图已确认OK(sm_104001_field_scene.png)；球场 idle/act 视频生成中(假卡死已唤醒worker查)

## 2026-07-13 落地范围拍板（缩到单皮肤双场景，高级皮肤分层暂缓）
- **高级皮肤分层先不做**；就足球宝贝 104001 一个皮肤做**两个场景**：
  - **更衣室 = 默认解锁**（免费体验钩子，未拥有皮肤也能玩，先钓上瘾）= 现有这套 → 归入 `lockerroom` 场景
  - **球场 = 获取皮肤后解锁**（未拥有看静态图预览+解锁引导，买皮肤后可玩）→ 新出 `field` 场景
- **球场视频要出**：idle+act 两支，时长/撩度**参考更衣室**(5s不拉长)。首帧图生成中(task f452, sm_104001_field_scene.png，gpt换背景保人物身份，ref=更衣室首帧)→出图后审→seadance生成 idle(fflf循环)+act(首帧驱动,参考更衣室凑近耳语的撩法换个球场动作)→压缩换入 SM_104001_field_{idle|act}.mp4 + preview
- 转化设计=**免费一个场景钓上瘾 + 第二个场景卡购买**，比"全部要买"钩子强
- 命名正式引入场景段：现有 SM_104001_{idle|act} → 迁 SM_104001_lockerroom_{idle|act}；球场 SM_104001_field_{idle|act}

## 2026-07-13 需求演进（产品设计，聊定的方向；梳理HTML=唯一入口）
唯一入口文档：`KB\产出-数值设计\X3_皮肤互动视频\X3_皮肤互动_需求梳理与现状_20260713.html`
- **商业结构（定）**：本体互动=随皮肤解锁(驱首购)；换装本质=皮肤SKU(驱复购)；互动分**基础/高级两档**——基础皮肤(节日标配)=单场景直接玩；高级皮肤=多场景(每场景互动不同)，未拥有只看**静态图**，解锁皮肤才有视频+互动
- **★简化(定)：一场景=一互动=一视频**，砍掉三部位×低高档(玩家感知不到，产能翻3倍浪费)。每场景仅 2 支核心：`idle`待机循环 + `act`点击互动。reject 也砍(静态图预览接管转化)
- **★命名规范(定)**：`SM_{皮肤ID}_{场景}_{idle|act|preview}`，场景用英文语义词(lockerroom/field)。preview.png=act首帧(白捡静态预览图)
- **圆形场景选择器(设计中)**：互动界面视频下方一排圆形按钮(原英雄详情底部tab位思路)，圆内=场景preview裁圆，默认选中皮肤默认场景，未解锁场景显🔒→点它弹静态图+解锁引导(不播视频)
- **静态图预览UI(设计定)**：场景静态图(preview=act最撩首帧)+**轻暗化**(还要看清人才勾得动)+🔒+文案「解锁皮肤即可体验完整互动」(用户确认OK)+解锁按钮。命名场景=「场景·动作」范式(地点给画面+动作给情绪，含蓄擦边好过审)，默认场景推荐「更衣室·耳语」lockerroom_whisper / 高级「球场·挑逗」field_tease
- **★解锁按钮=通用获取途径弹窗(逻辑已核实)**：调 `UIHelper.ShowItemObtain(皮肤ObtainItemID, ItemObtainConst.KEEP_OPEN_PANEL_NEED_COUNT, buySuccessAction: 刷新解锁)`(`UIHelper.ItemObtain.cs:46`)。**途径完全由配置表驱动**——读该道具 `CItem.ObtainID`(获取途径列表,可开箱/礼包/兑换多种)自动弹通用「获取途径」界面，不写死跳哪；运营在皮肤道具 ObtainID 配啥就显示啥。皮肤页「获取」按钮(`UIHeroInfo.Skin.cs OnBtnSkinGetTrigger`)走的就是这套，直接复用行为一致，买成功回调刷新解锁
- **现有9支归置**：留 idle + 选 touch_body_high 当 act，其余7支(三部位低高档+reject+greet)**退役**；更衣室即成简化版一个完整场景，不用重做
- **技术省成本锚**：静态图=首帧白捡；换场景=换背景AI白送；代码 SM_{皮肤}_{slot}→SM_{皮肤}_{场景}_{slot} 扩展小
- **仍待用户定**：①高级皮肤场景数(建议2-3) ②基础vs高级落差/基础互动深度 ③默认场景名(更衣室 vs 赛后加时) ④greet进场去留(倾向砍) ⑤act时长(5s→8-10s?) ⑥圆形选择器只在互动界面内 vs 也进皮肤页

## 2026-07-11 收尾：9支真片全齐 + 首次进入引导
- **视频全齐**：greet/idle/reject + touch_{head,hand,body}_{low,high} 共 9 支 seadance 真片，全走工程 compress_video.py 压缩（每支 <1MB，合计~4MB）。剩余生成任务的假卡死都靠 SendMessage 唤醒 worker --check-task 收尾（Gotcha15）
- **首次进入引导**（`UISkinMoment` ShowGuideBubble/EndGuide）：首次打开显示常驻引导气泡「点我的头、手或身体，会有专属回应哦~」（复用对白气泡节点，不走 3s 自动关），首次点击角色即关引导+触发互动+`GamePlayerPrefs.SetByRole(GuideKey,true)` 记住；GuideKey 按皮肤（换皮肤重引导一次）。GamePlayerPrefs 全局命名空间直接用
- **环境**：用户 Editor 连 **beta**（trick.json env_name=beta, client_version=0.9.999 过版本闸）

## 2026-07-11 去 demo 化（客户端务实正式版，纯展示无服务端，编译通过）
- **档位=真实判定**：`UISkinMoment.DoInteract` mTier=TierAuto 时按 `IsOwnedSkin()`（=`GetCanUseHeroSkin(skinCfg.Group).Contains(skinID)`，Group=本体英雄cfgID）分档：拥有→high 全解锁 / 未拥有→reject 导购。首版不接好感，low 档视频留给后续接 HeroClub 好感。编辑器切档按钮降级为 debug override（循环 Auto→未拥有→低→高）
- **入口白名单 gate**（`UISkinMomentEntry`）：`SupportedSkins={104001}`（正式版查 HeroSkinMoment 表有无行）+ `SupportedCraftingActv={101516世界杯开箱}`；皮肤页只对选中的支持皮肤显示、切走则 Remove；开箱只对 101516 显示。Attach 每次重建以更新目标皮肤（闭包捕获 skinCfgID）
- **多皮肤就绪**：SlotPath 用实例 mSkinCfgID（=Data.skinCfgID）不再写死 DemoSkinID
- **★剩余正式化清单（未做，待拍板深度/提交时机）**：①配置表 HeroSkinMoment（proto+导表）替代硬编码对白/白名单 ②对白多语言（现 cn 硬编码，走 x3-translation-automatic）③视频目录 StreamedAssets+OnDemand（现随包，补 HeroClub 冷路径 ExtractAsync）④弹窗队列屏蔽（打开期）⑤iOS 和谐闸门复用 ⑥入口按钮进 prefab（现代码动态挂）⑦是否接好感/服务端 ⑧prefab 从 SkinMomentDemoTool 生成物固化进仓 ⑨提交=单独 feature/skin-moment 分支+X3NEW 单+MR（勿混进 circus-homeland-port）

## 2026-07-11 增量：两个入口 + 视频压缩定版
- **入口×2 已加（现有文件仅 +2 行调用，其余新文件）**：①英雄详情皮肤页（`UIHeroInfo.SkinMoment.cs`，钩子=RefreshSelectHeroSkinView，按钮挂 mGoHeroSkin 随视图显隐，克隆 mBtnSkinChoose 样式放立绘右上）②世界杯开箱界面（`UIActvCrafting.SkinMoment.cs`，钩子=OnShown）。共享助手 `UISkinMomentEntry.cs`（克隆宿主按钮动态挂，幂等，点击 Show UISkinMoment）。demo 常显，正式版按皮肤/活动配置过滤
- **★世界杯开箱界面 = `UIActvCrafting`**（ActvType15=TRIGGER_TYPE_CRAFTING"制作活动"，运营叫开箱/福箱，BoxSlotItem 开箱）
- **★落 client 仓的视频压缩定版（用户拍板）**：一律用工程指定工具 `client\Tools\VideoTools\compress_video.py -i <file> --no-backup`（H.264/crf28/slower/**高度上限1080→竖版缩到608×1080**/AAC64k，对齐 .githooks/video_policy.json，压完过 pre-commit 钩子）；GRFal video_compression 只用于 KB 侧展示片迭代，**不用于落库**。3 支真片压后 0.25-0.76MB/支
- reject v2 生成任务假卡死（Gotcha15），已 SendMessage 唤醒 worker 直查收尾

## Demo 落地明细（2026-07-10）
**全部新增文件、零改现有代码**，在 client 仓 `circus-homeland-port` 分支工作区（未提交，不干扰在途工作）：
- `Assets\Scripts\UI\SkinMoment\UISkinMoment.cs`（业务类：greet→idle→touch 序列/遮罩采样/对白/档位切换按钮 demo 用）
- `Assets\Scripts\UI\Gen\Auto_UISkinMoment.cs`（手写绑定，Identifier=1720260710）
- `Assets\Editor\SkinMomentDemo\SkinMomentDemoTool.cs`（菜单 Tools/SkinMomentDemo：1-从 UIHeroClub.prefab 克隆构建 UISkinMoment.prefab；2-PlayMode 开窗）
- `Assets\Res\Video\SkinMomentVideo\SM_104001_{greet|idle|reject|touch_{part}_{low|high}}.mp4` ×9（先占位=借现有视频，AI 真片出来同名覆盖零代码改动）
- `Assets\Res\UI\Spirits\SkinMoment\SM_104001_mask.png`（热区遮罩，画法脚本 gen_sm_mask.py 在 KB demo\_assets）
- AI 资产：首帧场景图 `KB\产出-数值设计\X3_皮肤互动视频\demo\_assets\sm_104001_scene.png`（gpt改图保身份，黄昏更衣室，效果好）；4 支 seedance 视频（greet/idle循环fflf/touch_body_high/reject）经 x3-media worker 生成
- 运行法：退 PlayMode 等编译 → Tools/SkinMomentDemo/1-构建Prefab → PlayMode 登录主城 → 2-打开Demo窗口

## 🔑 本案踩坑沉淀（客户端 demo 开发通用）
- **WndMgr 命名空间=`UI` 不是 TFW.UI**（文件在 TFWCore 但 namespace UI）；`WndMgr.Show<T>` 按 Type 直连，**UITypeAutoRegisterGen 静态字典只服务按 ID 跳转（OpenPanelTab），新窗口不注册也能 Show**
- **离线编译检查法（不开/不打扰 Unity 验新 .cs）**：`<Unity>\Editor\Data\NetCoreRuntime\dotnet.exe <Unity>\Editor\Data\DotNetSdkRoslyn\csc.dll @rsp`，引用集=`Library\ScriptAssemblies\*.dll` + `Data\Managed\UnityEngine\*.dll` + `Data\UnityReferenceAssemblies\unity-4.8-api\*.dll`+`\Facades\*.dll`。⚠️别加 netstandard.dll（工程是 .NET4.8 profile 缺 mscorlib 会喷 CS0012/CS1983 假错）、别加 UnityEditor.dll 伞形（与 CoreModule 冲突 CS0433）
- **Play Mode 中 Unity 挂起脚本重编译**：新增脚本 .meta 已生成但菜单/类不出现 → 退 Play Mode + Ctrl+R 等编译
- **★X3 编辑器工具必须放 `Assets\GameMainLogicEditor\`（GameMainLogic.Editor 程序集），不能放裸 `Assets\Editor\`**：HybridCLR 架构下 Assets\Scripts=GameMainLogic 热更程序集（非自动引用），裸 Editor 目录归默认程序集看不到它 → 引用 UI.* 的编辑器脚本必 CS0234。诊断法=grep `%LOCALAPPDATA%\Unity\Editor\Editor.log` 搜文件名看编译错误（不用等用户截 Console）
- **★遮罩必须放 `Res/UI/Spirits/Club/images/mask/` 白名单目录**：`CustomizeAssetPostprocessor.Texture.cs` 的 `MaskImageDir` 只对该目录保留 isReadable，其他 UI 目录导入时**强制改回 isReadable:0**（手写 meta 也会被覆盖）→ GetPixel 采样失效=点击没反应。正式版要自建目录得改后处理器加白名单。手写 meta 抄 HeroClub 模板换 guid 仍是对的，但目录必须在白名单内（gen_sm_mask.py 待更新输出路径）
- **道具漂移穿帮（新变体）**：seedance 里"举起球"动作会把足球**变形成橄榄球**（不只是消失/被挡）。治法=prompt 加 CRITICAL PROP RULE 锁「球=圆形黑白六边形足球、每一帧保持、NEVER morph into american football」——凡道具被"操作"（举/抛/转）的段落都要锁形状
- **满幅场景片运动量阈值失真**：静止背景稀释帧间均值，透明立绘片的"<3.5=木头"线不适用（idle 实测 1.04 但角色呼吸感正常）——满幅片判活靠看帧，不靠均值；审片脚本 `check_videos.py` 在 KB demo\_assets（抽首中尾帧+首尾差+运动量一条龙）

## 关联
[[project-x3-hero-skin-video]]（皮肤视频化基建）· [[reference-x3-hero-skin-video-production]]（生产pipeline，seedance首选/kling嘴崩）
