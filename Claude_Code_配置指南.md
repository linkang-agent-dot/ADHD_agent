# Claude Code 配置指南

> 本指南介绍如何安装和配置 Claude Code，以及如何使用 MiniMax、Gemini 等第三方 API。

---

## 一、安装 Claude Code

### 1.1 安装 Claude Code CLI

**Windows PowerShell:**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**macOS/Linux:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

### 1.2 添加环境变量（Windows）

安装后如果提示 PATH 未配置，运行：

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\你的用户名\.local\bin", [EnvironmentVariableTarget]::User)
```

### 1.3 验证安装

```powershell
claude --version
```

---

## 二、安装 CC-Switch（推荐）

CC-Switch 是一个图形化工具，可以方便地切换不同的 API 提供商（MiniMax、Gemini 等）。

### 2.1 下载安装

**方法一：手动下载**

前往 [CC-Switch GitHub Releases](https://github.com/farion1231/cc-switch/releases) 下载最新版 MSI 安装包。

**方法二：PowerShell 一键安装**

```powershell
# 下载
Invoke-WebRequest -Uri "https://github.com/farion1231/cc-switch/releases/download/v3.11.1/CC-Switch-v3.11.1-Windows.msi" -OutFile "$env:TEMP\CC-Switch.msi"

# 安装
Start-Process "$env:TEMP\CC-Switch.msi"
```

### 2.2 启动 CC-Switch

安装后在开始菜单找到 **CC Switch**，或运行：

```powershell
Start-Process "C:\Users\你的用户名\AppData\Local\Programs\CC Switch\cc-switch.exe"
```

---

## 三、配置 MiniMax API

### 3.1 获取 API Key

1. 访问 [MiniMax 开放平台](https://platform.minimaxi.com/user-center/basic-information/interface-key)
2. 或购买 [Coding Plan](https://platform.minimaxi.com/user-center/payment/coding-plan)

### 3.2 使用 CC-Switch 配置（推荐）

1. 打开 CC-Switch
2. 点击右上角 **"+"** 按钮
3. 选择 **MiniMax** 供应商
4. 填写你的 MiniMax API Key
5. 模型名称设为 `MiniMax-M2.5`
6. 点击 **"添加"**
7. 回到首页，点击 **"启用"**

### 3.3 手动配置（备选）

编辑 `~/.claude/settings.json`（Windows: `C:\Users\你的用户名\.claude\settings.json`）：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "你的_MINIMAX_API_KEY",
    "ANTHROPIC_BASE_URL": "https://api.minimaxi.com/anthropic",
    "ANTHROPIC_MODEL": "MiniMax-M2.5",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "MiniMax-M2.5",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "MiniMax-M2.5",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "MiniMax-M2.5",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": 1
  }
}
```

### 3.4 创建 .claude.json

编辑 `~/.claude.json`（Windows: `C:\Users\你的用户名\.claude.json`），添加：

```json
{
  "hasCompletedOnboarding": true
}
```

---

## 四、配置 Gemini API

### 4.1 获取免费 API Key

访问 [Google AI Studio](https://aistudio.google.com/apikey) 获取免费的 Gemini API Key。

### 4.2 可用模型

| 模型名称 | 说明 | 适用场景 |
|---------|------|---------|
| `gemini-2.5-pro` | 高级推理能力 | 复杂编程任务 |
| `gemini-2.5-flash` | 最佳性价比 | 日常编程 |
| `gemini-2.5-flash-lite` | 最快速、最便宜 | 简单任务 |
| `gemini-3-flash` | 最新一代 | 前沿性能 |

### 4.3 使用 CC-Switch 配置（推荐）

1. 打开 CC-Switch
2. 点击右上角 **"+"** 按钮
3. 选择 **Google Gemini** 供应商
4. 填写你的 Gemini API Key
5. 模型名称设为 `gemini-2.5-pro`
6. 点击 **"添加"**
7. 回到首页，点击 **"启用"**

### 4.4 手动配置（备选）

编辑 `~/.claude/settings.json`：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "你的_GEMINI_API_KEY",
    "ANTHROPIC_BASE_URL": "https://generativelanguage.googleapis.com/v1beta/openai",
    "ANTHROPIC_MODEL": "gemini-2.5-pro",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "gemini-2.5-pro",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "gemini-2.5-pro",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "gemini-2.5-flash",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": 1
  }
}
```

---

## 五、使用 Claude Code Router (CCR)

CCR 是另一种配置方式，可以通过命令行管理多个 API 提供商。

### 5.1 安装 CCR

```powershell
npm install -g @musistudio/claude-code-router
```

### 5.2 配置

编辑 `~/.claude-code-router/config.json`：

```json
{
  "HOST": "127.0.0.1",
  "PORT": 8080,
  "Providers": [
    {
      "name": "gemini",
      "api_base_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
      "api_key": "你的_GEMINI_API_KEY",
      "models": ["gemini-2.5-pro", "gemini-2.5-flash"]
    }
  ],
  "Router": {
    "default": "gemini,gemini-2.5-pro",
    "background": "gemini,gemini-2.5-flash"
  }
}
```

### 5.3 使用

```powershell
# 启动 CCR 服务
ccr start

