# X2→X3 UI 资产搬运说明书（导出 → 落地 → 去重清理）

> 来源：两段录屏（2026-07-07 晚，均无声，是同一条流水线的上下半场）
> - 上半场 `X3验收\搬运.mp4`（20:48–20:50，2分04秒）＝ **X2 侧导出**（PrefabAssetExport）→ 本文 Part A
> - 下半场 `X3验收\prefab重复内容清理.mp4`（21:00–21:02，2分45秒）＝ **X3 侧落地 + 去重清理**（换皮无忧）→ 本文 Part B
>
> 实操对象：X2 强消耗/扭蛋机界面 `21201326` → X3 `UIActvCircusGacha`（马戏节扭蛋机）
> 两个工具是两个工程各自的 Editor 工具，**不是一个**：导出在 x2client，清理在 x3-project。
> 导出工具作者：zhangli，commit `9990489d3991`（新增）+ `defd018b702d`（补 Shader 导出），x2client `dev_festival`

---

## 🗺 全链路八阶段（先看这张，再看细节）

```
①反查         ②导出          ③落地         ④去重      ⑤换件       ⑥接线        ⑦注册     ⑧验证
谁加载谁   →  X2侧拷出来  →  拷进X3工程 → 清重复 → X2组件换X3 → 节点对齐代码 → DK+i18n → 起服验
(必做!)      (两条路选一)    (.meta同拷)  (换皮无忧) (X2 Migration) (Auto_契约)   (双表)   (6道关)
```

| 阶段 | 干什么 | 工具 | 本文/外部 |
|---|---|---|---|
| ① 反查 | 谁加载这个 prefab、怎么加载、代码绑了哪些节点路径 | `skills\unity-prefab-tools\prefab_code_binding_map.py` | §Part 0 |
| ② 导出 | X2 侧把 prefab + 依赖拷出来 | 路 A `Tools▸X2▸Prefab Asset Export` / 路 B `prefab_dependency_bundler.py` | Part A |
| ③ 落地 | 整包拷进 X3，`.meta` 同拷保 GUID | 手动 / Explorer | Part B §8 |
| ④ 去重 | 删未引用 + 重复项改指工程原件 | `Tools▸Prefab换皮`（换皮无忧） | Part B §9-10 |
| ⑤ 换件 | X2 组件 → X3 等价件、missing script 处置 | `Tools▸X2 Migration/*` | Part B §11 |
| ⑥ 接线 | 节点路径对齐代码契约 + 根组件五件套 + Top 组 | Editor 手拼 / 重生成 `Auto_` | Part C §14 |
| ⑦ 注册 | DK 双表 + i18n（`LC_`→`TXT_`） | `x3-translation-automatic` | Part C §15 |
| ⑧ 验证 | 编译→打开→起服→重登→主链路→外显 | — | Part C §16 |

⚠️ **①不能跳**。prefab 有两种被加载方式，后果完全不同：**嵌套引用**（`!u!1001` 块，扫依赖能扫到）vs **`assetPath` 字符串运行时加载**（**依赖扫描的盲区**，只能反查代码）。跳过①的典型症状＝界面主体正常、某类元素全缺。

---
# Part 0 · 反查（开工第一步）

拿到一个 X2 界面先回答三问，**看 prefab 本身答不出来**：
1. **谁加载它、怎么加载**（嵌套 vs assetPath 字符串）→ 决定要不要单独搬、动它会不会连带别人
2. **挂的脚本哪些是本模块专属、哪些是通用件** → 专属脚本决定要不要搬代码
3. **代码里 `GetChild("路径")` / `GetComponent<T>("路径")` / `AddListener(..., "节点名", ...)` 绑了哪些节点路径** → **硬编码，节点改名即断，必须原样保留**

工具 `prefab_code_binding_map.py`（GUID 双向反查，四类清单一次出）。⚠️ 大仓全量 walk 数分钟，用 `--code-root` 缩范围；别 ripgrep 全仓 grep（20s 超时）。
配套 `prefab_rect_tree.py`：不开 Unity 打印节点 RectTransform 链/锚定/Image 类型（诊断"编辑器里位置怪、运行时又对"、进度条 fillAmount 不生效）。

**两个实证反例，说明为什么这步必做**：
- 限时抢购：4 个 prefab **互不嵌套、各自 assetPath 独立加载、prefab 上零专属脚本**、绑定全靠节点路径 —— 只有反查得出。
- P2 建筑皮肤：特效**全是 `assetPath:` 字符串挂载**，`grep guid` 一个都扫不到（见 [[workflow_p2_to_x3_asset_port]] 四号坑）。

---
# Part A · X2 侧导出（PrefabAssetExport）

---

## 0. 这工具解决什么问题

搬一个 X2 界面到 X3，手工最痛的不是 prefab 本身，而是**它引用的几百张散落资源**——图、特效贴图、材质、shader、动画、多语言 Key，分布在 `Assets/P2/...` 和 `Assets/x2/...` 十几个目录里，漏一个到 X3 就是白图/紫模/空文案。

这个 Editor 工具做的事：**给它一个 prefab，它把整棵依赖树按类型分好类拷出来，连 `.meta` 一起拷**，再附一份清单和一份多语言 TSV。

