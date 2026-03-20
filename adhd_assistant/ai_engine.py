"""
AI Engine — the brain and heart of the ADHD assistant.

Responsibilities:
  - Daily planning: assess workload, prioritize, recommend must-do list
  - Next-task navigation: after completing a task, suggest what's next with context
  - Procrastination detection: analyze postpone patterns
  - Emotional support: warm, non-judgmental tone throughout
"""

import json
import logging
from datetime import datetime
from openai import AsyncOpenAI
from config import Config

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=Config.AI_API_KEY, base_url=Config.AI_BASE_URL)
MODEL = Config.AI_MODEL

SYSTEM_PROMPT = """你是一个专为 ADHD 用户设计的任务助手。你的核心身份：温暖的教练 + 诚实的伙伴。

## 你的性格
- 温暖、有幽默感、像一个懂你的好朋友
- 诚实但不刻薄——该指出问题时会指出，但永远带着理解
- 懂 ADHD：知道跑偏、拖延、忘事是大脑特点，不是人品问题
- 用简短的中文回复，不要长篇大论，ADHD 用户看不完长文
- 适当用 emoji 让消息更有温度，但不要过度

## 你的原则
1. 永远不 PUA：没完成 ≠ 你不行，是计划需要调整
2. 小步也是进步：完成 1 件也值得表扬
3. 休息是生产力：主动建议休息
4. 给退路：任何时候都可以说"今天不行了"
5. 一次只给一个下一步：不要信息过载

## 回复格式
- 使用简洁的文本格式，适合 Telegram 显示
- 用 emoji 做视觉分隔
- 核心信息放在最前面
"""

PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "⚪"}


async def _ask_ai(prompt: str, with_system: bool = True) -> str | None:
    """Call LLM API with error handling. Returns None on failure."""
    try:
        messages = []
        if with_system:
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.append({"role": "user", "content": prompt})
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error("AI call failed: %s", e)
        return None


async def plan_daily(tasks: list[dict]) -> str:
    if not tasks:
        return "📋 今天没有待办任务\n\n想加点什么？直接发消息给我就行"

    tasks_desc = "\n".join(
        f"- [{t['id']}] {t['title']} | 优先级:{t['priority']} | "
        f"预估:{t.get('estimated_minutes', 0)}分钟 | "
        f"推迟次数:{t.get('postpone_count', 0)} | "
        f"截止:{t.get('deadline', '无')}"
        for t in tasks
    )

    prompt = f"""现在是 {datetime.now().strftime('%Y-%m-%d %H:%M')}

以下是用户所有待处理的任务：
{tasks_desc}

请你：
1. 评估今天的工作负荷（假设有效工作时间 6 小时）
2. 按「紧急+重要+阻塞关系」排序
3. 推荐今日必做清单（不超过 4-5 件）
4. 如果超载了，明确告诉用户哪些可以推迟，不要让他们有心理负担
5. 给出简短的开工鼓励

回复格式示例：
📋 今日规划

📊 负荷评估：X 件事 / 约 X 小时 / [轻松/适中/有点满/超载]

🎯 今日必做：
1. 🔴 任务名 (预估Xmin) — 原因
2. ...

📌 可以推迟：
- 任务名 — 原因

💪 [一句简短鼓励]"""

    result = await _ask_ai(prompt)
    if result:
        return result

    # fallback: simple list
    lines = ["📋 今日任务（AI 暂时离线，简单列一下）\n"]
    high = [t for t in tasks if t["priority"] == "high"]
    medium = [t for t in tasks if t["priority"] == "medium"]
    low = [t for t in tasks if t["priority"] == "low"]
    for label, group in [("🔴 高优先", high), ("🟡 中优先", medium), ("⚪ 低优先", low)]:
        for t in group:
            est = f" ({t['estimated_minutes']}min)" if t.get("estimated_minutes") else ""
            lines.append(f"  {label} {t['title']}{est}")
    lines.append(f"\n共 {len(tasks)} 件事，加油 💪")
    return "\n".join(lines)


