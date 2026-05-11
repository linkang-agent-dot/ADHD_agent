from pathlib import Path

p = Path(r"D:\UGit\x2gdconf\fo\config\iap_config.tsv")
raw = p.read_bytes()
newline = b"\r\n" if b"\r\n" in raw else b"\n"
text = raw.decode("utf-8-sig")
lines = text.splitlines()

fixed = False
for i, line in enumerate(lines):
    parts = line.split("\t")
    if len(parts) > 1 and parts[1] == "2011920111":
        if len(parts) < 19:
            parts += [""] * (19 - len(parts))
            lines[i] = "\t".join(parts)
            fixed = True
        elif len(parts) > 19:
            raise SystemExit(f"too many columns: {len(parts)}")
        break
else:
    raise SystemExit("2011920111 not found")

if not fixed:
    print("already fixed")
else:
    out = "\n".join(lines) + "\n"
    if newline == b"\r\n":
        out = out.replace("\n", "\r\n")
    p.write_bytes(out.encode("utf-8"))
    print("fixed 2011920111 to 19 columns")