# 查看状态
ccr status

# 启动 Claude Code（通过 CCR 路由）
ccr code

# 或者手动设置环境变量
$env:ANTHROPIC_BASE_URL = "http://127.0.0.1:8080"
claude

# 停止服务
ccr stop
```

---

## 六、切换模型

### 6.1 在 Claude Code 会话中切换

```
/model
```

或直接指定：

```
/model gemini-2.5-pro
```

### 6.2 启动时指定模型

```powershell
claude --model gemini-2.5-flash
```

### 6.3 使用环境变量

```powershell
$env:ANTHROPIC_MODEL = "gemini-2.5-pro"
claude
```

### 6.4 使用 CC-Switch 切换（推荐）

1. 关闭当前运行的 Claude Code
2. 打开 CC-Switch
3. 点击想要使用的配置旁边的 **"启用"**
4. 重新打开终端运行 `claude`

---

## 七、VS Code 中使用 Claude Code

### 7.1 安装插件

```powershell
code --install-extension anthropic.claude-code
```

### 7.2 配置环境变量（以 MiniMax 为例）

打开 VS Code 设置，编辑 `settings.json`：

```json
{
  "claudeCode.environmentVariables": [
    {
      "name": "ANTHROPIC_BASE_URL",
      "value": "https://api.minimaxi.com/anthropic"
    },
    {
      "name": "ANTHROPIC_AUTH_TOKEN",
      "value": "你的_MINIMAX_API_KEY"
    },
    {
      "name": "API_TIMEOUT_MS",
      "value": "3000000"
    },
    {
      "name": "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
      "value": "1"
    },
    {
      "name": "ANTHROPIC_MODEL",
      "value": "MiniMax-M2.5"
    },
    {
      "name": "ANTHROPIC_SMALL_FAST_MODEL",
      "value": "MiniMax-M2.5"
    },
    {
      "name": "ANTHROPIC_DEFAULT_SONNET_MODEL",
      "value": "MiniMax-M2.5"
    },
    {
      "name": "ANTHROPIC_DEFAULT_OPUS_MODEL",
      "value": "MiniMax-M2.5"
    },
    {
      "name": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
      "value": "MiniMax-M2.5"
    }
  ],
  "claude-code.selectedModel": "MiniMax-M2.5"
}
```

---

## 八、常用命令速查

| 命令 | 说明 |
|------|------|
| `claude` | 启动 Claude Code |
| `claude --version` | 查看版本 |
| `claude --model xxx` | 指定模型启动 |
| `/model` | 会话内切换模型 |
| `/init` | 创建 CLAUDE.md 项目说明文件 |
| `ccr start` | 启动 CCR 服务 |
| `ccr stop` | 停止 CCR 服务 |
| `ccr status` | 查看 CCR 状态 |
| `ccr ui` | 打开 CCR Web 配置界面 |

---

## 九、API 端点汇总

| 提供商 | API 端点 |
|--------|----------|
| MiniMax | `https://api.minimaxi.com/anthropic` |
| Gemini (OpenAI 兼容) | `https://generativelanguage.googleapis.com/v1beta/openai` |
| Gemini (原生) | `https://generativelanguage.googleapis.com/v1beta` |

---

## 十、常见问题

### Q: 提示 "API Error" 怎么办？

1. 检查 API Key 是否正确
2. 确认环境变量 `ANTHROPIC_AUTH_TOKEN` 和 `ANTHROPIC_BASE_URL` 没有冲突
3. 清除可能存在的系统环境变量：

```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_AUTH_TOKEN", $null, [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $null, [EnvironmentVariableTarget]::User)
```

### Q: CC-Switch 启用后配置没生效？

1. 确保 Claude Code 已完全关闭
2. 在 CC-Switch 中点击"启用"
3. 重新打开终端运行 `claude`

### Q: 如何同时保留多个 API 配置？

使用 CC-Switch，它会自动管理多个配置，点击"启用"即可切换。

---

## 相关链接

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code/quickstart)
- [CC-Switch GitHub](https://github.com/farion1231/cc-switch)
- [Claude Code Router](https://musistudio.github.io/claude-code-router/)
- [MiniMax 开放平台](https://platform.minimaxi.com/)
- [Google AI Studio](https://aistudio.google.com/apikey)

---

*最后更新: 2026年3月*
