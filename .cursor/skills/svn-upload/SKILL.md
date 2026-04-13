---
name: svn-upload
description: |
  P2 美术资产 SVN 上传工具。将图片以指定 ID 为文件名复制到 SVN 工作目录，
  并通过 TortoiseProc.exe（本机无命令行 svn）完成 Add + Commit。
  支持单文件和批量上传，支持指定任意目标文件夹。
  内置常用目标路径：装饰物文件夹、头像框文件夹等。
  当用户提到"传SVN"、"上传SVN"、"svn提交"、"svn上传"、"传图到SVN"时使用。
---

# SVN 上传工具

将美术图片上传到 P2 项目 SVN 工作目录（`D:\CD_UI_NEW_2`）。

> ⚠️ 本机 TortoiseSVN **无命令行 `svn`**，所有操作必须用 `TortoiseProc.exe`

---

## 常用目标路径

| 类型 | 路径 |
|------|------|
| 装饰物图标 | `D:\CD_UI_NEW_2\2_UI_CUT\T_图标\Z装饰物\` |
| 头像框 | `D:\CD_UI_NEW_2\2_UI_CUT\T_图标\T头像框\` |
| 其他 | 用户直接告知路径 |

---

## 文件命名规则

- 文件名 = **ID（纯数字）+ `.png`**，例如 `151105160.png`
- 多文件时：用户提供的图片列表与 ID 列表**按顺序一一对应**

---

## 执行步骤

### 步骤 1：确认目标路径和 ID 映射

询问或根据上下文确认：
- 目标文件夹（装饰物 / 头像框 / 自定义）
- 图片源路径列表
- 对应的 ID 列表

### 步骤 2：复制文件

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dest = "D:\CD_UI_NEW_2\2_UI_CUT\T_图标\Z装饰物"   # ← 按实际修改

# ID → 源文件路径 映射（按顺序填入）
$files = @{
    "151105138" = "C:\path\to\image1.png"
    "151105137" = "C:\path\to\image2.png"
}

foreach ($id in $files.Keys) {
    Copy-Item $files[$id] "$dest\$id.png" -Force
    Write-Host "✅ 已复制: $id.png"
}
```

### 步骤 3：SVN Add（新文件才需要）

```powershell
$svnproc = "C:\Program Files\TortoiseSVN\bin\TortoiseProc.exe"
$dest = "D:\CD_UI_NEW_2\2_UI_CUT\T_图标\Z装饰物"   # ← 按实际修改

# 多个文件用 * 分隔
$addPaths = ($files.Keys | ForEach-Object { "$dest\$_.png" }) -join "*"

& $svnproc /command:add /path:$addPaths /closeonend:2
Start-Sleep -Seconds 3
```

> 若文件已在 SVN 版本控制内（之前已 add 过），跳过此步骤直接 Commit。

### 步骤 4：SVN Commit（弹出提交窗口）

```powershell
$svnproc = "C:\Program Files\TortoiseSVN\bin\TortoiseProc.exe"
$dest = "D:\CD_UI_NEW_2\2_UI_CUT\T_图标\Z装饰物"   # ← 按实际修改

$commitPaths = ($files.Keys | ForEach-Object { "$dest\$_.png" }) -join "*"

& $svnproc /command:commit /path:$commitPaths /logmsg:"新增图标 $($files.Keys -join ', ')"
```

弹出窗口后：确认文件勾选无误 → 点 **OK** 完成提交。

---

## 单文件快捷流程

```powershell
$svnproc = "C:\Program Files\TortoiseSVN\bin\TortoiseProc.exe"
$src  = "C:\path\to\source.png"    # ← 源文件
$id   = "151105160"                 # ← ID
$dest = "D:\CD_UI_NEW_2\2_UI_CUT\T_图标\T头像框"  # ← 目标文件夹

Copy-Item $src "$dest\$id.png" -Force
Write-Host "✅ 已复制: $id.png"

# Add + Commit
& $svnproc /command:add    /path:"$dest\$id.png" /closeonend:2
Start-Sleep -Seconds 2
& $svnproc /command:commit /path:"$dest\$id.png" /logmsg:"新增 $id"
```

---

## 注意事项

- 若文件已存在（修改更新而非新增），跳过 Add，直接 Commit
- `/closeonend:2` 表示操作成功时自动关闭 TortoiseProc 窗口
- Commit 窗口弹出后需人工点 OK 确认，不会自动提交
