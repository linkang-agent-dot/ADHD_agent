# -*- coding: utf-8 -*-
"""拉取首页签命中行：2115 用 comment/desc；2013 用模板描述/礼包标题。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".cursor" / "skills" / "google-workspace-cli"))
import gsheet_query as gq  # noqa: E402

# 与 scan_tech_festival_first_tab 输出一致（首页签命中条目）
TASK_BY_PACK = {
    111110002: [
        211550665, 211550666, 211550667, 211550669, 211550670, 211550671, 211550672, 211550673,
        211574174, 211574179, 211574183, 211574186, 211574190, 211574194, 211574198, 211574202,
        211574206, 211574210, 211574214, 211574218, 211574222, 211574226, 211574230, 211584619,
    ],
    111110003: [
        211550668, 211550672, 211550674, 211574175, 211574187, 211574203, 211574211, 211574223,
        211584621, 211584655, 211584656, 211584658, 211584660, 211584816, 211584817, 211584818,
        211584819, 211584820,
    ],
    111110004: [211574233, 211584623, 211584657, 211584659, 211584821, 211584822],
    111110005: [211584625, 211584661],
    111110006: [211584663, 211586326, 211586328, 211586330],
}

IAP_BY_PACK = {
    111110002: [],
    111110003: [2013510528],
    111110004: [],
    111110005: [201330988, 201330989, 201330990, 201330991, 2013450037, 2013505013],
    111110006: [201330989, 201330990, 201330991, 2013450037, 2013505014],
}


def load_task_rows():
    sid, _ = gq.resolve_table("2115_dev")
    rows = gq.gws_values(sid, "'activity_task_QA'!A:AZ")
    header = rows[0]
    id_col = 1
    idx = {h: i for i, h in enumerate(header)}
    by_id = {}
    for row in rows[1:]:
        if len(row) <= id_col:
            continue
        by_id[str(row[id_col]).strip()] = row
    return idx, by_id


def load_iap_rows():
    sid, _ = gq.resolve_table("2013_dev")
    rows = gq.gws_values(sid, "'iap_template_QA'!A:AZ")
    header = rows[0]
    id_col = 0
    idx = {h: i for i, h in enumerate(header)}
    by_id = {}
    for row in rows[1:]:
        if len(row) <= id_col:
            continue
        by_id[str(row[id_col]).strip()] = row
    return idx, by_id


def cell(row, idx, name, default=""):
    j = idx.get(name)
    if j is None or j >= len(row):
        return default
    return str(row[j]).strip() or default


def main() -> None:
    t_idx, t_by = load_task_rows()
    i_idx, i_by = load_iap_rows()

    pack_names = {
        111110002: "科技节·白 111110002",
        111110003: "科技节·绿 111110003",
        111110004: "科技节·蓝 111110004",
        111110005: "科技节·紫 111110005",
        111110006: "科技节·橙 111110006",
    }

    print("# 科技节保底卡包命中条目 — 含义说明\n")
    print("数据来源：2115 `activity_task_QA` / 2013 `iap_template_QA`（仅首页签扫描命中的那些 ID）。\n")

    print("## 2115 活动任务（A_INT_id）\n")
    print("字段：`N_STR_comment`（策划备注）、`A_STR_task_desc`（LC key 或空）。\n")

    for pid in sorted(TASK_BY_PACK.keys()):
        ids = TASK_BY_PACK[pid]
        if not ids:
            continue
        print(f"### {pack_names[pid]}\n")
        for tid in sorted(set(ids)):
            row = t_by.get(str(tid))
            if not row:
                print(f"- **{tid}**：(表中未找到该行)\n")
                continue
            cmt = cell(row, t_idx, "N_STR_comment", "—")
            desc = cell(row, t_idx, "A_STR_task_desc", "—")
            if desc == "—" or not desc:
                line = f"- **{tid}**：{cmt}"
            else:
                line = f"- **{tid}**：{cmt}；任务描述 key：`{desc}`"
            print(line + "\n")
        print()

    print("## 2013 IAP 模板（A_INT_id）\n")
    print("字段：`A_STR_temp_type`、`N_STR_temp_desc`、`A_STR_pkg_title`。\n")

    seen_iap = set()
    for pid in sorted(IAP_BY_PACK.keys()):
        ids = IAP_BY_PACK[pid]
        if not ids:
            continue
        print(f"### {pack_names[pid]}\n")
        for iid in sorted(set(ids)):
            if iid in seen_iap:
                continue
            seen_iap.add(iid)
            row = i_by.get(str(iid))
            if not row:
                print(f"- **{iid}**：(表中未找到该行)\n")
                continue
            typ = cell(row, i_idx, "A_STR_temp_type", "—")
            nd = cell(row, i_idx, "N_STR_temp_desc", "—")
            title = cell(row, i_idx, "A_STR_pkg_title", "—")
            print(f"- **{iid}**：类型 `{typ}`；描述：`{nd}`；礼包标题：`{title}`\n")
        print()

    print("---\n")
    print("## 归纳\n")
    print(
        "- **2115**：多为「节日通用连锁 / 密码箱 / 某期活动」任务链里的**免费档或中间档**奖励，"
        "白/绿/蓝/紫/橙对应链上不同进度；同一 `A_INT_id` 若出现在两种颜色统计里，"
        "是因为**奖励 JSON 里同时含多个档位的卡包**。\n"
    )
    print(
        "- **2013**：命中集中在**带多档随机/可选奖励的礼包模板**（`N_STR_temp_desc` / `A_STR_pkg_title` 可看出具体礼包名）；"
        "首页签下**白/蓝档未单独出现**在模板道具列里，可能与礼包结构或道具写在其他列有关。\n"
    )


if __name__ == "__main__":
    main()
