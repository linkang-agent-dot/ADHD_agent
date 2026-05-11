# -*- coding: utf-8 -*-
"""Complete rebuild of 换皮后数值 sheet with clean layout + formatting."""
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

SSID = "1B46X-aWpv0DXL9Q_sBvUkNBdLIw34wMPTnOLKQnPNOw"
SHEET = "换皮后数值"
SHEET_GID = 531423017

def gws(args_list):
    cmd = json.dumps({"args": args_list}, ensure_ascii=False)
    r = subprocess.run(["node","C:/ADHD_agent/scripts/gws_stdin.js"],
        input=cmd, capture_output=True, text=True, encoding='utf-8')
    return r.returncode == 0, r.stdout.strip()

def values_update(rng, vals, mode="RAW"):
    ok, out = gws(["sheets","spreadsheets","values","update",
        "--params", json.dumps({"spreadsheetId":SSID,"range":f"'{SHEET}'!{rng}","valueInputOption":mode}),
        "--json", json.dumps({"values":vals})])
    return ok

def batch_update(requests):
    ok, out = gws(["sheets","spreadsheets","batchUpdate",
        "--params", json.dumps({"spreadsheetId":SSID}),
        "--json", json.dumps({"requests":requests})])
    if not ok: print(f"  batchUpdate FAIL: {out[:200]}")
    return ok

def values_clear(rng):
    ok, out = gws(["sheets","spreadsheets","values","clear",
        "--params", json.dumps({"spreadsheetId":SSID,"range":f"'{SHEET}'!{rng}"}),
        "--json", "{}"])
    return ok

# ════════════════════════════════════════
# Step 1: Clear entire sheet
# ════════════════════════════════════════
print("Step 1: Clearing sheet...")
values_clear("A1:Z300")
print("  Cleared.")

# ════════════════════════════════════════
# Step 2: Build all rows
# ════════════════════════════════════════
print("Step 2: Building content...")

E = []  # empty row
rows = []

# ── Section 1: 设计思路 (R1-4) ──
rows.append(["设计思路"])                                    # R1
rows.append(E)
rows.append(["", "活动类型", "核心针对人群", "持续时长（h）", "上线频次", "排行榜范围", "能力值", "核心投放"])
rows.append(["", "付费活动", "超R", "", "", "-", "-", "机甲皮肤"])
rows.append(E)                                              # R5

# ── Section 2: 数值目录 (R6-12) ──
rows.append(["数值目录"])                                    # R6
rows.append(E)
rows.append(["", "序号", "数值名称", "内容", "本次是否有变化", "改动内容"])
rows.append(["", "1", "金字塔结构", "6层(6-5-4-3-2-1)，层消耗递增", "有", "新机制"])
rows.append(["", "2", "礼包设计", "锤子道具投放", "有", "沿用+微调限购"])
rows.append(["", "3", "奖励设计", "每格单道具投放", "有", "新增成长线宝箱自选2"])
rows.append(["", "4", "阶段奖励", "集齐4升层道具触发1次", "有", "新增"])
rows.append(E)                                              # R13

# ── Section 3: 金字塔结构 (R14-25) ──
rows.append(["金字塔结构"])                                  # R14
rows.append(E)
rows.append(["", "层级", "格数", "消耗/抽(tok)", "花费/抽($)", "层合计tok", "层合计$", "主要投放"])
rows.append(["", "L1 底层", "6", "1", "$5.50", "6", "$33.00", "训练加速+机甲经验+资源"])
rows.append(["", "L2", "5", "2", "$11.00", "10", "$55.00", "机能核心+训练加速+机甲经验"])
rows.append(["", "L3", "4", "5", "$27.50", "20", "$110.00", "机能核心+成长线宝箱+24h加速"])
rows.append(["", "L4", "3", "10", "$55.00", "30", "$165.00", "成长线宝箱+核心+24h加速"])
rows.append(["", "L5", "2", "18", "$99.00", "36", "$198.00", "橙碎+机能核心"])
rows.append(["", "L6 顶层", "1", "25", "$137.50", "25", "$137.50", "机甲皮肤(自选)"])
rows.append(["", "合计", "21", "", "", "127", "$698.50", ""])
rows.append(["", "", "", "", "", "", "", "Token单价 $5.50 | 满抽ROI 1.77"])
rows.append(E)                                              # R26

