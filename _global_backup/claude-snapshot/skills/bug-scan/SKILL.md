---
name: bug-scan
description: >-
  配置 BUG 巡检定时任务。自动创建 Windows 定时任务，工作日每小时扫描 Jira BUG 并写报告。
  触发词："配置巡检"、"setup bug scan"、"安装巡检"、"巡检设置"。
  查看巡检结果："查BUG"、"看看有啥BUG"、"BUG列表" → 直接读 _my_bugs_summary.txt。
---

# BUG 巡检定时任务

自动扫描 Jira 上 assignee 为当前用户的未解决 BUG，生成报告文件。与 `config-bugfix` skill（修复）配合使用。

## 架构

```
Windows Task Scheduler (每小时)
  → bug_scan.ps1
    → claude -p bug_scan_prompt.txt (非交互，跑完退出)
      → 查 Jira → 对比 → 写报告文件
```

巡检只读不改，修复由 `config-bugfix` skill 在独立会话中处理。

## 触发场景

### 场景 1：安装/配置巡检（"配置巡检"、"setup bug scan"）

执行下方「安装流程」，为用户创建定时任务。

### 场景 2：查看巡检结果（"查BUG"、"看看有啥BUG"、"BUG列表"）

直接读文件展示，不需要跑 Jira 查询：
```
Read C:/Users/{username}/_my_bugs_summary.txt
```
如果文件不存在，说明巡检还没配置，引导用户执行场景 1。

### 场景 3：手动跑一次巡检（"跑一次巡检"、"手动巡检"）

```powershell
powershell -ExecutionPolicy Bypass -File "{scripts_dir}/bug_scan.ps1"
```

## 安装流程

### Step 1：收集配置

问用户以下信息（有默认值的可以跳过）：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| Jira 地址 | `https://jira.tap4fun.com` | 内网 Jira 地址 |
| Jira 用户名 | 当前系统用户名 | Jira 登录名 |
| Jira API Token | 无，必填 | Jira 认证 token |
| 项目 key | `P2DEV,X2` | 逗号分隔，要扫哪些项目 |
| 巡检时段 | `9:23-20:23` | 工作时间 |
| 单次预算 | `$2` | claude -p 的 --max-budget-usd |

### Step 2：创建脚本目录和文件

脚本目录：`{user_home}/.claude/scripts/`

#### 文件 1：bug_scan_prompt.txt

根据用户配置生成 prompt 文件。模板如下（替换 `{变量}`）：

```
BUG 巡检（完整排查，不修复）。

调查每个 BUG 到"只差动手改"的程度：查表、看截图、定位问题根因、判断归属。但不做任何修改操作。

## Jira 连接

import urllib.request, base64, ssl, json, urllib.parse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

auth = base64.b64encode(b'{jira_user}:{jira_token}').decode()
base_url = '{jira_url}/rest/api/2'

## 步骤

1. 查询每个项目的未解决 BUG：
   JQL: assignee = {jira_user} AND project = {project_key} AND issuetype = Bug AND resolution = Unresolved ORDER BY priority DESC, created DESC

2. 读取上次结果 {user_home}/_my_bugs_summary.txt，对比差异

3. 对新增 BUG 做完整排查：
   a) 下载截图附件，分析 BUG 现象
   b) 分类判断（配置类/代码类/美术/需确认）
   c) 配置类 BUG 深入排查：用本地缓存或 API 查配置表，沿追踪链定位到具体表、行、字段、当前值
   d) 评估归属：可自动修 / 需策划案 / 转派程序 / 等美术 / 需确认

4. 合并旧分析+新排查，覆写 {user_home}/_my_bugs_summary.txt，格式：
   {KEY}  [{优先级}]  {类型} | {涉及表} | {归属}
     {标题}
     排查: {一句话说清问题根因和修复方向}

5. 追加巡检简报到 {user_home}/_bug_scan_log.txt

6. 新增可修复 BUG 追加到 {user_home}/_bugs_to_fix.txt

禁止：不修改任何配置、不写 Google Sheet、不操作 Jira。只读只报。
```

如果用户有配置表本地缓存或知识库（如 table-index.md、query_cache.py），在 prompt 中加上查询方法和追踪链。

#### 文件 2：bug_scan.ps1

```powershell
# BUG scan - called by Windows Task Scheduler
$promptFile = Join-Path $env:USERPROFILE ".claude\scripts\bug_scan_prompt.txt"
$logFile = Join-Path $env:USERPROFILE "_bug_scan_log.txt"

$startTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logFile -Value "[$startTime] Bug scan started" -Encoding UTF8

$prompt = Get-Content -Path $promptFile -Raw -Encoding UTF8

& claude -p $prompt --dangerously-skip-permissions --max-budget-usd {budget} 2>$null | Out-Null
$exitCode = $LASTEXITCODE

$endTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
if ($exitCode -eq 0) {
    Add-Content -Path $logFile -Value "[$endTime] Bug scan completed (exit=$exitCode)" -Encoding UTF8
} else {
    Add-Content -Path $logFile -Value "[$endTime] Bug scan FAILED (exit=$exitCode)" -Encoding UTF8
}
```

### Step 3：注册 Windows 定时任务

```powershell
Unregister-ScheduledTask -TaskName 'ClaudeBugScan' -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-ExecutionPolicy Bypass -WindowStyle Hidden -File {scripts_dir}\bug_scan.ps1'

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At '{start_time}'
$trigger.Repetition = (New-ScheduledTaskTrigger -Once -At '{start_time}' -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Hours {duration})).Repetition

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10)

Register-ScheduledTask -TaskName 'ClaudeBugScan' -Action $action -Trigger $trigger -Settings $settings -Description 'Claude BUG scan - weekday hourly Jira scan, read-only'
```

### Step 4：验证

1. 确认任务已注册：`Get-ScheduledTask -TaskName 'ClaudeBugScan'`
2. 手动跑一次测试：`powershell -ExecutionPolicy Bypass -File {scripts_dir}\bug_scan.ps1`
3. 检查产出文件是否正常

## 产出文件

| 文件 | 用途 | 模式 |
|------|------|------|
| `_my_bugs_summary.txt` | 当前 BUG 快照 | 覆写 |
| `_bug_scan_log.txt` | 巡检执行日志 | 追加 |
| `_bugs_to_fix.txt` | 待修配置类 BUG 清单 | 追加 |

## 卸载

```powershell
Unregister-ScheduledTask -TaskName 'ClaudeBugScan' -Confirm:$false
```

然后删除 `{scripts_dir}/bug_scan.ps1` 和 `bug_scan_prompt.txt`。
