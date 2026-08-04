import ast
import csv
import json
import re
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
FESTIVAL_SOURCE = Path(r"C:\ADHD_agent\KB\方法论\tools\circus_launch_gen.py")
DETAIL_SOURCE = BASE / "BINGO101830_受影响玩家明细.csv"
DETAIL_OUTPUT = BASE / "BINGO101830_受影响玩家明细_暂不上拼图服.csv"
MAIL_OUTPUT = BASE / "BINGO101830_钻石返还_iGame导入_暂不上拼图服.csv"
SUMMARY_OUTPUT = BASE / "summary_puzzle_paused_servers.json"


def load_festival_servers():
    source = FESTIVAL_SOURCE.read_text(encoding="utf-8")
    match = re.search(r"SERVERS\s*=\s*(\[[\s\S]*?\])\s*# D35\+", source)
    if not match:
        raise RuntimeError("未在马戏节部署清单中找到 SERVERS")
    servers = set(ast.literal_eval(match.group(1)))
    if len(servers) != 87:
        raise RuntimeError(f"马戏节服务器应为 87 个，实际 {len(servers)} 个")
    return servers


def main():
    festival_servers = load_festival_servers()
    with DETAIL_SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        original = list(reader)

    selected = [row for row in original if int(row["server_id"]) not in festival_servers]
    with DETAIL_OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selected)

    with MAIL_OUTPUT.open("w", encoding="gbk", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\r\n")
        for row in selected:
            writer.writerow(
                [row["server_id"], row["user_id"], f'[1002*{row["diamonds_consumed"]}]', "", "", ""]
            )

    base_summary = json.loads((BASE / "summary.json").read_text(encoding="utf-8"))
    distribution = Counter(int(row["diamonds_consumed"]) for row in selected)
    summary = {
        **base_summary,
        "subset_label": "仅暂不上拼图服玩家",
        "filter_rule": "server_id outside the finalized 87-server D35+ deployment list; user confirmed this complement is the server batch temporarily not receiving the puzzle activity",
        "filter_source": str(FESTIVAL_SOURCE),
        "puzzle_active_server_count": len(festival_servers),
        "excluded_puzzle_active_players": len(original) - len(selected),
        "excluded_puzzle_active_diamonds": sum(int(row["diamonds_consumed"]) for row in original)
        - sum(int(row["diamonds_consumed"]) for row in selected),
        "affected_players": len(selected),
        "affected_servers": len({row["server_id"] for row in selected}),
        "fast_finish_count": sum(int(row["fast_finish_count"]) for row in selected),
        "diamonds_to_return": sum(int(row["diamonds_consumed"]) for row in selected),
        "medals_received": sum(int(row["medals_received"]) for row in selected),
        "cards_received": sum(int(row["cards_received"]) for row in selected),
        "diamond_distribution": {str(key): distribution[key] for key in sorted(distribution)},
        "selected_server_ids": sorted({int(row["server_id"]) for row in selected}),
    }
    SUMMARY_OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    assert len({(row["server_id"], row["user_id"]) for row in selected}) == len(selected)
    assert all(int(row["diamonds_consumed"]) == int(row["fast_finish_count"]) * 1000 for row in selected)
    print(
        json.dumps(
            {
                "players": summary["affected_players"],
                "servers": summary["affected_servers"],
                "diamonds": summary["diamonds_to_return"],
                "excluded_puzzle_active_players": summary["excluded_puzzle_active_players"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
