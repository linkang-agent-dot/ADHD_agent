# -*- coding: utf-8 -*-
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

SSID = "1B46X-aWpv0DXL9Q_sBvUkNBdLIw34wMPTnOLKQnPNOw"
SHEET = "换皮后数值"
ITEM_ID = "11117107"

def gws_update(range_str, values):
    cmd_input = json.dumps({
        "args": [
            "sheets", "spreadsheets", "values", "update",
            "--params", json.dumps({
                "spreadsheetId": SSID,
                "range": f"'{SHEET}'!{range_str}",
                "valueInputOption": "RAW"
            }),
            "--json", json.dumps({"values": values})
        ]
    }, ensure_ascii=False)
    result = subprocess.run(
        ["node", "C:/ADHD_agent/scripts/gws_stdin.js"],
        input=cmd_input, capture_output=True, text=True, encoding='utf-8'
    )
    if result.returncode != 0:
        print(f"  FAIL {range_str}: {result.stderr[:200]}")
        return False
    resp = json.loads(result.stdout) if result.stdout else {}
    print(f"  OK: {range_str} ({resp.get('updatedCells','?')} cells)")
    return True

def write_chunk(rows, start_row):
    """Write rows in chunks of 30"""
    chunk = 30
    for i in range(0, len(rows), chunk):
        batch = rows[i:i+chunk]
        r1 = start_row + i
        r2 = r1 + len(batch) - 1
        ok = gws_update(f"A{r1}:K{r2}", batch)
        if not ok:
            # Try even smaller chunks
            for j, row in enumerate(batch):
                rr = r1 + j
                gws_update(f"A{rr}:K{rr}", [row])

# ══════════════════════════════════════════
# Build all data
# ══════════════════════════════════════════
rows = []

# ── 礼包设计 ──
rows.append(["礼包设计"])
rows.append([])
rows.append(["", "礼包总览", "", "", "", "", "", "", "", "", "", "", "", "", "老科技节"])
rows.append(["", "价格", "锤子数量", "限购次数", "性价比", "小计数量", "小计金额", "最低获取"])
rows.append(["", "4.99", "1", "2", "$4.99", "2", "9.98", "2"])
rows.append(["", "9.99", "2", "2", "$5.00", "4", "19.98", "4"])
rows.append(["", "19.99", "5.06", "1", "$3.95", "", "", "", "随机"])
rows.append(["", "19.99", "4", "1", "$5.00", "4", "19.99", "4"])
rows.append(["", "49.99", "9.50", "1", "$5.26", "", "", "", "随机"])
rows.append(["", "49.99", "8", "1", "$6.25", "8", "49.99", "8"])
rows.append(["", "99.99", "18.55", "1", "$5.39", "", "", "", "随机"])
rows.append(["", "99.99", "16", "5", "$6.25", "80", "499.95", "80", "无限续杯"])
rows.append([])
rows.append(["", "行为描述", "成本价值", "满抽token数"])
rows.append(["", "锤子道具价值", "6.25", "127"])
rows.append([])
rows.append(["", "", "", "", "一次性礼包", "~51", "$269.91"])
rows.append(["", "", "", "", "续杯补齐（满抽127tok）", "~76", "$474.94"])
rows.append(["", "", "", "", "总计（满抽）", "~127", "$744.85"])
rows.append([])
rows.append(["", "购买路径估算"])
rows.append(["", "玩家类型", "抽数(P值)", "消耗token", "一次性花费", "续杯花费", "总花费"])
rows.append(["", "运气好(P10)", "12", "~70", "$269.91", "$119.98(1次)", "~$390"])
rows.append(["", "中位数(P50)", "18", "~105", "$269.91", "$299.97(3次)", "~$570"])
rows.append(["", "运气差(P90)", "21", "127", "$269.91", "$474.94(5次)", "~$745"])
rows.append([])
rows.append([])

# ── 随机礼包明细 ──
rows.append(["", "随机礼包1", "目标中R"])
rows.append(["", "价格", "期望道具数量", "活动期间限购"])
rows.append(["", "19.99", "5.06", "1"])
rows.append([])
rows.append(["", "锤子数量", "配置权重", "期望概率", "期望获得"])

for n,w,p,e in [("4","150","44.38%","1.78"),("5","100","29.59%","1.48"),("6","50","14.79%","0.89"),("7","20","5.92%","0.41"),("8","10","2.96%","0.24"),("10","5","1.48%","0.15"),("12","2","0.59%","0.07"),("15","1","0.30%","0.04")]:
    rows.append(["", n, w, p, e])
rows.append(["", "", "338", "", "5.06"])
rows.append([])

rows.append(["", "随机礼包2", "目标大超R"])
rows.append(["", "价格", "期望道具数量", "活动期间限购"])
rows.append(["", "49.99", "9.50", "1"])
rows.append([])
rows.append(["", "锤子数量", "配置权重", "期望概率", "期望获得"])

