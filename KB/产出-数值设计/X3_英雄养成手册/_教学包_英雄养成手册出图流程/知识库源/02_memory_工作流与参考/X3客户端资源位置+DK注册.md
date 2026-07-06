---
tags: [kind/交接, domain/配置换皮, proj/X3, year/2026-06]
name: x3-dk
description: X3 client 仓里 .png/.prefab 实际位置，DK→GUID 注册的 asset 文件，tableResInfo.txt 名单陷阱，看图找 DK 的实操路径
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## ⚠️ client 仓美术图是 Git LFS 指针（2026-06-14 实证，反复读不到图的根因）
`C:\x3-project\client` 的 .png 大多是 **LFS 管理**：工作区里常只是 ~130 字节的指针文本(`version https://git-lfs...`)，**真图没下载**。症状：Read 读不到图/报不存在、PIL 也拿不到真像素、看不了别人的美术。
- 判别：`file <png>` 显示 `ASCII text` 或 `head -c 60` 见 `version https://git-lfs` = 指针；真图是 PNG 二进制（几 KB~MB）。
- 拉真图：`git lfs pull --include="<相对路径>"`（单张几秒；命令可能 exit 1 但文件已下载，看 `stat -c%s` 大小 >2000 即成功）。
- 我们自己新落仓的 png（如 ActvWorldCup/WC_*）是新加的真文件、不受影响，能直接读。

## X3 活动入口图标(ActvIcon)真规格 = 124×136 透明底自由形状物件（2026-06-15 实证修正）
⚠️ **推翻 2026-06-14 旧说"1024 满幅带背景非透明"——那是错的，反复犯糊涂的根源。**
实测真相（`git lfs pull` 后 PIL 直读）：
- **入库的真资产 = 124×136、RGBA 含透明、自由形状的主题物件图**。证据：`Spirits/Activity/img_Activity_icon_5.png`(金色双箭头) 和 `Spirits/ActivityImg/img_Activity_VD_icon_10.png`(夏日恋语花藤拱门) 都是 124×136、alpha extrema=(0,255)、透明底自由轮廓——**不是**满幅带背景的长方形缩略图。
- **图里不画圆/不画框**：列表里图标外那圈圆是 UI 层通用底框(`UIActivityListItem.mIconBgImage`)自动套的，所有活动共用，不在图里。把圆烤进图=双重圆+形状错（世界杯返工根因）。
- **出图规格**：主体居中、四角透明、奇幻半厚涂、与现有 `img_Activity_*icon_*` 同风格；**生成走高分辨率(1024)再缩到 124×136**（直接按 124 出会糊——旧note唯一对的一点），用 x3-media `activity_icon` 类型(透明底硬规则)。
- ActvOnline 表入口图标列 = **col22**（DK_img_Activity_*_icon_*，1-indexed；=脚本0-indexed col21 ActvIcon）；col23=bg(ActvImg)；col34(0-idx col33)=TopResource 右上角资源栏显示道具(`a|b`竖线分隔)。
- ⚠️**DK 双命名空间(2026-06-16 世界杯实证)**：**HUD入口图标(ActvIcon)解析走 `Path_Activity.asset`，道具图标(Item.DK_Icon)走 `Path_Item.asset`，两套独立 namespace**。想拿"道具图当HUD用"(如累充HUD用券图)：直接把 ActvIcon 列填道具 DK **不显示**(跨namespace找不到)；解=把该活动现用的 Activity-namespace DK 的 objPath **重指**到那张 png(Path_Activity 里改一行 objPath，配置列不动)，或在 Path_Activity 另注册一个新 DK 指向该 png。
- 💡 **反射**：对"某配置/资产该长啥样"犯糊涂时，**别空想/别靠旧note**——直接 `git lfs pull` 一个现成能用的同类活动(如夏日恋语)资产 PIL 直读+Read 看图反推，眼见为实。本条就是空想了一整会话(圆形该不该渲染、要不要写 UICircleGraphic.cs)后，靠看 img_Activity_VD_icon_10 才拉回正轨。
- ⚠️ **x3-media activity_icon worker 不做透明化(2026-06-15 两次实证)**：worker 对 activity_icon **多半直接吐白底图**(四角 alpha=255)，`transparency_method`/双底差分指令它**不一定执行**。结论：**实体物件图标(奖杯/箱子等)别跟 worker 较劲重派，本地一步抠白更可靠** → 用 `C:\ADHD_agent\scripts\flood_remove_white_bg.py`(四边洪水填充抠纯色底+可选 `--fit 124x136` 居中，保物件内部白)。验收必查四角 alpha=0、偏白边缘≈0。
  - ⚠️⚠️ **洪水抠白的命门**：它移除**与边缘相连**的背景白。若主体本身有白色部分且**与背景连通**(如玻璃/高光材质的白色足球顶、贴边白元素)，会被一起抠成透明/破洞(2026-06-15 世界杯足球被吃穿，调 thr 也救不了——玻璃高光是纯 255 白、与白底同色，颜色上无法分离)。
  - ✅ **玻璃/白高光主体的根治法 = 洋红幕重出 + 色键扣图(2026-06-15 验证有效)**：白底扣不开时，**别本地硬抠、别指望 worker 透明化**，改派 x3-media `general` 图生图：以原图为参考，让模型把同一主体**原样搬到纯洋红 #FF00FF 背景**(洋红离金/白/绿都远)，再用 `C:\ADHD_agent\scripts\chroma_key_remove.py --key magenta --fit 124x136` 色键扣幕(含去紫边+羽化)。白高光得以完整保留。绿幕同理但主体含绿(草)时别用绿。
  - ⚠️ rembg 语义抠图：本机 2026-06-15 **import 卡死**(onnxruntime 首次加载不返回)，别依赖；要用先单独验证能跑通。

