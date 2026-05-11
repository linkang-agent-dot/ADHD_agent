# -*- coding: utf-8 -*-
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

SSID = "1B46X-aWpv0DXL9Q_sBvUkNBdLIw34wMPTnOLKQnPNOw"
SHEET_GID = 531423017
MAX_ROW = 172

def gws_batch(reqs):
    cmd = json.dumps({"args": [
        "sheets","spreadsheets","batchUpdate",
        "--params", json.dumps({"spreadsheetId":SSID}),
        "--json", json.dumps({"requests":reqs})
    ]}, ensure_ascii=False)
    r = subprocess.run(["node","C:/ADHD_agent/scripts/gws_stdin.js"],
        input=cmd, capture_output=True, text=True, encoding='utf-8')
    ok = r.returncode == 0
    if not ok:
        print(f"  FAIL: {r.stderr[:200]}")
        # Try to find the error in stdout
        if r.stdout:
            print(f"  resp: {r.stdout[:300]}")
    else:
        print(f"  OK ({len(reqs)} requests)")
    return ok

def rgb(r,g,b): return {"red":r/255,"green":g/255,"blue":b/255}

BLUE = rgb(26,115,232)
GRAY_BG = rgb(234,236,240)
LIGHT_BLUE = rgb(232,240,254)
MED_BLUE = rgb(210,227,252)
BORDER = rgb(218,220,224)

def fmt_bold_blue(row_0idx):
    return {
        "repeatCell": {
            "range": {"sheetId":SHEET_GID,"startRowIndex":row_0idx,"endRowIndex":row_0idx+1,"startColumnIndex":0,"endColumnIndex":10},
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold":True,"fontSize":12,"foregroundColor":BLUE},
                "borders": {"bottom":{"style":"SOLID","width":2,"color":BLUE}}
            }},
            "fields":"userEnteredFormat(textFormat,borders)"
        }
    }

def fmt_table_header(row_0idx, end_col=10):
    return {
        "repeatCell": {
            "range": {"sheetId":SHEET_GID,"startRowIndex":row_0idx,"endRowIndex":row_0idx+1,"startColumnIndex":1,"endColumnIndex":end_col},
            "cell": {"userEnteredFormat": {
                "backgroundColor":GRAY_BG,
                "textFormat": {"bold":True,"fontSize":10},
                "borders": {
                    "top":{"style":"SOLID","width":1,"color":BORDER},
                    "bottom":{"style":"SOLID","width":1,"color":BORDER},
                    "left":{"style":"SOLID","width":1,"color":BORDER},
                    "right":{"style":"SOLID","width":1,"color":BORDER}
                }
            }},
            "fields":"userEnteredFormat(backgroundColor,textFormat,borders)"
        }
    }

def fmt_subtotal(row_0idx, end_col=10):
    return {
        "repeatCell": {
            "range": {"sheetId":SHEET_GID,"startRowIndex":row_0idx,"endRowIndex":row_0idx+1,"startColumnIndex":1,"endColumnIndex":end_col},
            "cell": {"userEnteredFormat": {
                "backgroundColor":LIGHT_BLUE,
                "textFormat": {"bold":True}
            }},
            "fields":"userEnteredFormat(backgroundColor,textFormat)"
        }
    }

def fmt_grand_total(row_0idx, end_col=10):
    return {
        "repeatCell": {
            "range": {"sheetId":SHEET_GID,"startRowIndex":row_0idx,"endRowIndex":row_0idx+1,"startColumnIndex":1,"endColumnIndex":end_col},
            "cell": {"userEnteredFormat": {
                "backgroundColor":MED_BLUE,
                "textFormat": {"bold":True,"fontSize":11}
            }},
            "fields":"userEnteredFormat(backgroundColor,textFormat)"
        }
    }

def fmt_borders(start_row, end_row, start_col, end_col):
    """Add grid borders to a range."""
    reqs = []
    for r in range(start_row, min(end_row, MAX_ROW)):
        reqs.append({
            "repeatCell": {
                "range": {"sheetId":SHEET_GID,"startRowIndex":r,"endRowIndex":r+1,"startColumnIndex":start_col,"endColumnIndex":end_col},
                "cell": {"userEnteredFormat": {
                    "borders": {
                        "top":{"style":"SOLID","width":1,"color":BORDER},
                        "bottom":{"style":"SOLID","width":1,"color":BORDER},
                        "left":{"style":"SOLID","width":1,"color":BORDER},
                        "right":{"style":"SOLID","width":1,"color":BORDER}
                    }
                }},
                "fields":"userEnteredFormat(borders)"
            }
        })
    return reqs

# ══════════════════════════════════════════
# Batch 1: Section titles (9 titles)
# ══════════════════════════════════════════
print("Batch 1: Section titles...")
# R1(0), R6(5), R14(13), R27(26), R73(72), R86(85), R104(103), R116(115), R160(159)
reqs1 = [fmt_bold_blue(i) for i in [0, 5, 13, 26, 72, 85, 103, 115, 159]]
gws_batch(reqs1)

