# -*- coding: utf-8 -*-
"""马戏节美术 DK 落地：规格化图 → client 仓（拷图+克隆锚点meta+Display/Path双注册）。
锚点=深海/世界杯同槽位资产（映射来自 x3-media task ref[0]）。幂等可重跑。
换节日复用：改 MAPPING 与 NORM 目录即可。"""
import io, os, re, sys, hashlib, shutil, bisect

sys.stdout.reconfigure(encoding="utf-8")
CLIENT = r"C:\x3-project\client\Assets"
NORM = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\马戏节\规格化"
DISPLAY_DIR = os.path.join(CLIENT, r"Editor\Config\DisplayKey")
PATH_DIR = os.path.join(CLIENT, r"Res\Config\DisplayKey")

# fn -> 锚点资产（Assets 下相对路径）。Amina 主稿不投放不在列。
MAPPING = {
 "Img_Player_AvatarFrame_circus.png": r"Res\UI\Spirits\Personalise\AvatarFrame\Img_Player_AvatarFrame_deepsea.png",
 "circus_box_close.png": r"Res\UI\Spirits\ActvWorldCup\WC_Crafting_BoxClose.png",
 "circus_box_open.png": r"Res\UI\Spirits\ActvWorldCup\WC_Crafting_BoxOpen.png",
 "circus_icon_title.png": r"Res\UI\Spirits\Activity\deepsea_icon_title.png",
 "circus_medal_icon.png": r"Res\UI\Spirits\ItemIcons\icon_global_deepsea_orb.png",
 "circus_ticket_icon.png": r"Res\UI\Spirits\ItemIcons\icon_global_deepsea_treasuremap.png",
 "icon_global_circus_invitation.png": r"Res\UI\Spirits\ItemIcons\icon_global_deepsea_invitation.png",
 "icon_global_circustitle.png": r"Res\UI\Spirits\ItemIcons\icon_global_deepseatitle.png",
 "icon_island_Circus.png": r"Res\UI\Spirits\ItemIcons\icon_island_Egypt.png",
 "img_Activity_circus_box_icon.png": r"Res\UI\Spirits\ActivityImg\img_Activity_deepsea_turntable_icon.png",
 "img_Activity_circus_bp_bg_v2.png": r"Res\UI\Spirits\ActivityImg_Download\img_Activity_deepsea_bp_bg.png",
 "img_Activity_circus_bp_icon.png": r"Res\UI\Spirits\ActivityImg\img_Activity_deepsea_bp_icon.png",
 "img_Activity_circus_exchange_bg.png": r"Res\UI\Spirits\ActivityImg_Download\img_Activity_deepsea_exchange_bg.png",
 "img_Activity_circus_exchange_icon.png": r"Res\UI\Spirits\ActivityImg\img_Activity_deepsea_exchange_icon.png",
 "img_Activity_circus_fund_bg.png": r"Res\UI\Spirits\ActivityImg_Download\img_Activity_deepsea_fund_bg.png",
 "img_Activity_circus_fund_icon.png": r"Res\UI\Spirits\ActivityImg\img_Activity_deepsea_fund_icon.png",
 "img_Activity_circus_hud_icon.png": r"Res\UI\Spirits\Activity\img_Activity_deepsea_hud_icon.png",
 "img_Activity_circus_icon_decor.png": r"Res\UI\Spirits\ActivityImg_Download\img_Activity_deepsea_icon_decor.png",
 "img_Activity_circus_island_diamond.png": r"Res\UI\Spirits\ActvVoyage\img_Activity_deepsea_island_diamond.png",
 "img_Activity_circus_island_lucky.png": r"Res\UI\Spirits\ActvVoyage\img_Activity_deepsea_island_lucky.png",
 "img_Activity_circus_island_mystery.png": r"Res\UI\Spirits\ActvVoyage\img_Activity_deepsea_island_mystery.png",
 "img_Activity_circus_island_start.png": r"Res\UI\Spirits\ActvVoyage\img_Activity_deepsea_island_start.png",
 "img_Activity_circus_island_treasure.png": r"Res\UI\Spirits\ActvVoyage\img_Activity_deepsea_island_treasure.png",
 "img_Activity_circus_monopoly_bg.png": r"Res\UI\Spirits\ActvVoyage\img_Activity_Monopoly_deepsea_bg.png",
 "img_Activity_circus_puzzle.png": r"Res\UI\Spirits\ActvVoyage\img_Activity_navigation_bg_9.png",
 "img_Activity_circus_schedule_bg_v2.png": r"Res\UI\Spirits\ActivityImg_Download\img_Activity_deepsea_schedule_bg.png",
 "img_Activity_circus_schedule_icon.png": r"Res\UI\Spirits\ActivityImg\img_Activity_deepsea_schedule_icon.png",
 "img_Activity_circus_tavern_bg.png": r"Res\UI\Spirits\ActivityImg_Download\img_Activity_deepsea_tavern_bg.png",
 "img_Activity_circus_tavern_icon.png": r"Res\UI\Spirits\ActivityImg\img_Activity_deepsea_tavern_icon.png",
 "img_Activity_circus_visit_icon.png": r"Res\UI\Spirits\ActivityImg\img_Activity_deepsea_visit_icon.png",
 "img_Activity_circus_weekcard_bg.png": r"Res\UI\Spirits\ActivityImg_Download\img_Activity_deepsea_weekcard_bg.png",
 "img_Activity_circus_wishpool_bg.png": r"Res\UI\Spirits\ActivityImg_Download\img_Activity_deepsea_wishpool_bg.png",
 "img_Activity_circus_wishpool_fountain.png": r"Res\UI\Spirits\ActvWishingPool\img_Activity_deepsea_wishpool_fountain.png",
 "img_Activity_circus_wishpool_icon.png": r"Res\UI\Spirits\ActivityImg\img_Activity_deepsea_wishpool_icon.png",
 "img_Activity_icon_Monopoly_circus.png": r"Res\UI\Spirits\ActivityImg\img_Activity_icon_Monopoly_deepsea.png",
 "img_card_image_81.png": r"Res\UI\Spirits\MemorialCard\img_card_image_80.png",
}