## ⚠️ 改 PNG/sprite 后"没生效"=客户端缓存（2026-06-16 荣耀金币缩放实证）
换了仓库里的 .png（如缩放图标），**运行中的客户端/已构建包不会自动刷新**——跟配置 .bytes(pull+重启即更新)不同，sprite 要：① Unity 编辑器里**右键该 png → Reimport**（重新导入 sprite），或 ② **重建客户端/重打图集**(sprite 多打进 atlas，build 时烘焙)。**只 git pull 仓库、看运行中的旧包/旧图集 = 还是旧图**。所以"图标改了但游戏里没变"先别怀疑没改对——`PIL` 量一下仓库里 png 的真实占比(见下条)确认文件已改，再让客户端 reimport/重建。

## ⚠️ reimport 后图标还显白框 ≠ 缓存问题 = 图本身白底没抠真透明（2026-06-23 世界杯荣耀兑换所实证）
"改了/reimport 了 HUD 图标还是白底方块" 别只往缓存/AB想——**先量 png 的 alpha 直方图**(`全透明% / semi% / opaque%`)。activity_icon 常见根因=**图本身带白色不透明背景**(x3-media activity_icon worker 多半吐白底不做透明化，见上「worker 不做透明化」)。实测 WC_Exchange_Icon：全透明仅 8.8%、全不透明 91.2%、中间行左右边缘采样 `(254,254,254,255)`=纯白不透明 → 奖杯/钱袋贴在白卡上，reimport 当然没用(png 内容问题非缓存)。
- **判别**：`px[x,y][3]` 直方图；中段边缘像素 alpha=255 且 RGB 近白 = 假透明白底。
- **修(实体物件图标·奖杯/箱子/币)**：本地 `C:\ADHD_agent\scripts\flood_remove_white_bg.py <png> --out <test>` 洪水抠白(KB 首选·比 GRFal worker 快可靠)→量结果(透明%↑·四角/边缘 alpha=0·残留近白≈1-2%=主体高光正常)→看图确认主体无破洞→覆盖原图。白高光主体被抠穿才上 GRFal remove_bg/洋红幕(见上)。124×136 尺寸保持。
- **坑**：该类 png 多是 **Git LFS** 管理(commit 显示 `2 insertions/2 deletions`=只改 LFS 指针·二进制 push 时上传)。不在 atlas(grep `.spriteatlas*` 确认)则 dev/Editor reimport 直读即生效·无需重建 AB。

