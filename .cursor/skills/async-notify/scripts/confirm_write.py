"""
confirm_write.py — 由 OpenClaw（虾哥）调用，将用户的飞书回复写入本地确认文件

用法：
  python confirm_write.py --task-id "confirm_20260330_142301_abc123" --decision yes --reply "确认，继续"
  python confirm_write.py --task-id "confirm_20260330_142301_abc123" --decision no --reply "取消吧"

参数：
  --task-id   任务 ID（从飞书消息中找到，格式 confirm_YYYYMMDD_HHMMSS_xxxxxx）
  --decision  yes / no / custom（custom 时以 --reply 原文为准）
  --reply     用户回复原文（可选）

支持的 decision 别名：
  yes:  是、yes、y、确认、同意、继续、ok、好、行、可以
  no:   否、no、n、不、取消、拒绝、算了、停、cancel

虾哥也可以直接解析用户的自然语言回复，只需传 --decision auto --reply "用户原文"，
脚本会自动识别 yes/no。
"""
import argparse
import sys
import os
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

CONFIRMED_DIR = r'C:\ADHD_agent\openclaw\workspace\async_tasks\confirmed'
PENDING_DIR = r'C:\ADHD_agent\openclaw\workspace\async_tasks\pending'

YES_WORDS = {'是', 'yes', 'y', '确认', '同意', '继续', 'ok', '好', '行', '可以', '嗯', '没问题', '执行', '批准'}
NO_WORDS  = {'否', 'no', 'n', '不', '取消', '拒绝', '算了', '停', 'cancel', '不行', '不要', '停止', '放弃'}


def auto_detect_decision(reply: str) -> str:
    """根据用户回复自动识别 yes/no"""
    text = reply.strip().lower()
    for w in YES_WORDS:
        if w in text:
            return 'yes'
    for w in NO_WORDS:
        if w in text:
            return 'no'
    # 无法识别，默认当作自定义回复（不是 yes/no）
    return 'custom'


def find_pending_task(task_id: str) -> dict | None:
    path = os.path.join(PENDING_DIR, f'{task_id}.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def list_pending_tasks() -> list[dict]:
    """列出所有待确认任务（供虾哥展示给用户）"""
    tasks = []
    if not os.path.exists(PENDING_DIR):
        return tasks
    for fname in os.listdir(PENDING_DIR):
        if fname.endswith('.json'):
            try:
                with open(os.path.join(PENDING_DIR, fname), 'r', encoding='utf-8') as f:
                    tasks.append(json.load(f))
            except Exception:
                pass
    return sorted(tasks, key=lambda x: x.get('timestamp', ''))


def main():
    parser = argparse.ArgumentParser(description='写入用户确认结果（由 OpenClaw 调用）')
    parser.add_argument('--task-id', required=False, help='任务 ID')
    parser.add_argument('--decision', default='auto', help='yes / no / auto / custom')
    parser.add_argument('--reply', default='', help='用户回复原文')
    parser.add_argument('--list', action='store_true', help='列出所有待确认任务')
    args = parser.parse_args()

    # 列出待确认任务
    if args.list:
        tasks = list_pending_tasks()
        if not tasks:
            print('[confirm_write] 当前没有待确认的任务')
        else:
            print(f'[confirm_write] 待确认任务（共 {len(tasks)} 个）：')
            for t in tasks:
                print(f'  • [{t["task_id"]}]')
                print(f'    任务：{t["task"]}')
                print(f'    问题：{t["question"]}')
                print(f'    来自：{t["agent"]}')
                print(f'    时间：{t["timestamp"]}')
        print(json.dumps({'pending': tasks}, ensure_ascii=False))
        return

    if not args.task_id:
        print('[confirm_write] 错误：需要提供 --task-id 或 --list', file=sys.stderr)
        sys.exit(1)

    task_id = args.task_id
    reply = args.reply.strip()
    decision = args.decision.lower()

    # auto 模式：根据回复自动识别
    if decision == 'auto':
        decision = auto_detect_decision(reply)
        print(f'[confirm_write] 自动识别决策: "{reply}" → {decision}')

    # 验证 task_id 是否存在
    pending = find_pending_task(task_id)
    if pending:
        print(f'[confirm_write] 找到待确认任务: {pending["task"]}')
    else:
        print(f'[confirm_write] ⚠️ 未找到 pending 任务 {task_id}（可能已超时或被处理）', file=sys.stderr)

    # 写入确认文件
    os.makedirs(CONFIRMED_DIR, exist_ok=True)
    confirmed_path = os.path.join(CONFIRMED_DIR, f'{task_id}.json')
    data = {
        'task_id': task_id,
        'decision': decision,
        'reply': reply,
        'confirmed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'task_info': pending or {}
    }
    with open(confirmed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f'[confirm_write] ✅ 已写入确认文件: {confirmed_path}')
    print(f'[confirm_write] 决策: {decision} | 回复: {reply}')
    print(json.dumps({'status': 'written', 'task_id': task_id, 'decision': decision}, ensure_ascii=False))


if __name__ == '__main__':
    main()
