#!/usr/bin/env python3
"""Query iGame player basic info by serverId + userId."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ENDPOINTS = {
    "beta": "https://ms-inner-gateway-qa.tap4fun.com/ark/game_info/{user_id}/basic",
    "dev": "https://ms-inner-gateway-dev.tap4fun.com/ark/game_info/{user_id}/basic",
}

ORIGINS = {
    "beta": "https://igame-qa.tap4fun.com",
    "dev": "https://igame-dev.tap4fun.com",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query iGame player info.")
    parser.add_argument("--server-id", default="", help="Server ID, e.g. 402")
    parser.add_argument("--user-id", default="", help="Player userId, e.g. 27438")
    parser.add_argument(
        "--player-url",
        default="",
        help="Player page URL, e.g. https://igame-dev.tap4fun.com/#/info/player/402/27438",
    )
    parser.add_argument("--env", choices=("beta", "dev"), default="dev", help="Environment")
    parser.add_argument("--token", default="", help="Bearer token without prefix")
    parser.add_argument("--clientid", default="", help="iGame clientid")
    parser.add_argument("--gameid", default="1090", help="Game ID header (default X3=1090)")
    parser.add_argument("--regionid", default="201", help="Region ID header (default 201)")
    parser.add_argument("--auth-file", default="~/.igame-auth.json", help="Auth JSON path")
    parser.add_argument("--raw", action="store_true", help="Print full API payload")
    return parser.parse_args()


def load_auth(path_text: str) -> dict[str, Any]:
    auth_path = Path(os.path.expanduser(path_text))
    if not auth_path.exists():
        return {}
    try:
        return json.loads(auth_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def parse_ids_from_url(player_url: str) -> tuple[str, str]:
    match = re.search(r"/info/player/(\d+)/(\d+)", player_url)
    if not match:
        return "", ""
    return match.group(1), match.group(2)


def format_result(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "userId": data.get("userId"),
        "userName": data.get("userName"),
        "serverId": data.get("serverId"),
        "serverName": data.get("serverName"),
        "playerLevel": data.get("playerLevel"),
        "mainCastleLevel": data.get("mainCastleLevel"),
        "power": data.get("power"),
        "vipLevel": data.get("vipLevel"),
        "totalCharge": data.get("totalCharge"),
        "lastLoginTime": data.get("lastLoginTime"),
        "registerUdid": data.get("registerUdid"),
        "loginUdid": data.get("loginUdid"),
        "accountStatus": data.get("accountStatus"),
        "chatStatus": data.get("chatStatus"),
        "accountId": data.get("accountId"),
        "characterId": data.get("characterId"),
    }


def main() -> int:
    args = parse_args()
    auth = load_auth(args.auth_file)
    server_id = str(args.server_id).strip()
    user_id = str(args.user_id).strip()

    if args.player_url:
        parsed_server, parsed_user = parse_ids_from_url(args.player_url)
        server_id = server_id or parsed_server
        user_id = user_id or parsed_user

    if not server_id or not user_id:
        print(
            "Missing IDs. Pass --server-id + --user-id, or provide --player-url.",
            file=sys.stderr,
        )
        return 2

    token = args.token or str(auth.get("token", "")).strip()
    clientid = args.clientid or str(auth.get("clientId", "")).strip()
    gameid = str(args.gameid or auth.get("gameId", "1090"))
    regionid = str(args.regionid or auth.get("regionId", "201"))

    if not token or not clientid:
        print(
            "Missing token/clientid. Pass --token/--clientid or prepare ~/.igame-auth.json",
            file=sys.stderr,
        )
        return 2

    base = ENDPOINTS[args.env].format(user_id=urllib.parse.quote(user_id))
    url = f"{base}?{urllib.parse.urlencode({'serverId': server_id})}"
    origin = ORIGINS[args.env]
    headers = {
        "accept": "*/*",
        "authorization": f"Bearer {token}",
        "clientid": clientid,
        "gameid": gameid,
        "regionid": regionid,
        "origin": origin,
        "referer": f"{origin}/",
    }

    request = urllib.request.Request(url=url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8", errors="replace")
            payload = json.loads(raw)
    except urllib.error.HTTPError as error:
        text = error.read().decode("utf-8", errors="replace")
        print(text, file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(str(error.reason), file=sys.stderr)
        return 1
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload.get("success") else 1

    if not payload.get("success"):
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        return 1

    data = payload.get("data") or {}
    if not isinstance(data, dict) or not data:
        print(json.dumps({"success": False, "message": "No player info found"}, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps(format_result(data), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
