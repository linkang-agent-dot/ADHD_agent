# -*- coding: utf-8 -*-
"""Pack__Pack.tsv 主数据栏体检（2026-07-06 沉淀，来源：深海节 Pack 主数据修正案）。

扫 4 类问题（判据与当次人工扫描一致）：
  1. name_txtkey   — c35 Name 填了 TXT_ 原始 key（应填中文真名，真名可从 tsv/i18n/Text__Text.tsv 反查）
  2. name_space    — c35 首尾空格 / 纯空格 / 空（表头铁律：必填禁空格）
  3. price_missing — 有 Price 档位(c7)但美元标注列 c6(列5) 空 → 可按 PackPrice 映射确定性补
  4. price_mismatch— c6 与 Price 档位 USD 不一致（注意：航海 207202-211 疑似权重列、BUYALL 疑似营销原价，
                     历史上属"待确认不动"，见 memory project_x3_deepsea_festival）

用法：python pack_masterdata_scan.py [--repo C:\\x3\\gdconfig]
输出各类问题行清单；修复用 tsv_edit.py set（--old 断言），别手写 csv.writer 回写。
"""
import argparse, csv, sys

USD = {'101':'0.99','102':'1.99','103':'2.99','104':'3.99','105':'4.99','106':'7.99',
       '107':'9.99','108':'12.99','109':'14.99','110':'17.99','111':'19.99','112':'29.99',
       '113':'39.99','114':'59.99','115':'99.99','116':'49.99'}

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=r'C:\x3\gdconfig')
    a = ap.parse_args()
    path = a.repo + r'\tsv\Pack__Pack.tsv'
    rows = list(csv.reader(open(path, encoding='utf-8', newline=''), delimiter='\t'))
    buckets = {'name_txtkey': [], 'name_space': [], 'price_missing': [], 'price_mismatch': []}
    for r in rows[6:]:
        if not r or not r[0].strip():
            continue
        pid = r[0].strip()
        rmk = (r[2] if len(r) > 2 else '').strip()
        p5 = (r[6] if len(r) > 6 else '').strip()
        pr = (r[7] if len(r) > 7 else '').strip()
        name = r[35] if len(r) > 35 else ''
        if name.startswith('TXT_'):
            buckets['name_txtkey'].append((pid, rmk, name))
        if name != name.strip() or (name == '' or name.strip() == ''):
            buckets['name_space'].append((pid, rmk, repr(name)))
        if pr in USD and not p5:
            buckets['price_missing'].append((pid, rmk, name, USD[pr]))
        elif pr in USD and p5 not in ('', '0') and p5 != USD[pr]:
            buckets['price_mismatch'].append((pid, rmk, p5, pr, USD[pr]))
    total = 0
    for k, v in buckets.items():
        print(f'== {k}: {len(v)}')
        total += len(v)
        for row in v:
            print('  ', row)
    print('TOTAL_ISSUES', total)
    return 0 if total == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
