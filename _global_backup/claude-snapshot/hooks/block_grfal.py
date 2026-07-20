#!/usr/bin/env python3
"""PreToolUse hook: 在特定会话/项目内硬拦一切 GRFal 调用。

生效条件（满足任一才检查，否则直接放行，不影响日常会话用 grfal）：
  1. 会话 ID 出现在 grfal_ban_sessions.txt（一行一个 session_id，# 开头为注释）
  2. 会话 cwd 路径包含 "avatar-replace" 或 "shiba-pet"（个人项目全程禁用公司 GRFal）

拦截范围（对 tool_input 整体序列化后做模式匹配，宁可误杀不可放过）：
  - call_grfal / grfal-api / grfal.tap4fun.com / 172.20.90.45 / 裸词 grfal
  - Skill 工具调用 grfal-api、x3-media*（其后端即 GRFal）
  - Agent 工具派 media-worker 子代理（GRFal 专用 worker）
"""
import json
import re
import sys
from pathlib import Path

BAN_LIST = Path(__file__).with_name("grfal_ban_sessions.txt")

PATTERNS = [
    r"call_grfal",
    r"grfal[-_]api",
    r"grfal\.tap4fun\.com",
    r"172\.20\.90\.45",
    r"\bgrfal\b",
]
BANNED_SKILL_PREFIXES = ("grfal-api", "x3-media")
BANNED_AGENT_TYPES = ("media-worker",)


def banned_sessions() -> set[str]:
    try:
        return {
            line.strip()
            for line in BAN_LIST.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
    except OSError:
        return set()


def is_guarded(payload: dict) -> bool:
    if payload.get("session_id", "") in banned_sessions():
        return True
    cwd = str(payload.get("cwd", "")).lower().replace("\\", "/")
    return "avatar-replace" in cwd or "shiba-pet" in cwd


def find_violation(payload: dict) -> str:
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    if tool == "Skill":
        skill = str(tool_input.get("skill", ""))
        if skill.startswith(BANNED_SKILL_PREFIXES):
            return f"Skill '{skill}' 的后端是公司 GRFal"
    if tool == "Agent":
        if str(tool_input.get("subagent_type", "")) in BANNED_AGENT_TYPES:
            return "media-worker 子代理是 GRFal 专用 worker"

    blob = json.dumps(tool_input, ensure_ascii=False)
    for pat in PATTERNS:
        if re.search(pat, blob, re.IGNORECASE):
            return f"匹配到 GRFal 特征: {pat}"
    return ""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # 读不到输入就放行，不阻塞正常工作

    if not is_guarded(payload):
        sys.exit(0)

    reason = find_violation(payload)
    if not reason:
        sys.exit(0)

    # ensure_ascii=True：Windows 控制台可能是 GBK，非 ASCII 直出会 UnicodeEncodeError
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "[BLOCKED] 本会话/avatar-replace 项目严禁触发公司 GRFal 平台（用户明令）。"
                f"已拦截：{reason}。请改用自建火山引擎通道（core/providers/volc.py）。"
            ),
        }
    }, ensure_ascii=True))
    sys.exit(0)


if __name__ == "__main__":
    main()
