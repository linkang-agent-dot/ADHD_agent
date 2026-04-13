# -*- coding: utf-8 -*-
"""
X2 配置表通用查询工具

解决反复手写 GSheet 查询脚本的问题。内置表号→spreadsheet ID 解析，
支持常用查询模式：表头、ID范围搜索、关键字搜索、列过滤、尾部行等。

用法:
    python gsheet_query.py headers  1118              # 显示1118表的列头（带列号）
    python gsheet_query.py search   2148 复活节        # 全表搜索关键字
    python gsheet_query.py idrange  1111 11112945 11112955  # ID范围查行
    python gsheet_query.py tail     1168 20            # 最后20行
    python gsheet_query.py filter   2148 5 1           # col[5]==1 的行
    python gsheet_query.py row      2148 21482703      # 按ID取单行（带列名）
    python gsheet_query.py tabs     1118               # 列出页签
    python gsheet_query.py resolve  1111               # 只显示 spreadsheet ID

环境:
    GOOGLE_WORKSPACE_PROJECT_ID=calm-repeater-489707-n1
"""

import subprocess, json, os, sys, argparse, shutil, time
from pathlib import Path

# ── 基础配置 ──────────────────────────────────────────────────

GWS_CMD = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
if not os.path.exists(GWS_CMD):
    GWS_CMD = shutil.which('gws') or 'gws'

os.environ.setdefault('GOOGLE_WORKSPACE_PROJECT_ID', 'calm-repeater-489707-n1')

X2_INDEX_SID = '1z2-AK4dFgdzd7U11uCgYzLpj3Qopkv9Rr-SbA7iLIMc'
X2_INDEX_TAB = 'fw_gsheet_config'
CACHE_FILE = Path(__file__).parent / '.table_registry_cache.json'
ALIAS_FILE = Path(__file__).parent / '.gsheet_aliases.json'
CACHE_TTL = 3600 * 24  # 24h

# 内置别名 — P2 项目表（_dev / _P2 后缀）
# 注册表自动解析的是 X2 项目（_x2_ 前缀）。P2 通过此处硬编码。
# 完整 SheetID 参照: config-library/table-index.md
BUILTIN_ALIASES = {
    # ── P2 装饰/道具子系统 ──
    '1111_P2':   '1FQqpeRfkXVwaEDSVi3oTaQNs2PLLDcsvQQmc-k0L3ws',
    '1118_dev':  '1ES3syKlMbqqmZezWFCzwL0elIdrgvisiUTnBwJNRHrk',
    '1168_dev':  '1KwX1xWoHHcmOGTaasZmMii2Al-YR_VXV3yoSGn3tBbA',
    '1511_dev':  '1Zs5l2MPz9nTDSV6VsAZAFsGRxRW0nLsGj2u1lF3PBQY',
    '2148_dev':  '1tI-J-BkIw7-NsoTN1yY-ZXJMW-edn7aK1GLsfVaeiVw',
    '2171_dev':  '1YJW39MBGg7aya62_hkhI1uRmyMknjZQV226Dqsksis4',
    # ── P2 活动/礼包子系统 ──
    '2011_dev':  '1yS_BehT_Rfcc3sXjDPsSaQRcjPh8YepucYTnUQDpEMc',
    '2013_dev':  '1sJzacpa0CBp1B8LQX1TboSBOA4T80_t8lH8eEzqHLbY',
    '2112_dev':  '1IKUBw678b2PU1m0md1vR9GxcH2uTNyLbR7VWgyAJ57E',
    '2115_dev':  '1K3-I4gCYKY-Zw5Ms05ozHtHKpOqYI-lp4kuuhqbWajY',
    '2135_dev':  '1KrcIA8jC4Aj6sFz44c_2lhtJ-lyD1OYu3QNpzaor8Mc',
}

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')


# ── GWS 底层调用 ─────────────────────────────────────────────

def gws_values(sid: str, rng: str) -> list:
    """读取 sheet 数据，返回二维数组"""
    params = json.dumps({'spreadsheetId': sid, 'range': rng})
    r = subprocess.run(
        [GWS_CMD, 'sheets', 'spreadsheets', 'values', 'get', '--params', params],
        capture_output=True, text=True, encoding='utf-8',
    )
    if r.returncode != 0:
        print(f"[gws error] {r.stderr or r.stdout}", file=sys.stderr)
        return []
    try:
        return json.loads(r.stdout).get('values', [])
    except json.JSONDecodeError:
        print(f"[parse error] {r.stdout[:200]}", file=sys.stderr)
        return []


