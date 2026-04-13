# -*- coding: utf-8 -*-
"""Export 42 template rows from iap_template_x2（qa） to TSV."""
import csv
import json
import subprocess
from pathlib import Path

IDS = [
    2013450003, 2013450004, 2013450005, 2013450006, 2013450007, 2013450008, 2013450009,
    2013450010, 2013450011, 2013450012, 2013450013, 2013450014, 2013450015, 2013450016,
    2013450017, 2013450018, 2013450019, 2013450020, 2013450021, 2013450022, 2013450023,
    2013500192, 2013500193, 2013500194, 2013500195, 2013500196, 2013500197, 2013500198,
    2013500202, 2013500203, 2013500204, 2013500205, 2013500206, 2013500207,
    2013500391, 2013500392, 2013500393, 2013500394,
    2013920001, 2013920002, 2013920003, 2013920004,
]
IDS = [str(i) for i in IDS]

SPREADSHEET = "1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E"
# Fullwidth parentheses in sheet name
RANGE = "'iap_template_x2\uFF08qa\uFF09'!A1:AS8000"


def main() -> None:
    cmd = (
        "gws sheets +read "
        f"--spreadsheet {SPREADSHEET} "
        f"--range {RANGE!r} "
        "--format json"
    )
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        print("gws stderr:", p.stderr[:4000])
        raise SystemExit(p.returncode)

    data = json.loads(p.stdout)
    rows = data["values"]

    by_id: dict[str, list] = {}
    for r in rows[7:]:
        if len(r) < 2:
            continue
        k = str(r[1]).strip()
        if k and k not in by_id:
            by_id[k] = r

    maxc = max((len(r) for r in rows[:7]), default=0)
    for i in IDS:
        if i in by_id:
            maxc = max(maxc, len(by_id[i]))

    def pad(r: list) -> list:
        return list(r) + [""] * (maxc - len(r))

    base = Path(__file__).resolve().parent.parent
    full = base / "iap_template_x2qa_42rows_paste.tsv"
    only = base / "iap_template_x2qa_42rows_only.tsv"

    missing: list[str] = []
    with full.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        for r in rows[:7]:
            w.writerow(pad(r))
        for i in IDS:
            if i not in by_id:
                missing.append(i)
            else:
                w.writerow(pad(by_id[i]))

    lines = full.read_text(encoding="utf-8-sig").splitlines()
    only.write_text("\n".join(lines[7:]) + "\n", encoding="utf-8-sig")

    print("written", full)
    print("written", only)
    print("max cols", maxc)
    print("missing:", missing if missing else "none")


if __name__ == "__main__":
    main()
