#!/usr/bin/env python3
"""Fetch recent messages from Discord channels using user token."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

DISCORD_API = "https://discord.com/api/v10"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def get_token():
    """Read Discord token from env or TOOLS.md fallback."""
    token = os.environ.get("DISCORD_USER_TOKEN")
    if token:
        return token
    # Try reading from TOOLS.md
    tools_path = os.path.expanduser("~/clawd/TOOLS.md")
    if os.path.exists(tools_path):
        with open(tools_path) as f:
            for line in f:
                if "Token:" in line and "MTM5" in line:
                    # Extract token between backticks or after **Token:**
                    import re
                    m = re.search(r'`([^`]+)`', line)
                    if m:
                        return m.group(1)
    return None


def discord_request(endpoint, token):
    """Make a Discord API request with rate limit handling."""
    url = f"{DISCORD_API}{endpoint}"
    req = Request(url, headers={
        "Authorization": token,
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
    })
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        if e.code == 429:
            retry = json.loads(e.read()).get("retry_after", 5)
            print(f"  Rate limited, waiting {retry}s...", file=sys.stderr)
            time.sleep(retry + 0.5)
            return discord_request(endpoint, token)
        raise


def snowflake_from_datetime(dt):
    """Convert datetime to Discord snowflake ID for 'after' parameter."""
    discord_epoch = 1420070400000  # 2015-01-01T00:00:00Z in ms
    ms = int(dt.timestamp() * 1000)
    return (ms - discord_epoch) << 22


def fetch_channel_messages(channel_id, token, hours=24, limit=50):
    """Fetch messages from a channel within the last N hours."""
    after_dt = datetime.now(timezone.utc) - timedelta(hours=hours)
    after_snowflake = snowflake_from_datetime(after_dt)
    
    endpoint = f"/channels/{channel_id}/messages?limit={limit}&after={after_snowflake}"
    time.sleep(2)  # Rate limit safety
    
    try:
        messages = discord_request(endpoint, token)
    except Exception as e:
        return {"error": str(e), "messages": []}
    
    if not isinstance(messages, list):
        return {"error": str(messages), "messages": []}
    
    results = []
    for msg in messages:
        results.append({
            "id": msg["id"],
            "author": msg["author"].get("username", "unknown"),
            "content": msg.get("content", ""),
            "timestamp": msg.get("timestamp", ""),
            "embeds": [
                {
                    "title": e.get("title", ""),
                    "description": e.get("description", "")[:500],
                    "url": e.get("url", ""),
                }
                for e in msg.get("embeds", [])
            ],
            "attachments": [a.get("url", "") for a in msg.get("attachments", [])],
        })
    
    return {"messages": sorted(results, key=lambda x: x["timestamp"])}


def main():
    parser = argparse.ArgumentParser(description="Fetch Discord channel messages")
    parser.add_argument("--config", required=True, help="Path to game config JSON")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours")
    parser.add_argument("--priority", choices=["high", "medium", "all"], default="high")
    parser.add_argument("--channel", help="Specific channel name to fetch")
    parser.add_argument("--limit", type=int, default=50, help="Max messages per channel")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    token = get_token()
    if not token:
        print(json.dumps({"error": "No Discord token found"}))
        sys.exit(1)

    discord_cfg = config.get("discord", {})
    channels = {}

    if args.channel:
        # Fetch specific channel
        for priority in ["high_priority", "medium_priority"]:
            if args.channel in discord_cfg.get(priority, {}):
                channels[args.channel] = discord_cfg[priority][args.channel]
                break
    else:
        channels.update(discord_cfg.get("high_priority", {}))
        if args.priority in ("medium", "all"):
            channels.update(discord_cfg.get("medium_priority", {}))

    output = {}
    for name, channel_id in channels.items():
        print(f"  Fetching #{name} ({channel_id})...", file=sys.stderr)
        result = fetch_channel_messages(channel_id, token, args.hours, args.limit)
        output[name] = result

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
