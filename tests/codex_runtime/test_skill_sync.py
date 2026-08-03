from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from CodexRuntime.skills.sync_claude_to_codex import (
    SkillFormatError,
    build_sync_plan,
    inventory_skills,
    merge_skill_markdown,
    validate_frontmatter,
)


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


def test_merge_preserves_codex_only_block_verbatim() -> None:
    source = VALID_SKILL.format(name="demo") + "\nNew shared body.\n"
    block = (
        "<!-- CODEX-ONLY:START -->\n"
        "Use actv_lookup.py before parsing TSV.\n"
        "<!-- CODEX-ONLY:END -->"
    )
    destination = VALID_SKILL.format(name="demo") + "\nOld shared body.\n\n" + block + "\n"

    merged = merge_skill_markdown(source, destination, "demo")

    assert block in merged
    assert "New shared body." in merged
    assert "Old shared body." not in merged


def test_merge_without_codex_block_returns_source() -> None:
    source = VALID_SKILL.format(name="demo") + "\nShared body.\n"
    destination = VALID_SKILL.format(name="demo") + "\nOld body.\n"

    assert merge_skill_markdown(source, destination, "demo") == source


@pytest.mark.parametrize(
    "destination",
    [
        "<!-- CODEX-ONLY:START -->\none\n<!-- CODEX-ONLY:START -->\ntwo\n<!-- CODEX-ONLY:END -->",
        "<!-- CODEX-ONLY:START -->\nunclosed",
        "<!-- CODEX-ONLY:END -->",
    ],
)
def test_merge_rejects_malformed_codex_markers(destination: str) -> None:
    source = VALID_SKILL.format(name="demo")

    with pytest.raises(SkillFormatError):
        merge_skill_markdown(source, destination, "demo")


def test_validate_frontmatter_requires_name_and_description() -> None:
    text = "---\nname: demo\n---\n# Demo\n"

    errors = validate_frontmatter(text, "demo")

    assert any("description" in error for error in errors)


def test_validate_frontmatter_rejects_name_mismatch() -> None:
    text = VALID_SKILL.format(name="wrong-name")

    errors = validate_frontmatter(text, "demo")

    assert any("does not match" in error for error in errors)


def operation_map(plan) -> dict[tuple[str, str], str]:
    return {(op.skill, op.relative_path): op.action for op in plan.operations}


def test_plan_adds_modifies_skips_and_preserves_without_writing(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    source_skill = make_skill(source, "demo")
    destination_skill = make_skill(destination, "demo")
    (source_skill / "same.txt").write_text("same", encoding="utf-8")
    (destination_skill / "same.txt").write_text("same", encoding="utf-8")
    (source_skill / "changed.txt").write_text("new", encoding="utf-8")
    (destination_skill / "changed.txt").write_text("old", encoding="utf-8")
    (source_skill / "new.txt").write_text("new", encoding="utf-8")
    (destination_skill / "codex-only.txt").write_text("keep", encoding="utf-8")
    before = (destination_skill / "changed.txt").read_text(encoding="utf-8")

    plan = build_sync_plan(source, destination)

    operations = operation_map(plan)
    assert operations[("demo", "same.txt")] == "skip"
    assert operations[("demo", "changed.txt")] == "modify"
    assert operations[("demo", "new.txt")] == "add"
    assert operations[("demo", "codex-only.txt")] == "preserve"
    assert (destination_skill / "changed.txt").read_text(encoding="utf-8") == before


def test_plan_excludes_runtime_artifacts(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    source_skill = make_skill(source, "demo")
    make_skill(destination, "demo")
    cache = source_skill / "__pycache__"
    cache.mkdir()
    (cache / "module.pyc").write_bytes(b"compiled")
    (source_skill / "debug.log").write_text("noise", encoding="utf-8")
    (source_skill / "scratch.tmp").write_text("noise", encoding="utf-8")

    plan = build_sync_plan(source, destination)

    planned_paths = {op.relative_path for op in plan.operations}
    assert "__pycache__/module.pyc" not in planned_paths
    assert "debug.log" not in planned_paths
    assert "scratch.tmp" not in planned_paths


def test_plan_blocks_missing_destination_by_default(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    make_skill(source, "new-skill")

    plan = build_sync_plan(source, destination)

    assert plan.blockers
    assert any("allow-create" in blocker for blocker in plan.blockers)


@pytest.mark.skipif(os.name != "nt", reason="Junction behavior is Windows-specific")
def test_plan_blocks_nested_junction(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    source_skill = make_skill(source, "demo")
    make_skill(destination, "demo")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("do not follow", encoding="utf-8")
    nested = source_skill / "linked"
    completed = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(nested), str(outside)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        pytest.skip(f"Junction creation unavailable: {completed.stderr}")

    plan = build_sync_plan(source, destination)

    assert any("reparse" in blocker.lower() or "junction" in blocker.lower() for blocker in plan.blockers)
    assert all(op.relative_path != "linked/secret.txt" for op in plan.operations)
