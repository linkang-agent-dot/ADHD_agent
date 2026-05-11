# -*- coding: utf-8 -*-
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

SSID = "1B46X-aWpv0DXL9Q_sBvUkNBdLIw34wMPTnOLKQnPNOw"
SHEET = "换皮后数值"

def gws_update(range_str, values):
    cmd = json.dumps({
        "args": ["sheets","spreadsheets","values","update",
            "--params", json.dumps({
                "spreadsheetId": SSID,
                "range": f"'{SHEET}'!{range_str}",
                "valueInputOption": "RAW"
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

# ════════════════════════════════════════
# 覆盖阶段奖励 section (row 215-253)
# ════════════════════════════════════════
E = ["","","","","","","","","","",""]
rows = []

rows.append(["阶段奖励设计"])
rows.append([])
rows.append(["", "一、触发规则"])
rows.append(["", "", "1、升层道具（每层最左侧）同时为阶段奖道具"])
rows.append(["", "", "2、累计获取4个升层道具后，弹窗领取阶段奖励"])
rows.append(["", "", "3、仅触发1次，触发后计数器不归零，不会再次触发"])
rows.append(["", "", "4、每个玩家至少5次升层 → 100%玩家必定触发"])
rows.append([])

rows.append(["", "二、触发时机"])
rows.append(["", "", "场景", "说明"])
rows.append(["", "", "最快触发", "连续4次升层(L1→L5)，约在$200花费时触发"])
rows.append(["", "", "典型触发", "中间有降层，第4次升层约在$250-350花费段"])
rows.append(["", "", "触发率", "100%（所有玩家必定触发恰好1次）"])
rows.append([])

rows.append(["", "三、奖励内容"])
rows.append(["", "", "道具", "数量", "道具id", "单价", "价值", "说明"])
rows.append(["", "", "锤子", "3", "11117107", "$6.25", "$18.75", "约1次L3抽或0.3次L4抽"])
rows.append(["", "", "机能核心", "30", "11118501", "$0.62", "$18.72", ""])
rows.append(["", "", "万能英雄碎片-橙色", "5", "11116304", "$2.50", "$12.48", ""])
rows.append(["", "", "", "", "", "阶段奖价值", "$49.95", ""])
rows.append([])

rows.append(["", "四、经济影响"])
rows.append(["", "", "指标", "数值", "说明"])
rows.append(["", "", "触发次数", "1次（固定）", "不归零，仅1次"])
rows.append(["", "", "token节省", "3 tok ($18.75)", "所有玩家统一"])
rows.append(["", "", "道具价值", "$31.20", "机能核心30+橙碎5"])
rows.append(["", "", "总价值", "$49.95", "每个玩家固定获得"])
rows.append([])

rows.append(["", "五、含阶段奖花费估算"])
rows.append(["", "", "玩家类型", "原花费", "token节省", "调整后花费", "额外道具"])
rows.append(["", "", "运气好(P10)", "~$450", "-$19", "~$431", "$31"])
rows.append(["", "", "中位数(P50)", "~$550", "-$19", "~$531", "$31"])
rows.append(["", "", "运气差(P90)", "~$750", "-$19", "~$731", "$31"])
rows.append([])

rows.append(["", "六、设计意图"])
rows.append(["", "", "1、前200-350刀正反馈：第4次升层时弹窗，鼓励继续投入"])
rows.append(["", "", "2、100%触发=全员福利，没有落差感"])
rows.append(["", "", "3、仅1次 → 经济影响固定可控($19 token + $31道具)"])
rows.append(["", "", "4、不归零 → 逻辑简洁，不需要客户端维护多轮计数"])

# 补空行清掉旧残留
while len(rows) < 39:
    rows.append(E)

print(f"Writing {len(rows)} rows from R215...")
write_rows(rows, 215)
print("Done!")
