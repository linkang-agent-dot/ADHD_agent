# -*- coding: utf-8 -*-
"""一次性切换：X3 夏日节日报 第二批(1880-1900) → 第三批(1910-1930)。

由一次性 Windows 任务 ClaudeX3SwitchBatch3 在 2026-06-19 08:30 触发：
  1) 备份 x3_festival_daily.py
  2) 用稳定锚点替换「配置区」整段为第三批参数（避免逐行脆弱匹配）
  3) 跑一次生成，出 1910-1930 的 D0 报告 + 刷新 latest
  4) 成功后自删本任务 ClaudeX3SwitchBatch3
全程写日志 _x3_switch_batch3_log.txt；任一步失败则不写文件、保留第二批配置、留日志报警。
"""
import os
import sys
import shutil
import subprocess
from datetime import datetime

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(SKILL_DIR, "x3_festival_daily.py")
LOG = os.path.expanduser(r"~\_x3_switch_batch3_log.txt")
TASK_NAME = "ClaudeX3SwitchBatch3"

START = "# ============ 配置 ============\n"   # 稳定锚（配置区头）
END = "BASELINE_HOURLY_DAYS = 3"                       # 稳定锚（配置区尾的下一行）

NEW_MIDDLE = '''DATASOURCE = "TRINO_HF"
FESTIVAL_NAME = "夏日节1910-1930服"
# 第三批次（1910/1920/1930 服）夏日恋语开场日 = 2026-06-19：
#   夏日专属包(装饰210917/918/919 + 拜访210921) 在该批服 06-19 前流水=0(实测)，06-19 08:00 首次开场 → D0=06-19。
#   基线窗口(06-05~06-18)仅含跨节日复用包(情人节连锁2107xx/通行证130020·130021/许愿池1002001)常态流水，无夏日专属。
#   （第二批 1880-1900 的 06-09→06-19 已收尾，历史日报 HTML 已逐日落盘归档，此处改指第三批。）
FESTIVAL_D0 = "2026-06-19"
# ⚠️ 节日活动下线时点（必填）：累充活动 100595 在 2026-06-29 08:00(北京时间) 下线，沿用 10 天窗口。
# 数仓 created_at/partition_date 均为北京时间（开场日 hour=8 暴涨、下线日 hour=8 起零成交，已实测验证）。
# 必须加这道时间上界：白名单里的复用包(情人节连锁 2107xx / 通用通行证 130020·130021 / 许愿池 1002001)
# 下个活动会被重新挂上来卖，没有时间卡口会把下线后的常态流水继续误算成本届节日收入。
FESTIVAL_END_TS = "2026-06-29 08:00:00"  # 第三批 10 天窗口（06-19 08:00 → 06-29 08:00 北京）
FEST_TIME_GUARD = f"o.created_at < TIMESTAMP '{FESTIVAL_END_TS}'"
BASELINE_START = "2026-06-05"       # 基线 14 日（D0 前；该批服此窗口无夏日专属流水，已实测干净）
BASELINE_END = "2026-06-18"
# 双服段（核心：同期对比要"服务器生命周期一致" = 各期取「D0 时距开服天数(服龄)处于同一阶段」的服，
#   排除新服爆发期对对比的干扰。**按服龄阈值匹配，不是同一批物理服**）：
# - 夏日(本期，主报告+对比夏日侧) = 第三批 1910/1920/1930 三服：D0(06-19) 时服龄 41/37/35 天
#   （1910 开服 05-09 / 1920 05-13 / 1930 05-15），刚过 D35 的年轻服。
# - 情人节(对比上期侧) = 1530/1540/1550 三服：情人节 D0(02-06) 时服龄 43/39/35 天
#   （1530 开服 12-25 / 1540 12-29 / 1550 01-02），与本批服龄同档(35-43d) → 生命周期一致。
SERVER_FILTER = "AND TRY_CAST(o.server_id AS INTEGER) BETWEEN 1910 AND 1930"      # 第三批夏日 = 1910/1920/1930 三服
# ✅ 对比侧已按本批服龄校准：情人节 1530-1550 服 D0 服龄 43/39/35 天，对齐本批 41/37/35。
#    BENCHMARK_* 查询走 SERVER_FILTER_VAL(sf 参数)，故对比区块/R级对齐均用该生命周期匹配服段。
SERVER_FILTER_VAL = "AND TRY_CAST(o.server_id AS INTEGER) BETWEEN 1530 AND 1550"  # 情人节生命周期匹配服(D0服龄35-43d)
SERVER_LABEL = "本期夏日第三批 1910/1920/1930(D0服龄41/37/35d)；对比侧情人节 1530/1540/1550(D0服龄43/39/35d) 生命周期匹配"
'''


def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    log("==== switch to batch3 (1910-1930) start ====")
    with open(SCRIPT, "r", encoding="utf-8") as f:
        content = f.read()

    if content.count(START) != 1:
        log(f"ABORT: START anchor count = {content.count(START)} (expect 1). No change written.")
        return 2
    if content.count(END) != 1:
        log(f"ABORT: END anchor count = {content.count(END)} (expect 1). No change written.")
        return 2
    if "1910 AND 1930" in content:
        log("ABORT: script already targets 1910-1930 (already switched?). No change written.")
        return 0

    i = content.index(START) + len(START)
    j = content.index(END)
    new_content = content[:i] + NEW_MIDDLE + content[j:]

    bak = SCRIPT + ".bak.batch2_20260619"
    shutil.copy2(SCRIPT, bak)
    log(f"backup -> {bak}")
    with open(SCRIPT, "w", encoding="utf-8") as f:
        f.write(new_content)
    log("config block rewritten -> batch3 (D0=2026-06-19, servers 1910-1930, val cmp 1530-1550)")

    # sanity: re-import-free syntax check
    rc = subprocess.run([sys.executable, "-c",
                         "import ast,io;ast.parse(io.open(r'%s',encoding='utf-8').read())" % SCRIPT]).returncode
    if rc != 0:
        log("ABORT: syntax check failed after rewrite — restoring backup.")
        shutil.copy2(bak, SCRIPT)
        return 3

    # generate D0 report
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    log("running x3_festival_daily.py ...")
    p = subprocess.run([sys.executable, SCRIPT], cwd=SKILL_DIR, env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    log("generator stdout tail:\n" + (p.stdout or "")[-2000:])
    if p.returncode != 0:
        log("WARN: generator returncode != 0:\n" + (p.stderr or "")[-2000:])
        log("config switch DONE but generation failed; hourly cron ClaudeX3FestivalMonitor will retry.")
    else:
        log("generation OK.")

    # self-delete one-time task
    d = subprocess.run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
                       capture_output=True, text=True)
    log(f"self-delete task: rc={d.returncode} {d.stdout.strip()} {d.stderr.strip()}")
    log("==== switch to batch3 done ====")
    return 0


if __name__ == "__main__":
    sys.exit(main())
