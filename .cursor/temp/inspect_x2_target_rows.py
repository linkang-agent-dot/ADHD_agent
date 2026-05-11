from pathlib import Path

root = Path(r"D:\UGit\x2gdconf")

for rel, ids in [
    ("fo/config/iap_config.tsv", {"2011920110", "2011920111", "2011920112"}),
    ("fo/config/activity_config.tsv", {"21127359", "21127360", "21127361"}),
]:
    print(f"\n=== {rel} ===")
    p = root / rel
    for i, line in enumerate(p.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
        parts = line.split("\t")
        if i <= 3 or (len(parts) > 1 and parts[1] in ids):
            print(i, len(parts), parts)

print("\n=== search 1511030002 / 1511018855 ===")
for p in (root / "fo").rglob("*.tsv"):
    txt = p.read_text(encoding="utf-8-sig", errors="ignore")
    if "1511030002" in txt or "1511018855" in txt:
        print(p.relative_to(root))
