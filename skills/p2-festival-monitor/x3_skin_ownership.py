# -*- coding: utf-8 -*-
"""X3 英雄皮肤全量清单 × 获取率（获取率 = 皮肤获取人数 / 该英雄解锁人数）。

口径（坑都在 [[reference_x3_datain_asset_query]]）：
  - 皮肤拥有 = `asset_id='Item_<皮肤道具id>' AND change_type='1'`（曾获得即拥有，外显永久）
  - 英雄解锁 = `asset_id='Item_50xxx'`，**别用 Hero_10xx**（dim_asset 里有但流水全零＝假资产形态）
    规律：Item_(50000 + heroId - 1000)，如霍普金斯 heroId=1034 → Item_50034
  - asset_id 必须带 `Item_` 前缀，change_type 必须是字符串 '1'

用法：
  python x3_skin_ownership.py                 # 默认成熟服 1000-1880
  python x3_skin_ownership.py --all-servers   # 全服
产出：同目录 x3_skin_ownership.json + 控制台表格
"""
import sys, os, json, csv, io, subprocess, argparse
sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from query_trino import execute_sql

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = r"C:\X3\wt_circus_float"      # 任一 gdconfig worktree，只读 git show
BRANCH = "origin/dev_festival"


def tsv(rel):
    d = subprocess.check_output(["git", "show", f"{BRANCH}:{rel}"], cwd=REPO).decode("utf-8", errors="replace")
    return list(csv.reader(io.StringIO(d), delimiter="\t"))


def load_i18n():
    """Text__Text.tsv：key 有 col0/col2 两种排布，且多 key 用 | 合并（见 i18n_lookup.py）"""
    rows = tsv("tsv/i18n/Text__Text.tsv")
    m = {}
    for r in rows[4:]:
        if len(r) < 4:
            continue
        for k in set(r[0].split("|")) | set(r[2].split("|")):
            if k.startswith("TXT_HeroSkin_Name_") or k.startswith("TXT_Hero_Name_"):
                m.setdefault(k, r[3])
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all-servers", action="store_true")
    a = ap.parse_args()
    seg = "" if a.all_servers else " AND TRY_CAST(server_id AS INTEGER) BETWEEN 1000 AND 1880"
    seg_name = "全服" if a.all_servers else "成熟服 1000-1880"

    hs = tsv("tsv/Hero__HeroSkin.tsv")
    i18n = load_i18n()

    skins = []
    for r in hs[4:]:
        if len(r) < 19 or not r[0].isdigit():
            continue
        sid, hero, item = r[0], r[3], r[11]
        if not item.isdigit():
            continue
        skins.append({
            "skin_id": sid, "hero_id": hero, "item_id": item,
            "name": i18n.get(f"TXT_HeroSkin_Name_{sid}", ""),
            "tag": r[18].strip(),
            "prop": r[12], "prop_num": r[13],
            "has_video": bool(r[20].strip()) if len(r) > 20 else False,
        })

    # 🔴 一个英雄有多个资产形态：本体 Item_500XX + 晋升 Item_500XXn（史诗/传奇…）
    # 只查本体会让分母偏小甚至为 0（实测斯隆本体 0 人、克里斯塔尔仅 2 人 → 获取率算出 500%/210700%）
    # 正确口径 = 该英雄名下**所有形态**去重人数，用 dim_asset 反查全集
    heroes = sorted({s["hero_id"] for s in skins if s["hero_id"].isdigit()})
    dim = execute_sql("SELECT asset_id, asset_name FROM v1090.dim_asset "
                      "WHERE asset_id LIKE 'Item_50%' AND asset_name LIKE '英雄-%'",
                      datasource="TRINO_HF")["data"]
    hero_assets = {}
    for h in heroes:
        base = f"Item_{50000 + int(h) - 1000}"
        forms = [d["asset_id"] for d in dim if d["asset_id"].startswith(base)]
        hero_assets[h] = forms or [base]

    def owners(asset_ids):
        out = {}
        for i in range(0, len(asset_ids), 120):
            chunk = asset_ids[i:i + 120]
            lst = ",".join(f"'{x}'" for x in chunk)
            sql = (f"SELECT asset_id, count(distinct user_id) o FROM v1090.ods_user_asset "
                   f"WHERE asset_id IN ({lst}) AND change_type='1'{seg} GROUP BY 1")
            for row in execute_sql(sql, datasource="TRINO_HF")["data"]:
                out[row["asset_id"]] = int(row["o"])
        return out

    def hero_owner_counts(mapping):
        """按英雄合并各形态 → 去重人数（各形态人数不能相加，会重复计人）。

        ⚠️ 逐英雄发一条 SQL 会跑到超时（31 个英雄 × 数十秒）。
        这里一条 SQL 全解决：本体 Item_500XX 与晋升 Item_500XXn 的**前 10 个字符相同**
        （'Item_50001' vs 'Item_500011'），故 substr(asset_id,1,10) 即是英雄键。
        """
        all_forms = sorted({a for forms in mapping.values() for a in forms})
        lst = ",".join(f"'{x}'" for x in all_forms)
        sql = (f"SELECT substr(asset_id,1,10) AS base, count(distinct user_id) o "
               f"FROM v1090.ods_user_asset "
               f"WHERE asset_id IN ({lst}) AND change_type='1'{seg} GROUP BY 1")
        by_base = {r["base"]: int(r["o"]) for r in execute_sql(sql, datasource="TRINO_HF")["data"]}
        return {h: by_base.get(f"Item_{50000 + int(h) - 1000}", 0) for h in mapping}

    print(f"查询中… 皮肤 {len(skins)} 款 / 英雄 {len(heroes)} 个 · 服段={seg_name}")
    sk_own = owners([f"Item_{s['item_id']}" for s in skins])
    hr_own = hero_owner_counts(hero_assets)

    for s in skins:
        s["owners"] = sk_own.get(f"Item_{s['item_id']}", 0)
        s["hero_owners"] = hr_own.get(s["hero_id"], 0)
        s["hero_forms"] = hero_assets.get(s["hero_id"], [])
        s["rate"] = (s["owners"] / s["hero_owners"] * 100) if s["hero_owners"] else None

    skins.sort(key=lambda x: (-(x["rate"] if x["rate"] is not None else -1), -x["owners"]))
    print(f"\n{'皮肤ID':8s}{'标签':6s}{'名字':22s}{'获取人数':>8s}{'解锁英雄':>9s}{'获取率':>8s}  属性")
    for s in skins:
        rate = f"{s['rate']:.1f}%" if s["rate"] is not None else "—"
        pn = s["prop_num"]
        prop = f"{s['prop']} +{int(pn)/100:.0f}%" if pn.isdigit() and int(pn) >= 100 else ""
        print(f"{s['skin_id']:8s}{s['tag'][:5]:6s}{s['name'][:20]:22s}{s['owners']:>8d}{s['hero_owners']:>9d}{rate:>8s}  {prop}")

    json.dump({"segment": seg_name, "skins": skins},
              open(os.path.join(HERE, "x3_skin_ownership.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\nsaved x3_skin_ownership.json  ({len(skins)} 款)")


if __name__ == "__main__":
    main()