def gws_sheet_meta(sid: str) -> dict:
    """获取 spreadsheet 元信息（标题 + 页签列表）"""
    params = json.dumps({
        'spreadsheetId': sid,
        'fields': 'properties.title,sheets.properties',
    })
    r = subprocess.run(
        [GWS_CMD, 'sheets', 'spreadsheets', 'get', '--params', params],
        capture_output=True, text=True, encoding='utf-8',
    )
    try:
        return json.loads(r.stdout)
    except:
        return {}


# ── 表号注册表 ────────────────────────────────────────────────

def _load_registry_from_gsheet() -> dict:
    """从 fw_gsheet_config 加载完整注册表"""
    rows = gws_values(X2_INDEX_SID, f'{X2_INDEX_TAB}!A:G')
    registry = {}
    for row in rows[1:]:  # skip header
        if len(row) >= 4:
            table_name = str(row[1]).strip()
            short_name = str(row[2]).strip()
            sid = str(row[3]).strip()
            if sid and len(sid) > 10:
                registry[table_name] = {
                    'category': str(row[0]).strip(),
                    'table_name': table_name,
                    'short_name': short_name,
                    'spreadsheet_id': sid,
                }
                if short_name:
                    registry[short_name] = registry[table_name]
    return registry


def load_registry(force_refresh=False) -> dict:
    """加载注册表（带本地缓存）"""
    if not force_refresh and CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding='utf-8'))
            if time.time() - cache.get('ts', 0) < CACHE_TTL:
                return cache['data']
        except:
            pass

    print("[info] Loading table registry from GSheet...", file=sys.stderr)
    data = _load_registry_from_gsheet()

    try:
        CACHE_FILE.write_text(json.dumps({
            'ts': time.time(),
            'data': data,
        }, ensure_ascii=False, indent=2), encoding='utf-8')
    except:
        pass

    return data


def _load_aliases() -> dict:
    """加载本地别名（内置 + 用户自定义）"""
    aliases = dict(BUILTIN_ALIASES)
    if ALIAS_FILE.exists():
        try:
            user_aliases = json.loads(ALIAS_FILE.read_text(encoding='utf-8'))
            aliases.update(user_aliases)
        except:
            pass
    return aliases


def resolve_table(table_key: str, registry: dict = None) -> tuple:
    """
    将表号/名称解析为 (spreadsheet_id, main_tab_name)。
    查找优先级：别名 > 注册表精确匹配 > 注册表模糊匹配 > 原样(长字符串)。
    支持: "1168_dev", "2148_dev", "1111", "1111_P2", "x2_item" 等。
    返回 (sid, tab) —— tab 可能为 None（需要自动探测）。
    """
    # 1. 别名优先
    aliases = _load_aliases()
    if table_key in aliases:
        return aliases[table_key], None

    # 2. 注册表
    if registry is None:
        registry = load_registry()

    if table_key in registry:
        entry = registry[table_key]
        return entry['spreadsheet_id'], None

    # 3. 模糊匹配：数字前缀
    key_lower = table_key.lower().replace('_', '')
    for name, entry in registry.items():
        name_clean = name.lower().replace('_', '')
        if key_lower in name_clean or name_clean.startswith(key_lower):
            return entry['spreadsheet_id'], None

    # 4. 如果输入看起来像 spreadsheet ID（长字符串），直接用
    if len(table_key) > 20:
        return table_key, None

    return None, None


def detect_main_tab(sid: str) -> str:
    """自动检测主页签（优先无后缀的、第一个非隐藏的）"""
    meta = gws_sheet_meta(sid)
    sheets = meta.get('sheets', [])
    if not sheets:
        return 'Sheet1'

    visible = [s['properties'] for s in sheets
               if not s['properties'].get('hidden', False)]
    if not visible:
        visible = [s['properties'] for s in sheets]

    # 优先选不含 "备份"/"副本"/"工作表" 的
    for p in visible:
        title = p['title']
        if not any(k in title for k in ['备份', '副本', '工作表', 'Copy', 'Sheet']):
            return title

    return visible[0]['title']


