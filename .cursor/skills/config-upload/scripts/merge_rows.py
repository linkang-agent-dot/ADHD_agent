"""
精准行合并脚本：从新下载的TSV中提取指定ID的行，合并到备份（原始）TSV中。
自动检测header中A_INT_id所在列。
用法：python merge_rows.py <tsv文件路径> <目标ID列表（逗号分隔）>
"""
import sys
import os

def find_id_col(header_line):
    cols = header_line.split("\t")
    for i, col in enumerate(cols):
        if col.strip() == "A_INT_id":
            return i
    return 0  # fallback to first column

def merge_rows(tsv_path, target_ids):
    bak_path = tsv_path + ".bak"
    new_path = tsv_path

    if not os.path.exists(bak_path):
        print("ERROR: backup not found: " + bak_path)
        sys.exit(1)

    target_id_set = set(str(i) for i in target_ids)

    with open(bak_path, encoding="utf-8") as f:
        original_lines = f.read().splitlines()

    with open(new_path, encoding="utf-8") as f:
        new_lines = f.read().splitlines()

    id_col = find_id_col(original_lines[0])
    print("  ID column index: " + str(id_col) + " (" + original_lines[0].split("\t")[id_col] + ")")

    new_rows = {}
    for line in new_lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) > id_col:
            row_id = parts[id_col].strip()
            new_rows[row_id] = line

    result = [original_lines[0]]
    replaced = set()
    for line in original_lines[1:]:
        if not line.strip():
            result.append(line)
            continue
        parts = line.split("\t")
        row_id = parts[id_col].strip() if len(parts) > id_col else ""
        if row_id in target_id_set:
            if row_id in new_rows:
                result.append(new_rows[row_id])
                replaced.add(row_id)
                print("  [updated] " + row_id)
            else:
                print("  [WARN] " + row_id + " not in new TSV, keeping original")
                result.append(line)
        else:
            result.append(line)

    new_ids = target_id_set - replaced
    for new_id in sorted(new_ids):
        if new_id in new_rows:
            result.append(new_rows[new_id])
            print("  [added] " + new_id)
        else:
            print("  [WARN] " + new_id + " not found anywhere, skipping")

    with open(new_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(result))
        if result:
            f.write("\n")

    print("  => done: " + new_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python merge_rows.py <tsv> <id1,id2,...>")
        sys.exit(1)
    path = sys.argv[1]
    ids = [x.strip() for x in sys.argv[2].split(",")]
    print("file: " + path)
    print("targets: " + str(ids))
    merge_rows(path, ids)