async def navigate_next(
    completed_task: dict,
    remaining_tasks: list[dict],
    today_stats: dict,
) -> str:
    if not remaining_tasks:
        stats = today_stats
        return (
            f"🎉 今天所有任务都搞定了！\n\n"
            f"完成了 {stats['completed']} 件事，工作了约 {stats['work_minutes']} 分钟\n"
            f"你今天很棒，去做点让自己开心的事吧 🌟"
        )

    tasks_desc = "\n".join(
        f"- [{t['id']}] {t['title']} | 优先级:{t['priority']} | "
        f"预估:{t.get('estimated_minutes', 0)}分钟 | "
        f"推迟次数:{t.get('postpone_count', 0)}"
        for t in remaining_tasks
    )

    prompt = f"""用户刚完成了任务：「{completed_task['title']}」
今日已完成 {today_stats['completed']} 件，剩余 {today_stats['remaining']} 件
已工作 {today_stats['work_minutes']} 分钟

剩余任务：
{tasks_desc}

请你：
1. 先简短表扬完成任务（1句话，有温度）
2. 如果已经连续工作超过 90 分钟，建议先休息 5 分钟
3. 推荐下一个该做的任务，说明为什么选它（1句话）
4. 如果该任务有上次的进度备注，提醒用户之前做到哪了

回复要简短，不超过 5 行。在最后标注推荐任务的 ID，格式：[NEXT:数字]"""

    result = await _ask_ai(prompt)
    if result:
        return result

    # fallback
    next_t = remaining_tasks[0]
    return (
        f"✅ 「{completed_task['title']}」搞定！\n\n"
        f"▶️ 下一件：{next_t['title']}\n"
        f"[NEXT:{next_t['id']}]"
    )


async def checkpoint_assess(
    current_task: dict | None,
    user_response: str,
    today_stats: dict,
) -> str:
    task_info = (
        f"当前正在做的任务：「{current_task['title']}」"
        if current_task
        else "当前没有在做任何任务"
    )

    prompt = f"""Checkpoint 时间到了。
{task_info}
用户回复：「{user_response}」
今日已完成 {today_stats['completed']} 件，剩余 {today_stats['remaining']} 件

请你：
1. 判断用户是否还在做该做的事（on_track: true/false）
2. 如果跑偏了，温和地提醒拉回来，不要指责
3. 如果在做别的事，评估那件事是否更重要
4. 如果用户表示累了，建议休息或调整计划

回复简短，不超过 4 行。
在末尾附上 JSON 标记：[TRACK:{{"on_track": true/false}}]"""

    result = await _ask_ai(prompt)
    if result:
        return result
    return "收到！继续加油 💪 [TRACK:{\"on_track\": true}]"


async def daily_review(tasks: list[dict], stats: dict) -> str:
    completed = [t for t in tasks if t["status"] == "completed"]
    not_done = [t for t in tasks if t["status"] in ("pending", "in_progress", "postponed")]

    completed_desc = "\n".join(f"- ✅ {t['title']}" for t in completed) or "- 无"
    not_done_desc = "\n".join(
        f"- ❌ {t['title']} (推迟{t['postpone_count']}次)" for t in not_done
    ) or "- 无"

    prompt = f"""今天结束了，以下是今天的情况：

已完成：
{completed_desc}

未完成：
{not_done_desc}

工作总时长：{stats['work_minutes']} 分钟

请你：
1. 给出总体评价（要诚实但温暖）
2. 对每个未完成的任务判断：是真的做不完，还是在逃避？
3. 如果有反复推迟的任务，建议拆分成小步骤
4. 给一句温暖的收工祝福
5. 如果完成率低，安慰为主，不要批判

回复不超过 10 行。"""

    result = await _ask_ai(prompt)
    if result:
        return result

    # fallback
    total = len(completed) + len(not_done)
    return (
        f"📊 今日完成 {len(completed)}/{total}\n\n"
        f"已完成：\n{completed_desc}\n\n"
        f"未完成：\n{not_done_desc}\n\n"
        f"辛苦了，早点休息 🌙"
    )


