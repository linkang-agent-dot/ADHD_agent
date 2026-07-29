"""
扫描节日换皮/玩法返工后残留的旧名文案。

背景：X3 节日多为整节日克隆（马戏节←深海节），克隆后活动备注、道具描述、
获取说明等下游文案常仍写着**上一个节日的名字**或**改版前的玩法名**。
内部备注只误导策划，但 TXT_ 开头的 i18n 是**玩家可见**的——玩家会照着去找一个不存在的活动。

用法：
  python scan_festival_stale_names.py <gdconfig路径> --festival 马戏 --stale 深海 转盘 世界杯 夏日

输出分两栏：🔴玩家可见(i18n TXT_) / 🟡内部备注，前者优先修。
"""
import argparse, csv, glob, os, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def load_rows(path):
    try:
        return list(csv.reader(open(path, encoding='utf-8', errors='replace'), delimiter='\t'))
    except Exception:
        return []


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', help='gdconfig 根目录')
    p.add_argument('--festival', default='马戏', help='当前节日关键词（用于圈定相关行）')
    p.add_argument('--stale', nargs='+', default=['深海', '转盘', '世界杯', '夏日', '尼罗'],
                   help='要找的旧名关键词')
    p.add_argument('--ids', nargs='*', default=[],
                   help='额外的相关 ID（活动/道具），命中这些 ID 的行也纳入检查')
    a = p.parse_args()

    tsv_dir = os.path.join(a.root, 'tsv')
    i18n_dir = os.path.join(tsv_dir, 'i18n')

    visible, internal = [], []

    # ---- ① i18n：玩家可见 ----
    for f in glob.glob(os.path.join(i18n_dir, '*.tsv')):
        rows = load_rows(f)
        for r in rows[5:]:
            if not r or not r[0].startswith('TXT_'):
                continue
            key = r[0]
            # 文案列（cn=col3, en=col4）
            cn = r[3] if len(r) > 3 else ''
            en = r[4] if len(r) > 4 else ''
            body = cn + ' ' + en
            hit = [s for s in a.stale if s in body]
            if not hit:
                continue
            # 只报与当前节日相关的：key 含相关 ID，或文案里同时出现当前节日词
            related = a.festival in body or any(i in key for i in a.ids)
            visible.append((os.path.basename(f), key, cn[:40], en[:50], ','.join(hit), related))

    # ---- ② 配置表备注列 ----
    for f in sorted(glob.glob(os.path.join(tsv_dir, '*.tsv'))):
        rows = load_rows(f)
        if len(rows) < 6:
            continue
        hdr = rows[4] if len(rows) > 4 else []
        for r in rows[5:]:
            for i, v in enumerate(r):
                if not isinstance(v, str) or not v.strip():
                    continue
                if i < len(hdr) and hdr[i].startswith('TXT_'):
                    continue  # i18n 源文，上面已覆盖
                hit = [s for s in a.stale if s in v]
                if hit and a.festival in ''.join(r[:6]):
                    internal.append((os.path.basename(f), r[0], hdr[i] if i < len(hdr) else f'col{i}',
                                     v[:50], ','.join(hit)))
                    break

    print(f'旧名关键词: {a.stale}   当前节日: {a.festival}')
    print('=' * 90)
    print(f'\n🔴 玩家可见（i18n TXT_）：{len(visible)} 条')
    for fn, k, cn, en, h, rel in visible[:40]:
        mark = '★相关' if rel else '  '
        print(f'  {mark} [{h}] {k}')
        print(f'         cn: {cn}')
        if en:
            print(f'         en: {en}')
    if len(visible) > 40:
        print(f'  … 还有 {len(visible)-40} 条')

    print(f'\n🟡 内部备注：{len(internal)} 条')
    for fn, rid, col, v, h in internal[:40]:
        print(f'   [{h}] {fn:38s} id={rid:10s} {col}= {v}')
    if len(internal) > 40:
        print(f'  … 还有 {len(internal)-40} 条')


if __name__ == '__main__':
    main()
