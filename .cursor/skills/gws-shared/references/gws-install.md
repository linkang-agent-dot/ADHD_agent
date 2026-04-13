# GWS CLI 安装与配置指南

> **注意**：gws CLI 完整文档见 `vendor/gws-cli/README.md`（git submodule）。本文件是快速安装参考，放在此处是因为 `vendor/` 是 git submodule，更新时会覆盖里面的文件。

## 第一步：安装

```bash
npm install -g @googleworkspace/cli
```

> 需要 Node.js 18+。npm 包内置各平台预编译二进制，无需 Rust 工具链。

验证安装：`gws --version`（当前版本 0.4.1+）

也可从 [GitHub Releases](https://github.com/googleworkspace/cli/releases) 下载预编译二进制。

## 第二步：写入 OAuth 客户端配置

在配置目录下创建 `client_secret.json`：
- **Windows**: `%APPDATA%\gws\client_secret.json`
- **macOS/Linux**: `~/.config/gws/client_secret.json`

文件内容（**公司通用，直接复制**）：

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "project_id": "sys-73981095154604987319156249",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "redirect_uris": ["http://localhost"]
  }
}
```

> 也可以直接复制下载目录中的原始文件：
> `copy %USERPROFILE%\Downloads\client_secret_669635606542-*.json %APPDATA%\gws\client_secret.json`

## 第三步：登录授权

```bash
gws auth login
```

浏览器弹出 Google 登录页面，使用**公司 Google 账号**登录并授权。
授权完成后凭据自动保存到配置目录的 `credentials.json`。

## 第四步：验证

```bash
gws auth status
```

确认输出中 `token_valid: true` 即表示配置成功。

快速测试：

```bash
gws drive files list --params '{\"pageSize\":\"5\"}'
```

## 配置文件一览

| 文件 | 路径（Windows `%APPDATA%\gws\`） | 说明 | 可否分享 |
|------|--------------------------------|------|---------|
| `client_secret.json` | 手动创建 | OAuth 客户端配置 | ✅ 公司通用 |
| `credentials.json` | 登录后自动生成 | 个人 OAuth 凭据 | ❌ 仅个人 |
| `token_cache.json` | 自动生成/刷新 | 访问令牌缓存 | ❌ 仅个人 |

## PowerShell JSON 传参注意事项

PowerShell 会吞掉 JSON 字符串中的双引号，必须用反斜杠转义：

```powershell
# ✅ 正确：反斜杠转义内部双引号
gws sheets spreadsheets get --params '{\"spreadsheetId\":\"xxx\"}'

# ✅ 推荐：使用 +read/+append 等助手命令，无需手写 JSON
gws sheets +read --spreadsheet <ID> --range "工作表名!A1:O50"

# ❌ 错误：PowerShell 会把内部双引号去掉，导致 JSON 解析失败
gws sheets spreadsheets get --params '{"spreadsheetId":"xxx"}'
```

## 完整文档

- 官方仓库：https://github.com/googleworkspace/cli
- 本地完整文档：`vendor/gws-cli/README.md`
- 配套 Agent Skills：`vendor/gws-cli/skills/`（已同步至 `.cursor/skills/gws-*`）