# ── 输出格式化 ────────────────────────────────────────────────

def fmt_row(row: list, indexed=False) -> str:
    if indexed:
        return '\t'.join(f'[{i}]{c}' for i, c in enumerate(row))
    return '\t'.join(str(c) for c in row)


def print_rows(rows: list, header: list = None, indexed=False, row_nums=True):
    if header:
        print(f"HEADER: {fmt_row(header, indexed=True)}")
    for i, row in rows:
        prefix = f"row {i}: " if row_nums else ""
        print(f"{prefix}{fmt_row(row, indexed)}")


# ── 查询命令 ──────────────────────────────────────────────────

def cmd_headers(sid, tab, args):
    """显示列头（带列号索引）"""
    rows = gws_values(sid, f"'{tab}'!1:1")
    if rows:
        for i, col in enumerate(rows[0]):
            print(f"  [{i}] {col}")
    else:
        print("(no header row found)")


def cmd_search(sid, tab, args):
    """全表搜索关键字"""
    keyword = args.keyword.lower()
    max_col = args.cols or 'AZ'
    rows = gws_values(sid, f"'{tab}'!A:{max_col}")
    header = rows[0] if rows else []
    matches = []
    for i, row in enumerate(rows):
        if i == 0:
            continue
        row_str = '\t'.join(str(c) for c in row).lower()
        if keyword in row_str:
            matches.append((i, row))

    print(f"Found {len(matches)} rows matching '{args.keyword}'")
    print_rows(matches, header=header, indexed=args.indexed)


def cmd_idrange(sid, tab, args):
    """按 ID 范围查找行（col A 默认，可指定 --id-col）"""
    id_col = args.id_col
    min_id, max_id = int(args.min_id), int(args.max_id)
    max_col = args.cols or 'AZ'
    rows = gws_values(sid, f"'{tab}'!A:{max_col}")
    header = rows[0] if rows else []
    matches = []
    for i, row in enumerate(rows):
        if i == 0:
            continue
        try:
            val = int(str(row[id_col]).strip())
            if min_id <= val <= max_id:
                matches.append((i, row))
        except (ValueError, IndexError):
            pass

    print(f"Found {len(matches)} rows with col[{id_col}] in [{min_id}, {max_id}]")
    print_rows(matches, header=header, indexed=args.indexed)


def cmd_tail(sid, tab, args):
    """显示最后 N 行"""
    n = int(args.n) if args.n else 15
    max_col = args.cols or 'AZ'
    rows = gws_values(sid, f"'{tab}'!A:{max_col}")
    header = rows[0] if rows else []
    data = [(i, row) for i, row in enumerate(rows) if i > 0 and len(row) > 0]
    tail = data[-n:]
    print(f"Last {len(tail)} rows (of {len(data)} total)")
    print_rows(tail, header=header, indexed=args.indexed)


def cmd_filter(sid, tab, args):
    """按列值过滤: col[idx] == value 或 col[idx] != value"""
    col_idx = int(args.col_idx)
    value = args.value
    negate = args.negate
    max_col = args.cols or 'AZ'
    rows = gws_values(sid, f"'{tab}'!A:{max_col}")
    header = rows[0] if rows else []
    matches = []
    for i, row in enumerate(rows):
        if i == 0:
            continue
        try:
            cell = str(row[col_idx]).strip()
        except IndexError:
            cell = ''
        hit = (cell == value) if not negate else (cell != value and cell != '')
        if hit:
            matches.append((i, row))

    op = '!=' if negate else '=='
    print(f"Found {len(matches)} rows with col[{col_idx}] {op} '{value}'")
    print_rows(matches, header=header, indexed=args.indexed)


def cmd_row(sid, tab, args):
    """按 ID 取单行并显示带列名的字段"""
    target_id = args.target_id
    id_col = args.id_col
    max_col = args.cols or 'AZ'
    rows = gws_values(sid, f"'{tab}'!A:{max_col}")
    header = rows[0] if rows else []
    for i, row in enumerate(rows):
        if i == 0:
            continue
        try:
            val = str(row[id_col]).strip()
            if val == target_id:
                print(f"row {i}:")
                for j, cell in enumerate(row):
                    col_name = header[j] if j < len(header) else f'col{j}'
                    print(f"  [{j}] {col_name} = {cell}")
                return
        except IndexError:
            pass
    print(f"ID '{target_id}' not found in col[{id_col}]")


