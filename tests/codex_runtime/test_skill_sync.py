from __future__ import annotations

import os
import subprocess
import json
from pathlib import Path

import pytest

from CodexRuntime.skills.sync_claude_to_codex import (
    SkillFormatError,
    apply_sync_plan,
    build_sync_plan,
    inventory_skills,
    main,
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


def test_inventory_classifies_auxiliary_directory_without_skill_file(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    (source / "workspace").mkdir()
    (destination / "workspace").mkdir()

    result = inventory_skills(source, destination)

    assert result.by_name("workspace").kind == "non-skill-directory"


def test_inventory_classifies_timestamped_backup_directory_as_non_skill(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    backup_name = "demo.bak.1780452777247"
    make_skill(source, backup_name, VALID_SKILL.format(name="demo"))
    make_skill(destination, backup_name, VALID_SKILL.format(name="demo"))

    result = inventory_skills(source, destination)

    assert result.by_name(backup_name).kind == "non-skill-directory"


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


def test_merge_preserves_destination_frontmatter_when_source_has_none() -> None:
    source = "# Shared body\n\nUpdated by Claude.\n"
    destination = VALID_SKILL.format(name="demo") + "\nOld body.\n"

    merged = merge_skill_markdown(source, destination, "demo")

    assert merged.startswith("---\nname: demo\ndescription:")
    assert "Updated by Claude." in merged
    assert "Old body." not in merged


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


@pytest.mark.parametrize("indicator", ["|", ">-"])
def test_validate_frontmatter_accepts_yaml_block_description(indicator: str) -> None:
    text = (
        "---\n"
        "name: demo_skill\n"
        f"description: {indicator}\n"
        "  Use when a long description spans lines.\n"
        "  The continuation remains part of the scalar.\n"
        "---\n"
        "# Demo\n"
    )

    assert validate_frontmatter(text, "demo_skill") == []


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


def test_plan_preserves_destination_line_endings_for_skill_markdown(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    source_skill = source / "demo"
    destination_skill = destination / "demo"
    source_skill.mkdir()
    destination_skill.mkdir()
    logical = VALID_SKILL.format(name="demo")
    (source_skill / "SKILL.md").write_bytes(logical.encode("utf-8"))
    (destination_skill / "SKILL.md").write_bytes(logical.replace("\n", "\r\n").encode("utf-8"))

    plan = build_sync_plan(source, destination)

    operation = next(op for op in plan.operations if op.relative_path == "SKILL.md")
    assert operation.action == "skip"
    assert operation.content == logical.replace("\n", "\r\n").encode("utf-8")


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


def test_plan_skips_non_skill_directories_without_blocking(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    (source / "workspace").mkdir()
    (destination / "workspace").mkdir()

    plan = build_sync_plan(source, destination)

    assert plan.blockers == ()
    assert plan.operations == ()


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


def test_cli_defaults_to_dry_run_and_does_not_write_target(tmp_path: Path, capsys) -> None:
    source, destination = make_roots(tmp_path)
    source_skill = make_skill(source, "demo")
    destination_skill = make_skill(destination, "demo")
    (source_skill / "value.txt").write_text("new", encoding="utf-8")
    target = destination_skill / "value.txt"
    target.write_text("old", encoding="utf-8")
    before = (target.read_bytes(), target.stat().st_mtime_ns)

    exit_code = main(["--source", str(source), "--destination", str(destination)])

    after = (target.read_bytes(), target.stat().st_mtime_ns)
    output = capsys.readouterr().out
    assert exit_code == 0
    assert before == after
    assert "DRY RUN" in output
    assert "physical-pair" in output
    assert "modify" in output


def test_cli_writes_json_report_with_documented_shape(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    make_skill(source, "demo")
    make_skill(destination, "demo")
    report = tmp_path / "report.json"

    exit_code = main(
        [
            "--source",
            str(source),
            "--destination",
            str(destination),
            "--json-report",
            str(report),
        ]
    )

    payload = json.loads(report.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["schema_version"] == 1
    assert payload["mode"] == "dry-run"
    assert payload["source_root"] == str(source)
    assert payload["destination_root"] == str(destination)
    assert isinstance(payload["inventory"], list)
    assert isinstance(payload["operations"], list)
    assert payload["blockers"] == []


def test_cli_returns_two_when_plan_has_blockers(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    make_skill(source, "missing-at-destination")

    exit_code = main(["--source", str(source), "--destination", str(destination)])

    assert exit_code == 2


def test_apply_backs_up_then_updates_and_adds_files(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    source_skill = make_skill(source, "demo")
    destination_skill = make_skill(destination, "demo")
    (source_skill / "changed.txt").write_text("new", encoding="utf-8")
    (destination_skill / "changed.txt").write_text("old", encoding="utf-8")
    (source_skill / "added.txt").write_text("added", encoding="utf-8")
    plan = build_sync_plan(source, destination)
    backup_root = tmp_path / "backups"

    result = apply_sync_plan(plan, backup_root)

    assert result.exit_code == 0
    assert result.backup_directory is not None
    assert (destination_skill / "changed.txt").read_text(encoding="utf-8") == "new"
    assert (destination_skill / "added.txt").read_text(encoding="utf-8") == "added"
    assert (result.backup_directory / "files" / "demo" / "changed.txt").read_text(encoding="utf-8") == "old"
    manifest = json.loads((result.backup_directory / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "applied"


def test_apply_failure_rolls_back_all_written_files(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    source_skill = make_skill(source, "demo")
    destination_skill = make_skill(destination, "demo")
    for name in ("a.txt", "b.txt"):
        (source_skill / name).write_text(f"new-{name}", encoding="utf-8")
        (destination_skill / name).write_text(f"old-{name}", encoding="utf-8")
    plan = build_sync_plan(source, destination)
    calls = 0

    def fail_second_replace(source_path, destination_path):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected apply failure")
        os.replace(source_path, destination_path)

    result = apply_sync_plan(plan, tmp_path / "backups", replace_func=fail_second_replace)

    assert result.exit_code == 3
    assert result.rollback_complete is True
    assert (destination_skill / "a.txt").read_text(encoding="utf-8") == "old-a.txt"
    assert (destination_skill / "b.txt").read_text(encoding="utf-8") == "old-b.txt"


def test_apply_with_blockers_performs_zero_writes(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    make_skill(source, "missing-at-destination")
    plan = build_sync_plan(source, destination)
    backup_root = tmp_path / "backups"

    result = apply_sync_plan(plan, backup_root)

    assert result.exit_code == 2
    assert not backup_root.exists()
    assert not (destination / "missing-at-destination").exists()


def test_apply_reports_incomplete_rollback(tmp_path: Path) -> None:
    source, destination = make_roots(tmp_path)
    source_skill = make_skill(source, "demo")
    destination_skill = make_skill(destination, "demo")
    for name in ("a.txt", "b.txt"):
        (source_skill / name).write_text(f"new-{name}", encoding="utf-8")
        (destination_skill / name).write_text(f"old-{name}", encoding="utf-8")
    plan = build_sync_plan(source, destination)
    calls = 0

    def fail_apply_and_rollback(source_path, destination_path):
        nonlocal calls
        calls += 1
        if calls >= 2:
            raise OSError("injected persistent failure")
        os.replace(source_path, destination_path)

    result = apply_sync_plan(plan, tmp_path / "backups", replace_func=fail_apply_and_rollback)

    assert result.exit_code == 4
    assert result.rollback_complete is False
