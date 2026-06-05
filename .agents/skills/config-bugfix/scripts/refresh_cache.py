# refresh_cache.py - Download config tables to local cache
# Usage:
#   python refresh_cache.py              # Download frequently used tables
#   python refresh_cache.py --all        # Download all tables from index
#   python refresh_cache.py 1111 2182    # Download specific tables by ID
#   python refresh_cache.py --index-only # Only refresh the index
import subprocess, json, sys, os, time

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding="utf-8")

CACHE_DIR = "C:/Users/linkang/_config_cache"
INDEX_SHEET_ID = "1wYJQoPcdmlw4HcjmR2QP41WP4Gb4k8Rd7iCJJX7H_8c"
INDEX_TAB = "fw_gsheet_config"

# Frequently used tables - always cached
FREQUENT = {"1111", "2111", "2112", "2115", "2121", "2154", "2182"}

os.makedirs(CACHE_DIR, exist_ok=True)

def get_sheets_api():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8", shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    creds = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=creds).spreadsheets()

def refresh_index(sheets_api):
    """Download fw_gsheet_config index and build table_id -> {name, sheet_id, tab} mapping."""
    print("[index] Downloading fw_gsheet_config...", end=" ", flush=True)
    r = sheets_api.values().get(
        spreadsheetId=INDEX_SHEET_ID,
        range=f"'{INDEX_TAB}'!A1:F600"
    ).execute()
    rows = r.get("values", [])

    # Parse: col0=category, col1=description (contains table_id), col2=tab_name, col3=sheet_id
    index = {}
    for row in rows[1:]:
        if len(row) < 4:
            continue
        desc = row[1]  # e.g. "2112_activity_config - ..."
        tab = row[2]   # e.g. "activity_config"
        sheet_id = row[3]

        # Extract table_id from description (first part before _)
        parts = desc.split("_", 1)
        table_id = parts[0].strip()
        if not table_id.isdigit():
            continue

        name = tab
        index[table_id] = {
            "name": name,
            "sheet_id": sheet_id,
            "description": desc,
        }

    # Save index
    index_path = os.path.join(CACHE_DIR, "_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"{len(index)} tables indexed")
    return index

def find_qa_tab(sheets_api, sheet_id):
    sp = sheets_api.get(spreadsheetId=sheet_id, fields="sheets.properties").execute()
    tabs = [s["properties"]["title"] for s in sp["sheets"]]
    # Prefer QA tab
    for t in tabs:
        if "QA" in t.upper() and "qa" in t.lower():
            return t
    for t in tabs:
        if "QA" in t:
            return t
    return tabs[0]

def download_table(sheets_api, table_id, info):
    sheet_id = info["sheet_id"]
    name = info["name"]

    # Find the right tab
    try:
        tab = find_qa_tab(sheets_api, sheet_id)
    except Exception:
        tab = name

    print(f"  {table_id} ({name}) tab={tab}...", end=" ", flush=True)
    start = time.time()

    try:
        r = sheets_api.values().get(
            spreadsheetId=sheet_id,
            range=f"'{tab}'!A:Z"
        ).execute()
        rows = r.get("values", [])
        header = rows[0] if rows else []

        data = {
            "table_id": table_id,
            "name": name,
            "tab": tab,
            "sheet_id": sheet_id,
            "header": header,
            "total_rows": len(rows) - 1,
            "rows": rows[1:],
            "cached_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        out_path = os.path.join(CACHE_DIR, f"{table_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        elapsed = time.time() - start
        print(f"{len(rows)-1} rows, {elapsed:.1f}s")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def main():
    args = sys.argv[1:]
    sheets_api = get_sheets_api()

    # Always refresh index first
    index = refresh_index(sheets_api)

    if args == ["--index-only"]:
        return

    # Determine which tables to download
    if args == ["--all"]:
        targets = set(index.keys())
        print(f"\nDownloading ALL {len(targets)} tables...")
    elif args:
        targets = set(args)
        print(f"\nDownloading {len(targets)} specified tables...")
    else:
        targets = FREQUENT
        print(f"\nDownloading {len(targets)} frequently used tables...")

    success = 0
    for tid in sorted(targets):
        if tid.startswith("-"):
            continue
        if tid not in index:
            print(f"  {tid}: not found in index, skipping")
            continue
        if download_table(sheets_api, tid, index[tid]):
            success += 1

    # Write manifest
    cached_tables = {}
    for f in os.listdir(CACHE_DIR):
        if f.endswith(".json") and not f.startswith("_"):
            tid = f.replace(".json", "")
            try:
                with open(os.path.join(CACHE_DIR, f), "r", encoding="utf-8") as fp:
                    d = json.load(fp)
            except (json.JSONDecodeError, OSError):
                continue
            # tolerate legacy / single-table cache files that lack some keys
            cached_tables[tid] = {
                "name": d.get("name", d.get("tab", tid)),
                "rows": d.get("total_rows", len(d.get("rows", []))),
                "cached_at": d.get("cached_at", ""),
            }

    manifest = {
        "cached_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "index_total": len(index),
        "cached_total": len(cached_tables),
        "tables": cached_tables,
    }
    with open(os.path.join(CACHE_DIR, "_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {success} tables cached at {CACHE_DIR}")
    print(f"Index: {len(index)} tables | Cached: {len(cached_tables)} tables")

if __name__ == "__main__":
    main()
