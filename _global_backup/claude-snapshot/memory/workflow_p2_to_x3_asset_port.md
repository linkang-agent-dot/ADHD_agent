---
name: workflow-p2-to-x3-asset-port
description: P2/X2→X3 Unity 3D 资产跨项目搬运手法（原GUID保链+材质重写+骨架克隆嵌套实例+DK双注册），搬家具/主城皮肤/装饰模型时套用
metadata: 
  node_type: memory
  type: reference
  originSessionId: 42ce653e-2e7b-416e-a7f6-25cb4ac83e33
  modified: 2026-07-31T09:57:56.788Z
---

# P2→X3 Unity 3D 资产搬运手法（2026-07-10 马戏节主城皮肤实战沉淀）

首例：P2 `anniversary2024` Lv2（马戏团旋转木马）→ X3 `Homeland_Circus` 岛屿皮肤，纯命令行零 Unity 操作，commit `5c503fe26bf` @ x3-project dev_festival。X3 已拍板家具=♻️直接搬 P2/X2 模型，此法通用。

## 核心原则：P2 资产带原 GUID 整套搬，内部引用链自持
prefab→fbx mesh→材质→贴图 的引用全靠 GUID+fileID；**连 .meta 一起原样拷贝（GUID 不改），引用自动成立**。fileID 映射在 fbx.meta 的 internalIDToNameTable 里，跟着 meta 走。GUID 碰撞概率可忽略（跨项目随机 128bit，非共享库资产）。

## ⚠️ 头号坑：P2 节点残留 Layer 会被 X3 相机剔除（实锤踩过）
P2 建筑 prefab 大量节点 `m_Layer: 19`（P2 的建筑层）；X3 里 19=**Entrance**，大地图相机不渲 → 模型摆进场景**完全隐形**（gizmo 在、模型无）。**搬运时必须把源项目 Layer 全刷成 0**（`sed s/m_Layer: 19/m_Layer: 0/g`，X3 岛屿皮肤惯例=全 Layer 0）。跨项目 Layer 语义不通用，凡搬 prefab 先 `grep -o "m_Layer: [0-9]*" | sort | uniq -c` 对照目标项目 TagManager.asset。修复 commit：48a8ff4e85b。

## 搬运清单怎么列全（别漏共享引用）
对源 prefab `grep -oE 'guid: [0-9a-f]{32}'` 去重，逐个归类：
- fbx / 材质 / AnimatorController → 必搬
- **共享 .anim**（P2 常引用 CityHall/Common/Animations 下的公共剪辑）→ 必搬，用 guid 反查 .anim.meta 定位
- 嵌套 PrefabInstance（如 P2 UpgradeIcon 升级角标）→ **剥离**：删 `--- !u!1001` 块 + 对应 `stripped` Transform 块 + 父节点 m_Children 里那行；删完 grep 源 guid 必须=0
- P2 脚本 MonoBehaviour（LOD渐隐/EffectReference 等）→ 不搬不剥，X3 里 missing script 无害
- 脚本的 ScriptableObject 配置（fadingConfig 等）→ 跟脚本一起弃

## 材质：内容换 X3、GUID 留 P2
P2 shader X3 没有（P2 自定义 Diffuse×Light，X3 URP homeland shader 只吃 `_MainTex`）。做法：**拷 X3 同类 .mat 全文**，替换其中贴图 guid → 我的烘焙图 guid、m_Name；**.mat.meta 用 P2 原 meta**（保 GUID，prefab 引用不断）。
- 贴图：P2 的 Light_High 是暗底夜灯发光图不是乘法光照图——烘焙直接用 Diffuse 转 PNG（2048→1024 足够）；png.meta 拷 X3 同类贴图 meta 换新 guid。

