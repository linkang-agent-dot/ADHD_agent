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
