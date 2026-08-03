#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
X2 导出文案 → X3 Text__Text.tsv 落表

配套：`x2x3_asset_port.py`（资产搬运）。X2 的 Editor 工具 `Tools ▸ X2 ▸ Prefab Asset Export`
勾「导出 TFWText 本地化 TSV」会产出 `localization_keys.tsv`（key + 17 语），本工具把它落进 X3。

用法：
  # 1. 体检：算出「已存在 / 待录」，并查 X2 译文的空缺与英文泄漏
  python x2_i18n_to_x3.py check --src D:\newX2\localization_keys_MERGED.tsv --tag 限时抢购

  # 2. 落表（默认预演，--go 才写盘；⚠️先 git branch --show-current 确认分支）
  python x2_i18n_to_x3.py land --src ... --tag 限时抢购 --go

━━━━━━━━━━━━ 2026-08-03 限时抢购实战踩到的坑，全在下面 ━━━━━━━━━━━━

【1】X3 Text 表接受 `lc_*` / `LC_*` key，不强制 `TXT_*`
     实证：表里本就有 `lc_ui_guaranteed` / `lc_ui_tap_blank_close` / `LC_MENU_congratulations_cap`。
     ⇒ **X2 搬来的 key 原名直接录，不用改 prefab**（改 prefab 才是真风险）。
     备注列照抄已有迁移标注格式：`<模块>迁移-X2;X2:<原key>`。

【2】键值列是 `|` 分隔的多 key 行（27269 行里 4299 行是多 key，展开 65782 个 key）
     判「key 是否已存在」必须 split('|')，否则会重复录。

【3】⛔ 千万别用 `utf-8-sig` 写回无 BOM 的文件
     X3 的 Text__Text.tsv **无 BOM**。用 `io.open(..., encoding='utf-8-sig')` 写会加上 BOM，
     首行表头被 git 判为「删一行加一行」，污染 diff。读用 utf-8-sig 无所谓（会剥 BOM），写必须 utf-8。
     校验：`head -c 3 <file> | xxd -p` 应为 `6f7074`（"opt"），不是 `efbbbf`。

【4】⛔ 官方 `i18n_leak_audit.py` 在这个场景有两个盲区，**必须自己再按行审一遍**
     a) `--changed` 在增删行后会打印
        `[scope] ⚠️ 行数与HEAD不一致(发生过增删行),无法精确定位改动→退回全表审计`
        → 报出几百条全表历史问题（`Text_ErrCode*` 那类内部文案本就不翻），淹没你的改动。
     b) `--grep <主题词>` 圈不到「key 里不含主题词」的行。实测限时抢购 30 条里有 5 条
        （`lc_ui_get_now_cap` / `LC_IAP_scene_limit` / `LC_IAP_vip_super_sale` / 两条 `box_botton`）
        逃过 `--grep flashsale`，而**真泄漏恰好就在其中一条**。
     ⇒ 本工具的 `check` 直接对「本次要落的这批行」做同形/空缺/中文泄漏检查，不依赖 grep 圈范围。

【5】⛔ 别默认 X2 的译文是干净的——它自己就带泄漏
     实测 `LC_IAP_vip_super_sale` 的 sp/fr/id/de/zh/ru/po/tr/th **9 列照抄英文 `SUPER SALE`**；
     `LC_IAP_flashsale_value_promotion` 的 cn/zh 是英文 `VALUE PROMOTION`（其余 14 语都译了）。
     搬 X2 译文 = 把 X2 的泄漏一起搬过来。落表前必须过本工具的泄漏检查。

【6】X2 / X3 术语可能冲突，游戏专名要按 X3 改写
     实测「商会」：X2 用 Syndicate 系（Sindicato/Syndikat/신디케이트/Синдикат/シンジケート），
     X3 用 Company 系（参照 `TXT_ActvOnline_ActvName_103701` 商会征召令）。
     ⇒ 落表前列出文案里的游戏专名，逐个在 X3 表里查现行译法。

【7】语言覆盖：X2 给 15 语，X3 要 16 语，只差 **ua（乌克兰语）**
     X2 列：en cn ar de fr jp kr po ru sp th tr zh vi id it pl（多出 ar/vi，X3 不用）
     X3 列：cn en sp fr id de kr zh ru **ua** jp it pl po tr th
     ⇒ 只需补 ua 一种；按 X3 现有术语翻（宝箱=Скриня / 大奖=головний приз / 分享=Поділитися）。

