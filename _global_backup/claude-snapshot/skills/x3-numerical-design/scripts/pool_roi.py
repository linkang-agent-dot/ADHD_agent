# -*- coding: utf-8 -*-
"""
奖池 EV / ROI 通用计算器（抽奖类活动数值设计标配工具）

用法：
    python pool_roi.py <池定义.json>
    python pool_roi.py --demo            # 跑内置马戏节扭蛋机样例

池定义 JSON 格式：
{
  "base": 125,                      # ROI 基准 = 单抽名义成本(钻)，通常=券的设计锚价
  "gem_usd": 0.002,                 # 钻→美元汇率（X3 实锤：$4.99 礼包给 2500 钻）
  "pools": [
    {"name": "付费池 82012", "target_pct": 700, "rows": [
        ["道具名", 单hit价值钻, 权重],
        ...
    ]}
  ]
}

为什么要这个工具（2026-07-29 马戏节扭蛋机血泪）：
  ★ EV 守恒 ≠ 体验守恒。删奖池行、把权重并给同类行时，期望值可以分文不差，
    但「最高单项命中率」会翻倍——玩家体感直接崩（57% 命中同一个道具＝10连里5.7格一样）。
    本工具每次都打印【最高单项命中率】就是为了强制看这个数，别只盯 EV。
    经验阈值：单项命中率 > 35% 就该警惕，> 50% 必然被玩家吐槽"怎么全是这个"。
"""
import sys, io, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOT_WARN = 35.0   # 单项命中率告警线(%)
HOT_BLOCK = 50.0  # 单项命中率红线(%)


def analyze(pool, base, gem_usd):
    name = pool.get("name", "奖池")
    target = pool.get("target_pct")
    rows = pool["rows"]
    tw = sum(r[2] for r in rows)
    if tw <= 0:
        raise ValueError(f"{name}: 总权重为 0")
    ev = sum(r[1] * r[2] / tw for r in rows)

    print(f"\n{'=' * 72}\n【{name}】  总权重 {tw}")
    print(f"{'道具':<24}{'权重':>6}{'命中%':>9}{'单hit钻':>10}{'EV钻':>9}{'EV占比':>8}")
    for n, v, w in rows:
        hit = w / tw * 100
        e = v * w / tw
        print(f"{n:<24}{w:>6}{hit:>8.2f}%{v:>10.0f}{e:>9.1f}"
              f"{(e / ev * 100 if ev else 0):>7.1f}%")
    print(f"{'合计':<24}{tw:>6}{'':>9}{'':>10}{ev:>9.1f}")

    pct = ev / base * 100 if base else 0
    line = f"  → ROI {pct:.1f}%"
    if target:
        line += f"  (目标 {target}%)  [{'OK' if abs(pct - target) < 6 else '偏离'}]"
    print(line + f"   ${ev * gem_usd:.3f}/抽")

    hot_n, hot_w = max(rows, key=lambda r: r[2])[0], max(r[2] for r in rows)
    hot = hot_w / tw * 100
    tag = "红线" if hot >= HOT_BLOCK else ("告警" if hot >= HOT_WARN else "OK")
    print(f"  → 最高单项命中率 {hot:.1f}%  ({hot_n})  [{tag}]")
    if hot >= HOT_WARN:
        print(f"     ⚠ 超过 {HOT_WARN}%：10连里平均 {hot / 10:.1f} 格是同一个道具，体感会被吐槽重复")
    return ev


def main():
    if "--demo" in sys.argv:
        cfg = DEMO
    elif len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        print(__doc__)
        return 1

    base, gem_usd = cfg.get("base", 125), cfg.get("gem_usd", 0.002)
    evs = [analyze(p, base, gem_usd) for p in cfg["pools"]]

    if len(evs) >= 2 and evs[0]:
        # 约定 pools[0]=付费池、pools[1]=免费池
        print(f"\n{'=' * 72}")
        print(f"免付比 = {evs[1] / evs[0] * 100:.1f}%   "
              f"(基准带：X2 15~29% / P2 11~18%；超上限=免费池超发)")
    return 0


# 内置样例 = 2026 马戏节扭蛋机重配平（付费700% / 免费150%），可当模板改
DEMO = {
    "base": 125, "gem_usd": 0.002,
    "pools": [
        {"name": "付费池 82012（改后）", "target_pct": 700, "rows": [
            ["罗盘×3", 750, 12],
            ["传奇技能书", 1000, 30],
            ["海妖经验(1142)×22500", 0.03 * 22500, 100],
            ["通用加速5m(11002)×10", (200 / 3) * 10, 100],
            ["船只强化材料×5", 500, 50],
            ["万能传奇信物", 5000, 10],
            ["外圈券1207×1", 2500, 5],
            ["内圈券1208×1", 2500, 5],
        ]},
        {"name": "免费池 82011（改后）", "target_pct": 150, "rows": [
            ["罗盘×1", 250, 15],
            ["招募加速5m×3", 200, 60],
            ["建造加速5m×3", 200, 45],
            ["研究加速5m×3", 200, 45],
            ["冒险阅历(1008)×10000", 0.03 * 10000, 50],
            ["硬木板(填充不计价)", 0, 50],
        ]},
    ],
}

if __name__ == "__main__":
    sys.exit(main())
