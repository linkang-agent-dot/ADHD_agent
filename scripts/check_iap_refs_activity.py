# -*- coding: utf-8 -*-
"""检查 2011(iap_config) 是否引用不存在的 2112(activity_config) 行 Id。"""
import re
import sys
from pathlib import Path

REPO = Path(r"D:\UGit\x2gdconf")
ACT = REPO / "fo" / "config" / "activity_config.tsv"
IAP = REPO / "fo" / "config" / "iap_config.tsv"

# 明确语义：仅匹配「指向活动配置行」的字段，避免误报 2115 task 等
PATTERNS = [
    (r'"actv_id"\s*:\s*(\d+)', "actv_id"),
    (r'"actv_base_id"\s*:\s*(\d+)', "actv_base_id"),
    (r'"typ"\s*:\s*"recharge_actv"\s*,\s*"id"\s*:\s*(\d+)', "recharge_actv.id"),
]


def load_activity_ids(path: Path) -> set[str]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    data_start = 0
    for i, line in enumerate(lines):
        parts = line.split("\t")
        if parts and parts[0] == "fwcli_name":
            data_start = i + 1
            break
    ids: set[str] = set()
    for line in lines[data_start:]:
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        aid = parts[1].strip()
        if aid.isdigit():
            ids.add(aid)
    return ids


def main():
    if not ACT.is_file() or not IAP.is_file():
        print("缺少文件:", ACT, IAP, file=sys.stderr)
        sys.exit(1)

    valid = load_activity_ids(ACT)
    iap_lines = IAP.read_text(encoding="utf-8", errors="replace").splitlines()

    data_start = 0
    for i, line in enumerate(iap_lines):
        parts = line.split("\t")
        if parts and parts[0] == "fwcli_name":
            data_start = i + 1
            break

    issues = []
    for li, line in enumerate(iap_lines[data_start:], start=data_start + 1):
        parts = line.split("\t")
        iap_id = parts[1].strip() if len(parts) > 1 else "?"
        for pat, label in PATTERNS:
            for m in re.finditer(pat, line):
                ref = m.group(1)
                if ref not in valid:
                    issues.append((iap_id, li, label, ref))

    print(f"分支工作区: {REPO}")
    print(f"activity_config 有效 Id 数: {len(valid)}")
    print(f"iap_config 检查行数: {len(iap_lines) - data_start}")
    print(f"缺失引用数: {len(issues)}")
    if not issues:
        print("未发现 2011 引用不存在的 activity_config(2112) Id。")
        return

    by_ref: dict[str, list[tuple[str, str, int]]] = {}
    for iap_id, li, label, ref in issues:
        by_ref.setdefault(ref, []).append((iap_id, label, li))

    print("\n【去重】缺失的 activity_config Id 及引用次数：")
    for ref in sorted(by_ref, key=lambda x: int(x)):
        rows = by_ref[ref]
        print(f"  {ref}  →  {len(rows)} 处（涉及 iap 行数）")
    print()

    print("以下 iap_config 行引用的活动 Id 在 activity_config 中不存在：\n")
    print("| iap Id | 行号 | 字段 | 引用的活动Id |")
    print("|--------|------|------|--------------|")
    for iap_id, li, label, ref in issues:
        print(f"| {iap_id} | {li} | {label} | {ref} |")


if __name__ == "__main__":
    main()
