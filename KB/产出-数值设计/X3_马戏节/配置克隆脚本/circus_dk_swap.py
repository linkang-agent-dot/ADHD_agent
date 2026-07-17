# -*- coding: utf-8 -*-
"""马戏节 gdconfig 占位DK→新DK 行级安全换名。断言：目标行存在+旧DK在该行+新DK已在client注册。
留占位不换（资产缺口）：开箱/装饰bg(turntable_bg)、拜访bg(候选未定稿)、拜访礼包图、装饰视频。"""
import io, os, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"C:\x3\gdconfig-circus\tsv"

# (文件, 行ID, 旧DK, 新DK)
SWAPS = [
 ("ActvCrafting__ActvCrafting.tsv","1517","DK_WC_Crafting_BoxClose","DK_circus_box_close"),
 ("ActvCrafting__ActvCrafting.tsv","1517","DK_WC_Crafting_BoxOpen","DK_circus_box_open"),
 ("ActvOnline__ActvGroup.tsv","143","DK_img_Activity_icon_Monopoly_deepsea","DK_img_Activity_icon_Monopoly_circus"),
 ("ActvOnline__ActvOnline.tsv","102803","DK_img_Activity_icon_Monopoly_deepsea","DK_img_Activity_icon_Monopoly_circus"),
 ("ActvOnline__ActvOnline.tsv","102803","DK_img_Activity_Monopoly_deepsea_bg","DK_img_Activity_circus_monopoly_bg"),
 ("ActvOnline__ActvOnline.tsv","106104","DK_img_Activity_deepsea_icon_decor","DK_img_Activity_circus_icon_decor"),
 ("ActvOnline__ActvOnline.tsv","101343","DK_img_Activity_deepsea_exchange_icon","DK_img_Activity_circus_exchange_icon"),
 ("ActvOnline__ActvOnline.tsv","101343","DK_img_Activity_deepsea_exchange_bg","DK_img_Activity_circus_exchange_bg"),
 ("ActvOnline__ActvOnline.tsv","101344","DK_img_Activity_deepsea_exchange_bg","DK_img_Activity_circus_exchange_bg"),
 ("ActvOnline__ActvOnline.tsv","109101","DK_img_Activity_deepsea_weekcard_bg","DK_img_Activity_circus_weekcard_bg"),
 ("ActvOnline__ActvOnline.tsv","101026","DK_img_Activity_deepsea_turntable_icon","DK_img_Activity_circus_box_icon"),
 ("ActvOnline__ActvOnline.tsv","105606","DK_img_Activity_deepsea_visit_icon","DK_img_Activity_circus_visit_icon"),
 ("ActvOnline__ActvOnline.tsv","105014","DK_img_Activity_deepsea_wishpool_icon","DK_img_Activity_circus_wishpool_icon"),
 ("ActvOnline__ActvOnline.tsv","105014","DK_img_Activity_deepsea_wishpool_bg","DK_img_Activity_circus_wishpool_bg"),
 ("ActvOnline__ActvOnline.tsv","102994","DK_img_Activity_deepsea_schedule_icon","DK_img_Activity_circus_schedule_icon"),
 ("ActvOnline__ActvOnline.tsv","102994","DK_img_Activity_deepsea_schedule_bg","DK_img_Activity_circus_schedule_bg_v2"),
 ("ActvOnline__ActvOnline.tsv","10071705","DK_img_Activity_deepsea_tavern_icon","DK_img_Activity_circus_tavern_icon"),
 ("ActvOnline__ActvOnline.tsv","10071705","DK_img_Activity_deepsea_tavern_bg","DK_img_Activity_circus_tavern_bg"),
 ("ActvOnline__ActvOnline.tsv","100599","DK_img_Activity_deepsea_fund_icon","DK_img_Activity_circus_fund_icon"),
 ("ActvOnline__ActvOnline.tsv","100599","DK_img_Activity_deepsea_fund_bg","DK_img_Activity_circus_fund_bg"),
 ("ActvOnline__ActvOnline.tsv","102251","DK_img_Activity_deepsea_bp_icon","DK_img_Activity_circus_bp_icon"),
 ("ActvOnline__ActvOnline.tsv","102251","DK_img_Activity_deepsea_bp_bg","DK_img_Activity_circus_bp_bg_v2"),
 ("ItemObtain__ItemObtain.tsv","100363","DK_img_Activity_deepsea_visit_icon","DK_img_Activity_circus_visit_icon"),
 ("ItemObtain__ItemObtain.tsv","1209","DK_img_Activity_deepsea_turntable_icon","DK_img_Activity_circus_box_icon"),
 ("Item__Item.tsv","81152","DK_icon_island_Egypt","DK_icon_island_Circus"),
 ("Item__Item.tsv","1209","DK_icon_global_deepsea_treasuremap","DK_circus_ticket_icon"),
 ("Item__Item.tsv","1210","DK_icon_global_deepsea_orb","DK_circus_medal_icon"),
 ("Item__Item.tsv","1213","DK_icon_global_deepsea_invitation","DK_icon_global_circus_invitation"),
 ("Item__Item.tsv","180081","DK_icon_card_image_80","DK_icon_card_image_81"),
 ("Item__Item.tsv","82006","DK_icon_global_deepseatitle","DK_icon_global_circustitle"),
 ("Item__Item.tsv","1211","DK_icon_global_deepsea_treasuremap","DK_icon_global_circus_gachacoin"),
 ("Item__Item.tsv","1212","DK_icon_global_deepsea_treasuremap","DK_icon_global_circus_gachavoucher"),
 ("Pack__ChainPack.tsv","702","DK_img_Activity_deepsea_icon_decor","DK_img_Activity_circus_icon_decor"),
 ("Skin__Skin.tsv","1017","DK_icon_island_Egypt","DK_icon_island_Circus"),
]

# 新DK必须已在 client Path 注册（防换到不存在的资源→游戏白图）
path_dir = r"C:\x3-project\client\Assets\Res\Config\DisplayKey"
registered = set()
for f in os.listdir(path_dir):
    if f.endswith(".asset"):
        for l in io.open(os.path.join(path_dir, f), encoding="utf-8"):
            l = l.strip()
            if l.startswith("- DK_"):
                registered.add(l[2:])
missing = {n for _,_,_,n in SWAPS} - registered
assert not missing, "新DK未注册: %s" % missing

changed = {}
for fn, rid, old, new in SWAPS:
    p = os.path.join(REPO, fn)
    lines = changed.get(p) or io.open(p, encoding="utf-8").read().split("\n")
    hit = 0
    for i, l in enumerate(lines):
        cols = l.split("\t")
        ids = [c.strip() for c in cols[:3]]
        if rid in ids and old in l:
            # 单元格级替换：完整DK名匹配（防前缀串扰）
            lines[i] = "\t".join(c.replace(old, new) if old in c else c for c in cols)
            hit += 1
    assert hit == 1, "%s id=%s old=%s 命中%d处(应=1)" % (fn, rid, old, hit)
    changed[p] = lines

for p, lines in changed.items():
    io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("写盘", os.path.basename(p))
print("换名", len(SWAPS), "处完成")
