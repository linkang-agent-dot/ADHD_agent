# -*- coding: utf-8 -*-
"""X3 其他节日外显逐件获取率。

口径：成熟服 1000-1880，近30日（2026-07-07~2026-08-05）活跃玩家；
分子为该活跃人群中历史曾获得目标外显的人数，分母为同服段近30日活跃人数。
同一外显的道具资产与解锁后实体资产按 user_id 去重合并。
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, r"C:\ADHD_agent\.agents\skills\ai-to-sql\scripts")
from query_trino import execute_sql

HERE = Path(__file__).resolve().parent
HTML = HERE / "X3节日外显养成线全景_模块页签版_20260804.html"
OUT = HERE / "x3_other_cosmetic_ownership.json"
START = "/* OTHER_COSMETIC_CATALOGS_START */"
END = "/* OTHER_COSMETIC_CATALOGS_END */"
DATE_FROM = "2026-07-07"
DATE_TO = "2026-08-05"
DENOMINATOR = 16969

# 配置实体ID → 发放Item ID。名称维表有返回上限或同名三件套时，用正式Item配置的引用链兜底。
CONFIG_ITEM = {
    "31001055": "151024", "31001070": "151040", "51001004": "151045", "51001005": "151053",
    "1001006": "152008", "2001010": "152007", "3001007": "152009",
    "1001008": "152014", "2001012": "152015", "3001009": "152016",
    "1001009": "152017", "2001013": "152018", "3001010": "152019",
    "1001010": "152021", "2001015": "152022", "3001011": "152023",
    "1001011": "152024", "2001016": "152025", "3001012": "152026",
    "1001012": "152027", "2001017": "152028", "3001013": "152029",
    "105": "82005", "106": "82006",
}


def norm(name: str) -> str:
    name = re.sub(r"[（(](永久|家具|纪念卡|表情|1天|3天|7天|15天|30天|1d|3d|7d|15d|30d)[）)]", "", name, flags=re.I)
    return re.sub(r"\s+", "", name).strip()


def load_catalogs() -> dict:
    text = HTML.read_text(encoding="utf-8")
    block = text.split(START, 1)[1].split(END, 1)[0]
    return json.loads(re.search(r"const moduleCatalogs=(\{[\s\S]*\});", block).group(1))


def allowed(module: str, asset_id: str) -> bool:
    rules = {
        "主城皮肤": ("Item_81", "Skin_"),
        "家具": ("Item_151", "FurnitureDecorate_"),
        "装饰三件套": ("Item_152", "FurnitureSkin_"),
        "行军皮肤": ("Item_150", "Item_151", "ShipSkin_"),
        "航迹": ("Item_150", "Item_151", "Skin_3"),
        "头像框": ("Item_80",),
        "纪念卡": ("Item_180", "MemorialCard_"),
        "聊天表情": ("Item_154",),
        "称号 / 铭牌": ("Item_80", "Item_82", "PlayerTitle_", "Title_"),
    }
    return asset_id.startswith(rules[module])


def direct_ids(module: str, item: dict) -> list[str]:
    iid = str(item["id"])
    if iid in CONFIG_ITEM:
        return [f"Item_{CONFIG_ITEM[iid]}"]
    if module in {"主城皮肤", "头像框", "纪念卡", "聊天表情"}:
        return [f"Item_{iid}"]
    if module == "航迹" and "Item_" in iid:
        return ["Item_" + iid.split("Item_", 1)[1].strip()]
    if module == "行军皮肤":
        return [f"ShipSkin_{iid}"]
    return []


def sql_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def main() -> None:
    if not os.environ.get("DATAIN_API_KEY"):
        raise RuntimeError("DATAIN_API_KEY missing; load the user environment variable first")
    catalogs = load_catalogs()
    flat_items = [(module, item) for module, catalog in catalogs.items()
                  for item in [x for g in catalog["groups"] for x in g["items"]]]
    # execute_sql 的结果集可能被接口截断；按20个名称一批反查，确保每批低于返回上限。
    dim_rows = []
    unique_names = sorted({norm(item["name"]) for _, item in flat_items})
    for i in range(0, len(unique_names), 20):
        chunk = unique_names[i:i + 20]
        clauses = []
        for name in chunk:
            safe = name.replace("'", "''")
            clauses.append(f"replace(replace(replace(asset_name,'（永久）',''),'（家具）',''),'（纪念卡）','') LIKE '%{safe}%'")
        dim_sql = "SELECT asset_id,asset_name FROM v1090.dim_asset WHERE " + " OR ".join(clauses)
        dim_rows.extend(execute_sql(dim_sql, limit=1000, datasource="TRINO_HF")["data"])
    by_name: dict[str, list[str]] = {}
    dim_ids = set()
    for row in dim_rows:
        dim_ids.add(row["asset_id"])
        by_name.setdefault(norm(row["asset_name"]), []).append(row["asset_id"])

    records = []
    target_rows = []
    all_assets = set()
    for module, catalog in catalogs.items():
        for item in [x for g in catalog["groups"] for x in g["items"]]:
            key = f"{module}|{item['id']}"
            candidates = {x for x in by_name.get(norm(item["name"]), []) if allowed(module, x)}
            # 直接ID来自正式配置，可直接作为日志资产查询键；不依赖维表返回是否截断。
            candidates.update(direct_ids(module, item))
            candidates = sorted(candidates)
            records.append({"key": key, "module": module, "id": item["id"], "name": item["name"], "asset_ids": candidates})
            for asset_id in candidates:
                target_rows.append((asset_id, key))
                all_assets.add(asset_id)

    values = ",".join(f"({sql_quote(a)},{sql_quote(k)})" for a, k in target_rows)
    in_list = ",".join(sql_quote(x) for x in sorted(all_assets))
    ownership_sql = f"""WITH active AS (
        SELECT DISTINCT user_id,server_id FROM v1090.ods_user_login
        WHERE partition_date BETWEEN '{DATE_FROM}' AND '{DATE_TO}'
          AND TRY_CAST(server_id AS INTEGER) BETWEEN 1000 AND 1880
    ), target(asset_id,item_key) AS (VALUES {values}), acquired AS (
        SELECT user_id,server_id,asset_id FROM v1090.ods_user_asset
        WHERE asset_id IN ({in_list}) AND change_type='1'
          AND TRY_CAST(server_id AS INTEGER) BETWEEN 1000 AND 1880
        GROUP BY 1,2,3
    )
    SELECT t.item_key,count(DISTINCT a.user_id) owners
    FROM acquired a JOIN target t ON a.asset_id=t.asset_id
    JOIN active u ON a.user_id=u.user_id AND a.server_id=u.server_id
    GROUP BY 1"""
    # query_trino 默认只保留前100行；这里最多217个item_key，必须显式放大limit。
    owner_rows = execute_sql(ownership_sql, limit=1000, datasource="TRINO_HF")["data"]
    owners = {row["item_key"]: int(row["owners"]) for row in owner_rows}
    for record in records:
        record["owners"] = owners.get(record["key"], 0) if record["asset_ids"] else None
        record["denominator"] = DENOMINATOR
        record["rate"] = (record["owners"] / DENOMINATOR * 100) if record["owners"] is not None else None
        record["status"] = "measured" if record["asset_ids"] else "unmapped"

    # 已知阳性回归样本：世界杯/深海均有数仓实证，任何一个为0都说明查询链仍在漏数。
    positive_checks = {"纪念卡|180079": 1, "纪念卡|180080": 1}
    by_key = {x["key"]: x for x in records}
    failed = [key for key, minimum in positive_checks.items() if (by_key[key]["owners"] or 0) < minimum]
    if failed:
        raise RuntimeError(f"known-positive ownership checks failed: {failed}")

    payload = {
        "segment": "成熟服 1000-1880",
        "active_window": f"{DATE_FROM}~{DATE_TO}",
        "denominator": DENOMINATOR,
        "formula": "近30日活跃玩家中历史曾获得人数 / 同服段近30日活跃人数",
        "items": records,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "items": len(records), "mapped": sum(x["status"] == "measured" for x in records),
        "unmapped": [f"{x['module']}|{x['id']}|{x['name']}" for x in records if x["status"] == "unmapped"],
        "asset_ids": len(all_assets), "output": str(OUT),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
