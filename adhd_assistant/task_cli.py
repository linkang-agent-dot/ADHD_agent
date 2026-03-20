"""
ADHD Task CLI — command-line interface to task management for OpenClaw exec.

Usage:
  python task_cli.py add "任务标题" [--priority high/medium/low] [--minutes 30] [--note "进度"]
  python task_cli.py list
  python task_cli.py now
  python task_cli.py start <task_id>
  python task_cli.py complete
  python task_cli.py postpone <task_id>
  python task_cli.py progress <task_id> "进度描述"
  python task_cli.py plan
  python task_cli.py review
  python task_cli.py settings
  python task_cli.py set <key> <value>
  python task_cli.py reward
"""

import sys
import os
import argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DB_PATH", os.path.join(os.path.dirname(__file__), "adhd.db"))

from mcp_server import (
    add_task, list_today_tasks, get_current_task, start_task,
    complete_current_task, postpone_task, save_progress,
    plan_today, daily_review, get_settings, update_setting,
    send_reward_image,
)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "add":
        parser = argparse.ArgumentParser()
        parser.add_argument("cmd")
        parser.add_argument("title")
        parser.add_argument("--priority", default="medium")
        parser.add_argument("--minutes", type=int, default=0)
        parser.add_argument("--deadline", default=None)
        parser.add_argument("--note", default=None)
        args = parser.parse_args()
        print(add_task(args.title, args.priority, args.minutes, args.deadline, args.note))

    elif cmd == "list":
        print(list_today_tasks())

    elif cmd == "now":
        print(get_current_task())

    elif cmd == "start":
        if len(sys.argv) < 3:
            print("需要提供 task_id")
            return
        print(start_task(int(sys.argv[2])))

    elif cmd == "complete":
        print(complete_current_task())

    elif cmd == "postpone":
        if len(sys.argv) < 3:
            print("需要提供 task_id")
            return
        print(postpone_task(int(sys.argv[2])))

    elif cmd == "progress":
        if len(sys.argv) < 4:
            print("需要提供 task_id 和 note")
            return
        print(save_progress(int(sys.argv[2]), " ".join(sys.argv[3:])))

    elif cmd == "plan":
        print(plan_today())

    elif cmd == "review":
        print(daily_review())

    elif cmd == "settings":
        print(get_settings())

    elif cmd == "set":
        if len(sys.argv) < 4:
            print("需要提供 key 和 value")
            return
        print(update_setting(sys.argv[2], sys.argv[3]))

    elif cmd == "reward":
        print(send_reward_image())

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
