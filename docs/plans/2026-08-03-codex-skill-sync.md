# Claude → Codex Skill Sync Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a safe Claude-to-Codex Skill synchronizer that skips Junctions, preserves explicit Codex-only instructions, blocks unsafe inputs, and defaults to read-only dry-run.

**Architecture:** A single Python CLI separates inventory, merge planning, validation, reporting, and transactional apply. Pure functions operate on temporary test trees; filesystem writes are isolated behind an apply function that backs up targets and rolls back on failure.

**Tech Stack:** Python 3 standard library, `pytest`, Windows filesystem/Junction detection, SHA-256, atomic `os.replace`.

---

### Task 1: Establish the test harness and inventory model

**Files:**
- Create: `tests/codex_runtime/test_skill_sync.py`
- Create: `CodexRuntime/skills/sync_claude_to_codex.py`

**Step 1: Write the failing inventory tests**

Create fixtures for source/destination roots and assert classification of:

```python
def test_inventory_classifies_physical_pair(tmp_path):
    src, dst = make_skill_pair(tmp_path, "demo")
    result = inventory_skills(src.parent, dst.parent)
    assert result.by_name("demo").kind == "physical-pair"

def test_inventory_reports_codex_only(tmp_path):
    src_root, dst_root = make_roots(tmp_path)
    make_skill(dst_root, "codex-extra")
    result = inventory_skills(src_root, dst_root)
    assert result.by_name("codex-extra").kind == "codex-only"
```

Add a Windows-only Junction test using `cmd /c mklink /J`; skip only when Junction creation is unavailable.

**Step 2: Run tests and verify RED**

Run:

```powershell
python -m pytest tests/codex_runtime/test_skill_sync.py -k inventory -v
```

Expected: collection/import failure because the synchronizer module does not exist.

**Step 3: Implement minimal inventory types and classification**

Add dataclasses `SkillEntry` and `InventoryResult`, plus:

```python
def inventory_skills(source_root: Path, destination_root: Path) -> InventoryResult:
    """Classify source/destination top-level skills without following reparse points."""
```

Use `Path.iterdir()` only at the top level and Windows file attributes to identify ReparsePoint/Junction before recursion.

**Step 4: Run inventory tests and verify GREEN**

Run the command from Step 2. Expected: inventory tests PASS.

**Step 5: Commit**

```powershell
git add CodexRuntime/skills/sync_claude_to_codex.py tests/codex_runtime/test_skill_sync.py
git commit -m "feat: classify Claude and Codex skill layouts"
```

### Task 2: Implement CODEX-ONLY extraction and frontmatter validation

**Files:**
- Modify: `tests/codex_runtime/test_skill_sync.py`
- Modify: `CodexRuntime/skills/sync_claude_to_codex.py`

**Step 1: Write failing merge tests**

Cover exact preservation, no-block behavior, duplicate markers, missing end marker, nested markers, missing `name`, missing `description`, and directory/name mismatch.

```python
def test_merge_preserves_codex_only_block_verbatim():
    block = "<!-- CODEX-ONLY:START -->\nUse actv_lookup.py.\n<!-- CODEX-ONLY:END -->"
    merged = merge_skill_markdown(CLAUDE_SKILL, CODEX_SKILL_WITH_BLOCK, "demo")
    assert block in merged
    assert "old shared body" not in merged
```

**Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/codex_runtime/test_skill_sync.py -k "merge or frontmatter" -v
```

Expected: FAIL because merge/validation functions are absent.

**Step 3: Implement parser and validator**

Add:

```python
CODEX_START = "<!-- CODEX-ONLY:START -->"
CODEX_END = "<!-- CODEX-ONLY:END -->"

