---
name: google-workspace-cli
description: Google Workspace CLI (gws) 工具，用于读写 Google Sheets/Docs/Drive。支持读取gsheet数据、上传数据到gsheet、搜索Drive文件、创建Google文档。当用户提到"gsheet"、"gsheet cli"、"读gsheet"、"写gsheet"、"上传到gsheet"、"Google表格"、"读取Google表格"、"Google Drive"、"gws"时使用。
---

# Google Workspace CLI 部署与使用指南

## 概述

本指南帮助你在 Windows 系统上配置 Google Workspace CLI (`gws`)，实现通过命令行访问 Google Drive、Sheets、Docs、Gmail、Calendar 等服务。配置完成后，可以：

- 读取/创建 Google Sheets 表格
- 读取/创建 Google Docs 文档
- 列出/搜索 Google Drive 文件
- 自动总结 Google 文档内容

**触发词**: 
- GSheet 相关: "gsheet"、"gsheet cli"、"读gsheet"、"写gsheet"、"上传到gsheet"、"从gsheet读取"、"gsheet数据"
- Google 表格: "Google表格"、"读取Google表格"、"写入Google表格"、"上传Google表格"
- Drive 相关: "Google Drive"、"Drive文件"、"搜索Drive"、"列出Drive"
- 配置相关: "配置gws"、"gws cli"、"Google Workspace CLI"、"Drive API"
- 操作相关: "创建Google文档"、"读取在线表格"、"同步到云端表格"

---

## 一、安装步骤

### 1.1 安装 gws CLI

```bash
npm install -g @googleworkspace/cli
```

验证安装：
```bash
gws --version
```

### 1.2 安装 Google Cloud SDK（可选，用于自动化配置）

```bash
winget install Google.CloudSDK --source winget --accept-package-agreements --accept-source-agreements
```

---

## 二、OAuth 配置（核心步骤）

### 重要原理

> **创建凭据的账号 ≠ 使用凭据的账号**
> 
> - 可以用**个人 Gmail** 创建 OAuth 凭据（相当于创建一把钥匙）
> - 然后用**公司账号**授权使用（相当于用这把钥匙开公司的门）
> - 这样即使公司账号没有 GCP 项目创建权限，也能使用 gws

### 2.1 创建 Google Cloud 项目

1. 用**个人 Gmail 账号**打开：https://console.cloud.google.com/projectcreate
2. 创建一个新项目（名称随意，如 `gws-cli`）
3. 记住项目 ID（格式类似 `calm-repeater-489707-n1`）

### 2.2 配置 OAuth 同意屏幕

1. 打开：`https://console.cloud.google.com/apis/credentials/consent?project=你的项目ID`
2. 选择 **External**（外部）
3. 填写：
   - 应用名称：`GWS CLI`
   - 用户支持邮箱：你的个人 Gmail
   - 开发者联系邮箱：你的个人 Gmail
4. 点击 **SAVE AND CONTINUE**

### 2.3 添加 Scopes（API 权限范围）

1. 在 OAuth 同意屏幕页面，找到 **資料存取權** / **Scopes** 部分
2. 点击 **ADD OR REMOVE SCOPES**
3. 添加以下 scopes：
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/calendar`
4. 保存

### 2.4 添加测试用户

1. 在 OAuth 同意屏幕页面，找到 **Test users** / **測試使用者**
2. 点击 **ADD USERS**
3. 添加你要使用的账号邮箱（如公司邮箱 `xxx@company.com`）
4. 保存

### 2.5 创建 OAuth 凭据

1. 打开：`https://console.cloud.google.com/apis/credentials?project=你的项目ID`
2. 点击 **CREATE CREDENTIALS** → **OAuth client ID**
3. 应用类型选择：**Desktop app**（电脑应用程式）
4. 名称：`GWS CLI`
5. 点击 **CREATE**
6. **下载 JSON 文件**

### 2.6 安装凭据文件

将下载的 JSON 文件复制到 gws 配置目录：

```powershell
# 创建配置目录
New-Item -ItemType Directory -Path "$env:USERPROFILE\.config\gws" -Force

# 复制凭据文件（替换为你的文件路径）
Copy-Item "C:\Users\你的用户名\Downloads\client_secret_xxx.json" "$env:USERPROFILE\.config\gws\client_secret.json"
```

