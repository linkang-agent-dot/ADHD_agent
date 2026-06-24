# -*- coding: utf-8 -*-
"""深海大富翁 结构隔离配置：新建 IslandGroup2 + EventGroup199-206 + repoint 2802/102802。
老配置(2801/组1/EG99-106)一行不动。dry-run 默认只打印，--apply 才落盘。"""
import sys, os
APPLY = "--apply" in sys.argv
ROOT = r"C:\x3\gdconfig\tsv"

# EventGroup(old) -> 岛屿类型 -> 深海岛屿DK
EG_DK = {
    99:  "DK_img_Activity_deepsea_island_start",     # 起始
    100: "DK_img_Activity_deepsea_island_diamond",   # 钻石
    101: "DK_img_Activity_deepsea_island_lucky",     # 幸运
    102: "DK_img_Activity_deepsea_island_lucky",
    103: "DK_img_Activity_deepsea_island_lucky",
    104: "DK_img_Activity_deepsea_island_treasure",  # 宝藏
    105: "DK_img_Activity_deepsea_island_treasure",
    106: "DK_img_Activity_deepsea_island_mystery",   # 神秘
}
MAP_BG_DK  = "DK_img_Activity_Monopoly_deepsea_bg"
HUD_ICON_DK = "DK_img_Activity_icon_Monopoly_deepsea"

def load(path):
    with open(path, "rb") as f:
        raw = f.read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8")
    eol = "\r\n" if crlf else "\n"
    # 末尾是否有终结换行
    trail = text.endswith(eol)
    lines = text.split(eol)
    if trail and lines and lines[-1] == "":
        lines = lines[:-1]
    return lines, eol, trail

def save(path, lines, eol, trail):
    out = eol.join(lines) + (eol if trail else "")
    with open(path, "wb") as f:
        f.write(out.encode("utf-8"))

def is_data(cells, idcol=0):
    v = cells[idcol].strip() if idcol < len(cells) else ""
    return v.isdigit()

# ---------- 1) ActvVoyageIsland: 克隆组1 -> 组2 ----------
isl_p = os.path.join(ROOT, "ActvVoyage__ActvVoyageIsland.tsv")
isl_lines, isl_eol, isl_trail = load(isl_p)
new_isl = []
cnt = 0
for ln in isl_lines:
    c = ln.split("\t")
    if is_data(c, 0) and c[1].strip() == "1":   # IslandGroup==1 的数据行
        n = c[:]
        n[0] = str(int(c[0]) + 100)        # 编号 101-124 -> 201-224
        n[1] = "2"                          # IslandGroup 1 -> 2
        n[7] = str(int(c[7]) + 100)        # EventGroupID +100
        new_isl.append("\t".join(n))
        cnt += 1
print(f"[Island] 克隆 {cnt} 行 (应=24)。样例:")
for s in new_isl[:2] + new_isl[-1:]:
    print("   ", s)
assert cnt == 24, "island 克隆行数 != 24"

# ---------- 2) ActvVoyageEvent: 克隆 EG99-106 -> 199-206 ----------
ev_p = os.path.join(ROOT, "ActvVoyage__ActvVoyageEvent.tsv")
ev_lines, ev_eol, ev_trail = load(ev_p)
new_ev = []
cnt = 0
dkset = set()
for ln in ev_lines:
    c = ln.split("\t")
    if is_data(c, 0) and c[1].strip().isdigit():
        eg = int(c[1])
        if eg in EG_DK:                      # 只克隆组1引用的8个EG
            n = c[:]
            n[0] = str(int(c[0]) + 100000)   # 行ID +100000
            n[1] = str(eg + 100)             # EventGroup +100
            if len(n) > 8 and n[8].startswith("DK_"):   # col9 DKImg 非空才换
                n[8] = EG_DK[eg]
                dkset.add(EG_DK[eg])
            new_ev.append("\t".join(n))
            cnt += 1
print(f"\n[Event] 克隆 {cnt} 行 (应=101)。涉及深海岛DK: {sorted(dkset)}")
assert cnt == 101, "event 克隆行数 != 101"
assert len(dkset) == 5, "深海岛DK种类 != 5"

# ---------- 3) ActvVoyage 2802: IslandGroup 1 -> 2 ----------
vy_p = os.path.join(ROOT, "ActvVoyage__ActvVoyage.tsv")
vy_lines, vy_eol, vy_trail = load(vy_p)
hit = 0
for i, ln in enumerate(vy_lines):
    c = ln.split("\t")
    if is_data(c, 0) and c[0].strip() == "2802":
        assert c[2].strip() == "1", f"2802 IslandGroup 不是1 而是 {c[2]}"
        c[2] = "2"
        vy_lines[i] = "\t".join(c)
        hit += 1
        print(f"\n[ActvVoyage] 2802 IslandGroup 1->2 OK")
assert hit == 1

# ---------- 4) ActvOnline 102802: ActvIcon/ActvImg ----------
ao_p = os.path.join(ROOT, "ActvOnline__ActvOnline.tsv")
ao_lines, ao_eol, ao_trail = load(ao_p)
hit = 0
for i, ln in enumerate(ao_lines):
    c = ln.split("\t")
    if is_data(c, 0) and c[0].strip() == "102802":
        print(f"\n[ActvOnline] 102802 改前 col22(icon)=[{c[21]}] col23(bg)=[{c[22]}]")
        assert c[21] == "DK_img_Activity_icon_Monopoly_6", f"ActvIcon 非预期: {c[21]}"
        assert c[22] == "DK_img_Activity_Monopoly_bg", f"ActvImg 非预期: {c[22]}"
        c[21] = HUD_ICON_DK
        c[22] = MAP_BG_DK
        ao_lines[i] = "\t".join(c)
        hit += 1
        print(f"[ActvOnline] 102802 改后 col22(icon)=[{c[21]}] col23(bg)=[{c[22]}]")
assert hit == 1

# ---------- 落盘 ----------
if APPLY:
    isl_lines2 = isl_lines + new_isl
    ev_lines2 = ev_lines + new_ev
    save(isl_p, isl_lines2, isl_eol, isl_trail)
    save(ev_p, ev_lines2, ev_eol, ev_trail)
    save(vy_p, vy_lines, vy_eol, vy_trail)
    save(ao_p, ao_lines, ao_eol, ao_trail)
    print("\n*** APPLIED 4 表已写盘 ***")
else:
    print("\n--- DRY-RUN (加 --apply 落盘) ---")
