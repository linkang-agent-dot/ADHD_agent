# -*- coding: utf-8 -*-
"""马戏节收口扫描：c33族规/hub/FK/白名单/i18n残留（deepsea_scan 精简版，换节日可复用）"""
import io, os, sys
sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\x3\gdconfig-circus\tsv"

def rd(p):
    return io.open(os.path.join(BASE, p), encoding="utf-8", newline="").read().split("\n")

issues = []
# 1. 马戏 13 个 AO 的 c33/c38
ao = {ln.split("\t")[0]: ln.split("\t") for ln in rd("ActvOnline__ActvOnline.tsv") if ln.split("\t")[0].isdigit()}
CIRCUS = {"101026": ("1209|5302001", "142"), "100599": ("1209|1057", "142"), "102250": ("1209|1210", "142"),
          "102251": ("1057|1202", "143"), "102803": ("1057|1202", "143"), "101829": ("1057|1202", "143"),
          "102994": ("", "142"), "10071705": ("1209|1210", "142"), "106104": ("", "142"),
          "101343": ("1209|1210", "142"), "101344": ("1057|1202", "143"), "105606": ("1209|1057", "142"),
          "105014": ("1209|1210", "142")}
for aid, (c33, hub) in CIRCUS.items():
    if aid not in ao:
        issues.append("AO缺失:" + aid)
        continue
    r = ao[aid]
    if r[33] != c33:
        issues.append("AO%s c33=%s 预期%s" % (aid, r[33], c33))
    if r[38] != hub:
        issues.append("AO%s c38=%s 预期%s" % (aid, r[38], hub))
# 2. FK: Pack.content→Reward 组
rw_groups = set(ln.split("\t")[1] for ln in rd("Reward__Reward.tsv") if len(ln.split("\t")) > 1)
packs = {ln.split("\t")[0]: ln.split("\t") for ln in rd("Pack__Pack.tsv") if ln.split("\t")[0].isdigit()}
check_packs = ["211035", "211045", "13025", "13028", "800010", "800014", "211032", "211046",
               "130044", "130045", "130047", "130048", "280002"] + [str(x) for x in range(2801012, 2801023)]
for pid in check_packs:
    if pid not in packs:
        issues.append("Pack缺失:" + pid)
        continue
    c = packs[pid][13]
    if c and c not in rw_groups:
        issues.append("Pack%s content=%s 无Reward组" % (pid, c))
# 3. 白名单
wl = ao["100599"][49].split("|")
for pid in wl:
    if pid not in packs:
        issues.append("白名单包不存在:" + pid)
# 4. i18n
keys = {}
for ln in rd("i18n/Text__Text.tsv"):
    f = ln.split("\t")
    if len(f) > 4:
        for k in f[0].split("|"):
            keys[k] = f[3]
for aid in CIRCUS:
    for kind in ("ActvName", "ActvDesc"):
        k = "TXT_ActvOnline_%s_%s" % (kind, aid)
        if k not in keys:
            issues.append("i18n缺key:" + k)
        elif "深海" in keys[k] or "夏日" in keys[k]:
            issues.append("i18n残留:" + k + "=" + keys[k][:20])
TAGS = ("_1209", "_1210", "_1213", "_180081", "_82006", "_16043", "_16044", "_16045",
        "MainEntranceName_142", "MainEntranceName_143", "_101026", "_100599", "_2002", "_2003",
        "_211035", "_211036", "_13025", "_702", "_703", "Name_106", "Name_81", "Story_81",
        "_102250", "_102251", "_102803", "_101829", "_102994", "_10071705", "_106104",
        "_101343", "_101344", "_105606", "_105014", "_211046")
for k, cn in keys.items():
    for tag in TAGS:
        if k.endswith(tag) and ("深海" in cn or "藏宝图" in cn or "宝珠" in cn or "夏日" in cn):
            issues.append("key残留:" + k + "=" + cn[:25])
            break

# 5b. 马戏 Pack 名 key 残留扫(深海/夏日/尼罗词)
PACKNAME_KEYS = [k for k in keys if k.startswith("TXT_Pack_Name_") and any(k.endswith("_%d" % x) for x in list(range(211032, 211047)) + list(range(13025, 13029)) + list(range(800010, 800015)) + [130044, 130045, 130047, 130048] + list(range(2801012, 2801023)))]
for k in PACKNAME_KEYS:
    cn = keys[k]
    if any(w in cn for w in ("深海", "夏日", "尼罗", "海滨")):
        issues.append("Pack名残留:" + k + "=" + cn[:20])
# 5c. 拜访/装饰 Reward 组内深海门头/家具件残留
LEGACY_DECOR = {"152017", "152018", "152019", "151043"}
for ln in rd("Reward__Reward.tsv"):
    fl = ln.split("	")
    if len(fl) > 4 and fl[1] in ("211046", "211032", "211033", "211034") and fl[3] in LEGACY_DECOR:
        issues.append("门头/家具残留: 组" + fl[1] + "|" + fl[3])
print("== 马戏节收口扫描 ==")
if not issues:
    print("全绿 0 issue")
else:
    for x in issues:
        print("X", x)
print("白名单包数:", len(wl))
