#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X3 常用 GM 组合命令：把「查服务器时间 -> 换算时间戳 -> 开活动」等多步固定组合做成一条命令。

背景: deployserveractivity 要 Unix 秒级时间戳，且服务器时间常被推进过——手动估算时间戳是
SKILL.md 明令禁止的高频翻车点。本脚本自动 getservertime + calendar.timegm 换算。

用法:
    # 开单服活动：自动取服务器时间为起点，持续 N 天
    python gm_combo.py open-activity --server 330 --player 14000 --actv 102993 --days 7 --env beta

    # 查服务器当前(逻辑)时间
    python gm_combo.py servertime --server 330 --player 14000 --env beta

参数说明:
    --player  getservertime 是玩家级 GM，必须给该服任一玩家ID（deployserveractivity 本身不用）
    --days/--hours  持续时长（可叠加）
    --start-offset-sec  开始时间相对服务器当前时间的偏移（默认 60s，给部署留缓冲）
"""
import argparse
import calendar
import re
import sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, __file__.rsplit('\\', 1)[0] if '\\' in __file__ else '.')
from gm_execute import load_auth, make_headers, submit_gm, query_result  # noqa: E402


def run_gm(env, headers, cmd, gm_args, server, player=''):
    gm_id = submit_gm(env, headers, cmd, gm_args, server, player)
    if gm_id < 0:
        return None
    result = query_result(env, headers, gm_id)
    if result is None:
        print(f'[!] {cmd} 提交成功(id={gm_id})但查不到执行结果', file=sys.stderr)
        return None
    return result


def get_server_time(env, headers, server, player):
    """返回 (datetime, 原始串)；失败返回 (None, err)"""
    r = run_gm(env, headers, 'getservertime', [], server, player)
    if r is None:
        return None, 'GM 执行失败'
    blob = str(r)
    m = re.search(r'(\d{4}-\d{2}-\d{2}/\d{2}:\d{2}:\d{2})', blob)
    if not m:
        return None, f'返回里没找到时间串: {blob[:300]}'
    return datetime.strptime(m.group(1), '%Y-%m-%d/%H:%M:%S'), m.group(1)


def main():
    ap = argparse.ArgumentParser(description='X3 GM 组合命令')
    sub = ap.add_subparsers(dest='op', required=True)

    p1 = sub.add_parser('servertime', help='查服务器逻辑时间')
    p2 = sub.add_parser('open-activity', help='getservertime -> 换算时间戳 -> deployserveractivity')
    p3 = sub.add_parser('advance-time', help='推进服务器时间(跨天用, setservertimebydhms, 不支持回退)')
    for p in (p1, p2, p3):
        p.add_argument('--server', required=True)
        p.add_argument('--player', required=True, help='该服任一玩家ID（玩家级 GM 需要）')
        p.add_argument('--env', choices=('dev', 'beta'), default='beta')
    p2.add_argument('--actv', required=True, help='ActvOnline 活动ID')
    p2.add_argument('--days', type=float, default=0)
    p2.add_argument('--hours', type=float, default=0)
    p2.add_argument('--start-offset-sec', type=int, default=60)
    p3.add_argument('--days', type=int, default=0)
    p3.add_argument('--hours', type=int, default=0)
    p3.add_argument('--minutes', type=int, default=0)
    p3.add_argument('--target', type=int, choices=(0, 1, 2), default=1,
                    help='0=Game+Center同步(需Center支持) 1=仅Game(推荐) 2=仅Center')
    args = ap.parse_args()

    auth_file = '~/.igame-credentials-dev.json' if args.env == 'dev' else '~/.igame-credentials.json'
    token, client_id = load_auth(auth_file)
    headers = make_headers(token, client_id, args.env)

    dt, raw = get_server_time(args.env, headers, args.server, args.player)
    if dt is None:
        print(f'[!] 取服务器时间失败: {raw}', file=sys.stderr)
        return 1
    print(f'服务器 {args.server} 当前逻辑时间: {raw}（注意可能被时移过，勿与本机时间比对）')

    if args.op == 'servertime':
        return 0

    if args.op == 'advance-time':
        if args.days == args.hours == args.minutes == 0:
            print('[!] advance-time 需要 --days/--hours/--minutes（只能往前推，不支持回退）', file=sys.stderr)
            return 1
        r = run_gm(args.env, headers, 'setservertimebydhms',
                   [str(args.days), str(args.hours), str(args.minutes), '0', str(args.target)],
                   args.server, args.player)
        if r is None or r.get('errMsg'):
            print(f'[FAIL] {r}', file=sys.stderr)
            return 1
        dt2, raw2 = get_server_time(args.env, headers, args.server, args.player)
        print(f'[OK] 推进 +{args.days}d{args.hours}h{args.minutes}m (target={args.target})，'
              f'现服务器时间: {raw2 if dt2 else "复查失败,手动 servertime 确认"}')
        return 0

    dur = timedelta(days=args.days, hours=args.hours)
    if dur.total_seconds() <= 0:
        print('[!] open-activity 需要 --days 或 --hours', file=sys.stderr)
        return 1
    start_ts = calendar.timegm(dt.timetuple()) + args.start_offset_sec
    end_ts = start_ts + int(dur.total_seconds())
    print(f'开活动 {args.actv}: start={start_ts} ({dt + timedelta(seconds=args.start_offset_sec)}) '
          f'end={end_ts} ({dt + timedelta(seconds=args.start_offset_sec) + dur})  [服务器时钟]')

    r = run_gm(args.env, headers, 'deployserveractivity',
               [str(args.actv), str(start_ts), str(end_ts)], args.server)
    if r is None:
        return 1
    err = r.get('errMsg', '')
    info = r.get('returnInfo', '')
    if r.get('status') and not err:
        print(f'[OK] deployserveractivity 成功: {info}')
        return 0
    print(f'[FAIL] errMsg={err} returnInfo={info}', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
