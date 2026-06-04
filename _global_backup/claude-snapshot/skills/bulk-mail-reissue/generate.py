"""
Bulk mail reissue — generate iGame batch-send-mail import CSV from an arbitrary source CSV.

Usage:
    python generate.py <source_csv> [--output <path>] [--map server=col,user=col,asset=col,amount=col]
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

# Column name aliases (case-insensitive)
ALIASES = {
    "server": ["server_id", "sid", "server", "serverid", "srv", "srv_id"],
    "user":   ["user_id", "uid", "userid", "player_id", "playerid", "role_id", "roleid"],
    "asset":  ["asset_id", "item_id", "itemid", "assetid", "id", "prop_id", "propid"],
    "amount": ["change_count", "amount", "count", "cnt", "qty", "quantity", "num"],
    # optional
    "asset_type": ["asset_type", "assettype", "type"],
}

OUTPUT_HEADER = ['服务器 ID', '玩家 ID', '玩家信息', '标题信息', '附件资产信息', '自定义']


def detect_encoding(path: Path) -> str:
    """Try utf-8-sig, utf-8, gbk in order."""
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            with open(path, "r", encoding=enc) as f:
                f.read()
            return enc
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Cannot decode {path} with utf-8-sig/utf-8/gbk")


def resolve_column(header: list[str], role: str, overrides: dict) -> str | None:
    """Find the column name in header that matches given role."""
    if role in overrides:
        return overrides[role]
    lower_map = {c.lower().strip(): c for c in header}
    for alias in ALIASES.get(role, []):
        if alias in lower_map:
            return lower_map[alias]
    return None


def parse_map_arg(s: str) -> dict:
    """Parse --map server=col1,user=col2,asset=col3,amount=col4."""
    out = {}
    if not s:
        return out
    for pair in s.split(","):
        k, _, v = pair.partition("=")
        out[k.strip()] = v.strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="Source CSV path")
    ap.add_argument("--output", help="Output CSV path (default: <source>_import.csv)")
    ap.add_argument("--map", default="", help="Column mapping overrides, e.g. server=sid,user=uid,asset=item,amount=cnt")
    ap.add_argument("--asset-type", default="item", help="Default assetType value (default: item)")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.exists():
        print(f"ERROR: source not found: {src}", file=sys.stderr)
        sys.exit(1)

    dst = Path(args.output) if args.output else src.with_name(src.stem + "_import.csv")
    overrides = parse_map_arg(args.map)

    enc = detect_encoding(src)
    with open(src, "r", encoding=enc) as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []

        col_server = resolve_column(header, "server", overrides)
        col_user   = resolve_column(header, "user",   overrides)
        col_asset  = resolve_column(header, "asset",  overrides)
        col_amount = resolve_column(header, "amount", overrides)
        col_type   = resolve_column(header, "asset_type", overrides)

        missing = [role for role, col in [("server", col_server), ("user", col_user),
                                           ("asset", col_asset), ("amount", col_amount)] if col is None]
        if missing:
            print(f"ERROR: cannot auto-detect columns: {missing}", file=sys.stderr)
            print(f"Source columns: {header}", file=sys.stderr)
            print(f"Re-run with --map, e.g. --map server=<col>,user=<col>,asset=<col>,amount=<col>", file=sys.stderr)
            sys.exit(2)

        rows = list(reader)

    # Write output: GBK + comma-delimited + CSV-quoted JSON
    count = 0
    sum_by_asset = defaultdict(int)
    with open(dst, "w", encoding="gbk", newline="") as fout:
        writer = csv.writer(fout, delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar='"')
        writer.writerow(OUTPUT_HEADER)
        for row in rows:
            atype = (row.get(col_type) if col_type else None) or args.asset_type
            aid = int(row[col_asset])
            amt = int(row[col_amount])
            items = [{"assetType": atype, "id": aid, "amount": amt}]
            j = json.dumps(items, ensure_ascii=False, separators=(",", ":"))
            writer.writerow([row[col_server], row[col_user], "", "", "", j])
            sum_by_asset[aid] += amt
            count += 1

    # Self-check
    src_sum = defaultdict(int)
    for row in rows:
        src_sum[int(row[col_asset])] += int(row[col_amount])
    sum_ok = src_sum == sum_by_asset

    print(f"Source encoding : {enc}")
    print(f"Column mapping  : server={col_server}, user={col_user}, asset={col_asset}, amount={col_amount}"
          + (f", asset_type={col_type}" if col_type else ""))
    print(f"Output          : {dst}")
    print(f"Rows            : {count}")
    print(f"Sum by asset_id :")
    for aid in sorted(sum_by_asset):
        print(f"  {aid}: {sum_by_asset[aid]} (src={src_sum[aid]}, match={src_sum[aid]==sum_by_asset[aid]})")
    print(f"Self-check      : {'OK' if sum_ok and count == len(rows) else 'FAIL'}")


if __name__ == "__main__":
    main()
