#!/usr/bin/env python3
"""Wait until the local GWS credentials can read a Google Sheet."""

from __future__ import annotations

import argparse
import json
import time

import gsheet_utils as gs


DEFAULT_SPREADSHEET_ID = "1Pblighke8cHVMrGVuN60A9Cz-yBSKO8JKZ0my2ntCqU"


def classify_probe_result(rc: int, stdout: str, stderr: str) -> tuple[str, str]:
    """Return (ready|waiting|error, detail) for one GWS probe."""
    payload = None
    try:
        payload = json.loads(stdout) if stdout.strip() else None
    except json.JSONDecodeError:
        pass

    if rc == 0 and isinstance(payload, dict) and "error" not in payload:
        return "ready", "GWS authentication is ready"

    error = payload.get("error", {}) if isinstance(payload, dict) else {}
    code = error.get("code")
    detail = error.get("message") or stderr.strip() or stdout.strip() or f"exit code {rc}"
    if code == 401 or "invalid_grant" in detail or "Authentication failed" in detail:
        return "waiting", detail
    return "error", detail


def probe(spreadsheet_id: str) -> tuple[str, str]:
    params = json.dumps(
        {
            "spreadsheetId": spreadsheet_id,
            "fields": "spreadsheetId",
        }
    )
    return classify_probe_result(
        *gs._call(["sheets", "spreadsheets", "get", "--params", params])
    )


def wait_for_auth(spreadsheet_id: str, timeout: float, interval: float) -> int:
    deadline = time.monotonic() + timeout
    while True:
        status, detail = probe(spreadsheet_id)
        if status == "ready":
            print(detail)
            return 0
        if status == "error":
            print(f"GWS authentication probe failed: {detail}")
            return 1
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print(f"Timed out waiting for GWS authentication: {detail}")
            return 2
        time.sleep(min(interval, remaining))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spreadsheet-id", default=DEFAULT_SPREADSHEET_ID)
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--interval", type=float, default=3)
    args = parser.parse_args()
    if args.timeout <= 0 or args.interval <= 0:
        parser.error("--timeout and --interval must be greater than zero")
    return wait_for_auth(args.spreadsheet_id, args.timeout, args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
