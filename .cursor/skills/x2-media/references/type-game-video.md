# 游戏视频制作（game_video）完整流程

从用户描述到输出 Unity 可用的视频，或为已有视频生成 C# 播放代码的完整工作流。

---

## 前置条件

1. **项目地址**：从 `config.json` 读取 `project_path`。**若未配置，必须强制要求用户先配置，不得进入后续步骤**
2. **网络环境**：需能访问 GRFal 服务（公司内网）

---

## 流程概览

```
用户需求
  ├─ A. 需要生成新视频 → Step 2~8（视频生成流程）
  └─ B. 已有视频文件（用户提供路径）→ 跳到 Step 9（代码集成）

--- 视频生成流程（Step 2~8）---

用户描述视频内容
    ↓
GRFal generate_video (model=vidu)
    ↓
用户确认内容（展示可点击链接 + 可切换模型）
    ├─ 不满意 → 换模型或重新描述
    └─ 满意 ↓
是否修改比例？（默认 16:9，可选 9:16/1:1/4:3 等）
    ↓ 需要则调用 video_reframe
【意图理解】判断是否纯色背景
    ├─ 纯色背景 → 抠背景 + 导出 SBS
    ├─ 非纯色背景 → 直接使用原视频
    └─ 无法判断 → 询问用户
    ↓
确认保存地址（自动推断功能模块 + 文件名）
    ↓
下载保存到项目目录
    ↓
输出成功：完整路径 + 文件大小

--- 代码集成流程（Step 9）---

是否需要生成/更新 C# 代码？
    ├─ 否 → 工作流结束
    └─ 是 → 按场景分类执行
```

---

## Step 2: 生成视频

```powershell
py "<grfal脚本路径>/call_grfal.py" --tool generate_video --params-file _params.json --timeout 600
```

默认模型 **vidu**，可选：seadance（即梦）/ hailuo / veo3 / sora / kling / wan / runway

## Step 3: 用户确认

展示视频 URL 为可点击链接，提示可切换模型或改描述。仅用户确认满意后继续。

## Step 4: 修改比例（可选）

若需修改，调用 `video_reframe`（直接使用 URL，无需下载）：

```powershell
py "<grfal脚本路径>/call_grfal.py" --tool video_reframe --params-file _params.json --timeout 600
```

## Step 5: 意图判断 → 是否抠背景

| 情况 | 判断依据 | 操作 |
|------|----------|------|
| 需要抠背景 | prompt 包含：黑色/白色背景、绿幕、纯色、单色、透明背景 | 抠背景 + 导出 SBS |
| 不需要 | prompt 描述具体场景（森林、城堡、战场） | 直接使用原视频 |
| 无法判断 | 无明确背景描述 | 询问用户 |

### 抠背景（直接使用 URL）

```powershell
py "<grfal脚本路径>/call_grfal.py" --tool video_remove_background --params-file _params.json --timeout 600
```

### 导出 SBS（默认 CRF 18）

```powershell
py "<grfal脚本路径>/call_grfal.py" --tool export_sbs_video --params-file _params.json --timeout 600
```

## Step 7: 确认保存地址

### 自动推断功能模块

| prompt 关键词 | 推断模块 |
|---------------|----------|
| 角色/人物/英雄/怪物/表情/笑/哭 | Character |
| 技能/魔法/攻击/释放/施法 | Skill |
| 特效/光效/粒子/爆炸 | Effect |
| 过场/剧情/CG/片头 | Cutscene |
| 图标/按钮/UI | UI |
| 联盟/公会/Boss | UnionBoss |
| 冒险/远征/征途/遗迹 | Adventure |
| 抽卡/召唤/招募 | Gacha |
| 航行/航海/大航海 | AgeSailing |
| 创建角色/选择角色 | CreateCharacter |
| 活动/赛季 | Activity |
| 其他 | Other |

### 文件名自动生成

从 prompt 提取关键词，转换为 **PascalCase**。禁止空格、中文、全小写。
不重复模块前缀：`Character/GoblinLaugh.webm` ✅，`Character/CharacterGoblinLaugh.webm` ❌

### 保存路径

```
{project_path}/Assets/x2/Video/Other/{功能模块}/{文件名}.{扩展名}
```

### 下载（PowerShell）

```powershell
$dir = "{project_path}\Assets\x2\Video\Other\{功能模块}"
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force }
Invoke-WebRequest -Uri "<视频URL>" -OutFile "$dir\{文件名}.{扩展名}"
```

## Step 8: 反馈

告知用户完整路径和文件大小。

---

## Step 9: C# 代码集成（可选）

视频保存成功后（或用户已有视频），询问是否需要生成 C# 播放代码。

### 场景分类

| 判断条件 | 场景 | 说明 |
|----------|------|------|
| prefab 名称以 `MenuBubble` 开头 | A. Bubble 气泡 | 新建/更新 MainMenuBubbleVideoPlayerBase 子类 |
| 用户提供已有 UI 脚本路径 | B. 已有 UI 添加视频 | 在现有脚本中添加三段式代码 |
| 用户说"路径从配置表读取" | C. 配置驱动 | 仅提供 VideoPath 格式建议 |

### VideoPath 统一格式

```csharp
VideoDef.VideoUrl("{模块}/{文件名}")  // 不含扩展名
```

详细代码模板见 `video-code-patterns.md`。

---

## 重要原则

1. **URL 优先**：所有视频处理步骤直接使用 URL，只在最后保存时才下载
2. **不用 --file 上传视频**：视频太大会失败，改用 URL 传参
3. **config.json 必须有 project_path**：未配置不得执行视频工作流
