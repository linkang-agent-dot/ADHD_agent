from pathlib import Path

p = Path(r"D:\UGit\x2gdconf\fo\config\activity_config.tsv")
ids = {"21127357", "21127358", "21127359", "21127360", "21127361", "21128001"}

with p.open("r", encoding="utf-8-sig", errors="replace") as f:
    for line_no, line in enumerate(f, 1):
        parts = line.rstrip("\n").split("\t")
        if len(parts) > 1 and parts[1] in ids:
            print(line_no, parts[1], parts[2] if len(parts) > 2 else "")
