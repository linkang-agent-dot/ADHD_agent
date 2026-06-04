---
name: x3-dk
description: X3 client 仓里 .png/.prefab 实际位置，DK→GUID 注册的 asset 文件，tableResInfo.txt 名单陷阱，看图找 DK 的实操路径
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

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
| **`C:\x3-project\client\Assets\Res\Config\DisplayKey\Path_*.asset`** | **真正用的注册表**（`H1DisplayPathAsset` 格式）— `Path_Activity.asset` / `Path_Animator.asset` 等按类分 |
| `C:\x3-project\client\Assets\Editor\Config\DisplayKey\Display_*.asset` | **旧系统，已不维护** — 之前 grep summer_* 在这里 0 命中（不要再看这）|
| `C:\x3-project\client\Assets\Editor\Config\tableResInfo.txt` | DK 汇总名单（**过期**：实际硬盘 .png 数量 > 此文件列出的 DK 数量） |

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

### 手工命令行编辑（无 Unity 时的应急方案）

如果只是加 1 个 DK（紧急修 BUG）可以直接编辑 Path_Activity.asset：
1. `keys:` 段按字母序找邻近位置，加 `    - DK_xxx`
2. `values:` 段找邻近 entry，加 `    - key: DK_xxx\n      objPath: Assets/...`
3. 两段顺序必须一致；2026-05-27 落 `DK_img_Activity_summer_bg_12` 实测可行（x3-project MR !224）

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
