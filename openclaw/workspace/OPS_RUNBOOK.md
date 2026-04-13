# OpenClaw 运维手册

> 踩坑记录 + 故障速查 + 部署规范。遇到问题先查这里。

---

## 1. 系统架构

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  飞书/TG     │◄───►│  Gateway      │◄───►│  Agent     │
│  (用户入口)   │     │  :18790       │     │  (MiniMax) │
└─────────────┘     └──────┬───────┘     └─────┬──────┘
                           │                    │
                    ┌──────┴───────┐      ┌─────┴──────┐
                    │  Watchdog    │      │  Cron      │
                    │  (进程守护)   │      │  (定时任务) │
                    └──────────────┘      └────────────┘
```

| 组件 | 路径/端口 | 作用 |
|------|----------|------|
| Gateway | `ws://127.0.0.1:18790` | WebSocket 网关，连接飞书/TG 和 Agent |
| Agent | MiniMax-M2.7 | AI 代理，执行用户指令 |
| Watchdog | `C:\ADHD_agent\openclaw\watchdog.ps1` | 每2分钟检测 Gateway，自动重启 |
| Cron | `C:\Users\linkang\.openclaw\cron\jobs.json` | 定时任务调度 |
| 配置文件 | `C:\Users\linkang\.openclaw\openclaw.json` | 全局配置（模型、渠道、插件） |
| Agent 规则 | `C:\ADHD_agent\openclaw\workspace\AGENTS.md` | Agent 行为规则 |
| Agent 记忆 | `C:\ADHD_agent\openclaw\workspace\MEMORY.md` | 持久化记忆 |
| 会话文件 | `C:\ADHD_agent\openclaw\agents\main\sessions\*.jsonl` | 对话历史 |

---

## 2. Windows 环境踩坑（高频）

### 2.1 `.ps1` 文件关联 → 弹记事本

**现象**：用 `Start-Process -FilePath "openclaw"` 启动时，Windows 弹出记事本打开 `openclaw.ps1`。

**根因**：Windows 默认将 `.ps1` 文件关联到记事本（安全策略），`Start-Process` 按文件关联处理而非执行。npm 安装的 CLI 工具同时生成 `.cmd` / `.ps1` 两个包装脚本。

**修复**：用 `.cmd` 包装脚本替代。

```powershell
# ❌ 错误 - 会弹记事本
Start-Process -FilePath "openclaw" -ArgumentList "gateway" -WindowStyle Hidden

# ✅ 正确
Start-Process -FilePath "openclaw.cmd" -ArgumentList "gateway" -WindowStyle Hidden
```

**影响范围**：所有通过 `Start-Process` 调用 npm 全局安装的 CLI 工具。

### 2.2 PowerShell `2>nul` 无效

**现象**：`dir xxx 2>nul` 报错 `Out-File: FileStream` 异常。

**根因**：`2>nul` 是 cmd.exe 语法，PowerShell 不识别 `nul` 设备。

```powershell
# ❌ cmd 语法
dir xxx 2>nul

# ✅ PowerShell 语法
dir xxx -ErrorAction SilentlyContinue
Get-ChildItem xxx 2>$null
```

### 2.3 PowerShell 中文/Emoji 编码

**现象**：Python 脚本的 `print()` 含 Emoji 或中文时报 `UnicodeEncodeError: 'gbk' codec can't encode`。

**修复**：脚本开头加编码设置。

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

### 2.4 PowerShell `cd /d` 无效

**现象**：`cd /d C:\path && command` 报错。

**根因**：`/d` 是 cmd.exe 语法。

```powershell
# ❌
cd /d C:\ADHD_agent && python script.py

# ✅ 直接 cd（PowerShell 自动跨盘符），或用 exec 的 working_directory 参数
Set-Location C:\ADHD_agent; python script.py
```

---

## 3. Gateway 运维

### 3.1 手动启停