for n,w,p,e in [("8","150","44.38%","3.55"),("9","100","29.59%","2.66"),("11","50","14.79%","1.63"),("13","20","5.92%","0.77"),("15","10","2.96%","0.44"),("17","5","1.48%","0.25"),("20","2","0.59%","0.12"),("25","1","0.30%","0.07")]:
    rows.append(["", n, w, p, e])
rows.append(["", "", "338", "", "9.50"])
rows.append([])

rows.append(["", "随机礼包3", "目标大超R"])
rows.append(["", "价格", "期望道具数量", "活动期间限购"])
rows.append(["", "99.99", "18.55", "1"])
rows.append([])
rows.append(["", "锤子数量", "配置权重", "期望概率", "期望获得"])

for n,w,p,e in [("16","150","44.38%","7.10"),("18","100","29.59%","5.33"),("21","50","14.79%","3.11"),("24","20","5.92%","1.42"),("27","10","2.96%","0.80"),("30","5","1.48%","0.44"),("35","2","0.59%","0.21"),("50","1","0.30%","0.15")]:
    rows.append(["", n, w, p, e])
rows.append(["", "", "338", "", "18.55"])
rows.append([])

rows.append(["", "收尾回收"])
rows.append(["", "", "道具回收", "行为成本价值", "回收道具", "回收数量", "付费价值", "回收ROI"])
rows.append(["", "", "锤子道具", "6.25", "15分钟加速", "1", "$0.11", "1.79%"])
rows.append([])
rows.append([])

# ── 阶段奖励设计 ──
rows.append(["阶段奖励设计"])
rows.append([])
rows.append(["", "一、触发规则"])
rows.append(["", "", "1、升层道具（每层最左侧）同时为阶段奖道具"])
rows.append(["", "", "2、累计获取4个升层道具后，弹窗领取阶段奖励"])
rows.append(["", "", "3、领取后计数器归零，下次再集齐4个可再次领取"])
rows.append(["", "", "4、阶段奖为通用奖励，不区分第几次触发"])
rows.append([])
rows.append(["", "二、触发概率（20万次模拟）"])
rows.append(["", "", "触发次数", "玩家占比", "说明"])
rows.append(["", "", "1次", "62.7%", "正常路径，5-7次升层"])
rows.append(["", "", "2次", "37.3%", "被降层较多，8+次升层"])
rows.append(["", "", "平均触发", "1.37次", ""])
rows.append([])
rows.append(["", "三、奖励内容（每次触发）"])
rows.append(["", "", "道具", "数量", "道具id", "单价", "价值", "说明"])
rows.append(["", "", "锤子", "3", ITEM_ID, "$6.25", "$18.75", "约1次L3抽或0.3次L4抽"])
rows.append(["", "", "机能核心", "30", "11118501", "$0.62", "$18.72", ""])
rows.append(["", "", "万能英雄碎片-橙色", "5", "11116304", "$2.50", "$12.48", ""])
rows.append(["", "", "", "", "", "阶段奖价值", "$49.95", ""])
rows.append([])
rows.append(["", "四、经济影响"])
rows.append(["", "", "指标", "数值", "说明"])
rows.append(["", "", "每次token节省", "3 tok ($18.75)", ""])
rows.append(["", "", "每次道具价值", "$31.20", ""])
rows.append(["", "", "每次总价值", "$49.95", ""])
rows.append(["", "", "平均总token节省", "4.11 tok ($25.69)", "1.37次x3tok"])
rows.append(["", "", "平均总道具价值", "$42.74", "1.37次x$31.20"])
rows.append(["", "", "平均总价值", "$68.43", "1.37次x$49.95"])
rows.append([])
rows.append(["", "五、含阶段奖花费估算"])
rows.append(["", "", "玩家类型", "原花费", "token节省", "调整后花费", "额外道具"])
rows.append(["", "", "运气好(P10)", "~$390", "-$19", "~$371", "$31"])
rows.append(["", "", "中位数(P50)", "~$570", "-$19~$38", "~$540", "$31~$62"])
rows.append(["", "", "运气差(P90)", "~$745", "-$38", "~$707", "$62"])
rows.append([])
rows.append(["", "六、设计意图"])
rows.append(["", "", "1、前200刀体感提升：第4次升层约在$150-200花费段触发，给玩家正反馈"])
rows.append(["", "", "2、降层补偿：被弹回的玩家更容易触发第2次，用额外道具弥补挫败感"])
rows.append(["", "", "3、经济影响可控：token节省仅$19-38，不影响600刀核心锚点"])

# ══════════════════════════════════════════
# Write in chunks
# ══════════════════════════════════════════
START = 137
print(f"Total rows: {len(rows)}, writing from row {START}...")
write_chunk(rows, START)
print(f"Done! Rows {START}-{START+len(rows)-1}")
