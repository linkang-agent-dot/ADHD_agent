"""One-off: create Google Doc from iap_config_x2master_sync_from_qa.md via gws."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def gws_exe() -> str:
    """Windows: npm installs gws.cmd; subprocess cannot run gws.ps1 as executable."""
    p = shutil.which("gws.cmd") or shutil.which("gws")
    if not p or p.lower().endswith(".ps1"):
        raise FileNotFoundError("gws not on PATH (install: npm i -g @googleworkspace/cli)")
    return p

MD_PATH = Path(__file__).resolve().parent.parent / "iap_config_x2master_sync_from_qa.md"


def md_to_plain(text: str) -> str:
    lines_out: list[str] = []
    for line in text.splitlines():
        if line.strip() == "---":
            lines_out.append("─" * 50)
            lines_out.append("")
            continue
        if re.match(r"^\|[\s\-:|]+\|$", line.strip()):
            continue
        if line.startswith("# "):
            lines_out.append(line[2:].strip())
            lines_out.append("")
        elif line.startswith("## "):
            lines_out.append(line[3:].strip())
            lines_out.append("")
        else:
            lines_out.append(line.replace("**", ""))
    out = "\n".join(lines_out)
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")
    return out.strip() + "\n"


def main() -> int:
    if not MD_PATH.is_file():
        print(f"Missing: {MD_PATH}", file=sys.stderr)
        return 1
    body = md_to_plain(MD_PATH.read_text(encoding="utf-8"))
    title = "iap_config：以 QA 为准同步到 master 说明"

    create_json = json.dumps({"title": title}, ensure_ascii=False)
    gx = gws_exe()
    r = subprocess.run(
        [gx, "docs", "documents", "create", "--json", create_json],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        return r.returncode
    doc = json.loads(r.stdout)
    doc_id = doc["documentId"]

    req = {
        "requests": [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": body,
                }
            }
        ]
    }
    r2 = subprocess.run(
        [
            gx,
            "docs",
            "documents",
            "batchUpdate",
            "--params",
            json.dumps({"documentId": doc_id}),
            "--json",
            json.dumps(req, ensure_ascii=False),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r2.returncode != 0:
        print(r2.stderr or r2.stdout, file=sys.stderr)
        return r2.returncode

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
