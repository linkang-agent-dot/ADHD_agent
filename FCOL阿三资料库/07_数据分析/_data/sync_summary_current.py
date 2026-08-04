# -*- coding: utf-8 -*-
"""把各位置定稿页的当前榜单同步回评价体系总入口。

位置页是分数、工资残差和时刻差的权威源；本脚本只负责汇总展示，避免总入口长期残留旧数字。
"""
from pathlib import Path
import os
import re

import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SUMMARY = ROOT / "永恒评价体系_系统总结_20260727.html"
PAGES = [
    ("中锋", "永恒中锋评价_定稿版_20260727.html", {"ST", "CF"}),
    ("边锋", "永恒边锋评价_定稿版_20260727.html", {"LW", "RW", "LM", "RM"}),
    ("前腰", "永恒前腰评价_定稿版_20260727.html", {"CAM"}),
    ("中场", "永恒中场评价_定稿版_20260727.html", {"CM"}),
    ("后腰", "永恒后腰评价_定稿版_20260727.html", {"CDM"}),
]


def visible_names(path, table_index):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    table = soup.find_all("table")[table_index]
    result = []
    for row in table.find_all("tr")[1:]:
        cell = row.find("td", class_="nm")
        if not cell:
            result.append("")
            continue
        own = cell.find(string=True, recursive=False)
        result.append((own or cell.get_text(" ", strip=True)).strip())
    return result


def load_tables():
    main_rows, delta_rows = [], []
    for group, filename, official in PAGES:
        path = ROOT / filename
        main, versus = pd.read_html(path)[:2]
        main["球员名"] = visible_names(path, 0)
        versus["球员名"] = visible_names(path, 1)
        main = main[main["官方位置"].isin(official)].copy()
        versus = versus[versus["官方位置"].isin(official)].copy()
        main["位置组"] = group
        versus["位置组"] = group
        main["工资残差值"] = pd.to_numeric(main["工资残差"], errors="coerce")
        versus["换代增幅值"] = pd.to_numeric(
            versus["加减"].astype(str).str.replace("+", "", regex=False), errors="coerce"
        )
        main_rows.append(main)
        delta_rows.append(versus)
    return pd.concat(main_rows, ignore_index=True), pd.concat(delta_rows, ignore_index=True)


def html_table(headers, rows):
    head = "".join("<th>%s</th>" % h for h in headers)
    body = "".join(
        "<tr>%s</tr>" % "".join("<td%s>%s</td>" % (' class="nm"' if i == 1 else "", v) for i, v in enumerate(row))
        for row in rows
    )
    return "<table><tr>%s</tr>%s</table>" % (head, body)


def replace_section(soup, heading_prefix, fragment_html):
    heading = next(h for h in soup.find_all("h2") if h.get_text(strip=True).startswith(heading_prefix))
    node = heading.next_sibling
    while node and not (getattr(node, "name", None) == "h2"):
        nxt = node.next_sibling
        node.extract()
        node = nxt
    fragment = BeautifulSoup(fragment_html, "html.parser")
    for child in list(fragment.contents)[::-1]:
        heading.insert_after(child)