def cmd_tabs(sid, tab, args):
    """列出所有页签"""
    meta = gws_sheet_meta(sid)
    sheets = meta.get('sheets', [])
    title = meta.get('properties', {}).get('title', '?')
    print(f"Spreadsheet: {title}")
    print(f"Tabs ({len(sheets)}):")
    for s in sheets:
        p = s['properties']
        hidden = ' [hidden]' if p.get('hidden', False) else ''
        current = ' ← (selected)' if p['title'] == tab else ''
        print(f"  {p['sheetId']:>12}  {p['title']}{hidden}{current}")


def cmd_resolve(sid, tab, args):
    """显示解析结果"""
    print(f"spreadsheet_id: {sid}")
    print(f"tab: {tab}")


def cmd_list(args):
    """列出注册表中所有表"""
    registry = load_registry(force_refresh=args.refresh)
    seen = set()
    entries = []
    for name, entry in registry.items():
        sid = entry['spreadsheet_id']
        if sid in seen:
            continue
        seen.add(sid)
        entries.append(entry)

    entries.sort(key=lambda e: e['table_name'])
    print(f"Total: {len(entries)} tables")
    for e in entries:
        print(f"  {e['table_name']:30s}  {e['short_name']:20s}  {e['spreadsheet_id'][:20]}...")

    # 也列出别名
    aliases = _load_aliases()
    if aliases:
        print(f"\nAliases ({len(aliases)}):")
        for name, sid in sorted(aliases.items()):
            print(f"  {name:20s}  {sid[:30]}...")


def cmd_alias(args):
    """管理本地别名"""
    if args.alias_action == 'list':
        aliases = _load_aliases()
        for name, sid in sorted(aliases.items()):
            builtin = ' (builtin)' if name in BUILTIN_ALIASES else ''
            print(f"  {name:20s}  {sid}{builtin}")
    elif args.alias_action == 'set':
        user_aliases = {}
        if ALIAS_FILE.exists():
            try:
                user_aliases = json.loads(ALIAS_FILE.read_text(encoding='utf-8'))
            except:
                pass
        user_aliases[args.alias_name] = args.alias_sid
        ALIAS_FILE.write_text(json.dumps(user_aliases, indent=2), encoding='utf-8')
        print(f"Alias set: {args.alias_name} → {args.alias_sid}")
    elif args.alias_action == 'rm':
        user_aliases = {}
        if ALIAS_FILE.exists():
            try:
                user_aliases = json.loads(ALIAS_FILE.read_text(encoding='utf-8'))
            except:
                pass
        if args.alias_name in user_aliases:
            del user_aliases[args.alias_name]
            ALIAS_FILE.write_text(json.dumps(user_aliases, indent=2), encoding='utf-8')
            print(f"Alias removed: {args.alias_name}")
        else:
            print(f"Alias '{args.alias_name}' not found (builtin aliases cannot be removed)")


