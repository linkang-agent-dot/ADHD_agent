---
name: async-notify
description: |
  异步多 Agent 协作通知系统。覆盖三大能力：
  1. 完成通知 — Agent 完成任务后通过飞书推送"已完成"（✅ 自动触发）
  2. 确认请求 — 需要用户决策时发飞书阻塞等待回复，虾哥把飞书回复转达给 Cursor
  3. 全自动后台执行 — daemon 常驻轮询任务队列，发现任务后自动调用 Cursor Agent CLI
     执行、写结果、推飞书，无需 Cursor 窗口保持打开，支持模型/模式/沙箱按任务配置
  所有脚本路径统一在 C:\ADHD_agent\.cursor\skills\async-notify\scripts\
  触发词：任务完成通知、飞书推送、等待确认、异步通知、agent 通知、
  反向调用、派任务给 Cursor、后台处理、cursor 后台、任务队列、
  notify done、notify confirm、submit task、cursor daemon、自动执行。
---

# Async Notify Skill — 飞书驱动的 Cursor 全自动化

## 系统架构

```
你的手机 / 电脑（飞书）
    │  发消息 / 收通知
    ▼
OpenClaw（虾哥）
    │  submit_task.py → cursor_inbox/{task_id}.json
    ▼
cursor_daemon.py（常驻后台）
    │  每 5 秒轮询 inbox
    │  发现 pending 任务
    │  调用 node.exe → index.js（Cursor Agent CLI）
    │  写结果到 cursor_outbox/{task_id}.json
    │  调用 notify_done.py
    ▼
飞书 ✅ 任务完成通知推送到你手机
```

---

## 一次性安装（Prerequisites）

### 1. 安装 Cursor Agent CLI

```powershell
# 在普通 PowerShell（非 Cursor 内置终端）执行
irm 'https://cursor.com/install?win32=true' | iex
```

### 2. 写入认证凭据（替代 agent login 交互流程）

`agent login` 会打开浏览器，无法在后台/沙箱中使用。直接写文件注入凭据：

```powershell
# 从 Cursor 账户页面取得 access_token / refresh_token
$authFile = "$env:APPDATA\Cursor\auth.json"
$json = '{"accessToken":"<你的access_token>","refreshToken":"<你的refresh_token>"}'
# 注意：必须用无 BOM 的 UTF-8，否则 Node.js JSON.parse 会失败
[System.IO.File]::WriteAllText($authFile, $json, [System.Text.UTF8Encoding]::new($false))
```

> **获取 token 的方法**：打开 Cursor → 右下角头像 → Account → 在浏览器登录页 F12 → 
> Network → 找 `/auth/token` 请求 → 取 `access_token`（或通过 OpenClaw 侧获取）

验证：
```powershell
agent status  # 应显示 ✓ Logged in as xxx@xxx.com
```

### 3. 启动 daemon（常驻后台）

```powershell
# 方式一：直接启动 watchdog（推荐，自动保活）
Start-Process python -ArgumentList `
  '"C:\ADHD_agent\.cursor\skills\async-notify\scripts\cursor_watchdog.py"' `
  -WindowStyle Hidden

# 方式二：指定默认模型启动
Start-Process python -ArgumentList `
  '"C:\ADHD_agent\.cursor\skills\async-notify\scripts\cursor_watchdog.py" --default-model claude-4.6-sonnet-medium' `
  -WindowStyle Hidden

# 验证是否运行
Get-Content "C:\ADHD_agent\openclaw\workspace\daemon_autoexec.log" -Tail 5
```

---

## 能力一：任务完成通知

任何涉及 2+ 工具调用的任务结束时自动发飞书，见 `async-notify.mdc` 规则。

```powershell
python "C:\ADHD_agent\.cursor\skills\async-notify\scripts\notify_done.py" `
  --task "P2导表-复活节" --result "成功上传5张表" --agent "Cursor"
```

飞书收到：
> ✅ **[Cursor] P2导表-复活节 — 已完成**  
> 成功上传5张表  
> ⏱ 2026-04-02 14:23

---

## 能力二：阻塞等待用户确认

不可逆操作前发飞书问用户，拿到答复再继续。

```python
import subprocess, sys, json

