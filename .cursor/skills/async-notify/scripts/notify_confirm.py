"""
notify_confirm.py — 向飞书发送需确认通知，并轮询等待用户回复

用法：
  python notify_confirm.py --task "任务名" --question "需要确认的问题" [--agent "Cursor"] [--timeout 600]

返回（最后一行 JSON）：
  {"decision": "yes", "reply": "用户回复原文", "task_id": "...", "elapsed": 12}
  {"decision": "no",  "reply": "用户回复原文", "task_id": "...", "elapsed": 30}
  {"decision": "timeout", "reply": "", "task_id": "...", "elapsed": 600}

示例：
  python notify_confirm.py --task "合并分支" --question "是否合并 feature/easter 到 main？" --agent "Cursor"
"""
import argparse
import sys
import os
import json
import time
import uuid
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
import feishu_helper

PENDING_DIR = r'C:\ADHD_agent\openclaw\workspace\async_tasks\pending'
CONFIRMED_DIR = r'C:\ADHD_agent\openclaw\workspace\async_tasks\confirmed'
POLL_INTERVAL = 5  # 秒


def generate_task_id() -> str:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    short = uuid.uuid4().hex[:6]
    return f'confirm_{ts}_{short}'


def write_pending(task_id: str, task: str, question: str, agent: str, timestamp: str):
    os.makedirs(PENDING_DIR, exist_ok=True)
    path = os.path.join(PENDING_DIR, f'{task_id}.json')
    data = {
        'task_id': task_id,
        'task': task,
        'question': question,
        'agent': agent,
        'timestamp': timestamp,
        'status': 'pending'
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def poll_confirmed(task_id: str, timeout: int) -> dict:
    confirmed_path = os.path.join(CONFIRMED_DIR, f'{task_id}.json')
    start = time.time()
    while True:
        elapsed = int(time.time() - start)
        if os.path.exists(confirmed_path):
            try:
                with open(confirmed_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data['elapsed'] = elapsed
                return data
            except Exception:
                pass
        if elapsed >= timeout:
            return {'decision': 'timeout', 'reply': '', 'task_id': task_id, 'elapsed': elapsed}
        remaining = timeout - elapsed
        print(f'[notify_confirm] ⏳ 等待用户回复... 已等 {elapsed}s / 超时 {timeout}s（剩余 {remaining}s）', flush=True)
        time.sleep(POLL_INTERVAL)


def cleanup_pending(task_id: str):
    path = os.path.join(PENDING_DIR, f'{task_id}.json')
    if os.path.exists(path):
        os.remove(path)


def main():
    parser = argparse.ArgumentParser(description='发送飞书确认请求并等待回复')
    parser.add_argument('--task', required=True, help='任务名称')
    parser.add_argument('--question', required=True, help='需要用户确认的问题')
    parser.add_argument('--agent', default='Cursor', help='Agent 标识')
    parser.add_argument('--timeout', type=int, default=600, help='最长等待秒数（默认 600 = 10分钟）')
    args = parser.parse_args()

    task_id = generate_task_id()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f'[notify_confirm] task_id: {task_id}')
    print(f'[notify_confirm] 任务: {args.task}')
    print(f'[notify_confirm] 问题: {args.question}')

    # 1. 写入 pending 文件（让 OpenClaw 可以识别待处理任务）
    pending_path = write_pending(task_id, args.task, args.question, args.agent, timestamp)
    print(f'[notify_confirm] 已写入 pending: {pending_path}')

    # 2. 发送飞书通知
    ok = feishu_helper.send_confirm_notification(
        task=args.task,
        question=args.question,
        agent=args.agent,
        task_id=task_id,
        timestamp=timestamp
    )

    if ok:
        print(f'[notify_confirm] ✅ 飞书通知已发送，开始等待回复...')
    else:
        print(f'[notify_confirm] ⚠️ 飞书通知发送失败，但仍会等待本地确认文件...', file=sys.stderr)

    # 3. 轮询等待确认
    result = poll_confirmed(task_id, args.timeout)

    # 4. 清理 pending 文件
    cleanup_pending(task_id)

    # 5. 输出结果（最后一行是机器可读的 JSON）
    decision = result.get('decision', 'timeout')
    reply = result.get('reply', '')
    elapsed = result.get('elapsed', 0)

    if decision == 'yes':
        print(f'[notify_confirm] ✅ 用户已确认: "{reply}" ({elapsed}s)')
    elif decision == 'no':
        print(f'[notify_confirm] ❌ 用户已拒绝: "{reply}" ({elapsed}s)')
    elif decision == 'timeout':
        print(f'[notify_confirm] ⏰ 等待超时 ({elapsed}s)，未收到回复')
    else:
        print(f'[notify_confirm] 💬 用户回复: "{reply}" ({elapsed}s)')

    # 最后一行输出机器可读 JSON（供调用方 parse）
    output = {'decision': decision, 'reply': reply, 'task_id': task_id, 'elapsed': elapsed}
    print(json.dumps(output, ensure_ascii=False))

    # 发送回执通知到飞书
    if decision != 'timeout':
        feishu_helper.send_text(
            f'✅ 已收到你的回复，Cursor Agent 正在继续执行。\n'
            f'任务：{args.task}\n决策：{"✅ 确认" if decision == "yes" else "❌ 拒绝"}\n你的回复：{reply}',
        )


if __name__ == '__main__':
    main()
