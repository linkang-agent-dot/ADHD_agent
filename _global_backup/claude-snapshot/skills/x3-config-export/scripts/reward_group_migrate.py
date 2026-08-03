# -*- coding: utf-8 -*-
r"""
X3 Reward 表「整组迁 fresh 连续块」工具 —— must-check 头号 Reward 铁律的实现。

## 为什么需要它
`Reward__Reward.tsv` 有硬约束：**同一 RewardID 内的 seq(col0) 必须连续**。
给一个已有奖励组加行时，若该组后面紧邻别的组、空位不够，就不能就地插入，
也不能 append 到文件尾（会打断连续性）——标准做法是把整组搬到表尾一个全新的
连续块，RewardID 保持不变，所有引用方零改动。

## 用法
  # 预览（不写盘）：给 13031/13032/13033 各追加一行道具 1211，数量跟随组内 1212 那行
  python reward_group_migrate.py --repo C:/X3/gdconfig-xxx \
      --groups 13031,13032,13033 --add-item 1211 --add-name 节日扭蛋币 \
      --copy-amount-from 1212 --dry-run

  # 追加固定数量（每组同值）
  python reward_group_migrate.py --repo ... --groups 13031 --add-item 1211 \
      --add-name 节日扭蛋币 --min 80 --max 208

  # 只迁移不加行（把散乱的组整理成连续块）
  python reward_group_migrate.py --repo ... --groups 13031 --migrate-only

## 安全保证
- 新 seq 起点用 **Python 全表精确扫 max**（must-check：awk 数值比较在该表会漏报真 max）
- 原子写入（tmp + os.replace），避免半截文件
- 写后自动校验：全表 col0 唯一 + 每个目标组 seq 连续，任一不过就报错退出
"""
import argparse
import io
import os
import sys

SEQ_COL = 0        # 行内部 seq
RID_COL = 1        # RewardID（外键，引用方用的就是它）
ITEM_COL = 3
NAME_COL = 4
MIN_COL = 5
MAX_COL = 6
MIRROR_COL = 14    # 末列镜像 seq（原表如此，迁移时要同步改）
HEADER_ROWS = 6


def load(path):
    raw = io.open(path, encoding='utf-8', newline='').readlines()
    nl = '\r\n' if raw and raw[0].endswith('\r\n') else '\n'
    return raw, nl


def exact_max_seq(raw):
    """全表精确 max —— 禁用 awk 数值比较（见 must-check）"""
    mx = 0
    for i, ln in enumerate(raw):
        if i < HEADER_ROWS:
            continue
        c = ln.split('\t')
        if c and c[0].strip().isdigit():
            mx = max(mx, int(c[0]))
    return mx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True, help='gdconfig worktree 根目录（正斜杠）')
    ap.add_argument('--groups', required=True, help='RewardID 列表，逗号分隔')
    ap.add_argument('--add-item', type=int, help='要追加的道具 ID')
    ap.add_argument('--add-name', default='', help='追加行的备注名')
    ap.add_argument('--copy-amount-from', type=int,
                    help='数量跟随组内该道具行的 Min/Max（"等量"场景）')
    ap.add_argument('--min', help='固定 MinNum（与 --copy-amount-from 二选一）')
    ap.add_argument('--max', default='', help='固定 MaxNum，留空=固定发 Min')
    ap.add_argument('--migrate-only', action='store_true', help='只整理连续块，不加行')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    if not a.migrate_only and not a.add_item:
        sys.exit("要么 --migrate-only，要么给 --add-item")
    if a.add_item and not (a.copy_amount_from or a.min):
        sys.exit("--add-item 需要 --copy-amount-from 或 --min")

    path = os.path.join(a.repo, 'tsv', 'Reward__Reward.tsv').replace('\\', '/')
    groups = [int(x) for x in a.groups.split(',')]
    raw, nl = load(path)
    mx = exact_max_seq(raw)
    print("精确 max seq =", mx)

    old = {g: [] for g in groups}
    keep = []
    for i, ln in enumerate(raw):
        if i < HEADER_ROWS:
            keep.append(ln)
            continue
        c = ln.rstrip('\r\n').split('\t')
        if len(c) > RID_COL and c[RID_COL].strip().isdigit() and int(c[RID_COL]) in groups:
            old[int(c[RID_COL])].append(c)
        else:
            keep.append(ln)

    for g in groups:
        if not old[g]:
            sys.exit("组 %d 一行都没找到，检查 RewardID" % g)

    seq = mx + 1
    block = []
    for g in groups:
        rows = [list(r) for r in old[g]]
        if not a.migrate_only:
            tpl = rows[0]
            if a.copy_amount_from:
                src = next((r for r in rows if r[ITEM_COL].strip() == str(a.copy_amount_from)), None)
                if src is None:
                    sys.exit("组 %d 内找不到道具 %d，无法跟随其数量" % (g, a.copy_amount_from))
                vmin, vmax = src[MIN_COL], src[MAX_COL]
            else:
                vmin, vmax = a.min, a.max
            new = list(tpl)
            new[ITEM_COL] = str(a.add_item)
            new[NAME_COL] = a.add_name
            new[MIN_COL] = vmin
            new[MAX_COL] = vmax
            rows.append(new)
            print("  组 %d: %d 行 -> %d 行（+道具%s %s~%s）"
                  % (g, len(rows) - 1, len(rows), a.add_item, vmin, vmax or vmin))
        for r in rows:
            r[SEQ_COL] = str(seq)
            if len(r) > MIRROR_COL:
                r[MIRROR_COL] = str(seq)
            block.append('\t'.join(r) + nl)
            seq += 1

    if a.dry_run:
        print("[dry-run] 新块 seq %d..%d，共 %d 行，未写盘" % (mx + 1, seq - 1, len(block)))
        return

    if keep and not keep[-1].endswith(('\n', '\r\n')):
        keep[-1] += nl
    tmp = path + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.writelines(keep + block)
    os.replace(tmp, path)

    # 写后校验（must-check 要求）
    seen, dup = set(), []
    gseq = {g: [] for g in groups}
    for i, ln in enumerate(io.open(path, encoding='utf-8')):
        if i < HEADER_ROWS:
            continue
        c = ln.rstrip('\r\n').split('\t')
        if not c or not c[SEQ_COL].strip().isdigit():
            continue
        s = int(c[SEQ_COL])
        if s in seen:
            dup.append(s)
        seen.add(s)
        if len(c) > RID_COL and c[RID_COL].strip().isdigit() and int(c[RID_COL]) in groups:
            gseq[int(c[RID_COL])].append(s)

    ok = not dup
    for g in groups:
        ss = gseq[g]
        cont = all(ss[i] + 1 == ss[i + 1] for i in range(len(ss) - 1))
        print("组 %d: %d 行 seq %s..%s 连续=%s" % (g, len(ss), ss[0], ss[-1], cont))
        ok = ok and cont
    if dup:
        print("!! col0 重复:", dup)
    if not ok:
        sys.exit("校验未通过，请检查（文件已写入，可 git checkout 回滚）")
    print("OK：col0 全表唯一 + 各组连续。记得跑 ExportTable.py 验 exit0")


if __name__ == '__main__':
    main()