### 2.7 启用必要的 API

用**个人账号**打开以下链接并点击 **Enable**：

- Drive API: `https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=你的项目ID`
- Sheets API: `https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=你的项目ID`
- Docs API: `https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=你的项目ID`

### 2.8 授予项目访问权限（如果使用公司账号）

1. 打开：`https://console.developers.google.com/iam-admin/iam?project=你的项目ID`
2. 点击 **GRANT ACCESS**
3. 添加公司邮箱，角色选择 **Editor** 或 **Owner**
4. 保存

### 2.9 登录授权

```bash
gws auth login
```

浏览器会弹出授权页面，用**目标账号**（如公司账号）登录并授权所有权限。

### 2.10 设置环境变量

```powershell
# 永久设置项目 ID
[Environment]::SetEnvironmentVariable("GOOGLE_WORKSPACE_PROJECT_ID", "你的项目ID", "User")

# 当前会话生效
$env:GOOGLE_WORKSPACE_PROJECT_ID = "你的项目ID"
```

---

## 三、验证配置

### 3.1 检查认证状态

```bash
gws auth status
```

应该显示：
- `token_valid: true`
- `scopes` 包含 drive, sheets, docs 等

### 3.2 测试 Drive API

```bash
gws drive files list
```

### 3.3 测试 Sheets API

```bash
# 替换为实际的 spreadsheetId
gws sheets spreadsheets get --params '{"spreadsheetId": "xxx", "fields": "properties.title"}'
```

---

## 四、常用命令

### 4.1 Drive 操作

```bash
# 列出文件
gws drive files list

# 搜索文件（PowerShell 中需要用变量方式）
$env:GOOGLE_WORKSPACE_PROJECT_ID = "你的项目ID"
gws drive files list | Select-String -Pattern "关键词"
```

### 4.2 Sheets 操作

```bash
# 获取表格信息
gws sheets spreadsheets get --params '{"spreadsheetId": "xxx"}'

# 读取单元格数据
gws sheets spreadsheets values get --params '{"spreadsheetId": "xxx", "range": "Sheet1!A1:Z50"}'
```

### 4.3 Docs 操作

由于 Windows PowerShell 引号转义问题，建议使用 Python 脚本：

```python
# create_doc.py
import subprocess
import json
import os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = '你的项目ID'

# 创建文档
create_body = {'title': '新文档标题'}
create_json = json.dumps(create_body, ensure_ascii=False)

cmd = [
    r'C:\Users\你的用户名\AppData\Roaming\npm\gws.cmd',
    'docs', 'documents', 'create',
    '--json', create_json
]

result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
doc_info = json.loads(result.stdout)
print(f"文档ID: {doc_info['documentId']}")
print(f"链接: https://docs.google.com/document/d/{doc_info['documentId']}/edit")
```

### 4.4 写入文档内容

```python
# update_doc.py
import subprocess
import json
import os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = '你的项目ID'

content = """这里是文档内容
支持多行
支持中文
"""

request = {
    'requests': [{
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    }]
}

json_str = json.dumps(request, ensure_ascii=False)

cmd = [
    r'C:\Users\你的用户名\AppData\Roaming\npm\gws.cmd',
    'docs', 'documents', 'batchUpdate',
    '--params', '{"documentId": "文档ID"}',
    '--json', json_str
]

result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
```

---

## 五、自动总结 Google 文档示例

### 5.1 读取 Google Sheet 并生成总结

