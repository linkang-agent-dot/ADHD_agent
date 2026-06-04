#!/usr/bin/env python3
"""Send a GM command through iGame backend gm-operate API."""

from __future__ import annotations

import argparse
import json
import sys
import pathlib
import urllib.error
import urllib.request

ENDPOINTS = {
    "beta": "https://ms-inner-gateway-qa.tap4fun.com/ark/gm-operate/add",
    "dev": "https://ms-inner-gateway-dev.tap4fun.com/ark/gm-operate/add",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send GM command by iGame gm-operate/add.")
    parser.add_argument("--server", required=True, help="Server ID, e.g. 402")
    parser.add_argument(
        "--players",
        default="",
        help='Comma-separated player IDs, e.g. "12345,23456". Empty means []',
    )
    parser.add_argument("--cmd", required=True, help="GM command name only")
    parser.add_argument(
        "--args",
        default="",
        help='Comma-separated args, e.g. "11151001,100000"',
    )
    parser.add_argument(
        "--env",
        choices=("beta", "dev"),
        default="dev",
        help="Target environment (default: dev)",
    )
    parser.add_argument(
        "--operate-type",
        type=int,
        default=3,
        help="operateType for gm-operate/add (default: 3)",
    )
    parser.add_argument(
        "--auth-file",
        default="C:/Users/linkang/.igame-auth.json",
        help='Auth json path with {"token":"...","clientId":"..."}',
    )
    parser.add_argument("--gameid", default="1090", help="Header gameid (default: 1090)")
    parser.add_argument("--regionid", default="201", help="Header regionid (default: 201)")
    return parser.parse_args()


def parse_csv_int(csv_text: str) -> list[int]:
    if not csv_text.strip():
        return []
    values: list[int] = []
    for token in csv_text.split(","):
        token = token.strip()
        if not token:
            continue
        values.append(int(token))
    return values


def parse_csv_str(csv_text: str) -> list[str]:
    if not csv_text.strip():
        return []
    return [token.strip() for token in csv_text.split(",") if token.strip()]


def load_auth(auth_file: str) -> tuple[str, str]:
    path = pathlib.Path(auth_file)
    with path.open("r", encoding="utf-8") as fp:
        auth = json.load(fp)
    token = (auth.get("token") or "").strip()
    client_id = (auth.get("clientId") or "").strip()
    if not token or not client_id:
        raise ValueError("auth file must contain token and clientId")
    return token, client_id


def main() -> int:
    args = parse_args()
    endpoint = ENDPOINTS[args.env]
    origin = "https://igame-qa.tap4fun.com" if args.env == "beta" else "https://igame-dev.tap4fun.com"

    try:
        players = parse_csv_int(args.players)
    except ValueError:
        print("Invalid --players: must be integers separated by commas.", file=sys.stderr)
        return 2

    gm_line_obj = {
        "server_ids": [int(args.server)],
        "cmd": args.cmd.strip(),
        "players": players,
        "args": parse_csv_str(args.args),
    }
    gm_line = json.dumps(gm_line_obj, ensure_ascii=False)
    if not gm_line.endswith((";", "；")):
        gm_line += "；"

    payload = {
        "operateType": args.operate_type,
        "gmCommand": [gm_line],
    }

    try:
        token, client_id = load_auth(args.auth_file)
    except FileNotFoundError:
        print(f"Auth file not found: {args.auth_file}", file=sys.stderr)
        return 2
    except (json.JSONDecodeError, ValueError) as error:
        print(f"Invalid auth file: {error}", file=sys.stderr)
        return 2

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "accept": "*/*",
            "authorization": f"Bearer {token}",
            "clientid": client_id,
            "content-type": "application/json",
            "gameid": str(args.gameid),
            "regionid": str(args.regionid),
            "origin": origin,
            "referer": f"{origin}/",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        text = error.read().decode("utf-8", errors="replace")
        print(text, file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(str(error.reason), file=sys.stderr)
        return 1

    print(text)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return 1

    if obj.get("success") is True:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
