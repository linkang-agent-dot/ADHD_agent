# -*- coding: utf-8 -*-
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

SSID = "1B46X-aWpv0DXL9Q_sBvUkNBdLIw34wMPTnOLKQnPNOw"
SHEET = "换皮后数值"

def gws_update(range_str, values, mode="RAW"):
    cmd = json.dumps({
        "args": ["sheets","spreadsheets","values","update",
            "--params", json.dumps({
                "spreadsheetId": SSID,
                "range": f"'{SHEET}'!{range_str}",
                "valueInputOption": mode
            }),
            "--json", json.dumps({"values": values})
        ]
    }, ensure_ascii=False)
    r = subprocess.run(["node","C:/ADHD_agent/scripts/gws_stdin.js"],
        input=cmd, capture_output=True, text=True, encoding='utf-8')
    ok = r.returncode == 0
    resp = json.loads(r.stdout) if r.stdout.strip() else {}
    print(f"  {'OK' if ok else 'FAIL'}: {range_str} ({resp.get('updatedCells','?')})")
    return ok

def write_rows(rows, start, chunk=25):
    for i in range(0, len(rows), chunk):
        batch = rows[i:i+chunk]
        r1 = start + i
        r2 = r1 + len(batch) - 1
        if not gws_update(f"A{r1}:K{r2}", batch):
            for j, row in enumerate(batch):
                gws_update(f"A{r1+j}:K{r1+j}", [row])

# ════════════════════════════════════════════
# 1. 更新奖励明细 (覆盖 row 41 起)
# ════════════════════════════════════════════
print("=== 1. Updating reward detail (row 41+) ===")

reward_rows = []
reward_rows.append(["", "格位", "层级", "每抽消耗", "奖励内容", "数量", "道具id", "道具类型", "单价", "格价值", "层合计/标记"])

# L1 (6格, 1tok)
reward_rows.append(["", "L1-1", "L1", "1tok($6)", "8h训练加速", "5", "11111158", "分钟（训练）", "$3.63", "$18.15", "升层"])
reward_rows.append(["", "L1-2", "L1", "1tok($6)", "机甲经验-50000", "40", "11118004", "机甲经验", "$0.42", "$16.80", ""])
reward_rows.append(["", "L1-3", "L1", "1tok($6)", "机能核心", "27", "11118501", "机能核心", "$0.62", "$16.74", ""])
reward_rows.append(["", "L1-4", "L1", "1tok($6)", "资源宝箱10w", "130", "11114330", "粮食", "$0.13", "$16.90", ""])
reward_rows.append(["", "L1-5", "L1", "1tok($6)", "8h训练加速", "5", "11111158", "分钟（训练）", "$3.63", "$18.15", ""])
reward_rows.append(["", "L1-6", "L1", "1tok($6)", "机甲经验-50000", "40", "11118004", "机甲经验", "$0.42", "$16.80", "降层"])
reward_rows.append(["", "", "", "", "", "", "", "L1合计 (6格×1tok=6tok/$33)", "", "$103.54", ""])
reward_rows.append([])

# L2 (5格, 2tok)
reward_rows.append(["", "L2-1", "L2", "2tok($11)", "机能核心", "50", "11118501", "机能核心", "$0.62", "$31.00", "升层"])
reward_rows.append(["", "L2-2", "L2", "2tok($11)", "8h训练加速", "8", "11111158", "分钟（训练）", "$3.63", "$29.04", ""])
reward_rows.append(["", "L2-3", "L2", "2tok($11)", "机甲经验-50000", "70", "11118004", "机甲经验", "$0.42", "$29.40", ""])
reward_rows.append(["", "L2-4", "L2", "2tok($11)", "机能核心", "50", "11118501", "机能核心", "$0.62", "$31.00", ""])
reward_rows.append(["", "L2-5", "L2", "2tok($11)", "8h训练加速", "8", "11111158", "分钟（训练）", "$3.63", "$29.04", "降层"])
reward_rows.append(["", "", "", "", "", "", "", "L2合计 (5格×2tok=10tok/$55)", "", "$149.48", ""])
reward_rows.append([])