# ── Section 4: 奖励明细 (R27-72) ──
rows.append(["奖励明细（每格单道具）"])                        # R27
rows.append(E)
rows.append(["", "基本定价：600刀一个机甲皮肤，金字塔爬塔，ROI 1.77"])
rows.append(["", "投放思路：机甲+SLG+万能橙为主，新增成长线宝箱自选覆盖装备/战车/机师/收藏品"])
rows.append(E)
rows.append(["", "格位", "层级", "消耗", "奖励内容", "数量", "道具id", "单价", "格价值", "标记"])

# L1
rows.append(["", "L1-1", "L1", "1tok($6)", "8h训练加速", "5", "11111158", "$3.63", "$18.15", "升层"])
rows.append(["", "L1-2", "L1", "", "机甲经验-50000", "40", "11118004", "$0.42", "$16.80", ""])
rows.append(["", "L1-3", "L1", "", "机能核心", "27", "11118501", "$0.62", "$16.74", ""])
rows.append(["", "L1-4", "L1", "", "资源宝箱10w", "130", "11114330", "$0.13", "$16.90", ""])
rows.append(["", "L1-5", "L1", "", "8h训练加速", "5", "11111158", "$3.63", "$18.15", ""])
rows.append(["", "L1-6", "L1", "", "机甲经验-50000", "40", "11118004", "$0.42", "$16.80", "降层"])
rows.append(["", "", "", "", "", "", "", "L1 合计 (6tok/$33)", "$103.54", ""])

# L2
rows.append(["", "L2-1", "L2", "2tok($11)", "机能核心", "50", "11118501", "$0.62", "$31.00", "升层"])
rows.append(["", "L2-2", "L2", "", "8h训练加速", "8", "11111158", "$3.63", "$29.04", ""])
rows.append(["", "L2-3", "L2", "", "机甲经验-50000", "70", "11118004", "$0.42", "$29.40", ""])
rows.append(["", "L2-4", "L2", "", "机能核心", "50", "11118501", "$0.62", "$31.00", ""])
rows.append(["", "L2-5", "L2", "", "8h训练加速", "8", "11111158", "$3.63", "$29.04", "降层"])
rows.append(["", "", "", "", "", "", "", "L2 合计 (10tok/$55)", "$149.48", ""])

# L3
rows.append(["", "L3-1", "L3", "5tok($28)", "机能核心", "75", "11118501", "$0.62", "$46.50", "升层"])
rows.append(["", "L3-2", "L3", "", "成长线宝箱自选2", "23", "11119797", "$2.00", "$46.00", ""])
rows.append(["", "L3-3", "L3", "", "24小时加速", "4", "11111109", "$10.89", "$43.56", ""])
rows.append(["", "L3-4", "L3", "", "机能核心", "75", "11118501", "$0.62", "$46.50", "降层"])
rows.append(["", "", "", "", "", "", "", "L3 合计 (20tok/$110)", "$182.56", ""])

# L4
rows.append(["", "L4-1", "L4", "10tok($55)", "成长线宝箱自选2", "56", "11119797", "$2.00", "$112.00", "升层"])
rows.append(["", "L4-2", "L4", "", "机能核心", "175", "11118501", "$0.62", "$108.50", ""])
rows.append(["", "L4-3", "L4", "", "24小时加速", "10", "11111109", "$10.89", "$108.90", "降层"])
rows.append(["", "", "", "", "", "", "", "L4 合计 (30tok/$165)", "$329.40", ""])

# L5
rows.append(["", "L5-1", "L5", "18tok($99)", "万能英雄碎片-橙色", "95", "11116304", "$2.50", "$237.50", "升层"])
rows.append(["", "L5-2", "L5", "", "机能核心", "380", "11118501", "$0.62", "$235.60", "降层"])
rows.append(["", "", "", "", "", "", "", "L5 合计 (36tok/$198)", "$473.10", ""])

