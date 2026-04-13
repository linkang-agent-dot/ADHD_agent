---
name: ops-troubleshoot
description: |
  OpenClaw 运维故障排查与修复。当遇到以下问题时自动触发：
  Gateway 启动失败、记事本弹出、Cron 推送失败、Agent 超时、
  Session 膨胀、飞书发送失败、配置文件损坏、PowerShell 编码错误。
  覆盖 Windows 环境踩坑、进程管理、反爬应对、Agent 行为矫正。
  当用户提到"挂了"、"报错"、"超时"、"弹窗"、"推送失败"、"启动失败"、
  "连不上"、"gateway"、"watchdog"、"cron 失败"时使用。
---

# OpenClaw 运维故障排查

## 触发条件

用户报告以下任何一种情况：
- Gateway 挂了 / 启动失败 / 连不上
- 记事本或其他程序异常弹出
- Cron 定时任务推送失败
- Agent（虾哥）超时、死循环、无视规则
- 飞书消息发不出去
- 配置文件报错
- 脚本执行编码错误

## 快速诊断（必须按顺序执行）

### Step 1: 检查系统状态

用 `exec` 依次检查（设 timeout=10）：

```powershell
# Gateway 是否运行
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -match "openclaw" } | Select-Object ProcessId

# Watchdog 是否运行
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -match "watchdog" } | Select-Object ProcessId

# 有无异常 Notepad 进程
Get-Process notepad -ErrorAction SilentlyContinue | Select-Object Id, MainWindowTitle

# Session 文件大小
Get-ChildItem "C:\ADHD_agent\openclaw\agents\main\sessions\*.jsonl" | Where-Object { $_.Name -notmatch "backup" } | Select-Object Name, @{N='KB';E={[math]::Round($_.Length/1KB)}}
```

### Step 2: 根据症状修复

---

## 故障：Gateway 启动失败

**排查**：
```powershell
openclaw.cmd gateway 2>&1
```

| 错误信息 | 修复方法 |
|---------|---------|
| `JSON5: invalid character` | `openclaw.json` 语法错误，用 `python -c "import json; json.load(open(r'C:\Users\linkang\.openclaw\openclaw.json', encoding='utf-8'))"` 定位，通常是文件末尾有重复内容，删除多余部分 |
| `gateway.lock exists` | `Remove-Item "C:\ADHD_agent\openclaw\gateway.lock" -Force` |
| `EADDRINUSE :18790` | 先 kill 旧 node 进程：`Get-CimInstance Win32_Process -Filter "Name='node.exe'" \| Where-Object { $_.CommandLine -match "openclaw" } \| ForEach-Object { taskkill /F /PID $_.ProcessId }` |

**启动 Gateway**：
```powershell
Remove-Item "C:\ADHD_agent\openclaw\gateway.lock" -Force -ErrorAction SilentlyContinue
Start-Process -FilePath "openclaw.cmd" -ArgumentList "gateway" -WindowStyle Hidden
```

等 10 秒后验证：
```powershell
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -match "openclaw" } | Select-Object ProcessId
```

---

## 故障：记事本异常弹出

**根因**：`watchdog.ps1` 用 `Start-Process "openclaw"` 启动 Gateway，Windows 把 `.ps1` 文件关联到记事本。

**修复**：
1. Kill 所有 Notepad：`Stop-Process -Name Notepad -Force -ErrorAction SilentlyContinue`
2. 检查 `watchdog.ps1` 第35行，确保是 `"openclaw.cmd"` 而非 `"openclaw"`：
   ```
   Start-Process -FilePath "openclaw.cmd" -ArgumentList "gateway" -WindowStyle Hidden
   ```
3. 重启 Watchdog：
   ```powershell
   # Kill 旧 watchdog
   Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -match "watchdog" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
   # 启动新 watchdog
   Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -WindowStyle Hidden -File C:\ADHD_agent\openclaw\watchdog.ps1" -WindowStyle Hidden
   ```

**规则**：Windows 上所有 `Start-Process` 调用 npm CLI 工具时，必须用 `.cmd` 后缀，不能裸名。

---

## 故障：Cron 推送失败

**常见错误**：`Channel is required when multiple channels are configured: telegram, feishu`

**修复**：所有 cron job 的 `delivery.channel` 必须显式指定，不能用 `"last"`。

```powershell
# 查看 cron 配置
python -c "import json; d=json.load(open(r'C:\Users\linkang\.openclaw\cron\jobs.json',encoding='utf-8')); [print(j['name'], j['delivery']) for j in d['jobs']]"

# 手动修改 jobs.json 中的 delivery.channel 为 "feishu"
```

**另一个错误**：`Action send requires a target`

**原因**：Cron 用 `isolated` session，没有投递上下文。不要在 cron 脚本里用 `message` 工具手动发，依赖 cron 的 `delivery.mode: "announce"` 自动推送。

---

## 故障：Agent 超时

**机票查询超时**：
- 对话中必须用 `--quick` 模式（约 2-3 分钟），禁止 `--full`（约 5 分钟）
- exec 的 `yieldMs` 设 200000，`timeout` 设 240
- 如果 exec 返回 "still running"，用 `process poll` 等待，不要杀进程

