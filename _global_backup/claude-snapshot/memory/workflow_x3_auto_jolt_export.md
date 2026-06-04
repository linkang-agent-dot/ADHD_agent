---
name: x3-push-jolt
description: X3 配置 push 后自动调用 jolt.exe 触发 Jenkins X3导配置任务，用户不用再手动跑 jolt
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9fa379f1-8095-4bed-9a37-401c299ba495
---

## 规则

任何 X3 配置改动（gdconfig 仓库）push 完，**立即**用 wrapper 调用 jolt 触发 Jenkins 导表。

> ⚠️ **前置（2026-05-29 起）**：导表读「提交的 tsv 缓存」不读 xlsx。改完 xlsx 必须先 `python scripts/xlsx_to_tsv.py --files <xlsx>` 重生成 tsv 并 commit，再 push+jolt，否则导出的是旧数据。详见 [[reference_x3_tsv_export_migration]]。

## 工具

- 入口：`C:\Users\linkang\.claude\jolt_export.py`
- 用法：`python C:\Users\linkang\.claude\jolt_export.py <branch>`（默认 `dev-summer-love-song`）
- 底层：jolt.exe (`C:\x3-project\Tools\Jolt\jolt.exe`) 是 Jenkins 快捷构建客户端，REPL 模式，wrapper 用 stdin 喂 `excel branch=... code_branch=...\nexit`

## Jenkins 任务

- 名称：**X3导配置**
- 入口：http://172.20.110.29:8080/job/X3%E5%AF%BC%E9%85%8D%E7%BD%AE/

## 输出语义

- `触发失败: 任务正在执行中 (#N) <URL>` → **不是错误**，说明已有 build 在跑（push 后 Jenkins 通常已自动触发），重复触发被拒；这种情况无需 retry，等当前 build 完即可。
- 正常触发会给新 build URL，把链接报给用户。

**Why:** 用户原话"后面我就不用再去导表烧脑了"——把"push → 跑 jolt → 等导表"这一段委托给我。2026-05-25 累充隔离需求 commit 042daba 后落地。

**How to apply:**
1. 改完 X3 任何 xlsx 或 Tools/* 代码 → git push → 立即 `python C:\Users\linkang\.claude\jolt_export.py <分支>`
2. 把 jolt 输出里的 build URL 报给用户
3. 不需要用户点头确认（已是默认工作流）
4. 用户在别的分支或临时改也可以传分支参数
