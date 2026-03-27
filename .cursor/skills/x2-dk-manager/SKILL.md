---
name: x2-dk-manager
description: >
  X2 Unity DisplayKey (DK) 管理工具。支持两大功能：
  1) 上传/录入 DK — 给定 type + 图片（或路径），自动分配全局唯一 key（跨所有 Display_*.asset 取最大值+1）、
     复制图片、自动将 meta 修正为 Sprite (2D and UI) 类型（textureType:8、spriteMode:1、iOS/Android 128px 压缩覆盖）、
     写入 Display_*.asset、Ctrl+Shift+E 导出、双重确认；
     多图时自动识别已知配套组合（Icon+IconBg / Icon+IconBg+IconFront 等 24 种）共用同一 key，
     不确定时询问是否为同一 DK；
  2) 查询远端 DK — 给定 key，搜索本地和远端分支的录入状态。
  当用户提到"DK"、"display key"、"录入DK"、"上传DK"、"添加DK"、"查DK"、"查询DK"、
  "dk远端"、"dk录入"、"ctrl+t"时使用。
---

# X2 DisplayKey (DK) 管理工具

## 项目路径

| 名称 | 绝对路径 |
|------|---------|
| Unity 工程根目录 | `D:\UGit\x2client\client` |
| DK 编辑器数据目录 | `D:\UGit\x2client\client\Assets\P2\Editor\DisplayKey\` |
| DK 运行时数据目录 | `D:\UGit\x2client\client\Assets\P2\Res\DisplayKey\` |
| DK 图片默认上传目录 | `D:\UGit\x2client\client\Assets\x2\Res\UI\DKUpload\{Type}\` |
| Git 仓库根目录 | `D:\UGit\x2client` |

---

## 前提条件

1. **Unity 编辑器已打开** `D:\UGit\x2client\client` 工程（复制图片后需要 Unity 自动生成 .meta）
2. **Git 仓库可用** — `D:\UGit\x2client` 已 clone 且可正常 fetch/push（查询远端功能需要）
3. **当前分支正确** — 在你要提交 DK 的目标分支上

---

## 功能1：上传/录入 DK

### 触发词

"录入DK"、"添加DK"、"上传DK"、"新增DK"、"加DK"

### 多图/多类型时的前置询问（⚠️ 重要）

当用户一次提供 **2 张或以上图片**，或明确指定 **多个不同类型**时，
**先判断是否属于已知配套组合**；不确定时**必须询问**，再继续任何 key 分配操作。

#### 已知配套组合（同一 DK、共用 key）

基于现有 2444 个跨类型 DK 统计得出：

| 频次 | 类型组合 | 含义/场景 |
|------|----------|-----------|
| 743 | `Icon + IconBg` | 活动图标 — Icon=前景图标，IconBg=背景底图（选中/未选中状态） |
| 256 | `Icon + Prefab + UIPrefab` | 图标 + 场景预制件 + UI预制件 |
| 249 | `Icon + UIPrefab` | 图标 + UI预制件 |
| 205 | `Icon + IconFront` | 图标 + 前景高亮叠加层 |
| 147 | `Icon + Portrait` | 图标 + 立绘/人物大图 |
| 106 | `Icon + Prefab` | 图标 + 场景/3D预制件 |
| 91 | `Icon + Prefab + PrefabShow` | 图标 + 预制件展示态 |
| 75 | `Icon + IconBg + IconFront` | 活动图标三件套（背景+图标+前景高亮） |
| 73 | `Icon + IconBg + Prefab + PrefabIcon` | 图标+背景+预制件+预制件图标 |
| 33 | `Head + Icon + IconBg + Prefab` | 英雄/角色资产套件（头像+图标+背景+预制件） |
| 30 | `Icon + IconBg + Prefab + UIPrefab` | 图标+背景+双预制件 |
| 29 | `Effect + Icon` | 特效 + 图标 |
| 22 | `Head + Icon + Prefab` | 英雄头像 + 图标 + 预制件 |
| 22 | `Icon + Prefab + PrefabHold + PrefabShow` | 图标 + 预制件三态（持有/展示） |
| 21 | `Head + Icon + IconBg + IconFront + Prefab` | 英雄完整套件（含高亮层） |
| 15 | `Head + Icon + IconBg + IconFront` | 英雄图标四件套 |
| 13 | `Icon + IconFront + IconMask + Prefab` | 图标+前景+遮罩+预制件 |
| 10 | `HeroSquareAvatar + Icon + Prefab` | 英雄方形头像 + 图标 + 预制件 |
| 9 | `Icon + IconBg + Portrait` | 图标+背景+立绘 |
| 7 | `Icon + MinigameIcon` | 主图标 + 小游戏图标 |
| 6 | `MinigameIcon + MinigamePrefab` | 小游戏图标 + 小游戏预制件 |
| 4 | `Avatar + Head + Icon` | 头像全套（大头像+头部+图标） |
| 4 | `Icon + IconBg + IconFront + IconMask` | 活动图标四件套（含遮罩） |
| 2 | `Guide + Icon` | 引导图标 + 主图标 |

> **判断规则**：用户说「X 张图一个DK」或类型组合**匹配或包含于**上表任一行，直接按**共用 key** 处理，无需再问。
> 否则（组合不在表中，或不确定）询问：
> ```
> "这 N 张图是同一个 DK（共用 key、不同 type），还是各自独立的 DK？"
> ```

| 用户回答 | 处理方式 |
|----------|---------|
| **同一个 DK** | 只分配 **1 个 key**，所有图片共用，各自写入对应 type 的 asset |
| **独立 DK** | 为每张图片分别分配独立 key |

---

### 用户输入（3 种方式，key 均可省略由系统自动分配）

**方式A：图片已在 Unity 工程内**
```
用户: 录入DK Icon, Assets/x2/Res/UI/NewSprite/Activity/icon_xxx.png
```

**方式B：直接丢图片**（粘贴/拖入聊天）
```
用户: [粘贴图片] Icon
```
图片自动存到默认路径，key 自动分配。

**方式C：给本地文件路径**
```
用户: 录入DK Icon, 源文件 D:\Downloads\icon.png
```

> 所有方式中 key 均可手动指定，如 `录入DK 1511030005 Icon`。不指定则自动分配。

### 21 种 DK 类型

```
Icon        IconBg      IconFront   IconMask
Prefab      PrefabIcon  PrefabShow  PrefabHold
UIPrefab    WorldPrefab
Effect      BattleEffect
Avatar      Head        HeadFrame
HeroSquareAvatar
Portrait
MinigameIcon  MinigamePrefab
Guide       Other
```

> 子目录类型（Evolved/MetroShoot/MiniGameCommon/MobControl/PipeGame/RaceMaster/TowerDefense）
> 需用户明确指出，否则默认写入主目录。

### 默认图片存放路径

方式B/C 用户未指定目标路径时，按 type 自动存放：

```
D:\UGit\x2client\client\Assets\x2\Res\UI\DKUpload\{Type}\DK_{key}.png
```

示例：`Assets/x2/Res/UI/DKUpload/Icon/DK_151100893.png`

---

### ⚠️ Meta 文件必须设为 Sprite (2D and UI) 类型

Unity 导入图片时默认生成 `textureType: 0`（Default），**DK 图片必须是 `textureType: 8`（Sprite 2D and UI）**，否则游戏运行时无法正常显示。

**复制图片后、等待 Unity 生成 .meta 之前，需要先把 .meta 重写为标准 Sprite 模板。**

或者在 Unity 生成 .meta 后，立即用脚本修正（步骤2.5，在步骤2之后、步骤3之前执行）：

#### 步骤2.5: 修正 .meta 为 Sprite 类型

```powershell
# 等 .meta 生成后，用标准 Sprite 模板覆盖（保留 guid 不变）
$metaPath = "D:\UGit\x2client\client\Assets\x2\Res\UI\DKUpload\{Type}\DK_{key}.png.meta"
$guid = (Get-Content $metaPath -TotalCount 2 | Select-Object -Last 1) -replace 'guid: ', ''

