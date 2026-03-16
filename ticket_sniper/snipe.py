#!/usr/bin/env python3
"""
大麦 App 抢票脚本 - CLI 入口

用法:
    python snipe.py                          # 使用 config.yaml
    python snipe.py --time "2026-03-15 10:00:00"
    python snipe.py --ticket "580" --count 2
"""

import argparse
import sys
from pathlib import Path

import yaml

from engine import DamaiAppSniper


def load_config(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"配置文件不存在: {path}")
        sys.exit(1)
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def apply_overrides(config: dict, args: argparse.Namespace) -> dict:
    if args.url:
        config["share_url"] = args.url
    if args.time:
        config["start_time"] = args.time
    if args.ticket:
        config["wanted_tickets"] = [args.ticket]
    if args.count:
        config["ticket_count"] = args.count
    if args.device:
        config["device_addr"] = args.device
    return config


def print_banner(config: dict):
    print()
    print("╔══════════════════════════════════════════╗")
    print("║       大 麦 App 抢 票 脚 本              ║")
    print("╚══════════════════════════════════════════╝")
    print()
    print(f"  设备:   {config.get('device_addr', '自动检测')}")
    url = config.get("share_url", "")
    import re
    m = re.search(r"itemId=(\d+)", url)
    print(f"  演出ID: {m.group(1) if m else '未设置'}")
    start = config.get("start_time", "")
    print(f"  时间:   {start if start else '立即开始'}")
    wanted = config.get("wanted_tickets", [])
    print(f"  票档:   {', '.join(w for w in wanted if w) or '自动'}")
    print(f"  数量:   {config.get('ticket_count', 1)} 张")
    buyers = config.get("buyers", [])
    print(f"  购票人: {', '.join(b for b in buyers if b) or '默认'}")
    print()
    print("  流程: 连接设备 → 打开大麦 → 跳转演出 → 选票 → 购买 → 提交")
    print()
    print("─" * 44)
    print()


def main():
    parser = argparse.ArgumentParser(description="大麦 App 抢票脚本")
    parser.add_argument("-c", "--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--url", help="演出分享链接")
    parser.add_argument("--time", help='抢购时间 "YYYY-MM-DD HH:MM:SS"')
    parser.add_argument("--ticket", help="票档关键词（如 580）")
    parser.add_argument("--count", type=int, help="购票数量")
    parser.add_argument("--device", help="设备地址（如 127.0.0.1:7555）")
    args = parser.parse_args()

    config = load_config(args.config)
    config = apply_overrides(config, args)

    print_banner(config)

    sniper = DamaiAppSniper(config)
    try:
        sniper.run()
    except KeyboardInterrupt:
        print("\n已退出")
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n常见问题排查:")
        print("  1. ADB 是否已安装？运行: adb devices")
        print("  2. 模拟器是否已启动？")
        print("  3. 大麦 App 是否已安装在模拟器/手机上？")
        print("  4. device_addr 是否正确？")
        sys.exit(1)


if __name__ == "__main__":
    main()