# L6
rows.append(["", "L6-1", "L6", "25tok($138)", "机甲皮肤(自选)", "1", "11112330", "", "", ""])
rows.append(E)
rows.append(["", "", "", "", "", "", "", "总计 21格 127tok $698.50", "$1,238.08", "ROI 1.77"])
rows.append(E)

# 养成线投放比例
rows.append(["", "养成线投放比例"])
rows.append(["", "养成线", "主要道具", "价值", "占比", "参考"])
rows.append(["", "机甲", "机能核心832+机甲经验190组", "$549", "44.3%", "手册18.8%—机甲主题合理偏高"])
rows.append(["", "英雄", "万能橙碎95", "$237", "19.2%", "手册18.3%—基本吻合"])
rows.append(["", "玩家自选", "成长线宝箱79个", "$158", "12.8%", "覆盖装备/战车/机师/收藏品"])
rows.append(["", "SLG通用", "加速14+26件+资源130", "$264", "21.3%", "基础建设"])
rows.append(["", "合计(不含皮肤)", "", "$1,238", "ROI 1.77", ""])
rows.append(E)                                              # ~R72

# ── Section 5: 总付费产出 (R73-84) ──
rows.append(["总付费产出"])
rows.append(E)
rows.append(["", "道具", "数量", "价值", "占比", "分布"])
rows.append(["", "机能核心", "832", "$519", "41.9%", "L1-27 L2-100 L3-150 L4-175 L5-380"])
rows.append(["", "万能英雄碎片-橙色", "95", "$237", "19.2%", "L5-95"])
rows.append(["", "成长线宝箱自选2", "79", "$158", "12.8%", "L3-23 L4-56"])
rows.append(["", "24小时加速", "14", "$152", "12.3%", "L3-4 L4-10"])
rows.append(["", "8h训练加速", "26", "$94", "7.6%", "L1-10 L2-16"])
rows.append(["", "机甲经验(5w)", "150", "$63", "5.1%", "L1-80 L2-70"])
rows.append(["", "资源宝箱10w", "130", "$17", "1.3%", "L1-130"])
rows.append(["", "合计", "", "$1,238", "100%", "ROI 1.77"])
rows.append(E)                                              # ~R85

# ── Section 6: 模拟结果 (R86-103) ──
rows.append(["模拟结果（20万次）"])
rows.append(E)
rows.append(["", "指标", "P10", "P25", "P50", "P75", "P90", "avg"])
rows.append(["", "抽数", "12", "15", "18", "20", "21", "16.9"])
rows.append(["", "花费($)", "434", "506", "594", "671", "698", "578"])
rows.append(["", "奖励价值($)", "656", "794", "996", "1166", "1238", "967"])
rows.append(["", "ROI", "1.51", "1.59", "1.66", "1.76", "1.77", "1.66"])
rows.append(E)

rows.append(["", "逐层累计体验（顺利一路升层）"])
rows.append(["", "进度", "累计花费", "累计价值", "累计ROI"])
rows.append(["", "清完L1", "$33", "$104", "3.14"])
rows.append(["", "清完L2", "$88", "$253", "2.88"])
rows.append(["", "清完L3", "$198", "$436", "2.20"])
rows.append(["", "清完L4", "$363", "$765", "2.11"])
rows.append(["", "清完L5", "$561", "$1,238", "2.21"])
rows.append(["", "出皮肤", "$698", "", "满抽"])
rows.append(E)                                              # ~R103

# ── Section 7: vs 老系统 (R104-114) ──
rows.append(["vs 老系统对比"])
rows.append(E)
rows.append(["", "指标", "老Gacha", "新金字塔"])
rows.append(["", "总奖励价值", "$1,085", "$1,238"])
rows.append(["", "平均花费", "~$665", "~$550"])
rows.append(["", "花费范围", "$620-$710", "$450-$750"])
rows.append(["", "ROI（满抽）", "1.77", "1.77"])
rows.append(["", "前$200体验", "5/12抽", "~13抽到L4"])
rows.append(["", "每格结构", "多道具组合", "单道具/格"])
rows.append(["", "新增道具", "-", "成长线宝箱自选2 (79个)"])
rows.append(E)                                              # ~R115