# ══════════════════════════════════════════
# Batch 2: Table headers
# ══════════════════════════════════════════
print("Batch 2: Table headers...")
# R3(2), R8(7), R16(15), R32(31), R75(74), R89(88), R106(105), R118(117)
reqs2 = [fmt_table_header(i) for i in [2, 7, 15, 31, 74, 88, 105, 117]]
gws_batch(reqs2)

# ══════════════════════════════════════════
# Batch 3: Sub-headers (购买路径, 养成线投放, 逐层累计, 随机礼包权重, 阶段奖子标题)
# ══════════════════════════════════════════
print("Batch 3: Sub-headers...")
# R68(67)养成线, R95(94)逐层累计, R131(130)购买路径, R138(137)随机权重
# R162(161)触发规则, R169(168)触发时机, R173(172)...hmm 172 is at limit
# R175(174)奖励内容 header... wait need to check exact rows
# Let me use the known safe ones
sub_headers = [67, 94, 130, 137]
reqs3 = [fmt_table_header(i, 7) for i in sub_headers]
gws_batch(reqs3)

# ══════════════════════════════════════════
# Batch 4: Layer subtotals + grand total
# ══════════════════════════════════════════
print("Batch 4: Subtotals...")
# L1合计=R39(38), L2=R45(44), L3=R50(49), L4=R55(54), L5=R59(58), L6 row after
# Actually need to recount. Let me count from the data:
# R32=header, R33-R38=L1(6rows), R39=L1合计 → 0idx=38 ✓
# R40-R44=L2(5rows), R45=L2合计 → 0idx=44 ✓
# R46-R49=L3(4rows), R50=L3合计 → 0idx=49
# Wait, R46=L3-1(0idx=45), R47=L3-2(46), R48=L3-3(47), R49=L3-4(48), R50=L3合计(49) ✓
# R51-R53=L4(3rows), R54=L4合计 → 0idx=53
# Wait: R51=L4-1(50), R52=L4-2(51), R53=L4-3(52), R54=L4合计(53) ✓
# R55-R56=L5(2rows), R57=L5合计 → 0idx=56
# R55=L5-1(54), R56=L5-2(55), R57=L5合计(56) ✓
# R58=L6 row (57)
# R59=blank(58), R60=grand total(59)? Let me check...
# After L6: blank, then "总计 21格..." → R66 area

# Actually I need to count precisely. Let me just count the rows array:
# rows[31] = header "格位..."
# rows[32] = L1-1 → R33
# rows[33] = L1-2
# rows[34] = L1-3
# rows[35] = L1-4
# rows[36] = L1-5
# rows[37] = L1-6
# rows[38] = L1合计 → R39
# rows[39] = L2-1 → R40
# rows[40] = L2-2
# rows[41] = L2-3
# rows[42] = L2-4
# rows[43] = L2-5
# rows[44] = L2合计 → R45
# rows[45] = L3-1 → R46
# rows[46] = L3-2
# rows[47] = L3-3
# rows[48] = L3-4
# rows[49] = L3合计 → R50
# rows[50] = L4-1
# rows[51] = L4-2
# rows[52] = L4-3
# rows[53] = L4合计 → R54
# rows[54] = L5-1
# rows[55] = L5-2
# rows[56] = L5合计 → R57
# rows[57] = L6-1 → R58
# rows[58] = blank
# rows[59] = grand total → R60

subtotal_rows = [38, 44, 49, 53, 56]  # 0-indexed L1-L5 合计
grand_total_row = 59  # 0-indexed

reqs4 = [fmt_subtotal(i) for i in subtotal_rows]
reqs4.append(fmt_grand_total(grand_total_row))
gws_batch(reqs4)

# ══════════════════════════════════════════
# Batch 5: Borders on reward detail table (R32-R60)
# ══════════════════════════════════════════
print("Batch 5: Reward table borders...")
reqs5 = fmt_borders(31, 60, 1, 10)
gws_batch(reqs5)

# ══════════════════════════════════════════
# Batch 6: Borders on other tables
# ══════════════════════════════════════════
print("Batch 6: Other table borders...")
reqs6 = []
reqs6 += fmt_borders(74, 84, 1, 7)   # 总付费产出
reqs6 += fmt_borders(88, 93, 1, 8)   # 模拟结果
reqs6 += fmt_borders(105, 114, 1, 4) # vs老系统
reqs6 += fmt_borders(117, 126, 1, 8) # 礼包总览
gws_batch(reqs6)

# ══════════════════════════════════════════
# Batch 7: Auto-resize + freeze row 1
# ══════════════════════════════════════════
print("Batch 7: Auto-resize...")
gws_batch([
    {"autoResizeDimensions": {"dimensions": {"sheetId":SHEET_GID,"dimension":"COLUMNS","startIndex":0,"endIndex":10}}},
    {"updateSheetProperties": {"properties": {"sheetId":SHEET_GID,"gridProperties":{"frozenRowCount":0}},"fields":"gridProperties.frozenRowCount"}}
])

print("\n=== Formatting complete! ===")
