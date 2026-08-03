from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


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


def _top_level_directories(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        raise ValueError(f"Skill root is not a directory: {root}")
    return {child.name: child for child in root.iterdir() if child.is_dir()}


def _is_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


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