# ── Section 8: 礼包设计 (R116-145) ──
rows.append(["礼包设计"])
rows.append(E)
rows.append(["", "价格", "锤子数量", "限购", "性价比", "小计数量", "小计金额", "备注"])
rows.append(["", "$4.99", "1", "2", "$4.99", "2", "$9.98", ""])
rows.append(["", "$9.99", "2", "2", "$5.00", "4", "$19.98", ""])
rows.append(["", "$19.99", "E[5.06]", "1", "$3.95", "", "", "随机"])
rows.append(["", "$19.99", "4", "1", "$5.00", "4", "$19.99", ""])
rows.append(["", "$49.99", "E[9.50]", "1", "$5.26", "", "", "随机"])
rows.append(["", "$49.99", "8", "1", "$6.25", "8", "$49.99", ""])
rows.append(["", "$99.99", "E[18.55]", "1", "$5.39", "", "", "随机"])
rows.append(["", "$99.99", "16", "5", "$6.25", "80", "$499.95", "无限续杯"])
rows.append(E)
rows.append(["", "锤子行为成本", "$6.25", "满抽 127 tok"])
rows.append(E)

rows.append(["", "购买路径估算"])
rows.append(["", "玩家类型", "抽数", "消耗tok", "一次性", "续杯", "总花费"])
rows.append(["", "运气好(P10)", "12", "~70", "$250", "$120(1次)", "~$370"])
rows.append(["", "中位数(P50)", "18", "~105", "$250", "$300(3次)", "~$550"])
rows.append(["", "运气差(P90)", "21", "127", "$250", "$500(5次)", "~$750"])
rows.append(E)

rows.append(["", "随机礼包权重"])
rows.append(["", "$19.99 (E[5.06]锤)", "", "$49.99 (E[9.50]锤)", "", "$99.99 (E[18.55]锤)", ""])
rows.append(["", "锤子", "权重", "锤子", "权重", "锤子", "权重"])
rows.append(["", "4", "150", "8", "150", "16", "150"])
rows.append(["", "5", "100", "9", "100", "18", "100"])
rows.append(["", "6", "50", "11", "50", "21", "50"])
rows.append(["", "7", "20", "13", "20", "24", "20"])
rows.append(["", "8", "10", "15", "10", "27", "10"])
rows.append(["", "10", "5", "17", "5", "30", "5"])
rows.append(["", "12", "2", "20", "2", "35", "2"])
rows.append(["", "15", "1", "25", "1", "50", "1"])
rows.append(["", "合计", "338", "合计", "338", "合计", "338"])
rows.append(E)

rows.append(["", "收尾回收：锤子→15分钟加速×1 ($0.11，ROI 1.79%)"])
rows.append(E)                                              # ~R159

# ── Section 9: 阶段奖励 (R160-182) ──
rows.append(["阶段奖励设计"])
rows.append(E)
rows.append(["", "触发规则"])
rows.append(["", "", "1、升层道具（每层最左侧）同时为阶段奖道具"])
rows.append(["", "", "2、累计获取4个升层道具后，弹窗领取阶段奖励"])
rows.append(["", "", "3、仅触发1次，触发后不归零，不再触发"])
rows.append(["", "", "4、每个玩家至少5次升层 → 100%触发恰好1次"])
rows.append(E)

rows.append(["", "触发时机"])
rows.append(["", "", "最快", "连续4次升层(L1→L5)，约$200花费时触发"])
rows.append(["", "", "典型", "中间有降层，约$250-350花费段触发"])
rows.append(["", "", "触发率", "100%（全员1次）"])
rows.append(E)

