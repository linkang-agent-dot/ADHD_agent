from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import uuid
from typing import Callable


CODEX_START = "<!-- CODEX-ONLY:START -->"
CODEX_END = "<!-- CODEX-ONLY:END -->"


class SkillFormatError(ValueError):
    pass


@dataclass(frozen=True)
class SkillEntry:
    name: str
    kind: str
    source: Path | None
    destination: Path | None


@dataclass(frozen=True)
class InventoryResult:
    entries: tuple[SkillEntry, ...]

    def by_name(self, name: str) -> SkillEntry:
        for entry in self.entries:
            if entry.name == name:
                return entry
        raise KeyError(name)


@dataclass(frozen=True)
class FileOperation:
    skill: str
    relative_path: str
    action: str
    source: Path | None
    destination: Path
    content: bytes | None = None


@dataclass(frozen=True)
class SyncPlan:
    source_root: Path
    destination_root: Path
    inventory: InventoryResult
    operations: tuple[FileOperation, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class ApplyResult:
    exit_code: int
    backup_directory: Path | None
    rollback_complete: bool | None
    error: str | None = None


def _top_level_directories(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        raise ValueError(f"Skill root is not a directory: {root}")
    return {child.name: child for child in root.iterdir() if child.is_dir()}


def _is_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _is_reparse_point(path: Path) -> bool:
    if path.is_symlink() or _is_junction(path):
        return True
    try:
        attributes = path.lstat().st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def inventory_skills(source_root: Path, destination_root: Path) -> InventoryResult:
    """Classify source/destination top-level skills without traversing them."""
    source_root = Path(source_root)
    destination_root = Path(destination_root)
    sources = _top_level_directories(source_root)
    destinations = _top_level_directories(destination_root)
    entries: list[SkillEntry] = []

    for name in sorted(sources.keys() | destinations.keys()):
        source = sources.get(name)
        destination = destinations.get(name)
        if source is not None and _is_junction(source):
            kind = "shared-junction"
        elif source is None:
            kind = "codex-only"
        elif destination is None:
            kind = "missing-destination"
        else:
            kind = "physical-pair"
        entries.append(
            SkillEntry(
                name=name,
                kind=kind,
                source=source,
                destination=destination,
            )
        )

    return InventoryResult(tuple(entries))


def _frontmatter_values(text: str) -> tuple[dict[str, str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["SKILL.md must start with YAML frontmatter"]
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return {}, ["YAML frontmatter is not closed"]

    values: dict[str, str] = {}
    errors: list[str] = []
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"Unsupported frontmatter line: {line}")
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value in {"|", ">", "|-", ">-", "|+", ">+"}:
            errors.append(f"Multiline frontmatter value is unsupported: {key}")
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values, errors


def validate_frontmatter(text: str, expected_name: str) -> list[str]:
    values, errors = _frontmatter_values(text)
    name = values.get("name", "")
    description = values.get("description", "")
    if not name:
        errors.append("frontmatter requires a non-empty name")
    elif not re.fullmatch(r"[A-Za-z0-9-]+", name):
        errors.append("frontmatter name may contain only letters, numbers, and hyphens")
    elif name != expected_name:
        errors.append(f"frontmatter name {name!r} does not match directory {expected_name!r}")
    if not description:
        errors.append("frontmatter requires a non-empty description")
    return errors


def extract_codex_only_block(text: str) -> str | None:
    start_count = text.count(CODEX_START)
    end_count = text.count(CODEX_END)
    if start_count == 0 and end_count == 0:
        return None
    if start_count != 1 or end_count != 1:
        raise SkillFormatError("Codex-only markers must appear exactly once as a pair")
    start = text.index(CODEX_START)
    end = text.index(CODEX_END)
    if end < start:
        raise SkillFormatError("Codex-only end marker appears before start marker")
    return text[start : end + len(CODEX_END)]


def merge_skill_markdown(source: str, destination: str | None, expected_name: str) -> str:
    source_errors = validate_frontmatter(source, expected_name)
    if source_errors:
        raise SkillFormatError("; ".join(source_errors))
    block = extract_codex_only_block(destination or "")
    if block is None:
        merged = source
    else:
        merged = source.rstrip() + "\n\n" + block + "\n"
    merged_errors = validate_frontmatter(merged, expected_name)
    if merged_errors:
        raise SkillFormatError("; ".join(merged_errors))
    return merged


EXCLUDED_DIRECTORIES = {"__pycache__", ".pytest_cache", "output", "outputs"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".temp"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_excluded(relative_path: Path) -> bool:
    return bool(
        any(part in EXCLUDED_DIRECTORIES for part in relative_path.parts)
        or relative_path.suffix.lower() in EXCLUDED_SUFFIXES
    )


def _walk_skill_files(skill_root: Path) -> tuple[dict[str, Path], list[str]]:
    files: dict[str, Path] = {}
    blockers: list[str] = []

    def visit(directory: Path) -> None:
        for child in sorted(directory.iterdir(), key=lambda item: item.name.lower()):
            relative = child.relative_to(skill_root)
            if _is_excluded(relative):
                continue
            if _is_reparse_point(child):
                blockers.append(f"Reparse point/Junction is not allowed inside Skill: {child}")
                continue
            if child.is_dir():
                visit(child)
            elif child.is_file():
                files[relative.as_posix()] = child

    visit(skill_root)
    return files, blockers


def _roots_overlap(source_root: Path, destination_root: Path) -> bool:
    source = source_root.resolve()
    destination = destination_root.resolve()
    return source == destination or source in destination.parents or destination in source.parents


def build_sync_plan(
    source_root: Path,
    destination_root: Path,
    *,
    allow_create: bool = False,
) -> SyncPlan:
    """Return a read-only synchronization plan."""
    source_root = Path(source_root)
    destination_root = Path(destination_root)
    inventory = inventory_skills(source_root, destination_root)
    operations: list[FileOperation] = []
    blockers: list[str] = []

    if _roots_overlap(source_root, destination_root):
        blockers.append("Source and destination roots must not overlap")
        return SyncPlan(source_root, destination_root, inventory, (), tuple(blockers))

    for entry in inventory.entries:
        if entry.kind in {"shared-junction", "codex-only"}:
            continue
        if entry.kind == "missing-destination" and not allow_create:
            blockers.append(f"Skill {entry.name!r} is missing at destination; use --allow-create")
            continue
        assert entry.source is not None
        destination_skill = entry.destination or destination_root / entry.name
        source_files, source_blockers = _walk_skill_files(entry.source)
        blockers.extend(source_blockers)
        if destination_skill.exists():
            destination_files, destination_blockers = _walk_skill_files(destination_skill)
            blockers.extend(destination_blockers)
        else:
            destination_files = {}

        if "SKILL.md" not in source_files:
            blockers.append(f"Skill {entry.name!r} has no source SKILL.md")
            continue

        for relative_path in sorted(source_files.keys() | destination_files.keys()):
            source = source_files.get(relative_path)
            destination = destination_skill / Path(relative_path)
            destination_existing = destination_files.get(relative_path)
            if source is None:
                operations.append(
                    FileOperation(
                        skill=entry.name,
                        relative_path=relative_path,
                        action="preserve",
                        source=None,
                        destination=destination,
                    )
                )
                continue

            try:
                if relative_path == "SKILL.md":
                    source_text = source.read_text(encoding="utf-8")
                    destination_text = (
                        destination_existing.read_text(encoding="utf-8")
                        if destination_existing is not None
                        else None
                    )
                    content = merge_skill_markdown(source_text, destination_text, entry.name).encode("utf-8")
                else:
                    content = source.read_bytes()
            except (OSError, UnicodeError, SkillFormatError) as exc:
                blockers.append(f"Skill {entry.name!r} file {relative_path!r}: {exc}")
                continue

            if destination_existing is None:
                action = "add"
            elif hashlib.sha256(content).hexdigest() == sha256_file(destination_existing):
                action = "skip"
            else:
                action = "modify"
            operations.append(
                FileOperation(
                    skill=entry.name,
                    relative_path=relative_path,
                    action=action,
                    source=source,
                    destination=destination,
                    content=content,
                )
            )

    return SyncPlan(
        source_root=source_root,
        destination_root=destination_root,
        inventory=inventory,
        operations=tuple(operations),
        blockers=tuple(blockers),
    )


def plan_to_dict(plan: SyncPlan, *, mode: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "mode": mode,
        "source_root": str(plan.source_root),
        "destination_root": str(plan.destination_root),
        "inventory": [
            {
                "name": entry.name,
                "kind": entry.kind,
                "source": str(entry.source) if entry.source is not None else None,
                "destination": str(entry.destination) if entry.destination is not None else None,
            }
            for entry in plan.inventory.entries
        ],
        "operations": [
            {
                "skill": operation.skill,
                "relative_path": operation.relative_path,
                "action": operation.action,
                "source": str(operation.source) if operation.source is not None else None,
                "destination": str(operation.destination),
            }
            for operation in plan.operations
        ],
        "blockers": list(plan.blockers),
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _atomic_write(
    destination: Path,
    content: bytes,
    *,
    replace_func: Callable[[Path, Path], None],
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.skill-sync-{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(content)
        replace_func(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def apply_sync_plan(
    plan: SyncPlan,
    backup_root: Path,
    *,
    replace_func: Callable[[Path, Path], None] = os.replace,
) -> ApplyResult:
    """Apply a blocker-free plan and roll back every completed write on failure."""
    if plan.blockers:
        return ApplyResult(exit_code=2, backup_directory=None, rollback_complete=None)

    writable = [operation for operation in plan.operations if operation.action in {"add", "modify"}]
    if not writable:
        return ApplyResult(exit_code=0, backup_directory=None, rollback_complete=None)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup_directory = Path(backup_root) / timestamp
    backup_files = backup_directory / "files"
    backup_directory.mkdir(parents=True, exist_ok=False)
    manifest_path = backup_directory / "manifest.json"
    manifest: dict[str, object] = {
        "schema_version": 1,
        "status": "prepared",
        "source_root": str(plan.source_root),
        "destination_root": str(plan.destination_root),
        "operations": [],
    }

    for operation in writable:
        record = {
            "skill": operation.skill,
            "relative_path": operation.relative_path,
            "action": operation.action,
            "destination": str(operation.destination),
            "pre_hash": sha256_file(operation.destination) if operation.destination.exists() else None,
        }
        cast_operations = manifest["operations"]
        assert isinstance(cast_operations, list)
        cast_operations.append(record)
        if operation.action == "modify":
            backup = backup_files / operation.skill / Path(operation.relative_path)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(operation.destination, backup)
    _write_json(manifest_path, manifest)

    applied: list[FileOperation] = []
    try:
        for operation in writable:
            assert operation.content is not None
            _atomic_write(operation.destination, operation.content, replace_func=replace_func)
            applied.append(operation)
    except Exception as exc:
        rollback_errors: list[str] = []
        for operation in reversed(applied):
            try:
                if operation.action == "modify":
                    backup = backup_files / operation.skill / Path(operation.relative_path)
                    _atomic_write(operation.destination, backup.read_bytes(), replace_func=replace_func)
                elif operation.destination.exists():
                    operation.destination.unlink()
            except Exception as rollback_exc:
                rollback_errors.append(f"{operation.destination}: {rollback_exc}")
        rollback_complete = not rollback_errors
        manifest["status"] = "rolled-back" if rollback_complete else "rollback-incomplete"
        manifest["error"] = str(exc)
        manifest["rollback_errors"] = rollback_errors
        _write_json(manifest_path, manifest)
        return ApplyResult(
            exit_code=3 if rollback_complete else 4,
            backup_directory=backup_directory,
            rollback_complete=rollback_complete,
            error=str(exc),
        )

    manifest["status"] = "applied"
    _write_json(manifest_path, manifest)
    return ApplyResult(
        exit_code=0,
        backup_directory=backup_directory,
        rollback_complete=None,
    )


def _print_summary(plan: SyncPlan, *, mode: str) -> None:
    inventory_counts = Counter(entry.kind for entry in plan.inventory.entries)
    operation_counts = Counter(operation.action for operation in plan.operations)
    print("DRY RUN" if mode == "dry-run" else "APPLY")
    print("Inventory: " + ", ".join(f"{key}={value}" for key, value in sorted(inventory_counts.items())))
    print("Operations: " + ", ".join(f"{key}={value}" for key, value in sorted(operation_counts.items())))
    print(f"Blockers: {len(plan.blockers)}")
    for blocker in plan.blockers:
        print(f"  BLOCK: {blocker}")


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely synchronize Claude Skills to Codex Skills")
    parser.add_argument("--source", type=Path, default=Path(r"C:\Users\linkang\.claude\skills"))
    parser.add_argument("--destination", type=Path, default=Path(r"C:\Users\linkang\.agents\skills"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Plan changes without writing (default)")
    mode.add_argument("--apply", action="store_true", help="Apply a blocker-free plan transactionally")
    parser.add_argument("--allow-create", action="store_true", help="Allow creation of missing destination Skills")
    parser.add_argument("--json-report", type=Path, help="Write a structured JSON report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    mode = "apply" if args.apply else "dry-run"
    plan = build_sync_plan(args.source, args.destination, allow_create=args.allow_create)
    _print_summary(plan, mode=mode)
    report = plan_to_dict(plan, mode=mode)
    if plan.blockers:
        if args.json_report is not None:
            _write_json(args.json_report, report)
        return 2
    if args.apply:
        result = apply_sync_plan(plan, Path.home() / ".codex" / "tmp" / "skill-sync-backups")
        report["application"] = {
            "exit_code": result.exit_code,
            "backup_directory": str(result.backup_directory) if result.backup_directory else None,
            "rollback_complete": result.rollback_complete,
            "error": result.error,
        }
        if args.json_report is not None:
            _write_json(args.json_report, report)
        if result.backup_directory is not None:
            print(f"Backup: {result.backup_directory}")
        return result.exit_code
    if args.json_report is not None:
        _write_json(args.json_report, report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