## 外壳：克隆 X3 骨架 prefab + 嵌套实例
X3 系统 prefab（如 Homeland_*）有固定结构（根碰撞体/uiMountPoint/SelectPoint/EffectRoot挂特效脚本/水波mesh/容器节点55°X旋转+1.3缩放）——**整文件克隆，只把模型子节点换成 P2 prefab 的 PrefabInstance**：
1. 删原模型子节点 4 块（GameObject/Transform/MeshFilter/MeshRenderer），水波等保留（跨文件夹引用原资产没问题）
2. 容器 m_Children 里原 Transform id 原位替换为 stripped id
3. 文件尾追加 `--- !u!1001 &<instId>` PrefabInstance（m_TransformParent=容器 Transform；m_Modifications 对源 prefab **根 Transform fileID**（=源文件里 `m_Father: {fileID: 0}` 那个）打 pos/rot/scale/RootOrder/EulerHint 修改；m_SourcePrefab=P2 prefab guid）+ `--- !u!4 &<stripId> stripped` Transform 块。格式直接抄任一现成 PrefabInstance 块（serializedVersion 2/3，Unity 2022 通用）
4. 新 prefab 自身 .meta 用新 guid；文件内 fileID 是文件内命名空间，克隆不用改

## ⚠️ 二号坑：X3 岛屿骨架容器自带 55°X 前倾，直立模型要反打 -55° 补偿
Homeland 骨架的模型容器节点烘了 `rot X=55°`（X3 岛 FBX 是按此预倾角制作的所以显示正常）；P2/X2 正常直立建模的建筑挂进去会**向前躺 55°**。修=嵌套实例 modifications 加 `m_LocalRotation x=-0.46174863 w=0.8870109`（euler -55,0,0）+ EulerHint.x=-55。commit 13605e592e2。微调朝向/大小在嵌套节点上做，别动 Clone 根（会连水波一起转）。

## 缩放定标
Blender 无头 probe 两边 FBX 包围盒（skills\blender-fbx-render\probe_bounds.py）。坑：源 prefab 根可能自带缩放（P2 建筑根=0.1 是 P2 世界尺度），嵌套实例的 modifications 直接覆盖根缩放——按「目标容器空间想要几个单位 ÷ FBX 原始包围盒」算（马戏案：X3 岛≈4.6~6 单位，P2 fbx≈5.5 → scale 0.9，y=-2.06 对齐水波面）。进 Unity 后可视调。

## ⚠️ 切分支/换资源时用户 Unity 开着 = 三连幽灵症状（都不是仓库坏了）
07-10 实战一天内全遇到，特征=磁盘/git 层全部自洽但编辑器报异常：
1. **幽灵编译错**（如 `HotFixLogicMain.cs(229) CS0234`）：报错文件是 **.gitignore 的本地生成文件**（`client/Assets/Scripts/HotFixLogicMain.cs`=热更入口注册,分支树上没有）或编译到了 checkout 中间态。判别=报错行号内容与磁盘对不上+全仓 grep 类名零命中。修=重启 Unity；顽固则删 `client\Library\ScriptAssemblies`。
2. **白模**：换贴图瞬间被导入缓存吃到中间态（见下）。
3. **UGit 面板仓库消失**：UGit 是 Unity 编辑器插件，编译失败/Safe Mode 时插件不加载 → 用户以为"仓库没了"。git fsck/branch/stash 摆证据安抚，重启 Unity 恢复。
预防：**给用户动 client 仓（切分支/换二进制）前，先让对方退出 Play、最好关 Unity**。