def extract_codex_only_block(text: str) -> str | None: ...
def validate_frontmatter(text: str, expected_name: str) -> list[str]: ...
def merge_skill_markdown(source: str, destination: str | None, expected_name: str) -> str: ...
```

Parse the small YAML subset without adding dependencies: locate the first `---` pair, then read scalar `name:` and `description:` lines. Reject ambiguous or multiline values in v1 rather than guessing.

**Step 4: Run tests and verify GREEN**

Run Step 2 command. Expected: all merge/frontmatter tests PASS.

**Step 5: Commit**

```powershell
git add CodexRuntime/skills/sync_claude_to_codex.py tests/codex_runtime/test_skill_sync.py
git commit -m "feat: preserve Codex-only skill instructions"
```

### Task 3: Build the non-destructive file plan

**Files:**
- Modify: `tests/codex_runtime/test_skill_sync.py`
- Modify: `CodexRuntime/skills/sync_claude_to_codex.py`

**Step 1: Write failing planner tests**

Assert that the plan:

- adds source-only files;
- modifies changed common files;
- skips same-hash files;
- reports but retains destination-only files;
- excludes `__pycache__`, `*.pyc`, logs, temp files, and known output directories;
- blocks symlinks/reparse points inside a physical Skill;
- blocks any resolved path outside its declared root.

**Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/codex_runtime/test_skill_sync.py -k plan -v
```

Expected: FAIL because `build_sync_plan` is absent.

**Step 3: Implement plan dataclasses and hashing**

Add `FileOperation`, `SkillPlan`, `SyncPlan`, `sha256_file()`, exclusion rules, and:

```python
def build_sync_plan(source_root: Path, destination_root: Path, *, allow_create: bool = False) -> SyncPlan:
    """Return an immutable plan; never write to either root."""
```

Special-case `SKILL.md` through `merge_skill_markdown`; all other files remain byte copies.

**Step 4: Run planner tests and verify GREEN**

Run Step 2 command. Expected: planner tests PASS.

**Step 5: Commit**

```powershell
git add CodexRuntime/skills/sync_claude_to_codex.py tests/codex_runtime/test_skill_sync.py
git commit -m "feat: plan non-destructive skill synchronization"
```

### Task 4: Add dry-run CLI and reports

**Files:**
- Modify: `tests/codex_runtime/test_skill_sync.py`
- Modify: `CodexRuntime/skills/sync_claude_to_codex.py`
- Create: `CodexRuntime/skills/README.md`

**Step 1: Write failing CLI tests**

Call `main([...])` with temporary roots and verify:

- no flag means dry-run;
- dry-run does not change target mtimes/hashes;
- human summary includes classification and operation counts;
- `--json-report` writes the documented schema;
- blockers return exit code 2.

**Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/codex_runtime/test_skill_sync.py -k "cli or report or dry_run" -v
```

Expected: FAIL because CLI/report functions are absent.

**Step 3: Implement argparse CLI**

Required arguments/defaults:

```text
--source C:\Users\linkang\.claude\skills
--destination C:\Users\linkang\.agents\skills
--dry-run (default behavior)
--apply
--allow-create
--json-report PATH
```

Make `--dry-run` and `--apply` mutually exclusive. Document examples and exit codes in README.

**Step 4: Run CLI tests and verify GREEN**

Run Step 2 command. Expected: CLI tests PASS.

**Step 5: Commit**

```powershell
git add CodexRuntime/skills/sync_claude_to_codex.py CodexRuntime/skills/README.md tests/codex_runtime/test_skill_sync.py
git commit -m "feat: add dry-run skill sync reporting"
```

### Task 5: Implement transactional apply and rollback

**Files:**
- Modify: `tests/codex_runtime/test_skill_sync.py`
- Modify: `CodexRuntime/skills/sync_claude_to_codex.py`

**Step 1: Write failing transaction tests**

Verify:

- every modified existing file is backed up before first write;
- new files are recorded for rollback removal;
- writes use a sibling temporary file and `os.replace`;
- injected failure restores modified files and removes new files;
- rollback success returns 3, incomplete rollback returns 4;
- a plan containing blockers performs zero writes.

**Step 2: Run tests and verify RED**

```powershell
python -m pytest tests/codex_runtime/test_skill_sync.py -k "apply or rollback or backup" -v
```

Expected: FAIL because transaction functions are absent.

**Step 3: Implement apply**

Add:

```python
def apply_sync_plan(plan: SyncPlan, backup_root: Path) -> ApplyResult:
    """Apply atomically per file and rollback the whole plan on failure."""
