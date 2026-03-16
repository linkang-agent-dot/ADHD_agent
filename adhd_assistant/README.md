# ADHD Task Assistant 🧠

专为 ADHD 用户设计的任务管理助手。通过 Telegram Bot 实现零摩擦任务捕获和主动推送提醒。

## 核心功能

| 功能 | 说明 |
|------|------|
| 📥 零摩擦捕获 | 发消息 = 记录任务，AI 自动解析优先级和时间 |
| 🧠 AI 每日规划 | 每天早上评估负荷，推荐今日必做清单 |
| 🧭 下一步导航 | 完成一个任务后，自动告诉你接下来做什么 |
| ⏰ 定时 Checkpoint | 每 2 小时主动问你进展，防止跑偏 |
| 🫂 情绪支持 | 温暖鼓励、休息提醒、不 PUA |
| 📊 每日复盘 | AI 判断哪些是真忙，哪些是在逃避 |

## 快速开始

### 1. 创建 Telegram Bot

1. 打开 Telegram，搜索 `@BotFather`
2. 发送 `/newbot`，按提示设置名称
3. 复制获得的 Bot Token

### 2. 获取 Gemini API Key

1. 打开 [Google AI Studio](https://aistudio.google.com/apikey)
2. 创建 API Key

### 3. 配置环境

```bash
cd adhd_assistant
cp .env.example .env
```

编辑 `.env` 文件，填入：
- `TELEGRAM_BOT_TOKEN` — 第 1 步获取的 Token
- `GEMINI_API_KEY` — 第 2 步获取的 Key

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 启动

```bash
python main.py
```

### 6. 获取 Chat ID

1. 在 Telegram 中找到你的 Bot，发送 `/start`
2. Bot 会回复你的 Chat ID
3. 将 Chat ID 填入 `.env` 文件的 `TELEGRAM_CHAT_ID`
4. 重启 Bot（定时推送需要 Chat ID）

## 使用方法

### 记录任务
直接发消息给 Bot：
- `明天和策划对需求`
- `紧急 提交活动配置`
- `下周五前写复盘文档`

AI 会自动解析优先级、预估时间和截止日期。

### 快捷命令
| 命令 | 说明 |
|------|------|
| `/today` | 查看今日任务 |
| `/now` | 查看当前正在做的任务 |
| `/plan` | AI 帮你规划今天 |
| `/review` | 今日复盘 |
| `/help` | 帮助信息 |

### 快捷文字
| 文字 | 说明 |
|------|------|
| `完成` / `做完了` | 完成当前任务 |
| `休息` / `累了` | 休息提醒 |
| `今天` | 同 /today |
| `现在` | 同 /now |

## 配置项

在 `.env` 文件中可调整：

| 配置 | 默认值 | 说明 |
|------|--------|------|
| `MORNING_REPORT_HOUR` | 9 | 早报推送时间（小时） |
| `MORNING_REPORT_MINUTE` | 0 | 早报推送时间（分钟） |
| `CHECKPOINT_INTERVAL` | 120 | Checkpoint 间隔（分钟） |
| `REST_REMINDER_INTERVAL` | 90 | 连续工作提醒休息（分钟） |
| `TIMEZONE` | Asia/Shanghai | 时区 |

## 技术栈

- **Telegram Bot**: python-telegram-bot v21+
- **AI**: Google Gemini 2.0 Flash
- **数据库**: SQLite (aiosqlite)
- **调度**: python-telegram-bot JobQueue
