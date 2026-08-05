"""把 X3 正式英雄皮肤道具 ICON 内嵌进养成线 HTML。

权威链：x3_skin_ownership.item_id -> Item__Item.tsv DK_ICON -> Path_*.asset -> PNG。
脚本只更新 HERO_ITEM_ICONS 标记区，重复执行安全。
"""

from __future__ import annotations

import base64
import csv
import io
import json
import re
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
HTML = HERE / "X3节日外显养成线全景_模块页签版_20260804.html"
SKIN_JSON = Path(r"C:\ADHD_agent\skills\p2-festival-monitor\x3_skin_ownership.json")
ITEM_TSV = Path(r"C:\x3\gdconfig\tsv\Item__Item.tsv")
CLIENT = Path(r"C:\x3-project\client")
PATH_DIR = CLIENT / r"Assets\Res\Config\DisplayKey"
START = "/* HERO_ITEM_ICONS_START */"
END = "/* HERO_ITEM_ICONS_END */"


def load_item_icon_dks(item_ids: set[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    with ITEM_TSV.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f, delimiter="\t"):
            if row and row[0] in item_ids:
                # Item 表当前 DK_ICON 位于第21列（Python index 20）。
                result[row[0]] = row[20].strip() if len(row) > 20 else ""
    return result


def load_dk_paths() -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(r"- key: ([^\r\n]+)\r?\n\s+objPath: ([^\r\n]+)")
    for asset in PATH_DIR.glob("Path_*.asset"):
        for dk, obj_path in pattern.findall(asset.read_text(encoding="utf-8", errors="ignore")):
            result[dk.strip()] = obj_path.strip()
    return result


def webp_data_uri(path: Path) -> str:
    with Image.open(path) as src:
        image = src.convert("RGBA")
        image.thumbnail((112, 112), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        image.save(out, format="WEBP", quality=86, method=6)
    return "data:image/webp;base64," + base64.b64encode(out.getvalue()).decode("ascii")


def main() -> None:
    skin_data = json.loads(SKIN_JSON.read_text(encoding="utf-8"))["skins"]
    item_ids = {str(s["item_id"]) for s in skin_data}
    item_dks = load_item_icon_dks(item_ids)
    dk_paths = load_dk_paths()

    icons: dict[str, dict[str, str]] = {}
    missing: list[str] = []
    for skin in skin_data:
        item_id = str(skin["item_id"])
        name = skin["name"]
        dk = item_dks.get(item_id, "")
        rel = dk_paths.get(dk, "")
        path = CLIENT / Path(rel) if rel else Path()
        if not dk or not rel or not path.is_file():
            missing.append(f"{name} | Item_{item_id} | {dk or 'NO_DK'}")
            continue
        icons[name] = {"src": webp_data_uri(path), "item": item_id, "dk": dk}

    if missing:
        raise RuntimeError("以下皮肤道具 ICON 未解析：\n" + "\n".join(missing))
    if len(icons) != 48:
        raise RuntimeError(f"期望48款 ICON，实际{len(icons)}款")

    payload = json.dumps(icons, ensure_ascii=False, separators=(",", ":"))
    block = f"{START}\nconst heroItemIcons={payload};\n{END}"
    html = HTML.read_text(encoding="utf-8")
    if START in html and END in html:
        html = re.sub(
            re.escape(START) + r"[\s\S]*?" + re.escape(END),
            lambda _: block,
            html,
            count=1,
        )
    else:
        html = html.replace("function heroSkinCatalog(){", block + "\nfunction heroSkinCatalog(){", 1)
    HTML.write_text(html, encoding="utf-8")
    print(f"embedded_icons={len(icons)} html={HTML} size={HTML.stat().st_size}")


if __name__ == "__main__":
    main()
