"""
submit_task.py — 向 Cursor 后台 Agent 提交任务（由 OpenClaw 调用）

用法：
  python submit_task.py --title "任务标题" --instructions "具体指令" [选项]

示例：
  python submit_task.py \\
    --title "生成复活节换皮配置" \\
    --instructions "根据模板生成 ID 21127630 的换皮配置行，参考 config-reskin skill" \\
    --context "活动名: 复活节, 分支: feature/easter-2026" \\
    --model claude-4.6-opus-high-thinking \\
    --notify

参数：
  --title         任务标题（简短）
  --instructions  Cursor Agent 需要执行的具体指令（越详细越好）
  --context       可选的额外上下文信息
  --notify        提交后发飞书通知告知用户任务已入队
  --priority      优先级 high/normal/low（默认 normal）
  --model         指定 Agent 使用的模型（覆盖 daemon 全局默认）
                  例: claude-4.6-opus-high-thinking / gemini-3-flash / gpt-5.3-codex
  --mode          执行模式: plan(只读规划) / ask(问答) / 不填=完整agent
  --sandbox       沙箱模式: enabled / disabled
"""
import argparse
import sys
import os
import json
import uuid
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

INBOX_DIR = r'C:\ADHD_agent\openclaw\workspace\cursor_inbox'


def generate_task_id() -> str:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    short = uuid.uuid4().hex[:6]
    return f'task_{ts}_{short}'


def write_task(task_id: str, title: str, instructions: str, context: str,
               submitted_by: str, priority: str,
               model: str = None, mode: str = None, sandbox: str = None) -> str:
    os.makedirs(INBOX_DIR, exist_ok=True)
    path = os.path.join(INBOX_DIR, f'{task_id}.json')
    data = {
        'task_id': task_id,
        'title': title,
        'instructions': instructions,
        'context': context,
        'submitted_by': submitted_by,
        'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'priority': priority,
        'status': 'pending'
    }
    if model:
        data['model'] = model
    if mode in ('plan', 'ask'):
        data['mode'] = mode
    if sandbox in ('enabled', 'disabled'):
        data['sandbox'] = sandbox
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def list_queue() -> list[dict]:
    """查看当前队列状态"""
    if not os.path.exists(INBOX_DIR):
        return []
    tasks = []
    for fname in sorted(os.listdir(INBOX_DIR)):
        if fname.endswith('.json') and not fname.startswith('_'):
            try:
                with open(os.path.join(INBOX_DIR, fname), 'r', encoding='utf-8') as f:
                    tasks.append(json.load(f))
            except Exception:
                pass
    return tasks


def list_results() -> list[dict]:
    """查看已完成任务结果"""
    outbox = r'C:\ADHD_agent\openclaw\workspace\cursor_outbox'
    if not os.path.exists(outbox):
        return []
    results = []
    for fname in sorted(os.listdir(outbox)):
        if fname.endswith('.json'):
            try:
                with open(os.path.join(outbox, fname), 'r', encoding='utf-8') as f:
                    results.append(json.load(f))
            except Exception:
                pass
    return results


def main():
    parser = argparse.ArgumentParser(description='向 Cursor 后台 Agent 提交任务')
    parser.add_argument('--title', help='任务标题')
    parser.add_argument('--instructions', help='具体执行指令')
    parser.add_argument('--context', default='', help='额外上下文')
    parser.add_argument('--submitted-by', default='OpenClaw', help='提交方标识')
    parser.add_argument('--priority', default='normal', choices=['high', 'normal', 'low'])
    parser.add_argument('--notify', action='store_true', help='提交后发飞书通知')
    parser.add_argument('--list', action='store_true', help='查看任务队列')
    parser.add_argument('--results', action='store_true', help='查看已完成任务结果')
    parser.add_argument('--model', default=None,
                        help='指定 Agent 使用的模型，例: claude-4.6-opus-high-thinking')
    parser.add_argument('--mode', default=None, choices=['plan', 'ask'],
                        help='执行模式: plan=只读规划 / ask=问答 / 不填=完整agent')
    parser.add_argument('--sandbox', default=None, choices=['enabled', 'disabled'],
                        help='沙箱模式开关')
    parser.add_argument('--daily-report', action='store_true',
                        help='快捷指令：生成并提交 AI 提效日报任务')
    parser.add_argument('--daily-report-date', default=None,
                        help='日报日期 YYYYMMDD，默认今天')
    args = parser.parse_args()

    # 快捷：日报
    if args.daily_report:
        daily_script = os.path.join(os.path.dirname(__file__), 'daily_report.py')
        import subprocess
        cmd = [sys.executable, daily_script]
        if args.daily_report_date:
            cmd += ['--date', args.daily_report_date]
        proc = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace', timeout=60)
        print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        sys.exit(proc.returncode)

    # 查看队列
    if args.list:
        tasks = list_queue()
        if not tasks:
            print('[submit_task] 队列为空')
        else:
            print(f'[submit_task] 当前队列（{len(tasks)} 个任务）：')
            for t in tasks:
                status_icon = {'pending': '⏳', 'processing': '🔄', 'done': '✅'}.get(t.get('status', ''), '❓')
                print(f'  {status_icon} [{t["task_id"]}] {t["title"]} ({t.get("status","?")})')
        print(json.dumps({'queue': tasks}, ensure_ascii=False))
        return

    # 查看结果
    if args.results:
        results = list_results()
        if not results:
            print('[submit_task] 暂无已完成任务')
        else:
            print(f'[submit_task] 已完成任务（{len(results)} 个）：')
            for r in results:
                print(f'  ✅ [{r.get("task_id")}] {r.get("title","?")}')
                print(f'     结果: {r.get("result","")[:100]}')
        print(json.dumps({'results': results}, ensure_ascii=False))
        return

    # 提交任务
    if not args.title or not args.instructions:
        parser.error('提交任务时 --title 和 --instructions 为必填项')

    task_id = generate_task_id()
    path = write_task(
        task_id=task_id,
        title=args.title,
        instructions=args.instructions,
        context=args.context,
        submitted_by=args.submitted_by,
        priority=args.priority,
        model=args.model,
        mode=args.mode,
        sandbox=args.sandbox,
    )

    print(f'[submit_task] ✅ 任务已入队')
    print(f'[submit_task] task_id: {task_id}')
    print(f'[submit_task] 文件: {path}')
    print(f'[submit_task] 标题: {args.title}')
    if args.model:
        print(f'[submit_task] 模型: {args.model}')
    if args.mode:
        print(f'[submit_task] 模式: {args.mode}')

    # 可选：发飞书通知
    if args.notify:
        try:
            import feishu_helper
            feishu_helper.send_text(
                f'📋 [{args.submitted_by}] 新任务已提交给 Cursor Agent\n'
                f'任务：{args.title}\n'
                f'task_id：{task_id}\n'
                f'（后台 Agent 会自动处理并通知结果）'
            )
            print('[submit_task] 飞书通知已发送')
        except Exception as e:
            print(f'[submit_task] 飞书通知失败（不影响任务）: {e}', file=sys.stderr)

    print(json.dumps({'status': 'queued', 'task_id': task_id}, ensure_ascii=False))


if __name__ == '__main__':
    main()
