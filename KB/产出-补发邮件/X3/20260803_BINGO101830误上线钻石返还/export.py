#!/usr/bin/env python3
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

SKILL_SCRIPTS = Path(r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.path.insert(0, str(SKILL_SCRIPTS))
from _datain_api import execute_sql

OUT = Path(__file__).resolve().parent

SQL = r"""
WITH medal_sessions AS (
    SELECT
        server_id,
        user_id,
        session_id,
        MIN(created_at) AS medal_first,
        MAX(created_at) AS medal_last,
        SUM(change_count) AS medals_received
    FROM v1090.ods_user_asset
    WHERE partition_date BETWEEN '2026-07-30' AND '2026-07-31'
      AND created_at >= TIMESTAMP '2026-07-30 15:23:00'
      AND created_at <  TIMESTAMP '2026-07-31 13:43:56'
      AND asset_id = 'Item_1210'
      AND change_type = '1'
      AND reason_id = 'activity_reward'
    GROUP BY 1,2,3
),
diamond_sessions AS (
    SELECT
        server_id,
        user_id,
        session_id,
        COUNT(*) AS fast_finish_count,
        SUM(change_count) AS diamonds_consumed,
        MIN(created_at) AS diamond_first,
        MAX(created_at) AS diamond_last
    FROM v1090.ods_user_asset
    WHERE partition_date BETWEEN '2026-07-30' AND '2026-07-31'
      AND created_at >= TIMESTAMP '2026-07-30 15:23:00'
      AND created_at <  TIMESTAMP '2026-07-31 13:43:56'
      AND asset_id = 'Item_1002'
      AND change_type = '2'
      AND change_count = 1000
      AND reason_id = 'activity_puzzle_task_fast_finish'
    GROUP BY 1,2,3
),
card_sessions AS (
    SELECT
        server_id,
        user_id,
        session_id,
        SUM(change_count) AS cards_received
    FROM v1090.ods_user_asset
    WHERE partition_date BETWEEN '2026-07-30' AND '2026-07-31'
      AND created_at >= TIMESTAMP '2026-07-30 15:23:00'
      AND created_at <  TIMESTAMP '2026-07-31 13:43:56'
      AND asset_id = 'Item_180083'
      AND change_type = '1'
      AND reason_id = 'activity_reward'
    GROUP BY 1,2,3
),
session_detail AS (
    SELECT
        d.server_id,
        d.user_id,
        d.session_id,
        d.fast_finish_count,
        d.diamonds_consumed,
        m.medals_received,
        COALESCE(c.cards_received, 0) AS cards_received,
        d.diamond_first,
        d.diamond_last,
        m.medal_first,
        m.medal_last
    FROM diamond_sessions d
    JOIN medal_sessions m
      ON d.server_id = m.server_id
     AND d.user_id = m.user_id
     AND d.session_id = m.session_id
    LEFT JOIN card_sessions c
      ON d.server_id = c.server_id
     AND d.user_id = c.user_id
     AND d.session_id = c.session_id
)
SELECT
    server_id,
    user_id,
    SUM(fast_finish_count) AS fast_finish_count,
    SUM(diamonds_consumed) AS diamonds_consumed,
    SUM(medals_received) AS medals_received,
    SUM(cards_received) AS cards_received,
    MIN(diamond_first) AS diamond_first,
    MAX(diamond_last) AS diamond_last,
    MIN(medal_first) AS medal_first,
    MAX(medal_last) AS medal_last
FROM session_detail
GROUP BY 1,2
ORDER BY diamonds_consumed DESC, server_id, user_id
"""


def main():
    os.environ["DATAIN_API_KEY"] = os.environ.get("DATAIN_API_KEY") or os.environ.get("DATAIN_API_KEY_USER", "")
    rows = execute_sql(SQL, datasource="TRINO_HF")
    if not rows:
        raise SystemExit("No affected players returned")

    for row in rows:
        row["server_id"] = str(row["server_id"])
        row["user_id"] = str(row["user_id"])
        for key in ("fast_finish_count", "diamonds_consumed", "medals_received", "cards_received"):
            row[key] = int(row.get(key) or 0)

    assert len({(r["server_id"], r["user_id"]) for r in rows}) == len(rows)
    assert all(r["diamonds_consumed"] == r["fast_finish_count"] * 1000 for r in rows)

    detail_path = OUT / "BINGO101830_受影响玩家明细.csv"
    fieldnames = [
        "server_id", "user_id", "fast_finish_count", "diamonds_consumed",
        "medals_received", "cards_received", "diamond_first", "diamond_last",
        "medal_first", "medal_last",
    ]
    with detail_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    import_path = OUT / "BINGO101830_钻石返还_iGame导入.csv"
    with import_path.open("w", encoding="gbk", newline="") as f:
        writer = csv.writer(f, lineterminator="\r\n")
        for row in rows:
            writer.writerow([row["server_id"], row["user_id"], f"[1002*{row['diamonds_consumed']}]", "", "", ""])

    distribution = Counter(r["diamonds_consumed"] for r in rows)
    summary = {
        "activity_cfg_id": 101830,
        "query_window_bjt": ["2026-07-30 15:23:00", "2026-07-31 13:43:56"],
        "affected_players": len(rows),
        "affected_servers": len({r["server_id"] for r in rows}),
        "fast_finish_count": sum(r["fast_finish_count"] for r in rows),
        "diamonds_to_return": sum(r["diamonds_consumed"] for r in rows),
        "medals_received": sum(r["medals_received"] for r in rows),
        "cards_received": sum(r["cards_received"] for r in rows),
        "diamond_distribution": {str(k): distribution[k] for k in sorted(distribution)},
        "scope": "Only 1000-diamond fast-finish rows in sessions that received Item_1210 via activity_reward before official puzzle 101829 started.",
        "excluded": "Four 1500-diamond rows from two users; 101830 group 109 has no 1500-diamond FinishCost.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
