#!/usr/bin/env python3
"""Lookup player UDID by userId from iGame gateway."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = "https://ms-inner-gateway-dev.tap4fun.com/ark/game/players"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query player UDID by userId.")
    parser.add_argument("--user-id", required=True, help="Player userId")
    parser.add_argument("--token", default="", help="Bearer token without prefix")
    parser.add_argument("--clientid", default="", help="iGame clientid")
    parser.add_argument("--gameid", default="1090", help="Game ID header (default: X3)")
    parser.add_argument("--regionid", default="201", help="Region ID header (default: 201)")
    parser.add_argument("--auth-file", default="~/.igame-auth.json", help="Auth JSON path")
    return parser.parse_args()


def load_auth(path_text: str) -> dict[str, Any]:
    auth_path = Path(os.path.expanduser(path_text))
    if not auth_path.exists():
        return {}
    try:
        return json.loads(auth_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    args = parse_args()
    auth = load_auth(args.auth_file)

    token = args.token or str(auth.get("token", ""))
    clientid = args.clientid or str(auth.get("clientId", ""))
    gameid = str(args.gameid or auth.get("gameId", "1090"))
    regionid = str(args.regionid or auth.get("regionId", "201"))

    if not token or not clientid:
        print("Missing token/clientid. Pass --token/--clientid or prepare ~/.igame-auth.json", file=sys.stderr)
        return 2

    query = urllib.parse.urlencode(
        {
            "keywords": args.user_id,
            "type": 1,
            "pageIndex": 1,
            "pageSize": 100,
        }
    )
    url = f"{BASE_URL}?{query}"
    headers = {
        "accept": "*/*",
        "authorization": f"Bearer {token}",
        "clientid": clientid,
        "gameid": gameid,
        "regionid": regionid,
        "origin": "https://igame-dev.tap4fun.com",
        "referer": "https://igame-dev.tap4fun.com/",
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

    if not payload.get("success"):
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        return 1

    data = payload.get("data") or []
    if not data:
        print(json.dumps({"success": False, "message": "No player found"}, ensure_ascii=False), file=sys.stderr)
        return 1

    player = data[0]
    result = {
        "userId": player.get("userId"),
        "udid": player.get("udid"),
        "userName": player.get("userName"),
        "serverId": player.get("serverId"),
        "serverName": player.get("serverName"),
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
