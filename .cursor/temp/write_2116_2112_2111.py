"""
写入 X2 占星节掉落转付费配置：
- 2116: 10 行 (21161748-21161757)
- 2112: 3 行 (21127359/21127360/21127361)
- 2111: 3 行 (211110567/211110568/211110569)
"""
import subprocess, json, sys

GWS = r"C:\Users\linkang\AppData\Roaming\npm\gws.cmd"

def gws_append(spreadsheet_id, rows):
    """用 gws +append 把多行追加到第一个 tab"""
    json_values = json.dumps(rows, ensure_ascii=False)
    result = subprocess.run(
        [GWS, "sheets", "+append",
         "--spreadsheet", spreadsheet_id,
         "--json-values", json_values],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result

# ─────────────────────────────────────────────────────
# 1. X2 2116  activity_item_exchange（线上版本）
# ─────────────────────────────────────────────────────
ID_2116 = "1LWuPMcNTxujTWHHsNRJgB3t9ZY_84rjxTAKu0kvl2dA"

def make_give(item_id, val):
    return json.dumps([{"asset":{"typ":"item","id":item_id,"val":val},"setting":{"serial_number":1}}], separators=(",",":"))

def make_get(item_id, val):
    return json.dumps([{"asset":{"typ":"item","id":item_id,"val":val},"setting":{"serial_number":1}}], separators=(",",":"))

rows_2116 = [
    ["", "33", "21161748", "2026-占星节-掉落转付费", make_give(111111119,12),  make_get(11111048,1),  "8001", "15"],
    ["", "33", "21161749", "2026-占星节-掉落转付费", make_give(111111119,10),  make_get(11119473,1),  "8002", "20"],
    ["", "33", "21161750", "2026-占星节-掉落转付费", make_give(111111119,20),  make_get(11116304,1),  "8003", "15"],
    ["", "33", "21161751", "2026-占星节-掉落转付费", make_give(111111119,2),   make_get(11111055,1),  "8004", "35"],
    ["", "33", "21161752", "2026-占星节-掉落转付费", make_give(111111119,5),   make_get(11118501,1),  "8005", "50"],
    ["", "33", "21161753", "2026-占星节-掉落转付费", make_give(111111119,15),  make_get(11116604,1),  "8006", "22"],
    ["", "33", "21161754", "2026-占星节-掉落转付费", make_give(111111118,2),   make_get(11119453,1),  "8007", "250"],
    ["", "33", "21161755", "2026-占星节-掉落转付费", make_give(111111118,10),  make_get(11114003,1),  "8008", "15"],
    ["", "33", "21161756", "2026-占星节-掉落转付费", make_give(111111118,20),  make_get(11117024,1),  "8009", "5"],
    ["", "33", "21161757", "2026-占星节-掉落转付费", make_give(111111118,5),   make_get(11111156,1),  "8010", "20"],
]

print("=== 跳过 2116 (已写入) ===")

# ─────────────────────────────────────────────────────
# 2. X2 2112  activity_config_QA
# ─────────────────────────────────────────────────────
ID_2112 = "1Z37Db-2Cy1h6Far_LBPSpKHOtNNki9rzXgLUsvBSJwo"

filter_json   = json.dumps({"op":"ge","typ":"building","id":111811,"val":6}, separators=(",",":"))
schema_common = json.dumps({"typ":"schema","id":[1,2,3,4,5,6]}, separators=(",",":"))

# ---------- 21127359 掉落活动 ----------
text_drop = json.dumps({
    "group_label":"LC_EVENT_droptopay_tuohuang_title",
    "label":"LC_EVENT_droptopay_tuohuang_droptitle",
    "title":"LC_EVENT_droptopay_tuohuang_droptitle"
}, separators=(",",":"))

comp_drop = json.dumps([
    {"typ":"drop","id":21241917}, {"typ":"drop","id":21241918},
    {"typ":"drop","id":21241919}, {"typ":"drop","id":21241920},
    {"typ":"drop","id":21241921}, {"typ":"drop","id":21241922},
    {"typ":"drop","id":21241923}
], separators=(",",":"))

desc_drop = json.dumps({"rule":"LC_EVENT_droptopay_tuohuang_dropactv_rule"}, separators=(",",":"))

# ---------- 21127360 礼包 ----------
text_pkg = json.dumps({
    "group_label":"LC_EVENT_droptopay_tuohuang_title",
    "label":"LC_EVENT_droptopay_tuohuang_libaotitle"
}, separators=(",",":"))
comp_pkg = json.dumps([{"typ":"discount","id":212100316}], separators=(",",":"))
desc_pkg = json.dumps({}, separators=(",",":"))

# ---------- 21127361 主活动 ----------
text_main = json.dumps({
    "group_label":"LC_EVENT_droptopay_tuohuang_title",
    "label":"LC_EVENT_droptopay_tuohuang_title",
    "title":"LC_EVENT_droptopay_tuohuang_title"
}, separators=(",",":"))

# 构建主活动的 activity_components：
# actv_links, drop_topay_show, drop_topay, new_progress×180, retake×4, exchange×10(新IDs)
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

def row_2112(act_id, comment, constant, priority, base_id, text, components, description,
             ui_template, banner_url, show_hud):
    return [
        "",             # col A (empty)
        str(act_id),    # A_INT_id
        comment,        # S_STR_comment
        constant,       # A_STR_constant
        "0",            # A_INT_index
        str(priority),  # S_INT_priority
        str(base_id),   # A_INT_base_activity_id
        filter_json,    # A_MAP_filter
        text,           # A_MAP_text
        components,     # A_ARR_activity_components
        description,    # A_MAP_description
        str(ui_template), # A_INT_ui_template
        "1",            # S_INT_rank_group
        '""',           # S_STR_banner_obj_url
        banner_url,     # S_STR_banner_url
        "0",            # S_STR_banner_version
        "0",            # A_INT_default_displaykey
        "0",            # A_INT_icon_displaykey
        str(show_hud),  # A_INT_show_hud
        "0",            # A_INT_calendar
        "[]",           # A_ARR_calendar_reward
        '""',           # S_STR_calendar_banner_url
        "0",            # A_INT_dependent
        "1511030002",   # C_INT_title_icon
        "1",            # S_INT_merge_save
        '""',           # S_STR_mini_banner_url
        "0",            # A_INT_country_use_type
    ]

rows_2112 = [
    row_2112(21127359, "占星节-掉落转付费-掉落活动",
             "event_labor_2025_2_drop_schema1", 49993, 211201001,
             text_drop, comp_drop, desc_drop,
             21191332, "assets/x2/operation/EventBanner/summer_drop_banner.png",
             21127359),
    row_2112(21127360, "占星节-掉落转付费-礼包",
             "event_labor_2025_2_drop_pkg_schema1", 49994, 211201002,
             text_pkg, comp_pkg, desc_pkg,
             21191081, "assets/x2/operation/EventBanner/summer_drop_banner.png",
             21127359),
    row_2112(21127361, "占星节-掉落转付费-主活动",
             "event_labor_2025_shop_schema1", 49995, 211201003,
             text_main, comp_main_json, desc_main,
             21191331, "assets/operation/P2dlcimg/activityImg/EventBanner_BG_428.png",
             21127359),
]

print("\n=== 写入 2112 (3行) ===")
r = gws_append(ID_2112, rows_2112)
out = (r.stdout or "")[:300].encode("ascii","replace").decode("ascii")
err = (r.stderr or "")[:200].encode("ascii","replace").decode("ascii")
print("STDOUT:", out)
print("STDERR:", err)
print("Exit:", r.returncode)

# ─────────────────────────────────────────────────────
# 3. X2 2111  activity_calendar_x2（线上）
# ─────────────────────────────────────────────────────
ID_2111 = "1x-kAjIEox-JX_CQffEVw1shKZZlUpxR_fe0flTz2Iuk"

schema_2111 = json.dumps({"typ":"schema","id":[1,2,3,4,5,6]}, separators=(",",":"))
times_120h  = json.dumps({"fcastdur":"0h","actvdur":"120h","closedur":"0h"}, separators=(",",":"))
actv_group  = json.dumps({}, separators=(",",":"))

# 主活动：trigger afcutc (936h 是前期值，占星节时需更新)
trigger_main = json.dumps({"typ":"afcutc","val":"936h"}, separators=(",",":"))
# 掉落活动 & 礼包：trigger activity_start → 21127361
trigger_sub  = json.dumps({"typ":"activity_start","val":"21127361"}, separators=(",",":"))

rows_2111 = [
    # 211110567 → 21127361 主活动
    ["", "211110567", "21127361", "占星节-掉落转付费-主活动",
     schema_2111, trigger_main, times_120h, actv_group, "2", "0"],
    # 211110568 → 21127359 掉落活动
    ["", "211110568", "21127359", "占星节-掉落转付费-掉落活动",
     schema_2111, trigger_sub,  times_120h, actv_group, "2", "0"],
    # 211110569 → 21127360 礼包
    ["", "211110569", "21127360", "占星节-掉落转付费-礼包",
     schema_2111, trigger_sub,  times_120h, actv_group, "2", "0"],
]

print("\n=== 写入 2111 (3行) ===")
r = gws_append(ID_2111, rows_2111)
out2 = (r.stdout or "")[:300].encode("ascii","replace").decode("ascii")
err2 = (r.stderr or "")[:200].encode("ascii","replace").decode("ascii")
print("STDOUT:", out2)
print("STDERR:", err2)
print("Exit:", r.returncode)

print("\n✅ 全部写入完成")