# ── CLI 入口 ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='X2 配置表通用查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s headers  1118
  %(prog)s search   2148 复活节
  %(prog)s idrange  1111_P2 11112945 11112955
  %(prog)s tail     1168 20
  %(prog)s filter   2148 5 1          # col[5]==1
  %(prog)s filter   2148 5 0 --not    # col[5]!=0
  %(prog)s row      2148 21482703
  %(prog)s tabs     1118
  %(prog)s list
  %(prog)s list --refresh
        """,
    )

    sub = parser.add_subparsers(dest='command')

    # -- list (no table arg)
    p_list = sub.add_parser('list', help='列出所有注册表')
    p_list.add_argument('--refresh', action='store_true', help='强制刷新缓存')

    # -- alias
    p_alias = sub.add_parser('alias', help='管理本地别名')
    alias_sub = p_alias.add_subparsers(dest='alias_action')
    alias_sub.add_parser('list', help='列出所有别名')
    p_set = alias_sub.add_parser('set', help='设置别名')
    p_set.add_argument('alias_name', help='别名')
    p_set.add_argument('alias_sid', help='spreadsheet ID')
    p_rm = alias_sub.add_parser('rm', help='删除别名')
    p_rm.add_argument('alias_name', help='别名')

    # -- 需要 table 参数的命令
    for name, help_text in [
        ('headers', '显示列头'),
        ('tabs', '列出页签'),
        ('resolve', '解析表号→ID'),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument('table', help='表号/表名/spreadsheet ID')
        p.add_argument('--tab', help='指定页签名（默认自动检测）')

    # -- search
    p = sub.add_parser('search', help='全表搜索关键字')
    p.add_argument('table', help='表号')
    p.add_argument('keyword', help='搜索关键字')
    p.add_argument('--tab', help='指定页签名')
    p.add_argument('--indexed', action='store_true', help='输出带列号索引')
    p.add_argument('--cols', help='列范围（默认AZ）', default=None)

    # -- idrange
    p = sub.add_parser('idrange', help='按 ID 范围查找')
    p.add_argument('table', help='表号')
    p.add_argument('min_id', help='最小 ID')
    p.add_argument('max_id', help='最大 ID')
    p.add_argument('--id-col', type=int, default=0, help='ID 所在列号（默认0）')
    p.add_argument('--tab', help='指定页签名')
    p.add_argument('--indexed', action='store_true', help='输出带列号索引')
    p.add_argument('--cols', help='列范围', default=None)

    # -- tail
    p = sub.add_parser('tail', help='显示最后 N 行')
    p.add_argument('table', help='表号')
    p.add_argument('n', nargs='?', default='15', help='行数（默认15）')
    p.add_argument('--tab', help='指定页签名')
    p.add_argument('--indexed', action='store_true', help='输出带列号索引')
    p.add_argument('--cols', help='列范围', default=None)

    # -- filter
    p = sub.add_parser('filter', help='按列值过滤')
    p.add_argument('table', help='表号')
    p.add_argument('col_idx', help='列号')
    p.add_argument('value', help='匹配值')
    p.add_argument('--not', dest='negate', action='store_true', help='取反（!=）')
    p.add_argument('--tab', help='指定页签名')
    p.add_argument('--indexed', action='store_true', help='输出带列号索引')
    p.add_argument('--cols', help='列范围', default=None)

    # -- row
    p = sub.add_parser('row', help='按 ID 取单行（带列名）')
    p.add_argument('table', help='表号')
    p.add_argument('target_id', help='目标 ID')
    p.add_argument('--id-col', type=int, default=0, help='ID 所在列号（默认0）')
    p.add_argument('--tab', help='指定页签名')
    p.add_argument('--cols', help='列范围', default=None)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # list / alias 不需要 table 解析
    if args.command == 'list':
        cmd_list(args)
        return
    if args.command == 'alias':
        if not args.alias_action:
            cmd_alias(type('Args', (), {'alias_action': 'list'})())
        else:
            cmd_alias(args)
        return

    # 解析 table → spreadsheet ID + tab
    sid, _ = resolve_table(args.table)
    if not sid:
        print(f"[error] Cannot resolve table '{args.table}'. Use 'list' to see available tables.",
              file=sys.stderr)
        sys.exit(1)

    tab = getattr(args, 'tab', None)
    if not tab:
        tab = detect_main_tab(sid)
    print(f"[info] Table: {args.table} → {sid[:20]}... / '{tab}'", file=sys.stderr)

    # P2 表自动检测：如果 col[0] 是 p2_title，自动将 id_col 偏移+1
    if hasattr(args, 'id_col'):
        header_rows = gws_values(sid, f"'{tab}'!A1:A1")
        if header_rows and header_rows[0] and str(header_rows[0][0]).strip() == 'p2_title':
            if args.id_col == 0:
                args.id_col = 1
                print(f"[info] P2 table detected, auto-shifted --id-col to 1", file=sys.stderr)

    dispatch = {
        'headers': cmd_headers,
        'search': cmd_search,
        'idrange': cmd_idrange,
        'tail': cmd_tail,
        'filter': cmd_filter,
        'row': cmd_row,
        'tabs': cmd_tabs,
        'resolve': cmd_resolve,
    }

    dispatch[args.command](sid, tab, args)


if __name__ == '__main__':
    main()
