from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
