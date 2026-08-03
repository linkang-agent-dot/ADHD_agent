#!/usr/bin/env python3
"""Durable handoff ledger for Codex sub-agents and ephemeral BTW chats."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator


DEFAULT_ROOT = Path(r"C:\ADHD_agent\CodexMemory\handoffs")
SCRIPT_PATH = Path(__file__).resolve()


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def root_dir() -> Path:
    return Path(os.environ.get("CODEX_HANDOFF_ROOT", str(DEFAULT_ROOT)))


def short_id(value: str | None, length: int = 8) -> str:
    value = value or "unknown"
    compact = re.sub(r"[^A-Za-z0-9]", "", value)
    return (compact or hashlib.sha1(value.encode("utf-8")).hexdigest())[-length:]


def safe_name(value: str, fallback: str = "untitled", limit: int = 42) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[\x00-\x1f<>:\"/\\|?*]", "_", value)
    value = re.sub(r"\s+", "_", value).strip(" ._")
    return (value[:limit].rstrip(" ._") or fallback)


def prompt_title(prompt: str | None) -> str:
    if not prompt:
        return "untitled"
    lines = [line.strip() for line in prompt.splitlines() if line.strip()]
    useful = [
        line
        for line in lines
        if not line.startswith(("<", "# AGENTS", "</", "- "))
        and "instructions for" not in line.lower()
    ]
    candidate = useful[-1] if useful else (lines[-1] if lines else "untitled")
    if ";" in candidate or "；" in candidate:
        candidate = re.split(r"[;；]", candidate)[-1]
    return safe_name(candidate)


@contextlib.contextmanager
def ledger_lock(root: Path) -> Iterator[None]:
    root.mkdir(parents=True, exist_ok=True)
    lock_path = root / ".handoff.lock"
    handle = lock_path.open("a+b")
    try:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            while True:
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(0.05)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else (default or {})
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default or {}


def append_markdown(path: Path, heading: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"\n## {heading}\n\n{body.strip()}\n")


def snapshot_transcript(source: str | None, destination: Path, warnings: list[str]) -> None:
    if not source:
        return
    src = Path(source)
    if not src.is_file():
        warnings.append(f"transcript unavailable: {source}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copyfile(src, destination)
    except OSError as exc:
        warnings.append(f"transcript snapshot failed: {exc}")


def index_path(root: Path, session_id: str) -> Path:
    return root / "_index" / f"{safe_name(session_id, 'unknown', 80)}.json"


def load_index(root: Path, session_id: str) -> dict[str, Any]:
    return load_json(index_path(root, session_id), {"session_id": session_id})


def save_index(root: Path, session_id: str, data: dict[str, Any]) -> None:
    data["session_id"] = session_id
    data["updated_at"] = now_iso()
    atomic_json(index_path(root, session_id), data)


def extract_first_user_prompt(transcript_path: str | None) -> str | None:
    if not transcript_path:
        return None
    try:
        with Path(transcript_path).open(encoding="utf-8") as handle:
            for line in handle:
                obj = json.loads(line)
                if obj.get("type") != "response_item":
                    continue
                payload = obj.get("payload", {})
                if payload.get("type") != "message" or payload.get("role") != "user":
                    continue
                texts = [
                    item.get("text", "")
                    for item in payload.get("content", [])
                    if item.get("type") in {"input_text", "text"}
                ]
                text = "\n".join(texts).strip()
                if text and len(text) < 12000 and "# AGENTS.md instructions" not in text:
                    return text
    except (OSError, json.JSONDecodeError):
        return None
    return None


def ensure_conversation(
    root: Path,
    session_id: str,
    transcript_path: str | None = None,
    prompt: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    idx = load_index(root, session_id)
    if transcript_path and not idx.get("main_transcript_path"):
        idx["main_transcript_path"] = transcript_path
    relative = idx.get("folder")
    if relative:
        folder = root / relative
    else:
        source_prompt = prompt or extract_first_user_prompt(transcript_path)
        title = prompt_title(source_prompt)
        folder_name = f"{datetime.now().astimezone():%Y-%m-%d}_{title}_{short_id(session_id)}"
        folder = root / folder_name
        suffix = 2
        while folder.exists() and load_json(folder / "main.json").get("session_id") != session_id:
            folder = root / f"{folder_name}_{suffix}"
            suffix += 1
        idx["folder"] = folder.name
        idx["title"] = title
    folder.mkdir(parents=True, exist_ok=True)
    main = load_json(folder / "main.json")
    main.update(
        {
            "schema_version": 1,
            "session_id": session_id,
            "title": idx.get("title", "untitled"),
            "main_transcript_path": idx.get("main_transcript_path"),
            "updated_at": now_iso(),
        }
    )
    main.setdefault("created_at", now_iso())
    atomic_json(folder / "main.json", main)
    save_index(root, session_id, idx)
    return folder, idx


def state_path(record_dir: Path) -> Path:
    return record_dir / "state.json"


def update_state(record_dir: Path, **updates: Any) -> dict[str, Any]:
    state = load_json(state_path(record_dir))
    state.update(updates)
    state.setdefault("schema_version", 1)
    state.setdefault("created_at", now_iso())
    state["updated_at"] = now_iso()
    state.setdefault("warnings", [])
    atomic_json(state_path(record_dir), state)
    return state


def side_record(folder: Path, transcript_path: str | None, turn_id: str | None) -> tuple[Path, str]:
    identity = transcript_path or turn_id or f"side-{time.time_ns()}"
    record_id = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:8]
    return folder / "BTW" / record_id, record_id


def subagent_record(folder: Path, agent_type: str, agent_id: str) -> Path:
    return folder / "sub-agent" / f"{safe_name(agent_type, 'agent', 30)}_{short_id(agent_id)}"


def find_subagent_record(folder: Path, agent_id: str) -> Path | None:
    base = folder / "sub-agent"
    matches = list(base.glob(f"*_{short_id(agent_id)}")) if base.exists() else []
    return matches[0] if matches else None


def checkpoint_command(session_id: str, channel: str, record_id: str) -> str:
    return (
        f'python "{SCRIPT_PATH}" checkpoint --session-id "{session_id}" '
        f'--channel "{channel}" --record-id "{record_id}" --message "<结论/改动/未决项/下一步>"'
    )


def recovery_context(folder: Path, max_chars: int = 10000) -> tuple[str, list[Path]]:
    sections: list[str] = []
    records: list[Path] = []
    for channel in ("sub-agent", "BTW"):
        base = folder / channel
        if not base.exists():
            continue
        for record in sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: p.name):
            state = load_json(record / "state.json")
            if state.get("status") == "claimed":
                continue
            pieces = []
            for name in ("final-handoff.md", "checkpoints.md", "user-prompts.md"):
                path = record / name
                if path.is_file():
                    text = path.read_text(encoding="utf-8", errors="replace").strip()
                    if text:
                        pieces.append(f"### {name}\n{text[-3500:]}")
            if not pieces:
                continue
            sections.append(
                f"## {channel}/{record.name} status={state.get('status', 'unknown')}\n"
                + "\n".join(pieces)
            )
            records.append(record)
    if not sections:
        return "", []
    text = (
        "[SUBAGENT_HANDOFF_RECOVERY]\n"
        "以下是 BTW/sub-agent 未接管备份。先吸收用户判断、已完成改动和未决项，再继续主任务；"
        "接管后运行 handoff claim 命令。\n\n"
        + "\n\n".join(sections)
    )
    return text[:max_chars], records


def hook_output(additional_context: str = "", *, decision_block: str | None = None) -> dict[str, Any]:
    if decision_block:
        return {"decision": "block", "reason": decision_block}
    if not additional_context:
        return {"continue": True}
    return {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        },
    }


def handle_event(event: dict[str, Any], root: Path | None = None) -> dict[str, Any]:
    root = root or root_dir()
    name = event.get("hook_event_name", "")
    session_id = str(event.get("session_id") or "unknown")
    transcript = event.get("transcript_path")
    turn_id = str(event.get("turn_id") or "")

    with ledger_lock(root):
        idx = load_index(root, session_id)

        if name == "SessionStart":
            if transcript:
                idx["main_transcript_path"] = transcript
                save_index(root, session_id, idx)
            if idx.get("folder"):
                folder = root / idx["folder"]
                context, _ = recovery_context(folder)
                if context:
                    return {
                        "continue": True,
                        "hookSpecificOutput": {
                            "hookEventName": "SessionStart",
                            "additionalContext": context,
                        },
                    }
            return {"continue": True}

        if name == "UserPromptSubmit":
            prompt = str(event.get("prompt") or "")
            main_transcript = idx.get("main_transcript_path")
            if not main_transcript:
                idx["main_transcript_path"] = transcript
                save_index(root, session_id, idx)
                main_transcript = transcript
            folder, idx = ensure_conversation(root, session_id, main_transcript, prompt)
            if transcript and main_transcript and os.path.normcase(transcript) != os.path.normcase(main_transcript):
                record, record_id = side_record(folder, transcript, turn_id)
                append_markdown(record / "user-prompts.md", f"{now_iso()} turn={turn_id}", prompt)
                warnings: list[str] = []
                snapshot_transcript(transcript, record / "transcript-snapshot.jsonl", warnings)
                update_state(
                    record,
                    parent_session_id=session_id,
                    agent_id=record_id,
                    agent_type="BTW",
                    channel="BTW",
                    status="active",
                    transcript_path=transcript,
                    warnings=warnings,
                )
                context = (
                    "这是 BTW 临时子对话。用户输入已备份。每形成一个业务判断或完成一次实际改动，立即执行：\n"
                    + checkpoint_command(session_id, "BTW", record_id)
                    + "\n结束前必须写明结论、改动、未决项和主对话下一步。"
                )
                return hook_output(context)
            context, _ = recovery_context(folder)
            return hook_output(context)

        folder, _ = ensure_conversation(root, session_id, transcript)

        if name == "SubagentStart":
            agent_id = str(event.get("agent_id") or "unknown")
            agent_type = str(event.get("agent_type") or "agent")
            record = subagent_record(folder, agent_type, agent_id)
            update_state(
                record,
                parent_session_id=session_id,
                agent_id=agent_id,
                agent_type=agent_type,
                channel="sub-agent",
                status="active",
                parent_transcript_path=transcript,
            )
            context = (
                "你是带持久化 handoff 的子 agent。每形成关键结论、获得用户业务判断或完成实际改动后，立即执行：\n"
                + checkpoint_command(session_id, "sub-agent", record.name)
                + "\n你的 final 必须包含：结论、实际改动、验证、未决项、主对话下一步。"
            )
            return {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStart",
                    "additionalContext": context,
                },
            }

        if name == "SubagentStop":
            agent_id = str(event.get("agent_id") or "unknown")
            agent_type = str(event.get("agent_type") or "agent")
            record = find_subagent_record(folder, agent_id) or subagent_record(folder, agent_type, agent_id)
            message = str(event.get("last_assistant_message") or "").strip()
            warnings: list[str] = []
            agent_transcript = event.get("agent_transcript_path")
            snapshot_transcript(agent_transcript, record / "transcript-snapshot.jsonl", warnings)
            if message:
                (record / "final-handoff.md").write_text(message + "\n", encoding="utf-8", newline="\n")
            update_state(
                record,
                parent_session_id=session_id,
                agent_id=agent_id,
                agent_type=agent_type,
                channel="sub-agent",
                status="completed" if message else "interrupted",
                transcript_path=agent_transcript,
                warnings=warnings,
            )
            if not message and not event.get("stop_hook_active"):
                return hook_output(decision_block="补齐结构化 handoff 后再结束子 agent。")
            return {"continue": True}

        if name == "Stop":
            main_transcript = idx.get("main_transcript_path")
            if transcript and main_transcript and os.path.normcase(transcript) != os.path.normcase(main_transcript):
                message = str(event.get("last_assistant_message") or "").strip()
                if message:
                    active_subagents = []
                    base = folder / "sub-agent"
                    if base.exists():
                        active_subagents = [
                            p for p in base.iterdir()
                            if p.is_dir() and load_json(p / "state.json").get("status") == "active"
                        ]
                    if len(active_subagents) == 1:
                        record = active_subagents[0]
                    else:
                        record, _ = side_record(folder, transcript, turn_id)
                    append_markdown(record / "checkpoints.md", f"{now_iso()} turn={turn_id}", message)
                    warnings: list[str] = []
                    snapshot_transcript(transcript, record / "transcript-snapshot.jsonl", warnings)
                    state = load_json(record / "state.json")
                    update_state(record, status=state.get("status", "active"), warnings=warnings)
            return {"continue": True}

        return {"continue": True}


def resolve_record(root: Path, session_id: str, channel: str, record_id: str) -> Path:
    idx = load_index(root, session_id)
    if not idx.get("folder"):
        raise SystemExit(f"No handoff conversation found for session {session_id}")
    folder = root / idx["folder"]
    base = folder / channel
    direct = base / record_id
    if direct.is_dir():
        return direct
    matches = list(base.glob(f"*{safe_name(record_id, record_id, 80)}*")) if base.exists() else []
    if len(matches) == 1:
        return matches[0]
    raise SystemExit(f"Handoff record not found: {channel}/{record_id}")


def resolve_conversation_folder(root: Path, session_id: str) -> Path:
    """Resolve a handoff folder through the session index; never guess its name."""
    idx = load_index(root, session_id)
    if not idx.get("folder"):
        raise SystemExit(f"No handoff conversation found for session {session_id}")
    return root / idx["folder"]


def cmd_locate(args: argparse.Namespace) -> int:
    print(resolve_conversation_folder(root_dir(), args.session_id))
    return 0


def cmd_checkpoint(args: argparse.Namespace) -> int:
    root = root_dir()
    with ledger_lock(root):
        record = resolve_record(root, args.session_id, args.channel, args.record_id)
        append_markdown(record / "checkpoints.md", now_iso(), args.message)
        state = load_json(record / "state.json")
        update_state(record, status=state.get("status", "active"))
    print(record)
    return 0


def cmd_claim(args: argparse.Namespace) -> int:
    root = root_dir()
    claimed: list[str] = []
    with ledger_lock(root):
        idx = load_index(root, args.session_id)
        if not idx.get("folder"):
            return 0
        folder = root / idx["folder"]
        for channel in ("sub-agent", "BTW"):
            base = folder / channel
            if not base.exists():
                continue
            for record in base.iterdir():
                if not record.is_dir():
                    continue
                state = load_json(record / "state.json")
                if state.get("status") == "claimed":
                    continue
                update_state(record, status="claimed", claimed_at=now_iso())
                claimed.append(str(record))
    for item in claimed:
        print(item)
    return 0


def cmd_hook() -> int:
    try:
        event = json.load(sys.stdin)
        result = handle_event(event)
    except Exception as exc:  # Hooks must not break the user's task.
        result = {"continue": True, "systemMessage": f"handoff hook warning: {exc}"}
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("hook")
    checkpoint = sub.add_parser("checkpoint")
    checkpoint.add_argument("--session-id", required=True)
    checkpoint.add_argument("--channel", choices=("sub-agent", "BTW"), required=True)
    checkpoint.add_argument("--record-id", required=True)
    checkpoint.add_argument("--message", required=True)
    claim = sub.add_parser("claim")
    claim.add_argument("--session-id", required=True)
    locate = sub.add_parser("locate")
    locate.add_argument("--session-id", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "hook":
        return cmd_hook()
    if args.command == "checkpoint":
        return cmd_checkpoint(args)
    if args.command == "claim":
        return cmd_claim(args)
    if args.command == "locate":
        return cmd_locate(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
