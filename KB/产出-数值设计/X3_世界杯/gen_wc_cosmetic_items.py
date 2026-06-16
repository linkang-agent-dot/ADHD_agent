# -*- coding: utf-8 -*-
"""批量生成世界杯自选宝箱所需道具/池/宝箱 → 暂存文件(供review后分批进gdconfig)。
读 cfg 表 + 克隆模板道具,产: 48框道具 + 48表情道具 + 2自选池(Reward组) + 2宝箱道具 + i18n。
ID段(已验空闲): 框道具80300-80347 / 表情道具15700-15747 / 宝箱1148-1149 /
               池组291201(框)/291202(表情) / Reward行号24565-24660。
"""
import io, sys, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = r"C:\x3\gdconfig"
ITEM = REPO + r"\tsv\Item__Item.tsv"
FRAMECFG = REPO + r"\tsv\Personalize__PersonalizeAvatarFrameCfg.tsv"
EMOCFG = REPO + r"\tsv\Emoticons__Emoticons.tsv"
REWARD = REPO + r"\tsv\Reward__Reward.tsv"
OUT = pathlib.Path(r"C:\ADHD_agent\KB\产出-数值设计\X3_世界杯\_stage_cosmetic")
OUT.mkdir(exist_ok=True)

def rows(path):
    return [ln.split('\t') for ln in pathlib.Path(path).read_text(encoding='utf-8').split('\n') if ln]

def find(path, idx, val):
    for r in rows(path):
        if len(r) > idx and r[idx] == val:
            return r
    return None

# 模板
item_rows = rows(ITEM)
def item_by_id(i):
    for r in item_rows:
        if r and r[0] == str(i): return r[:]
    raise SystemExit(f"模板道具{i}未找到")
TPL_FRAME = item_by_id(80010)   # ItemType9 框道具
TPL_EMOTE = item_by_id(15400)   # ItemType9 表情道具
TPL_CHEST = item_by_id(1080)    # ItemType20 自选盒
NCOL = len(TPL_FRAME)
rew_tpl = next(r for r in rows(REWARD) if len(r) > 1 and r[1] == "291101")  # Reward行模板
RNCOL = len(rew_tpl)

# 1) 读WC框cfg (col0=cfgID col4=DK col9=name) id 10028-10075
frames = []
for r in rows(FRAMECFG):
    if len(r) > 9 and r[4].startswith("DK_Img_Player_AvatarFrame_WC"):
        frames.append((r[0], r[4], r[9]))   # (cfgID, DK, name)
frames.sort(key=lambda x: int(x[0]))
# 2) 读WC表情cfg (col0=ID col1=DK_WC_{code} col6=备注名)
emotes = []
for r in rows(EMOCFG):
    if len(r) > 6 and r[1].startswith("DK_WC_"):
        code = r[1].replace("DK_WC_", "")
        nm = (r[6] or r[3]).replace("世界杯-", "").replace("[", "").replace("]", "")
        emotes.append((r[0], code, nm))     # (emoticonID, code, name)
emotes.sort(key=lambda x: int(x[0]))
assert len(frames) == 48 and len(emotes) == 48, f"框{len(frames)} 表情{len(emotes)}"

def mkitem(tpl, iid, name, desc, param, dk, sub="", obtain=""):
    r = tpl[:]; r[0] = str(iid); r[1] = name; r[2] = sub; r[3] = desc; r[8] = param; r[20] = dk
    if len(r) > 11: r[11] = obtain   # 清模板残留的获取说明
    return '\t'.join(r)

# 框道具 80300+
frame_items, frame_text = [], []
for i, (cfg, dk, nm) in enumerate(frames):
    iid = 80300 + i
    frame_items.append(mkitem(TPL_FRAME, iid, f"{nm}助威头像框", f"使用后永久获得「{nm}」世界杯助威头像框。", f"{cfg}|-1", dk, sub="头像框-世界杯", obtain="世界杯竞猜自选头像框宝箱获取"))
    frame_text.append((iid, f"{nm}助威头像框", f"使用后永久获得「{nm}」世界杯助威头像框。"))