【8】⚠️ X2 的 localization tsv 表头里 `id` 出现两次
     第 0 列是 key 的 `id`，第 15 列才是印尼语 `id`。`header.index('id')` 会取到 key 列。
     **必须按位置取列**，本工具已按位置写死并带自检断言。

【9】直写 tsv 的新 key 不要再跑 CompositeI18n 扫描（skill 陷阱 6）
     扫描会把这些行标回「新增」，已填译文下一轮被当待翻项重翻。走「场景 A：直接改语言列」。
"""
import csv, io, os, re, sys, json, shutil, argparse

X3TSV_DEFAULT = r'C:\x3\gdconfig\tsv\i18n\Text__Text.tsv'
X3_LANGS = ['cn', 'en', 'sp', 'fr', 'id', 'de', 'kr', 'zh', 'ru', 'ua', 'jp', 'it', 'pl', 'po', 'tr', 'th']
# 坑【8】X2 按位置取列（表头 'id' 出现两次）
X2_POS = {'key': 0, 'en': 1, 'cn': 2, 'ar': 3, 'de': 4, 'fr': 5, 'jp': 6, 'kr': 7,
          'po': 8, 'ru': 9, 'sp': 10, 'th': 11, 'tr': 12, 'zh': 13, 'vi': 14,
          'id': 15, 'it': 16, 'pl': 17}
CJK = re.compile(r'[\u4e00-\u9fff]')
KEY_PREFIX = ('TXT_', 'Text_', 'LC_', 'lc_')   # 坑【2】+ skill 陷阱 7：LC_/lc_ 必须认


def load_logical(path):
    """逻辑行重组：只有以 key 前缀开头的物理行才算新行（表里有裸换行 cell）"""
    raw = io.open(path, encoding='utf-8-sig', newline='').read().split('\n')
    out, buf = [], None
    for ln in raw:
        if ln.startswith(KEY_PREFIX) or buf is None:
            if buf is not None:
                out.append(buf)
            buf = ln
        else:
            buf += '\n' + ln
    if buf is not None:
        out.append(buf)
    return out


def read_x2(path):
    with io.open(path, encoding='utf-8-sig', newline='') as fh:
        rows = list(csv.reader(fh, delimiter='\t'))
    hdr = rows[0]
    for n, p in X2_POS.items():
        if n == 'key':
            continue
        assert p < len(hdr) and hdr[p].lower() == n, \
            'X2 列位置对不上：%s 应在第 %d 列，实为 %r（坑【8】）' % (n, p, hdr[p] if p < len(hdr) else None)
    out = {}
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        out[r[0].strip()] = {n: (r[X2_POS[n]].strip() if X2_POS[n] < len(r) else '')
                             for n in X2_POS if n != 'key'}
    return out


def x3_existing_keys(path):
    ks = set()
    for l in load_logical(path):
        k = l.split('\t')[0]
        if k.startswith(KEY_PREFIX):
            ks.update(x.strip() for x in k.split('|') if x.strip())
    return ks


def audit(rows):
    """对「本次要落的这批行」直接审 —— 不依赖 grep 圈范围（坑【4】）"""
    bad = []
    for k, v in rows.items():
        en = (v.get('en') or '').strip()
        if en and not re.fullmatch(r'[\W\d_]+', en):
            same = [c for c in X3_LANGS if c != 'en' and (v.get(c) or '').strip() == en]
            if same:
                bad.append(('EN_LEAK', k, 'en=%s 同形列=%s' % (en[:40], same)))
        for c in X3_LANGS:
            val = (v.get(c) or '').strip()
            if not val:
                bad.append(('EMPTY', k, c))
            elif c not in ('cn', 'zh', 'jp') and CJK.search(val):
                bad.append(('CJK_LEAK', k, '%s=%s' % (c, val[:40])))
    return bad


def build(src, x3tsv, ua_map=None, overrides=None):
    x2 = read_x2(src)
    have = x3_existing_keys(x3tsv)
    todo = {k: v for k, v in x2.items() if k not in have}
    rows = {}
    for k, v in todo.items():
        d = {c: v.get(c, '') for c in X3_LANGS}
        d['ua'] = (ua_map or {}).get(k, '')          # 坑【7】X2 无 ua
        if overrides and k in overrides:              # 坑【6】术语改写
            d.update(overrides[k])
        rows[k] = d
    return rows, sorted(set(x2) & have)


def emit(lines, out_path):
    io.open(out_path, 'w', encoding='utf-8').write('\n'.join(lines))
    print('-> %s' % out_path)


def cmd_check(a):
    rows, exist = build(a.src, a.x3tsv,
                        ua_map=json.load(io.open(a.ua, encoding='utf-8')) if a.ua else None)
    L = ['=== X2→X3 文案体检 ===',
         'X2 条目 %d；X3 已存在 %d；待录 %d' % (len(rows) + len(exist), len(exist), len(rows)),
         '已存在: %s' % ', '.join(exist), '']
    bad = audit(rows)
    if bad:
        L.append('=== ❌ %d 条问题（落表前必须修，坑【4】【5】）===' % len(bad))
        for t, k, d in bad:
            L.append('  %-9s %-42s %s' % (t, k, d))
    else:
        L.append('=== ✅ 无 EN_LEAK / CJK_LEAK / EMPTY ===')
    emit(L, a.log)


def cmd_land(a):
    ua = json.load(io.open(a.ua, encoding='utf-8')) if a.ua else None
    ov = json.load(io.open(a.overrides, encoding='utf-8')) if a.overrides else None
    rows, exist = build(a.src, a.x3tsv, ua_map=ua, overrides=ov)
    bad = audit(rows)
    if bad and not a.force:
        emit(['%-9s %-42s %s' % b for b in bad], a.log)
        sys.exit('❌ %d 条泄漏/空缺，拒绝落表（看 %s；确认无误可加 --force）' % (len(bad), a.log))

    hdr = next(csv.reader(io.open(a.x3tsv, encoding='utf-8-sig', newline=''), delimiter='\t'))
    CI = {c: hdr.index(c) for c in X3_LANGS}
    raw = io.open(a.x3tsv, encoding='utf-8-sig', newline='').read()
    nl = '\r\n' if '\r\n' in raw[:5000] else '\n'
    new = []
    for k in sorted(rows):
        cells = [''] * len(hdr)
        cells[0], cells[1] = k, 'AI'
        cells[2] = '%s迁移-X2;X2:%s' % (a.tag, k)     # 坑【1】沿用已有迁移标注格式
        for c in X3_LANGS:
            cells[CI[c]] = rows[k][c]
        for x in cells:
            assert '\t' not in x and '\n' not in x and '\r' not in x, '含 tab/真换行: %s' % k
        new.append('\t'.join(cells))

    print('待录 %d 行（已存在 %d 条跳过）' % (len(new), len(exist)))
    if not a.go:
        emit(new, a.log)
        print('DRY RUN（加 --go 写盘）')
        return
    shutil.copy2(a.x3tsv, a.x3tsv + '.bak')
    tmp = a.x3tsv + '.tmp'
    # 坑【3】写必须 utf-8（不带 sig），否则给无 BOM 的表加 BOM 污染首行
    with io.open(tmp, 'w', encoding='utf-8', newline='') as fh:
        fh.write(raw.rstrip('\r\n') + nl + nl.join(new) + nl)
    os.replace(tmp, a.x3tsv)                          # 原子写入
    print('已写入（备份 %s.bak）' % a.x3tsv)
    print('自检：head -c 3 应为 6f7074 而非 efbbbf；git diff 应是纯新增 0 删除')


def main():
    ap = argparse.ArgumentParser(description='X2 导出文案 → X3 Text__Text.tsv')
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name, fn in (('check', cmd_check), ('land', cmd_land)):
        p = sub.add_parser(name)
        p.add_argument('--src', required=True, help='X2 的 localization_keys.tsv')
        p.add_argument('--x3tsv', default=X3TSV_DEFAULT)
        p.add_argument('--tag', default='X2搬运', help='备注列前缀，如「限时抢购」')
        p.add_argument('--ua', help='ua 译文 JSON: {key: "乌克兰语"}')
        p.add_argument('--overrides', help='术语改写 JSON: {key: {lang: text}}（坑【6】）')
        p.add_argument('--log', default='i18n_land.txt')
        if name == 'land':
            p.add_argument('--go', action='store_true')
            p.add_argument('--force', action='store_true', help='有泄漏也硬落（不建议）')
        p.set_defaults(func=fn)
    a = ap.parse_args()
    a.func(a)


if __name__ == '__main__':
    main()