rows.append(["", "奖励内容（每次触发）"])
rows.append(["", "", "道具", "数量", "道具id", "单价", "价值"])
rows.append(["", "", "锤子", "3", "11117107", "$6.25", "$18.75"])
rows.append(["", "", "机能核心", "30", "11118501", "$0.62", "$18.72"])
rows.append(["", "", "万能英雄碎片-橙", "5", "11116304", "$2.50", "$12.48"])
rows.append(["", "", "合计", "", "", "", "$49.95"])
rows.append(E)

rows.append(["", "经济影响"])
rows.append(["", "", "token节省", "3 tok ($18.75)", "所有玩家统一"])
rows.append(["", "", "道具价值", "$31.20", "机能核心30+橙碎5"])
rows.append(["", "", "总价值", "$49.95/人", "固定"])
rows.append(E)

rows.append(["", "设计意图"])
rows.append(["", "", "1、前200-350刀正反馈：第4次升层弹窗，鼓励继续投入"])
rows.append(["", "", "2、100%触发=全员福利，没有落差感"])
rows.append(["", "", "3、仅1次+不归零 → 经济影响固定可控，逻辑简洁"])

TOTAL = len(rows)
print(f"  Total rows: {TOTAL}")

# ════════════════════════════════════════
# Step 3: Write data in chunks
# ════════════════════════════════════════
print("Step 3: Writing data...")
chunk = 30
for i in range(0, TOTAL, chunk):
    batch = rows[i:i+chunk]
    r1 = i + 1
    r2 = r1 + len(batch) - 1
    ok = values_update(f"A{r1}:J{r2}", batch)
    print(f"  {'OK' if ok else 'FAIL'}: R{r1}-R{r2}")

# ════════════════════════════════════════
# Step 4: Apply formatting
# ════════════════════════════════════════
print("Step 4: Applying formatting...")

def rgb(r,g,b): return {"red":r/255,"green":g/255,"blue":b/255}

WHITE = rgb(255,255,255)
DARK_BG = rgb(32,33,36)
HEADER_BG = rgb(66,133,244)     # Google blue
HEADER_BG2 = rgb(52,73,94)     # dark blue-gray
TABLE_HEADER = rgb(234,236,240) # light gray
ALT_ROW = rgb(248,249,250)     # very light gray
BORDER_COLOR = rgb(218,220,224)
GREEN = rgb(52,168,83)
RED = rgb(234,67,53)

# Section title rows (col A has the title)
# R1=设计思路, R6=数值目录, R14=金字塔结构, R27=奖励明细, R73=总付费产出
# R86=模拟结果, R104=vs老系统, R116=礼包设计, R160=阶段奖励

section_title_rows = [0, 5, 13, 26, 72, 85, 103, 115, 159]  # 0-indexed

# Table header rows (the row with column names)
table_header_rows = [2, 7, 15, 31, 74, 88, 105, 117, 131, 137, 173, 179]

# Build formatting requests
reqs = []

# 1. Section titles: bold, larger, blue text, bottom border
for r in section_title_rows:
    reqs.append({
        "repeatCell": {
            "range": {"sheetId":SHEET_GID, "startRowIndex":r, "endRowIndex":r+1, "startColumnIndex":0, "endColumnIndex":10},
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold": True, "fontSize": 12, "foregroundColor": rgb(26,115,232)},
                "borders": {"bottom": {"style":"SOLID","width":2,"color":rgb(26,115,232)}}
            }},
            "fields": "userEnteredFormat(textFormat,borders)"
        }
    })

