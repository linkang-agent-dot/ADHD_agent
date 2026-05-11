from pathlib import Path

root = Path(r"D:\UGit\x2gdconf")
targets = {"1511030002", "1511018855"}
for p in (root / "fo").rglob("*.tsv"):
    for i, line in enumerate(p.read_text(encoding="utf-8-sig", errors="ignore").splitlines(), 1):
        if any(t in line for t in targets):
            parts = line.split("\t")
            hit = [t for t in targets if t in line]
            print(p.relative_to(root), i, hit, parts[:8])