async def classify_message(user_text: str, context_info: str = "") -> dict:
    """Classify user message into: task / command / settings / chat."""
    today_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    prompt = f"""# 意图分类

你是 ADHD 用户的 Telegram 任务助手。根据用户消息和当前上下文，判断意图并返回JSON。

## 当前上下文
{context_info}
当前时间: {today_str}

## 助手功能概览
任务记录 | AI每日规划 | 完成导航 | 定时Checkpoint | 喝水提醒 | 午休/晚休提醒 | 每日复盘 | 连续工作提醒 | 情绪支持 | 设置修改
命令: /today /now /plan /review /help /settings

## 四种意图及返回格式

**task** — 用户描述了一件需要去做的事（不是已完成的事）
{{"intent":"task","title":"简洁标题","priority":"high/medium/low","estimated_minutes":数字,"deadline":null或"YYYY-MM-DD","progress_note":"已有进度描述或null"}}

**command** — 用户想触发一个操作（查看/完成/休息/规划等）
可用: today, now, plan, review, complete, rest, help, settings
{{"intent":"command","command":"命令名"}}

**settings** — 用户想修改某个配置项的值
可改: morning_hour, morning_minute, checkpoint_interval, rest_interval
{{"intent":"settings","key":"设置项","value":"新值","confirm_text":"确认描述"}}

**chat** — 闲聊、提问、反馈，不属于以上三种
{{"intent":"chat","reply":"基于功能和上下文的具体有用回复，2-4句"}}

## 核心判断原则

1. **意图看本质**：不要匹配关键词，要理解用户真正想干什么。"交接完成了"是在说做完了（complete），不是在创建新任务。
2. **上下文优先**：用户的消息可能很短或有指代（"这个""它""记一下"），必须结合「最近对话」和「当前状态」来理解。
3. **完成 vs 新任务**：用户说某事"完成了/搞定了/做完了/弄好了/OK了" → command:complete。用户说"要做XX/帮我记XX" → task。区别在于事情是【已完成】还是【将要做】。
4. **规划类**：用户问接下来做什么、该做什么、排优先级 → command:plan
5. **设置类**：用户想调整时间/间隔/频率，通常含"改""调""太早/太晚/太频繁" → settings
6. **chat 回复质量**：必须基于助手的真实功能回答，不要编造不存在的能力。回复要具体、有温度。

## 格式示例（仅展示格式，不是穷举）

"提交活动配置" → {{"intent":"task","title":"提交活动配置","priority":"medium","estimated_minutes":30,"deadline":null,"progress_note":null}}
"做完了" → {{"intent":"command","command":"complete"}}
"帮我规划一下" → {{"intent":"command","command":"plan"}}
"早报改到10点" → {{"intent":"settings","key":"morning_hour","value":"10","confirm_text":"早报时间改为 10:00"}}
"你有什么功能" → {{"intent":"chat","reply":"..."}}

用户消息: "{user_text}"

只返回一行JSON，不要其他任何文字。"""

    result = await _ask_ai(prompt, with_system=False)
    if result:
        text = result.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0].strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            text = text[start:end]
        try:
            parsed = json.loads(text)
            intent = parsed.get("intent")
            logger.info("classify_message: input=%r → intent=%s", user_text, intent)
            if intent in ("task", "chat", "settings", "command"):
                return parsed
        except json.JSONDecodeError:
            logger.warning("classify_message: failed to parse JSON: %s", text)

    # fallback heuristics
    text_lower = user_text.lower().strip()

    settings_keywords = ("改成", "调成", "调整", "太早", "太晚", "太频繁", "间隔", "改到", "设置")
    if any(kw in text_lower for kw in settings_keywords):
        return {"intent": "command", "command": "settings"}

    command_hints = {
        "today": ("任务", "剩下", "还有", "列表", "今天", "今日", "待办"),
        "now": ("当前", "正在做", "在做"),
        "plan": ("规划", "计划", "安排", "该做什么", "干什么", "推荐", "清单", "建议", "排序", "优先级", "先做"),
        "review": ("复盘", "总结", "怎么样"),
        "complete": ("完成", "做完", "搞定", "done"),
        "rest": ("休息", "歇", "累"),
        "settings": ("设置",),
    }
    for cmd, keywords in command_hints.items():
        if any(kw in text_lower for kw in keywords):
            return {"intent": "command", "command": cmd}

    question_markers = ("?", "？", "吗", "呢", "什么", "怎么", "哪", "谁", "为什么", "是不是", "能不能", "可以吗")
    chat_markers = ("你好", "hello", "hi", "嗨", "dd", "谢谢", "哈哈", "嗯", "好的", "ok", "不错", "可以")

    if any(m in text_lower for m in question_markers):
        return {"intent": "chat", "reply": "我是你的 ADHD 任务助手 🧠\n\n直接发消息给我就能记录任务\n发 /help 查看完整用法"}
    if text_lower in chat_markers or len(text_lower) <= 3:
        return {"intent": "chat", "reply": "在的！有什么需要记录的吗？💬"}

    priority = "medium"
    for kw in ("紧急", "马上", "立刻", "urgent", "asap"):
        if kw in text_lower:
            priority = "high"
            break
    return {
        "intent": "task",
        "title": user_text[:50],
        "description": "",
        "priority": priority,
        "estimated_minutes": 0,
        "deadline": None,
    }