# L3 (4格, 5tok)
reward_rows.append(["", "L3-1", "L3", "5tok($28)", "机能核心", "75", "11118501", "机能核心", "$0.62", "$46.50", "升层"])
reward_rows.append(["", "L3-2", "L3", "5tok($28)", "成长线宝箱自选2", "23", "11119797", "玩家自选", "$2.00", "$46.00", ""])
reward_rows.append(["", "L3-3", "L3", "5tok($28)", "24小时加速", "4", "11111109", "分钟（通用）", "$10.89", "$43.56", ""])
reward_rows.append(["", "L3-4", "L3", "5tok($28)", "机能核心", "75", "11118501", "机能核心", "$0.62", "$46.50", "降层"])
reward_rows.append(["", "", "", "", "", "", "", "L3合计 (4格×5tok=20tok/$110)", "", "$182.56", ""])
reward_rows.append([])

# L4 (3格, 10tok)
reward_rows.append(["", "L4-1", "L4", "10tok($55)", "成长线宝箱自选2", "56", "11119797", "玩家自选", "$2.00", "$112.00", "升层"])
reward_rows.append(["", "L4-2", "L4", "10tok($55)", "机能核心", "175", "11118501", "机能核心", "$0.62", "$108.50", ""])
reward_rows.append(["", "L4-3", "L4", "10tok($55)", "24小时加速", "10", "11111109", "分钟（通用）", "$10.89", "$108.90", "降层"])
reward_rows.append(["", "", "", "", "", "", "", "L4合计 (3格×10tok=30tok/$165)", "", "$329.40", ""])
reward_rows.append([])

# L5 (2格, 18tok)
reward_rows.append(["", "L5-1", "L5", "18tok($99)", "万能英雄碎片-橙色", "95", "11116304", "通用碎片（橙）", "$2.50", "$237.50", "升层"])
reward_rows.append(["", "L5-2", "L5", "18tok($99)", "机能核心", "380", "11118501", "机能核心", "$0.62", "$235.60", "降层"])
reward_rows.append(["", "", "", "", "", "", "", "L5合计 (2格×18tok=36tok/$198)", "", "$473.10", ""])
reward_rows.append([])

# L6 (1格, 25tok)
reward_rows.append(["", "L6-1", "L6", "25tok($138)", "机甲皮肤(自选)", "1", "11112330", "机甲皮肤", "", "", ""])
reward_rows.append([])

reward_rows.append(["", "", "", "", "", "", "", "总计 (21格, 127tok, $698.50)", "", "$1,238.08", "ROI 1.77"])
reward_rows.append([])

# 养成线投放比例
reward_rows.append(["", "养成线投放比例"])
reward_rows.append(["", "养成线", "道具", "价值", "占比", "vs养成手册(超R)"])
reward_rows.append(["", "机甲", "机能核心832 + 机甲经验190组", "$549", "44.3%", "手册18.8% — 机甲主题合理偏高"])
reward_rows.append(["", "英雄", "万能橙碎95", "$237", "19.2%", "手册18.3% — 基本吻合"])
reward_rows.append(["", "玩家自选", "成长线宝箱79个", "$158", "12.8%", "覆盖装备/战车/机师/收藏品"])
reward_rows.append(["", "SLG通用", "加速26+14 + 资源130", "$264", "21.3%", "基础建设"])
reward_rows.append(["", "", "不含皮肤合计", "$1,238", "ROI 1.77", ""])
reward_rows.append([])
reward_rows.append([])

write_rows(reward_rows, 41)
print(f"  Reward section: {len(reward_rows)} rows from R41 to R{41+len(reward_rows)-1}")

