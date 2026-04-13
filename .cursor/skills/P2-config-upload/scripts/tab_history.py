"""
tab_history.py — 记录每次下载的页签名，检测页签名变化

用法：
  python tab_history.py check  <table_id> <tab_name>   # 检测是否变化
  python tab_history.py update <table_id> <tab_name>   # 记录新页签名
  python tab_history.py show                            # 查看全部历史

check 返回：
  exit 0  → 无变化或首次记录（安全）
  exit 1  → 页签名变化，stdout 输出警告信息
"""

import sys
import json
import os

# 页签历史仅作本机 Cursor/导表辅助，必须落在仓库外，避免 `git add .` 误提交进 gdconfig/x2gdconf。
def _default_history_file() -> str:
    override = os.environ.get("P2_TAB_HISTORY_FILE", "").strip()
    if override:
        return os.path.normpath(override)
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        d = os.path.join(base, "P2GSheetTabHistory")
    else:
        base = os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state")
        d = os.path.join(base, "p2_gsheet_tab_history")
    return os.path.normpath(os.path.join(d, "tab_history.json"))


HISTORY_FILE = _default_history_file()


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(data):
    parent = os.path.dirname(HISTORY_FILE)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cmd_check(table_id, new_tab):
    history = load_history()
    old_tab = history.get(table_id)
    if old_tab is None:
        print(f"[tab_history] First record: {table_id} -> {new_tab}")
        return 0
    if old_tab == new_tab:
        return 0
    print(f"[tab_history] [WARN] Tab name changed! Table {table_id}: prev={old_tab}, now={new_tab}")
    return 1


def cmd_update(table_id, new_tab):
    history = load_history()
    old_tab = history.get(table_id)
    history[table_id] = new_tab
    save_history(history)
    if old_tab and old_tab != new_tab:
        print(f"[tab_history] Updated {table_id}: {old_tab} -> {new_tab}")
    else:
        print(f"[tab_history] Recorded {table_id} -> {new_tab}")


def cmd_show():
    history = load_history()
    if not history:
        print("[tab_history] No history records found")
        return
    print(f"[tab_history] {len(history)} records:")
    for tid, tab in sorted(history.items()):
        print(f"  {tid:>8} -> {tab}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]
    if cmd == "check" and len(args) == 3:
        sys.exit(cmd_check(args[1], args[2]))
    elif cmd == "update" and len(args) == 3:
        cmd_update(args[1], args[2])
    elif cmd == "show":
        cmd_show()
    else:
        print(f"用法错误: {args}")
        sys.exit(2)
