---
name: workflow-p2-to-x3-asset-port
description: P2/X2→X3 Unity 3D 资产跨项目搬运手法（原GUID保链+材质重写+骨架克隆嵌套实例+DK双注册），搬家具/主城皮肤/装饰模型时套用
metadata: 
  node_type: memory
  type: reference
  originSessionId: 42ce653e-2e7b-416e-a7f6-25cb4ac83e33
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
1. **P2 shader（High/Low/Shadow 全部）依赖 C# 全局日夜 uniform**（`_GlobalDayNightColor`/`_ToneMappingMin/Max`/`_LightIntensity`/雾参数），X3 没脚本喂值→全局默认 0→`col.rgb *= _GlobalDayNightColor` **乘成全黑**。别搬 shader，用 X3 `X3_World_City.shader`（guid 0e3b6aad...，unlit `_MainTex*_Color`）。
2. **diffuse 必须用 Low 档**：High 档 diffuse 是给 PBR 管线的原始 albedo（平、艳，unlit 下没质感）；Low 档 diffuse 光影/AO 全烘进颜色（两图 87% 像素不同、分辨率相同 2048）——配 X3 unlit shader 正好是 P2 低端机在游戏里的最终画面。马戏案修正 commit `43b1f96db15`。
3. 阴影片不搬：X3 原生岛=岛体+水波两件套、无阴影片惯例，且其 shader 同样依赖全局 uniform。

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
