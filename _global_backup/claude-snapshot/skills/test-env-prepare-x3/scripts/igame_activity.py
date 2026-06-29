#!/usr/bin/env python3
"""iGame 活动管理 API — 创建/查询跨服活动。"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

SUBMIT_ENDPOINTS = {
    "dev": "https://ms-inner-gateway-dev.tap4fun.com/ark/activity/submit",
    "beta": "https://ms-inner-gateway-qa.tap4fun.com/ark/activity/submit",
}

LIST_ENDPOINTS = {
    "dev": "https://ms-inner-gateway-dev.tap4fun.com/ark/activity/list",
    "beta": "https://ms-inner-gateway-qa.tap4fun.com/ark/activity/list",
}

ORIGINS = {
    "dev": "https://igame-dev.tap4fun.com",
    "beta": "https://igame-qa.tap4fun.com",
}

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def load_auth(auth_file: str = "~/.igame-credentials.json") -> tuple[str, str]:
    path = Path(auth_file).expanduser()
    with path.open("r", encoding="utf-8") as f:
        auth = json.load(f)
    return auth["token"].strip(), auth["clientId"].strip()


def _headers(token: str, client_id: str, env: str) -> dict:
    return {
        "authorization": f"Bearer {token}",
        "clientid": client_id,
        "content-type": "application/json",
        "gameid": "1090",
        "regionid": "201",
        "origin": ORIGINS[env],
        "referer": f"{ORIGINS[env]}/",
    }


def submit_activity(env: str, headers: dict, cfg_id: str, name: str,
                    servers: list[list[str]], start_time: int, end_time: int,
                    across_server: int = 1, across_server_rank: int = 1,
                    end_show_time: int = 30, preview_time: int = 0) -> dict:
    """创建活动。endShowTime 是结束后展示分钟数(默认30)，previewTime 默认0。"""
    body = json.dumps([{
        "activityConfigId": cfg_id,
        "name": name,
        "acrossServer": across_server,
        "acrossServerRank": across_server_rank,
        "startTime": start_time,
        "endTime": end_time,
        "endShowTime": end_show_time,
        "previewTime": preview_time,
        "servers": servers,
    }]).encode()

    req = urllib.request.Request(SUBMIT_ENDPOINTS[env], data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        return json.loads(resp.read())


def list_activities(env: str, headers: dict, page: int = 1, size: int = 10) -> dict:
    """查询活动列表。"""
    url = f"{LIST_ENDPOINTS[env]}?pageIndex={page}&pageSize={size}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
        return json.loads(resp.read())


def main() -> int:
    parser = argparse.ArgumentParser(description="iGame 活动管理")
    sub = parser.add_subparsers(dest="cmd")

    c = sub.add_parser("create", help="创建活动")
    c.add_argument("--cfg-id", required=True, help="活动配置ID (如 100702)")
    c.add_argument("--name", required=True, help="活动名称 (如 酒馆争霸)")
    c.add_argument("--servers", required=True, help="跨服分组，逗号分隔 (如 220,230)")
    c.add_argument("--start", type=int, required=True, help="开始时间戳(ms)")
    c.add_argument("--end", type=int, required=True, help="结束时间戳(ms)")
    c.add_argument("--across-server", type=int, default=1, help="是否跨服 (default 1)")
    c.add_argument("--across-rank", type=int, default=1, help="是否跨服排名 (default 1)")
    c.add_argument("--env", choices=("dev", "beta"), default="beta")
    c.add_argument("--auth-file", default="")

    l = sub.add_parser("list", help="查询活动列表")
    l.add_argument("--page", type=int, default=1)
    l.add_argument("--size", type=int, default=10)
    l.add_argument("--env", choices=("dev", "beta"), default="beta")
    l.add_argument("--auth-file", default="")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0

    auth_file = args.auth_file or ("~/.igame-credentials-dev.json" if args.env == "dev" else "~/.igame-credentials.json")
    token, client_id = load_auth(auth_file)
    headers = _headers(token, client_id, args.env)

    if args.cmd == "create":
        servers = [[s.strip() for s in args.servers.split(",")]]
        result = submit_activity(args.env, headers, args.cfg_id, args.name,
                                 servers, args.start, args.end,
                                 args.across_server, args.across_rank)
        if result.get("success"):
            print(f"创建成功: activity_id={result['data']}")
        else:
            print(f"创建失败: {result.get('message')}", file=sys.stderr)
            return 1

    elif args.cmd == "list":
        result = list_activities(args.env, headers, args.page, args.size)
        for a in result.get("data", []):
            status = a.get("status")
            print(f"ID={a['id']} cfg={a['activityConfigId']} name={a.get('name','')} "
                  f"status={status} servers={a.get('servers','')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