## ⚠️ 三号坑：P2 shader 全家不可搬 + 贴图必选 Low 档（2026-07-13 实锤）
P2 建筑资源分 **High/Low 双档**（High=PBR 三贴图 `3D_PBR_Building_New`；Low=unlit 双贴图 `3D_Unlit_Building`+烘焙阴影片）。两个关键结论：
1. **P2 shader（High/Low/Shadow 全部）依赖全局日夜 uniform**（`_GlobalDayNightColor`/`_ToneMappingMin/Max` 等，经 `DayNightSystemShaderHelper.hlsl`）。~~X3 没人喂值必黑~~**（07-13 纠偏）X3 同为 TFW 引擎系，自带同名 helper（`client/Assets/Res/Shader/Include/DayNightSystemShaderHelper.hlsl`）且运行时在喂**（X3 自家 FX_AddBlend_Particle 等 shader 线上就在乘这些全局）——P2 shader 可搬，两种姿势：①include 改指 X3 的 helper ②把日夜/ToneMapping 行全注释（客户端同事 07-13 实测法，commit 1a2f25cb7fa）。图省事仍可用 X3 `X3_World_City.shader`（guid 0e3b6aad...，unlit `_MainTex*_Color`）+烘焙图。坑：P2 include 路径带 `Assets/P2/` 前缀，X3 没有，原样搬必编译错。
2. **diffuse 必须用 Low 档**：High 档 diffuse 是给 PBR 管线的原始 albedo（平、艳，unlit 下没质感）；Low 档 diffuse 光影/AO 全烘进颜色（两图 87% 像素不同、分辨率相同 2048）——配 X3 unlit shader 正好是 P2 低端机在游戏里的最终画面。马戏案修正 commit `43b1f96db15`。
3. 阴影片不搬：X3 原生岛=岛体+水波两件套、无阴影片惯例，且其 shader 同样依赖全局 uniform。

## ⚠️ 四号坑：特效走 assetPath 字符串动态加载 = guid 扫描盲区（2026-07-13 同事验收抓漏）
P2 建筑皮肤的特效**不在 prefab 依赖树里**：prefab 上 10+ 个挂点 MonoBehaviour 用 `assetPath: Assets/P2/Res/Effect/Prefab/.../Fx_*.prefab` 字符串运行时加载——`grep guid` 列搬运清单**永远扫不到**。凡搬 P2/X2 建筑类 prefab，必须额外 `grep assetPath:` 一遍。特效搬运手法（马戏案 commit df53c2e567d，81 资产）：
- 特效真身可能不在 assetPath 写的路径（写 Scene/ 实际在 Prefab/CityBuilding/<主题>/Common/），按文件名 find 定位；依赖树三层：fx prefab→材质(30个全用同一个 P2 万用特效 shader `FX_AddBlend_DistortionDissolve_Flow_New`，**自包含零全局依赖可直搬**)→贴图(公共库 `Res/Effect/Textures/{glow,mask,trail,...}`)；有材质藏 MiniGames 目录（rg 全仓 alternation 一把解）。
- X3 侧不用 P2 加载脚本：**挂点节点跟 prefab 一起搬过来了**（同名空节点），直接在搬过来的 prefab 里给每个挂点追加嵌套 PrefabInstance（m_Children 加 stripped id + 文件尾 1001 块，pos/rot 归零即可，scale 不写=继承源值）静挂常驻。
- 粒子 `scalingMode: 0`(Hierarchy) 会跟父级缩放走，模型整体缩放不用管粒子；fx prefab 同样有 Layer19 残留要刷 0；纯粒子无脚本可整搬。
- 脚本范式 `scratchpad/build_fx_port.py`（2026-07-13 会话）。

## 姿态/精度排查两法（实战沉淀）
- **贴图糊**：先查两处——烘焙 PNG 有没有被降采样（别自作聪明降 2048→1024，主城视角建筑满屏，直接用源图全分辨率）+ png.meta `maxTextureSize`/平台 override 上限。纯换 PNG 内容（同 guid/meta）零配置改动。
- **突然白模（之前有色）**：九成是换贴图时用户 Unity 开着，导入缓存吃到中间态文件（rebase/LFS 过程的瞬时指针）。判别=磁盘 `head -c 80` 看 PNG 真伪（真文件则非仓库问题）→ 让用户看 Project 缩略图 → 右键 Reimport（png+整个文件夹）。教训：**换二进制资源前提醒用户退出 Play/最好关焦点**，换完让对方 Reimport。
- **部件悬空/姿态不对**：用 Blender 渲 FBX 的**基准姿态图**（bind pose + 动画首尾帧各一张）当 ground truth，跟游戏内截图对照——能立刻区分「动画没播」vs「prefab 节点位置偏」vs「本来就这样」。脚本范式 `skills\blender-fbx-render\render_anniv_lv2.py`（按名字过滤只留目标档位 mesh）。修复姿势=让用户 Scene 里点击悬空部件定位节点→手拖到位→报节点名+数值→烘回 prefab。

