# Cursor 后台 Agent — 启动引导

## ⚡ 每次对话开始必做：检查是否有待执行任务

**进入对话的第一步**，先检查是否有挂起的任务：

```powershell
# 检查 _current_task.json（daemon 收到任务时自动写入）
type "C:\ADHD_agent\openclaw\workspace\cursor_outbox\_current_task.json" 2>$null
# 检查 inbox 中状态为 processing 的任务
Get-ChildItem "C:\ADHD_agent\openclaw\workspace\cursor_inbox\" | ForEach-Object { $t = Get-Content $_.FullName | ConvertFrom-Json; if ($t.status -eq 'processing') { Write-Host $_.Name $t.title } }
```

如果有 `processing` 任务 → **立即执行它**，不要等用户说。

---

## 如何启动

在 Cursor 里开一个**新的 Agent 对话窗口**，把下面这段话复制粘贴进去发送：

---

```
你现在是 Cursor 后台任务处理 Agent。

请立刻执行以下脚本，等待 OpenClaw 派发的任务（等待时间最长 1 小时）：

python "C:\ADHD_agent\.cursor\skills\async-notify\scripts\cursor_daemon.py" --timeout 3600

脚本说明：
- 脚本会轮询任务队列，发现任务时打印任务内容并退出
- 退出后，你读取输出中 CURSOR_TASK_START 和 CURSOR_TASK_END 之间的 JSON，按 instructions 字段执行任务
- 执行完成后，把结果写入：
  C:\ADHD_agent\openclaw\workspace\cursor_outbox\{task_id}.json
  格式：{"task_id": "...", "title": "...", "status": "done", "result": "结果摘要", "completed_at": "时间"}
- 如果任务有产出文件（图片/文档/配置等），必须用飞书发给虾哥：
  python -c "
  import sys; sys.path.insert(0, r'C:\ADHD_agent\.cursor\skills\async-notify\scripts')
  import feishu_helper
  feishu_helper.send_images([r'产出文件路径1', r'产出文件路径2'], caption='任务产出说明')
  "
- 写完结果、发完产出后，调用 notify_done.py 发飞书完成通知
- 发完通知后，立刻再次运行 cursor_daemon.py 等待下一个任务

循环规则：
  等待任务 → 收到任务 → 执行任务 → 【发产出文件到飞书】→ 写结果 → 发完成通知 → 再次等待

现在开始，运行脚本。
```

---

## 架构图

```
OpenClaw（虾哥）
  │ submit_task.py
  ▼
cursor_inbox/task_xxx.json  ←── 任务队列（Python 轮询，0 token）
  │ 有任务时 daemon 退出，输出任务内容
  ▼
Cursor 后台 Agent 读取并执行
  │ exec / 文件操作 / 生成配置 / 写代码
  ▼
cursor_outbox/result_xxx.json
  │ send_images() ← 如有产出文件先发飞书
  │ notify_done.py
  ▼
飞书：产出图片/文件 + ✅ 完成通知
  │
  └──► 再次运行 daemon，等待下一个任务
```

## 后台模式（计划任务 / watchdog）

`cursor_watchdog.py` 启动的 daemon 带 **`--stay-alive`**：领到任务后发飞书、写 `_current_task.json`，**进程不退出**，继续每 5 秒扫 inbox。若不用此项，领任务后进程退出，在下次 watchdog 触发前（最长约 5 分钟）**无人监听**，新任务会积压。

在 Cursor 里**手动**跑 daemon、要靠终端里 `CURSOR_TASK_START` 读任务时：**不要**加 `--stay-alive`（默认领任务后退出）。

## 路径速查

| 用途 | 路径 |
|------|------|
| 等待脚本 | `C:\ADHD_agent\.cursor\skills\async-notify\scripts\cursor_daemon.py` |
| 提交任务 | `C:\ADHD_agent\.cursor\skills\async-notify\scripts\submit_task.py` |
| 任务队列 | `C:\ADHD_agent\openclaw\workspace\cursor_inbox\` |
| 任务结果 | `C:\ADHD_agent\openclaw\workspace\cursor_outbox\` |
| 完成通知 | `C:\ADHD_agent\.cursor\skills\async-notify\scripts\notify_done.py` |
| 发图片产出 | `feishu_helper.send_images(paths, caption=...)` |