```powershell
# 启动
Remove-Item "C:\ADHD_agent\openclaw\gateway.lock" -Force -ErrorAction SilentlyContinue
Start-Process -FilePath "openclaw.cmd" -ArgumentList "gateway" -WindowStyle Hidden

# 停止
Get-CimInstance Win32_Process -Filter "Name='node.exe'" |
    Where-Object { $_.CommandLine -match "openclaw" } |
    ForEach-Object { taskkill /F /PID $_.ProcessId }

# 检查是否运行
Get-CimInstance Win32_Process -Filter "Name='node.exe'" |
    Where-Object { $_.CommandLine -match "openclaw" } |
    Select-Object ProcessId, CommandLine
```

### 3.2 Gateway 启动失败排查

| 错误 | 原因 | 修复 |
|------|------|------|
| `JSON5: invalid character` | `openclaw.json` 语法错误 | 用 `python -c "import json; json.load(open(...))"` 验证，修复语法 |
| `gateway.lock exists` | 上次异常退出残留锁文件 | 删除 `gateway.lock` |
| `EADDRINUSE :18790` | 端口被占用 | 先 kill 旧进程，再启动 |
| `gateway closed (1000)` | 其他 CLI 连接时 gateway 已关闭 | 先启动 gateway，再执行 agent 命令 |

### 3.3 `openclaw.json` 常见问题

- **重复内容追加**：文件末尾可能出现重复的 JSON 片段（曾遇到 `plugins` 段被重复追加），导致解析失败。检查方法：
  ```powershell
  python -c "import json; json.load(open(r'C:\Users\linkang\.openclaw\openclaw.json', encoding='utf-8')); print('OK')"
  ```
- **Doctor 自动修改**：OpenClaw 的 Doctor 功能会自动迁移配置格式（如把飞书 single-account 迁移到 `accounts.default`），但有时会写坏文件。修改前建议备份：
  ```powershell
  Copy-Item openclaw.json openclaw.json.bak
  ```

---

## 4. Watchdog 运维

### 4.1 启停

```powershell
# 启动（隐藏窗口）
Start-Process -FilePath "powershell.exe" `
  -ArgumentList "-ExecutionPolicy Bypass -WindowStyle Hidden -File C:\ADHD_agent\openclaw\watchdog.ps1" `
  -WindowStyle Hidden

# 查找进程
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
    Where-Object { $_.CommandLine -match "watchdog" } |
    Select-Object ProcessId

# 停止
Stop-Process -Id <PID> -Force

# 查看日志
Get-Content C:\ADHD_agent\openclaw\watchdog.log -Tail 20
```

### 4.2 Watchdog 功能

1. **Session 大小守护**：会话文件超过 500KB 时自动备份并重启 Gateway（防止 MiniMax API token 超限）
2. **Gateway 存活检测**：每 120 秒检测一次，挂了自动重启

### 4.3 已修复的问题

- `Start-Process "openclaw"` 弹记事本 → 改为 `"openclaw.cmd"`（2026-03-26 修复）

---

## 5. Cron 定时任务

### 5.1 当前任务

| 任务 | Cron | 脚本 | delivery |
|------|------|------|----------|
| 旅游攻略推送 | `0 11 * * 1-5` | `xiaohongshu_push_v3.py` | `feishu` |
| 国际机票日报 | `30 11 * * 1-5` | `ctrip_tracker.py` | `feishu` |

### 5.2 delivery.channel 必须显式指定

**踩坑**：如果同时配置了 telegram + feishu 两个渠道，`delivery.channel` 设为 `"last"` 会报错：

```
Channel is required when multiple channels are configured: telegram, feishu
```

**修复**：所有 cron job 的 `delivery.channel` 必须显式设为 `"feishu"`（或 `"telegram"`），不能用 `"last"`。

```powershell
# 修改方法（通过 OpenClaw CLI）
openclaw.cmd cron update --id <job-id> --delivery '{"channel":"feishu","mode":"announce"}'
```

### 5.3 Isolated Session 限制

Cron 默认用 `sessionTarget: "isolated"`（隔离会话），这意味着：
- 没有之前的对话上下文
- 不知道"上次用的渠道"是哪个（所以 `channel: "last"` 失效）
- `message` 工具需要显式 `target`（如 open_id）