## ⚠️ jolt 导表 ≠ 下发 DK 资源（两条独立管线，2026-06-16 世界杯应援表情诊断）
"配置有 / dkasset 也写了，但 DK 进不去客户端"——根因几乎都是**只跑了 jolt、没重建客户端**。X3 资源进客户端走**两条互不相干的管线**：
- **配置表**（如 Emoticons 行）→ `jolt 导表`(tsv→ProtoGen/*.bytes) → 配置热更，pull+重启即生效。jolt **只管这条**。
- **DK 注册（Path_*.asset）+ 它指向的二进制（.png/.gif.bytes/prefab）** → **客户端资源构建**（Unity 打 AssetBundle / 重出包），**jolt 完全不碰**。
- 后果：只跑 jolt → 客户端"知道"有第 N 行表情、Res=`DK_WC_xxx`，但解析 DK 时包里**根本没这批资源** → 空白。这≠配置错，是没出客户端资源。
- 排查顺序（确认源仓全对后别再翻配置）：表行✅→Path_*.asset 的 keys/values **逐下标平行**✅(见上文"索引平行铁律")→二进制文件+.meta 齐✅→已 commit/push✅ ⇒ **剩下就是没重建客户端**，归客户端/程序出资源包，不是你 jolt 能代替的。
- **编辑器自测让 DK 生效**：① `Assets>Refresh`(Ctrl+R) 让 Unity 发现 git 拉来的新文件 → ② 右键目标目录 Reimport → ③ **重启 Unity**(Path_*.asset 是加载进内存的 DK→路径字典，手改文本后旧字典还在内存里，Reimport 不一定够，重启最稳) → ④ 重进 Play。⚠️前提:看项目 AssetBundle 模式开关——模拟/直读模式上面就够;读真实 AB 模式则编辑器也得先打 AB。
- **★"DK 文件全对但运行时显示旧图/不显示" = 客户端读旧 AB 包，新 DK 没烘进去（2026-06-23 深海转盘背景实证）**：典型特征=**同一活动里老 DK 显示对、新加的 DK 不显示**（深海转盘"盘面深海皮对、背景 turntable_bg 错"——盘面 DK 同事早期入、已烘进 dev 时打的 AB；背景是后加的 feature 新 DK、没进 AB）。**判据**：Path+Display+png+guid 全对、`LoadFromDisk`→`Save And Generate Code` 也做了、重启 Play 还不显示 → 不是配置/DK 文件问题，是**客户端在读真实 AB 模式、新 DK 没在包里**。**解**：切 Editor 模拟/直读模式（绕 AB），或重打 AB 把新资源烘进去。别再翻配置/重注册 DK（文件层没问题）。
- **★为什么"有的 DK 不用打 AB、有的要"（2026-06-23 用户追问·接管 keypoint）**：不是 DK 特殊，是**在不在你用的那个 AB 包里**。**dev 分支的 DK** 早经过构建打过 AB → 拉下来包里就有、直接显示、不用动；**feature 分支新加、还没合 dev / 没走出包的 DK** 不在任何 AB 包里 → 本地自测必须手动打 AB（`Tools>Project Builder>AssetBundle>Build Asset Bundles`，先 Clear 再 Build）或切直读模式。**合 dev 走正式构建出包后，feature 新 DK 就和老 DK 一样进 AB 包，谁拉都能看**。X3 打 AB 菜单路径 = `Tools/Project Builder/AssetBundle/`（Build/Clear/Profile Asset Bundles）；开发自测的快速直读模式开关代码里没明搜到，问程序。

## ⚠️ 图标主体占比规范（道具/货币 icon，2026-06-16 荣耀金币实证）
AI 生的 icon 常**主体满画布(占比 90%+)**，游戏里显大、跟现有道具不协调。**标准占比≈70-75%**(参考同类：尼罗猫眼石币 `ItemIcons/icon_global_Egypt02.png` = 69%×75%)。规范化法(同[[project-x3-worldcup-activity]]头像框48队/avatarframe那套)：①`alpha.point(lambda x:255 if x>=30 else 0).getbbox()` 取**真实主体bbox**(先阈值化排抗锯齿淡像素,否则 getbbox 被噪点骗成满画布) ②裁出主体 ③等比缩到 max边≈73%×画布边(256→~188px) ④居中贴回原尺寸透明画布。验收四角 alpha=0。**纯资源改图(同文件名/DK/meta)不用改配置/导表,只 commit client png**。

## 实际资源（.png）位置

| 类别 | 路径 |
|------|------|
| **活动图（节日 bg/icon/btn/box）** | `C:\x3-project\client\Assets\Res\UI\Spirits\ActivityImg\` 和 `ActivityImg_Download\` |
| 礼包面板图 | `C:\x3-project\client\Assets\Res\UI\Spirits\Pack\` |
| 视频 | client 仓内 video 子目录 |

实际 .png 文件名 = DK 去掉 `DK_` 前缀。
- `DK_img_Activity_VD_bg_13` → `img_Activity_VD_bg_13.png`
- `DK_img_Activity_summer_bg_10` → `img_Activity_summer_bg_10.png`
- `DK_img_gift_bg_28` → `img_gift_bg_28.png`

## DK 注册位置（X3 项目实际用的新系统）

| 文件 | 内容 |
|------|------|
| **`C:\x3-project\client\Assets\Editor\Config\DisplayKey\Display_*.asset`** | **★真源/编辑源**（entry 格式：`key:`(无DK_前缀) `type:` `desc:` `guid:`(指资源.meta) `exportCode:0`）。Unity「生成dk」(Ctrl+T / Save And Generate) **以它为准重新生成 Path_*.asset**。**不是旧系统！**（推翻 2026-06-14 旧记录） |
| **`C:\x3-project\client\Assets\Res\Config\DisplayKey\Path_*.asset`** | **运行时映射**（`H1DisplayPathAsset`，`DK_`前缀→objPath，keys/values 平行）。**由 Display 生成**；runtime/dev 直接读它解析 DK。Path key = `DK_` + Display key |
| `C:\x3-project\client\Assets\Editor\Config\tableResInfo.txt` | DK 汇总名单（**过期**：实际硬盘 .png 数量 > 此文件列出的 DK 数量） |

### ⚠️⚠️ 只写 Path、不写 Display = 不稳，一次「生成dk」就被清（2026-06-22 世界杯 278 DK 全丢事故）
**事故**：commit `e255ed352f9`「生成dk」(zhangli) 是一次 Unity **全量重导出**——以各 `Display_*.asset` 为真源重生成所有 `Path_*.asset`，把**只手写进 Path、没登记 Display** 的 DK **全部静默清掉**（净删 278 个，横跨 Path_Activity/Emoticons/Item/Memory/MiscIcons/Personalise/Role/Video 8 个文件）。世界杯整套外显(队徽48/队伍板48/头像框48/应援表情96/开箱兑换基金通行证入口图/足球宝贝Hero40皮肤/各类道具图标 共259) + 其他节日连带(深海/情人节/夏日/埃及/纪念卡/视频 19)全中招。
- **根因**：世界杯及多个节日当初都用「直接手编辑 Path_*.asset」快捷做法注册 DK（见本文件末「DK 注册即用」段），**漏了 Display 这一步**。Display 里没有 → 重导出按 Display 为准就删了。对照：酒馆头像框(tavern01-03)做对了——`3ab88152c5a` 先登 Display + `f38dc404494` 补登 Path，两边都有 → 同次重导出**保住了**。
- **铁律**：新增 DK **必须同时写 Display(真源) + Path(运行时)**，缺 Display 早晚被「生成dk」清。或：重导出前先 `git pull` 同步最新 Display。
- **诊断**：`git show <生成dk提交> --numstat | grep Path_` 看哪些 Path 被大改；`git show <commit> -- <file> | grep '^-    - key:'` 列被删 key；净丢 = 父提交 keys - 当前 keys。
- **恢复法（2026-06-22 实证，脚本 `scratchpad/restore_e255_dk_v2.py`）**：① 从 `<提交>^:<file>` 父提交取回 key→objPath（objPath 可能含空格/括号，正则用 `(.+)` 不是 `(\S+)`）② **Path 用「父提交锚点法」纯插入**：把每个丢失 key 插到「它在父提交里的最近前驱-且当前仍在-的 key」之后（父提交本身是 Unity 排好序的，照此插即保持有序）③ **Display 末尾追加**（key 去 DK_ 前缀 + 从 `<client/objPath>.meta` 读 guid + type + exportCode:0；Display 是 list，顺序无所谓）④ **纯插入、绝不重写现有行**（整段重建会改坏历史损坏条目，如 underwear_icon33 的 objPath 被拆成两行 `...icon33`+`        1.png`，重建会丢续行）⑤ 每文件**自适应行尾**(LF/CRLF，别硬编码，否则混用)⑥ 校验：diff 纯增零删 + keys≡values 平行 + 每个 objPath 文件真实存在。
- **⚠️ Path 排序不是 Python `str.lower()`**：是 .NET 文化敏感排序，标点(`_`/`(`/`)`)collation 复杂（如 `goldbag(small)` 排在 `(small_1)` 前，`_`≠最低标点）。**别试图复刻比较器**——用上面的「父提交锚点法」绕开。
- **gdconfig 子模块脏时 x3-project 提交被 pre-commit 钩子拦**（`uncommitted gdconfig content changes block`）——子模块有在途改动时父仓提不了，别绕钩子，等在途状态清掉再提交。

### Path_*.asset 文件格式（YAML）

```yaml
MonoBehaviour:
  m_Name: Path_Activity
  type: Activity
  paths:
    keys:                              # DK 名列表（按字母序）
    - DK_img_Activity_summer_bg_11
    - DK_img_Activity_summer_bg_12     # ← 新加
    - DK_img_Activity_summer_bg_2
    ...
    values:                             # 对应 path 列表（按 keys 同序对应）
    - key: DK_img_Activity_summer_bg_11
      objPath: Assets/Res/UI/Spirits/ActivityImg_Download/img_Activity_summer_bg_11.png
    - key: DK_img_Activity_summer_bg_12   # ← 新加
      objPath: Assets/Res/UI/Spirits/ActivityImg_Download/img_Activity_summer_bg_12.png
    - key: DK_img_Activity_summer_bg_2
      objPath: Assets/Res/UI/Spirits/ActivityImg_Download/img_Activity_summer_bg_2.png
    ...
```

**`keys` 和 `values` 是两个并列列表，按索引对应**。手工编辑必须同时在两处插入对应内容，否则 DK→path 映射错位会导致整批 DK 加载错误图片。

### Unity 编辑器入口

菜单 `Config / Display Key`（快捷键 **Ctrl+T**），打开 `DisplayKeyPanel.cs` 编辑窗口。
- 入口源码：`Assets/GameMainLogicEditor/Tools/DisplayKey/DisplayKeyPanel.cs`
- 在面板里添加 DK 名 + 拖入 sprite → 自动写入对应 Path_*.asset
- 比手工编辑 yaml 更安全（不会错位）
- **★刷新「已 push 的新 DK」让运行时生效的正确按钮顺序 = 先 `LoadFromDisk` → 再 `Save And Generate Code`**（2026-06-23 转盘背景实证）：面板初始内存是旧状态，先 LoadFromDisk 把磁盘最新（含新 push 的 DK）灌进内存，再 Save 才不会倒退。**绝不能跳过 LoadFromDisk 直接 Save**——旧内存覆盖磁盘 = 清掉新 DK（同 e255 全量重导出机制）。症状：DK 文件/guid/Path/Display 全对但运行时 ActvImg 显示旧图 = 字典没刷新。

### 手工命令行编辑（无 Unity 时的应急方案）

如果只是加 1 个 DK（紧急修 BUG）可以直接编辑 Path_Activity.asset：
1. `keys:` 段按字母序找邻近位置，加 `    - DK_xxx`
2. `values:` 段找邻近 entry，加 `    - key: DK_xxx\n      objPath: Assets/...`
3. 两段顺序必须一致；2026-05-27 落 `DK_img_Activity_summer_bg_12` 实测可行（x3-project MR !224）

## 批量注册 DK（脚本化，2026-06-14 世界杯96个实证）

一次注册几十~上百个 DK（如 48 队×2）别手工，按 memory 的"两段末尾同序追加"写脚本：
1. 落仓：图拷进 `Spirits/<目录>/`，每张配 .meta（抄同目录现成 sprite meta，正则换 `guid`+`spriteID` 为 `uuid4().hex`）。
2. 注册 `Path_Activity.asset`（活动类资源都进这个）：定位 `    values:` 行索引 vi → keys 段在 `lines[:vi]` 末尾插 N 个 `    - DK_xxx` → values 段在 EOF 前追加 N 组 `    - key: DK_xxx`/`      objPath: Assets/Res/UI/Spirits/<目录>/xxx.png`，两段同序。先备份 .asset.bak。
3. **必校验**：keys 列表 == values 的 key 列表（平行一致），且 `git diff --numstat` 应纯增不减（删=动了别人的行）。
   - ⚠️⚠️**索引平行铁律(2026-06-16 荣耀金币血泪)**：`Path_*.asset` 是 Unity SerializedDictionary，**keys[i] 与 values[i] 按下标配对，不是靠 values 里的 `key:` 字段**。所以新 DK 必须在 keys 段和 values 段**插在同一个锚 key 之后(同位置)**；若两段用不同锚(如 keys 在 EmoteChest 后、values 在 AvatarFrameChest 后)→ 插入点错位 → 新 DK 按下标指到隔壁条目的图。**症状**：`item.DK_Icon=DK_WC_GloryCoin` 却显示成宝箱(=被错位指到了 EmoteChest 的 png)，keys/values 条目数还相等(566==566)、objPath 字面也对、骗过粗检。**单个插入务必同锚；批量末尾追加天然同序所以安全**。校验要逐 index 比对 `keys[i]==values[i].key`，不能只比条目数。修法=把 values 段错位的两对调换顺序对齐 keys 段。
4. DK 命名 = `DK_` + 文件名去 .png（如 `DK_WC_Badge_BRA`）。
- 实战 commit f46cd774b2e：96 DK 一次入表，1103→1199 平行一致，diff 288 增 0 减。client 直接 push dev_festival（无 Unity 也可，命令行追加比 Ctrl+T 更可控、且不会像全量重导出那样删别人的）。

### ⚠️⚠️ 末尾追加"安全"有前提：keys 必须在排序里单调，否则 Unity 编辑器反序列化静默丢弃（2026-06-16 世界杯应援表情血泪，推翻"末尾追加天然安全"）
`Path_*.asset` 的 `paths` 是 **`SerializableSortedDictionary`（有序字典）**。runtime(built client)按平行数组建 dict、顺序无所谓；**但 Unity 编辑器侧反序列化要求 keys 按它的排序递增，遇到第一个"比前一个 key 小"的乱序条目就从那里开始把后面全丢掉**（不报错、Library 也正常重导）。
- **触发条件**：末尾整块追加的 DK 里有**两个交替的命名家族**——本次 `DK_WC_xxx`(动图) 和 `DK_icon_global_WC_xxx`(icon) 逐队交替 → 排序键在 `w`/`i` 之间来回跳 → 非单调 → 编辑器丢掉整批 WC（文件里有、`Inspector` 里没有、运行时 `displayKey X not found`）。**Path_Activity 那 96 队徽没事，是因为 `DK_WC_TeamPanel_*`/`DK_WC_Badge_*` 同 `dk_wc_` 前缀、单调不跳**——所以"末尾追加"只对单调 key 安全。
- **症状链**：配置✅+Path_*.asset 文件里 keys/values 平行✅+png 已导入 GUID 有效✅+已 commit✅，但运行时 `not found` 且重启无效 → **点 asset 看 Inspector：缺的 key 不在列表 = 中招**。
- **Unity 的排序 = OrdinalIgnoreCase**（实证：`sorted(keys, key=str.lower)` 能复现现有条目顺序；`sorted()` 纯码点 ordinal 不匹配，**别用 Python 默认排序**）。
- **修法（不删数据，只重排位置）**：解析 keys + values(key,objPath) → `sorted(pairs, key=lambda kv: kv[0].lower())` → 重写两段同序 → 校验 `keys==values` 平行 + `keys==sorted(keys,key=str.lower)` + 数量不变 + git diff 纯重排。reimport+**重启 Unity**(清静态 DK 字典缓存)→ Inspector 验缺失 key 回来。⚠️中招后**别点 Ctrl+T 重新导出**(此时 Unity 内存已丢该批，一存就把它们永久删出文件)。
- **预防**：批量末尾追加后，最后统一对**整个 keys/values 按 lower() 排一次序**再落仓（= Unity 自己 Ctrl+T 导出的顺序），一劳永逸。

## tableResInfo.txt 不是 ground truth

2026-05-26 排查夏日恋语图时：tableResInfo 只列 5 张 summer_bg（1/2/8/9/10），实际硬盘 11 张（bg_1 到 bg_11 全有）。**不要把 tableResInfo 当作"美术出过几张图"的判据**，直接 `find / Glob` .png 文件最可靠。

## X3 节日 DK 命名约定

| 节日 | DK 前缀 | 例 |
|------|--------|----|
| 情人节 | `VD_` (Valentine's Day) | `DK_img_Activity_VD_bg_13` |
| 夏日恋语 | `summer_`（**不是 `summer_love_song_`**） | `DK_img_Activity_summer_bg_10` |
| 圣诞 | `Christmas_` / `xmas_` | |
| 万圣节 | `halloween_` | `DK_img_Activity_halloween_bg_16` |
| 尼罗（埃及节）| `Egypt_` / `MF_`（Mermaid Fest？）| `DK_img_Activity_Egypt_bg_15` / `DK_img_Activity_MF_bg_13` |
| 新春 | `spring_` / `springfestival_` | `DK_img_Activity_spring_bg_3` |

## 看图 / 找 DK 操作

```bash
# 看具体图（在对话里用 Read 直接读 .png 会内联显示）
find C:/x3-project/client/Assets -iname "*Activity_summer_bg*.png" 2>/dev/null

# Explorer 打开浏览
explorer.exe "C:\x3-project\client\Assets\Res\UI\Spirits\ActivityImg_Download"

# 查某 DK 是否已注册（在 tableResInfo / 任何 Display_*.asset 出现即注册）
grep -rn "DK_img_Activity_summer_bg_1" C:/x3-project/client/Assets/Editor/Config/
```

## 实战经验

- **配置写新 DK 前先看 client 仓有没有 .png**：硬盘上有就能用，不在硬盘上得让美术先出图 + 走 [[feedback_dk_resource_workflow]]
- **tableResInfo.txt 看起来缺图时**：去 ActivityImg/ActivityImg_Download 目录用 `find -iname` 真实搜，名单可能是过期版本
- **跨节日复用 DK 是 BUG 信号**：节日活动用了别节日前缀的 DK（如夏日活动用 `VD_*`），90% 是没换图，需要确认美术

## ⚠️ 踩坑：Unity 全量重导出 Path_*.asset 静默删掉别人手工注册的 DK（2026-06-05）

**现象**：合并/上传美术后，一批节日资源「掉了」——背景/ICON/HUD 入口图标空白，且**跨多个节日**（夏日 + 尼罗同时掉）。

**根因**：有人在 Unity 里 Ctrl+T 重导出 DisplayKey 后整文件提交 `Path_Activity.asset`（commit msg 常见「XXX美术上传」「重新导出displaykey配置」），但他的本地 Unity 工作区 DisplayKey 状态是**过期的**（早于别人后来手工/单独提交追加的节日 DK）。这份全量重导出会**覆盖整个 keys/values 段、静默删掉**那些较新的注册行。`png 文件还在硬盘上，只是 .asset 里的 key+objPath 两行没了` → 加载失败表现为资源空白。

实战：`046c519e874 海妖美术上传`(龚亮) 一次删了 7 个 DK（`VD_icon_9/10`、`Egypt_icon_11/12`、`summer_bg_12`、`VD_bg_18`、`ActvNewQueue_Hud`），全是 linkang `b29dc46f5cb`+team 早先单独提交注册的。

**「掉了」的资源 → 配置字段定位**（先确认 DK 名，再查谁引用它）：
- 礼包 ICON → `Pack.Icon`(col27) / `ChainPack.Icon`(col3) / `PackTypeInfo.Icon`(col4)；装饰阶梯礼包三处都要查（见 [[reference_x3_pack_tab_icon]]）
- 礼包背景 → `Pack.MainBg`(col30) / `BottomBg`(col31)；`Pack.Head`(col25)=主界面入口图标
- **拜访礼包面板小图** → `ActvVisitPack.DK_PackIcon`(col8)
- **「HUD」=活动主界面入口图标** → 多在 `ActvOnline` 表（用户口中拜访礼包「HUD 掉了」常指这个，不是 Pack.Head）

**诊断方法（git pickaxe 定位删除提交）**：
```bash
# 1. DK 当前是否还注册（key=0 即丢了）
grep -c "key: DK_xxx$" client/Assets/Res/Config/DisplayKey/Path_Activity.asset
# 2. 谁删的（-S 列出改变该字符串出现次数的提交，最新一条+当前缺失=删除者）
git log --oneline -S "DK_xxx" -- client/Assets/Res/Config/DisplayKey/Path_Activity.asset
# 3. 该提交一次删了哪些（看全貌，别只修用户报的那几个）
git show <commit> -- .../Path_Activity.asset | grep -E '^-    - DK_'
# 4. png 还在不在（在=只需补注册行，不用重新出图）
git show <commit>^:.../Path_Activity.asset | grep -A1 "key: DK_xxx$"   # 取回 objPath
```

**修复（2026-06-05 实测安全手法，覆盖"按字母序插"的旧说法）**：
- 真正的运行期不变式是 **`keys[i] == values[i].key` 按 index 平行对应**（验证：提 keys 列表 + values 的 `- key:` 列表，两者完全相等）。runtime 把两个平行数组建成 dict 查，**顺序不影响功能**。
- ⚠️ 文件**不是 Python ordinal 排序**（`keys==sorted(keys)` 为 False）——Unity 用的是大小写不敏感/.NET 式排序，**别试图复刻字母序插入**（bisect 会算错位、还可能打乱已有行）。
- ✅ 安全做法：**把 N 个 `key` 追加到 keys 段末尾（`values:` 行之前）+ N 个 `key/objPath` 追加到 values 段末尾（EOF 前），两段同序**。这样既保住 index 对应（老条目 0..n-1 不动、新条目 n..n+N-1 在两段同位），diff 又小又好审。下次谁 Unity 重导出会自动重排，无副作用。
- 取 objPath：`git show <删除提交>^:.../Path_Activity.asset | grep -A1 "key: DK_xxx$"`。png 在仓库就只补注册行，不动美术。
- 坑：文件里可能有**历史损坏条目**（如 `DK_img_Activity_underwear_icon33` 的 objPath 被拆成两行 `...icon33` + `        1.png`），解析 values 时按"只匹配 `- key:` 行定位"绕过它，**别去修**（不是你的活）。
- client 仓 protected dev → feature branch + MR（[[workflow_x3_protected_branch_mr]]，注意 MR title 用 ASCII 否则 500）。提交只 `git add` 目标 .asset，别带进工作区里别人的 prefab WIP。

**预防**：禁止「XX美术上传」式整文件全量重导出 Path_*.asset；新增 DK 应只追加自己那几条 key+value，或重导出前先 `git pull` 同步最新注册。关联 [[workflow_x3_merge_conflict_audit]] 同属「整文件覆盖丢别人改动」家族。

## ★多agent共享client仓·DK注册改完立即commit(2026-06-23深海HUD实证)
- **坑**:并发的另一个agent对同分支做 `git pull` 快进 / `git add -A` commit → **pull FF 把我未提交的 Path/Display 编辑整段冲掉**(working tree+index都没了);幸运的是他 `git add -A` 把我 **untracked 的 png/meta 扫进了他的提交**(反而幸存·meta guid保留)。
- **教训**:共享client仓多agent时,**DK注册(Path+Display)改完马上 commit**,别留working tree过夜;被冲掉后=pngs在盘上(untracked幸存),只需**复用现存meta guid重注册Path/Display**(脚本`scratchpad/rereg_hud.py`:读meta guid+排序插Path跳已存在+追加Display跳已存在)再立即commit。
- **★双补扛Ctrl+T实证**:我9 HUD+拼图封面+深海框+纪念卡 全 Display+Path 双补 → 用户Ctrl+T Save全量重导出后**一个没掉**(Display是真源·重生成Path含它们);**只Path不Display的早被清**(铁律再验证)。
## ★Ctrl+T Save「净删」判定:看key集合set diff·别只看numstat(2026-06-23)
- 全量重导出后 `git diff --numstat` 某Path文件显示如 19增/20删(净-1)≠丢了DK——多是**重排(删旧位+加新位)+空行/格式差**。**真丢判定** = `before_keys(git show HEAD:file) - after_keys(working) 的set差`;set差为空=纯重排没丢(本次Path_Personalise/Role/Emoticons numstat均-1但set差=0=没丢)。
- **Save重排要不要提交**:功能不需要(runtime读Path平行数组·顺序无关·DK已在各自commit);多agent并发时**别提交大范围重排**(动别人模块Path易冲突)·想锁Unity规范序才提交。丢弃=`git checkout --`回干净态·已commit的DK不受影响。

## ★DK 注册即用，dev 不过包（2026-06-22 世界杯铭牌实证）
- **X3 dev/Editor 走 LocalAsset 直读 AssetDatabase**：新图注册进 `Path_*.asset`(DK→objPath)+Unity 导入(GUID 解析正常)后，**Editor Play / 本地 dev 直接能加载**，**无需 AssetBundle 重建**。重建 bundle 只对「打出来的独立/移动客户端」才必要(运行时走 BundleManager 查 manifest，见 ResourceMgr/AssetMgrImpl.AB/BundleManager)。bundle 全量重建入口=`Tools/Project Builder/AssetBundle/Build Asset Bundles`(TFWEditor.X3Builder.BuildAssetBundles)。
- **验证 DK 是否生效(无需 Play)**：`scripts/client.py --port <Editor> invoke --type TFW.DisplayKeyExtension --member ToDisplayKeyAssetPath --kind call --args "DK_xxx"` → 返回正确 objPath 即注册成功(见 [[DebugUtils]])。
- **`sValidDisplayKeys` 不是运行时门**：`DisplayKeyExtension.ToDisplayKeyAssetPath` 里 `#if UNITY_EDITOR` 的 "未被配置表使用或导出到代码" 校验**仅当 `OpenDisplayKeyValidation()` 被调用(DK 审计工具)时才生效**；正常 Play/Editor 下 `sValidDisplayKeys==null`→跳过，DK 直接按 Path_*.asset 解析。
- **直接手编辑 Path_*.asset 注册 DK（无 Unity Ctrl+T）即可**：按单锚平行插 keys[]/values[] 段(见 [[project-x3-worldcup-activity]] v0.37 注册脚本)，Unity 重导后 DisplayKey 系统读取生效。

## ★DK 入库后需 Ctrl+T Save（2026-06-23 用户嘱·通用）
手编/脚本注册 DK 进 `Path_*.asset`(+`Display_*.asset`) 后，**在 Unity 里 Ctrl+T(DisplayKey 面板) Save 一下**让注册正式生效/持久化（编辑器内存的 DK 字典靠这个刷新）。⚠️Ctrl+T=全量重导出→Save 前必 `git pull` 同步最新，否则静默删别人后加的 DK（e255 事故同源）。

## ★坑：DK 已注册但 `exportCode:0` → 代码用 `DisplayKeyConfig.DK_xxx` 编译报 CS0117（2026-06-23 队列礼包实证）
`Scripts/Config/DisplayKeyConfig.cs` 是**自动生成**的常量类(`public const string DK_xxx = "DK_xxx"`)，**只为 `exportCode: 1` 的 DK 生成常量**。DK 在 `Display_*.asset`/`Path_*.asset` 注册了、PNG 也在，但若 `exportCode: 0`(默认)，`DisplayKeyConfig` 里就**没有**对应常量 → 代码写 `DisplayKeyConfig.DK_xxx` 报 `CS0117: 'DisplayKeyConfig' does not contain a definition for 'DK_xxx'`。整个 CardCollectionV2 家族(195个)全是 exportCode:0=都不导出，靠 DK **字符串**用。
- **判别**：`grep -A4 "key: <dk名>" Display_*.asset` 看 exportCode；`grep -c "<dk名>" Scripts/Config/DisplayKeyConfig.cs`=0 即没生成常量。
- **修法（推荐·一行·零风险）**：DK 取图的 API(如 `ItemUnitView.SetIcon(string)`→`UIHelper.SetImageWithDisplayKey`)吃的就是 **DK 字符串**，且 `DisplayKeyConfig.DK_xxx` 常量值也只是 `"DK_xxx"`——直接传字符串字面量 `SetIcon("DK_img_card_v2_new_queue")` 等价，编译立即过，无需 Unity 重生成。
- **备选（要常量才用）**：Display 条目 `exportCode:0→1` + Unity Ctrl+T Save 重生成 DisplayKeyConfig.cs。⚠️Ctrl+T=全量重导出有 e255 删别人 DK 风险(见上「DK 入库后需 Ctrl+T Save」)，且为单个 DK 破例导出跟同族不一致——能用字符串就别走这条。

## ★坑：工作区 .meta 纯 guid 改动 = Unity 重导 churn·别提交（2026-06-23 深海节实证）
多 agent/分支来回切时，client 仓常冒出一批 `.meta` **只改 `guid:` 那一行**(别的没动)的未提交改动；同文件**每次切分支新 guid 都不一样**(随机重滚)=Unity 反复重导入触发，非有意改。**危险**：老 guid 多被 prefab/mat 引用→**一旦提交引用就断**(资产 missing 丢图/丢材质)。判别:`git diff <meta>` 只有 guid 一行变 + 资产是真文件(非LFS指针)。**处理:别 commit·别在 Ctrl+T Save 时连带提交→`git checkout -- <meta>` 还原基线 guid**。
