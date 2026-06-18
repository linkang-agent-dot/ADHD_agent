# -*- coding: utf-8 -*-
"""
异国美酒储蓄罐 · 每日双档改造 —— 配置自动应用脚本（纯追加，不改任何现有行）
用法：切到 dev 的 feature 分支后，在 C:\\x3\\gdconfig\\tsv 跑：
    python apply_config_异国美酒双档.py
做三件事（全部 append，幂等：已存在则跳过）：
  1) Pack__Pack.tsv      : 克隆 500031(档1 $9.99) → 新增 500032(档2 $19.99, Group 11)
  2) PiggyBank__PiggyBank.tsv : 新增行 ID 51 (PackID 500032, GroupId 261, MainBg _2)
  3) PiggyBank__Grade.tsv     : 新增组 261, Grade 3-35, Num 20 (行ID 736-768)
注意：档1(500031) 完全不动。客户端选档另见 client_patch_UIPiggyBankContent.md。
⚠️ xlsx-tsv 一致性闸门(2026-06-04起)：本脚本只改 tsv。若 jenkins gate 要求 xlsx 同步，
   需对应在 Pack.xlsx / PiggyBank.xlsx 加同样的行，或接受 gate 自动回灌 + 本次 build rc=24 重导。
"""
import csv, os, io

TSV_DIR = r"C:\x3\gdconfig\tsv"

def read_rows(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    nl = "\r\n" if "\r\n" in text else "\n"
    rows = list(csv.reader(io.StringIO(text), delimiter="\t"))
    return rows, nl, text

def append_rows(path, new_rows, nl):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", lineterminator=nl, quoting=csv.QUOTE_MINIMAL)
    for r in new_rows:
        w.writerow(r)
    add = buf.getvalue()
    # 确保原文件以换行结尾再追加
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        cur = f.read()
    if cur and not cur.endswith(("\n", "\r")):
        add = nl + add
    with io.open(path, "a", encoding="utf-8", newline="") as f:
        f.write(add)

def has_id(rows, val, col=0):
    return any(r and len(r) > col and r[col] == val for r in rows)

# ---------- 1) Pack__Pack.tsv ----------
pack_path = os.path.join(TSV_DIR, "Pack__Pack.tsv")
rows, nl, _ = read_rows(pack_path)
if has_id(rows, "500032"):
    print("[Pack] 500032 已存在，跳过")
else:
    src = next((r for r in rows if r and r[0] == "500031"), None)
    if src is None:
        raise SystemExit("[Pack] 找不到参考行 500031，中止")
    new = list(src)                 # 克隆档1整行(54列)
    new[0]  = "500032"              # col1  ID
    new[6]  = "19.99"               # col7  备注价(显示用)
    new[7]  = "111"                 # col8  Price → PackPrice 点 $19.99
    # col10 PackType=21 / col22 PlayerLv=3 / col25 ColdTime=24h 沿用克隆值，不改
    new[43] = "11"                  # col44 Group → 独立 CD 组(空号11)
    append_rows(pack_path, [new], nl)
    print("[Pack] 已新增 500032 ($19.99, Group 11)")

# ---------- 2) PiggyBank__PiggyBank.tsv ----------
pb_path = os.path.join(TSV_DIR, "PiggyBank__PiggyBank.tsv")
rows, nl, _ = read_rows(pb_path)
if has_id(rows, "51"):
    print("[PiggyBank] 行 51 已存在，跳过")
else:
    src = next((r for r in rows if r and r[0] == "46"), None)
    if src is None:
        raise SystemExit("[PiggyBank] 找不到参考行 46，中止")
    new = list(src)                 # [ID,ResID,Level,PackID,Name,ValueText,MainBg,Num,GroupId,...]
    new[0] = "51"                   # ID
    new[3] = "500032"               # PackID → 档2
    new[6] = "DK_ui_Howtogetit_piggybank_2"   # MainBg 用 _2 与档1(_3)区分(可选)
    new[8] = "261"                  # GroupId → Grade 组 261
    append_rows(pb_path, [new], nl)
    print("[PiggyBank] 已新增行 51 (PackID 500032, GroupId 261)")

# ---------- 3) PiggyBank__Grade.tsv ----------
grade_path = os.path.join(TSV_DIR, "PiggyBank__Grade.tsv")
rows, nl, _ = read_rows(grade_path)
if any(r and len(r) > 2 and r[2] == "261" for r in rows):
    print("[Grade] 组 261 已存在，跳过")
else:
    # 格式: [ID, '', GroupId, Grade, Num]  (参考组260: Grade 3-35, Num 10)
    new_rows = []
    rid = 736
    for grade in range(3, 36):       # 3..35 共 33 行
        new_rows.append([str(rid), "", "261", str(grade), "20"])  # 档2 产出 20
        rid += 1
    append_rows(grade_path, new_rows, nl)
    print("[Grade] 已新增组 261 (Grade 3-35, Num 20, %d 行)" % len(new_rows))

print("完成。请 git diff 复核三张表只新增、未改现有行。")