🔑 **能 drop-in 的原因是 `.meta` 一起拷 → GUID 不变 → prefab 里的引用在 X3 自动成立**（跟 [[workflow_p2_to_x3_asset_port]] 里 3D 资产搬运同一个原理）。实证：X2 侧 `Activity_bg_GachaMachineA.png` guid `e24ba7a9d89ed264d9d7fc91d0df8781`，落到 X3 `Assets/Res/UI/Sprite/UIActvCircusGacha/Images/` 后 guid 一模一样，prefab 里那行引用没改过。

---

## 1. 工具位置

| 项 | 值 |
|---|---|
| 菜单 | **Tools ▸ X2 ▸ Prefab Asset Export** |
| 另一入口 | Project 里选中 prefab → 右键 **Tools ▸ X2 ▸ Export Prefab Assets...**（自动填好目标，省一步拖拽） |
| 源码 | `x2client\client\Assets\Editor\PrefabAssetExport\`（`PrefabAssetExportWindow.cs` / `PrefabAssetExportUtility.cs` / `PrefabLocalizationExportUtility.cs`） |
| 工程 | `D:\UGit\x2client\client`（Unity 2022.3.62f1c1，录屏里开的是 `TFW_Logo` 场景） |

⚠️ **只有 X2 侧有这个工具，X3 客户端没有对应的导入工具**（全仓搜 `PrefabAssetExport` 零命中）——X3 侧就是手工把整目录拷进去（见 §5），别去 X3 菜单里找。

---

## 2. 操作五步（录屏原样复现）

> 🔑 **纠偏（2026-07-30 重读源码）：下面五步里的「拖场景 / Unpack / 改名 / 存 Assets 根」只在「要落地一个改了名的自包含 prefab」时才需要**（扭蛋机场景：X2 名 `21201326` → X3 名 `UIActvXxx`）。
> **只想导出依赖清单做比对/看有什么** → 直接 **Project 选中源 prefab → 右键 `Tools ▸ X2 ▸ Export Prefab Assets...`**（`OpenFromContext` 会自动填好目标 Prefab），四步全省。工具本身只吃 `AssetDatabase.GetDependencies`，不要求解包。
>
> ### 两条路线，先定目标再选（2026-07-31 FlashSale 实测对照）
>
> | | **保链路线**：原地右键原件 | **断链路线**：拖场景+Unpack+改名+存根目录 |
> |---|---|---|
> | prefab 大小 | 3.6 MB | 29.6 MB（8×，嵌套内容硬拷进本体） |
> | `.meta` guid | `0902ea9d…` = x2 原件真身，X3 落地即接原链 | `48aa782b…` = 新资产，与 x2 原件断链 |
> | manifest `[Prefabs]` | 17（4 主 + 13 公共件） | **0** ← 125 个 `!u!1001` 全展平 |
> | 公共件 | 保留为独立 prefab，跟 X3 公共件升级走 | 内联成哑拷贝，从此不跟升级；但**锁死 X2 外观** |
> | 叶子资产完整性 | 同 | 108 条、`UNRESOLVED 0` —— 展平不丢叶子，图/材质/shader 照样全捞 |
>
> **选谁**：
> - 目标是**在 X3 里重写这个界面 / 换皮改名 / 要一个自包含不受 X3 公共件影响的版本** → **断链路线**，`[Prefabs 0]` 是正确结果，不是事故。（FlashSale 走的就是这条。）
> - 目标是**保 guid 直接落地**（X2/X3 同源资产原地解析、零拷贝）**或只想看依赖清单做比对** → 原地右键即可，四步全省；工具只吃 `AssetDatabase.GetDependencies`，不要求解包。
>
> ⚠️ 断链路线的第 3 步「改名」别跳：工具拿 **prefab 文件名**当输出子目录名，跳过就得事后连 `.meta` 一起手改。落地名不变（如 X3 代码硬编码 `assetPath` 仍加载 `FlashSale`）才可以跳。

### 第 1 步：把源 prefab 拖进场景
Project 搜 `21201326` → 拖到 Hierarchy（录屏用的是最轻的 `TFW_Logo` 启动场景当白板，别开主城场景，慢）。
⚠️ X2 里同名 prefab 有三份：`P2/Res/UI/Prefab/Activity/Module/21201326.prefab`、`x2/Res/.../21201326.prefab`、`21201326_old.prefab`。**要 x2 那份**（x2 覆盖 P2），`_old` 是旧版残留。

### 第 2 步：Unpack Completely
右键实例 → **Unpack Completely**。
**为什么必须做**：不解包，导出的 prefab 会留一条指回 X2 原 prefab 的嵌套引用（`!u!1001` PrefabInstance 块），到 X3 就是断链。解包后整棵树变成普通 GameObject，自包含。
✅ 验证：导出的 `_manifest.txt` 里 `[Prefabs 0]`、prefab 文件里 `--- !u!1001` 计数 = 0（本例 368 个 GameObject，0 个嵌套实例）。

### 第 3 步：改成 X3 的名字
Inspector 顶部改根节点名 → 本例 `UIactvfesstrong`（X3 命名习惯 `UIActvXxx`）。
**为什么在导出前改**：工具用 **prefab 文件名**当输出子目录名（`输出目录\<prefab名>\`），改完名字导出的整包目录名就是 X3 的名字，不用事后重命名。

### 第 4 步：拖回 Project 存成 prefab 资源
把 Hierarchy 里改好名的节点拖到 Project 的 `Assets` 根目录 → 得到 `Assets/UIactvfesstrong.prefab`。
（工具只接受 `Assets/` 下的 prefab 资源，场景里的实例不行。存根目录是图省事，导完删掉即可。）

### 第 5 步：开工具，导出
**Tools ▸ X2 ▸ Prefab Asset Export**，面板四项：

| 字段 | 录屏取值 | 说明 |
|---|---|---|
| 目标 Prefab | `UIactvfesstrong` | 从 Project 拖进来 |
| 输出目录 | `D:\newX2\Copy` | 代码里的默认值，记在 EditorPrefs（下次自动带上）。真正产物在 `D:\newX2\Copy\<prefab名>\` |
| | | 🔴 **每次导出前必须改成本次专属目录**（如 `D:\newX2\Copy\FlashSale_manualA`）。不改 = 同名 prefab 的历史导出包会被掺进新文件：`CopyAssetWithMeta` 走 `GetUniqueDestinationPath`，重名不覆盖而是**加 `_1` 后缀塞在旁边**，两次导出混成一坨且无法按后缀干净拆分（同一次导出内的重名也会吃 `_1`）。唯一真被覆盖的是生成文件 `_manifest.txt` / `localization_keys.tsv`。 |
| 排除红点资源 | ✅ | 路径含 `reddot / red_dot / redpoint / hongdian / 红点` 的资源不导（X3 有自己的红点体系） |
| 复制主 Prefab 到 Prefabs | ✅ | 主 prefab 自己也拷一份进 `Prefabs\` |
| 导出 TFWText 本地化 TSV | ✅ | 见下文 §4 |

点 **导出资源** → 完成后**自动弹开资源管理器**定位到产物目录；面板下方「导出日志」列出每个资源的原始路径（有「复制全部」按钮）。失败会红字报错并写 Console。

---

## 3. 产物结构（本例实测）

```
D:\newX2\Copy\UIactvfesstrong\
├─ Images\        64 个 png + 各自 .meta   ← textureType = Sprite 的图
├─ Textures\      11 个                    ← 非 Sprite 贴图（特效用 glow/mask/noise/ring/trail）
├─ Animations\     9 个                    ← .anim / .controller
├─ Materials\      9 个                    ← .mat（特效材质）
├─ Shaders\        1 个                    ← .shader
├─ Prefabs\        1 个                    ← UIactvfesstrong.prefab（主 prefab 本体，3.9 MB）
├─ _manifest.txt                           ← 清单：源路径、导出时间、开关状态、分类明细
└─ localization_keys.tsv                   ← 15 个 lc_ Key × 17 语言
```

**`_manifest.txt` 记的是"资源在 X2 的原始路径"**，价值在换皮时反查：
```
[Images 64]
Assets/P2/Res/UI/Atlas/Event/ActivityWhiteRect.png          ← P2 公共图
Assets/x2/Res/UI/TextureNew/Activity/Activity_bg_GachaMachineA.png   ← X2 专属图（要换皮的）
Assets/x2/Res/UI/NewSprite/Common/frame/Common_frame_IconBox2_Epic.png ← X2 通用框（X3 有对应件，可弃）
...
```
→ 一眼分出「**必须换皮的活动专属图**」和「**X3 已有的通用件（别搬，用 X3 自己的）**」。本例 64 张图最后只有 21 张真正落进 X3。

---

## 4. 分类规则 & 参数含义（源码级，别猜）

- **依赖收集**：`AssetDatabase.GetDependencies(prefab, recursive:true)`，只要 `Assets/` 下的，跳过 `Packages/`、`Library/`。
- **图片走哪个目录**：读 TextureImporter，`textureType == Sprite` → `Images`，否则 → `Textures`；拿不到 importer 时按路径兜底（含 `/texturenew/ /textures/ /texture/` → Textures）。
- **认的后缀**：图 `png jpg jpeg tga psd bmp gif webp`；动画 `anim controller overridecontroller playable`；另有 `prefab / mat / shader`。**其余类型全部不导**（音频、字体、ScriptableObject、C# 脚本都不在内）。
- **同名冲突**：自动加后缀 `_1 _2`（所以 X3 侧会看到 `Activity_bg_GachaMachineA_2_1.png` 这种名字——不是美术命名，是工具去重来的）。
- **多语言 TSV**：只收根下所有 `TFWText` 组件的 Key，且必须匹配 `^(lc|LC)_[a-z0-9_]+$`；硬编码文本/纯符号会被跳过并在日志里报「跳过 N 个非 lc_ Key」。文案值从 `Assets/P2/Config/Gen/i18n/<lang>.bytes` 里读，列 = `id` + 17 语（en cn ar de fr jp kr po ru sp th tr zh vi id it pl），UTF-8 带 BOM，换行转 `\n`、Tab 转空格。

---

## 5. ⚖️ 路 A（Editor 工具）vs 路 B（命令行打包器）—— 两个真实包实测对照

第二条导出路：`C:\ADHD_agent\skills\unity-prefab-tools\prefab_dependency_bundler.py`（正则解 guid + 反查源文件，文件级拷贝，**复现路 A 的产物格式**）。
两个包摊开对比（左＝路 A `D:\newX2\Copy\UIactvfesstrong`，右＝路 B `D:\newX2\Copy\FlashSale`）：
```
路A: _manifest.txt  Animations Images Materials Prefabs Shaders Textures  localization_keys.tsv
路B: _manifest.txt  Animations Images                Prefabs        Other
```

| 差异点 | 路 A · Editor 工具 | 路 B · 打包器 |
|---|---|---|
| **依赖怎么算** | Unity `AssetDatabase.GetDependencies` —— **权威，不存在算不出** | 正则 grep `guid:` + 按 `--index-root` 反查 → **FlashSale 包挂 52 个 `UNRESOLVED guids`** |
| **图分类语义** | 读 TextureImporter：**Sprite→`Images`，非 Sprite→`Textures`**（扭蛋机 `Textures/` 全是 `Glow_*/Mask_*` 特效贴图） | 按扩展名：**`.png` 一律 `Images`** → 特效贴图与 UI 图混在一起 |
| **材质 / shader** | 单独分 `Materials/`（9）`Shaders/`（1） | FlashSale 包**这两个目录都没有**（真没有 or 在 52 个 UNRESOLVED 里） |
| **多语言** | 出 `localization_keys.tsv`（`lc_` Key × 17 语全文案） | **没有** → 落地后"满屏 `LC_` 裸 key"时无译文可对 |
| **字体 / TMP FontAsset / SO** | **静默丢**（分类表只认 图/anim/prefab/mat/shader，`.ttf`/`.asset` 不在内） | `Other/` 兜底接住（FlashSale 包 2 个 `.ttf` 就在这） |
| **嵌套 prefab** | 流程要求先 Unpack → **摊平自包含**，支撑 prefab 一个都不用搬 | **原样保留**为独立 prefab（FlashSale 包 17 个＝4 主＋13 支撑） |
| **一次几个** | **1 个**（4 个要跑 4 遍 → 4 目录，共享资源重复 4 份） | **多个**（`--prefab a b c`，共享资源只 1 份） |
| **要不要开 Unity** | 要 | 不要 |

**结论：不是某条路错，是两条路盲区互补。**
- 路 B 的代价＝**UNRESOLVED 缺口 + 没译文 + 特效贴图分类混淆**（限时抢购"满屏 LC_ 裸 key"直接对应第二项）。
- 路 A 的代价＝**丢字体/FontAsset**、一次一个、要 Unpack（摊平后公共件不再跟 X3 升级走）。
- ✅ **最优做法＝两条都跑，产物摆一起 diff**（路 A 导到独立目录如 `..\Copy\<名字>_manualA\`，别覆盖路 B 包）：用路 A 消灭 UNRESOLVED + 拿译文，用路 B 补字体 + 看真实嵌套结构。

## 6. 导出完了下一步

进 **Part B**（X3 侧落地 + 去重清理）。工具只搬"皮"，**骨（代码/组件/配置）一概不搬**，收尾清单见 Part B §11 + Part C。

---

## 6. 坑位清单

| 坑 | 后果 | 规避 |
|---|---|---|
| **Unpack 与目标路线不匹配** | 断链路线忘了 Unpack → prefab 带 `!u!1001` 指回 X2 原件、公共件没搬齐则断链；保链路线误 Unpack → 公共件整批内联、guid 变新资产 | 导出后看 manifest 的 `[Prefabs]`：**断链路线必须 = 0，保链路线必须 ≠ 0**（FlashSale=17）。两条路线定义见 §2 顶部对照表 |
| 输出目录沿用默认 `D:\newX2\Copy` | 同名 prefab 的历史包被掺入 `_1` 副本，混成一坨拆不干净 | 每次导出前改成本次专属目录（见 §2 第 5 步表） |
| 只拷 png 不拷 `.meta` | GUID 重排，prefab 全白图 | 整目录拷，别挑文件 |
| 搬 X2 通用件进 X3 | 同一张公共图两份、后续 X3 改版不同步 | 按 `_manifest.txt` 分「专属 vs 通用」 |
| 拿 `21201326_old` 或 P2 那份当源 | 搬的是旧版界面 | 确认路径是 `Assets/x2/Res/UI/Prefab/Activity/Module/21201326.prefab` |
| 指望它搬字体/音效/脚本 | 静默不导（分类表里没这些后缀） | 单独手搬 |
| 以为 TSV 能直接进 X3 | Key 体系不同（LC_ vs TXT_） | 当译文参考，走 X3 i18n 流程 |
| 换二进制资源时 Unity 开着 | 导入缓存吃到中间态 → 白模/糊图 | 拷完让对方 Reimport 目录 |

---

---
# Part B · X3 侧落地 + 去重清理（换皮无忧）

> 来源：`X3验收\prefab重复内容清理.mp4`。X3 客户端 = `C:\x3-project\client`（Unity 2022.3.61f1c1，`GameBoot` 场景，分支 `dev_festival`）。

## 8. 先把整包丢进 X3

把 Part A 导出的 `UIactvfesstrong\` 整个文件夹（含 `.meta`）拷进 X3 `Assets\` 下。录屏里落在 **`Assets/Res/Uiactvfesstrong/`**（Res 顶层）——这是**临时中转位**，别当最终位置：X3 工程规范（`AIDocs\X2_to_X3_Migration\07_File_Placement.md`）明确「**不要在 `Assets/Res/` 顶层乱建新目录**」，正式位置是
```
UI 图        → Assets/Res/UI/Sprite/<功能模块>/
UI prefab    → Assets/Res/UI/Prefab/<功能模块>/
```
本案最终落在 `Assets/Res/UI/Sprite/UIActvCircusGacha/Images/`（**实证**：里面的 `Activity_bg_GachaMachineA.png` guid = X2 侧同一个 `e24ba7a9…`，drop-in 生效）。

✅ **落进去马上验一次**：双击 prefab 进 Prefab 模式——录屏里两台扭蛋机、球、按钮全都正常显示，说明图的 GUID 链没断。这一步比任何日志都直观。

## 9. 清理工具：Tools ▸ Prefab换皮（窗口名「换皮无忧」）

| 项 | 值 |
|---|---|
| 菜单 | **Tools ▸ Prefab换皮** → 窗口标题 `换皮无忧`，页签 `换皮无忧 — 资源目录清理` |
| 源码 | `x3-project\client\Assets\Editor\HuanPiWuYou\`（`HuanPiWuYouWindow.cs` + `UIPrefabResourceFolderCleanupPanel.cs`，独立 asmdef） |
| 干什么 | 面板自述：**「删掉资源目录内 Prefab 未引用的文件；同名/同 GUID 重复项改为工程原件 GUID 后删除副本。」** |

### ⚠️ 不跑这工具时，`REPLACE` 那一半的活要自己补（2026-07-31 限时抢购实证）

按 guid 算差集只挡住「同 guid 重复」，**漏掉「同文件名 + MD5 相同 + guid 不同」的重复件** —— 那才是 `REPLACE` 负责的。落地后必须补一道**同名件检查**：拷进去的每个文件名，在 X3 全仓找同名件比 MD5。

实测 53 件落地件 → 4 件在 X3 有同名件：

| 文件 | X3 原件 | MD5 | 处置 |
|---|---|---|---|
| `Common_icon_FrequencyBg1.png` | `Res/UI/Spirits/ActvMecha/`（`51daedae…`） | 相同 | 真重复：prefab 里 `a38a9594…`→`51daedae…` + 删副本 |
| `Mask_009.tga` | `Res/Effect/Textures/Mask/` + `Res/Effect/UI/Textures/` 两份 | 相同 | 真重复，但**无人引用**（依赖它的材质 X3 本来就有、指向 X3 自己那份）⇒ 直接删，不用改引用 |
| `BoxReward.anim` | `Res/Ani/` + `Res/UI/Animation/` 两份（都 8048B） | **不同**（我们 8360B） | 各自保留，落活动子目录 |
| `FX_AddBlend_DistortionDissolve_Flow_New_UI.shader` | `Res/Shader/X3/Effect/`（`871d85d6…`） | **不同** | 各自保留，见下方 shader 坑 |

**删前必查引用**：无人引用的直接删，有引用的才做 guid 文本替换。

### 🔴 它对 `.shader` 只比文件名不比内容 → 会误替换不同的 shader

源码注释「shader 换皮场景：同名即替换」。实测两份同名 shader **内部声明不同**：

| 文件 | `Shader "..."` 声明 |
|---|---|
| `Res/Shader/Effect/FX_AddBlend_DistortionDissolve_Flow_New_UI.shader` | `TFW/Effect/**UI**/FX_AddBlend_DistortionDissovle_Flow_New_UI` ← UI 变体 |
| `Res/Shader/X3/Effect/FX_AddBlend_DistortionDissolve_Flow_New_UI.shader` | `TFW/Effect/FX_AddBlend_DistortionDissovle_Flow_New_UI` ← 通用版 |

跑那工具会把 UI 变体替换成通用版，**特效渲染直接变**。判据＝比 `.shader` 里的 `Shader "路径名"` 声明，**不是比文件名**。（顺带：两者声明名不同，所以两份共存**不会**造成 `Shader.Find` 歧义。）

### 🔴🔴 事故实录（2026-07-31 限时抢购）：它删掉了 143 个 X3 原生 prefab

**「资源目录」字段填成 `Assets/Res/UI/Prefab/Activity` ⇒ 那个目录下除根 prefab 外的 143 个 X3 原生 prefab（`ActvRank` / `ActvTaskTemplate` / `ActvWonderTemplate` / `BattlePassRwdItem` / `DailyGift` / `GlassBox` / `HeroChampionList` …）全被删，共 286 个文件（含 `.meta`），根 prefab 还被 PatchGuid 改写。**

**机制**：白名单 = `GetDependencies(根prefab, true)`，目录里不在白名单的**一律删**。而**断链路线**（Unpack）的 prefab 依赖里 `[Prefabs 0]` —— 一个 prefab 都不引用 ⇒ 同目录所有 prefab 全成了「未引用」。**断链路线 + 共享目录 = 必然全灭。**

**三条铁律**：
1. **「资源目录」只能填这次搬运专属的新目录**（`Assets/Res/UI/Sprite/UIActvXxx/` 这种），**绝对不能填 `Res/UI/Prefab/Activity`、`Res/UI/Animation`、`Res/Shader/Effect` 等任何工程共享目录**。共享目录里的东西不该由这个工具管。
2. **必须先点「预览」看 `将删 N`**。N 明显大于你这次搬进来的件数 = 立刻停手。本次预览会显示 `将删 143`，而搬进来的只有 4 个。
3. **走断链路线（`[Prefabs 0]`）时，只有 prefab 目录不能交给它** —— 它算不出「这些 prefab 是别人的」，只能靠你把目录范围框对。

> **⚠️ 纠正（2026-08-03）：别把上面读成「整个工具不能用」。** 危险的只是「资源目录」这个字段填了共享目录，**不是工具本身**——它的删除范围**只限该字段指向的目录内**。填本次搬运的**专属目录**就是安全的，而且正是收掉「同名+MD5 重复」和「孤儿文件」的正解。
>
> **正确姿势＝按专属目录分多次跑**，每次只换「资源目录」，每次**先点「预览」看 `将删 N`**（N=0~2 正常；N 几十/几百＝目录填错，立刻停手）。
>
> 限时抢购实操（3 次）：
> | # | 资源目录 | 预期 |
> |---|---|---|
> | 1 | `Assets/Res/UI/Sprite/UIActvFlashSale/Images` | 收掉 `Common_icon_FrequencyBg1.png`（改引用 + 删副本，prefab 里 9 处全在 `ChestProgress`） |
> | 2 | `Assets/Res/UI/Materials/UIActvFlashSale`（含子目录 Textures） | 收掉 `Mask_009.tga`（无人引用，按"未引用"删，正合意） |
> | 3 | `Assets/Res/UI/Animation/UIActvFlashSale` | 预期 0 改动（`BoxReward.anim` 同名但内容不同，不判重） |
>
> **禁填清单**：`Res/UI/Prefab/Activity`（共享，143 件事故）· `Res/Shader/Effect`（共享 + shader 只比名会误换 UI 变体）。
> 它结尾的 `断链 GUID：M` 可当独立交叉验证 —— **M≠0 常常是正常的**（按 §「断链三类判读」判），别当点错了。

**恢复**（被删的是 tracked 文件，可完整复原）：
```bash
cd C:\x3-project && git checkout -- client/Assets/Res/UI/Prefab/Activity   # 恢复 143 个原生 prefab
# 根 prefab 被 PatchGuid 改写过 → 从导出包重新拷（连 .meta）
cp D:\newX2\<包>\Prefabs\<名>.prefab* client\Assets\Res\UI\Prefab\Activity\
```
⚠️ 先把被改写的根 prefab 另存一份再 checkout，万一里面有你手工改过的东西。

⚠️ **它不在 `Tools ▸ X2 Migration` 那一栏**，也**没登记进官方工具目录** `AIDocs\X2_to_X3_Migration\13_Migration_Tools.md`（那份只列了 6 个 `X2 Migration/` 工具）——别人翻文档找不到它，交接时要专门交代。

### 操作四步
1. Project 里**先选中根 prefab 再开菜单** → 窗口会自动填「根 Prefab」并尝试推断资源目录（`FillFromSelection`）。
2. **资源目录**：「推断」按钮只认 `Assets/Res/UI/<prefab名>` 这一种路径，录屏里包放在 `Assets/Res/Uiactvfesstrong` → 推断不出来、字段留空。手法＝Project 里右键那个文件夹 → **Copy Path（Alt+Ctrl+C）** → 粘进字段（录屏最终值 `Assets/Res/Uiactvfesstrong`）。
3. **先点「预览」**（dry-run，只出报告不动文件）。报告格式：
   ```
   ===== 预览 =====
   将删 N，GUID 替换 M
   REPLACE <搬来的副本路径> → <X3 工程原件路径>
   DELETE  <要删的文件路径>
   ```
   录屏这一把是直接点了「执行清理」没走预览——**别学**，预览是唯一的后悔机会。
4. 「执行清理」→ 弹确认框「**将替换 GUID 并删除文件，建议先 Git 提交。继续？**」→ 继续。

### ⏱ 它很慢，别以为卡死
录屏点下去后 Unity 一直挂 `Hold on (busy for 58s…) HuanPiWuYouWindow.MouseUp`，**视频 165 秒结束时还在跑**。原因在算法：要遍历全工程每个 `.meta` 建 GUID→路径表，还要对包里每个文件名在整个 `Assets` 下 `GetFiles` 递归搜同名文件。X3 工程体量下分钟级正常。**跑之前先 git commit**（确认框也这么提示），别在里面点其他东西。

## 10. 清理规则（源码级，决定它会删什么）

**A. 删「prefab 没引用到的」**：以 `AssetDatabase.GetDependencies(根prefab, true)` 为白名单（`.cs` 不计），资源目录里凡不在白名单的一律进删除列表。→ 这就是 64 张图砍到 21 张的机制：Part A 是按「prefab 依赖」导的，但导出后你可能改过 prefab（换掉 X2 通用件、删节点），多出来的就在这一步被清掉。
**B. 去重，两条判据**：
- **同 GUID**：全工程 GUID→路径表里同一 GUID 出现多次且有一份在资源目录内 → 判重。
- **同文件名 + MD5 内容一致**：同名文件在工程别处也有且内容完全相同 → 判重。**例外：`.shader` 只比文件名不比内容**（源码注释「shader 换皮场景：同名即替换」）。
**C. 保留哪一份（`PickKeep`）**：优先**不在**资源目录里的那份（＝X3 工程原件），其次被 prefab 引用的，再按路径字母序。→ 语义就是「留工程原件，删你搬来的副本」。
**D. 怎么改引用**：文本级把旧 GUID 字符串全量替换成保留件的 GUID，改的文件范围 = 根 prefab + 资源目录内所有序列化文件（`.prefab .unity .mat .anim .controller .asset .shader .spriteatlas …`）。**这是纯文本 replace，不走 Unity API。**
**E. 收尾自检**：执行完报告尾部输出 `已删除：N，断链 GUID：M`——**`断链 GUID` 必须是 0**，非 0 说明 prefab 里还引用着工程中不存在的 GUID（漏搬资源）。
**F. `_manifest.txt` 被硬编码保护**，不会被删（`localization_keys.tsv` 没保护，会被当"未引用"删掉——想留就先挪出资源目录）。

⚠️ **它只保 prefab 和资源目录内的引用**。如果**别的** prefab / 场景 / 材质也引用着被删的那份副本（在资源目录外），GUID 不会被改 → 那边直接断链。所以清理前确认这批资源没被其他地方引上。

## 11. 清理完还剩的活（工具全都管不到）

1. **移到规范目录**：`Res/UI/Sprite/<模块>/`、`Res/UI/Prefab/<模块>/`（见 §8）。
2. **prefab 根节点补 X3 五件套**：RectTransform + UIConfig + Canvas(SortingOrder=11) + CanvasScaler(1080×1920) + GraphicRaycaster——不补，`UIBase.InitCanvas` 打开即 `MissingComponentException`。
3. **补 X3 节日标配左上信息区**：从 `UIActvLaborGacha.prefab` 整棵移植 `CentreOther/Animation/Top`，别复用 X2 自带顶部骨架（样式不对，会被打回）。
4. **X2 组件换 X3 等价件**——这才是 `Tools ▸ X2 Migration` 那一栏的活，按需跑：
   | 菜单项 | 干什么 |
   |---|---|
   | `CommonItemShow → UIItemTemplate 替换` | X2 道具框 → X3 `UIItemTemplate` |
   | `Head1 → UIPlayerAvatar 替换` | X2 玩家头像 → X3 `UIPlayerAvatar` |
   | `AllianceFlag → UIAllianceSymbolUnit 替换` | X2 联盟旗 → X3 联盟徽记 |
   | `清理 LayoutRtlAlignment(RTL) missing 组件` | X2 RTL 布局镜像组件（X3 无此脚本，missing 会**阻断 SavePrefabAsset**）→ 按 guid 精确删 |
   | `多语言键回填（按 fileID）` | 用 X2 导出的 `.loc.json` 回填 X3 `TFWText.languageKey` |
   | `Replace X2BetterOutline → BetterOutline` / `X2 红点组件替换工具` | 描边 / 红点组件换 X3 版 |
   官方详解＝`x3-project\AIDocs\X2_to_X3_Migration\13_Migration_Tools.md`（**新增工具必须回去登记**，那份有维护约定）；整套迁移流程走 x3-project 的 `.claude/skills/x2-to-x3-migration`。
5. **剩下的 Missing Script**：本例 prefab 有 466 处 `m_Script`、32 个 X2 脚本 GUID。⚠️ **别用 `RemoveMonoBehavioursWithMissingScript` 一把梭**——它无差别删，会误伤「X3 有等价、只是 guid 链断了、该修不该删」的组件（官方文档记了 `ExOutlineMix` 的实证反例）。按 X3 侧新写的 `Auto_` 绑定逐个重挂。
6. **多语言**：`localization_keys.tsv` 只是**参考译文**（X2 是 `LC_*`，X3 是 `TXT_*`，键体系不通用），正式走 `x3-translation-automatic`。

---

## 12. 一句话全流程

> **X2**：找到源 prefab → 拖进 `TFW_Logo` 场景 → **Unpack Completely** → 改成 X3 名字 → 拖回 `Assets/` → **Tools▸X2▸Prefab Asset Export** → 导出到 `D:\newX2\Copy\<名字>\`
> **X3**：整包（带 `.meta`）拷进工程 → 双击 prefab 确认图没白 → **git commit** → 选中 prefab 开 **Tools▸Prefab换皮** → 资源目录用 Copy Path 粘进去 → **预览**看清单 → 执行清理（等 1 分钟+）→ 确认报告 `断链 GUID：0`
> **收尾**：移到 `Res/UI/{Sprite,Prefab}/<模块>/` → 补根组件五件套 + Top 信息区 → 跑 `Tools▸X2 Migration` 各替换工具 → 重挂 `Auto_` 代码 → 走 X3 i18n

---
# Part C · 接线 / 注册 / 验证（⑥⑦⑧，工具全管不到）

## 14. ⑥ 接线：让 prefab 和代码对上

**双向，选一个方向**：
- **改 prefab 迁就代码**：读 `Auto_UIXxx.cs` 里的 `FindByFullPath("路径")` / `GetComponent<T>("路径")` / `AddListener(..., "节点名", ...)`，照着摆节点起名
- **改代码迁就 prefab**：prefab 拼好后用 X3 UI 工具**重新生成 `Auto_`**

⚠️ **框架对缺失节点静默容错**（`FindByFullPath` 返回 null、`AddListener` 仅报错）→ 少一个节点**不崩、不报错**，只是"那块永远不显示"。**这是最难发现的一类**，只能逐条核契约。

还要补两块 X3 界面骨架（X2 prefab 一定没有）：
- **根节点五件套**：RectTransform + UIConfig + Canvas(SortingOrder=11) + CanvasScaler(1080×1920) + GraphicRaycaster —— 不补，`UIBase.InitCanvas` 打开即 `MissingComponentException`
- **Top 信息区**：从 `UIActvLaborGacha.prefab` 整棵移植 `CentreOther/Animation/Top`（标题/倒计时/描述/btn_info），**别复用 X2 自带顶部骨架**（样式不符，会被打回）

## 15. ⑦ 注册：DK + i18n
- **DK**：`Display_*.asset` + `Path_*.asset` **双表同锚平行插**，键序 OrdinalIgnoreCase，校验 `keys[i]==values[i].key`（铁律见 [[reference_x3_client_resources]]）。DK 表多人共用 → **按 hunk 提，别整文件提**
- **i18n**：X2 `LC_*` 与 X3 `TXT_*` **键体系不通用**，`localization_keys.tsv` 只当译文参考，正式走 `x3-translation-automatic`；新错误码要录 `Text_ErrCode*`，漏了裸 key 上屏；**只填 cn/en 的话繁中客户端空白（繁中读 `zh` 列）**

## 16. ⑧ 验证六道关（缺一环别说"好了"）
```
① Unity Editor 编译过
② prefab 打得开、图不白、无 missing script 阻断保存
③ 起本地服 + GM 开活动
④ 完整重登（不点任何按钮）→ 数据就该在      ← 填充在 OnPostInit，重连不触发
⑤ 主链路走通一次（买 / 领 / 抽）
⑥ 外显逐项核（图标不重复、无占位数字）
```
⚠️ 中途从命令行/外部改过 `.bytes` 或图 → **必须完全关掉 Editor 重开**（热塞对运行中 Editor 无效，读的是已导入的 TextAsset）。

## 17. 🪤 每阶段典型翻车对照表

| 阶段 | 症状 | 根因 |
|---|---|---|
| ① 反查 | 界面主体正常，某类元素（特效/图标）全缺 | `assetPath` 字符串加载＝guid 扫描盲区，压根没搬 |
| ② 导出 | 到 X3 少东西 / 多一堆重复 | 路 A 丢字体 FontAsset；路 B 留 UNRESOLVED |
| ③ 落地 | **界面全空**，日志 `Empty bundle path for asset:` | 落点/名字改了，代码写死的 assetPath 找不到 |
| ③ 落地 | 全白图 | 只拷 png 没拷 `.meta`，GUID 重排 |
| ④ 清理 | 别的界面突然断链 | 被删副本在资源目录外还有人引用 |
| ⑤ 换件 | prefab **存不下去** | `LayoutRtlAlignment` missing 阻断 `SavePrefabAsset` |
| ⑤ 换件 | 满屏 `LC_XXX` | 本地化脚本被剥、Key 没回填 |
| ⑥ 接线 | 某块**永远不显示**、按钮点了没反应 | 节点路径对不上，框架静默容错不报错 |
| ⑥ 接线 | 一格里图标全一样 + 占位数字（如 555） | **一个节点上叠了多个画图组件，只驱动了其中一个**（限时抢购 A 类翻车点：`BoxNormal/Card/Icon` 挂 TFWImage 底图 + 2 个 X2 item 组件，代码只设底图 sprite；正解＝调 item 组件的 `SetItem(itemId)`） |
| ⑦ 注册 | 图能显示但 DK 查不到 / 繁中空白 | DK 单表插了没插另一张；i18n 没填 `zh` 列 |
| ⑧ 验证 | 改了没生效、数据是旧的 | 外部改 bytes 没重开 Editor |

---
相关：[[workflow_p2_to_x3_asset_port]]（3D 资产/UI 迁移坑全集）· [[reference_x2_strong_consume_client]]（强消耗客户端速查）· `KB\方法论\活动程序开发\X3_马戏节扭蛋机_实现方案.md` · `x3-project\AIDocs\X2_to_X3_Migration\`（官方迁移文档集，权威）· `KB\换皮档案\X3\2026-07-22_限时抢购(X2搬运).md`（本案实战操作单）
