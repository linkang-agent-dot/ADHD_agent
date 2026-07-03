# -*- coding: utf-8 -*-
r"""合并多场 GM纯命令 → 切成每块 ≤5,000,000 字符的粘贴块(iGame GM 输入框上限)。
按行边界切,绝不切断单条命令。用法: python _chunk_gm_commands.py <场key1> <场key2> ...
  例: python _chunk_gm_commands.py R32-ESPvAUT R32-PORvCRO R32-SUIvALG
产出: 发奖csv\GM纯命令_合并_partN.txt (N从1起) ; 每块字符数打印出来。
"""
import sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
CSVDIR = pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\发奖csv")

# ★iGame GM 输入框实测 ~500,000 字符就爆 → 默认 490,000 留余量(非5M!);可 --limit 覆盖
args = sys.argv[1:]
LIMIT = 490_000
if "--limit" in args:
    i = args.index("--limit"); LIMIT = int(args[i + 1]); args = args[:i] + args[i + 2:]
keys = args
if not keys:
    sys.exit("用法: python _chunk_gm_commands.py [--limit N] <场key...>  (如 R32-ESPvAUT R32-PORvCRO)")

# 收集所有命令行(跨场合并,去尾空行)
lines = []
for k in keys:
    f = CSVDIR / f"GM纯命令_{k}.txt"
    if not f.exists():
        print(f"⚠️跳过(不存在): {f.name}"); continue
    for ln in f.read_text(encoding='utf-8').splitlines():
        if ln.strip():
            lines.append(ln)
print(f"合并 {len(keys)} 场 → 共 {len(lines)} 条命令")

# 按行边界切块(块内用\n连接,块字符数含换行 ≤LIMIT)
chunks, cur, cur_len = [], [], 0
for ln in lines:
    add = len(ln) + 1  # +1 换行
    if cur and cur_len + add > LIMIT:
        chunks.append(cur); cur, cur_len = [], 0
    cur.append(ln); cur_len += add
if cur:
    chunks.append(cur)

# 写出
for i, ch in enumerate(chunks, 1):
    out = CSVDIR / (f"GM纯命令_合并_part{i}.txt" if len(chunks) > 1 else "GM纯命令_合并.txt")
    txt = "\n".join(ch)
    out.write_text(txt, encoding='utf-8')
    print(f"  {out.name}: {len(txt):,} 字符 / {len(ch)} 条命令  {'✅' if len(txt) <= LIMIT else '🔴超限'}")
print(f"共 {len(chunks)} 块 (每块 ≤{LIMIT:,} 字符)")
