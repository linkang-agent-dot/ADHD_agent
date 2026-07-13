# -*- coding: utf-8 -*-
"""Stage 3: combine A+B+C into finished videos.

Usage: python remix.py <批次名> <数量|max> --base <产品根目录>

Constraints: A/B different script clusters (text-sim dedup), never repeat a
combo in the ledger, never reproduce a reference final (all three parts
similar), prefer 3 different hosts, spread segment usage evenly.
Reads optional <base>/pipeline/reference_finals.json: [[Atext,Btext,Ctext],...]
"""
import difflib
import json
import re
from pathlib import Path

from common import parse_base, paths, run, norm

SIM_SCRIPT = 0.60
SIM_REF = 0.55


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio() if a and b else 0.0


def host_of(source):
    m = re.search(r"-([一-鿿]+)-", source)  # first CJK run between dashes = host name
    return m.group(1) if m else source


def seg_text(P, entry):
    j = P["analysis"] / (Path(entry["source"]).stem + ".json")
    if not j.exists():
        return ""
    data = json.loads(j.read_text(encoding="utf-8"))
    t0, t1 = entry["start"], entry["end"]
    return norm("".join(s["text"] for s in data["segments"]
                        if s["start"] >= t0 - 0.5 and s["end"] <= t1 + 0.5))


def main():
    base, args = parse_base(__doc__)
    P = paths(base)
    batch = args[0] if args else "batch1"
    want = args[1] if len(args) > 1 else "max"
    ref_file = P["pipeline"] / "reference_finals.json"
    references = json.loads(ref_file.read_text(encoding="utf-8")) if ref_file.exists() else []

    ledger_path = P["lib"] / "ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    pool = {"A": [], "B": [], "C": []}
    for e in ledger:
        e["text"] = seg_text(P, e)
        e["host"] = host_of(e["source"])
        pool[e["segment"]].append(e)

    for typ, items in pool.items():  # script clusters
        cid = 0
        for it in items:
            it.setdefault("cluster", None)
        for it in items:
            if it["cluster"] is None:
                it["cluster"] = f"{typ}{cid}"
                for other in items:
                    if other["cluster"] is None and sim(it["text"], other["text"]) >= SIM_SCRIPT:
                        other["cluster"] = f"{typ}{cid}"
                cid += 1
    print({t: f"{len(v)} segs / {len({i['cluster'] for i in v})} scripts"
           for t, v in pool.items()})

    used = {tuple(u) for e in ledger for u in e.get("used_in", [])}

    def ref_like(a, b, c):
        return any(sim(a["text"], norm(ra)) >= SIM_REF and sim(b["text"], norm(rb)) >= SIM_REF
                   and sim(c["text"], norm(rc)) >= SIM_REF for ra, rb, rc in references)

    def pick_bc(a, require_diff_host):
        for b in sorted(pool["B"], key=lambda x: usage.get(x["file"], 0)):
            if b["source"] == a["source"] or sim(a["text"], b["text"]) >= SIM_SCRIPT:
                continue
            if require_diff_host and b["host"] == a["host"]:
                continue
            for c in sorted(pool["C"], key=lambda x: usage.get(x["file"], 0)):
                if c["source"] in (a["source"], b["source"]):
                    continue
                if (a["file"], b["file"], c["file"]) in used or ref_like(a, b, c):
                    continue
                return b, c
        return None

    usage, combos = {}, []
    n_target = len(pool["A"]) if want == "max" else int(want)
    guard = 0
    while len(combos) < n_target and guard < n_target * 40:
        guard += 1
        a = min(pool["A"], key=lambda x: usage.get(x["file"], 0))
        bc = pick_bc(a, True) or pick_bc(a, False)
        if not bc:
            print("pool exhausted at", len(combos))
            break
        b, c = bc
        combos.append((a, b, c))
        used.add((a["file"], b["file"], c["file"]))
        for x in (a, b, c):
            usage[x["file"]] = usage.get(x["file"], 0) + 1

    out_dir = P["out"] / batch
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for i, (a, b, c) in enumerate(combos, 1):
        name = f"成品_{i:03d}__A{a['host']}+B{b['host']}+C{c['host']}.mp4"
        lst = out_dir / "_l.txt"
        lst.write_text("".join(f"file '{(P['lib'] / x['file']).as_posix()}'\n"
                               for x in (a, b, c)), encoding="utf-8")
        try:
            run([P["ffmpeg"], "-y", "-f", "concat", "-safe", "0", "-i", lst,
                 "-c", "copy", out_dir / name])
            ok = True
        except RuntimeError:
            ok = False
        lst.unlink()
        records.append({"no": i, "file": name, "ok": ok, "A": a["file"], "B": b["file"],
                        "C": c["file"], "hosts": [a["host"], b["host"], c["host"]],
                        "dur": round(sum(x["end"] - x["start"] for x in (a, b, c)), 1)})
        for e in ledger:
            if e["file"] in (a["file"], b["file"], c["file"]):
                e.setdefault("used_in", []).append([a["file"], b["file"], c["file"]])
        print(("OK " if ok else "FAIL ") + name)

    ledger_path.write_text(json.dumps(
        [{k: v for k, v in e.items() if k not in ("text", "host", "cluster")} for e in ledger],
        ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / "记录.json").write_text(json.dumps(records, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
    lines = [f"# 批次 {batch} 摘要", "", f"- 成片数：{len(records)}（目标 {n_target}）",
             f"- 素材池：A×{len(pool['A'])} B×{len(pool['B'])} C×{len(pool['C'])}",
             "- 约束：A/B 异脚本、历史防重、排除参考成品同款、优先三段异主播", "",
             "| # | 成片 | 主播组合 | 时长 |", "|---|---|---|---|"]
    lines += [f"| {r['no']} | {r['file']} | {'+'.join(r['hosts'])} | {r['dur']}s |"
              for r in records]
    (out_dir / "摘要.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"done: {len(records)} finals -> {out_dir}")


if __name__ == "__main__":
    main()