async def water_praise() -> str:
    """Generate a unique, creative praise for drinking water."""
    prompt = """用户刚喝了一杯水，请生成一条有趣、独特的正反馈夸奖。

要求：
- 用中文，简短（1-3句话）
- 有趣、有创意、不要套话
- 可以用比喻、冷知识、幽默、夸张、游戏梗、动漫梗、职场梗等任意风格
- 让用户觉得喝水是一件很酷的事
- 可以加 1-2 个 emoji
- 每次都要不一样，不要重复

示例风格参考（不要照抄）：
- "你刚才喝的那口水，正在以光速滋润你的 860 亿个脑细胞 🧠💧"
- "恭喜你获得成就：[今日续命成功] 🏆"
- "+1 水分 buff，注意力 +10%，心情 +5%，饮料抗性 +20%"
- "这杯水的 ROI 比你买的任何奶茶都高"
- "你的肾脏发来感谢信：谢谢主人选择了水 💌"

直接返回文字，不要其他格式。"""

    result = await _ask_ai(prompt, with_system=False)
    if result:
        return f"💧 {result.strip()}"
    return "💧 好样的！每一口水都是在给自己充电 🔋"


async def water_scold() -> str:
    """Generate a playful scolding for drinking soda instead of water."""
    prompt = """用户承认自己喝了饮料而不是水，请生成一条幽默的"吐槽"。

要求：
- 用中文，简短（1-3句话）
- 语气是朋友间的玩笑吐槽，不是真的骂人
- 幽默、有梗、让人笑着反省
- 最后引导他去喝一杯水补救
- 可以加 1-2 个 emoji
- 每次不一样

示例风格参考（不要照抄）：
- "好家伙，你的血管正在变成可乐管道 🥤 快去喝杯水冲一冲"
- "饮料：让你开心 3 分钟的昂贵糖水。现在去喝杯免费的水补救一下"
- "你的身体正在处理你灌进去的糖分，它表示很累。去倒杯水安慰一下它"

直接返回文字，不要其他格式。"""

    result = await _ask_ai(prompt, with_system=False)
    if result:
        return f"🥤 {result.strip()}\n\n现在去补一杯水吧 💧"
    return "🥤 饮料不算喝水哦！去补一杯真正的水吧 💧"


async def get_encouragement(task_title: str, tasks_done_today: int) -> str:
    prompts = {
        0: f"开始今天第一件事「{task_title}」！\n万事开头难，开始了就成功一半 💪",
        1: f"第 2 件了！「{task_title}」\n节奏不错，继续保持 🎯",
        2: f"第 3 件！「{task_title}」\n你今天状态很好啊 🔥",
    }
    if tasks_done_today in prompts:
        return prompts[tasks_done_today]
    return f"继续！「{task_title}」\n今天已经搞定 {tasks_done_today} 件了，你太行了 🌟"


async def rest_reminder(work_minutes: int) -> str:
    if work_minutes >= 180:
        return (
            "🛑 你已经连续工作 3 小时了！\n\n"
            "这不是建议，是命令：站起来走走 🚶\n"
            "喝水、伸懒腰、看看远处\n"
            "大脑需要真正地休息一下"
        )
    elif work_minutes >= 120:
        return (
            "☕ 连续工作 2 小时了\n\n"
            "你很专注，但也该歇一歇了\n"
            "起来活动 5 分钟，回来效率更高"
        )
    else:
        return (
            "☕ 工作一阵子了，要不要休息一下？\n\n"
            "哪怕站起来倒杯水也好\n"
            "小休息 = 大能量"
        )