## DK 双注册 + 收尾
- Display_Model.asset 末尾追加（key 无 DK_ 前缀 + type: Model + guid=新 prefab guid + exportCode: 0）+ Path_Model.asset 同锚平行插（键序=OrdinalIgnoreCase；校验 keys[i]==values[i].key + sorted）——铁律见 [[reference_x3_client_resources]]
- LFS 自动接管（png/fbx 落仓即变指针，正常 add/push 即可）
- 文件夹要配 folderAsset .meta；⚠️ `os.path.join(dir,'')+'​.meta'` 会把 meta 写进文件夹里，模板见 build 脚本
- 工作区：x3-project 用 **sparse worktree**（`git worktree add --no-checkout` + `sparse-checkout set` 只拉 Homeland+DisplayKey），不动主工作树别人的在途改动；push `HEAD:dev_festival`
- **主工作树提交注意**：x3-project 主树 commit-msg 钩子要求 `X3NEW-` 前缀（sparse worktree 里没触发过）；用户 Unity 开着时工作区会持续冒 meta churn，rebase 用 `git pull --rebase --autostash` 一把过
- **搬完客户端还剩两步**：①配置接线 Skin__Skin(SkinType=1) DK_Prefab=新 DK + Item_81xxx（gdconfig）②Unity 里 Ctrl+R 刷新 + Ctrl+T 先 LoadFromDisk 再 Save；真机/dev 服要等 AB 重建
- **不配表先在游戏里看（Play 内摆模型评审法）**：运行时主城岛节点 = Hierarchy `UnitRoot > City > North:<等级>:<uid>`，其 `GameObject` 子节点=岛模型容器（uiMountPoint/SelectPoint/EffectRoot 为兄弟）。评审四步：拖新 prefab 到 `City` 下 → 对原节点 Transform **Copy Component→Paste Component Values** 对位 → 取消勾选原 `GameObject` 子节点隐藏旧岛 → 调嵌套节点 scale/y。⚠️Play 内改动退出即丢，调好的数值要手记后回填 prefab 提交。

## 🔑 X3 原生岛屿皮肤=2.5D 平面卡片，搬真 3D 模型必缺岛座（2026-07-13 实锤）
所有原生 Homeland_*（1~4/周年/儿童节/塞壬等）的"mesh"都是**厚度 0 的剪影面片**（homeland_1 仅 52 顶点，Z extent=0），整张岛+岛座+建筑画在贴图上，靠容器 55° 倾角朝向相机——**岛座是画出来的，不是建模的**。P2/X2 搬来的真 3D 模型混进卡片堆里就会"漂在海上没底座"。
**原生解法=补一张岛座卡片**：①贴图=AI 生成"空岛座"（岩石托盘+顶部平坦无建筑，绿幕→removebg→verify）②材质=克隆 `Homeland_1/Material/homeland_1.mat`（shader `X3_World_City`：无光照透明混合 SrcAlpha/OneMinusSrcAlpha、**Cull Off 双面**、队列 3006，只吃 _MainTex）——Cull Off 意味着 **Unity 内置 Quad 朝向随便摆不用管** ③prefab 容器下直挂 Quad 节点（fileID 10210/guid 0000...e000...）identity 旋转（卡片约定=容器 XY 平面），垫在模型脚下（马戏案初值 scale 5.8 / y -2.8，模型底 y=-2.06）。透明排序自动正确：3D 模型不透明先写深度，卡片 3006 后画被正确遮挡；水波 3005 在卡片之下。
探 FBX 几何不用下 Blender：skill 目录自带 `FBX2glTF.exe` 转 glTF 读 accessors 即可（顶点数/包围盒/UV）。
⚠️ 绿幕 removebg 的图 alpha=0 像素 RGB 仍是绿色，双线性采样会渗绿边——落盘前做**边缘色外扩**（alpha 加权模糊迭代填充透明区 RGB，PIL 十几行，见 2026-07-13 会话）再进 Unity；verify_transparency 查不出这个（它只看 alpha）。