result = subprocess.run([
    sys.executable,
    r"C:\ADHD_agent\.cursor\skills\async-notify\scripts\notify_confirm.py",
    "--task", "合并分支",
    "--question", "即将把 feature/easter 合并到 main，影响23个文件，是否继续？",
    "--agent", "Cursor",
    "--timeout", "600"
], capture_output=True, text=True, encoding='utf-8')

output = json.loads(result.stdout.strip().split('\n')[-1])
# output = {"decision": "yes"/"no"/"timeout", "reply": "用户回复原文"}

if output["decision"] == "yes":
    pass  # 继续
elif output["decision"] == "no":
    pass  # 取消
```

**内部流程**：写 `async_tasks/pending/` → 飞书推问题 → 每5秒轮询 `confirmed/` → 返回决策。

---

## 能力三：全自动后台执行（核心）

### 任务提交格式

向 `cursor_inbox/` 目录放一个 JSON 文件，daemon 会自动拾取：

```json
{
  "task_id": "task_20260402_example",
  "title": "任务标题",
  "instructions": "详细指令，越详细越好",
  "context": "可选的背景信息",
  "submitted_by": "OpenClaw",
  "priority": "normal",
  "status": "pending",
  "submitted_at": "2026-04-02 14:00:00",

  // 以下字段可选，用于控制 Agent CLI 行为
  "model": "claude-4.6-opus-high-thinking",  // 覆盖全局默认模型
  "mode": "plan",                             // plan=只读规划 / ask=问答 / 不填=完整agent
  "sandbox": "disabled"                       // enabled/disabled
}
```

### 可用模型列表（`agent --list-models` 查看）

| 常用模型 ID | 说明 |
|------------|------|
| `claude-4.6-sonnet-medium` | Sonnet 4.6，均衡，推荐日常任务 |
| `claude-4.6-opus-high-thinking` | Opus 4.6 Thinking，最强推理 |
| `gemini-3-flash` | 快速轻量 |
| `gpt-5.4-medium` | GPT-5.4 均衡 |
| `gpt-5.3-codex` | 代码专用 |
| `auto` | CLI 自动选择 |

### 通过 submit_task.py 提交任务

```powershell
python "C:\ADHD_agent\.cursor\skills\async-notify\scripts\submit_task.py" `
  --title "任务标题" `
  --instructions "Cursor 需要做什么的详细指令" `
  --context "额外背景" `
  --submitted-by "OpenClaw" `
  --notify
```

### 查看任务状态

```powershell
# 查看待处理队列
python "C:\ADHD_agent\.cursor\skills\async-notify\scripts\submit_task.py" --list

# 查看已完成结果
python "C:\ADHD_agent\.cursor\skills\async-notify\scripts\submit_task.py" --results

# 查看实时日志
Get-Content "C:\ADHD_agent\openclaw\workspace\daemon_autoexec.log" -Tail 20 -Wait
```

---

## Daemon 运维

### 启动 / 停止 / 重启

```powershell
# 停止
powershell -NoProfile -ExecutionPolicy Bypass `
  -File "C:\ADHD_agent\.cursor\skills\async-notify\scripts\stop_cursor_daemon.ps1"

# 重启（用 watchdog，自动带 --auto-execute）
Start-Process python -ArgumentList `
  '"C:\ADHD_agent\.cursor\skills\async-notify\scripts\cursor_watchdog.py" --force-restart' `
  -WindowStyle Hidden

# 切换默认模型重启
Start-Process python -ArgumentList `
  '"C:\ADHD_agent\.cursor\skills\async-notify\scripts\cursor_watchdog.py" --force-restart --default-model gpt-5.3-codex' `
  -WindowStyle Hidden
```

### daemon 参数说明

```
cursor_daemon.py 参数：
  --timeout 86400       最长等待秒数（watchdog 默认传 86400 = 24小时）
  --stay-alive          执行完任务后继续轮询（不退出）
  --auto-execute        启用 CLI 自动执行模式（watchdog 默认开启）
  --default-model xxx   全局默认模型（任务 JSON 中的 model 字段优先级更高）

