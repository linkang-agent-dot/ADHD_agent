# -*- coding: utf-8 -*-
"""从 X3 工程 Spirits/ 只读拷贝 v2 出图需要的官方 sprite → _src2/assets/x3/
   同时导出 sprite → spriteBorder 映射（Unity L,B,R,T）到 borders.json
   另把 03_横转竖demo\demo美术资源包 的 P2 玩法图素 + demo 抽出的 assets 也软拷进来（只读源）"""
import os, sys, json, shutil, re

HERE = os.path.dirname(os.path.abspath(__file__))
IDX = json.load(open(os.path.join(HERE, "_guid_index.json"), encoding="utf-8"))
ASSETS = r"C:\x3-project\client\Assets"
OUT = os.path.join(HERE, "assets", "x3")
os.makedirs(OUT, exist_ok=True)

WANT = """
img_cm_bg_tanchu img_cm_biaoti img_cm_bg_1 img_cm_bg_2
img_ledger_bg_taizhang1 img_ledger_bg_taizhangliebiao
img_ledger_anniu_taizhang_fenye img_ledger_anniu_taizhang_fenye2
img_gift_bg_7 img_gift_bg_tc_3 img_gift_bg_tc_5 img_gift_bg_tc_8 img_gift_bg_17
img_cm_anniu3_geen img_cm_anniu1_geen img_cm_anniu_gold img_cm_anniu3_blue img_cm_anniu1_blue
img_gift_bg_Discount img_gift_line img_cm_bg_ditu5 img_cm_bg_biaoti2
img_gift_bg_4 img_gift_time img_cm_anniu_guize img_cm_zhizuo_guanbianniu img_cm_anniu_return
img_Activity_rank_bg01 img_Activity_rank_bg02 img_Activity_rank_box04 img_Activity_rank_box05
img_Activity_rank_box07 img_Activity_rank_icon01 img_rank_toyxiangkuang
img_cm_rankbg_icon_1st img_cm_rankbg_icon_2ed img_cm_rankbg_icon_3th
img_cm_rank_icon_1st img_cm_rank_icon_2ed img_cm_rank_icon_3th
img_TXDS_jindutiao1 img_TXDS_jindutiao2 img_VIP_bg_jindutiao_1
img_idle_shouyi_shijian1 img_idle_shouyi_shijian2 img_idle_bg_fenggexian
im_bm_bg_13 img_ledger_bg_ditu1 img_ledger_anniu_jiantou2 img_heros_line img_hs_bg_1
img_chouka_kuang img_cm_bg_iconkuang img_cm_bg_iconkuang_gold img_cm_bg_icon_touxiangkuang1
ui_Howtogetit_bg_2 ui_Howtogetit_bg_3 ui_Howtogetit_bg_4 ui_Howtogetit_bg_6
ui_Howtogetit_piggybank_3 ui_piggybank_JDT_1 ui_piggybank_JDT_2 ui_Howtogetit_icon
img_Activity_schedule_btn_1 img_Activity_schedule_btn_2 img_Activity_bg_05
img_TXDS_icon_rank img_TXDS_icon_gou icon_global_integral img_cm_icon_integral
img_gift_bg_5 img_gift_bg_31 img_shop_bg_8 img_Activity_bg_integral_5
img_Activity_woodenstake_jdt_1 img_gift_icon_4 img_TXDS_bg_2
img_Activity_arrow_1 img_Activity_arrow_2 img_Activity_arrow_3 img_Activity_arrow_4
img_cm_hongdian img_cm_bg_ziyuan img_cm_bg_ziyuan3 img_route_icon_lock img_remember_icon_lock
img_Activity_navigation_bg_2 img_Activity_rank_bg03 img_battlepass_bg_2
img_Activity_icon_integral_1 img_Activity_icon_integral_2 img_Activity_icon_integral_3
img_Activity_bg_integral_2 img_Activity_bg_integral_3 img_Activity_bg_integral_4
img_Activity_bg_integral_6 img_Activity_bg_integral_7 img_Activity_bg_integral_8
img_dtc_btn_+ img_cm_bg_kuang4 img_cm_biaoti2
img_multi_tier_buy_bg1 img_multi_tier_buy_bg2 img_multi_tier_buy_table
img_multi_tier_buy_btn_close img_multi_tier_buy_free_icon
ui_battlepass_point_1 ui_battlepass_point_2 img_battlepass_icon_lock
img_TXDS_pd_5 img_TXDS_pd_1 icon_global_gold1
ChainPackBg1 ChainPackBg2 ChainPacktag3 ui_giftpack_img_soldout ui_giftpack_title
img_gift_bg_68 common_gradient ui_battlepass_bg_4 img_route_bg_4
""".split()

byname = {}
for g, v in IDX.items():
    byname.setdefault(v["name"], []).append(v)

borders = {}
ok, miss = [], []
for w in WANT:
    cands = [v for v in byname.get(w, []) if "/Spirits/" in v["path"] or "/Atlas/" in v["path"]]
    if not cands:
        miss.append(w)
        continue
    v = cands[0]
    src = os.path.join(ASSETS, v["path"].replace("Assets/", "").replace("/", os.sep))
    if not os.path.isfile(src):
        miss.append(w + "(file?)")
        continue
    dst = os.path.join(OUT, os.path.basename(src))
    shutil.copyfile(src, dst)
    b = v.get("border") or [0, 0, 0, 0]
    borders[w] = {"file": "assets/x3/" + os.path.basename(src),
                  "unity_LBRT": b,
                  # CSS border-image-slice = 上 右 下 左
                  "css_TRBL": [int(b[3]), int(b[2]), int(b[1]), int(b[0])],
                  "src": v["path"]}
    ok.append(w)

json.dump(borders, open(os.path.join(HERE, "borders.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
sys.stdout.reconfigure(encoding="utf-8")
print("copied %d, missing %d: %s" % (len(ok), len(miss), miss))