# ════════════════════════════════════════════
# 2. 更新总付费产出 (row 91 起)
# ════════════════════════════════════════════
print("\n=== 2. Updating item totals (row 91+) ===")

totals_rows = []
totals_rows.append(["总付费产出"])
totals_rows.append([])
totals_rows.append(["", "", "道具", "数量", "价值", "占比", "说明"])
totals_rows.append(["", "", "机能核心", "832", "$517", "41.8%", "L1-27+L2-100+L3-150+L4-175+L5-380"])
totals_rows.append(["", "", "万能英雄碎片-橙色", "95", "$237", "19.2%", "L5-95"])
totals_rows.append(["", "", "成长线宝箱自选2", "79", "$158", "12.8%", "L3-23+L4-56 (新增)"])
totals_rows.append(["", "", "24小时加速", "14", "$152", "12.3%", "L3-4+L4-10"])
totals_rows.append(["", "", "8h训练加速", "26", "$94", "7.6%", "L1-10+L2-16"])
totals_rows.append(["", "", "机甲经验(5w)", "150", "$63", "5.1%", "L1-80+L2-70"])
totals_rows.append(["", "", "资源宝箱10w", "130", "$17", "1.3%", "L1-130"])
totals_rows.append(["", "", "合计", "", "$1,238", "100%", "ROI 1.77"])
totals_rows.append([])
totals_rows.append([])

write_rows(totals_rows, 91)

# ════════════════════════════════════════════
# 3. 更新模拟结果区的ROI (row 105 附近)
# ════════════════════════════════════════════
print("\n=== 3. Updating ROI in summary (row 28-30) ===")

gws_update("C29:C30", [["$698.50"],["1.77"]])

# ════════════════════════════════════════════
# 4. 更新礼包限购 (row 141, 144, 148)
# ════════════════════════════════════════════
print("\n=== 4. Updating package limits ===")

# Row 141: $4.99 限购 → 2 (was already 2, just confirming)
# Row 144: $19.99固定 限购 2→1
gws_update("D144:D144", [["1"]])
# The package total estimate also changes slightly
gws_update("A153:G155", [
    ["", "", "", "", "一次性礼包", "~47", "$249.92"],
    ["", "", "", "", "续杯补齐（满抽127tok）", "~80", "$499.95"],
    ["", "", "", "", "总计（满抽）", "~127", "$749.87"],
])

# Update purchase path estimates
gws_update("A159:G161", [
    ["", "运气好(P10)", "12", "~70", "$249.92", "$199.98(2次)", "~$450"],
    ["", "中位数(P50)", "18", "~105", "$249.92", "$299.97(3次)", "~$550"],
    ["", "运气差(P90)", "21", "127", "$249.92", "$499.95(5次)", "~$750"],
])

# ════════════════════════════════════════════
# 5. 更新vs对比表 (row 122+)
# ════════════════════════════════════════════
print("\n=== 5. Updating comparison table ===")

comp_rows = []
comp_rows.append(["vs 老系统对比"])
comp_rows.append([])
comp_rows.append(["", "指标", "老Gacha", "新金字塔"])
comp_rows.append(["", "总奖励价值", "$1,085", "$1,238"])
comp_rows.append(["", "平均花费", "~$665", "~$550"])
comp_rows.append(["", "花费范围", "$620-$710", "$450-$750"])
comp_rows.append(["", "ROI（满抽）", "1.77", "1.77"])
comp_rows.append(["", "前$200体验", "5/12抽", "~13抽到L4"])
comp_rows.append(["", "每格结构", "多道具组合", "单道具/格"])
comp_rows.append(["", "新增道具", "-", "成长线宝箱自选2 (79个, $158)"])
comp_rows.append(["", "说明", "所有人固定12抽", "运气好$450搞定，运气差$750满抽补偿更多奖励"])

write_rows(comp_rows, 122)

print("\n=== All updates complete! ===")