飞书推送时如果 `message` 工具报 `Action send requires a target`，说明隔离会话里没有投递目标。解决方案是依赖 cron 的 `delivery.mode: "announce"` 自动推送，而不是在脚本里手动调 `message`。

---

## 6. 携程机票监控

### 6.1 反爬应对策略

| 方案 | 结果 |
|------|------|
| 直接请求航班列表页 | ❌ 触发验证码，返回反爬页面 |
| 拦截 Ctrip 内部 API | ❌ 需要认证 cookie，不可持续 |
| 日历栏价格抽取 | ✅ 可用，但只有日历最低价（含转机） |
| 直飞筛选 URL 参数 `directflight=1` | ❌ 破坏日历栏，无价格返回 |

**当前方案**：抓取日历栏价格 + 静态直飞航司知识库。价格为日历最低价（含转机），直飞信息靠预置数据标注。

### 6.2 运行模式

```powershell
# Quick（对话查询，全10条航线，每窗口1样本，约2-3分钟）
python ctrip_tracker.py --quick

# Full（Cron 专用，全样本，约5分钟）
python ctrip_tracker.py --full

# 指定目的地+日期
python ctrip_tracker.py --dest 大阪 --from 2026-05-01 --to 2026-05-07

# 国家别名查询
python ctrip_tracker.py --dest 日本  # 自动映射为东京+大阪

# 带直飞标注
python ctrip_tracker.py --quick --direct
```

### 6.3 超时防范

- 对话场景必须用 `--quick`，否则超时
- exec 的 `yieldMs` 设 200000（200秒），`timeout` 设 240
- 连续3条航线抓取失败时自动熔断，不会无限等待
- 在 AGENTS.md 中已强制约束 Agent 不得在对话中使用 `--full`

### 6.4 数据文件

| 文件 | 用途 |
|------|------|
| `flight_data/flight_history.json` | 历史价格数据 |
| `uploads/flight_trend.png` | 趋势图 |
| `ctrip_tracker.py` | 主脚本 |

---

## 7. Agent 行为管理

### 7.1 AGENTS.md 规则不生效

**现象**：虾哥无视 AGENTS.md 里的规则（如用 `browser` 替代 `exec`，回复解释性文字而不是执行脚本）。

**原因**：
1. Session 上下文优先级高于 AGENTS.md——如果之前的对话中有过"用 browser 查携程"的成功案例，Agent 会优先学习这个模式
2. MiniMax 模型的 instruction following 没有 GPT/Claude 强

**修复方法**：
1. **重置会话**：让 Agent 从干净的上下文开始，不受历史对话干扰
   ```powershell
   # 备份当前会话
   $ts = Get-Date -Format "yyyyMMdd_HHmmss"
   Get-ChildItem "C:\ADHD_agent\openclaw\agents\main\sessions\*.jsonl" |
       Where-Object { $_.Name -notmatch "backup|reset" } |
       ForEach-Object { Rename-Item $_.FullName "$($_.BaseName)-backup-$ts.jsonl" }
   # 重启 Gateway
   ```
2. **AGENTS.md 中用强制性措辞**：用"必须"、"绝对禁止"、❌/✅ 标记，比"建议"/"可以"有效得多
3. **给出可复制粘贴的完整命令**：不要只写参数说明，直接给完整的 exec 命令行

### 7.2 工具失败死循环

**现象**：Agent 对同一个报错的工具调用无限重试，刷屏且浪费 token。

**预防**：AGENTS.md 中加了"工具失败熔断规则"——同一工具连续失败3次必须停止。

### 7.3 Session 文件膨胀

**现象**：会话文件增长到几百KB后，MiniMax API 报 token 超限（错误码 794/796）。

**预防**：
- Watchdog 自动检测并备份超过 500KB 的会话
- AGENTS.md 中加了"上下文管理规则"，要求 Agent 主动将信息写入 MEMORY.md

---

## 8. 飞书推送

### 8.1 API 权限

当前 App（`cli_a934245330789ccf`）已获权限：

