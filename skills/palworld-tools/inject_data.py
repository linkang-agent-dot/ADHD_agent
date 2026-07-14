# -*- coding: utf-8 -*-
"""把 pals_full.json 精简后注入全图鉴 HTML 的 const PALS 行。可重复执行。"""
import json, io, re

pals = json.load(open("pals_full.json", encoding="utf-8"))
slim = []
for p in pals:
    slim.append({
        "num": p.get("num"), "name": p["name"], "elems": p.get("elems", []),
        "hp": p.get("hp"), "atk": p.get("atk"), "def": p.get("def"),
        "works": p.get("works", []), "skill": p.get("skill", ""),
        "skill_desc": (p.get("skill_desc") or "")[:180],
        "ride": p.get("ride", False), "fly": p.get("fly", False),
        "skill_tech": p.get("skill_tech"), "minlv": p.get("minlv"),
    })
data = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))

tp = r"C:\Users\linkang\Desktop\幻兽帕鲁1.0_全图鉴.html"
s = io.open(tp, encoding="utf-8").read()
s2 = re.sub(r"const PALS = \[.*?\];\n", lambda m: "const PALS = " + data + ";\n", s, count=1, flags=re.S)
assert s2 != s and '"minlv"' in s2, "injection failed"
tmp = tp + ".tmp"
io.open(tmp, "w", encoding="utf-8").write(s2)
import os; os.replace(tmp, tp)
print("reinjected", len(slim), "pals,", len(data) // 1024, "KB")
