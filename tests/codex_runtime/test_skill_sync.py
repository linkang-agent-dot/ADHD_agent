from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from CodexRuntime.skills.sync_claude_to_codex import inventory_skills


VALID_SKILL = """---
name: {name}
description: Use when testing the skill synchronizer.
---

# {name}
"""


def make_roots(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "claude-skills"
    destination = tmp_path / "codex-skills"
    source.mkdir()
    destination.mkdir()
    return source, destination


def make_skill(root: Path, name: str, body: str | None = None) -> Path:
    skill = root / name
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        body if body is not None else VALID_SKILL.format(name=name),
        encoding="utf-8",
    )
    return skill


def test_inventory_classifies_physical_pair(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    make_skill(source, "demo")
    make_skill(destination, "demo")

    result = inventory_skills(source, destination)

    assert result.by_name("demo").kind == "physical-pair"


def test_inventory_reports_codex_only(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    make_skill(destination, "codex-extra")

    result = inventory_skills(source, destination)

    assert result.by_name("codex-extra").kind == "codex-only"


def test_inventory_reports_missing_destination(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    make_skill(source, "new-claude-skill")

    result = inventory_skills(source, destination)

    assert result.by_name("new-claude-skill").kind == "missing-destination"


@pytest.mark.skipif(os.name != "nt", reason="Junction behavior is Windows-specific")
def test_inventory_skips_source_junction(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    physical = tmp_path / "physical-demo"
    make_skill(tmp_path, "physical-demo")
    junction = source / "demo"
    completed = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(physical)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        pytest.skip(f"Junction creation unavailable: {completed.stderr}")
    make_skill(destination, "demo")

    result = inventory_skills(source, destination)

    entry = result.by_name("demo")
    assert entry.kind == "shared-junction"
    assert entry.source == junction
