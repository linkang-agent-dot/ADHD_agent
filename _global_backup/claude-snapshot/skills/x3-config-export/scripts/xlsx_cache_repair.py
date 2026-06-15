# -*- coding: utf-8 -*-
"""
xlsx_cache_repair.py — Excel/WPS COM 改 xlsx 后的浮点缓存串修复（zip 手术，不用 openpyxl）

背景（2026-06-12 HeroSkin 104001 实测）：
- gdconfig 的 xlsx 千万别用 openpyxl / sync_xlsx_tsv.py --from-tsv 写：会丢全簿公式缓存值，
  gate 再 xlsx->tsv 自动同步时把空值灌进 tsv 公式列（HeroSkill Id 列整列清空级别事故）。
- 安全姿势 = Excel COM(手动计算+CalculateBeforeSave=False) 改 xlsx，但保存仍会把少量
  浮点缓存串"规范化"(17位->15位 shortest repr)，checker 按字符串比对会报 mismatch。
- 本脚本：遍历指定 sheet xml 的 <c r="X"><v>num</v>，与同坐标 tsv 串比对，
  数值相等但字符串不同的，把 xlsx 串替换回 tsv 串。其余 zip member 原样写回。

用法:
  python xlsx_cache_repair.py <xlsx路径> <sheetN.xml=tsv路径> [<sheetM.xml=tsv路径> ...]
  例: python xlsx_cache_repair.py data/Hero.xlsx \
        sheet4.xml=tsv/Hero__HeroAttributes.tsv sheet15.xml="tsv/Hero__#经验计算.tsv"
  (sheet 名->xml 映射看 xl/workbook.xml + xl/_rels/workbook.xml.rels)

修完后跑: python scripts/sync_xlsx_tsv.py --check --files data/<表>.xlsx 直到 mismatch=0
"""
import io, sys, zipfile, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def col_to_idx(col):
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n


def repair(xlsx_path, jobs):
    """jobs: {'xl/worksheets/sheet4.xml': 'tsv/Hero__HeroAttributes.tsv', ...}"""
    zin = zipfile.ZipFile(xlsx_path)
    buf = io.BytesIO()
    zout = zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED)
    total = 0
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename in jobs:
            tsv = [l.split('\t') for l in
                   open(jobs[item.filename], encoding='utf-8').read().split('\n')]
            t = data.decode('utf-8')
            cnt = [0]

            def fix(m):
                ref, val = m.group(1), m.group(2)
                cm = re.match(r'([A-Z]+)(\d+)', ref)
                r, c = int(cm.group(2)), col_to_idx(cm.group(1))
                try:
                    tv = tsv[r - 1][c - 1]   # checker 行号 = tsv 行号 = xlsx 行号
                except IndexError:
                    return m.group(0)
                if tv != val:
                    try:
                        fv, ft = float(val), float(tv)
                        if fv == ft or abs(ft - fv) < 1e-9 * max(1, abs(fv)):
                            cnt[0] += 1
                            return m.group(0).replace('<v>%s</v>' % val, '<v>%s</v>' % tv)
                    except ValueError:
                        pass
                return m.group(0)

            # <f .../> 自闭合(共享公式)与 <f>...</f> 两种都要覆盖
            t = re.sub(r'<c r="([A-Z]+\d+)"[^>]*?>(?:<f[^>]*/>|<f[^>]*>.*?</f>)?'
                       r'<v>(-?\d+\.?\d*(?:[eE][+-]?\d+)?)</v></c>', fix, t)
            data = t.encode('utf-8')
            print('%s: patched %d cells' % (item.filename, cnt[0]))
            total += cnt[0]
        zout.writestr(item, data)
    zout.close()
    zin.close()
    open(xlsx_path, 'wb').write(buf.getvalue())
    print('total patched:', total)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    xlsx = sys.argv[1]
    jobs = {}
    for arg in sys.argv[2:]:
        xml, tsv = arg.split('=', 1)
        if not xml.startswith('xl/'):
            xml = 'xl/worksheets/' + xml
        jobs[xml] = tsv
    repair(xlsx, jobs)
