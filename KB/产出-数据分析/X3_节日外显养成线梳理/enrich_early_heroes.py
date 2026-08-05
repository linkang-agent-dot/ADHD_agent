"""把 D35 前可见英雄池写入 X3 节日外显养成线 HTML。

口径：Hero.ShowTimecycleID -> TimeCycle；“D35前”严格指 D0-D34。
无 ShowTimecycleID 记为 D0 起显示；-1 为未进入常规显示范围。
这里只判断英雄何时进入可见/可投放范围，不等于玩家届时已经获得英雄。
"""

from __future__ import annotations

import base64
import csv
import io
import json
import re
import subprocess
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
HTML = HERE / "X3节日外显养成线全景_模块页签版_20260804.html"
SKIN_JSON = Path(r"C:\ADHD_agent\skills\p2-festival-monitor\x3_skin_ownership.json")
REPO = Path(r"C:\X3\wt_circus_float")
BRANCH = "origin/dev_festival"
CLIENT = Path(r"C:\x3-project\client")
PATH_DIR = CLIENT / r"Assets\Res\Config\DisplayKey"
START = "/* EARLY_HERO_DATA_START */"
END = "/* EARLY_HERO_DATA_END */"
QUALITY_NAMES = {"1": "普通", "2": "稀有", "3": "史诗", "4": "传奇"}


def git_tsv(rel: str) -> list[list[str]]:
    raw = subprocess.check_output(
        ["git", "show", f"{BRANCH}:{rel}"], cwd=REPO
    ).decode("utf-8", errors="replace")
    return list(csv.reader(io.StringIO(raw), delimiter="\t"))


def records(rows: list[list[str]]) -> list[dict[str, str]]:
    index = next(i for i, row in enumerate(rows) if row and row[0] == "ID")
    header = rows[index]
    result = []
    for row in rows[index + 1 :]:
        if not row or not row[0]:
            continue
        padded = row + [""] * (len(header) - len(row))
        result.append(dict(zip(header, padded)))
    return result


def load_dk_paths() -> dict[str, str]:
    mapping: dict[str, str] = {}
    pattern = re.compile(r"- key: ([^\r\n]+)\r?\n\s+objPath: ([^\r\n]+)")
    for asset in PATH_DIR.glob("Path_*.asset"):
        for dk, obj_path in pattern.findall(
            asset.read_text(encoding="utf-8", errors="ignore")
        ):
            mapping[dk.strip()] = obj_path.strip()
    return mapping


def webp_data_uri(path: Path) -> str:
    with Image.open(path) as source:
        image = source.convert("RGBA")
        image.thumbnail((104, 104), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, format="WEBP", quality=84, method=6)
    return "data:image/webp;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def display_window(hero: dict[str, str], cycles: dict[str, dict[str, str]]):
    cycle_id = hero["ShowTimecycleID"].strip()
    if not cycle_id:
        return True, 0, "D0起显示", "无显示时间门槛"
    if cycle_id == "-1":
        return False, 9999, "未进入常规显示", "ShowTimecycleID=-1"

    cycle = cycles[cycle_id]
    trigger_type = cycle["TriggerType"]
    start = cycle["StartTime"]
    if trigger_type == "2":
        match = re.match(r"(\d+)d", start)
        if not match:
            raise ValueError(f"无法解析 TimeCycle {cycle_id}: {start}")
        ui_day = int(match.group(1)) + 1
        return ui_day < 35, ui_day, f"D{ui_day}", cycle["列1"]
    if trigger_type == "6":
        week, weekday = map(int, start.split()[:2])
        latest_day = (week - 1) * 7
        weekday_name = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "日"}[weekday]
        return (
            latest_day < 35,
            latest_day,
            f"第{week}周周{weekday_name}（最晚D{latest_day}）",
            cycle["列1"],
        )
    return False, 9999, start, cycle["列1"]


def buff_label(skin: dict, config: dict[str, str]) -> str:
    raw_num = str(skin.get("prop_num", "")).strip()
    if not raw_num.isdigit() or int(raw_num) == 0:
        return "无属性BUFF"
    name = re.sub(r"<[^>]+>|\{0\}", "", config.get("buff备注", "")).strip()
    value = int(raw_num) / 100
    value_text = f"{value:g}%"
    return f"{name or ('属性' + str(skin.get('prop', '')))} +{value_text}"