GUID_RE = re.compile(r"^guid: [0-9a-f]{32}", re.M)

def new_guid(fn):
    return hashlib.md5(("circus2026_" + fn).encode()).hexdigest()

# 预载全部 Display asset 文本，供 namespace 反查
displays = {}
for f in os.listdir(DISPLAY_DIR):
    if f.endswith(".asset"):
        p = os.path.join(DISPLAY_DIR, f)
        displays[f] = io.open(p, encoding="utf-8").read()

def find_ns(anchor_key):
    pat = "- key: %s\n" % anchor_key
    for f, txt in displays.items():
        if pat in txt:
            return f
    return None

report = []
for fn, rel in sorted(MAPPING.items()):
    src = os.path.join(NORM, fn)
    anchor = os.path.join(CLIENT, rel)
    tgt = os.path.join(os.path.dirname(anchor), fn)
    assert os.path.exists(src), "规格化图缺失 " + fn
    assert os.path.exists(anchor) and os.path.exists(anchor + ".meta"), "锚点缺失 " + rel
    st = []
    # 1) 拷图
    if not os.path.exists(tgt):
        shutil.copy2(src, tgt); st.append("png✓")
    else:
        st.append("png已存在")
    # 2) meta 克隆（锚点 importer 设置原封，换 guid）
    if not os.path.exists(tgt + ".meta"):
        m = io.open(anchor + ".meta", encoding="utf-8").read()
        m2 = GUID_RE.sub("guid: " + new_guid(fn), m, count=1)
        assert m2 != m, "meta里没找到guid " + rel
        io.open(tgt + ".meta", "w", encoding="utf-8", newline="\n").write(m2)
        st.append("meta✓")
    else:
        st.append("meta已存在")
    # 3) DK 注册（锚点有 DK 才注册；guid 必须取 meta 实际值）
    anchor_key = os.path.splitext(os.path.basename(rel))[0]
    new_key = os.path.splitext(fn)[0]
    ns = find_ns(anchor_key)
    if ns is None:
        st.append("无DK(纯sprite引用)")
    else:
        txt = displays[ns]
        if ("- key: %s\n" % new_key) in txt:
            st.append("DK已注册@" + ns)
        else:
            # 取锚点条目块（key 行起，到下一个 "  - key:" 或字段块结束）
            i = txt.index("- key: %s\n" % anchor_key)
            blk_start = txt.rfind("\n", 0, i) + 1
            j = txt.find("\n  - key: ", i)
            blk_end = (j + 1) if j != -1 else len(txt)
            blk = txt[blk_start:blk_end]
            guid_actual = re.search(r"guid: ([0-9a-f]{32})", io.open(tgt + ".meta", encoding="utf-8").read()).group(1)
            nblk = blk.replace("- key: %s\n" % anchor_key, "- key: %s\n" % new_key)
            nblk = re.sub(r"guid: [0-9a-f]{32}", "guid: " + guid_actual, nblk)
            if not nblk.endswith("\n"):
                nblk += "\n"
                blk_end_txt = txt[:blk_end] + "\n"
                txt = blk_end_txt + txt[blk_end:]
                blk_end += 1
            txt = txt[:blk_end] + nblk + txt[blk_end:]
            displays[ns] = txt
            st.append("Display✓@" + ns)
        # Path 侧：⚠️paths=keys/values 平行字典（按下标配对），必须【成对】追加到两列表末尾。
        # 只插 keys 的光杆写法=全部DK下标错位事故（2026-07-17 血案，修复见 circus_dk_path_realign.py）
        pns = os.path.join(PATH_DIR, ns.replace("Display_", "Path_"))
        if os.path.exists(pns):
            lines = io.open(pns, encoding="utf-8").read().split("\n")
            dk_new = "DK_" + new_key
            if ("    - key: " + dk_new) in lines:
                st.append("Path已注册")
            else:
                ki, vi = lines.index("    keys:"), lines.index("    values:")
                obj_path = "Assets/" + os.path.relpath(tgt, CLIENT).replace("\\", "/")
                while lines and lines[-1] == "":
                    lines.pop()
                lines.insert(vi, "    - " + dk_new)          # keys 末尾（values: 行前）
                lines += ["    - key: " + dk_new, "      objPath: " + obj_path, ""]  # values 末尾成对
                io.open(pns, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
                st.append("Path✓")
        else:
            st.append("Path文件缺失!" + pns)
    report.append((fn, ns or "-", " ".join(st)))

# 回写 Display（内存改的统一落盘）
for f, txt in displays.items():
    p = os.path.join(DISPLAY_DIR, f)
    old = io.open(p, encoding="utf-8").read()
    if old != txt:
        io.open(p, "w", encoding="utf-8", newline="\n").write(txt)

for fn, ns, st in report:
    print("%-46s %-28s %s" % (fn, ns, st))
print("\n共", len(report), "项")
