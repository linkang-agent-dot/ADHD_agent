# -*- coding: utf-8 -*-
"""Audit fo/config table diffs for merge e981df7 vs parent1; optional gws spot-check."""
import json
import re
import subprocess
import sys

GWS = r"C:\Users\linkang\AppData\Roaming\npm\gws.cmd"
GDCONFIG = r"C:\gdconfig"
INDEX_SS = "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c"
PARENT = "e981df7^1"
MERGE = "e981df7"


def run_git(*args, input=None):
    r = subprocess.run(
        ["git", "-C", GDCONFIG, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        input=input,
    )
    return r.stdout, r.stderr, r.returncode


def gws_values(spreadsheet_id: str, range_a1: str):
    params = json.dumps({"spreadsheetId": spreadsheet_id, "range": range_a1})
    r = subprocess.run(
        [GWS, "sheets", "spreadsheets", "values", "get", "--params", params],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        return None, r.stderr
    try:
        return json.loads(r.stdout).get("values", []), None
    except json.JSONDecodeError:
        return None, r.stdout[:500]


def gws_sheets(spreadsheet_id: str):
    params = json.dumps(
        {"spreadsheetId": spreadsheet_id, "fields": "sheets.properties.title,sheets.properties.gridProperties.rowCount"}
    )
    r = subprocess.run(
        [GWS, "sheets", "spreadsheets", "get", "--params", params],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        return None
    data = json.loads(r.stdout)
    return [
        (s["properties"]["title"], s["properties"].get("gridProperties", {}).get("rowCount", 0))
        for s in data.get("sheets", [])
    ]


def pick_tab(titles_rows):
    """Prefer *_QA, then *_master, else largest GRID by rowCount."""
    names = [t for t, _ in titles_rows]
    for pref in ("_QA", "QA"):
        for t, n in titles_rows:
            if pref in t and "备份" not in t:
                return t
    for t, n in titles_rows:
        if "master" in t.lower():
            return t
    # fallback: max rows among tabs that look like data (exclude 备份/日志)
    cand = [(t, n) for t, n in titles_rows if "备份" not in t and "日志" not in t]
    if not cand:
        cand = titles_rows
    cand.sort(key=lambda x: -x[1])
    return cand[0][0] if cand else names[0]


def load_index():
    params = json.dumps(
        {"spreadsheetId": INDEX_SS, "range": "fw_gsheet_config!A1:F1200"}
    )
    r = subprocess.run(
        [GWS, "sheets", "spreadsheets", "values", "get", "--params", params],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    rows = json.loads(r.stdout).get("values", [])
    # P2: B=编号前缀, C=页签, D=子表ID
    m = {}
    for row in rows:
        if len(row) < 4:
            continue
        tab = str(row[2]).strip()
        sid = str(row[3]).strip()
        if not sid or sid == "SheetID":
            continue
        m[tab] = sid
    return m


def diff_summary(path: str):
    out, err, code = run_git("diff", PARENT, MERGE, "--", path)
    if code != 0:
        return None
    added = [ln[1:] for ln in out.splitlines() if ln.startswith("+") and not ln.startswith("+++")]
    removed = [ln[1:] for ln in out.splitlines() if ln.startswith("-") and not ln.startswith("---")]
    # data rows: first field looks like int id
    id_re = re.compile(r"^(\d+)\t")
    add_ids = []
    rem_ids = []
    for ln in added:
        m = id_re.match(ln)
        if m:
            add_ids.append(m.group(1))
    for ln in removed:
        m = id_re.match(ln)
        if m:
            rem_ids.append(m.group(1))
    return {
        "chars": len(out),
        "added_rows": len(added),
        "removed_rows": len(removed),
        "add_ids_head": add_ids[:12],
        "rem_ids_head": rem_ids[:12],
        "only_comment_change": False,
    }


def find_row_for_id(tsv_rel: str, target_id: str):
    """1-based row in merge commit file matching first column."""
    out, _, code = run_git("show", f"{MERGE}:{tsv_rel}")
    if code != 0 or not out:
        return None
    for i, line in enumerate(out.splitlines(), 1):
        if line.startswith(target_id + "\t"):
            return i
    return None


def main():
    tab_to_ss = load_index()
    changed, _, _ = run_git(
        "diff", "--name-only", PARENT, MERGE, "--", "fo/config/"
    )
    paths = [p for p in changed.splitlines() if p.strip()]
    print("=== fo/config 变更文件数:", len(paths), "===\n")

    issues = []
    gws_checks = []

    for rel in sorted(paths):
        base = rel.split("/")[-1].replace(".tsv", "")
        summ = diff_summary(rel)
        if not summ:
            continue
        sid = tab_to_ss.get(base)
        line = f"{base}: diff_chars={summ['chars']} ~+{summ['added_rows']} ~-{summ['removed_rows']} sid={'OK' if sid else 'MISSING'}"
        if summ["add_ids_head"]:
            line += f" | 新增ID样例:{','.join(summ['add_ids_head'][:5])}"
        if summ["rem_ids_head"]:
            line += f" | 删除ID样例:{','.join(summ['rem_ids_head'][:5])}"
        print(line)

        # Heuristic: pure renames? if many +/- with same id count mismatch
        ai, ri = set(summ["add_ids_head"]), set(summ["rem_ids_head"])
        if ai & ri:
            issues.append(f"{base}: 同批diff出现相同ID增减(可能为整行替换/改字段): {ai & ri}")

        if not sid:
            issues.append(f"{base}: fw_gsheet_config 未找到页签名映射，无法 gws 抽查")

        # gws spot: pick one new id or first removed id's replacement
        probe_id = None
        if summ["add_ids_head"]:
            probe_id = summ["add_ids_head"][0]
        elif summ["rem_ids_head"]:
            probe_id = summ["rem_ids_head"][0]

        if sid and probe_id and summ["chars"] < 800000:  # skip iap_config full verify
            row = find_row_for_id(rel, probe_id)
            if row and row <= 50000:
                gws_checks.append((base, sid, probe_id, row, rel))

    print("\n=== 启发式疑点 ===")
    for x in issues:
        print(x)
    if not issues:
        print("(无)")

    print("\n=== gws 抽样（每表 1 个 ID，对比 merge 提交文件同列前几格）===")
    for base, sid, probe_id, row, rel in gws_checks[:28]:
        titles = gws_sheets(sid)
        if not titles:
            print(f"{base}: 无法列出子表 ({sid})")
            continue
        tab = pick_tab(titles)
        # 读 A 列该行附近 1 行，列 A-G
        rng = f"'{tab.replace(chr(39), chr(39)+chr(39))}'!A{row}:G{row}"
        vals, err = gws_values(sid, rng)
        if err:
            print(f"{base}: gws 读失败 {err[:120]}")
            continue
        if not vals:
            print(f"{base}: 行{row} 空（可能行号与线上一致性不同） tab={tab}")
            continue
        out_show, _, c2 = run_git("show", f"{MERGE}:{rel}")
        git_line = None
        if c2 == 0 and out_show:
            lines = out_show.splitlines()
            if row - 1 < len(lines):
                git_line = lines[row - 1]
        if git_line is None:
            print(f"{base}: git show {MERGE}:{rel} 无第{row}行")
            continue
        gws_cells = "\t".join(vals[0][:7]) if vals[0] else ""
        match = gws_cells.split("\t")[0] == probe_id if vals[0] else False
        print(f"{base} tab={tab} row={row} id={probe_id} 首列一致={match}")
        if not match:
            print(f"  gws: {gws_cells[:160]}...")
            print(f"  git: {git_line[:160]}...")

    # iap_config: only stats
    iap = diff_summary("fo/config/iap_config.tsv")
    if iap:
        print("\n=== iap_config（过大，仅 diff 规模）===")
        print(f"chars={iap['chars']} added_lines~{iap['added_rows']} removed~{iap['removed_rows']}")
        out, _, _ = run_git("diff", PARENT, MERGE, "--", "fo/config/iap_config.tsv")
        # 统计以 + 开头的行里新出现的 8 位 ID
        new_ids = re.findall(r"^\+(\d{7,9})\t", out, re.M)
        del_ids = re.findall(r"^-(\d{7,9})\t", out, re.M)
        from collections import Counter

        print(f"以 diff 行首计: +侧7-9位ID行数={len(new_ids)} -侧={len(del_ids)}")
        if new_ids:
            c = Counter(new_ids)
            print("新增行首ID top5:", c.most_common(5))
        if del_ids:
            c2 = Counter(del_ids)
            print("删除行首ID top5:", c2.most_common(5))

    return 0


if __name__ == "__main__":
    sys.exit(main())
