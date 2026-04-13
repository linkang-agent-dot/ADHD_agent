import json
import re


def main() -> None:
    src = r"C:\Users\linkang\.cursor\projects\c-ADHD-agent\agent-tools\0b00bf78-8d2b-4b25-aec3-8013bd928e85.txt"
    sheet = "activity_task_QA"
    reward_col = "G"  # A_INT_group(A), A_INT_id(B), ... A_ARR_reward(G)

    updates: list[dict] = []

    with open(src, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.startswith("row "):
                continue
            m = re.match(r"^row (\d+): (.*)$", line)
            if not m:
                continue
            row_num = int(m.group(1))
            tsv = m.group(2)
            cols = tsv.split("\t")
            if len(cols) < 7:
                raise RuntimeError(f"Unexpected column count at row {row_num}: {len(cols)}")

            reward = cols[6]
            reward = reward.replace('"id":111110002,', '"id":111110305,')
            reward = reward.replace('"id":11119772,', '"id":11112500,')
            # Minify reward JSON to avoid CLI arg splitting on spaces
            reward_obj = json.loads(reward)
            reward = json.dumps(reward_obj, ensure_ascii=False, separators=(",", ":"))

            updates.append(
                {
                    "range": f"{sheet}!{reward_col}{row_num}",
                    "values": [[reward]],
                }
            )

    body = {
        "valueInputOption": "RAW",
        "data": updates,
    }

    out_path = r"C:\ADHD_agent\batch_update_2115_rewards_easter.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False, separators=(",", ":"))

    old_left = [
        u
        for u in updates
        if "11119772" in u["values"][0][0] or "111110002" in u["values"][0][0]
    ]
    print(f"updates: {len(updates)}")
    print(f"out: {out_path}")
    print(f"old_left: {len(old_left)}")
    if updates:
        print(f"first_range: {updates[0]['range']}")
        print(f"first_value_prefix: {updates[0]['values'][0][0][:120]}")


if __name__ == "__main__":
    main()

