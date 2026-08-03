# -*- coding: utf-8 -*-
r"""
X3 节日「活动道具回收」审计 —— 查某节日的节日道具有没有配回收、补偿多少。

## 机制（服务端 ActivityMeta.cs::RecycleActivityItem）
`ActvOnline` col44 `ItemRecycle`，格式 `道具ID,补偿RewardID`，多组用 `|` 分隔。
活动结束时：全额扣掉玩家持有的该道具 → 按 **Reward 内容 × 持有数** 折算 → 发邮件
（`CConstCfg.ActvItemRecycleMail`）。**第二个值是 RewardID 不是 itemID**（数字常与
VIP点数 itemID 2022 撞号，别看错）。

## 已知惯例与坑
- **组 2022 = 钻石×100，是跨节日通用回收补偿，被 20+ 活动共用**（30留/元旦/尼罗/
  情人节/春节/世界杯/深海/马戏…含线上在跑的）。**要改补偿额必须新建独立组**，
  直接改 2022 = 历代所有节日一起变（must-check「跨节日共享奖池组」铁律）。
- **历代节日只回收「消耗券」、不回收「兑换币」**（尼罗1128✅/1129❌、情人节1134✅/1135❌、
  世界杯1146✅/1147❌、深海1200✅/1201❌）——兑换币留给玩家自己去集市花掉，是既定设计。
- 🪤**照位置抄会翻车**：扭蛋机的道具语义与别的节日**相反**——它的「币」(1211)才是免费
  消耗品、「券」(1212)是真金白银买的。按历代「回收券不回收币」的位置惯例抄，结果就是
  免费的赔钱、付费的蒸发。**配回收前先判道具的真实性质（免费产出 vs 付费购买），别看名字。**

## 用法
  python recycle_audit.py --groups 143,144                    # 按 ActvGroup 审某节日
  python recycle_audit.py --items 1207-1215,1057,1058,1202    # 直接指定道具清单
  python recycle_audit.py --groups 144 --repo C:/X3/gdconfig-xxx --ref origin/dev_festival
"""
import argparse
import csv
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

IR_COL = 44      # ActvOnline.ItemRecycle
GRP_COL = 38     # ActvOnline.GroupId


def show(repo, ref, path):
    r = subprocess.run(['git', '-C', repo, 'show', f'{ref}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"读不到 {path}：{r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout.decode('utf-8', errors='replace')


def parse_items(spec):
    out = []
    for part in spec.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-')
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='C:/x3/gdconfig')
    ap.add_argument('--ref', default='origin/dev_festival')
    ap.add_argument('--groups', help='ActvGroup 列表，逗号分隔（按节日审）')
    ap.add_argument('--items', help='道具ID清单，支持 1207-1215 区间写法')
    a = ap.parse_args()
    if not a.groups and not a.items:
        sys.exit('至少给 --groups 或 --items')

    rew, iname = {}, {}
    for ln in show(a.repo, a.ref, 'tsv/Reward__Reward.tsv').split('\n')[6:]:
        c = ln.split('\t')
        if len(c) > 6 and c[1].strip().isdigit():
            rew.setdefault(int(c[1]), []).append((c[3], c[4], c[5]))
    for ln in show(a.repo, a.ref, 'tsv/Item__Item.tsv').split('\n')[6:]:
        c = ln.split('\t')
        if len(c) > 1 and c[0].strip().isdigit():
            iname[int(c[0])] = c[1]

    rows = list(csv.reader(io.StringIO(show(a.repo, a.ref, 'tsv/ActvOnline__ActvOnline.tsv')),
                           delimiter='\t'))
    groups = set(a.groups.split(',')) if a.groups else None
    recycled, actv, shared = {}, [], {}
    for r in rows[6:]:
        if not r or not r[0].strip().isdigit():
            continue
        ir = r[IR_COL] if len(r) > IR_COL else ''
        for pair in ir.split('|') if ir.strip() else []:
            p = pair.split(',')
            if len(p) == 2:
                shared.setdefault(int(p[1]), []).append(r[0])   # 全表统计补偿组共享面
        if groups is not None and (r[GRP_COL] if len(r) > GRP_COL else '') not in groups:
            continue
        actv.append((r[0], r[2], ir))
        for pair in ir.split('|') if ir.strip() else []:
            p = pair.split(',')
            if len(p) == 2:
                recycled[int(p[0])] = (int(p[1]), r[0], r[2])

    def fmt(rid):
        it = rew.get(rid, [])
        return ' + '.join('%s×%s' % (n or ('item' + i), q) for i, n, q in it) or f'(组{rid}空!)'

    items = parse_items(a.items) if a.items else sorted(
        set(recycled) | {i for i in iname if 1000 <= i < 1300 and any(
            i == x for x in recycled)})
    if a.groups and not a.items:
        items = sorted(set(recycled))
        print('※ 未给 --items，只列已配回收的道具；要查漏配请用 --items 给全清单\n')

    print('=' * 92)
    print('%-6s %-14s %-34s %s' % ('道具', '名称', '每 1 个补偿', '配在'))
    print('-' * 92)
    for iid in items:
        nm = (iname.get(iid, '?') or '?')[:13]
        if iid in recycled:
            rid, ao, ao_nm = recycled[iid]
            n_shared = len(set(shared.get(rid, [])))
            tag = f'  ⚠️组{rid}被{n_shared}个活动共用' if n_shared > 1 else ''
            print('%-6s %-14s %-34s %s(%s)%s' % (iid, nm, fmt(rid), ao, ao_nm, tag))
        else:
            print('%-6s %-14s %-34s %s' % (iid, nm, '❌ 未配（活动结束直接作废）', '—'))

    print('\n' + '=' * 92)
    print('各活动 ItemRecycle 现状')
    print('-' * 92)
    for ao, nm, ir in sorted(actv):
        print('  %-9s %-12s %s' % (ao, (nm or '')[:12], ir or '(空)'))
    print('\n提示：补偿组被多活动共用时，改补偿额必须新建独立组，别直接改共享组。')


if __name__ == '__main__':
    main()
