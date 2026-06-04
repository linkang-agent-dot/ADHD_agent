---
name: dws
description: 管理钉钉全产品能力（AI表格/审批/考勤/日历/群聊机器人/通讯录/待办/日志/DING消息/文档/钉盘/邮箱/AI听记/AI应用/工作台等）。操作钉钉任意产品数据时使用。
cli_version: ">=1.0.8"
---

# 钉钉全产品 Skill

通过 `dws` 命令管理钉钉全产品能力。`dws` 是智能 wrapper，自动路由到最优版本：
- **主力 v1.0.8（dws.local）**：aitable / attendance / calendar / chat / contact / devdoc / ding / oa / report / todo / workbench
- **补充 v0.2.27（PC）**：doc / drive / mail / minutes / aiapp / conference / finance / docparse / aidesign 等

## 严格禁止 (NEVER DO)
- 不要使用 dws 命令以外的方式操作（禁止 curl、HTTP API、浏览器）
- 不要编造 UUID、ID 等标识符，必须从命令返回中提取
- 不要猜测字段名/参数值，操作前必须先查询确认

## 严格要求 (MUST DO)
- 所有命令必须加 `--format json` 以获取可解析输出
- 危险操作必须先向用户确认，用户同意后才加 `--yes` 执行
- 单次批量操作不超过 30 条记录
- 所有命令必须**严格遵循**对应产品参考文档里规定的参数格式

## 产品总览

| 产品 | 用途 | 参考文件 |
|------|------|----------|
| `aitable` | AI表格：表格/数据表/字段/记录增删改查/模板搜索 | [aitable.md](./references/products/aitable.md) |
| `approval` | 审批（旧接口，已迁移到 `oa`）| [simple.md](./references/products/simple.md) |
| `attendance` | 考勤：打卡记录/排班/统计 | [attendance.md](./references/products/attendance.md) |
| `calendar` | 日历：日程/参与者/会议室/闲忙查询 | [calendar.md](./references/products/calendar.md) |
| `chat` | 群聊与机器人：搜索群/建群/群成员管理/机器人消息/Webhook | [chat.md](./references/products/chat.md) |
| `contact` | 通讯录：用户查询/部门查询/组织架构 | [contact.md](./references/products/contact.md) |
| `devdoc` | 开放平台文档搜索 | [simple.md](./references/products/simple.md) |
| `ding` | DING消息：发送/撤回（应用内/短信/电话） | [ding.md](./references/products/ding.md) |
| `doc` | 钉钉文档：搜索/读写/上传下载/创建/更新 ⚡PC | [doc.md](./references/products/doc.md) |
| `drive` | 钉盘文件管理：列表/上传/下载/创建文件夹 ⚡PC | [drive.md](./references/products/drive.md) |
| `mail` | 邮箱：收发邮件/邮箱管理 ⚡PC | [mail.md](./references/products/mail.md) |
| `minutes` | AI听记：会议纪要列表/详情/更新 ⚡PC | [minutes.md](./references/products/minutes.md) |
| `aiapp` | AI应用：创建/查询/修改 ⚡PC | [aiapp.md](./references/products/aiapp.md) |
| `conference` | 视频会议：预约/管理 ⚡PC | [conference.md](./references/products/conference.md) |
| `oa` | OA审批：待处理/同意/拒绝/撤销/记录 | [oa.md](./references/products/oa.md) |
| `report` | 日志：按模板创建/收件箱/已发送/模板/统计 | [report.md](./references/products/report.md) |
| `todo` | 待办：创建/查询/修改/标记完成/删除 | [todo.md](./references/products/todo.md) |
| `workbench` | 工作台：应用管理 | [workbench.md](./references/products/workbench.md) |

> ⚡PC 标注的产品由 PC 旧版处理，wrapper 自动路由，用户无感知。

## 意图判断决策树

用户提到"表格/多维表/AI表格/记录/数据" → `aitable`
用户提到"审批/请假/报销/出差/加班/待审批" → `oa`
用户提到"考勤/打卡/排班" → `attendance`
用户提到"日程/日历/会议室/约会" → `calendar`
用户提到"群聊/建群/群成员/群管理/机器人发消息/Webhook/通知" → `chat`
用户提到"通讯录/同事/部门/组织架构" → `contact`
用户提到"开发/API/调用错误文档" → `devdoc`
用户提到"DING/紧急消息/电话提醒" → `ding`
用户提到"文档/钉钉文档/知识库/写文档" → `doc`
用户提到"钉盘/文件/上传文件/下载文件" → `drive`
用户提到"邮件/邮箱/收邮件/发邮件" → `mail`
用户提到"AI听记/会议纪要/录音/听记" → `minutes`
用户提到"AI应用/智能应用" → `aiapp`
用户提到"视频会议/会议预约" → `conference`
用户提到"日志/日报/周报/提交日报/填日志" → `report`
用户提到"待办/TODO/任务提醒" → `todo`
用户提到"工作台/应用管理" → `workbench`

