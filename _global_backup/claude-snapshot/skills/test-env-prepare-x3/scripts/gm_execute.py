#!/usr/bin/env python3
"""Execute GM commands on X3 servers via iGame gateway."""

from __future__ import annotations

import argparse
import json
import pathlib
import ssl
import sys
import time
import urllib.error
import urllib.request

ENDPOINTS = {
    "dev": "https://ms-inner-gateway-dev.tap4fun.com/ark/gm-operate/add",
    "beta": "https://ms-inner-gateway-qa.tap4fun.com/ark/gm-operate/add",
}

DETAIL_ENDPOINTS = {
    "dev": "https://ms-inner-gateway-dev.tap4fun.com/ark/gm-operate/detail",
    "beta": "https://ms-inner-gateway-qa.tap4fun.com/ark/gm-operate/detail",
}

ORIGINS = {
    "dev": "https://igame-dev.tap4fun.com",
    "beta": "https://igame-qa.tap4fun.com",
}

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def load_auth(auth_file: str) -> tuple[str, str]:
    path = pathlib.Path(auth_file).expanduser()
    with path.open("r", encoding="utf-8") as f:
        auth = json.load(f)
    token = auth.get("token", "").strip()
    client_id = auth.get("clientId", "").strip()
    if not token or not client_id:
        raise ValueError(f"auth file must contain token and clientId: {path}")
    return token, client_id


def make_headers(token: str, client_id: str, env: str) -> dict:
    return {
        "authorization": f"Bearer {token}",
        "clientid": client_id,
        "content-type": "application/json",
        "gameid": "1090",
        "regionid": "201",
        "origin": ORIGINS[env],
        "referer": f"{ORIGINS[env]}/",
    }


def submit_gm(env: str, headers: dict, cmd: str, args: list[str], server_id: str, player_id: str) -> int:
    gm_obj = {"cmd": cmd, "args": args, "serverIds": server_id}
    if player_id:
        gm_obj["playerIds"] = player_id

    gm_line = json.dumps(gm_obj, ensure_ascii=False)
    payload = json.dumps({"operateType": 3, "gmCommand": [gm_line]}, ensure_ascii=False).encode()

    req = urllib.request.Request(ENDPOINTS[env], data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        result = json.loads(resp.read().decode())

    if not result.get("success"):
        print(f"Submit failed: {result.get('message') or result.get('code')}", file=sys.stderr)
        return -1

    return result["data"]["id"]


def query_result(env: str, headers: dict, gm_id: int, retries: int = 5) -> dict | None:
    url = f"{DETAIL_ENDPOINTS[env]}?id={gm_id}"
    for i in range(retries):
        time.sleep(2 if i == 0 else 3)
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
            result = json.loads(resp.read().decode())
        contents = result.get("data", {}).get("contents", [])
        if contents:
            return contents[0]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute X3 GM command via iGame gateway")
    parser.add_argument("--server", required=True, help="Server ID (e.g. 330)")
    parser.add_argument("--player", default="", help="Player ID (e.g. 14000). Empty for server-level commands")
    parser.add_argument("--cmd", required=True, help="GM command name (e.g. additem)")
    parser.add_argument("--args", default="", help="Comma-separated args (e.g. 230004,50,0)")
    parser.add_argument("--env", choices=("dev", "beta"), default="beta", help="Environment (default: beta)")
    parser.add_argument("--auth-file", default="", help="Auth JSON path (auto-selects by env if empty)")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for execution result")
    args = parser.parse_args()

    auth_file = args.auth_file or ("~/.igame-credentials-dev.json" if args.env == "dev" else "~/.igame-credentials.json")

    try:
        token, client_id = load_auth(auth_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Auth error: {e}", file=sys.stderr)
        return 2

    headers = make_headers(token, client_id, args.env)
    cmd_args = [a.strip() for a in args.args.split(",") if a.strip()] if args.args else []

    gm_id = submit_gm(args.env, headers, args.cmd, cmd_args, args.server, args.player)
    if gm_id < 0:
        return 1

    print(f"Submitted: id={gm_id} cmd={args.cmd} server={args.server} player={args.player or '(none)'}")

    if args.no_wait:
        return 0

    result = query_result(args.env, headers, gm_id)
    if result is None:
        print("Timeout: no execution result after retries", file=sys.stderr)
        return 1

    status = result.get("status")
    return_info = result.get("returnInfo", "")
    err_msg = result.get("errMsg", "")

    if status and not err_msg:
        print(f"Success: {return_info}")
        return 0
    else:
        print(f"Failed: errMsg={err_msg} returnInfo={return_info}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
