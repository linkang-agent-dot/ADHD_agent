# -*- coding: utf-8 -*-
"""Check comment column values in the diff data."""
import subprocess

REPO = r"C:\gdconfig"
SOURCE = "origin/dev_7days_v86"
TARGET = "origin/dev"

files = [
    "fo/config/activity_config.tsv",
    "fo/config/activity_package.tsv",
    "fo/config/activity_asset_retake.tsv",
    "fo/config/activity_task.tsv",
]

for f in files:
    name = f.split("/")[-1].replace(".tsv", "")
    content = subprocess.run(
        ["git", "show", f"{SOURCE}:{f}"],
        capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=REPO
    ).stdout
    lines = content.strip().split('\n')
    header = lines[0].split('\t')
    
    print(f"\n=== {name} ({len(header)} cols) ===")
    print(f"  Header: {header}")
    
    comment_idx = None
    for i, h in enumerate(header):
        if 'comment' in h.lower():
            comment_idx = i
            break
    
    if comment_idx is not None:
        print(f"  Comment column: [{comment_idx}] {header[comment_idx]}")
        for row in lines[1:4]:
            cols = row.split('\t')
            val = cols[comment_idx] if comment_idx < len(cols) else '<MISSING>'
            print(f"    id={cols[0]}, comment=[{val}]")
    else:
        print(f"  No comment column found")
    
    # Check diff rows
    diff = subprocess.run(
        ["git", "diff", f"{TARGET}...{SOURCE}", "--", f],
        capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=REPO
    ).stdout
    
    added = []
    for line in diff.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            c = line[1:].strip()
            if c:
                added.append(c)
    
    if added and comment_idx is not None:
        print(f"  Diff rows comment values:")
        for row in added[:3]:
            cols = row.split('\t')
            val = cols[comment_idx] if comment_idx < len(cols) else '<MISSING>'
            print(f"    id={cols[0]}, comment=[{val}]")
