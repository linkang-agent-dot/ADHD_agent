#!/usr/bin/env python3
"""Submit one iGame activity deployment payload to iGame gateway."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


DEFAULT_URL = "https://ms-inner-gateway-dev.tap4fun.com/ark/activity/submit"
DEFAULT_ORIGIN = "https://igame-dev.tap4fun.com"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit iGame activity deployment.")
    parser.add_argument("--token", required=True, help="Bearer token without Bearer prefix")
    parser.add_argument("--clientid", required=True, help="iGame clientid header value")
    parser.add_argument("--activity-config-id", required=True, help="Activity config ID")
    parser.add_argument("--name", required=True, help="Activity name")
    parser.add_argument("--server", required=True, help="Single target server id, e.g. 403")
    parser.add_argument("--start-ms", type=int, required=True, help="Start epoch milliseconds")
    parser.add_argument("--end-ms", type=int, required=True, help="End epoch milliseconds")
    parser.add_argument("--preview-ms", type=int, default=0, help="previewTime")
    parser.add_argument("--end-show-ms", type=int, default=0, help="endShowTime")
    parser.add_argument("--across-server", type=int, default=0, help="acrossServer")
    parser.add_argument("--across-server-rank", type=int, default=1, help="acrossServerRank")
    parser.add_argument("--gameid", default="1090", help="Game ID header (default X3=1090)")
    parser.add_argument("--regionid", default="201", help="Region ID header (default 201)")
    parser.add_argument("--url", default=DEFAULT_URL, help="Submit endpoint URL")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN, help="Origin header value")
    parser.add_argument("--referer", default=f"{DEFAULT_ORIGIN}/", help="Referer header value")
    return parser.parse_args()


def build_payload(args: argparse.Namespace) -> list[dict]:
    return [
        {
            "activityConfigId": args.activity_config_id,
            "previewTime": args.preview_ms,
            "startTime": args.start_ms,
            "endTime": args.end_ms,
            "endShowTime": args.end_show_ms,
            "acrossServerRank": args.across_server_rank,
            "acrossServer": args.across_server,
            "name": args.name,
            "servers": [[str(args.server)]],
        }
    ]


def main() -> int:
    args = parse_args()
    payload = build_payload(args)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    headers = {
        "accept": "*/*",
        "authorization": f"Bearer {args.token}",
        "clientid": args.clientid,
        "content-type": "application/json",
        "gameid": str(args.gameid),
        "regionid": str(args.regionid),
        "origin": args.origin,
        "referer": args.referer,
    }

    request = urllib.request.Request(args.url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            text = response.read().decode("utf-8", errors="replace")
            print(text)
            data = json.loads(text)
            if isinstance(data, dict) and data.get("success") is True:
                return 0
            return 1
    except urllib.error.HTTPError as error:
        text = error.read().decode("utf-8", errors="replace")
        print(text, file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(str(error.reason), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
