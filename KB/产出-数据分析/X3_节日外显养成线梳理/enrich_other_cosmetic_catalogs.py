"""为 X3 节日外显其余9个模块生成“具体资产+ICON+投放方式”目录。

资源链优先使用配置中的 DK，再经 Path_*.asset 定位客户端正式 PNG，压成 WebP
后以内嵌 data URI 写入主 HTML。重复执行只替换标记区。
"""

from __future__ import annotations

import ast
import base64
import csv
import io
import json
import re
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
HTML = HERE / "X3节日外显养成线全景_模块页签版_20260804.html"
OWNERSHIP = HERE / "x3_other_cosmetic_ownership.json"
TSV = Path(r"C:\x3\gdconfig\tsv")
CLIENT = Path(r"C:\x3-project\client")
PATH_DIR = CLIENT / r"Assets\Res\Config\DisplayKey"
GALLERY_GEN = Path(r"C:\ADHD_agent\KB\产出-本地化与美术\X3\外显图库_表情头像框铭牌\_gen_festival_cosmetics.py")
CACHE = HERE / ".cosmetic_icon_cache"
START = "/* OTHER_COSMETIC_CATALOGS_START */"
END = "/* OTHER_COSMETIC_CATALOGS_END */"


def rows(name: str, encoding: str = "utf-8") -> list[list[str]]:
    with (TSV / name).open("r", encoding=encoding, errors="replace", newline="") as f:
        return list(csv.reader(f, delimiter="\t"))


def literals(*names: str) -> dict[str, object]:
    tree = ast.parse(GALLERY_GEN.read_text(encoding="utf-8"))
    wanted = set(names)
    result: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id in wanted:
            result[target.id] = ast.literal_eval(node.value)
    missing = wanted - result.keys()
    if missing:
        raise RuntimeError(f"图库生成器缺少字面量：{sorted(missing)}")
    return result


def load_dk_paths() -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(r"- key: ([^\r\n]+)\r?\n\s+objPath: ([^\r\n]+)")
    for asset in PATH_DIR.glob("Path_*.asset"):
        for dk, obj_path in pattern.findall(asset.read_text(encoding="utf-8", errors="ignore")):
            result[dk.strip()] = obj_path.strip()
    return result


DK_PATHS = load_dk_paths()


def icon_path(dk: str) -> Path | None:
    rel = DK_PATHS.get(dk, "")
    path = CLIENT / Path(rel) if rel else None
    return path if path and path.is_file() else None


def webp_data_uri(path: Path) -> str:
    CACHE.mkdir(exist_ok=True)
    key = f"{path.stat().st_mtime_ns}_{path.stat().st_size}_{path.name}".encode("utf-8")
    import hashlib

    cache = CACHE / (hashlib.md5(key).hexdigest() + ".webp")
    if not cache.exists():
        with Image.open(path) as src:
            image = src.convert("RGBA")
            image.thumbnail((112, 112), Image.Resampling.LANCZOS)
            image.save(cache, format="WEBP", quality=84, method=4)
    return "data:image/webp;base64," + base64.b64encode(cache.read_bytes()).decode("ascii")


def entry(name: str, iid: str, period: str, route: str, meta: str, dk: str) -> dict[str, str]:
    path = icon_path(dk)
    if not path:
        raise RuntimeError(f"ICON未解析：{name} | {iid} | {dk}")
    status = "missing" if ("待补" in route or "暂无获取渠道" in route) else ""
    return {
        "name": name,
        "id": str(iid),
        "period": period,
        "route": route,
        "meta": meta,
        "dk": dk,
        "src": webp_data_uri(path),
        "status": status,
    }


def group(title: str, note: str, items: list[dict[str, str]]) -> dict[str, object]:
    return {"title": title, "note": note, "items": items}