$template = @"
fileFormatVersion: 2
guid: $guid
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 0
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {x: 0.5, y: 0.5}
  spritePixelsToUnits: 100
  spriteBorder: {x: 0, y: 0, z: 0, w: 0}
  spriteGenerateFallbackPhysicsShape: 0
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 3
    buildTarget: Standalone
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 3
    buildTarget: iPhone
    maxTextureSize: 128
    resizeAlgorithm: 0
    textureFormat: 49
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 1
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  - serializedVersion: 3
    buildTarget: Android
    maxTextureSize: 128
    resizeAlgorithm: 0
    textureFormat: 49
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 1
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: 5e97eb03825dee720800000000000000
    internalID: 0
    vertices: []
    indices: 
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {}
  mipmapLimitGroupName: 
  pSDRemoveMatte: 0
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"@
[System.IO.File]::WriteAllText($metaPath, $template, [System.Text.Encoding]::UTF8)
Write-Host "Meta 已修正为 Sprite 类型，guid=$guid"
```

**关键差异对比（Default vs Sprite）：**

| 字段 | Default（错误） | Sprite（正确） |
|------|----------------|----------------|
| `textureType` | 0 | **8** |
| `spriteMode` | 0 | **1** (Single) |
| `alphaIsTransparency` | 0 | **1** |
| `enableMipMap` | 1 | **0** |
| `nPOTScale` | 1 | **0** |
| `wrapU/wrapV` | 0 (Clamp) | **1** (Repeat) |
| `spriteGenerateFallbackPhysicsShape` | 1 | **0** |
| iPhone `maxTextureSize` | 2048 | **128** |
| iPhone `textureFormat` | -1 | **49** |
| iPhone `overridden` | 0 | **1** |
| Android `maxTextureSize` | 2048 | **128** |
| Android `textureFormat` | -1 | **49** |
| Android `overridden` | 0 | **1** |

---

### 执行流程（精确命令）

#### 步骤0: Key 自动分配（用户未提供 key 时）

```powershell
# ⚠️ 必须搜索【全部】Display_*.asset，取全局最大值 +1，避免跨类型 key 冲突
Get-ChildItem "D:\UGit\x2client\client\Assets\P2\Editor\DisplayKey\Display_*.asset" |
  ForEach-Object { Get-Content $_.FullName } |
  Select-String '"key":(\d+)' |
  ForEach-Object { [long]$_.Matches[0].Groups[1].Value } |
  Sort-Object |
  Select-Object -Last 1