```python
# summarize_sheet.py
import subprocess
import json
import os

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = '你的项目ID'
GWS_CMD = r'C:\Users\你的用户名\AppData\Roaming\npm\gws.cmd'

def read_sheet(spreadsheet_id, range_name):
    """读取 Google Sheet 数据"""
    params = json.dumps({
        'spreadsheetId': spreadsheet_id,
        'range': range_name
    })
    
    cmd = [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return json.loads(result.stdout)

def create_doc(title):
    """创建新文档"""
    create_json = json.dumps({'title': title}, ensure_ascii=False)
    cmd = [GWS_CMD, 'docs', 'documents', 'create', '--json', create_json]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return json.loads(result.stdout)['documentId']

def write_to_doc(doc_id, content):
    """写入文档内容"""
    request = {
        'requests': [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
    }
    
    params = json.dumps({'documentId': doc_id})
    json_str = json.dumps(request, ensure_ascii=False)
    
    cmd = [GWS_CMD, 'docs', 'documents', 'batchUpdate', '--params', params, '--json', json_str]
    subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

# 使用示例
if __name__ == '__main__':
    # 1. 读取源表格
    sheet_id = '你的表格ID'
    data = read_sheet(sheet_id, 'Sheet1!A1:Z50')
    
    # 2. 生成总结内容
    summary = "文档总结\n\n"
    for row in data.get('values', [])[:10]:
        summary += '\t'.join(row) + '\n'
    
    # 3. 创建新文档并写入
    doc_id = create_doc('自动生成的总结文档')
    write_to_doc(doc_id, summary)
    
    print(f"总结文档已创建: https://docs.google.com/document/d/{doc_id}/edit")
```

---

## 六、故障排除

### 6.1 权限不足错误

```
Request had insufficient authentication scopes
```

**解决**: 重新运行 `gws auth login`，确保授权所有权限

### 6.2 API 未启用错误

```
API has not been used in project xxx before or it is disabled
```

**解决**: 打开错误信息中的链接，启用对应的 API

### 6.3 项目未找到错误

```
Project 'projects/xxx' not found or deleted
```

**解决**: 检查并设置正确的 `GOOGLE_WORKSPACE_PROJECT_ID` 环境变量

### 6.4 PowerShell JSON 引号问题

Windows PowerShell 处理 JSON 引号有问题，建议：
1. 使用 Python 脚本调用 gws
2. 或使用 WSL

---

## 七、快速配置清单

- [ ] 安装 gws CLI: `npm install -g @googleworkspace/cli`
- [ ] 创建 Google Cloud 项目（个人账号）
- [ ] 配置 OAuth 同意屏幕
- [ ] 添加 API Scopes
- [ ] 添加测试用户
- [ ] 创建 OAuth 凭据（Desktop app）
- [ ] 下载并安装 client_secret.json
- [ ] 启用 Drive/Sheets/Docs API
- [ ] 授予项目访问权限（IAM）
- [ ] 运行 `gws auth login` 授权
- [ ] 设置 `GOOGLE_WORKSPACE_PROJECT_ID` 环境变量
- [ ] 验证: `gws drive files list`

---

## 八、X2 导表集成

### 8.1 X2 配置表页签工具

本 skill 包含 `x2_sheet_info.py` 脚本，可用于 X2 导表前的页签-分支匹配检查。

**使用方法**：

```powershell
# 设置环境变量
$env:GOOGLE_WORKSPACE_PROJECT_ID = "calm-repeater-489707-n1"

# 进入 skill 目录
cd C:\ADHD_agent\.cursor\skills\google-workspace-cli

# 列出所有 X2 配置表
python x2_sheet_info.py --list

# 查找 1111 相关表的页签
python x2_sheet_info.py 1111

# 读取 i18n 表的所有页签
python x2_sheet_info.py --tabs i18n

# 检查页签与 X2 仓库当前分支是否匹配
python x2_sheet_info.py --check item_dev --repo "D:\UGit\x2gdconf"
```

### 8.2 与 X2 导表 Skill 配合使用

在执行 X2 导表前，可以先用此工具检查页签：

1. 查看目标表有哪些页签及版本标注
2. 检查当前分支与页签版本是否匹配
3. 避免下载错误版本的配置

**示例流程**：
```powershell
# 1. 查看 1111 表的页签
python x2_sheet_info.py 1111
# 输出: item, item_dev, item_hotfix 等

# 2. 检查当前分支
python x2_sheet_info.py --check item_dev

# 3. 确认无误后，执行 X2 导表
cd D:\UGit\x2gdconf
.\tools\fwcli.exe googlexlsx -a . -d tmp_xlsx -r xxx -f 1111
```

---

## 九、参考链接

- gws CLI 官方仓库: https://github.com/googleworkspace/cli
- Google Cloud Console: https://console.cloud.google.com/
- OAuth 同意屏幕: https://console.cloud.google.com/apis/credentials/consent
- API 库: https://console.cloud.google.com/apis/library
