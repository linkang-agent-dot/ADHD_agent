"""
notify_done.py — 任务完成后向飞书推送完成通知

用法：
  python notify_done.py --task "任务名" --result "结果摘要" [--agent "Cursor"]

示例：
  python notify_done.py --task "P2导表" --result "成功上传 5 张表" --agent "Cursor"
"""
import argparse
import sys
import os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
import feishu_helper


def main():
    parser = argparse.ArgumentParser(description='发送任务完成飞书通知')
    parser.add_argument('--task', required=True, help='任务名称')
    parser.add_argument('--result', required=True, help='结果摘要')
    parser.add_argument('--agent', default='Cursor', help='Agent 标识（如 Cursor、OpenClaw）')
    args = parser.parse_args()

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[notify_done] 发送完成通知: [{args.agent}] {args.task}')

    ok = feishu_helper.send_done_notification(
        task=args.task,
        result=args.result,
        agent=args.agent,
        timestamp=timestamp
    )

    if ok:
        print(f'[notify_done] ✅ 飞书通知已发送')
        print('{"status": "sent", "task": "' + args.task + '", "timestamp": "' + timestamp + '"}')
    else:
        print(f'[notify_done] ❌ 飞书通知发送失败（详见 stderr）')
        print('{"status": "failed", "task": "' + args.task + '"}')
        sys.exit(1)


if __name__ == '__main__':
    main()
