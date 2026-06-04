---
name: x3-i18n-backup-files-trap
description: X3 data/ 目录下的 _backup_*.xlsx 会被 CompositeI18n 扫描器扫到，跟正式 xlsx 内容冲突时报错
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 22c25965-252c-40fd-9575-d6ee02470233
---

## 规则

跑 `CompositeI18n` 扫描 i18n 前，必须把 `C:\x3\gdconfig\data\_backup_*.xlsx` 临时移出 data/ 目录（或改后缀）。

**Why:** CompositeI18n 扫描 `data/` 下所有 `*.xlsx`（含 _backup_*），如果 backup 文件里某行 key 的 CN 跟正式表里同 key 的 CN 不一致，扫描器会抛 `Exception('key = ..., chinese = ..., Key2ChineseDict[key] = ...')`，整个流程中断。

实战案例：2026-05-26 修 X3NEW-753 时改了 ActvOnline 101514 的 ActvDesc（CN 改成"你愿陪她度过这个夏天吗"），跑扫描报错—— `_backup_ActvOnline_*.xlsx` 里同 ID 仍是旧的"转动命运之轮——"，跟新 CN 冲突。

**How to apply:** 跑扫描前的固定步骤：
```bash
mkdir -p /c/x3/gdconfig/_tmp_backups
mv /c/x3/gdconfig/data/_backup_*.xlsx /c/x3/gdconfig/_tmp_backups/
# 跑扫描
python C:/Users/linkang/.claude/run_i18n_scan.py
# 恢复 backup
mv /c/x3/gdconfig/_tmp_backups/*.xlsx /c/x3/gdconfig/data/
rmdir /c/x3/gdconfig/_tmp_backups
```

或者长期方案：建议团队把 `data/_backup_*.xlsx` 加进 `.gitignore` 并约定 backup 必须放 `_tmp_backups/` 子目录而非平铺在 `data/`。
