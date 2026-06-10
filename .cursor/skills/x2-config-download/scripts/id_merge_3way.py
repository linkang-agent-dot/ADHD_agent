#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ID-keyed cell-level 3-way TSV merge for x2gdconf conflict resolution.
Rule (union, dev/ours wins on genuine same-cell conflict):
  - cell: ours==theirs -> keep; ours==base (dev untouched) & theirs changed -> take theirs (absorb master);
          theirs==base (master untouched) & dev changed -> keep ours; both changed differently -> keep ours.
  - row only in theirs AND not in base -> master net-new -> add.
  - row in base+theirs but NOT in ours -> dev deleted -> honor deletion (skip).
ID = column index 1 (0-based); rows whose col1 is not a pure-digit id are 'structural' (header/meta), kept from ours.
"""
import sys, subprocess, re, os

REPO = r"D:\UGit\x2gdconf"
ID_COL = 1
ID_RE = re.compile(r"^\d{3,}$")

def show(stage, path):
    r = subprocess.run(["git","-C",REPO,"show",f":{stage}:{path}"],capture_output=True)
    return r.stdout.decode("utf-8")

def split_lines(txt):
    # keep LF, strip trailing CR; do not add/remove a trailing empty line beyond original
    has_tn = txt.endswith("\n")
    body = txt[:-1] if has_tn else txt
    lines = [l.rstrip("\r") for l in body.split("\n")]
    return lines, has_tn

def rowid(cells):
    # composite key: col1 (must be id-like) + col2, unique across all these tables
    if len(cells) > ID_COL:
        v = cells[ID_COL].strip()
        if ID_RE.match(v):
            c2 = cells[2].strip() if len(cells) > 2 else ""
            return v + "\x00" + c2
    return None

def build_dict(lines):
    d = {}
    for l in lines:
        cells = l.split("\t")
        rid = rowid(cells)
        if rid is not None and rid not in d:
            d[rid] = cells
    return d

def merge_file(path, write):
    base_txt, ours_txt, theirs_txt = show(1,path), show(2,path), show(3,path)
    ours_lines, has_tn = split_lines(ours_txt)
    base_lines,_ = split_lines(base_txt)
    theirs_lines,_ = split_lines(theirs_txt)
    base_d = build_dict(base_lines)
    theirs_d = build_dict(theirs_lines)
    ours_d = build_dict(ours_lines)
    header_cols = len(ours_lines[0].split("\t"))

    stat = {"kept":0,"absorb_cells":0,"conflict_dev_win":0,"absorb_rows":0,"net_new":0,"dev_deleted_honored":0}
    out = []
    for l in ours_lines:
        cells = l.split("\t")
        rid = rowid(cells)
        if rid is None:
            out.append(l); continue
        t = theirs_d.get(rid)
        if t is None:
            out.append(l); stat["kept"]+=1; continue
        b = base_d.get(rid)
        if t == cells:
            out.append(l); stat["kept"]+=1; continue
        # cell-level
        merged = list(cells)
        row_absorb=0; row_conf=0
        n = max(len(cells), len(t))
        for j in range(n):
            o = cells[j] if j < len(cells) else ""
            tv = t[j] if j < len(t) else ""
            bv = b[j] if (b is not None and j < len(b)) else None
            if o == tv:
                continue
            if bv is not None and o == bv:
                merged[j] = tv; row_absorb+=1            # dev untouched, master changed -> absorb
            elif bv is not None and tv == bv:
                pass                                       # master untouched, dev changed -> keep dev
            else:
                pass                                       # genuine conflict -> keep dev
                row_conf+=1
        stat["absorb_cells"]+=row_absorb
        if row_conf: stat["conflict_dev_win"]+=1
        if row_absorb: stat["absorb_rows"]+=1
        out.append("\t".join(merged))

    # master net-new rows: in theirs, not in base, not in ours
    for rid, t in theirs_d.items():
        if rid not in base_d and rid not in ours_d:
            out.append("\t".join(t)); stat["net_new"]+=1
    # dev-deleted honored (info only): in base & theirs but not ours
    for rid in theirs_d:
        if rid in base_d and rid not in ours_d:
            stat["dev_deleted_honored"]+=1

    # validate field counts
    bad = [(i,len(r.split("\t"))) for i,r in enumerate(out) if rowid(r.split("\t")) is not None and len(r.split("\t"))!=header_cols]
    res_txt = "\n".join(out) + ("\n" if has_tn else "")
    if write:
        with open(os.path.join(REPO,path),"wb") as f:
            f.write(res_txt.encode("utf-8"))
    return stat, len(ours_lines), len(out), header_cols, bad

if __name__ == "__main__":
    write = "--write" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    for path in files:
        stat,nin,nout,cols,bad = merge_file(path, write)
        print(f"#### {path}")
        print(f"   行数 ours={nin} -> merged={nout} (+{nout-nin})  列={cols}")
        print(f"   保留dev行={stat['kept']}  吸收master的行={stat['absorb_rows']}(共{stat['absorb_cells']}格)  真冲突取dev行={stat['conflict_dev_win']}  master净新增行={stat['net_new']}  dev删行(尊重)={stat['dev_deleted_honored']}")
        if bad:
            print(f"   !!! 字段数异常行数={len(bad)} 示例={bad[:3]}")
        else:
            print(f"   字段数校验: OK")
