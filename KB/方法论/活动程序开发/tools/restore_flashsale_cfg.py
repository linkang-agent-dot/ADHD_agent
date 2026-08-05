# -*- coding: utf-8 -*-
"""
【范式脚本】恢复被删除的 X3 配置行 —— 改 TARGETS/PRICE_FIX 即可用于任何"配置源被撤除、
要从历史版本手术式捞回来"的场合。本文件保留限时抢购(2026-08-04)的实参作为可运行样例。

★ 为什么不能直接 git checkout 整文件：目标分支往往已落后主干上百个提交，
  整文件回滚会把别人的改动一起盖掉。所以只能**按行恢复 + 逐条闸门**。

★ 五道闸门（任一不满足就 BLOCK 不写，这是"别冲配置"的落地方式）：
  1. schema 闸门：源版本有、当前 schema 已删除的字段 → BLOCK（字段语义变了不能盲搬）
  2. **按字段名映射，不按列位置搬** —— 表可能在中间插过列
     （实例：ActvOnline 插入 BaseActvID 等 4 列，把 ExcludeActvIDs 从 idx52 挤到 idx56，
      按位置照搬会整行串列，而且不会报错）
  3. id 撞号闸门（含多主键表的第二唯一列，如 Reward 的 ID vs RewardID）
  4. 按 id 数值**插入有序位置**，不追加末尾（Reward 有组内 id 连续性校验，乱序会挂全量导表）
  5. 原子写入(tmp+os.replace) + utf-8 无 BOM + 保留原换行

★ 补引用要以 `Tools/table_exporter/ExportTable.py` 的 depend_checks 为准，**不能靠扫表头的"引用表"行**
  —— 有的引用列表头是空的（实例：ActvFlashSale.AssistRewardIds），只有 def schema 知道。
  做法＝跑导表 → 按它报的缺口补 → 再跑，直到 EXIT=0（限时抢购迭代了 3 轮）。
"""

import csv
import io
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO = r'C:/x3/gdconfig'
SRC_REV = '806d9640'   # 撤除前最后一个好版本
HDR = 5                # row0-4 元数据, row5=字段名, 数据从 row6 起

PRICE_FIX = {'211105': '107', '211106': '111', '211107': '116', '211108': '115'}
PACK_IDS = [str(i) for i in range(211101, 211109)]

# (路径, 选行用的列名, 目标值集合, 额外唯一性校验列名)
TARGETS = [
    ('tsv/Pack__Pack.tsv',             'ID',       PACK_IDS,     None),
    ('tsv/Reward__Reward.tsv',         'RewardID', PACK_IDS,     'ID'),
    ('tsv/Item__Item.tsv',             'ID',       ['1214', '1215'], None),
    ('tsv/ActvOnline__ActvOnline.tsv', 'ID',       ['101029'],   None),
    # ActvFlashSale 主表声明的奖励组：ShareRewardId=8202101 / AssistRewardIds=8202102|03|04。
    # ⚠️ 客户端已砍分享/助力，但**配置表仍声明这些字段、服务端代码也还在** ⇒ 导表的
    #    depend_checks 会校验它们存在（实测 exit1: "Reward, depend_keys: {8202101..04} not existed"）。
    #    ⚠️ 注意 AssistRewardIds 那列 row2「引用表」是空的，靠扫 row2 找引用会漏掉它，
    #       只有 def schema 知道 ⇒ 判"引用是否补齐"必须以本地 ExportTable.py 为准，别靠扫表头。
    ('tsv/Reward__Reward.tsv',         'RewardID',
     ['8202101', '8202102', '8202103', '8202104'], 'ID'),
    # AO 101029 的 ActvRule 列指向它（玩法规则弹窗）。MailTemplate 101109 现存不用补。
    ('tsv/RuleTips__RuleTips.tsv',     'ID',       ['40003'],    None),
]

NEW_FILES = [
    'tsv/ActvFlashSale__ActvFlashSale.tsv',
    'tsv/ActvFlashSale__ActvFlashSalePack.tsv',
    'tsv/ActvFlashSale__ActvFlashSaleReward.tsv',
]