脚本范式：`scratchpad/build_port.py`（本次会话，含全部 YAML 手术+校验断言）；worktree 在 `C:\x3\client-circus`（分支 circus-homeland-port）。岛座卡片版脚本=`build_base_card.py`（2026-07-13 会话 scratchpad，同款断言风格）。

## 🛠 X2 侧有现成「一键导依赖」工具：Tools▸X2▸Prefab Asset Export（2026-07-07 zhangli 造，别再手工扒图）
搬 X2 界面进 X3 不用手工找几百张散图：x2client `Assets/Editor/PrefabAssetExport/`（commit 9990489d3991 + defd018b702d 补 shader）。
给一个 prefab → 按 Images(Sprite)/Textures(非Sprite)/Animations/Materials/Shaders/Prefabs 分目录拷出**连 .meta**（GUID 不变→丢进 X3 引用自动成立，实证 `Activity_bg_GachaMachineA.png` guid e24ba7a9… X2/X3 两侧一致），
外加 `_manifest.txt`（每个资源的 X2 原始路径 → 一眼分「活动专属图 vs X3 已有通用件」，扭蛋机案 64 张只留 21）+ `localization_keys.tsv`（仅 `^lc_` Key×17语，从 `P2/Config/Gen/i18n/<lang>.bytes` 读；**跟 X3 的 TXT_ 体系不通用，只当译文参考**）。
Unpack Completely **只在断链路线要做**（见下方「路A 内部两条线」，别无脑当铁律）；走它时验证 = manifest `[Prefabs 0]`。输出子目录名 = prefab 文件名，所以**要改名的先改再导**。
不导的：脚本/字体/音效/SO（分类表没这些后缀，静默跳过）；prefab 里 X2 脚本 GUID 到 X3 全是 Missing Script（扭蛋机案 466 处/32 个 guid），按 X3 `Auto_` 重挂。
**X3 侧配套的去重清理工具＝Tools▸Prefab换皮**（窗口「换皮无忧」，`x3-project\client\Assets\Editor\HuanPiWuYou\`）：给根 prefab + 资源目录，①删目录内 prefab 未引用的文件 ②同 GUID / 同名+同 MD5 的重复项（shader 只比名不比内容）把引用改成**工程原件**GUID 再删副本（保留判据＝优先目录外那份）。
🪤四个坑：①「推断」只认 `Assets/Res/UI/<prefab名>`，包放别处要右键 Copy Path 手粘 ②**必须先点「预览」再执行**（dry-run 出 REPLACE/DELETE 清单；确认框自己都提示"建议先 Git 提交"）③全工程扫 .meta + 逐文件名递归找同名，X3 体量下**分钟级卡住是正常的**（录屏 165s 结束时还在跑）④只改根 prefab + 资源目录内的引用，**目录外别的 prefab/场景引用同一副本会被删断链**；`_manifest.txt` 有硬编码保护、`localization_keys.tsv` 没有会被当未引用删掉。
执行完报告尾部 `断链 GUID` **必须=0**。⚠️ 此工具**没登记进** `x3-project\AIDocs\X2_to_X3_Migration\13_Migration_Tools.md`（那份只列 6 个 `Tools▸X2 Migration/` 工具：道具框/头像/联盟旗/RTL清理/多语言回填/描边红点），交接要专门交代。
**⚖️ 导出有两条路，盲区互补，别二选一（2026-07-30 两个真实包实测）**：路A=Editor `Tools▸X2▸Prefab Asset Export`，路B=`skills\unity-prefab-tools\prefab_dependency_bundler.py`。
路A 赢在：Unity `GetDependencies` **权威无 UNRESOLVED** / 按 TextureImporter 分 Sprite→Images·非Sprite→Textures（**语义正确**，特效贴图不混进 UI 图）/ 单出 Materials+Shaders / **出 `localization_keys.tsv`（lc_ Key×17语全文案）**。
路B 赢在：**`Other/` 兜底接住字体/`.asset`**（路A 分类表只认 图/anim/prefab/mat/shader，`.ttf`/FontAsset **静默丢**）/ 一次吃多个 prefab（共享资源只 1 份，路A 一次一个跑 N 遍会重复 N 份）/ 保留嵌套 prefab 结构 / 不用开 Unity。
**🎯 路A vs 路B 的差距已量化（2026-07-31 限时抢购 4 包实测，逐件 diff）**：同一批 prefab，路A 算出 52 个必拷件，上次走路B 只搬到 36 个，**漏 19 个＝9 Textures + 7 Materials + 1 Shader + 2 anim**，全在 **Shader→Material→Texture 三层特效链**上（一层不落地整条断 ⇒ 界面外显组件报错）。根因＝路B 正则扫 `guid:` **看不见 `.mat`/`.shader` 内部引用**（它产出的 52 个 UNRESOLVED 正是这批），Unity `GetDependencies` 看得见。⚠️ **结论：外显翻车怪"AI 全自动"是错的，怪工具选错**——同一个 AI 拿路A 的包搬就不漏。路B 还会**多搬公共件 prefab**（断链路线已内联，属污染）。
**🛠️ 已固化成工具，别再现写脚本**：`KB\方法论\活动程序开发\tools\x2x3_asset_port.py`
`index --x3 <X3\client>` 建 guid 索引（扫 3~4 万 `.meta`，约 10min，**后台跑**，X3 无大改动可复用缓存）→ `plan --pkg <导出包...> --actv UIActvXxx` 出差集+落地计划（默认预演）→ 加 `--go` 执行。内置：只新增不覆盖／同名不同 guid 碰撞点名并跳过／`_1` 副本先比 MD5 再取非 `_1`／落点按下面实证约定。
**落地前必算「X3 已有 vs 必须拷」**：X2/X3 同源，同 guid 资产原地解析零拷贝；整包倒进去会造出一堆重复副本（后续 X3 公共件改版你这套不跟着走）。限时抢购 160 guid 里 **108 已有、只需拷 52**。
**🔑 落点别照 X2 路径平移**（2026-07-31 拿 108 个已有件实证：`Assets/{P2,x2}/Res/…`→`Assets/Res/…` 只有 **68%** 命中，7% 仅大小写差，**26% 真不同**）。两条 X3 真实约定：① `Effect/Material` 在 X3 叫 **`Materials`**（复数）② **换皮带进来的公共件塞进本活动自己的目录**（先例 `UIActvCircusGacha/Images`、`UIActvLaborGacha/{,Textures}`、`UIMonopolyPigBanck/Images`）。⚠️ 同 guid 资产在 X3 可能**被改过名**（`Glow_043.PNG`→`ui_glow01.PNG`、`Glow_2002.png`→`.../Common_Ship/tex/Glow_004.png`）——按 guid 判存在，别按文件名。
**⚠️ 同名不同 guid 碰撞必查**：X3 可能已有同名但不同 guid 的件，平铺进去会**覆盖 X3 原件**。实例：`BoxReward.anim` X3 有**两份**（`Res/Ani/` + `Res/UI/Animation/`，都 8048B，guid 各异），X2 那份是第三变体 8360B ⇒ 落进**活动专属子目录** `Res/UI/Animation/<活动名>/`（先例：X3 自己的 `Res/UI/Animation/HeroClub/`）。guid 决定引用，目录随便放不影响链路。
**🔴🔴 换皮无忧清理面板会删光共享目录（2026-07-31 真事故：删掉 143 个 X3 原生 prefab / 286 文件）**：白名单＝`GetDependencies(根prefab,true)`，目录里不在白名单的**一律删**。断链路线（Unpack）的 prefab `[Prefabs 0]`＝不引用任何 prefab ⇒ **同目录所有 prefab 全成"未引用"全灭**。铁律：①「资源目录」只填**本次搬运专属新目录**（`Res/UI/Sprite/UIActvXxx/`），**禁填** `Res/UI/Prefab/Activity`、`Res/UI/Animation`、`Res/Shader/Effect` 等共享目录 ②**必须先点「预览」看 `将删 N`**，N 远大于本次搬入件数＝立刻停手（本次 `将删 143` vs 搬入 4）③走断链路线时该工具对 prefab 目录基本不可用。恢复＝`git checkout -- <目录>`（被删的是 tracked 可完整复原）＋根 prefab 被 PatchGuid 改写过要从导出包重拷（先另存备份再 checkout）。
**🔑 算 missing script 必须扫三处**（否则误报，2026-07-31 连踩两次）：`Assets/`（项目脚本）+ `Packages/`（内嵌包，UGUI 的 `LayoutElement`/`ContentSizeFitter`/`Shadow`/`Mask` 都在这）+ `Library/PackageCache/`（注册表包实际落地处，Spine `SkeletonGraphic`、UIEffect `Bevel`/`UIParticleSystem` 在这）。只扫 Assets 误报 19 个缺失、漏 PackageCache 误报 4 个，**真实答案 0 个**——X2/X3 UI 框架层脚本 guid 几乎全共享（`TFWImage` 1284 实例等）。
**拷法**：**Explorer 拷 + 目标工程 Unity 关闭**，`.meta` 必须一起拷。拖进 Unity Project 窗口 = Import，**Unity 忽略你的 .meta 重新生成 guid** ⇒ 引用全断满屏白图；Unity 开着拷 = 导入缓存吃中间态（白模/糊图）。
**校验坑**：`shutil.copy2` 保留源 mtime（可能是几个月前），用 `find -newermt` 数落地文件会得 **0**，要用 `git status --porcelain | grep '^??'`（目录会折叠，需展开再计数）。落地全是 untracked ⇒ 回退 = `git clean -fd <那几个目录>`。
⇒ **最优＝两条都跑、产物摆一起 diff**（路A 导到 `..\Copy\<名字>_manualA\` 别覆盖 B 包）：路A 消灭 UNRESOLVED+拿译文，路B 补字体+看真实嵌套。实证代价：限时抢购只走路B → 52 个 UNRESOLVED + 无译文 → 落地"满屏 LC_ 裸 key"。
**🔑 路A 内部还分两条线，先定目标再选，别把其中一条当"坑"（2026-07-31 FlashSale 实测）**：
- **断链路线**＝拖场景/Unpack/改名/存 Assets 根 → 导。产出新 guid 的自包含件，公共件内联成哑拷贝（锁死 X2 外观、不跟 X3 公共件升级走）。**`[Prefabs 0]` 是正确结果不是事故**；叶子资产不丢（实测 108 条 `UNRESOLVED 0`），体积会涨数倍（3.6MB→29.6MB）。**要在 X3 重写界面/换皮改名 就走这条**。
- **保链路线**＝Project 选中原件右键 `Tools▸X2▸Export Prefab Assets...` 直接导（工具只吃 GetDependencies，不要求解包）。保 x2 原 guid（X2/X3 同源资产原地解析零拷贝），公共件保留为独立 prefab（FlashSale `[Prefabs 17]`）。**只想看依赖清单 / 要保 guid 落地 走这条**。
- 验收判据统一看 manifest `[Prefabs]`：断链必须=0，保链必须≠0。断链路线的「改名」别跳（工具拿 prefab 文件名当输出子目录名），除非落地名不变。
**🔴 输出目录每次必须改成本次专属目录**：默认 `D:\newX2\Copy` → 产物写进 `...\Copy\<prefab名>\`，同名 prefab 的历史包会被掺入。`CopyAssetWithMeta` 走 `GetUniqueDestinationPath`，重名**不覆盖**、加 `_1` 后缀塞旁边 ⇒ 旧包一个不丢但两次导出混成一坨拆不干净（同一次导出内的重名也吃 `_1`）；真被重写的只有生成文件 `_manifest.txt`/`localization_keys.tsv`。
👉 完整说明书（**①反查→②导出→③落地→④去重→⑤换件→⑥接线→⑦注册→⑧验证 八阶段全链路** + 路A/B 对照 + 每阶段翻车对照表）：`KB\方法论\活动程序开发\X2到X3_UI资产搬运_PrefabAssetExport说明书.md`

## X2→X3 UI prefab 迁移必补：根节点组件套装（2026-07-20 扭蛋机实证）
X2 界面 prefab 根节点没有 X3 UIBase 要求的组件——运行时 `UIBase.InitCanvas`（UIBase.cs:681）直接设 `canvas.renderMode`，根无 Canvas = 打开即 `MissingComponentException`（Editor.log 栈顶 `WndMgr show <UI名> ... MissingComponentException: There is no 'Canvas'`）。**迁移完必对照任一 X3 正常界面（如 UIActvLaborGacha）核根组件五件套**：RectTransform + UIConfig(e8f4194e9ed83794da496c6236ff0d7f，遮罩/防连点) + Canvas(SortingOrder=11) + CanvasScaler(0cd44c1031e1…，1080×1920) + GraphicRaycaster(dc42784cf147…)。四块全自包含（只指 m_GameObject），可从 LaborGacha 照抄换新 fileID 手术进 YAML；验证=根组件列表同构 + component 引用无悬空。找真根=`m_Father: {fileID: 0}` 的 RectTransform（文件首块不一定是根）。

## X2→X3 UI 迁移第二坑：缺 X3 节日基本模块（标题/描述/倒计时，2026-07-20 扭蛋机实证·两轮定稿）
X2 界面没有 X3 节日活动页标配的左上角信息区（标题+时钟倒计时+描述小字，样式见任一 X3 节日 tab 页）。
- ❌**别复用 X2 自带的顶部骨架**（扭蛋机 `Cont/Top` 那种）——第一轮这么干被用户打回：X2 那套位置在底部居中+橙框样式，和 X3 左上角标准完全不符，"能挂字"≠"样式对"。
- ✅**正解=从 X3 标准界面整棵移植 Top 组**：`UIActvLaborGacha.prefab` 的 `CentreOther/Animation/Top`（仅 9 节点：txt_title / Time(bg+Icon+txt) / btn_info(bg) / ActvDesc），YAML 手术=BFS 收集子树全部块（GameObject/RectTransform/组件）→ 新 fileID 全量重映射（内部引用 remap、m_Script/sprite 等外部 guid 原样保留、遇 !u!1001 PrefabInstance 中止）→ 顶层 tf 的 m_Father 指到目标根 + 根 m_Children 追加（放最后=渲染最上层）→ 验证=路径树 + component/children 引用无悬空（⚠️验证正则块尾要 `(?=\n--- |\Z)` 含 \Z，否则文件尾块漏解析误报丢节点）。
- 代码：Auto_ 引用 `Top/txt_title`、`Top/ActvDesc`、`Top/Time/txt`、`Top/Time`，btn_info 加监听；主 cs 一行 `UIHelper.SetActivityBaseInfo(activityId, title, desc, time, goTime:, ruleInfo:)`（UIHelper.Activity.cs:202，title=cfg.ActvName/desc=ActvDesc/time 自动倒计时+到期隐藏/ruleInfo 按 ActvRule 配置显隐）。X2 骨架容器照旧整体 SetActive(false)。
配套坑：新写活动行的 TXT_ActvOnline_ActvName/ActvDesc 只填 cn+en 时，繁中客户端 tab 显英文——克隆行 16 语全带 vs 新写行只有 cn/en，收口时至少补 zh。
