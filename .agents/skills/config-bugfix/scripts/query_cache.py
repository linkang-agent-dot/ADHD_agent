# query_cache.py - Query local config cache
# Usage:
#   python query_cache.py --list                   # List cached tables
#   python query_cache.py --index                  # List ALL tables from index (even uncached)
#   python query_cache.py --index 2182             # Show index info for a table
#   python query_cache.py 1111 11112175            # Exact ID lookup (col[0] or col[1])
#   python query_cache.py 1111 --search keyword    # Fuzzy search all columns
#   python query_cache.py 1111 --col 2 keyword     # Search specific column
#   python query_cache.py --search-all keyword     # Cross-table global search (all cached tables)
import json, sys, os

CACHE_DIR = "C:/Users/linkang/_config_cache"

def load_table(table_id):
    path = os.path.join(CACHE_DIR, f"{table_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_index():
    path = os.path.join(CACHE_DIR, "_index.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def print_row(header, row, row_num):
    print(f"=== Row {row_num} ===")
    for j, val in enumerate(row):
        if val:
            col_name = header[j] if j < len(header) else f"col{j}"
            print(f"  {col_name}: {val}")
    print()

def main():
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding="utf-8")

    args = sys.argv[1:]

    if not args or args[0] == "--list":
        manifest_path = os.path.join(CACHE_DIR, "_manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                m = json.load(f)
            print(f"Last refresh: {m['cached_at']}")
            print(f"Index: {m.get('index_total','?')} tables | Cached: {m['cached_total']} tables\n")
            for tid, info in sorted(m["tables"].items()):
                print(f"  {tid} ({info['name']}): {info['rows']} rows [{info['cached_at']}]")
        else:
            print("No cache. Run refresh_cache.py first.")
        return

    if args[0] == "--index":
        index = load_index()
        if not index:
            print("No index. Run refresh_cache.py first.")
            return
        if len(args) >= 2:
            tid = args[1]
            if tid in index:
                info = index[tid]
                print(f"{tid}: {info['description']}")
                print(f"  sheet_id: {info['sheet_id']}")
                print(f"  name: {info['name']}")
                cached = os.path.exists(os.path.join(CACHE_DIR, f"{tid}.json"))
                print(f"  cached: {'yes' if cached else 'no'}")
            else:
                # Fuzzy search index
                kw = tid.lower()
                for k, v in sorted(index.items()):
                    if kw in k or kw in v["description"].lower() or kw in v["name"].lower():
                        cached = "C" if os.path.exists(os.path.join(CACHE_DIR, f"{k}.json")) else " "
                        print(f"  [{cached}] {k}: {v['description'][:60]}")
        else:
            for tid, info in sorted(index.items()):
                cached = "C" if os.path.exists(os.path.join(CACHE_DIR, f"{tid}.json")) else " "
                print(f"  [{cached}] {tid}: {info['name']}")
        return

    table_id = args[0]
    data = load_table(table_id)

    if data is None:
        index = load_index()
        if index and table_id in index:
            print(f"{table_id} not cached but found in index: {index[table_id]['description']}")
            print(f"Run: python refresh_cache.py {table_id}")
        else:
            print(f"{table_id} not found in cache or index.")
        return

    header = data["header"]

    if len(args) >= 3 and args[1] == "--search":
        keyword = args[2].lower()
        count = 0
        for i, row in enumerate(data["rows"], start=2):
            text = " ".join(str(c) for c in row).lower()
            if keyword in text:
                print_row(header, row, i)
                count += 1
                if count >= 20:
                    print(f"... (first 20 shown)")
                    break
        print(f"Found {count} matches" if count else f"No match for '{keyword}'")

    elif len(args) >= 4 and args[1] == "--col":
        col_idx = int(args[2])
        keyword = args[3].lower()
        count = 0
        for i, row in enumerate(data["rows"], start=2):
            if len(row) > col_idx and keyword in str(row[col_idx]).lower():
                print_row(header, row, i)
                count += 1
                if count >= 20:
                    break
        print(f"Found {count} matches")

    elif len(args) >= 2:
        target_id = args[1]
        found = False
        for i, row in enumerate(data["rows"], start=2):
            if row and (str(row[0]) == target_id or (len(row) > 1 and str(row[1]) == target_id)):
                print_row(header, row, i)
                found = True
        if not found:
            print(f"ID {target_id} not found in {table_id}")
    else:
        print(f"{table_id} ({data['name']}): {data['total_rows']} rows, cached {data['cached_at']}")
        print(f"Header: {header}")

if __name__ == "__main__":
    main()