# 然后 +1 得到新 key
# 再在对应类型的 asset 中确认新 key 不存在:
Get-Content "D:\UGit\x2client\client\Assets\P2\Editor\DisplayKey\Display_{type}.asset" |
  Select-String '"key":{newKey}'
# 如果为空则可用
```

#### 步骤1: (仅方式B/C) 复制图片到 Unity 工程

```powershell
# 创建目标目录（如不存在）
New-Item -ItemType Directory -Path "D:\UGit\x2client\client\Assets\x2\Res\UI\DKUpload\{Type}" -Force

# 方式B: Cursor 保存的图片路径在 image_files 元数据中提供
Copy-Item "{cursor保存的图片路径}" "D:\UGit\x2client\client\Assets\x2\Res\UI\DKUpload\{Type}\DK_{key}.png"

# 方式C: 用户给的源路径
Copy-Item "{用户源路径}" "D:\UGit\x2client\client\Assets\x2\Res\UI\DKUpload\{Type}\DK_{key}.png"
```

#### 步骤2: (仅方式B/C) 等待 Unity 生成 .meta 文件

```powershell
$metaPath = "D:\UGit\x2client\client\{图片完整路径}.meta"
$waited = 0
while (-not (Test-Path $metaPath) -and $waited -lt 30) {
    Start-Sleep -Seconds 2
    $waited += 2
}
if (Test-Path $metaPath) {
    Get-Content $metaPath -TotalCount 3
} else {
    # 超时 → 提示用户: "请切到 Unity 窗口让它检测新文件，或按 Ctrl+R 刷新"
    # 用户回复后再次检查
}
```

#### 步骤3: 读取 GUID

```powershell
Get-Content "{图片路径}.meta" -TotalCount 2 | Select-Object -Last 1
# 输出: "guid: 0816e22841b0c8b4faaf7e52da260cb3"
# 提取 guid 值
```

#### 步骤4: Key 去重检查

```powershell
# 使用 Grep 工具搜索:
Grep pattern='"key":{key}' path='D:\UGit\x2client\client\Assets\P2\Editor\DisplayKey\Display_{type}.asset'
# 如果有结果 → 报错 "❌ key={key} 已存在，跳过"
# 如果无结果 → 继续
```

#### 步骤5: 写入 Display_{type}.asset

```
使用 Read 工具读取文件最后 3 行，找到 data: 列表的最后一条
使用 StrReplace 工具，在最后一条后面追加新行:

  - '{"key":{key},"type":"{type}","desc":"","dkObj":{"assetGuid":"{guid}"},"intArg":0}'