# 表情道具 15700+
emote_items, emote_text = [], []
for i, (eid, code, nm) in enumerate(emotes):
    iid = 15700 + i
    emote_items.append(mkitem(TPL_EMOTE, iid, f"{nm}（表情）", f"使用后永久获得「{nm}」世界杯聊天表情。", str(eid), f"DK_icon_global_WC_{code}", sub="表情-世界杯", obtain="世界杯竞猜自选表情宝箱获取"))
    emote_text.append((iid, f"{nm}（表情）", f"使用后永久获得「{nm}」世界杯聊天表情。"))
# 宝箱道具
chests = [
    mkitem(TPL_CHEST, 1148, "世界杯自选助威头像框宝箱", "打开后，可在世界杯各队助威头像框中任选一个！", "291201", "DK_WC_AvatarFrameChest"),
    mkitem(TPL_CHEST, 1149, "世界杯自选助威表情宝箱",   "打开后，可在世界杯各队助威聊天表情中任选一个！", "291202", "DK_WC_EmoteChest"),
]
chest_text = [(1148, "世界杯自选助威头像框宝箱", "打开后，可在世界杯各队助威头像框中任选一个！"),
              (1149, "世界杯自选助威表情宝箱", "打开后，可在世界杯各队助威聊天表情中任选一个！")]

# 自选池 Reward组: 291201(框,行24565-24612) / 291202(表情,行24613-24660)
def mkrew(rowid, grp, item, name):
    r = rew_tpl[:]; r[0] = str(rowid); r[1] = str(grp); r[3] = str(item); r[4] = name; r[5] = "1"
    return '\t'.join(r)
pool = []
rid = 24565
for i, (cfg, dk, nm) in enumerate(frames):
    pool.append(mkrew(rid, 291201, 80300 + i, f"{nm}助威头像框")); rid += 1
for i, (eid, code, nm) in enumerate(emotes):
    pool.append(mkrew(rid, 291202, 15700 + i, f"{nm}（表情）")); rid += 1

# i18n Text行: 克隆Desc_1146结构(独立行)
txt_rows = [r for r in rows(REWARD)]  # placeholder
def write(name, lines):
    (OUT / name).write_text('\n'.join(lines) + '\n', encoding='utf-8')
write("frame_items.tsv", frame_items)
write("emote_items.tsv", emote_items)
write("chest_items.tsv", chests)
write("pools.tsv", pool)

# Text(name+desc): 用简单格式 TXT_Item_Name_{id}\tAI\t\t{zh}\t{en占位=zh}... 各语言列填中文(上线前翻译)
TEXT = REPO + r"\tsv\i18n\Text__Text.tsv"
ttpl = next(r for r in rows(TEXT) if r and r[0] == "TXT_Item_Desc_1134")
TCOL = len(ttpl)
def mktext(key, zh):
    r = [''] * TCOL; r[0] = key; r[1] = "AI"; r[3] = zh
    for c in range(4, min(19, TCOL)): r[c] = zh  # 各语言列先填中文,上线前x3-translation翻
    return '\t'.join(r)
alltext = []
for iid, nm, ds in frame_text + emote_text + chest_text:
    alltext.append(mktext(f"TXT_Item_Name_{iid}", nm))
    alltext.append(mktext(f"TXT_Item_Desc_{iid}", ds))
write("text.tsv", alltext)

print(f"暂存生成于 {OUT}")
print(f"框道具 {len(frame_items)} (80300-{80300+len(frame_items)-1})")
print(f"表情道具 {len(emote_items)} (15700-{15700+len(emote_items)-1})")
print(f"自选池 {len(pool)} 行 (组291201框48 + 组291202表情48, 行号24565-{rid-1})")
print(f"宝箱道具 {len(chests)} (1148框/1149表情)")
print(f"i18n Text {len(alltext)} 行")
print("--- 样本:框道具首行 ---"); print(frame_items[0])
print("--- 样本:表情道具首行 ---"); print(emote_items[0])
print("--- 样本:宝箱 ---"); print(chests[0])
print("--- 样本:池首行 ---"); print(pool[0])
