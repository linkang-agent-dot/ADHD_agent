# -*- coding: utf-8 -*-
"""刷新国服永恒赛季名单，并把新增球员并入评价体系数据源。

职责：
1. 从 fifaaddict 国服接口刷新 el_list.json；
2. 抓取新增永恒球员的完整属性，写入 el_tm_attrs_full.json / el_stats.json；
3. 若新增永恒球员原本位于 tm_only_attrs.json，则迁入同名 TM 对照并移出时刻独有池。

只补新增记录，不覆盖已有球员的历史快照。
"""
import http.cookiejar
import json
import os
import sys
import time
import urllib.request
import uuid

sys.stdout.reconfigure(encoding="utf-8")
SP = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"


def atomic_json(path, value):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)


def new_session():
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    def get(url, headers=None):
        merged = {
            "User-Agent": UA,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://cn.fifaaddict.com/fo4db",
        }
        if headers:
            merged.update(headers)
        req = urllib.request.Request(url, headers=merged)
        return opener.open(req, timeout=30).read().decode("utf-8")

    token = get("https://cn.fifaaddict.com/api2?rq=araiwa&t=" + uuid.uuid4().hex).strip()
    return get, token


def fetch_list(season):
    get, token = new_session()
    url = "https://cn.fifaaddict.com/api2?q=fo4db&class=%s&sv=cn&locale=cn" % season
    return json.loads(get(url, {"X-ARAIWA": token}))


def fetch_player(uid):
    get, token = new_session()
    url = "https://cn.fifaaddict.com/api2?fo4pid=pid%s&locale=cn" % uid
    return json.loads(get(url, {"X-ARAIWA": token}))


def compact_player(result):
    db = result["db"]
    return {
        "attr": result["attr"],
        "ovr": db["pos1val"],
        "salary": db["salary"],
        "weight": db["weight"],
        "height": db["height"],
        "traits": list((result.get("traits") or {}).keys()),
        "pos1": db["pos1"],
    }


def main():
    el_path = os.path.join(SP, "el_list.json")
    full_path = os.path.join(SP, "el_tm_attrs_full.json")
    stats_path = os.path.join(SP, "el_stats.json")
    tm_only_path = os.path.join(SP, "tm_only_attrs.json")

    live_el = fetch_list("el")
    full = json.load(open(full_path, encoding="utf-8"))
    stats = json.load(open(stats_path, encoding="utf-8"))
    tm_only = json.load(open(tm_only_path, encoding="utf-8"))

    added = []
    promoted = []
    for player in live_el["db"]:
        name, uid = player["name"], player["uid"]
        record = full.setdefault(name, {})
        if name in tm_only and "TM" not in record:
            record["TM"] = tm_only.pop(name)
            promoted.append(name)
        if "EL" in record and uid in stats:
            continue

        result = fetch_player(uid)
        record["EL"] = compact_player(result)
        stats[uid] = {
            "player": result["db"],
            "traits": result.get("traits"),
            "price": result.get("price"),
        }
        added.append(name)
        time.sleep(1.5)

    atomic_json(el_path, live_el)
    atomic_json(full_path, full)
    atomic_json(stats_path, stats)
    atomic_json(tm_only_path, tm_only)
    print("EL count:", len(live_el["db"]))
    print("Added EL:", ", ".join(added) if added else "none")
    print("Promoted TM comparisons:", ", ".join(promoted) if promoted else "none")
    print("TM-only count:", len(tm_only))


if __name__ == "__main__":
    main()