| 权限 | 用途 |
|------|------|
| `im:message:send_as_bot` | 发送消息 |
| `im:message` | 消息读写 |
| `im:resource` | 上传图片/文件 |

**缺少的权限**：`im:chat:readonly` / `im:chat`（无法列出群聊列表）。

### 8.2 直接发送消息（绕过 Agent）

当 Agent 的 `message` 工具无法正常工作时，可以用 Python 直接调飞书 API：

```python
import requests, json, os

app_id = 'cli_a934245330789ccf'
app_secret = os.environ.get('FEISHU_APP_SECRET', '')
open_id = 'ou_e48f6c4c0395f45b74b51525f348678b'  # 用户的 open_id

# 获取 token
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': app_id, 'app_secret': app_secret})
token = r.json()['tenant_access_token']

# 发消息
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
requests.post(
    'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id',
    headers=headers,
    json={'receive_id': open_id, 'msg_type': 'text',
          'content': json.dumps({'text': '测试消息'})}
)
```

### 8.3 上传图片

```python
# 上传图片获取 image_key
with open('image.png', 'rb') as f:
    rimg = requests.post('https://open.feishu.cn/open-apis/im/v1/images',
        headers={'Authorization': f'Bearer {token}'},
        data={'image_type': 'message'},
        files={'image': ('image.png', f, 'image/png')})
image_key = rimg.json()['data']['image_key']
```

---

## 9. 故障速查表

| 现象 | 原因 | 修复 |
|------|------|------|
| 记事本弹出 | watchdog 用 `Start-Process "openclaw"` 启动 gateway | 改为 `"openclaw.cmd"` |
| Cron 推送不到飞书 | `delivery.channel` 设为 `"last"` | 改为显式 `"feishu"` |
| Gateway 启动失败 JSON 错误 | `openclaw.json` 被追加重复内容 | 删除文件末尾多余内容 |
| Agent 超时 | 机票脚本用了 `--full` 模式 | 对话中只用 `--quick` |
| Agent 弹记事本说明 | 无视 AGENTS.md 规则 | 重置 session，强化规则措辞 |
| Python 打印 Emoji 报错 | Windows GBK 编码 | `sys.stdout.reconfigure(encoding='utf-8')` |
| exec 中文乱码 | PowerShell 默认编码 | 用 Python 替代 PowerShell 命令 |
| 携程抓不到价格 | 反爬验证码 / 页面结构变化 | 检查日历栏 selector `.price`，连续失败3次自动停止 |
| `message` 报 `requires a target` | Isolated session 没有投递上下文 | 用 cron delivery 机制替代手动发送 |
| Session 文件过大 | 长对话 token 膨胀 | Watchdog 自动备份 >500KB 的会话 |

---

## 10. 开机自启配置

Watchdog 通过 Windows 任务计划程序开机自启：

```powershell
# 查看任务
schtasks /query /tn "OpenClaw Watchdog" /fo LIST /v

# 如果需要重新创建
schtasks /create /tn "OpenClaw Watchdog" /tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\ADHD_agent\openclaw\watchdog.ps1" /sc onlogon /rl highest
```

Gateway 不需要单独配置自启——Watchdog 会自动检测并启动。

---

## 11. 日常维护 Checklist

- [ ] Gateway 是否运行：`Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -match "openclaw" }`
- [ ] Watchdog 是否运行：`Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -match "watchdog" }`
- [ ] Cron 最近执行状态：查看 `C:\Users\linkang\.openclaw\cron\jobs.json` 中的 `state.lastRunStatus`
- [ ] 会话文件大小：`Get-ChildItem "C:\ADHD_agent\openclaw\agents\main\sessions\*.jsonl" | Where-Object { $_.Name -notmatch "backup" } | Select-Object Name, @{N='KB';E={[math]::Round($_.Length/1KB)}}`
- [ ] Watchdog 日志异常：`Get-Content C:\ADHD_agent\openclaw\watchdog.log -Tail 10`

---

*最后更新：2026-03-26 | 维护者：Cursor Agent*
