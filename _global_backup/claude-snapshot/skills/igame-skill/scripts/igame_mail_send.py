#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X3(1090) iGame 玩家邮件直发 CLI —— 等价于 UI「发玩家邮件」上传CSV，走 POST /ark/mails/send/players。

用法：
  1) 直接发 payload JSON（完整请求体，字段见 memory reference_x3_igame_mail_import.md）:
       python igame_mail_send.py payload.json            # dry-run 只打印
       python igame_mail_send.py payload.json --send     # 真发（生产!）
  2) 从 X3 导入 CSV（GBK 6列: 服务器 ID,玩家 ID,道具信息[ID*数量],...）+ 多语言内容构建并发送:
       python igame_mail_send.py --csv 补发.csv --content content.json --remark "xxx补发" [--valid-hours 1920] [--send]
     content.json 格式: {"ru": {"title": "...", "body": "..."}, "en": {"title": "...", "body": "..."}}
  3) 查邮件状态（detail status: 2=待审(要人在iGame后台放行) 1=已发送sentAt回填 3=驳回/撤回(不会再发!);
     workflow 流水: 8=提交 7=审批通过(审批人须非提交人,如龚亮) 0=发送中 1=已发送 3=驳回/撤回）:
       python igame_mail_send.py --status <mailId>
  4) 查发件箱最近 N 单: python igame_mail_send.py --outbox [N]

坑位：网关 success 只是登记；判真发出看 --status 的 sentAt/to[].failReason；最终以数仓入账为准。
"""
import argparse, csv, json, re, sys, urllib.request

# Windows GBK 控制台打不出非 GBK 字符(如法语«»)会让 dry-run 崩溃——强制 stdout/stderr UTF-8
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

GATEWAY = 'https://webgw-cn.tap4fun.com'
AUTH_FILE = r'C:\Users\linkang\.igame-auth.json'


def _headers():
    auth = json.load(open(AUTH_FILE))
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + auth['token'],
        'clientid': auth.get('clientId', ''),
        'gameid': str(auth.get('gameId', '1090')),
        'regionid': str(auth.get('regionId', '201')),
    }


def _call(method, path, body=None):
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req = urllib.request.Request(GATEWAY + path, data=data, headers=_headers(), method=method)
    resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read().decode('utf-8'))


def build_from_csv(csv_path, content_path, remark, valid_hours):
    to = []
    with open(csv_path, encoding='gbk') as f:
        rows = list(csv.reader(f))
    # ★自动判表头:X3导入CSV无表头(首列纯数字server_id),别当表头跳掉第1个玩家;有表头(首列非数字)才跳
    start = 1 if (rows and rows[0] and not rows[0][0].strip().isdigit()) else 0
    for row in rows[start:]:
        if not row or not row[0].strip():
            continue
        server_id, player_id, items = row[0].strip(), row[1].strip(), row[2].strip()
        assets = []
        for m in re.finditer(r'(\d+)\s*\*\s*(\d+)', items):
            assets.append({'assetType': 'PROP', 'id': m.group(1), 'amount': int(m.group(2))})
        if not assets:
            sys.exit(f'行解析不到道具: {row}')
        to.append({'serverId': server_id, 'playerId': player_id, 'assets': assets, 'extension': ''})
    langs = json.load(open(content_path, encoding='utf-8'))
    content = [{'lang': k, 'title': v['title'], 'body': v['body'], 'collectionId': -1} for k, v in langs.items()]
    return {
        'to': to, 'content': content, 'mailCategoryId': 1, 'sendType': -1,
        'validPeriod': valid_hours, 'customParams': '', 'rewardVersion': '', 'remark': remark,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('payload', nargs='?', help='payload JSON 文件')
    ap.add_argument('--csv', help='X3 导入 CSV(GBK 6列)')
    ap.add_argument('--content', help='多语言内容 JSON: {lang:{title,body}}')
    ap.add_argument('--remark', default='', help='后台备注(建议: 事由_人数张数_日期)')
    ap.add_argument('--valid-hours', type=int, default=1920, help='邮件有效期小时(默认1920=80天)')
    ap.add_argument('--send', action='store_true', help='真发。缺省 dry-run 只打印 payload')
    ap.add_argument('--status', type=int, help='查邮件单状态')
    ap.add_argument('--outbox', nargs='?', const=5, type=int, help='查发件箱最近N单')
    a = ap.parse_args()

    if a.status:
        print(json.dumps(_call('GET', f'/ark/mails/{a.status}'), ensure_ascii=False, indent=2))
        return
    if a.outbox:
        print(json.dumps(_call('POST', '/ark/mails', {'pageIndex': 1, 'pageSize': a.outbox}), ensure_ascii=False, indent=2))
        return

    if a.csv:
        if not a.content or not a.remark:
            sys.exit('--csv 模式必须带 --content 和 --remark')
        payload = build_from_csv(a.csv, a.content, a.remark, a.valid_hours)
    elif a.payload:
        payload = json.load(open(a.payload, encoding='utf-8'))
    else:
        ap.print_help(); return

    n_to = len(payload['to'])
    n_items = sum(x['amount'] for t in payload['to'] for x in t['assets'])
    print(f'收件 {n_to} 人 / 道具合计 {n_items} / 语言 {[c["lang"] for c in payload["content"]]} / remark={payload.get("remark","")}')
    if not a.send:
        print('--- DRY RUN(加 --send 真发, 生产操作先经用户确认) ---')
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    r = _call('POST', '/ark/mails/send/players', payload)
    print(json.dumps(r, ensure_ascii=False))
    if r.get('success'):
        # ★按刚设的remark精确匹配定位真实mailId;别盲取data[0](最顶可能别的草稿,曾误报V2礼包)。★翻页找:刚发的会被outbox里别的邮件(问卷奖励等)顶下去,单页30不够
        mine = []
        for pi in range(1, 8):
            box = _call('POST', '/ark/mails', {'pageIndex': pi, 'pageSize': 30})
            d = box.get('data', [])
            mine = [m for m in d if m.get('remark') == payload.get('remark')]
            if mine or len(d) < 30:
                break
        if mine:
            top = mine[0]
            print(f"已登记 mailId={top['id']} status={top['status']}(2=待审需去iGame放行) 收件={top.get('receiverCount')} remark={top['remark']}")
        else:
            print(f"已登记(网关success)·翻7页仍未按remark匹配到(outbox刷新延迟?)·稍后去发件箱按 remark='{payload.get('remark')}' 查真实mailId")


if __name__ == '__main__':
    main()
