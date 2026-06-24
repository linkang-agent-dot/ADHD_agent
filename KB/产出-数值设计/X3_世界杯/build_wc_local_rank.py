# -*- coding: utf-8 -*-
"""
世界杯开箱 本服排行榜 占位配置 (placeholder)
- 参考跨服排行榜 RankCfg 1005 + Reward组 30581-30587
- 新建 本服 RankCfg 1006 (RankType=6)，上榜需求(col14)=1000
- 数值数量级减少 (速度道具 ÷10)
- 核心奖励 皮肤5304001 -> 纪念卡180079(绿茵之星)
- 世界之巅头衔82004(跨服全球头衔) 在本服版剔除
- 挂到 ActvCrafting 1516 field[6] 本服排行榜
"""
import csv, sys, math, os

REPO = r"C:\x3\gdconfig"
DRY = "--apply" not in sys.argv

NEW_RANK = 1006
SLOT_START = 100424          # 7 个连续空闲档位
REW_ID_START = 40252         # Reward col0 起始(全表max=40251)
GRP_OFFSET = 10              # 30581 -> 30591

def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.reader(f, delimiter="\t"))

def width(rows):
    return max(len(r) for r in rows[:5])

def pad(r, w):
    return r + [""] * (w - len(r)) if len(r) < w else r

def append_rows(path, newrows):
    w = width(load(path))
    newrows = [pad(r, w) for r in newrows]
    # assert ids (col0) not present
    existing = set(r[0] for r in load(path)[5:] if r)
    for r in newrows:
        assert r[0] not in existing, f"ID {r[0]} 已存在于 {path}"
    if DRY:
        print(f"\n[DRY] {os.path.basename(path)} 追加 {len(newrows)} 行 (宽度{w}):")
        for r in newrows:
            print("   " + "\t".join(r))
        return
    # write LF
    with open(path, "a", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter="\t", lineterminator="\n")
        for r in newrows:
            wr.writerow(r)
    print(f"[OK] {os.path.basename(path)} +{len(newrows)} 行")

# ---------- 1. RankCfg 1006 ----------
rc_path = os.path.join(REPO, "tsv/Rank__RankCfg.tsv")
rc = load(rc_path)
src = next(r for r in rc[5:] if r and r[0] == "1005")
new = list(src)
new[0] = str(NEW_RANK)
new[1] = "活动-世界杯-开箱-本服积分排名"
new[2] = "本服排名"
new[3] = "6"          # RankType 12跨服 -> 6本服
new[14] = "1000"      # 上榜需求 (用户: 积分要求改到1000)
append_rows(rc_path, [new])

# ---------- 2. RankRewardSlotCfg ----------
slot_path = os.path.join(REPO, "tsv/Rank__RankRewardSlotCfg.tsv")
slot = load(slot_path)
# 1005 的 7 个档位, 按起始排名排序
src_slots = sorted([r for r in slot[5:] if len(r) > 1 and r[1] == "1005"],
                   key=lambda r: int(r[2]))
new_slots = []
for i, r in enumerate(src_slots):
    nr = list(r)
    nr[0] = str(SLOT_START + i)
    nr[1] = str(NEW_RANK)
    nr[4] = str(int(r[4]) + GRP_OFFSET)   # Reward组 30581->30591
    nr[5] = "世界杯-开箱-本服积分排名"
    new_slots.append(nr)
append_rows(slot_path, new_slots)

# ---------- 3. Reward 30591-30597 ----------
rew_path = os.path.join(REPO, "tsv/Reward__Reward.tsv")
rew = load(rew_path)
src_rows = [r for r in rew[5:] if len(r) > 1 and r[1].isdigit()
            and 30581 <= int(r[1]) <= 30587]
src_rows.sort(key=lambda r: (int(r[1]), r[0]))
new_rew = []
rid = REW_ID_START
for r in src_rows:
    item = r[3]
    if item == "82004":          # 世界之巅头衔: 本服版剔除
        continue
    nr = list(r)
    nr[0] = str(rid); rid += 1
    nr[1] = str(int(r[1]) + GRP_OFFSET)
    if item == "5304001":        # 皮肤 -> 纪念卡
        nr[3] = "180079"
        nr[4] = "绿茵之星（纪念卡）"
        nr[5] = "1"
    else:                        # 速度道具 数量级减少 ÷10 (向上取整, 最低1)
        old = int(r[5])
        nr[5] = str(max(1, int(old / 10 + 0.5)))
    if len(nr) > 11:
        nr[11] = (r[11] or "").replace("世界杯-抽奖", "世界杯-开箱-本服") or "世界杯-开箱-本服排名"
    new_rew.append(nr)
append_rows(rew_path, new_rew)

print("\n生成汇总: RankCfg 1006 / Slot %d-%d / Reward %d-%d (组30591-30597)"
      % (SLOT_START, SLOT_START+len(new_slots)-1, REW_ID_START, rid-1))
print("待执行: ActvCrafting 1516 field[6] = 1006  (本服排行榜挂载)")