def main():
    raw = SUMMARY.read_text(encoding="utf-8")
    raw = raw.replace("显示值 ≥165→3分", "显示值 ≥165→4分")
    raw = raw.replace("档位分 1/2/3", "档位分 1/2/4")
    raw = raw.replace("145/155/165=1/2/3分", "145/155/165=1/2/4分")
    raw = raw.replace("终分 ÷ 满分132", "终分 ÷ 该位置满分")
    raw = raw.replace("正牌8人", "正牌10人")
    raw = raw.replace("66人", "69人")
    raw = raw.replace("53人", "51人")
    raw = raw.replace(
        "66永恒+47时刻全量34项属性（数据底座）；_data/README.md=数据登记册",
        "69永恒（其中43张有同名时刻对照）；tm_only_attrs.json另含51名时刻独有球员；_data/README.md=数据登记册",
    )
    soup = BeautifulSoup(raw, "html.parser")
    main_df, delta_df = load_tables()

    cm = main_df[main_df["位置组"] == "中场"].sort_values("终分", ascending=False)
    cm_rows = []
    for rank, (_, row) in enumerate(cm.iterrows(), 1):
        cm_rows.append([
            rank,
            row["球员名"],
            "%.1f" % float(row["终分"]),
            int(row["薪"]),
            "%+.1f" % float(row["工资残差值"]),
            row["评语"],
        ])
    cm_html = html_table(["#", "球员", "终分", "薪", "工资残差", "一句话"], cm_rows)
    cm_html += (
        '<p class="small">当前正牌中场：马特乌斯165.5登顶；图雷155.5第2，哈维143第3，'
        '杰拉德141.5第4，皮尔洛与兰帕德137并列第5。后腰近亲参考：马特乌斯128同样高于全部正牌后腰。</p>'
    )
    replace_section(soup, "中场终榜", cm_html)
    next(h for h in soup.find_all("h2") if h.get_text(strip=True).startswith("中场终榜")).string = (
        "中场终榜（正牌10人落位，2026-08-04更新）"
    )

    wages = main_df.dropna(subset=["工资残差值"]).sort_values("工资残差值", ascending=False).head(12)
    wage_rows = [[
        i,
        row["球员名"],
        row["位置组"],
        "%.1f" % float(row["终分"]),
        int(row["薪"]),
        "%+.1f" % float(row["工资残差值"]),
    ] for i, (_, row) in enumerate(wages.iterrows(), 1)]
    deltas = delta_df.dropna(subset=["换代增幅值"]).sort_values("换代增幅值", ascending=False).head(12)
    delta_rows = [[
        i,
        row["球员名"],
        row["位置组"],
        "%.1f" % float(row["永恒8卡"]),
        "%.1f" % float(row["时刻8卡"]),
        "%+.1f" % float(row["换代增幅值"]),
    ] for i, (_, row) in enumerate(deltas.iterrows(), 1)]
    value_html = (
        '<p class="small"><b>双维超模定义：</b>①换代增幅=永恒8卡−同名时刻8卡；②工资残差=终分−同位置工资定价线。'
        '两项都高且绝对终分过主力线，才是完整意义上的超模卡。</p>'
        '<h3>工资残差 Top12</h3>'
        + html_table(["#", "球员", "位置", "终分", "薪", "工资残差"], wage_rows)
        + '<h3>永恒对时刻换代增幅 Top12</h3>'
        + html_table(["#", "球员", "位置", "永恒8", "时刻8", "提升"], delta_rows)
        + '<p class="small">马特乌斯：绝对分第1、换代+82总榜第4、工资残差+17.6总榜第5，当前双维综合第一。'
          '皮尔洛换代+80但工资残差仅+1.3，属于换代超模；索尔斯克亚无时刻对照且工资残差−5.3，不属于超模。</p>'
    )
    dual_prefix = "双维超模榜" if any(
        h.get_text(strip=True).startswith("双维超模榜") for h in soup.find_all("h2")
    ) else "质价比（工资口径）"
    replace_section(soup, dual_prefix, value_html)
    wage_h = next(h for h in soup.find_all("h2") if h.get_text(strip=True).startswith(dual_prefix))
    wage_h.string = "双维超模榜（换代增幅 × 工资残差，2026-08-04）"

    new_h = soup.new_tag("h2")
    new_h.string = "新增永恒三卡速览（2026-08-04）"
    new_rows = [
        [1, '<a href="https://cn.fifaaddict.com/fo4db/pidvzkvzpow">马特乌斯</a>', "CM/CDM", "165.5 / 128.0", "+82.0", "+17.6", "双维超模王"],
        [2, '<a href="https://cn.fifaaddict.com/fo4db/pidyolwvovb">皮尔洛</a>', "CM/CDM", "137.0 / 99.0", "+80.0", "+1.3", "换代超模"],
        [3, '<a href="https://cn.fifaaddict.com/fo4db/pidwblkmmld">索尔斯克亚</a>', "ST/CF", "79.0", "无时刻", "−5.3", "队套/情怀卡"],
    ]
    # html_table escapes nothing by design; links are trusted, fixed local content.
    new_fragment = BeautifulSoup(
        html_table(["#", "球员", "位置", "主/副位终分", "换代", "工资残差", "结论"], new_rows),
        "html.parser",
    )
    if any(h.get_text(strip=True).startswith("新增永恒三卡速览") for h in soup.find_all("h2")):
        replace_section(soup, "新增永恒三卡速览", str(new_fragment))
        existing_h = next(
            h for h in soup.find_all("h2") if h.get_text(strip=True).startswith("新增永恒三卡速览")
        )
        existing_h.string = new_h.string
    else:
        wage_h.insert_before(new_h)
        for child in list(new_fragment.contents):
            wage_h.insert_before(child)

    out = str(soup)
    tmp = str(SUMMARY) + ".tmp"
    Path(tmp).write_text(out, encoding="utf-8")
    os.replace(tmp, SUMMARY)
    print("ok", SUMMARY)


if __name__ == "__main__":
    main()