def build() -> dict[str, object]:
    lit = literals(
        "city", "city_other", "deco_beam", "deco_floor", "deco_wall",
        "trail", "ship_fest", "frame", "card_mem", "emoji",
    )
    item_rows = {r[0]: r for r in rows("Item__Item.tsv", "utf-8-sig") if r and r[0].isdigit()}
    item = lambda iid: item_rows[str(iid)]

    # 主城：旧白皮书9款 + 后续2款。
    city_items = []
    for iid, name, period, attr, route, _ in lit["city"]:
        city_items.append(entry(name, iid, period, route, attr, item(iid)[20]))
    for iid, name, period, attr, route, _ in lit["city_other"]:
        if name not in {"回声魔山", "梦幻王蝶巢穴"}:
            continue
        city_items.append(entry(name, iid, period, route, attr, item(iid)[20]))

    # 家具：当前配置中明确写了节日获取来源的36件。
    non_fest = ["摊位", "开拓航道商店", "酒馆狂欢礼包", "秋季酿酒大赛", "金币鸡仔", "远征商店", "累计充值"]
    furniture_items = []
    for r in rows("FurnitureDecorate__FurnitureDecorate.tsv")[29:]:
        if len(r) < 29 or not r[0].isdigit():
            continue
        iid, name, dk, source = r[0], r[1], r[6], r[28]
        if not ("jiaju" in dk or "Halloween" in dk):
            continue
        if not source or any(k in source for k in non_fest):
            continue
        furniture_items.append(entry(name, iid, source.replace("活动获取", ""), source, "城内节日家具", dk))
    furniture_items.sort(key=lambda x: int(x["id"]))

    # 装饰三件套：6套×3件。
    deco_rows = {r[0]: r for r in rows("FurnitureSkin__FurnitureSkin.tsv") if r and r[0].isdigit()}
    deco_routes = {
        "樱花·春风品酒节": "节日活动进度 / 累充高档赠送",
        "人鱼之歌·魂归之潮": "节日活动进度 / 累充高档赠送",
        "25海滨假日": "节日活动进度 / 累充高档赠送",
        "25中秋": "节日活动进度 / 累充高档赠送",
        "25圣诞": "装潢礼包 210417（$99.99，三件整套）",
        "26春节": "装潢礼包 210816（$99.99，三件整套）",
    }
    deco_groups: dict[str, list[dict[str, str]]] = {}
    for kind, key in (("横梁", "deco_beam"), ("地板", "deco_floor"), ("墙纸", "deco_wall")):
        for iid, name, period, _ in lit[key]:
            dk = deco_rows[iid][3]
            deco_groups.setdefault(period, []).append(entry(name, iid, period, deco_routes[period], kind, dk))

    # 行军皮肤：14款节日船皮，现有知识库只确认到节日与配套航迹，具体奖励容器保留待补。
    ship_items = []
    for iid, name, period, fx, dk_name in lit["ship_fest"]:
        route = f"{period}对应节日活动；与{fx}成套；具体奖励容器待补"
        ship_items.append(entry(name, iid, period, route, f"船皮肤 · 配套{fx}", "DK_" + dk_name))

    # 航迹：逐款列原始兑换、返场、常驻/BP附加渠道。
    trail_items = []
    for ids, name, period, _ in lit["trail"]:
        skin_id, item_id = [x.strip() for x in ids.split("/")]
        routes = [f"原始{period}兑换商店：2000节日货币，限购1"]
        if skin_id != "3012":
            routes.append("尼罗返场商店1335：200圣甲虫碎片，限购1")
        if skin_id == "3002":
            routes.append("常驻商店")
        if skin_id == "3010":
            routes.append("BP进度奖励")
        trail_items.append(entry(name, f"{skin_id} / Item_{item_id}", period, "；".join(routes), "航迹特效 · 无属性", item(item_id)[20]))

    # 头像框：16款节日框 + 48款世界杯国家框。
    frame_items = []
    for iid, name, period, route, _ in lit["frame"]:
        frame_items.append(entry(name, iid, period, route, "永久" if "7天" not in route else "7天", item(iid)[20]))
    wc_frames = []
    for iid in range(80300, 80348):
        r = item(str(iid))
        wc_frames.append(entry(r[1].replace("（永久）", ""), str(iid), "世界杯", r[11] or "世界杯竞猜自选头像框宝箱获取", "永久·国家助威框", r[20]))

    # 纪念卡：当前7张节日卡。
    card_items = []
    for iid, name, period, _, route, attr in lit["card_mem"]:
        card_items.append(entry(name, iid, period, route, attr, item(iid)[20]))

    # 聊天表情：5款节日表情 + 48款世界杯国家表情。
    emoji_items = []
    for iid, name, period, _ in lit["emoji"]:
        emoji_items.append(entry(name, iid, period, "节日BP进度 / 活动免费奖励", "聊天表情", item(iid)[20]))
    wc_emojis = []
    for iid in range(15420, 15468):
        r = item(str(iid))
        wc_emojis.append(entry(r[1].replace("（表情）", ""), str(iid), "世界杯", "世界杯助威表情；具体发放容器待补", "国家助威表情", r[20]))

    # 称号/铭牌：现表7款，直接使用配置获取来源。
    title_items = []
    for r in rows("PlayerTitle__PlayerTitle.tsv"):
        if len(r) < 8 or not r[0].isdigit():
            continue
        quality = {"0": "蓝", "1": "紫", "2": "橙", "3": "橙+"}.get(r[7], r[7])
        title_items.append(entry(r[1], r[0], "活动称号", r[5] or "来源待补", f"{quality}品质 · 站位Buff", r[2]))

    catalogs = {
        "主城皮肤": {"scope": "当前节日资源11款（白皮书9款 + 后续2款）", "groups": [group("节日主城皮肤", "功能型外显；逐款列活动/礼包入口", city_items)]},
        "家具": {"scope": "当前配置明确节日来源36件；旧白皮书基线38件", "groups": [group("节日家具", "按当前 FurnitureDecorate 获取来源字段收口", furniture_items)]},
        "装饰三件套": {"scope": "6套 / 18件", "groups": [group(period, f"3件套 · {deco_routes[period]}", items) for period, items in deco_groups.items()]},
        "行军皮肤": {"scope": "14款节日船皮", "groups": [group("节日行军皮肤", "全部带属性并绑定配套航迹；奖励容器未完全对账的逐款标待补", ship_items)]},
        "航迹": {"scope": "7款节日航迹", "groups": [group("节日航迹", "原始兑换 + 返场 + 常驻/BP渠道并列", trail_items)]},
        "头像框": {"scope": "16款节日框 + 48款世界杯国家框 = 64款", "groups": [group("节日主题头像框", "累充 / 活动进度 / 排名 / 近期活动", frame_items), group("世界杯国家助威头像框", "48款 · 世界杯竞猜自选头像框宝箱", wc_frames)]},
        "纪念卡": {"scope": "当前7张节日卡", "groups": [group("节日纪念卡", "逐卡列当前获取状态与成长属性", card_items)]},
        "聊天表情": {"scope": "5款节日表情 + 48款世界杯国家表情 = 53款", "groups": [group("节日主题表情", "BP进度 / 活动免费奖励", emoji_items), group("世界杯国家助威表情", "48款 · 具体发放容器待补", wc_emojis)]},
        "称号 / 铭牌": {"scope": "当前配置7款活动称号", "groups": [group("活动称号 / 铭牌", "逐款读取 PlayerTitle 获取来源", title_items)]},
    }
    return catalogs


