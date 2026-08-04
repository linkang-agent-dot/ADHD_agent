#!/usr/bin/env python3
"""完整复刻马戏拼图 101830 -> 101831，所有可变子配置使用独立 ID。

默认只校验并打印计划；传 --apply 才追加 TSV。脚本幂等：目标任一 ID 已存在即拒绝执行。
"""

from __future__ import annotations

import argparse
import csv
import io
from pathlib import Path


SOURCE = {
    "ao": "101830",
    "puzzle": "1830",
    "tc": "1831",
    "reward_group": "1101",
    "task_group": "109",
    "reward_ids": ("603801", "603805", "603806"),
}

TARGET = {
    "ao": "101831",
    "puzzle": "1831",
    "tc": "1832",
    "reward_group": "1102",
    "task_group": "111",
    "reward_ids": ("603807", "603808", "603809"),
}

FILES = {
    "ao": "tsv/ActvOnline__ActvOnline.tsv",
    "puzzle": "tsv/ActvPuzzle__ActvPuzzle.tsv",
    "tc": "tsv/TimeCycle__TimeCycle.tsv",
    "puzzle_reward": "tsv/ActvPuzzle__ActvPuzzleReward.tsv",
    "puzzle_task": "tsv/ActvPuzzle__ActvPuzzleTask.tsv",
    "reward": "tsv/Reward__Reward.tsv",
    "text": "tsv/i18n/Text__Text.tsv",
}


def read_rows(path: Path) -> list[list[str]]:
    return list(csv.reader(io.StringIO(path.read_text(encoding="utf-8-sig")), delimiter="\t"))


def one(rows: list[list[str]], col: int, value: str, label: str) -> list[str]:
    hits = [row for row in rows[6:] if len(row) > col and row[col] == value]
    if len(hits) != 1:
        raise AssertionError(f"{label}: expected 1 row for col{col}={value}, got {len(hits)}")
    return hits[0].copy()


def many(rows: list[list[str]], col: int, value: str, count: int, label: str) -> list[list[str]]:
    hits = [row.copy() for row in rows[6:] if len(row) > col and row[col] == value]
    if len(hits) != count:
        raise AssertionError(f"{label}: expected {count} rows for col{col}={value}, got {len(hits)}")
    return hits


def assert_absent(rows: list[list[str]], col: int, values: tuple[str, ...], label: str) -> None:
    found = sorted({row[col] for row in rows[6:] if len(row) > col and row[col] in values})
    if found:
        raise AssertionError(f"{label}: target IDs already exist: {found}")


def append_rows(path: Path, rows: list[list[str]]) -> None:
    for row in rows:
        if any("\t" in cell or "\r" in cell or "\n" in cell for cell in row):
            raise AssertionError(f"{path.name}: cloned row contains physical tab/newline")
    with path.open("a", encoding="utf-8", newline="") as f:
        for row in rows:
            f.write("\t".join(row) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    tables = {name: read_rows(repo / rel) for name, rel in FILES.items()}

    assert_absent(tables["ao"], 0, (TARGET["ao"],), "ActvOnline")
    assert_absent(tables["puzzle"], 0, (TARGET["puzzle"],), "ActvPuzzle")
    assert_absent(tables["tc"], 0, (TARGET["tc"],), "TimeCycle")
    assert_absent(tables["puzzle_reward"], 3, (TARGET["reward_group"],), "ActvPuzzleReward")
    assert_absent(tables["puzzle_task"], 2, (TARGET["task_group"],), "ActvPuzzleTask")
    assert_absent(tables["reward"], 1, TARGET["reward_ids"], "Reward")

    ao = one(tables["ao"], 0, SOURCE["ao"], "ActvOnline")
    ao[0] = TARGET["ao"]
    ao[1] = "26马戏节-BINGO拼图(复刻101830·独立活动)"
    ao[4] = TARGET["puzzle"]
    ao[7] = TARGET["tc"]

    puzzle = one(tables["puzzle"], 0, SOURCE["puzzle"], "ActvPuzzle")
    puzzle[0] = TARGET["puzzle"]
    puzzle[1] = TARGET["reward_group"]
    puzzle[2] = TARGET["task_group"]

    tc = one(tables["tc"], 0, SOURCE["tc"], "TimeCycle")
    tc[0] = TARGET["tc"]
    tc[1] = "活动-26马戏节BINGO拼图101831-复刻101830(当前过期关闭·排期时重设窗口)"

    reward_map = dict(zip(SOURCE["reward_ids"], TARGET["reward_ids"]))
    puzzle_rewards = many(tables["puzzle_reward"], 3, SOURCE["reward_group"], 11, "ActvPuzzleReward")
    for index, row in enumerate(puzzle_rewards):
        row[0] = str(int(TARGET["reward_group"]) * 1000 + index)
        row[3] = TARGET["reward_group"]
        row[4] = reward_map[row[4]]

    puzzle_tasks = many(tables["puzzle_task"], 2, SOURCE["task_group"], 25, "ActvPuzzleTask")
    for index, row in enumerate(puzzle_tasks):
        row[0] = str(int(TARGET["task_group"]) * 100 + index)
        row[2] = TARGET["task_group"]
        row[8] = TARGET["reward_ids"][0]

    reward_rows: list[list[str]] = []
    for source_id in SOURCE["reward_ids"]:
        reward_rows.extend([row.copy() for row in tables["reward"][6:] if len(row) > 1 and row[1] == source_id])
    if len(reward_rows) != 6:
        raise AssertionError(f"Reward: expected 6 source rows, got {len(reward_rows)}")
    max_seq = max(int(row[0]) for row in tables["reward"][6:] if row and row[0].isdigit())
    for offset, row in enumerate(reward_rows, 1):
        row[0] = str(max_seq + offset)
        row[1] = reward_map[row[1]]

    text_key_map = {
        "TXT_ActvPuzzle_PuzzleName_1830": "TXT_ActvPuzzle_PuzzleName_1831",
        "TXT_ActvOnline_ActvName_101830": "TXT_ActvOnline_ActvName_101831",
        "TXT_ActvOnline_ActvDesc_101830": "TXT_ActvOnline_ActvDesc_101831",
    }
    text_rows: list[list[str]] = []
    for old_key, new_key in text_key_map.items():
        source = one(tables["text"], 0, old_key, f"Text {old_key}")
        if any(row and row[0] == new_key for row in tables["text"][6:]):
            raise AssertionError(f"Text target key already exists: {new_key}")
        source[0] = new_key
        text_rows.append(source)

    changes = {
        "ao": [ao],
        "puzzle": [puzzle],
        "tc": [tc],
        "puzzle_reward": puzzle_rewards,
        "puzzle_task": puzzle_tasks,
        "reward": reward_rows,
        "text": text_rows,
    }
    total = sum(len(rows) for rows in changes.values())
    if total != 48:
        raise AssertionError(f"expected 48 total rows, got {total}")
    print("PLAN", {name: len(rows) for name, rows in changes.items()}, "TOTAL", total)
    print("MAPPING", f"{SOURCE['ao']} -> {TARGET['ao']}; source and 101829 unchanged")

    if not args.apply:
        print("DRY_RUN_OK: pass --apply to write")
        return
    for name, rows in changes.items():
        append_rows(repo / FILES[name], rows)
    print("APPLY_OK")


if __name__ == "__main__":
    main()