def git_show(rev, path):
    r = subprocess.run(['git', 'show', '%s:%s' % (rev, path)], cwd=REPO, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def parse(raw):
    text = raw.decode('utf-8', errors='replace')
    nl = '\r\n' if '\r\n' in text[:4096] else '\n'
    return list(csv.reader(io.StringIO(text), delimiter='\t')), nl


def main():
    go = '--go' in sys.argv
    problems, plan = [], []

    for path, keycol, ids, uniqcol in TARGETS:
        full = os.path.join(REPO, path)
        src_raw = git_show(SRC_REV, path)
        if src_raw is None:
            problems.append('%s: 源版本取不到' % path)
            continue
        with open(full, 'rb') as f:
            cur_raw = f.read()
        if cur_raw[:3] == b'\xef\xbb\xbf':
            problems.append('%s: 当前文件带 BOM' % path)
            continue

        src_rows, _ = parse(src_raw)
        cur_rows, nl = parse(cur_raw)
        sn, cn = src_rows[HDR], cur_rows[HDR]

        # 闸门：源里有、现在没有的字段 = 语义变了，不能盲搬
        dropped = [n for n in sn if n and n not in cn]
        if dropped:
            problems.append('%s: 源字段在当前 schema 已消失 %s' % (path, dropped))
            continue
        if keycol not in cn:
            problems.append('%s: 找不到选行列 %s' % (path, keycol))
            continue

        skey, ckey = sn.index(keycol), cn.index(keycol)
        want = set(ids)
        picked_src = [r for r in src_rows[HDR + 1:] if len(r) > skey and r[skey].strip() in want]
        if not picked_src:
            problems.append('%s: 源里找不到目标行' % path)
            continue

        # 已存在的 id 直接跳过（幂等重跑：本脚本分两轮补引用，第二轮不该被第一轮的成果挡住）
        have = {r[ckey].strip() for r in cur_rows[HDR + 1:] if len(r) > ckey}
        skipped = sorted(want & have)
        if skipped:
            print('  (跳过已存在) %s %s=%s' % (path, keycol, skipped))
            want -= have
            if not want:
                continue
            picked_src = [r for r in picked_src if r[skey].strip() in want]

        # 按字段名映射到当前列序（新增字段留空）
        new_rows_out, novalue = [], set()
        for r in picked_src:
            vals = {sn[i]: r[i] for i in range(min(len(sn), len(r))) if sn[i]}
            out = []
            for nm in cn:
                if nm and nm in vals:
                    out.append(vals[nm])
                else:
                    if nm:
                        novalue.add(nm)
                    out.append('')
            new_rows_out.append(out)

        # 额外唯一性校验（Reward.ID）
        if uniqcol:
            ui_c, ui_s = cn.index(uniqcol), sn.index(uniqcol)
            cur_uniq = {r[ui_c].strip() for r in cur_rows[HDR + 1:] if len(r) > ui_c}
            clash = [r[ui_s].strip() for r in picked_src if r[ui_s].strip() in cur_uniq]
            if clash:
                problems.append('%s: %s 撞号 %s' % (path, uniqcol, clash[:5]))
                continue

        # Price 修复（IAP 本体）
        fixed = 0
        if path.endswith('Pack__Pack.tsv'):
            pi, ii = cn.index('Price'), cn.index('ID')
            for out in new_rows_out:
                if out[ii].strip() in PRICE_FIX:
                    out[pi] = PRICE_FIX[out[ii].strip()]
                    fixed += 1

        # 按 id 数值插入有序位置
        sort_i = cn.index(uniqcol) if uniqcol else ckey
        data = list(cur_rows[HDR + 1:])
        for out in sorted(new_rows_out, key=lambda x: int(x[sort_i])):
            rid, pos = int(out[sort_i]), len(data)
            for i, ex in enumerate(data):
                if len(ex) > sort_i and ex[sort_i].strip().isdigit() and int(ex[sort_i]) > rid:
                    pos = i
                    break
            data.insert(pos, out)

        plan.append((path, full, cur_rows[:HDR + 1] + data, nl,
                     len(new_rows_out), fixed, len(cur_rows) - HDR - 1, sorted(novalue)))

    print('=' * 76)
    for path, _, _, nl, n, fixed, before, novalue in plan:
        extra = '  Price补%d' % fixed if fixed else ''
        print('  %-32s +%-3d行  %d→%d%s' % (path, n, before, before + n, extra))
        if novalue:
            print('       新字段留空: %s' % novalue)
    for f in NEW_FILES:
        ex = os.path.exists(os.path.join(REPO, f))
        print('  %-32s %s' % (f, '已存在(跳过)' if ex else 'checkout %s' % SRC_REV))

    if problems:
        print('\n🔴 BLOCK:')
        for p in problems:
            print('   - ' + p)
        return 1
    if not go:
        print('\n(演练。加 --go 落盘)')
        return 0

    for f in NEW_FILES:
        if os.path.exists(os.path.join(REPO, f)):
            continue
        r = subprocess.run(['git', 'checkout', SRC_REV, '--', f], cwd=REPO, capture_output=True)
        print('  checkout %-46s rc=%d' % (f, r.returncode))

    for path, full, rows, nl, _, _, _, _ in plan:
        buf = io.StringIO()
        csv.writer(buf, delimiter='\t', lineterminator=nl,
                   quoting=csv.QUOTE_MINIMAL).writerows(rows)
        tmp = full + '.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='') as fh:
            fh.write(buf.getvalue())
        os.replace(tmp, full)
        with open(full, 'rb') as fh:
            print('  写入 %-32s 无BOM=%s' % (path, fh.read(3) != b'\xef\xbb\xbf'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