def main() -> None:
    catalogs = build()
    ownership = json.loads(OWNERSHIP.read_text(encoding="utf-8"))
    owner_index = {x["key"]: x for x in ownership["items"]}
    for module, catalog in catalogs.items():
        catalog["ownership"] = {
            "segment": ownership["segment"],
            "window": ownership["active_window"],
            "denominator": ownership["denominator"],
            "formula": ownership["formula"],
        }
        for item in [x for g in catalog["groups"] for x in g["items"]]:
            row = owner_index[f"{module}|{item['id']}"]
            item["owners"] = row["owners"]
            item["denominator"] = row["denominator"]
            item["rate"] = row["rate"]
            item["rate_status"] = row["status"]
            item["asset_ids"] = row["asset_ids"]
    total = sum(len(g["items"]) for c in catalogs.values() for g in c["groups"])
    payload = json.dumps(catalogs, ensure_ascii=False, separators=(",", ":"))
    block = f"{START}\nconst moduleCatalogs={payload};\n{END}"
    html = HTML.read_text(encoding="utf-8")
    if START in html and END in html:
        html = re.sub(re.escape(START) + r"[\s\S]*?" + re.escape(END), lambda _: block, html, count=1)
    else:
        html = html.replace("function heroSkinCatalog(){", block + "\nfunction heroSkinCatalog(){", 1)
    HTML.write_text(html, encoding="utf-8")
    print("modules=", len(catalogs), "items=", total)
    print({k: sum(len(g["items"]) for g in v["groups"]) for k, v in catalogs.items()})


if __name__ == "__main__":
    main()
