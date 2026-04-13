# -*- coding: utf-8 -*-
"""从 iap_config.tsv 的 TimeInfo / IapStatus 中剔除无效 activity Id 引用。"""
import json
from pathlib import Path

IAP_PATH = Path(r"D:\UGit\x2gdconf\fo\config\iap_config.tsv")

# 2112 中不存在的活动 Id
BAD = {21127226, 21127233, 21127240, 21127241, 21127242, 21127243, 21127244}
# 与 21127226 成对误用的门槛 Id（仅在与 21127226 同一条 IapStatus 中一并去掉）
PAIR_DROP_25 = 21127225

IDX_TIME = 9
IDX_IAP = 12


def clean_timeinfo(s: str) -> str:
    s = (s or "").strip()
    if not s or s == "{}":
        return "{}"
    try:
        d = json.loads(s)
    except json.JSONDecodeError:
        return s
    if not isinstance(d, dict):
        return s
    normal = d.get("normal")
    if not isinstance(normal, list):
        return s
    new_n = []
    for item in normal:
        if not isinstance(item, dict):
            new_n.append(item)
            continue
        aid = item.get("actv_id")
        bid = item.get("actv_base_id")
        if aid in BAD or bid in BAD:
            continue
        new_n.append(item)
    rest = {k: v for k, v in d.items() if k != "normal"}
    if not new_n:
        if not rest:
            return "{}"
        rest["normal"] = []
        return json.dumps(rest, ensure_ascii=False, separators=(",", ":"))
    rest["normal"] = new_n
    return json.dumps(rest, ensure_ascii=False, separators=(",", ":"))


def clean_iapstatus(s: str) -> str:
    s = (s or "").strip()
    if not s or s == "[]":
        return "[]"
    if s == "0":
        return "0"
    try:
        arr = json.loads(s)
    except json.JSONDecodeError:
        return s
    if not isinstance(arr, list):
        return s
    had_226 = any(
        isinstance(x, dict)
        and x.get("typ") == "recharge_actv"
        and x.get("id") == 21127226
        for x in arr
    )
    out = []
    for x in arr:
        if not isinstance(x, dict):
            out.append(x)
            continue
        if x.get("typ") == "recharge_actv":
            rid = x.get("id")
            if rid in BAD:
                continue
            if had_226 and rid == PAIR_DROP_25:
                continue
        out.append(x)
    return json.dumps(out, ensure_ascii=False, separators=(",", ":"))


def main():
    text = IAP_PATH.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out_lines = []
    changed = 0
    for i, line in enumerate(lines):
        if not line.endswith("\n"):
            line_nl = line + "\n"
        else:
            line_nl = line
        raw = line_nl.rstrip("\r\n")
        parts = raw.split("\t")
        if (
            len(parts) > IDX_IAP
            and (not parts[0].strip())
            and parts[1].strip().isdigit()
        ):
            t0 = parts[IDX_TIME]
            m0 = parts[IDX_IAP]
            t1 = clean_timeinfo(t0)
            m1 = clean_iapstatus(m0)
            if t1 != t0 or m1 != m0:
                parts[IDX_TIME] = t1
                parts[IDX_IAP] = m1
                changed += 1
                raw = "\t".join(parts)
            line_nl = raw + ("\n" if line_nl.endswith("\n") else "")
        out_lines.append(line_nl)

    IAP_PATH.write_text("".join(out_lines), encoding="utf-8", newline="")
    print(f"updated rows: {changed}")


if __name__ == "__main__":
    main()
