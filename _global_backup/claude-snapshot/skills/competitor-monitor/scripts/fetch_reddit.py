#!/usr/bin/env python3
"""Fetch recent posts from a subreddit via Reddit JSON API (no auth needed)."""

import argparse
import json
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen


def fetch_subreddit(subreddit, sort="new", limit=25, hours=24):
    """Fetch recent posts from subreddit."""
    url = f"https://old.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    })

    with urlopen(req) as resp:
        data = json.loads(resp.read())

    cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
    posts = []

    for child in data.get("data", {}).get("children", []):
        p = child.get("data", {})
        if p.get("created_utc", 0) < cutoff:
            continue
        posts.append({
            "title": p.get("title", ""),
            "author": p.get("author", ""),
            "score": p.get("score", 0),
            "num_comments": p.get("num_comments", 0),
            "url": f"https://reddit.com{p.get('permalink', '')}",
            "selftext": p.get("selftext", "")[:500],
            "flair": p.get("link_flair_text", ""),
            "created": datetime.fromtimestamp(p.get("created_utc", 0), tz=timezone.utc).isoformat(),
        })

    return posts


def main():
    parser = argparse.ArgumentParser(description="Fetch Reddit posts")
    parser.add_argument("--config", required=True, help="Path to game config JSON")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours")
    parser.add_argument("--limit", type=int, default=25, help="Max posts to fetch")
    parser.add_argument("--sort", default="new", choices=["new", "hot", "top"])
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    subreddit = config["reddit"]["subreddit"]
    posts = fetch_subreddit(subreddit, args.sort, args.limit, args.hours)

    print(json.dumps({
        "subreddit": subreddit,
        "post_count": len(posts),
        "posts": posts,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
