# -*- coding: utf-8 -*-
"""更新 ActvVoyageIsland group2 母版(col6名/col7故事)为深海cn·按IslandType。--apply落盘。"""
import sys
APPLY = "--apply" in sys.argv
P = r"C:\x3\gdconfig\tsv\ActvVoyage__ActvVoyageIsland.tsv"
# IslandType -> (深海名, 深海故事)
T = {
 "1": ("启航港",   "扬帆启航之地，回到此处可获得任意两个海风礁或珊瑚秘境的奖励。"),
 "5": ("海风礁",   "海风轻拂的幸运礁石，可获得一份随机奖励。"),
 "2": ("沉船宝藏", "深海沉船埋藏的宝库，可获得随机航海金币。"),
 "4": ("珊瑚秘境", "珊瑚丛中闪耀宝石光芒，到达后可获得随机钻石。"),
 "3": ("迷雾漩涡", "被迷雾笼罩的未知海域，触发一个随机事件。"),
}
raw = open(P, "rb").read(); crlf = b"\r\n" in raw
text = raw.decode("utf-8"); eol = "\r\n" if crlf else "\n"
trail = text.endswith(eol); lines = text.split(eol)
if trail and lines and lines[-1] == "": lines = lines[:-1]
cnt = 0
for i, ln in enumerate(lines):
    c = ln.split("\t")
    if len(c) > 7 and c[0].strip().isdigit() and c[1].strip() == "2":  # group2 数据行
        t = c[3].strip()
        if t in T:
            c[5], c[6] = T[t]
            lines[i] = "\t".join(c); cnt += 1
print(f"更新 group2 母版 {cnt} 行(应24)")
# 抽样
for ln in lines:
    c = ln.split("\t")
    if len(c)>7 and c[0].strip() in ("201","203","205","202","207".replace("207","")):
        pass
for chk in ("201","202","205","207","219"):
    for ln in lines:
        c = ln.split("\t")
        if c[0].strip()==chk: print(f"  {chk}(type{c[3]}): {c[5]} / {c[6][:20]}…"); break
assert cnt==24
if APPLY:
    out = eol.join(lines)+(eol if trail else "")
    open(P,"wb").write(out.encode("utf-8")); print("*** APPLIED ***")
else: print("--- DRY-RUN ---")
