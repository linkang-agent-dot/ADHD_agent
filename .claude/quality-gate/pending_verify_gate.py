#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收工拦门 (Stop hook)。两道，均 fail-open（任何错都放行，绝不卡死收工）：
  道1 · 验收 marker：~/.claude/.pending_verify/ 有 status=pending 的 marker → 拦，提示派 task-checker。
  道2 · 收工自检（反馈循环 + 归档）：本次会话动过文件(Write/Edit) 且没刚拦过 → 拦一次，
        提醒过「新规律沉淀 / 产物归档 / 复用工具」三问——不靠用户提醒（feedback_proactive_knowledge_update）。
  防死循环：道2 拦一次后写时间戳，180s 内 或 stop_hook_active=true → 不再拦。
被 ~/.claude/settings.json 的 Stop hook 调用，input(JSON) 从 stdin 进。
marker 的建/删/改由主 Claude 负责，本脚本只读不写（仅道2 写自己的时间戳便利贴）。
"""
import sys, os, json, glob, time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def read_input():
    try:
        data = sys.stdin.read()
        return json.loads(data) if data and data.strip() else {}
    except Exception:
        return {}

def pending_tasks(pend_dir):
    out = []
    if not os.path.isdir(pend_dir):
        return out
    for fp in glob.glob(os.path.join(pend_dir, "*.json")):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                m = json.load(f)
        except Exception:
            continue
        if str(m.get("status", "pending")).lower() == "pending":
            out.append(m.get("task") or os.path.basename(fp))
    return out

def had_substantial_work(tp):
    """本次会话 transcript 里出现过 Write/Edit/NotebookEdit → 视为有实质改动（值得收工自检）。"""
    if not tp or not os.path.isfile(tp):
        return False
    try:
        if os.path.getsize(tp) > 30 * 1024 * 1024:  # 超大 transcript 跳过判断，保守当无（防超时）
            return False
        with open(tp, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
    except Exception:
        return False
    return ('"Write"' in txt) or ('"Edit"' in txt) or ('"NotebookEdit"' in txt)

def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))

def main():
    inp = read_input()
    home = os.path.expanduser("~")
    pend_dir = os.path.join(home, ".claude", ".pending_verify")

    # 道1 · 验收 marker（有 pending 就拦）
    pend = pending_tasks(pend_dir)
    if pend:
        tasks = "、".join(pend)
        block(
            f"以下产物还没过验收，先别收工：{tasks}。\n"
            f"对每个派子 agent task-checker（传 marker 里的 type + 产物位置 + 任务名）跑验收，并按结果处理：\n"
            f"  · 全部通过 -> 删除 ~/.claude/.pending_verify/ 下对应 marker，再收工；\n"
            f"  · 发现 blocker -> 把 marker 的 status 改成 \"reviewed\"，把问题列给用户决定『修 / 跳过』；\n"
            f"  · 实在读不到产物/验收员跑不了 -> 同样改 reviewed，并明确告诉用户『验收没跑成，需人工确认』，不要假装通过。"
        )
        return

    # 道2 · 收工自检（反馈循环 + 归档）—— 仅本次动过文件，且防死循环
    if not had_substantial_work(inp.get("transcript_path", "")):
        return  # 纯对话/没动文件 → 放行
    if inp.get("stop_hook_active", False):
        return  # 已因 hook 继续过 → 放行避免死循环
    ts_file = os.path.join(pend_dir, ".codify_check_ts")
    now = time.time()
    try:
        if os.path.exists(ts_file) and (now - os.path.getmtime(ts_file) < 180):
            return  # 180s 内拦过 → 放行避免连环拦
    except Exception:
        pass
    try:
        os.makedirs(pend_dir, exist_ok=True)
        with open(ts_file, "w", encoding="utf-8") as f:
            f.write(str(now))
    except Exception:
        pass
    block(
        "收工前过一遍自检（这次动过文件，可能有该沉淀/归档的）——做过或不适用就一句话说明再收工，别等用户提醒：\n"
        "  1. 反馈循环：有没有新规律 / 踩坑 / 方法论 / 新链路？→ 当场沉淀到 memory / 流程文档 / checklist（元规则 feedback_proactive_knowledge_update：不攒、不等提醒）。\n"
        "  2. 归档：有没有产物（原型 / 报告 / 方案 / 配置 / 图 / 范本）？→ 归档到 KB 固定路径（见 reference_output_paths）。\n"
        "  3. 复用而非现写：有没有把可复用的工具/脚本固化进知识库，而不是留一堆一次性脚本？\n"
        "都做了/不适用，再收工。"
    )

if __name__ == "__main__":
    try:
        main()
    except Exception:
        # 任何意外都放行：这个门只负责提醒，绝不允许自己的 bug 卡住收工
        pass
    sys.exit(0)
