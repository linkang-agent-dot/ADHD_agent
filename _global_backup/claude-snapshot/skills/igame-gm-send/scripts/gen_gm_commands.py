#!/usr/bin/env python3
"""【只生成不执行】把玩家名单 → 批量加分 GM 命令清单 txt，供人工审核后再跑。

用途(世界杯竞猜结算周末流程)：ai-to-sql 查出买了指定订单的玩家 → 本脚本生成 GM 命令清单 →
人工过目无误 → 再用 batch_add_score.py 真发。本脚本【绝不调用网关、不加分】。

输入玩家名单(二选一)：
  --players "27798,27843,27877"     逗号分隔玩家id
  --players-file buyers.txt         每行一个玩家id(# 和空行忽略;可直接喂 ai-to-sql 导出的一列)
必填：
  --server 3080         服号
  --activity 7655210947394404352   活动【运行时雪花id】(世界杯BP=7655210947394404352)
  --score 600           每人加多少分
可选：
  --activity-name "世界杯BP" --note "R32 巴西vs德国 $4.99档 猜中结算"
  --out <txt路径>(默认 scratchpad)  --cmd addactivityscore

输出 txt 含：①汇总 ②batch csv(直接存文件喂 batch_add_score.py) ③每人 gmCommand JSON ④确认后的运行命令。
"""
from __future__ import annotations
import argparse, json, sys, pathlib


def load_players(a):
    ids = []
    if a.players:
        ids = [x.strip() for x in a.players.split(",") if x.strip()]
    elif a.players_file:
        for ln in pathlib.Path(a.players_file).read_text(encoding="utf-8-sig").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and ln.lstrip("-").isdigit():
                ids.append(ln)
    # 去重保序
    seen, out = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i); out.append(i)
    return out


def main():
    ap = argparse.ArgumentParser(description="生成批量加分GM命令清单(不执行)")
    ap.add_argument("--players"); ap.add_argument("--players-file")
    ap.add_argument("--server", required=True)
    ap.add_argument("--activity", required=True)
    ap.add_argument("--score", required=True)
    ap.add_argument("--activity-name", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--cmd", default="addactivityscore")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    players = load_players(a)
    if not players:
        print("没有玩家id。用 --players 或 --players-file。", file=sys.stderr); return 2

    csv_lines = [f"{a.server},{p},{a.activity},{a.score}" for p in players]
    L = []
    L.append("=" * 64)
    L.append("批量加活动/BP积分 GM 命令清单  [仅供审核 · 未执行]")
    L.append("=" * 64)
    L.append(f"服号(serverId)   : {a.server}")
    L.append(f"活动(雪花id)     : {a.activity}  {a.activity_name}")
    L.append(f"每人加分(score)  : {a.score}")
    L.append(f"GM命令(cmd)      : {a.cmd}  (= GMAddActivityScore)")
    L.append(f"玩家数           : {len(players)}")
    if a.note:
        L.append(f"备注             : {a.note}")
    L.append("")
    L.append("-" * 64)
    L.append("① batch csv（存成 .csv 喂 batch_add_score.py --csv）")
    L.append("-" * 64)
    L.append("# serverId,playerId,activityId,score")
    L.extend(csv_lines)
    L.append("")
    L.append("-" * 64)
    L.append("② iGame GM 输入框命令（可整块复制粘贴，一行一条，； 分隔）")
    L.append("-" * 64)
    for p in players:
        inner = json.dumps({"serverIds": str(a.server), "cmd": a.cmd,
                            "playerIds": str(p), "args": [str(a.activity), str(a.score)]},
                           ensure_ascii=False)
        L.append(inner + "；")
    L.append("")
    L.append("-" * 64)
    L.append("③ 审核无误后 · 真执行命令（届时由人工/确认后运行）")
    L.append("-" * 64)
    L.append("# 把上面 ① 的 csv 存为 settle.csv，然后：")
    L.append("python C:/Users/linkang/.claude/skills/igame-gm-send/scripts/batch_add_score.py --csv settle.csv --env dev")
    L.append("# (脚本逐条发 + 自动查 gm-operate/detail 核 errCode=0，最后汇总成功/失败)")
    L.append("")
    L.append("⚠️ 本清单未执行任何加分。活动id 必须是运行时雪花号(非配置号102243)。")
    txt = "\n".join(L)

    out = a.out or ("C:/Users/linkang/AppData/Local/Temp/claude/C--Users-linkang/"
                    "9da95be6-425a-409d-8285-149ff9642852/scratchpad/gm_commands_preview.txt")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out).write_text(txt, encoding="utf-8")
    print(txt)
    print(f"\n[已写出] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