cursor_watchdog.py 参数：
  --force-restart       先杀旧 daemon 再启动新的
  --no-auto-execute     用传统打印模式（不自动执行）
  --default-model xxx   传给 daemon 的默认模型
```

### 日志位置

| 日志文件 | 内容 |
|---------|------|
| `daemon_autoexec.log` | 主日志：任务拾取、模型、执行结果 |
| `daemon_stdout.log` | daemon 进程 stdout（等待心跳） |
| `daemon_watchdog.log` | watchdog 启停记录 |
| `daemon.pid` | 当前 daemon PID（JSON 格式） |

---

## 模型控制优先级

```
任务 JSON "model" 字段
        ↓ 没有则
watchdog --default-model 参数
        ↓ 没有则
Cursor Agent CLI 内置默认（composer-2-fast）
```

---

## 关键坑（Windows 专项）

### 1. PowerShell UTF-8 BOM 问题
PowerShell `Set-Content -Encoding UTF8` 会写入 BOM（`\xEF\xBB\xBF`），
导致 Node.js `JSON.parse` 失败，agent CLI 认证失效。

**✅ 正确写法**：
```powershell
[System.IO.File]::WriteAllText($path, $json, [System.Text.UTF8Encoding]::new($false))
```

### 2. agent.CMD 中文乱码
`agent.CMD → cursor-agent.ps1 → node.exe` 三层传递，中文 prompt 经 cmd.exe 会乱码崩溃。

**✅ 修复**：daemon 直接调用 `node.exe index.js`，完全绕过 shell 包装层：
```
%LOCALAPPDATA%\cursor-agent\versions\<最新版本>\node.exe
%LOCALAPPDATA%\cursor-agent\versions\<最新版本>\index.js
```

### 3. agent CLI 认证文件路径
Windows 上 auth.json 存放于：
```
%APPDATA%\Cursor\auth.json
```
（app name = `"cursor"`，经 `toWindowsTitleCase` → `"Cursor"`，非 `"cursor-agent"`）

### 4. Cursor 沙箱限制
`agent login` 需要打开浏览器，Cursor 内置终端沙箱无法完成。
必须在普通 PowerShell 中运行，或直接写 auth.json 注入凭据。

---

## 脚本清单

| 脚本 | 调用方 | 用途 |
|------|--------|------|
| `notify_done.py` | Cursor Agent | 发飞书完成通知 |
| `notify_confirm.py` | Cursor Agent | 发飞书确认请求 + 轮询等待 |
| `cursor_daemon.py` | 系统（后台） | 轮询任务队列，自动调用 Agent CLI 执行 |
| `cursor_watchdog.py` | 系统（定时任务） | 保活 daemon，支持模型/模式参数透传 |
| `submit_task.py` | OpenClaw / 脚本 | 向 cursor_inbox 提交任务 |
| `confirm_write.py` | OpenClaw | 写回用户飞书确认结果 |
| `stop_cursor_daemon.ps1` | 外部 PowerShell | 优雅停止 daemon |
| `feishu_helper.py` | 内部依赖 | 飞书 API 工具函数 |

---

## 共享目录结构

```
C:\ADHD_agent\openclaw\workspace\
  cursor_inbox\           ← pending 任务 JSON（daemon 轮询这里）
  cursor_outbox\          ← 执行结果 JSON（OpenClaw 读这里）
    _current_task.json    ← 当前正在执行的任务
  async_tasks\
    pending\              ← notify_confirm 写入的待确认任务
    confirmed\            ← 虾哥写入用户决策
  daemon.pid              ← daemon PID
  daemon_autoexec.log     ← 主执行日志
  daemon_stdout.log       ← daemon stdout
  daemon_watchdog.log     ← watchdog 日志
```

---

## 飞书 API 配置

- `app_id`：`cli_a934245330789ccf`
- `open_id`：`ou_e48f6c4c0395f45b74b51525f348678b`
- `app_secret`：自动从 `C:\Users\linkang\.openclaw\openclaw.json` 的 `env.FEISHU_APP_SECRET` 读取