注意:
- 缩进: 2 个空格
- 外层: 单引号包裹整个 JSON
- 不要修改已有条目
```

#### 步骤6: ✅ 确认1（写入确认）

```
使用 Grep 搜索 Display_{type}.asset 中的 "key":{key}
验证 assetGuid 与 .meta 中的 guid 一致
输出: "✅ 确认1通过: key={key} 已写入 Display_{type}.asset, GUID={guid}"
```

#### 步骤7: 等待用户 Export

```
输出: "请在 Unity 中按 Ctrl+Shift+E 导出，完成后告诉我"
说明: Ctrl+Shift+E 会同时执行 Export 和 Generate Script，一步到位
等待用户回复 "完成了" / "按了" / "好了" 等确认
```

#### 步骤8: ✅ 确认2（导出确认）

```powershell
# 搜索运行时数据
Get-Content "D:\UGit\x2client\client\Assets\P2\Res\DisplayKey\Path_{type}.asset" |
  Select-String "key: {key}" -Context 0,2

# 预期输出:
#   - key: {key}
#     objPath: Assets/x2/Res/UI/DKUpload/{Type}/DK_{key}.png
#     intArg: 0
```

```
验证 objPath 正确
输出: "✅ 确认2通过: key={key} 已导出到 Path_{type}.asset, objPath={path}"
如果找不到: "❌ 确认2失败，请检查 Unity Console 是否有报错"
```

#### 步骤9: 输出总结表

```
| 项目 | 结果 |
|------|------|
| Key | {key} |
| Type | {type} |
| GUID | {guid} |
| 图片位置 | {objPath} |
| ✅ 确认1（编辑器写入） | 通过 |
| ✅ 确认2（运行时导出） | 通过 |

然后询问: "需要我帮你 git commit 吗？还是继续录下一个？"
```

---

## 功能2：查询远端 DK

### 触发词

"查DK"、"查询DK"、"DK远端"、"DK有没有"、"DK录入了吗"

### 用户输入

| 字段 | 说明 | 示例 |
|------|------|------|
| **key** | DK 数字编号（支持多个，空格/逗号分隔） | `1511030001` 或 `1511030001, 1511030002` |

### 执行流程（精确命令）

#### 步骤1: 本地搜索

```
使用 Grep 工具:
pattern: "key":{key}
path: D:\UGit\x2client\client\Assets\P2\Editor\DisplayKey
记录: 所在文件(类型)、GUID
```

#### 步骤2: 远端搜索

```powershell
# 工作目录: D:\UGit\x2client

# 获取当前分支名
git branch --show-current

# 在远端当前分支搜索（根据步骤1找到的文件路径）
git show origin/{branch}:client/Assets/P2/Editor/DisplayKey/Display_{type}.asset 2>$null |
  Select-String '"key":{key}'

# 同时检查 origin/dev
git show origin/dev:client/Assets/P2/Editor/DisplayKey/Display_{type}.asset 2>$null |
  Select-String '"key":{key}'
```

> 注意: git show 的路径用正斜杠，相对于 git 仓库根目录 `D:\UGit\x2client`，
> 所以要加 `client/` 前缀。

#### 步骤3: 输出结果表

```
| Key | Type | 本地 | 远端({branch}) | 远端(dev) | GUID |
|-----|------|------|----------------|-----------|------|
| 1511030001 | Icon | ✅ | ✅ | ✅ | f745...f8 |
| 1511030002 | Icon | ✅ | ❌ | ❌ | abc1...2d |
```

---

## 批量操作示例

**批量上传（方式A）**:
```
用户: 帮我录入以下 DK:
Icon, Assets/x2/Res/UI/xxx/icon1.png
Icon, Assets/x2/Res/UI/xxx/icon2.png
Prefab, Assets/x2/Res/Prefab/xxx/prefab1.prefab
```

**丢图片上传（方式B）**:
```
用户: [粘贴图片] Icon
```

**批量查询**:
```
用户: 帮我查这几个 DK: 1511030001 1511030002 1511030003
```

---

## 常见问题处理

| 场景 | 处理方式 |
|------|---------|
| .meta 文件不存在 | 报错：图片可能未导入 Unity，请先确认图片已放入工程并等待 Unity 导入 |
| .meta 等待超时（方式B/C） | 提示用户切到 Unity 窗口让它刷新资源，或在 Unity 中按 Ctrl+R |
| key 已存在 | 报错：该 key 已录入，跳过。显示已有条目的 GUID 供对比 |
| Display_*.asset 文件不存在 | 该类型可能是新类型或子目录类型，需确认路径 |
| 确认2失败 | 提示用户检查 Unity Console 是否有报错，可能需要重新按 Ctrl+Shift+E |
| 远端搜索 git 命令失败 | 提示网络问题或远端分支不存在 |
| 图片复制目标路径不存在 | 自动 `New-Item -Force` 创建目录 |
| 用户粘贴的图片格式不是 PNG | 提醒 Unity 图标通常为 PNG 格式，确认是否继续 |
