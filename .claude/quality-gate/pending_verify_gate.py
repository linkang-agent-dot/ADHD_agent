#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收工拦门 (Stop hook)。被 ~/.claude/settings.json 的 Stop hook 调用。
逻辑极简、且对自身错误 fail-open——绝不因为脚本 bug 卡住你所有的活：

  看 ~/.claude/.pending_verify/ 里有没有 status=pending 的 marker：
    - 有  -> 拦住收工，提示主 Claude 去派 design-doc-checker 验收
    - 没有 / 都已 reviewed -> 放行（normal 情况，静默退出）
    - 脚本自己出任何错 -> 放行（不拖累日常工作）

marker = ~/.claude/.pending_verify/<任务>.json，内容形如
  {"task": "深海节策划案", "sheet_id": "1AbC...", "status": "pending"}
status 只有两种：
  pending  = 产物输出了但还没验收（要拦）
  reviewed = 验收员跑过了，有 blocker 待用户定夺（放行，让 Claude 把问题交给用户）
marker 的建/删/改由主 Claude 负责，本脚本只读不写。

注：marker 目录固定在用户全局 ~/.claude/.pending_verify（运行时状态，不随本仓库走）。
"""
import sys, os, json, glob

# 强制 UTF-8 输出：Windows 上 Python 3.14 默认按 GBK 写 stdout，
# 而 Claude Code 按 UTF-8 读 hook 输出，不强制会让中文 reason 乱码。
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def main():
    home = os.path.expanduser("~")
    pend_dir = os.path.join(home, ".claude", ".pending_verify")
    if not os.path.isdir(pend_dir):
        return  # 没有目录 = 没有待验收的活，放行

    pending = []
    for fp in glob.glob(os.path.join(pend_dir, "*.json")):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                m = json.load(f)
        except Exception:
            continue  # 坏 marker 跳过，不拦
        if str(m.get("status", "pending")).lower() == "pending":
            pending.append(m.get("task") or os.path.basename(fp))

    if not pending:
        return  # 全部已验收/无待办，放行

    tasks = "、".join(pending)
    reason = (
        f"以下产物还没过验收，先别收工：{tasks}。\n"
        f"请对每个派子 agent task-checker（传 marker 里的 type + 产物位置 + 任务名）跑验收，并按结果处理：\n"
        f"  · 全部通过 -> 删除 ~/.claude/.pending_verify/ 下对应 marker，再收工；\n"
        f"  · 发现 blocker -> 把 marker 的 status 改成 \"reviewed\"，把问题列给用户决定『修 / 跳过』；\n"
        f"  · 实在读不到产物/验收员跑不了 -> 同样改 reviewed，并明确告诉用户『验收没跑成，需人工确认』，不要假装通过。"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        # 任何意外都放行：这个门只负责提醒，绝不允许自己的 bug 卡住用户全部工作
        pass
    sys.exit(0)
