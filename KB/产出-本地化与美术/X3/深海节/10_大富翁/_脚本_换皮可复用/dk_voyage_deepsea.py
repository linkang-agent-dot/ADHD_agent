# -*- coding: utf-8 -*-
"""深海大富翁 6个DK入库(Display+Path双补·纯追加不动现有条目)。--apply 才落盘。"""
import sys, os, re, shutil, uuid
APPLY = "--apply" in sys.argv
CLIENT = r"C:\x3-project\client"
FIN = r"C:\ADHD_agent\KB\产出-本地化与美术\X3\深海节\10_大富翁\_FINAL_正式版"
SPR = r"Assets\Res\UI\Spirits\ActvVoyage"          # 落仓子目录(objPath用正斜杠)
SPR_FS = os.path.join(CLIENT, "Assets", "Res", "UI", "Spirits", "ActvVoyage")
DISPLAY = os.path.join(CLIENT, "Assets", "Editor", "Config", "DisplayKey", "Display_Activity.asset")
PATH    = os.path.join(CLIENT, "Assets", "Res", "Config", "DisplayKey", "Path_Activity.asset")
META_TPL = os.path.join(SPR_FS, "img_Activity_icon_island_4.png.meta")

# 源中文文件 -> 目标名(无.png) -> DK key(=img_前缀)   按lower()排序后的顺序
ASSETS = [
    ("02_岛_钻石_蓝水晶(复用island_2_lv5)_184x224.png", "img_Activity_deepsea_island_diamond"),
    ("05_岛_幸运_珊瑚宝箱_184x224.png",                  "img_Activity_deepsea_island_lucky"),
    ("04_岛_神秘_珊瑚问号_184x224.png",                  "img_Activity_deepsea_island_mystery"),
    ("01_岛_起始_潜艇基地_184x224.png",                  "img_Activity_deepsea_island_start"),
    ("03_岛_宝藏_代币_184x224.png",                      "img_Activity_deepsea_island_treasure"),
    ("00_地图_深海_540x960.png",                         "img_Activity_Monopoly_deepsea_bg"),
]

def new_guid(): return uuid.uuid4().hex

# ---- 1) 拷png + 生成meta ----
tpl = open(META_TPL, "r", encoding="utf-8").read()
guids = {}
plan = []
for src, name in ASSETS:
    sp = os.path.join(FIN, src)
    assert os.path.exists(sp), f"源缺失: {sp}"
    dst_png = os.path.join(SPR_FS, name + ".png")
    g = new_guid()
    guids[name] = g
    meta = re.sub(r"^guid: [0-9a-f]{32}", "guid: " + g, tpl, count=1, flags=re.M)
    meta = re.sub(r"spriteID: [0-9a-f]{32}", "spriteID: " + new_guid(), meta, count=1)
    plan.append((sp, dst_png, dst_png + ".meta", meta, name, g))
    print(f"  {name}.png  guid={g}  <- {src}")

# ---- 2) Display_Activity 追加(EOF·list顺序无所谓) ----
disp = open(DISPLAY, "rb").read().decode("utf-8")
disp_eol = "\r\n" if "\r\n" in disp else "\n"
disp_add = "".join(
    f"  - key: {name}{disp_eol}    type: Activity{disp_eol}    desc: {disp_eol}    guid: {guids[name]}{disp_eol}    exportCode: 0{disp_eol}"
    for _, name in ASSETS)
disp_new = (disp if disp.endswith(disp_eol) else disp + disp_eol) + disp_add

# ---- 3) Path_Activity 纯追加(keys段末/values段末·同序) ----
praw = open(PATH, "rb").read().decode("utf-8")
peol = "\r\n" if "\r\n" in praw else "\n"
plines = praw.split(peol)
# 定位 keys段末 = "    values:" 行
vi = next(i for i, l in enumerate(plines) if l.strip() == "values:" and l.startswith("    "))
key_block = [f"    - DK_{name}" for _, name in ASSETS]
val_block = []
for _, name in ASSETS:
    val_block.append(f"    - key: DK_{name}")
    val_block.append(f"      objPath: {SPR}/{name}.png".replace("\\", "/"))
# 末尾空行处理: 在EOF追加values
# 插入keys块 at vi(values:行之前)
new_plines = plines[:vi] + key_block + plines[vi:]
# 找新的EOF(去掉末尾空串)
while new_plines and new_plines[-1] == "":
    tail_empty = new_plines.pop()
new_plines += val_block
path_new = peol.join(new_plines) + peol

print(f"\n[Display] +{len(ASSETS)} 条目")
print(f"[Path] +{len(key_block)} keys, +{len(ASSETS)} values")
print("\nDK列表:", [f"DK_{n}" for _, n in ASSETS])

if APPLY:
    for sp, dpng, dmeta, meta, name, g in plan:
        shutil.copyfile(sp, dpng)
        open(dmeta, "w", encoding="utf-8", newline="").write(meta)
    open(DISPLAY, "wb").write(disp_new.encode("utf-8"))
    open(PATH, "wb").write(path_new.encode("utf-8"))
    print("\n*** APPLIED ***")
else:
    print("\n--- DRY-RUN (--apply 落盘) ---")