**Agent 工具死循环**：
- 同一工具连续失败 3 次 → 停止重试，换方案或报告
- 检查 AGENTS.md 中"工具失败熔断规则"是否存在

---

## 故障：携程反爬验证码触发

**现象**：脚本返回空数据 / 连续航线失败 / 截图出现"请完成以下验证"

**常见原因**：
1. Agent 用 `browser` 工具直接访问了 `flights.ctrip.com`，叠加脚本请求导致 IP 被封
2. 短时间多次运行脚本（测试/调试/cron 撞在一起）

**修复**：
1. 等待 1-2 小时让 IP 冷却
2. 如果是 Agent 用 browser 导致的，重置 session（见下方"Agent 无视规则"）
3. 脚本已内置以下反爬措施（ctrip_tracker.py）：
   - 6 个 User-Agent 随机轮换
   - 5 种浏览器视口随机切换
   - 页面加载后 2.5-5.0 秒随机等待
   - 航线切换间 2.0-4.5 秒随机延迟
   - 路由间额外 3.0-7.0 秒间隔
   - locale/timezone 模拟真实用户
4. **绝对禁止** Agent 用 `browser` 工具访问 `flights.ctrip.com`

---

## 故障：Agent 无视 AGENTS.md 规则

**现象**：虾哥用 `browser` 替代 `exec`，回复解释性文字而不是执行脚本，或直接用 browser 访问携程触发反爬。

**修复**：
1. 重置 session（清除历史上下文的干扰）：
   ```powershell
   $ts = Get-Date -Format "yyyyMMdd_HHmmss"
   Get-ChildItem "C:\ADHD_agent\openclaw\agents\main\sessions\*.jsonl" |
       Where-Object { $_.Name -notmatch "backup|reset" } |
       ForEach-Object { Rename-Item $_.FullName "$($_.BaseName)-backup-$ts.jsonl" }
   ```
2. 重启 Gateway
3. AGENTS.md 中用强制性措辞："必须"、"绝对禁止"、❌/✅ 标记
4. 给完整可复制的 exec 命令，不要只写参数说明
5. 在 AGENTS.md 的 browser 禁令中加强措辞，说明后果（触发反爬 = IP 被封 = 事故）

---

## 故障：Session 文件膨胀

**现象**：会话超过 500KB → MiniMax API 报 token 超限（794/796）。

**处理**：Watchdog 自动检测并备份。如需手动处理：
```powershell
Get-ChildItem "C:\ADHD_agent\openclaw\agents\main\sessions\*.jsonl" |
    Where-Object { $_.Name -notmatch "backup" -and $_.Length -gt 500KB } |
    ForEach-Object {
        $ts = Get-Date -Format "yyyyMMdd_HHmmss"
        Rename-Item $_.FullName "$($_.BaseName)-backup-$ts.jsonl"
    }
```
然后重启 Gateway。

---

## 故障：飞书发送失败

**API 直接发消息**（绕过 Agent）：
```python
import requests, json, os
app_id = 'cli_a934245330789ccf'
app_secret = os.environ.get('FEISHU_APP_SECRET', '')
open_id = 'ou_e48f6c4c0395f45b74b51525f348678b'

r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': app_id, 'app_secret': app_secret})
token = r.json()['tenant_access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

requests.post('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id',
    headers=headers,
    json={'receive_id': open_id, 'msg_type': 'text',
          'content': json.dumps({'text': '消息内容'})})
```

**缺少的权限**：`im:chat:readonly`（无法列群聊）。当前已有 `im:message:send_as_bot` 和 `im:resource`。

---

## Windows 编码速查

| 场景 | 修复 |
|------|------|
| Python print Emoji 报 GBK 错误 | `sys.stdout.reconfigure(encoding='utf-8')` |
| PowerShell `2>nul` 报错 | 用 `2>$null` 或 `-ErrorAction SilentlyContinue` |
| `cd /d` 报错 | 直接用 `Set-Location` 或 exec 的 working_directory |
| Matplotlib 中文方块 | `plt.rcParams['font.sans-serif'] = ['SimHei']` |
| Matplotlib ¥ 符号缺失 | 用 "Y" 或 "RMB" 替代 ¥ |

---

## 关键路径速查

| 用途 | 路径 |
|------|------|
| 全局配置 | `C:\Users\linkang\.openclaw\openclaw.json` |
| Cron 配置 | `C:\Users\linkang\.openclaw\cron\jobs.json` |
| Watchdog 脚本 | `C:\ADHD_agent\openclaw\watchdog.ps1` |
| Watchdog 日志 | `C:\ADHD_agent\openclaw\watchdog.log` |
| Agent 规则 | `C:\ADHD_agent\openclaw\workspace\AGENTS.md` |
| Agent 记忆 | `C:\ADHD_agent\openclaw\workspace\MEMORY.md` |
| 会话目录 | `C:\ADHD_agent\openclaw\agents\main\sessions\` |
| 机票脚本 | `C:\ADHD_agent\openclaw\workspace\ctrip_tracker.py` |
| 机票数据 | `C:\ADHD_agent\openclaw\workspace\flight_data\flight_history.json` |
| 文件上传目录 | `C:\ADHD_agent\openclaw\workspace\uploads\` |
| 详细运维手册 | `C:\ADHD_agent\openclaw\workspace\OPS_RUNBOOK.md` |