# 2. Table headers: bold, gray background
for r in table_header_rows:
    reqs.append({
        "repeatCell": {
            "range": {"sheetId":SHEET_GID, "startRowIndex":r, "endRowIndex":r+1, "startColumnIndex":0, "endColumnIndex":10},
            "cell": {"userEnteredFormat": {
                "backgroundColor": TABLE_HEADER,
                "textFormat": {"bold": True, "fontSize": 10},
                "borders": {
                    "top": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "bottom": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                }
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,borders)"
        }
    })

# 3. Reward detail table borders (R32-R66 = data rows of 21 slots + layer totals)
# Add thin borders to the entire reward block
for r in range(31, 67):  # rows 32-67 (0-indexed 31-66)
    reqs.append({
        "repeatCell": {
            "range": {"sheetId":SHEET_GID, "startRowIndex":r, "endRowIndex":r+1, "startColumnIndex":1, "endColumnIndex":10},
            "cell": {"userEnteredFormat": {
                "borders": {
                    "top": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "bottom": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "left": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "right": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                }
            }},
            "fields": "userEnteredFormat(borders)"
        }
    })

# 4. Layer total rows: bold + light blue background
layer_total_rows_0idx = [38, 44, 50, 55, 59, 62]  # the "Lx 合计" rows
for r in layer_total_rows_0idx:
    reqs.append({
        "repeatCell": {
            "range": {"sheetId":SHEET_GID, "startRowIndex":r, "endRowIndex":r+1, "startColumnIndex":1, "endColumnIndex":10},
            "cell": {"userEnteredFormat": {
                "backgroundColor": rgb(232,240,254),
                "textFormat": {"bold": True}
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    })

# 5. Grand total row (R66): bold + darker blue bg
reqs.append({
    "repeatCell": {
        "range": {"sheetId":SHEET_GID, "startRowIndex":65, "endRowIndex":66, "startColumnIndex":1, "endColumnIndex":10},
        "cell": {"userEnteredFormat": {
            "backgroundColor": rgb(210,227,252),
            "textFormat": {"bold": True, "fontSize": 11}
        }},
        "fields": "userEnteredFormat(backgroundColor,textFormat)"
    }
})

# 6. 总付费产出 table borders (R75-R84)
for r in range(74, 84):
    reqs.append({
        "repeatCell": {
            "range": {"sheetId":SHEET_GID, "startRowIndex":r, "endRowIndex":r+1, "startColumnIndex":1, "endColumnIndex":7},
            "cell": {"userEnteredFormat": {
                "borders": {
                    "top": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "bottom": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "left": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "right": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                }
            }},
            "fields": "userEnteredFormat(borders)"
        }
    })

# 7. 模拟结果 table borders (R89-R93)
for r in range(88, 93):
    reqs.append({
        "repeatCell": {
            "range": {"sheetId":SHEET_GID, "startRowIndex":r, "endRowIndex":r+1, "startColumnIndex":1, "endColumnIndex":8},
            "cell": {"userEnteredFormat": {
                "borders": {
                    "top": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "bottom": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "left": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "right": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                }
            }},
            "fields": "userEnteredFormat(borders)"
        }
    })

# 8. vs老系统 table borders (R106-R114)
for r in range(105, 114):
    reqs.append({
        "repeatCell": {
            "range": {"sheetId":SHEET_GID, "startRowIndex":r, "endRowIndex":r+1, "startColumnIndex":1, "endColumnIndex":4},
            "cell": {"userEnteredFormat": {
                "borders": {
                    "top": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "bottom": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "left": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "right": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                }
            }},
            "fields": "userEnteredFormat(borders)"
        }
    })

# 9. 礼包 table borders (R118-R126)
for r in range(117, 126):
    reqs.append({
        "repeatCell": {
            "range": {"sheetId":SHEET_GID, "startRowIndex":r, "endRowIndex":r+1, "startColumnIndex":1, "endColumnIndex":8},
            "cell": {"userEnteredFormat": {
                "borders": {
                    "top": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "bottom": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "left": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                    "right": {"style":"SOLID","width":1,"color":BORDER_COLOR},
                }
            }},
            "fields": "userEnteredFormat(borders)"
        }
    })

# 10. Auto-resize columns
reqs.append({
    "autoResizeDimensions": {
        "dimensions": {"sheetId":SHEET_GID, "dimension":"COLUMNS", "startIndex":0, "endIndex":10}
    }
})

# Send formatting in one batch
print(f"  Sending {len(reqs)} format requests...")
batch_update(reqs)

print("\n=== DONE! Sheet rebuilt with clean layout + formatting. ===")
print(f"Total: {TOTAL} rows")