关键区分：`aitable`（数据表格）vs `todo`（待办任务）
关键区分：`report`（钉钉日志/日报周报）vs `todo`（待办任务）
关键区分：`chat` send-by-bot（机器人身份发消息）vs send-by-webhook（自定义机器人Webhook）
关键区分：`doc`（钉钉文档内容）vs `drive`（钉盘文件存储）

> 更多易混淆场景见 [intent-guide.md](./references/intent-guide.md)

## 已知限制与 Bug

| 问题 | 说明 |
|------|------|
| `oa approval list-initiated` 参数报错 | v1.0.8 bug，传任意时间格式均返回"参数错误"，暂时无法使用 |
| `chat message` 无法拉取群聊历史 | 钉钉开放平台硬限制，`message` 子命令只有 send/recall，无 list/history |
| `oa approval list-forms` 需管理员权限 | 非管理员账号调用返回 200002，无法列出所有审批表单 |

## 危险操作确认

以下操作不可逆，执行前必须展示操作摘要并获得用户明确同意，再加 `--yes` 执行：

| 产品 | 命令 | 说明 |
|------|------|------|
| `aitable` | `base delete` | 删除整个 AI 表格 |
| `aitable` | `record delete` | 删除记录（支持批量） |
| `calendar` | `event delete` | 删除日程 |
| `calendar` | `participant delete` | 移除日程参与者 |
| `calendar` | `room delete` | 取消会议室预定 |
| `chat` | `group members remove` | 移除群成员 |
| `todo` | `task delete` | 删除待办 |

### 确认流程
```
Step 1 → 展示操作摘要（操作类型 + 目标对象 + 影响范围）
Step 2 → 用户明确回复确认（如 "确认" / "好的"）
Step 3 → 加 --yes 执行命令
```

## 核心流程

1. **意图分类**：判断用户指令核心动词属于哪个产品
2. **歧义处理**：模糊或多产品关键字时，主动追问
3. **精准映射**：参考产品总览和意图决策树选择产品
4. **充分阅读**：读对应产品参考文件，执行命令

## dws Wrapper（SSH 转发到 Win PC）

当前环境中 `dws` 是一个 SSH wrapper，实际在 Win PC 上执行 `dws.exe`。多行/长文本参数会导致 PowerShell 转义失败，需要走 **文件中转** 方案。

### 多行消息发送（MUST DO）

凡是消息内容包含换行符（`\n`），**不要**直接把文本作为参数传给 dws，必须：

1. 把文本写入本地临时文件
2. `scp` 到 Win PC 的 `AppData/Local/Temp/dws_arg.txt`
3. 在 PowerShell 里用 `Get-Content -Raw` 读取后作为参数传入

当前 wrapper 脚本（`~/.local/bin/dws`）已自动处理此逻辑：检测到参数含 `\n` 时自动走 scp 文件中转，agent 直接传多行字符串即可，无需手动操作。

**示例（shell 变量赋值多行文本后直接调用）：**
```bash
MSG=$'第一行\n第二行\n第三行'
dws chat message send --group "<group_id>" "$MSG" --format json
```

### 单行消息
正常调用，无特殊处理。

### Gotchas
- `send-by-bot` 要求机器人已加入目标群，否则报错；群未加机器人时改用 `chat message send`（以当前用户身份发送）
- 群 ID 即 `openConversationId`（`cid...` 格式），必须从 `dws chat search` 或已知配置中获取，禁止编造
- `send-by-bot` 的 robot-code 默认值：`dingjmwomovvvles2xfc`
- 用户 userId 与 staffId/employeeId 不同，发消息必须用 `dws contact user get-self` 或 `search` 拿到的 userId（`k7ve6n4akc2jtfyzuaojbjzluq` 格式）

## 错误处理

1. 遇到错误，加 `--verbose` 重试一次
2. 仍然失败，报告完整错误信息，禁止自行尝试替代方案
3. 认证失败时，参考 [global-reference.md](./references/global-reference.md) 认证章节
4. 高频错误排查见 [error-codes.md](./references/error-codes.md)

## 详细参考（按需读取）

- [references/products/](./references/products/) — 各产品命令详细参考
- [references/intent-guide.md](./references/intent-guide.md) — 意图路由指南
- [references/global-reference.md](./references/global-reference.md) — 全局标志/认证/输出格式
- [references/field-rules.md](./references/field-rules.md) — AI表格字段类型规则
- [references/error-codes.md](./references/error-codes.md) — 错误码 + 调试流程
- [scripts/](./scripts/) — 各产品批量操作脚本
