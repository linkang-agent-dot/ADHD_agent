"""写入 X2 2112 占星节掉落转付费 3 行"""
import subprocess, json, sys

GWS = r"C:\Users\linkang\AppData\Roaming\npm\gws.cmd"
ID_2112 = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"

EMPTY_STR = '""'  # gws 配置表空字段
filter_json = json.dumps({"op":"ge","typ":"building","id":111811,"val":6}, separators=(",",":"))

# ── Row 1: 21127359 掉落活动 ──────────────────────────────
text_drop = json.dumps({
    "group_label":"LC_EVENT_droptopay_tuohuang_title",
    "label":"LC_EVENT_droptopay_tuohuang_droptitle",
    "title":"LC_EVENT_droptopay_tuohuang_droptitle"
}, separators=(",",":"))
comp_drop = json.dumps([
    {"typ":"drop","id":21241917},{"typ":"drop","id":21241918},
    {"typ":"drop","id":21241919},{"typ":"drop","id":21241920},
    {"typ":"drop","id":21241921},{"typ":"drop","id":21241922},
    {"typ":"drop","id":21241923}
], separators=(",",":"))
desc_drop = json.dumps({"rule":"LC_EVENT_droptopay_tuohuang_dropactv_rule"}, separators=(",",":"))

row1 = ["", "21127359", "占星节-掉落转付费-掉落活动",
        "event_labor_2025_2_drop_schema1", "0", "49993", "211201001",
        filter_json, text_drop, comp_drop, desc_drop,
        "21191332", "1", EMPTY_STR,
        "assets/x2/operation/EventBanner/summer_drop_banner.png",
        "0", "0", "0", "21127359", "0", "[]", EMPTY_STR,
        "0", "1511030002", "1", EMPTY_STR, "0"]

# ── Row 2: 21127360 礼包 ──────────────────────────────────
text_pkg = json.dumps({
    "group_label":"LC_EVENT_droptopay_tuohuang_title",
    "label":"LC_EVENT_droptopay_tuohuang_libaotitle"
}, separators=(",",":"))
comp_pkg = json.dumps([{"typ":"discount","id":212100316}], separators=(",",":"))
desc_pkg = json.dumps({}, separators=(",",":"))

row2 = ["", "21127360", "占星节-掉落转付费-礼包",
        "event_labor_2025_2_drop_pkg_schema1", "0", "49994", "211201002",
        filter_json, text_pkg, comp_pkg, desc_pkg,
        "21191081", "1", EMPTY_STR,
        "assets/x2/operation/EventBanner/summer_drop_banner.png",
        "0", "0", "0", "21127359", "0", "[]", EMPTY_STR,
        "0", "1511030002", "1", EMPTY_STR, "0"]

# ── Row 3: 21127361 主活动 ────────────────────────────────
text_main = json.dumps({
    "group_label":"LC_EVENT_droptopay_tuohuang_title",
    "label":"LC_EVENT_droptopay_tuohuang_title",
    "title":"LC_EVENT_droptopay_tuohuang_title"
}, separators=(",",":"))

comp_main = (
    [{"typ":"actv_links","id":212100317}] +
    [{"typ":"drop_topay_show","id":212100315}] +
    [{"typ":"drop_topay","id":212100314}] +
    [{"typ":"new_progress","id":i} for i in range(212100319, 212100499)] +
    [{"typ":"retake","id":21371255},{"typ":"retake","id":21371256},
     {"typ":"retake","id":21371257},{"typ":"retake","id":21371258}] +
    [{"typ":"exchange","id":i} for i in range(21161748, 21161758)]
)
comp_main_json = json.dumps(comp_main, separators=(",",":"))
desc_main = json.dumps({"rule":"LC_EVENT_droptopay_tuohuang_rule"}, separators=(",",":"))

row3 = ["", "21127361", "占星节-掉落转付费-主活动",
        "event_labor_2025_shop_schema1", "0", "49995", "211201003",
        filter_json, text_main, comp_main_json, desc_main,
        "21191331", "1", EMPTY_STR,
        "assets/operation/P2dlcimg/activityImg/EventBanner_BG_428.png",
        "0", "0", "0", "21127359", "0", "[]", EMPTY_STR,
        "0", "1511030002", "1", EMPTY_STR, "0"]

# ── 逐行写入（分三次避免超长 JSON 问题） ──────────────────
for i, row in enumerate([row1, row2, row3], 1):
    jv = json.dumps([row], ensure_ascii=False)
    r = subprocess.run(
        [GWS, "sheets", "+append", "--spreadsheet", ID_2112, "--json-values", jv],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    status = "OK" if r.returncode == 0 else "FAIL"
    out_snippet = (r.stdout or "")[:200].encode("ascii","replace").decode()
    err_snippet = (r.stderr or "")[:200].encode("ascii","replace").decode()
    print(f"Row {i} ({['21127359','21127360','21127361'][i-1]}): {status}")
    if r.returncode != 0:
        print("  OUT:", out_snippet)
        print("  ERR:", err_snippet)
    else:
        # 提取 updatedRange
        import re
        m = re.search(r'"updatedRange"\s*:\s*"([^"]+)"', r.stdout or "")
        if m:
            print("  Range:", m.group(1))

print("done")