def main() -> None:
    hero_rows = [
        row
        for row in records(git_tsv("tsv/Hero__Hero.tsv"))
        if re.fullmatch(r"\d{4}", row["ID"])
    ]
    cycles = {
        row["ID"]: row for row in records(git_tsv("tsv/TimeCycle__TimeCycle.tsv"))
    }
    skin_rows = json.loads(SKIN_JSON.read_text(encoding="utf-8"))["skins"]
    skin_configs = {
        row["ID"]: row for row in records(git_tsv("tsv/Hero__HeroSkin.tsv"))
    }
    skins_by_hero: dict[str, list[dict]] = {}
    for skin in skin_rows:
        skins_by_hero.setdefault(str(skin["hero_id"]), []).append(skin)

    dk_paths = load_dk_paths()
    early = []
    d35_exact = []
    for hero in hero_rows:
        included, order_day, display, schedule_note = display_window(hero, cycles)
        if display == "D35":
            d35_exact.append(hero["Name"])
        if not included:
            continue

        dk = hero["DK_HeadIcon"].strip()
        relative = dk_paths.get(dk, "")
        image_path = CLIENT / Path(relative) if relative else Path()
        if not image_path.is_file():
            raise FileNotFoundError(f"英雄头像未解析：{hero['ID']} {hero['Name']} {dk}")

        hero_skins = sorted(
            skins_by_hero.get(hero["ID"], []), key=lambda x: int(x["skin_id"])
        )
        hero_owners = next(
            (int(x["hero_owners"]) for x in hero_skins if x.get("hero_owners") is not None),
            None,
        )
        early.append(
            {
                "id": hero["ID"],
                "name": hero["Name"],
                "quality": int(hero["Quality"]),
                "quality_name": QUALITY_NAMES[hero["Quality"]],
                "display": display,
                "order_day": order_day,
                "source": hero["列1"],
                "schedule_note": schedule_note,
                "hero_owners": hero_owners,
                "icon": webp_data_uri(image_path),
                "skins": [
                    {
                        "id": skin["skin_id"],
                        "name": skin["name"],
                        "tag": skin["tag"] or "普通/无标签",
                        "owners": int(skin["owners"]),
                        "rate": skin["rate"],
                        "prop": skin.get("prop", ""),
                        "prop_num": skin.get("prop_num", ""),
                        "buff": buff_label(skin, skin_configs.get(str(skin["skin_id"]), {})),
                    }
                    for skin in hero_skins
                ],
            }
        )

    early.sort(key=lambda x: (not bool(x["skins"]), x["order_day"], int(x["id"])))
    free_pool = []
    for hero in early:
        if hero["quality"] not in (2, 3):
            continue
        for skin in hero["skins"]:
            prop_num = int(skin["prop_num"]) if str(skin["prop_num"]).isdigit() else 0
            if skin["rate"] is None or skin["rate"] > 1 or prop_num > 100:
                continue
            free_pool.append(
                {
                    **skin,
                    "hero_id": hero["id"],
                    "hero_name": hero["name"],
                    "hero_quality": hero["quality"],
                    "hero_quality_name": hero["quality_name"],
                }
            )
    free_pool.sort(key=lambda x: (x["rate"], int(x["id"])))
    payload = {
        "scope": "D0-D34",
        "source": f"{BRANCH}: Hero__Hero.tsv → TimeCycle__TimeCycle.tsv",
        "heroes": early,
        "d35_exact": d35_exact,
        "free_pool_rule": "英雄品质为稀有/史诗，皮肤获取率≤1%，且无BUFF或BUFF≤1%",
        "free_pool": free_pool,
    }
    block = (
        f"{START}\nconst earlyHeroData="
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + f";\n{END}"
    )
    html = HTML.read_text(encoding="utf-8")
    if START in html and END in html:
        html = re.sub(
            re.escape(START) + r"[\s\S]*?" + re.escape(END),
            lambda _: block,
            html,
            count=1,
        )
    else:
        html = html.replace("/* HERO_ITEM_ICONS_START */", block + "\n/* HERO_ITEM_ICONS_START */", 1)
    HTML.write_text(html, encoding="utf-8")

    with_skin = sum(bool(x["skins"]) for x in early)
    print(
        f"early_heroes={len(early)} with_skin={with_skin} "
        f"no_skin={len(early)-with_skin} skins={sum(len(x['skins']) for x in early)} "
        f"free_pool={len(free_pool)} d35_exact={','.join(d35_exact)} "
        f"html_size={HTML.stat().st_size}"
    )


if __name__ == "__main__":
    main()