```

Generate backup manifests containing source/destination roots, pre-write hashes, operation list, timestamp, and rollback result. Do not delete destination-only files.

**Step 4: Run transaction tests and verify GREEN**

Run Step 2 command. Expected: transaction tests PASS.

**Step 5: Commit**

```powershell
git add CodexRuntime/skills/sync_claude_to_codex.py tests/codex_runtime/test_skill_sync.py
git commit -m "feat: apply skill sync with rollback"
```

### Task 6: Validate against the real Skill trees without writing

**Files:**
- Create: `CodexMemory/reports/skill-sync-dry-run-20260803.json`
- Modify: `CodexMemory/reference_codex_claude_asset_boundary.md`

**Step 1: Run the complete unit suite**

```powershell
python -m pytest tests/codex_runtime/test_skill_sync.py -v
```

Expected: PASS, no skipped tests except Junction creation when unsupported.

**Step 2: Capture pre-run target state**

Record hashes and mtimes for all files under `C:\Users\linkang\.agents\skills` to a temporary comparison file outside the repo.

**Step 3: Run real dry-run**

```powershell
python CodexRuntime/skills/sync_claude_to_codex.py --dry-run --json-report CodexMemory/reports/skill-sync-dry-run-20260803.json
```

Expected:

- exit 0 or 2 only;
- 32 current Junctions classified as skipped;
- 8 known divergent physical Skills appear in differences unless later changes altered the count;
- no target writes.

**Step 4: Prove dry-run made zero writes**

Recompute hashes and mtimes and compare with Step 2. Expected: exact match.

**Step 5: Review blockers**

If exit 2, document every blocker in the report and fix the synchronizer or source data before any apply. Do not weaken safety checks merely to reach exit 0.

**Step 6: Update boundary documentation**

Record actual classification counts, report path, blocker summary, and whether apply is safe.

**Step 7: Commit**

```powershell
git add CodexMemory/reports/skill-sync-dry-run-20260803.json CodexMemory/reference_codex_claude_asset_boundary.md
git commit -m "test: audit Claude to Codex skill synchronization"
```

### Task 7: Controlled first apply and post-apply verification

**Files:**
- Modify: `CodexMemory/reference_codex_claude_asset_boundary.md`
- Create: `CodexMemory/reports/skill-sync-apply-20260803.json`

**Step 1: Present the exact apply list**

Before changing live Skills, show the user the dry-run summary: Skills/files to modify or add, preserved CODEX-ONLY blocks, destination-only files, blockers, and backup destination.

**Step 2: Obtain explicit approval for the first live apply**

This is required because the target contains live Skill instructions and scripts. Do not infer approval from approval of the synchronizer design.

**Step 3: Run apply**

```powershell
python CodexRuntime/skills/sync_claude_to_codex.py --apply --json-report CodexMemory/reports/skill-sync-apply-20260803.json
```

Expected: exit 0 and a printed backup path.

**Step 4: Re-run dry-run**

Expected: no remaining public-source changes; Codex-only and destination-only content still reported as preserved, not removed.

**Step 5: Validate Skill loading and pollution**

Run:

```powershell
rg -l --glob '*.md' '\.Codex' C:\Users\linkang\.agents\skills
```

Expected: zero matches unless an explicitly documented Codex-only instruction intentionally contains the literal term. Then run the available Codex Skill loading smoke check and verify no frontmatter/load errors.

**Step 6: Update documentation and commit**

Record apply result, backup path, post-apply hashes, and smoke-test outcome, then commit only synchronizer-owned files and reports.
