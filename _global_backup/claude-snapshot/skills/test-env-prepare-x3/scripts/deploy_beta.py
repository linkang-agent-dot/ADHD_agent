#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X3 beta 服一条龙部署：Play+Map(+Center) 同批 deploy -> 等20s -> 复查 Status=Run -> Down 自动重试一次。

把 SKILL.md「部署铁律」4 条固化成一条命令，替代每次主会话现场编排（部署会话曾单次烧 $600-900）。

用法:
    python deploy_beta.py --server 220 --tag dev_festival           # Center 自动判断(换分支才带)
    python deploy_beta.py --server 320 --tag dev --center no        # 强制不带 Center
    python deploy_beta.py --server 220 --tag master --center yes    # 强制带 Center
    python deploy_beta.py --server 220 --query                      # 只查现状不部署

退出码: 0=全部 Run 且 tag 正确; 2=部署后仍有 Down/tag 不符(已重试一次); 1=参数/环境错误。
注意: 仅 beta kadmin (110-510)。dev(inner) 环境 / 本地服 3080 不走本脚本。
"""
import argparse
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, __file__.rsplit('\\', 1)[0] if '\\' in __file__ else '.')
from kadmin_api import deploy_app, query_app, app_history  # noqa: E402

# 主机拓扑: PlayService -> 同主机 CenterService（见 SKILL.md 服务器拓扑）
CENTER_MAP = {110: 61, 120: 61, 210: 62, 220: 62, 230: 62,
              310: 63, 320: 63, 330: 63, 500: 65, 510: 65}


def get_status(names):
    """返回 {Name: (Status, LastDeployTag)}"""
    r = query_app(name=names)
    out = {}
    for item in r.get('info', {}).get('list', []) or []:
        out[item.get('Name')] = (item.get('Status'), item.get('LastDeployTag'))
    return out


def report(status, names):
    for n in names:
        st, tag = status.get(n, ('未返回', '?'))
        print(f'  {n:<34} Status={st:<6} LastDeployTag={tag}')


def wait_all_run(names, tag, first_wait=20, polls=6, interval=10):
    time.sleep(first_wait)
    for i in range(polls):
        status = get_status(names)
        ok = all(status.get(n, ('', ''))[0] == 'Run' and status.get(n, ('', ''))[1] == tag for n in names)
        if ok:
            return True, status
        if i < polls - 1:
            time.sleep(interval)
    return False, status


def main():
    ap = argparse.ArgumentParser(description='X3 beta kadmin 一条龙部署（同批+复查+重试）')
    ap.add_argument('--server', type=int, required=True, help='Play 服号，如 220')
    ap.add_argument('--tag', help='分支 tag，如 dev / dev_festival / master')
    ap.add_argument('--center', choices=('auto', 'yes', 'no'), default='auto',
                    help='是否带同主机 Center（auto=换分支才带）')
    ap.add_argument('--query', action='store_true', help='只查现状不部署')
    args = ap.parse_args()

    s = args.server
    if s not in CENTER_MAP:
        print(f'[!] 未知服 {s}（beta 拓扑只有 {sorted(CENTER_MAP)}）；dev(inner)/本地服不走本脚本')
        return 1
    play, mp, center = f'default_PlayService_{s}', f'default_MapService_{s + 1}', f'default_CenterService_{CENTER_MAP[s]}'

    print(f'== 部署前现状 ==')
    pre = get_status([play, mp, center])
    report(pre, [play, mp, center])

    if args.query:
        return 0
    if not args.tag:
        print('[!] 部署需要 --tag')
        return 1

    # Center 决策：换分支必须带（代码版本一致铁律2）
    cur_tag = pre.get(play, ('', ''))[1]
    with_center = {'yes': True, 'no': False}.get(args.center, cur_tag != args.tag)
    names = [play, mp] + ([center] if with_center else [])
    print(f'\n== 部署 {names} -> tag={args.tag} （Center: {"带" if with_center else "不带"}'
          f'{"，当前tag=" + str(cur_tag) + " 判定" if args.center == "auto" else ""}）==')

    for attempt in (1, 2):
        r = deploy_app(name=names, tag=args.tag)
        hist = [x.get('applicationDeployHistoryId') for x in r.get('info', {}).get('nameStatus', []) or []]
        print(f'已提交（history={hist}），等 20s 后复查...')
        ok, status = wait_all_run(names, args.tag)
        print(f'== 第{attempt}次部署后状态 ==')
        report(status, names)
        if ok:
            print('\n[OK] 全部 Status=Run 且 tag 正确。')
            return 0
        if attempt == 1:
            bad = [n for n in names if status.get(n, ('', ''))[0] != 'Run']
            print(f'\n[!] {bad} 未达 Run，自动重试一次...')
    print('\n[FAIL] 重试后仍未全部 Run，需要人工排查（kadmin 界面看容器日志 / 镜像是否存在该 tag）。')
    return 2


if __name__ == '__main__':
    sys.exit(main())
