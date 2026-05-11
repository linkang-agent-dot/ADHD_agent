from pathlib import Path

p = Path(r"D:\UGit\x2gdconf\fo\config\activity_config.tsv")
target_ids = {"21127359", "21127360", "21127361"}

raw = p.read_bytes()
newline = b"\r\n" if b"\r\n" in raw else b"\n"
text = raw.decode("utf-8-sig")
lines = text.splitlines()

target_lines = []
remaining = []
insert_after_idx = None

for line in lines:
    parts = line.split("\t")
    row_id = parts[1] if len(parts) > 1 else ""
    if row_id in target_ids:
        target_lines.append(line)
        continue
    remaining.append(line)

if [line.split("\t")[1] for line in target_lines] != ["21127359", "21127360", "21127361"]:
    raise SystemExit(f"unexpected target order: {[line.split(chr(9))[1] for line in target_lines]}")

for idx, line in enumerate(remaining):
    parts = line.split("\t")
    if len(parts) > 1 and parts[1] == "21127358":
        insert_after_idx = idx
        break

if insert_after_idx is None:
    raise SystemExit("cannot find 21127358")

new_lines = remaining[: insert_after_idx + 1] + target_lines + remaining[insert_after_idx + 1 :]
new_text = "\n".join(new_lines) + "\n"
if newline == b"\r\n":
    new_text = new_text.replace("\n", "\r\n")

p.write_bytes(new_text.encode("utf-8"))
print("moved 21127359-21127361 after 21127358")
