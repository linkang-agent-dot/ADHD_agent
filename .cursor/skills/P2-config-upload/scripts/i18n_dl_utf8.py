#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n_dl_utf8.py — UTF-8 友好的 1011/i18n 下载脚本
用 gws（Sheets API v4）替代 GSheetDownloader.exe，解决 Windows GBK 无法写 ar.tsv 的问题。

用法：
    python i18n_dl_utf8.py

注意：P2-config-upload Skill 对表 1011 有**临时禁令**——Agent 不得用本脚本输出做 git 提交/推送；
本脚本仅供负责人在本机手动跑表使用。
"""

import subprocess, json, os, sys
from pathlib import Path

GWS         = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
SHEET_ID    = '11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY'
I18N_DIR    = Path(r'C:\gdconfig\fo\i18n')

# 与 GSheetDownloader 一致的 tab 处理顺序
I18N_TABS = [
    'RSS', 'RESEARCH', 'MENU', 'NPC', 'ASSET', 'MAP', 'BUFF', 'MAIL',
    'SOLDIER', 'ERRCODE', 'ITEM', 'BUILDING', 'HORDE', 'TIP', 'UNION',
    'PLAYER', 'STORY', 'LEADERBOARD', 'FTE', 'QUEST', 'TRIGGER', 'NEWS',
    'PUSH', 'IAP', 'SOCIAL', 'ART', 'EVENT', 'CHINA', 'HERO', 'SATELLITE',
    'METRO', 'SITUATION', 'minigame', 'ARENA', 'KVK',
]

os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')


CHUNK_SIZE = 1000   # rows per API call — keep small to avoid gws timeout


def _gws_fetch(range_str, max_retries=3):
    """单次 gws +read，带重试。返回 values list。"""
    import time
    last_err = None
    for attempt in range(1, max_retries + 1):
        r = subprocess.run(
            [GWS, 'sheets', '+read', '--spreadsheet', SHEET_ID, '--range', range_str],
            capture_output=True, text=True, encoding='utf-8',
        )
        if r.returncode == 0:
            try:
                return json.loads(r.stdout).get('values', [])
            except Exception as e:
                last_err = f'JSON parse error: {e}'
        else:
            last_err = r.stderr[:200] or '(no stderr)'
        if attempt < max_retries:
            time.sleep(2 ** attempt)
    raise RuntimeError(f'{range_str}: {last_err}')


def gws_read(tab_name, chunk_size=CHUNK_SIZE):
    """通过 gws 下载指定 tab 的全部行（分块 {chunk_size} 行，避免超时）。"""
    headers = _gws_fetch(f'{tab_name}!1:1')
    if not headers:
        return []
    header_row = headers[0]

    all_rows = [header_row]
    row_start = 2
    while True:
        row_end   = row_start + chunk_size - 1
        chunk     = _gws_fetch(f'{tab_name}!{row_start}:{row_end}')
        if not chunk:
            break
        all_rows.extend(chunk)
        if len(chunk) < chunk_size:
            break
        row_start += chunk_size

    return all_rows


def i18n_record(dict_i18n, keys, lang, index_int, key, value):
    if lang not in keys:
        keys[lang] = {}
    if lang not in dict_i18n:
        dict_i18n[lang] = {}
    d         = dict_i18n[lang]
    idx_keys  = keys[lang]
    line      = value + '\t' + str(index_int)
    if key in d and idx_keys.get(key) != index_int:
        d.setdefault('duplicate_keys', []).append(key)
    else:
        d[key]        = line
        idx_keys[key] = index_int


def i18n_process(dict_i18n, keys, tab_name, rows):
    if not rows:
        print(f'  [SKIP] {tab_name}: empty response')
        return
    headers   = rows[0]
    lang_cnt  = len(headers)
    if lang_cnt < 3:
        print(f'  [SKIP] {tab_name}: too few columns ({lang_cnt})')
        return
    print(f'  {tab_name}: {len(rows)-1} rows, {lang_cnt} cols', flush=True)
    for row in rows[1:]:
        if not row or row[0] == '':
            continue
        # 不够宽的行补空
        while len(row) < lang_cnt:
            row.append('')
        index_int = row[0]
        id_str    = row[1]
        for l in range(2, lang_cnt):
            if not headers[l]:
                break
            i18n_record(dict_i18n, keys, headers[l], index_int,
                        f'{tab_name}_{id_str}', row[l])


def i18n_save(dict_i18n):
    I18N_DIR.mkdir(parents=True, exist_ok=True)
    saved, skipped = 0, 0
    for lang, lang_data in sorted(dict_i18n.items()):
        # 跳过非语言列（保险起见）
        if lang in ('ID_int', 'ID', ''):
            continue
        if 'duplicate_keys' in lang_data:
            dupes = lang_data['duplicate_keys'][:5]
            print(f'  [WARN] {lang}: {len(lang_data["duplicate_keys"])} duplicate keys, e.g. {dupes}')
            skipped += 1
            continue
        path = I18N_DIR / f'{lang}.tsv'
        rows = sorted(lang_data.items())        # 按 id 字母排序
        # newline='' disables any line-ending translation; we write \r\n explicitly
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write('id\tvalue\tindex_int\r\n')
            for key, val in rows:
                # strip embedded real newlines — gws API may return them in multi-line cells;
                # existing TSV format keeps \n as 2-char game escape sequences on a single line
                key_clean = key.replace('\r', '').replace('\n', '\\n')
                val_clean = val.replace('\r', '').replace('\n', '\\n')
                f.write(f'{key_clean}\t{val_clean}\r\n')
        saved += 1
    print(f'\n写入完成：{saved} 个语言文件 → {I18N_DIR}')
    if skipped:
        print(f'（{skipped} 个语言因 duplicate_keys 跳过，请手动排查）')
    return saved


def main():
    print('=== i18n_dl_utf8.py: 下载 1011/i18n ===')
    dict_i18n, keys = {}, {}
    tab_ok, tab_fail = 0, 0

    for tab in I18N_TABS:
        try:
            print(f'[↓] {tab} ...', end=' ', flush=True)
            rows = gws_read(tab)
            i18n_process(dict_i18n, keys, tab, rows)
            tab_ok += 1
        except Exception as e:
            print(f'\n  [ERROR] {tab}: {e}')
            tab_fail += 1

    print(f'\nTab 下载完成：成功 {tab_ok}，失败 {tab_fail}')
    print('=== 写入 fo/i18n/ ===')
    saved = i18n_save(dict_i18n)

    # 结果汇总
    print(f'\n==============================')
    print(f'成功: {saved} 个语言文件，Tab 失败: {tab_fail}')
    print(f'==============================')
    return 0 if saved > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
