#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重导还原过的 X2 配置表时，把指定行 ID 恢复成某 ref 的值(默认HEAD)，保住之前的还原、其余行保留GSheet导入值。

用途：某表曾把若干行 revert 成 master 值(因GSheet仍是节日值)，重导该表时这些行会被GSheet再带回。
跑本脚本把这些行恢复成 HEAD(=已还原的master值)，只动这些行，其余导入改动不碰。

用法:
  python restore_rows_to_ref.py <相对路径tsv> <id1,id2,...> [ref(默认HEAD)]
例:
  python restore_rows_to_ref.py fo/config/iap_template.tsv 2013670001,2013680004,2013699146
  python restore_rows_to_ref.py fo/config/item.tsv 11119555,11119556,11119557

ID 列自动探测(col1优先, 否则col0)。改完打印恢复了哪些行, 之后自行 git diff 复核 + git add 提交。
"""
import subprocess, os, sys, re
REPO=r"D:\UGit\x2gdconf"
ID_RE=re.compile(r"^\d{3,}$")
def main():
    if len(sys.argv)<3:
        print(__doc__); sys.exit(1)
    F=sys.argv[1].replace("\\","/")
    ids=set(x.strip() for x in sys.argv[2].split(",") if x.strip())
    ref=sys.argv[3] if len(sys.argv)>3 else "HEAD"
    refdata=subprocess.run(["git","-C",REPO,"show",f"{ref}:{F}"],capture_output=True).stdout.decode("utf-8").replace("\r","").split("\n")
    # detect id col
    idcol=1
    for col in (1,0):
        hit=tot=0
        for l in refdata[1:200]:
            c=l.split("\t")
            if len(c)>col: tot+=1; hit+=1 if ID_RE.match(c[col].strip()) else 0
        if tot and hit/tot>0.6: idcol=col; break
    hmap={}
    for l in refdata:
        c=l.split("\t")
        if len(c)>idcol and c[idcol].strip() in ids: hmap[c[idcol].strip()]=l
    missing=ids-set(hmap)
    if missing: print(f"[WARN] ref {ref} 里找不到这些ID: {missing}")
    full=os.path.join(REPO,F)
    txt=open(full,"rb").read().decode("utf-8"); tn=txt.endswith("\n")
    lines=(txt[:-1] if tn else txt).split("\n")
    n=0
    for i,l in enumerate(lines):
        c=l.split("\t")
        if len(c)>idcol and c[idcol].strip() in hmap and lines[i]!=hmap[c[idcol].strip()]:
            lines[i]=hmap[c[idcol].strip()]; n+=1; print("restored",c[idcol].strip())
    open(full,"wb").write(("\n".join(lines)+("\n" if tn else "")).encode("utf-8"))
    print(f"restored rows: {n} (idcol={idcol}, ref={ref})")
if __name__=="__main__": main()
